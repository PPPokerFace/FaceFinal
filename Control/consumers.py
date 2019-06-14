# chat/consumers.py
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
import json
from dl.FaceEngine import FaceEngine
import asyncio
import time
from threading import Thread
import cv2


class WelcomeDataShowConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = 'welcomeData'
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name,
        )
        self.close()

    def receive(self, text_data):
        async_to_sync(self.send)(text_data=json.dumps(
            text_data
        ))

    def welcome_data(self, event):
        text_data = event['message']
        # Send message to WebSocket
        self.send(text_data=text_data)
