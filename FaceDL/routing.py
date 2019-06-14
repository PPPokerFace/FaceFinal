# chat/routing.py
from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url('ws/monitor/', consumers.ImageConsumer),
    url('ws/face-recognition/',consumers.FaceRecognitionConsumer),
]