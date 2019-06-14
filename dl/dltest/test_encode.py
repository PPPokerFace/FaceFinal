import cv2
import base64
import numpy as np

def base64_encode_image(img):
    img = cv2.imencode('.jpg',img)[1]
    img = str(base64.b64encode(img))[2:-1]
    return img


def base64_decode_image(img_data):
    img_b64decode = base64.b64decode(img_data)
    img_array = np.frombuffer(img_b64decode, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return img

img=cv2.imread("/Users/ty/Desktop/毕业设计/Project/facebank/lyf/timg.jpg")

encode=base64_encode_image(img)
print(encode)

decode=base64_decode_image(encode)
cv2.imshow("r",decode)
cv2.waitKey(0)