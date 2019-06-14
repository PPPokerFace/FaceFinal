class config():
    def __init__(self):
        self.redisHost = "localhost"
        self.redisPort = 6379
        self.redisDb = 0

        self.yoloCfg='face-yolov3-tiny.cfg'
        self.yoloModel= 'tiny.pt'

        self.useMobileFaceNet = True


try:
    from django.conf import settings
    class configDjango():
        def __init__(self):
            self.redisHost=settings.REDIS_HOST
            self.redisPort=settings.REDIS_PORT
            self.redisDb=settings.REDIS_DB


except:
    pass


