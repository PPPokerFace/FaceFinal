#!/usr/bin/env python
import os
import sys
import multiprocessing
from threading import Thread
from Control.dataShowListener import getData
from dl.model_serverX import classify_process

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FaceV1.settings')
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    model_server = multiprocessing.Process(target=classify_process)
    model_server.daemon = True
    model_server.start()

    getDataThread = Thread(target=getData)
    getDataThread.daemon = True
    getDataThread.start()

    execute_from_command_line(sys.argv)


