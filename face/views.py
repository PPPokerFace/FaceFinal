from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.views.generic.base import *
from django.core.cache import cache
# Create your views here.
import base64
import numpy as np
import cv2
import torch
from dl.yolo.yolo import YOLO
from dl import helper
import uuid
import redis
import json
import time

@csrf_exempt
def dododo(request):
    db = redis.StrictRedis(host=settings.REDIS_HOST,
                           port=settings.REDIS_PORT, db=settings.REDIS_DB)

    #    print(request.body)
    img = request.POST.get('image')

    if img is None:
        return JsonResponse({"msg":"No image"})


    bbox = request.POST.get('bbox')
    detected = int(request.POST["detected"]) if "detected" in request.POST else 0
    #detected=0
    if bbox is None :
        detected=False
    try:
        bbox=list(map(int,map(float,bbox.split(','))))
        bbox = None if len(bbox) != 4 else bbox
    except:
        bbox=None
    name=request.POST.get('name')
    recognize = request.POST["recognize"] if "recognize" in request.POST else 1
    savePic=request.POST["savePic"] if "savePic" in request.POST else 0
    saveVec=request.POST["saveVec"] if "saveVec" in request.POST else 0
    # print(img)


    # Get the image in ndarray
    try:
        #If send from browser
        img_data = img.split(",")[-1]
    except:
        #Send from base64
        img_data = img

    image=helper.base64_decode_image(img_data)
    #cv2.imwrite(time.strftime("%Y%m%d%H%M%S", time.localtime()) + ".jpg", image)

    k = str(uuid.uuid4())
    #image = helper.base64_decode_image(image)

    d = {"id": k,
         "image": img_data,
         "name":name,
         "detected": detected,
         "recognize":recognize,
         "bbox": bbox,
         "savePic":savePic,
         "saveVec":saveVec
         }
    db.rpush(settings.IMAGE_QUEUE, json.dumps(d))

    data = {"success": False}
    while True:
        # attempt to grab the output predictions
        output = db.get(k)

        # check to see if our model has classified the input
        # image
        if output is not None:
            # add the output predictions to our data
            # dictionary so we can return it to the client
            output = output.decode("utf-8")
            data["predictions"] = json.loads(output)

            # delete the result from the database and break
            # from the polling loop
            db.delete(k)
            break

        # sleep for a small amount to give the model a chance
        # to classify the input image
        time.sleep(settings.CLIENT_SLEEP)

    # indicate that the request was a success
    data["success"] = True

    # yoloModel = settings.YOLO_MODEL
    # yoloModel.predict(img_torch,(288,288))
    # print("ip address:", request.META.get('HTTP_X_FORWARDED_FOR'))

    return JsonResponse(data)