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
IMAGE_PATH = "jemma.png"

# initialize the number of requests for the stress test along with
# the sleep amount between requests
NUM_REQUESTS = 500
SLEEP_COUNT = 0.05

def call_predict_endpoint(n):
	# load the input image and construct the payload for the request

	#image = open(IMAGE_PATH, "rb").read()
	image_np=cv2.imread(IMAGE_PATH)
	image = cv2.imencode('.jpg', image_np)[1]
	image_code = str(base64.b64encode(image))[2:-1]
	payload = {"image": image_code}

	# submit the request
	r = requests.post(KERAS_REST_API_URL, data=payload,verify=False).json()

	# ensure the request was sucessful
	if r["success"]:
		print("[INFO] thread {} OK".format(n))

	# otherwise, the request failed
	else:
		print("[INFO] thread {} FAILED".format(n))

# loop over the number of threads
for i in range(0, NUM_REQUESTS):
	# start a new thread to call the API
	t = Thread(target=call_predict_endpoint, args=(i,))
	t.daemon = True
	t.start()
	time.sleep(SLEEP_COUNT)

# insert a long sleep so we can wait until the server is finished
# processing the images
time.sleep(300)