import torch
import redis
import json
import cv2
import numpy as np

# from django.conf import settings

from dl.yolo.yolo import YOLO
from dl.face_dlib.FaceAlignment import FaceAlignment
from dl.insightFace.insightFace import InsightFace
from dl.hnsw.pyw_hnswlib import HNSWIndex
from dl import utils

class FaceEngine():
    def __init__(self):
        if torch.cuda.is_available():
            torch.cuda.empty_cache();
        self.detectionModel = YOLO()
        self.detectionModel.loadModel("face-yolov3-tiny.cfg", "tiny.pt", 416)
        self.alignmentModel = FaceAlignment()
        self.recognitionModel = InsightFace(use_mobilefacenet=False)
        self.searchModel = HNSWIndex("cosine", 512)
        self.searchModelUpdateTimeStamp = -1
        #        self.r = redis.StrictRedis(host=settings.REDIS_HOST,
        #                                   port=settings.REDIS_PORT, db=settings.REDIS_DB)
        self.r = redis.StrictRedis(host="localhost",
                                   port=6379, db=0)
        self.captrue = cv2.VideoCapture()

    def openCapture(self, videoCaptureId):
        try:
            self.closeCapture()
            self.captrue.open(videoCaptureId)
            return self.captrue.isOpened()
        except:
            return False

    def closeCapture(self):
        if self.captrue.isOpened():
            self.captrue.release()
        return True

    def isCaotureOpened(self):
        return self.captrue.isOpened()

    def faceDetection(self, frame):
        tensor = self.detectionModel.prepare_image(frame, auto=True)
        print(tensor.shape)
        output = self.detectionModel.predict(tensor, frame.shape)
        return output[0]

    def faceAlignment(self, frame, faceTensor):
        face_rectangles = list()
        for *xyxy, conf, score, label in faceTensor:
            xmin = int(xyxy[0])
            ymin = int(xyxy[1])
            xmax = int(xyxy[2])
            ymax = int(xyxy[3])
            score = float(conf) * float(score)
            face_rectangles.append((xmin, ymin, xmax, ymax))
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 0, 0xff), 2)

        faces = list()
        if len(face_rectangles) != 0:
            faces = self.alignmentModel.faceAlignment(frame, face_rectangles=face_rectangles)
        return faces

    def faceRecognition(self, faces):
        face_batch = list()
        for face in faces:
            face_transed = self.recognitionModel.prepare_transform(face)
            face_batch.append(face_transed)
        if len(face_batch) == 0:
            return None
        face_vecs = self.recognitionModel.predict(torch.stack(face_batch, 0))
        return face_vecs.cpu().detach().numpy()

    def faceSearch(self, vecs):
        hnswUpdateTimeStamp = int(self.r.get("hnswUpdateTimeStamp")) if self.r.get(
            "hnswUpdateTimeStamp") is not None else 0
        if hnswUpdateTimeStamp > self.searchModelUpdateTimeStamp:
            self.searchModelUpdateTimeStamp = hnswUpdateTimeStamp
            self.searchModel.load_index()
        if self.searchModel.cur_ind == 0:
            return [], np.array([])

        labels, distances = self.searchModel.knn_query(vecs, k=10)
        return labels, distances

    def faceEngine(self, frame):

        faceTensor = self.faceDetection(frame)
        faceImages = self.faceAlignment(frame, faceTensor)
        if len(faceImages) == 0:
            return [], np.array([])
        faceVecs = self.faceRecognition(faceImages)
        labels, distances = self.faceSearch(faceVecs)

        return labels, distances

    def faceVideo(self):
        if self.captrue.isOpened() is False:
            return json.dumps({"retVal": -1,
                               "retMsg": "Can't open the camera stream"})

        while self.captrue.isOpened():
            success, frame = self.captrue.read()
            if success:
                labels, distances = self.faceEngine(frame)
                print(labels, distances)


    def faceFrame(self):
        if not self.captrue.isOpened():
            return {"retVal": -1,
                    "retMsg": "Can't open the camera stream"}

        success, frame = self.captrue.read()

        if not success:
            return {"retVal": -2,
                    "retMsg": "Can't open the camera stream"}

        imageEncode = utils.base64_encode_image(frame)
        faceTensor = self.faceDetection(frame)
        faceInfo = list()
        for *xyxy, conf, score, label in faceTensor:
            faceInfo.append({
                "xmin": int(xyxy[0]),
                "ymin": int(xyxy[1]),
                "xmax": int(xyxy[2]),
                "ymax": int(xyxy[3]),
                "conf": int(float(conf) * float(score)*100)})

        faceImages = self.faceAlignment(frame, faceTensor)
        if len(faceImages) != 0:
            faceVecs = self.faceRecognition(faceImages)
            labels, distances = self.faceSearch(faceVecs)
            print(labels,distances)
            for index,(label,distance) in enumerate(zip(labels, distances)):
                faceInfo[index]["label"] = label[0]
                faceInfo[index]["distance"] = int(distance[0]*100)      #JSON not support FP32

        return {"retVal": 1,
                "retMsg": "Success.",
                "image": imageEncode,
                "faceInfo": faceInfo
                }

    def facePicture(self,frame):
        imageEncode = utils.base64_encode_image(frame)
        faceTensor = self.faceDetection(frame)
        faceInfo = list()
        for *xyxy, conf, score, label in faceTensor:
            faceInfo.append({
                "xmin": int(xyxy[0]),
                "ymin": int(xyxy[1]),
                "xmax": int(xyxy[2]),
                "ymax": int(xyxy[3]),
                "conf": int(float(conf) * float(score)*100)})

        faceImages = self.faceAlignment(frame, faceTensor)
        if len(faceImages) != 0:
            faceVecs = self.faceRecognition(faceImages)
            labels, distances = self.faceSearch(faceVecs)
            print(labels,distances)
            for index,(label,distance) in enumerate(zip(labels, distances)):
                faceInfo[index]["label"] = label[0]
                faceInfo[index]["distance"] = int(distance[0]*100)      #JSON not support FP32

        return {"retVal": 1,
                "retMsg": "Success.",
                "image": imageEncode,
                "faceInfo": faceInfo
                }
