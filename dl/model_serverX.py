# import the necessary packages
from django.conf import settings
import torch

import redis
import time
import json
import numpy as np
import math
from threading import Thread
import random
from dl.yolo.yolo import YOLO
from dl.face_dlib.FaceAlignment import FaceAlignment
from dl.insightFace.insightFace import InsightFace
from dl.hnsw.pyw_hnswlib import HNSWIndex
from dl import utils
from .faceBank import FaceBank
import time


def classify_process():
    # connect to Redis server
    time.sleep(5)

    db = redis.StrictRedis(host=settings.REDIS_HOST,
                           port=settings.REDIS_PORT, db=settings.REDIS_DB)

    print("===* Loading model... *===")
    yolo_model = YOLO()

    fa = FaceAlignment()

    insightFace = InsightFace(use_mobilefacenet=settings.USE_MOBILEFACENET)

    hnsw = HNSWIndex('cosine', 512)

    db.flushdb()
    try:
        hnsw.load_index()
    except:
        hnsw.init_index(max_elements=15000, ef_construction=200, M=512)

    hnsw.set_ef(512)
#    if hnsw.cur_ind == 0:
    db.set("hnswUpdateSignal", 1)

    try:
        hnswDict = np.load("hnswdict.npy").item()
    except:
        hnswDict = dict()

    delete_mask = []

    #    fb=FaceBank()
    #    if hnsw.cur_ind != hnswDict.get("len"):
    #        t=Thread(target=fb.updateFaceBank)
    #        t.start()

    print("===* Model loaded     *===")

    fb = FaceBank()

    stream = "FRStream"
    group = "FRGroup"
    consumer = "FRConsumer"
    # try:
    db.xgroup_create(stream, group, id="0-0", mkstream=True)
    # except:
    #    pass
    NewHNSWIndex=None
    # continually pool for new images to classify
    while True:
        # attempt to grab a batch of images from the database
        # db.xread(streams={stream:'>'},
        #          count=settings.BATCH_SIZE//2,
        #          block=300)

        groupData = db.xreadgroup(groupname=group,
                                  consumername=consumer,
                                  streams={stream: '>'},
                                  count=settings.BATCH_SIZE // 2,
                                  block=300)

        hnswUpdateSignal = int(db.get("hnswUpdateSignal")) \
            if db.get("hnswUpdateSignal") is not None else 0
        if hnswUpdateSignal:
            NewHNSWIndex = HNSWIndex('cosine', 512)
            NewHNSWIndex.init_index(max_elements=20000, ef_construction=100, M=512)
            db.set("hnswUpdateSignal", 0)
            t = Thread(target=fb.updateFaceBank, args=(NewHNSWIndex, db))
            t.daemon = True
            t.start()

        hnswDictUpdateSignal = int(db.get("hnswDictUpdateSignal")) \
            if db.get("hnswDictUpdateSignal") is not None else 0
        if hnswDictUpdateSignal:
            hnsw = NewHNSWIndex
            hnsw.save_index()
            delete_mask = []
            db.set("hnswDictUpdateSignal", 0)
            hnswDict = json.loads(db.get("hnswDict")) if db.get("hnswDict") is not None else hnswDict

        if len(groupData) == 0 or len(groupData[0][1]) == 0:
            continue
        # groupData[0][0] is the stream name
        groupData = groupData[0][1]

        Data = []
        for groupdata in groupData:
            id = groupdata[0].decode('utf8')
            data = json.loads(list(groupdata[1].values())[0])

            if data.get('type') == "Signal":            #Signal 项什么都不做
                db.xack(stream, group, id)
                db.xdel(stream, id)

                pass
            elif data.get("type") == "Delete":
                db.xack(stream, group, id)
                db.xdel(stream, id)
                md5 = data.get("md5")
                name = data.get("name")
                if md5 in hnswDict and name in hnswDict[md5]["name"]:
                    index = hnswDict[md5]["name"].index(name)
                    delete_mask.append(hnswDict[md5]["id"][index])
                    dictLen = hnswDict["len"]
                    hnswLen = hnsw.cur_ind - len(delete_mask)
                    if dictLen > hnswLen:
                        db.set("hnswUpdateSignal", 1)

            elif data.get("type") == "Recognition":
                Data.append((id, data))
        groupData = Data

        # Now groupData[0] is the id ang groupData[1] is the data

        batch_for_detect = []
        image_sizes_for_detect = []
        image_ids_for_detect = []
        for index, groupdata in enumerate(groupData):
            data = groupdata[1]
            if not data.get("detected"):
                # Get the image and image shape
                image = utils.base64_decode_image(data["image"])
                image_size = image.shape

                # Get the image size and id in the groupData
                image_sizes_for_detect.append(image_size)
                image_ids_for_detect.append(index)

                # data prepare and batch
                batch = yolo_model.prepare_image(image)
                batch_for_detect.append(batch)

        if len(batch_for_detect) > 0:
            start = time.time()
            data = torch.stack(batch_for_detect, 0)
            results = yolo_model.predict(data, image_sizes_for_detect)

            for (imageID, resultSet) in zip(image_ids_for_detect, results):
                # initialize the list of output predictions
                groupData[imageID][1]["face"] = []
                # loop over the results and add them to the list of
                # output predictions

                for *xyxy, conf, score, label in resultSet:
                    r = {"xmin": int(xyxy[0]),
                         "ymin": int(xyxy[1]),
                         "xmax": int(xyxy[2]),
                         "ymax": int(xyxy[3]),
                         "score": float(conf) * float(score)}
                    groupData[imageID][1]["face"].append(r)
            end = time.time()
            print("* YOLO : {} / {}".format(data.shape, end - start))

        # It's the map from ImageID to FaceImage , the ImageID is from groupData.
        image2faceMap = [None] * len(groupData)

        batch_for_recognize = []
        # It's the map from FaceID to ImageID , the FaceID is from batch_for_recognize
        # and the ImageID is from groupData.
        face2ImageIDMap = []
        face2ImageLocationMap = []

        for index, groupdata in enumerate(groupData):
            data = groupdata[1]

            image = utils.base64_decode_image(data["image"])

            face_rectangles = []
            #            if isinstance(data["face"],str):
            #                data['face']=json.loads(data["face"])

            for face in data["face"]:
                face_rectangles.append((face["xmin"], face["ymin"], face["xmax"], face["ymax"]))

            if len(face_rectangles) == 0:
                continue
            aligned_face = fa.faceAlignment(image, face_rectangles=face_rectangles)

            image2faceMap[index] = aligned_face

            for loc, face in enumerate(aligned_face):
                face_transed = insightFace.prepare_transform(face)

                # Append to the batch for recognize
                batch_for_recognize.append(face_transed)
                face2ImageIDMap.append(index)
                face2ImageLocationMap.append(loc)

        BATCH_SIZE = settings.BATCH_SIZE
        for i in range(int(math.ceil(len(batch_for_recognize) / BATCH_SIZE))):
            start = time.time()
            start_index = i * BATCH_SIZE
            end_index = (i + 1) * BATCH_SIZE
            data = torch.stack(batch_for_recognize[start_index:end_index], 0)

            embedings = insightFace.predict(data)

            for index, embeding in enumerate(embedings):

                embeding_numpy = embeding.cpu().detach().numpy()

                id = face2ImageIDMap[start_index + index]
                loc = face2ImageLocationMap[start_index + index]

                timeid = groupData[id][0]
                jsonData = groupData[id][1]

                if jsonData["saveVec"]:
                    hnsw.add_items([embeding_numpy],
                                   ids=[jsonData.get("name")])
                    hnsw.save_index()
                    if jsonData.get("md5"):
                        hnswDict = json.loads(db.get("hnswDict")) if db.get("hnswDict") is not None else hnswDict
                        md5 = jsonData["md5"]
                        name = jsonData["name"]
                        if md5 not in hnswDict:
                            hnswDict[md5] = {"name": [],
                                             "id": []}
                        hnswDict[md5]["name"].append(name)
                        hnswDict[md5]["id"].append(hnsw.cur_ind)
                        hnswDict["len"] += 1
                        db.set("hnswDict", json.dumps(hnswDict))
                    jsonData["vec"] = embeding_numpy.tolist()

                ret = {
                    "match": None,
                    "score": 0
                }

                if "recognize" not in jsonData or jsonData["recognize"] == True:
                    try:
                        if len(delete_mask) != 0:
                            labelsid, labels, distances = hnsw.knn_query_id(embeding_numpy, k=3)
                            labelsid, labels, distances = list(labelsid[0]), labels[0], distances[0]
                            new_labels = []
                            new_distances = []
                            for id in labelsid:
                                if id not in delete_mask:
                                    index = labelsid.index(id)
                                    new_labels.append(labels[index])
                                    new_distances.append(distances[index])
                            labels = new_labels
                            distances = np.array(new_distances)
                        else:
                            labels, distances = hnsw.knn_query(embeding_numpy, k=1)
                            labels, distances = labels[0], distances[0]
                        ret = {"match": labels[0],
                               "score": float(1 - distances[0])}
                        print(labels, 1 - distances)
                    except:
                        pass

                jsonData["face"][loc]["match"] = ret["match"]
                jsonData["face"][loc]["similarity"] = ret["score"]
                jsonData["retVal"] = 1

            end = time.time()
            print("* InsightFace : {} / {}".format(data.shape, end - start))

        for groupdata in groupData:
            timeid = groupdata[0]
            jsonData = groupdata[1]

            # 人脸检测失败
            if len(jsonData["face"]) == 0:
                jsonData["retVal"] = 101
            # 验证成功
            elif jsonData.get("match") is not None:
                jsonData["retVal"] = 1
            # 添加成功
            elif jsonData.get("saveVec"):
                jsonData["retVal"] = 2

            jsonData.pop("image")
            jsonData.pop("detected")
            jsonData.pop("recognize")
            jsonData.pop("savePic")
            jsonData.pop("saveVec")

            # loop over the results and add them to the list of
            # output predictions
            # store the output predictions in the database, using
            # the image ID as the key so we can fetch the results
            db.set(timeid, json.dumps(jsonData))
            db.xack(stream, group, timeid)
