# USAGE
# python stress_test.py

# import the necessary packages
from threading import Thread
import requests
import time
import cv2
import base64
import json
from pathlib import Path
# initialize the Keras REST API endpoint URL along with the input
# image path
API = "http://127.0.0.1:8000/face-recognition/"

test=Path('/Users/ty/Desktop/Data/test')
f=open("test.txt","w")
for img in test.iterdir():
    image_np=cv2.imread(str(img))
    image = cv2.imencode('.jpg', image_np)[1]
    image_code = str(base64.b64encode(image))[2:-1]
    name= str(img).split('/')[-1]
    data = {"image":
                image_code,
            'name':name}
    r = requests.post(API, data=json.dumps(data),verify=False).json()
    f.write(name)
    if r["retVal"]==1:
        f.write(" {} {}\n".format(r["face"][0]["match"],r["face"][0]["similarity"]))
        print("{} {} {}".format(name,r["face"][0]["match"],r["face"][0]["similarity"]))
    else:
        f.write("\n")
        
