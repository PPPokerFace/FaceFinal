# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
import json
from dl.FaceEngine import FaceEngine
import asyncio
import time
from threading import Thread
import cv2
import redis
from django.conf import settings
from Share import helper


class AsyncImageConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        self.faceEngine = FaceEngine()
        # self.faceEngine.openCapture(0)
        await self.accept()

    async def disconnect(self, code):
        print("close disconnect.")
        if self.faceEngine:
            self.faceEngine.closeCapture()

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = text_data
        data = json.loads(data)
        print(data)
        if "requestVal" not in data:
            await self.send(json.dumps({"retVal": -1}))
            return
        id = data["id"]
        #        if not id.startswith("rtsp://"):
        #            await self.send(json.dumps({"retVal": -10}))
        #            return
        id = int(id)
        open = self.faceEngine.openCapture(id)

        loop = asyncio.get_event_loop()
        aa = await loop.run_in_executor(None, self.sendFrame)
        print(aa)
        # loop = asyncio.get_event_loop()
        #        loop.run_until_complete(self.sendFrame(loop))
        #        loop.close()

    #        self.t=Thread(target=self.sendFrame)
    #        self.t.daemon=True
    #        self.t.start()

    # print(open)
    # while True:
    #     res = self.faceEngine.faceFrame()
    #     await self.send(
    #         text_data=json.dumps(res))
    #     await asyncio.sleep(0.01)

    def image_message(self, event):
        print(event["message"])

    async def sendFrame(self):
        print(111111111)
        while True:
            res = self.faceEngine.faceFrame()
            await self.send(
                text_data=json.dumps(res))
            await asyncio.sleep(0.05)


class ImageConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = "ImageGroup"
        self.faceEngine = FaceEngine()
        # self.faceEngine.openCapture(0)

        self.accept()

    def disconnect(self, code):
        print("close disconnect.")
        if self.faceEngine:
            self.faceEngine.closeCapture()

    # Receive message from WebSocket
    def receive(self, text_data):
        data = text_data
        data = json.loads(data)
        print(data)
        if "requestVal" not in data:
            self.send(json.dumps({"retVal": -1}))
            return

        id = data["id"]
        try:
            id = int(id)
        except:
            pass
        open = self.faceEngine.openCapture(id)

        self.t = Thread(target=self.sendFrame)
        self.t.daemon = True
        self.t.start()

    def image_message(self, event):
        print(event["message"])

    def sendFrame(self):
        while True:
            res = self.faceEngine.faceFrame()
            self.send(
                text_data=json.dumps(res))
            time.sleep(0.05)


class FaceRecognitionConsumer(WebsocketConsumer):
    def connect(self):
        self.r = redis.StrictRedis(host=settings.REDIS_HOST,
                                   port=settings.REDIS_PORT,
                                   db=settings.REDIS_DB)
        self.stream = "FRStream"
        self.ids = []
        self.t = Thread(target=self.getData)
        self.t.daemon = True
        self.t.start()
        self.accept()

    def disconnect(self, code):
        pass

    # Receive message from WebSocket
    def receive(self, text_data):
        data = text_data
        data = json.loads(data)

        image = data.get("image")

        try:
            # If send from browser
            img_data = image.split(",")[-1]
        except:
            # Send from base64
            img_data = image

        try:
            img = helper.base64_decode_image(img_data)
            assert img is not None
        except:
            return;

        bbox = data.get("face")
        detected = helper.data_cast(data["detected"]) if "detected" in data else 1

        d = {
            "type": "Recognition",
            "image": img_data,
            "name": "",
            "detected": detected,
            "recognize": 1,
            "face": bbox,
            "savePic": 0,
            "saveVec": 0
        }

        # db.rpush(settings.IMAGE_QUEUE, json.dumps(d))
        id = self.r.xadd(self.stream, {'data': json.dumps(d)})
        self.ids.append(id)

    def getData(self):

        while True:
            # attempt to grab the output predictions

            for id in self.ids:
                output = self.r.get(id)

            # check to see if our model has classified the input
            # image
                if output is not None:
                # add the output predictions to our data
                # dictionary so we can return it to the client
                    output = output.decode("utf-8")
                    output = json.loads(output)

                    self.send(
                        text_data=json.dumps(output))
                # delete the result from the database and break
                # from the polling loop
                    self.r.delete(id)
                    self.r.xdel(self.stream, id)
                    self.ids.remove(id)
                    break

            # sleep for a small amount to give the model a chance
            # to classify the input image
            time.sleep(settings.CLIENT_SLEEP)


