import sys
import os

sys.path.append("..")
sys.path.append("../..")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
from yolo.yolo import YOLO
from yolo.utils.datasets import letterbox
import cv2
import torch
import torchvision.transforms as trans

img = cv2.imread("jemma.png")
yolo = YOLO()

image, _, _, _ = letterbox(img, height=288)

image = image.unsqueeze(0)

res = yolo.predict(image, img.shape)

print(res)

cv2.rectangle(img, (res[0][0][0], res[0][0][1]), (res[0][0][2], res[0][0][3]), (0, 0, 255))

cv2.imshow("img", img)

cv2.waitKey(0)
