"""
WSGI config for FaceV1 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FaceV1.settings')

application = get_wsgi_application()

#from dl.model_serverX import classify_process
#import multiprocessing

#model_server = multiprocessing.Process(target=classify_process)
#model_server.daemon = True
#model_server.start()

#from dl.FaceEngine import FaceEngine

#faceEngine = FaceEngine()

#faceEngine.openCapture("rtsp://admin:Adminadmin@192.168.1.201:554/cam/realmonitor?channel=1&subtype=0")
#faceEngine.faceVideo()

