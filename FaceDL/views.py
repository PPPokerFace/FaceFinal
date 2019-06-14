from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.generic.base import View
from rest_framework.views import APIView
import cv2
# Create your views here.
from Share import helper
import redis
import json
import time
from Share import helper


class FaceRecognition(APIView):

    def post(self, request):
        r = redis.StrictRedis(host=settings.REDIS_HOST,
                              port=settings.REDIS_PORT, db=settings.REDIS_DB)

        stream = "FRStream"
        try:
            body = json.loads(request.body)
        except:
            body = request.POST

        image = body.get("image")

        if image is None:
            return JsonResponse({"msg": "No image",
                                 "retVal": "-1"})

        # Get the image in ndarray
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
            return JsonResponse({"msg": "Error image",
                                 "retVal": "-2"})

        bbox = body.get("face")
        detected = helper.data_cast(body["detected"]) if "detected" in body else 1

        if isinstance(bbox, list) is False \
                or len(bbox) == 0:
            detected = False

        name = body.get('name')

        recognize = helper.data_cast(body["recognize"]) if "recognize" in body else 1
        savePic = helper.data_cast(body["savePic"]) if "savePic" in body else 0
        saveVec = helper.data_cast(body["saveVec"]) if "saveVec" in body else 0

        d = {
            "type": "Recognition",
            "image": img_data,
            "name": name,
            "detected": detected,
            "recognize": recognize,
            "face": bbox,
            "savePic": savePic,
            "saveVec": saveVec
        }

        if body.get("md5"):
            d["md5"] = body["md5"]

        # db.rpush(settings.IMAGE_QUEUE, json.dumps(d))
        id = r.xadd(stream, {'data': json.dumps(d)})

        while True:
            # attempt to grab the output predictions
            output = r.get(id)

            # check to see if our model has classified the input
            # image
            if output is not None:
                # add the output predictions to our data
                # dictionary so we can return it to the client
                output = output.decode("utf-8")
                output = json.loads(output)

                # delete the result from the database and break
                # from the polling loop
                r.delete(id)
                r.xdel(stream, id)
                break

            # sleep for a small amount to give the model a chance
            # to classify the input image
            time.sleep(settings.CLIENT_SLEEP)
        return JsonResponse(output)

    def get(self, request):
        return JsonResponse({'retVal': 601})


class FaceDelete(APIView):

    def post(self, request):
        r = redis.StrictRedis(host=settings.REDIS_HOST,
                              port=settings.REDIS_PORT, db=settings.REDIS_DB)

        stream = "FRStream"
        try:
            d = json.loads(request.body)
        except:
            d = request.POST

        d["type"] = "Delete"

        id = r.xadd(stream, {'data': json.dumps(d)})

        return JsonResponse({"retMsg": "Success",
                             "retVal": 1})

    def get(self, request):
        pass


class ObjectDetectionMetrics(APIView):
    def post(self, request):
        f = open("/Users/ty/Desktop/CCCCC/test.txt", "w")
        f.write(request.body.decode('utf8'))
        f.close()
        return JsonResponse({'results': "OK"})
