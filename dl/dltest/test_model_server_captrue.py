# USAGE
# python stress_test.py

# import the necessary packages
from threading import Thread
import requests
import time
import cv2
import base64
# initialize the Keras REST API endpoint URL along with the input
# image path
KERAS_REST_API_URL = "https://127.0.0.1/dododo/"

capture = cv2.VideoCapture(0);
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

def do(api,data):
    return requests.post(api, data=data, verify=False).json()

while capture.isOpened():

    success,frame=capture.read()

    if success :

        image = cv2.imencode('.jpg', frame)[1]
        image_code = str(base64.b64encode(image))[2:-1]
        data = {"image": image_code}

        t = Thread(target=do, args=(KERAS_REST_API_URL,data))
        t.daemon = True
        t.start()



        cv2.imshow("res",frame)

    cv2.waitKey(200)
