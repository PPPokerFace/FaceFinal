import base64
import sys
import numpy as np
import cv2
import hashlib

def base64_encode(array):
    # base64 encode the input NumPy array
    return base64.b64encode(array).decode("utf-8")


def base64_decode(array, dtype):
    # if this is Python 3, we need the extra step of encoding the
    # serialized NumPy string as a byte object
    if sys.version_info.major == 3:
        a = bytes(array, encoding="utf-8")

    # convert the string to a NumPy array using the supplied data
    # type and target shape
    a = np.frombuffer(base64.decodebytes(array), dtype=dtype)
    return a


def base64_encode_image(img):
    img = cv2.imencode('.jpg', img)[1]
    img = str(base64.b64encode(img))[2:-1]
    return img


def base64_decode_image(img_data):
    img_b64decode = base64.b64decode(img_data)
    img_array = np.frombuffer(img_b64decode, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return img


def data_cast(data):
    return True if str(bool(data)).lower() == "true" else False

def GetFileMd5(file):
    if isinstance(file,str):
        f=open(file,"rb")
    else:
        f=file.file
    hash_val = hashlib.md5()
    while True:
        b = f.read(8096)
        if not b:
            break
        hash_val.update(b)
    if isinstance(file,str):
        f.close()
    return hash_val.hexdigest()
