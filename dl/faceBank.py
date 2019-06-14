import cv2
import numpy as np
import os
from pathlib import Path
from django.conf import settings
import redis
from .yolo.yolo import YOLO
from .face_dlib.FaceAlignment import FaceAlignment
from .insightFace.insightFace import InsightFace
from .hnsw.pyw_hnswlib import HNSWIndex
import time
from .utils import base64_encode_image
import requests
import json
from Share import helper
from threading import Thread
import hashlib


class FaceBank:

    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.facebank_dir = os.path.join(BASE_DIR, "..", "media", "2019")

        print("facebank: ", self.facebank_dir)

        self.encode = 3

        # self.yolo_model = YOLO()
        # self.face_alignment = FaceAlignment()
        # self.insightFace_model = InsightFace()
        # self.hnsw = HNSWIndex()

    def initFaceBank(self, encode=3):
        db = redis.StrictRedis(host=settings.REDIS_HOST,
                               port=settings.REDIS_PORT, db=settings.REDIS_DB)
        try:
            self.hnswDict = np.load("hnswdict.npy").item()
        except:
            self.hnswDict = dict()

        newHnswDict = dict()
        newHnswDict["len"] = 0
        hnsw = HNSWIndex('cosine', 512)
        hnsw.init_index(max_elements=100000, ef_construction=100, M=512)

        pathDir = Path(self.facebank_dir)

        for person in pathDir.iterdir():
            if person.is_file():
                continue

            for image_path in person.iterdir():
                if not image_path.is_file():
                    continue

                name = str(image_path).split('/')[-2]

                try:
                    md5 = helper.GetFileMd5(str(image_path))
                    if md5 in self.hnswDict:
                        if name in self.hnswDict[md5]["name"]:
                            newHnswDict[md5] = self.hnswDict[md5]
                            continue;
                        else:
                            newHnswDict[md5]["name"].append(name)
                    else:
                        newHnswDict[md5] = {
                            "name": [name]}
                    newHnswDict[md5]["name"] = list(set(newHnswDict[md5]["name"]))
                    newHnswDict[md5]["len"] = len(newHnswDict[md5]["name"])
                    newHnswDict["len"] += newHnswDict[md5]["len"]
                except:
                    continue

                img = cv2.imread(str(image_path))
                # 非图片文件或读取文件失败
                if img is None:
                    continue;

                print(str(image_path))

                img_encode = base64_encode_image(img)

                data = {"image": img_encode,
                        "name": name,
                        "detected": False,
                        "recognize": False,
                        "bbox": [],
                        "savePic": False,
                        "saveVec": True,
                        }

                # submit the request
                r = requests.post("http://127.0.0.1:8000/face-recognition/", data=json.dumps(data), verify=False).json()

                # ensure the request was sucessful
                if r["retVal"] == 2:
                    newHnswDict[md5]["vec"] = r["vec"]
                    print("[INFO] {} ----Add success".format(str(image_path)))
                elif r["retVal"] == 101:
                    print("[INFO] {} ----No Face".format(str(image_path)))

        np.save("hnswdict.npy", newHnswDict)
        db.set("hnswdict", json.dumps(newHnswDict))
        db.set("hnswdictupdatetime", int(round(time.time())))  # 毫秒级时间戳

    def loadFaceBank(self):
        pass

    def updateFaceBank(self, newHnsw, db):

        try:
            self.hnswDict = np.load("hnswdict.npy").item()
        except:
            self.hnswDict = dict()

        newHnswDict = dict()
        newHnswDict["len"] = 0

        pathDir = Path(self.facebank_dir)
        isUpdate = False

        for person in pathDir.iterdir():
            if person.is_file():
                continue

            for image_path in person.iterdir():
                if not image_path.is_file():
                    continue

                name = str(image_path).split('/')[-2]

                try:
                    md5 = helper.GetFileMd5(str(image_path))
                except:
                    continue
                if md5 in self.hnswDict or md5 in newHnswDict:
                    if md5 not in newHnswDict:
                        newHnswDict[md5] = {"name": [],
                                            "id": []}
                    if name not in newHnswDict[md5]["name"]:
                        newHnswDict[md5]["name"].append(name)
                        newHnswDict[md5]["id"].append(newHnsw.cur_ind)
                        if newHnswDict[md5].get("vec") is None:
                            newHnswDict[md5]["vec"] = self.hnswDict[md5]["vec"]
                        if md5 in self.hnswDict:
                            newHnsw.add_items([self.hnswDict[md5]["vec"]],
                                              ids=[name])
                        elif md5 in newHnswDict:
                            newHnsw.add_items([newHnswDict[md5]["vec"]],
                                              ids=[name])
                        newHnswDict["len"] += 1
                    else:
                        continue

                else:

                    img = cv2.imread(str(image_path))
                    # 非图片文件或读取文件失败
                    if img is None:
                        continue

                    print(str(image_path))

                    img_encode = base64_encode_image(img)

                    data = {"image": img_encode,
                            "name": name,
                            "detected": False,
                            "recognize": False,
                            "face": [],
                            "savePic": False,
                            "saveVec": True,
                            }

                    # submit the request
                    r = requests.post("http://127.0.0.1:8000/face-recognition/", data=json.dumps(data),
                                      verify=False).json()

                    # ensure the request was sucessful
                    f=open("res.txt","a")
                    if r["retVal"] == 2:
                        newHnswDict[md5] = {"name": [name],
                                            "id": [newHnsw.cur_ind]}
                        newHnswDict[md5]["vec"] = r["vec"]
                        newHnsw.add_items([newHnswDict[md5]["vec"]],
                                          ids=[name])
                        newHnswDict["len"] += 1
                        print("[INFO] {} ----Add success".format(str(image_path)))
                        f.write("[INFO] {} ----Add success".format(str(image_path))+"\n")

                    elif r["retVal"] == 101:
                        print("[INFO] {} ----No Face".format(str(image_path)))
                        f.write("[INFO] {} ----No Face".format(str(image_path))+"\n")

        stream = "FRStream"
        d={"type":"Signal"}
        db.xadd(stream, {'data': json.dumps(d)})
        np.save("hnswdict.npy", newHnswDict)
        db.set("hnswDict", json.dumps(newHnswDict))
        db.set("hnswDictUpdateSignal", 1)
        db.set("hnswUpdateTimeStamp", int(round(time.time() * 1000)))

