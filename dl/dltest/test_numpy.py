import numpy as np
import json
import sys

sys.path.append("..")
import base64


def base64_encode_image(a):
    # base64 encode the input NumPy array
    return base64.b64encode(a).decode("utf-8")


def base64_decode_image(a, dtype, shape):
    # if this is Python 3, we need the extra step of encoding the
    # serialized NumPy string as a byte object
    if sys.version_info.major == 3:
        a = bytes(a, encoding="utf-8")

    # convert the string to a NumPy array using the supplied data
    # type and target shape
    a = np.frombuffer(base64.decodebytes(a), dtype=dtype)
    return a


a = np.array([1, 2, 3, 4, 5])
a = base64_encode_image(a)
if sys.version_info.major == 3:
    a = bytes(a, encoding="utf-8")
a = np.frombuffer(base64.decodebytes(a),dtype=int)

print(a)
