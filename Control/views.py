import json
import os
from pathlib import Path

from django.http import JsonResponse, HttpResponse
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics, mixins, viewsets
from Share.models import *
from Share import helper
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import *
from .filters import *
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.permissions import BasePermission
from rest_framework.parsers import MultiPartParser
from django.conf import settings
import zipfile
import cv2
import numpy as np
import base64
import datetime
import uuid
import requests
import redis


# Create your views here.
class StudentPagoination(PageNumberPagination):
    """学生分页器"""
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'p'
    max_page_size = 100


class StudentViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """学生ViewSet"""
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    pagination_class = StudentPagoination
    filter_backends = (DjangoFilterBackend,)
    filter_class = StudentFilters
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class YearCheckInTimePermission(BasePermission):
    def has_permission(self, request, view):
        if request.method is "PUT":
            obj = YearCheckInEvent.objects.get(year=datetime.datetime.now().year)
            start_time = obj.start_time
            end_time = obj.end_time
            if start_time < datetime.datetime.now() < end_time:
                return True
            else:
                return False
        return True

class YearCheckInDataPagoination(PageNumberPagination):
    """新生签到分页器"""
    page_size = 15
    page_size_query_param = 'page_size'
    page_query_param = 'p'
    # max_page_size = 5


class YearCheckInDataViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.CreateModelMixin,
                             mixins.DestroyModelMixin,
                             mixins.UpdateModelMixin,
                             viewsets.GenericViewSet):
    """新生签到ViewSet"""
    queryset = YearCheckInData.objects.all()
    serializer_class = YearCheckInDataSerializer
    pagination_class = YearCheckInDataPagoination
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filter_class = YearCheckInDataFilters
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,YearCheckInTimePermission,)


class YearCheckInEventPagoination(PageNumberPagination):
    """新生签到分页器"""
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'p'
    max_page_size = 100


class YearCheckInEventViewSet(mixins.ListModelMixin,
                              mixins.RetrieveModelMixin,
                              mixins.CreateModelMixin,
                              mixins.DestroyModelMixin,
                              mixins.UpdateModelMixin,
                              viewsets.GenericViewSet):
    """新生签到ViewSet"""
    queryset = YearCheckInEvent.objects.all()
    serializer_class = YearCheckInEventSerializer
    pagination_class = YearCheckInEventPagoination
    filter_backends = (DjangoFilterBackend,)
    filter_class = YearCheckInEventFilters
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class PublicInfoPagoination(PageNumberPagination):
    """新生签到分页器"""
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'p'
    max_page_size = 100


class PublicInfoViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    queryset = PublicInfo.objects.all()
    serializer_class = PublicInfoSerializer
    pagination_class = PublicInfoPagoination
    filter_backends = (DjangoFilterBackend,)
    filter_class = PublicInfoFilters
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class PostCardPagoination(PageNumberPagination):
    """新生签到分页器"""
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'p'
    max_page_size = 100


class PostCardViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):
    queryset = PostCard.objects.all()
    serializer_class = PostCardSerializer
    pagination_class = PostCardPagoination
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filter_class = PostCardFilters
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class CommentPagoination(PageNumberPagination):
    """新生签到分页器"""
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'p'
    max_page_size = 100


class CommentViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = CommentPagoination
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filter_class = CommentFilters
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class UploadImage(APIView):
    parser_classes = (MultiPartParser,)
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        db = redis.StrictRedis(host=settings.REDIS_HOST,
                               port=settings.REDIS_PORT, db=settings.REDIS_DB)
        loadFile = request.FILES["file"]

        if loadFile._name.endswith(".zip") and request._user.is_superuser:
            files = zipfile.ZipFile(loadFile, 'r')
            stu_list = Student.objects.all()
            for file in files.namelist():
                id_number = stu_list.get(stu_number=file._name.split('.')[0])
                files.extract(file, os.path.join("media", str(datetime.datetime.now().year), id_number,
                                                 str(uuid.uuid4()) + file._name.split('.')[1]))
            db.set("hnswUpdateSignal", 1)
            return Response("ok")
        else:
            from PIL import Image
            im_pic = Image.open(loadFile)
            img = cv2.cvtColor(np.asarray(im_pic), cv2.COLOR_RGB2BGR)
            from Share.helper import base64_encode_image
            img_encode = base64_encode_image(img)

            # submit the request
            save_dir = os.path.join("media", str(datetime.datetime.now().year), request._user.username)
            if not os.path.isdir(save_dir):
                os.mkdir(save_dir)
            filename = str(uuid.uuid4()) + '.' + loadFile._name.split('.')[-1]
            cv2.imwrite(os.path.join(save_dir, filename), img)
            md5 = helper.GetFileMd5(os.path.join(save_dir, filename))
            hnswDict = db.get("hnswDict")
            if hnswDict is not None:
                hnswDict = json.loads(hnswDict)
                if md5 in hnswDict and request._user.username in hnswDict[md5]["name"]:
                    return HttpResponse(content="File exists", status=500)

            data = {"image": img_encode,
                    "name": request._user.username,
                    "detected": 0,
                    "recognize": 0,
                    "face": [],
                    "savePic": 0,
                    "saveVec": 1,
                    "md5": md5
                    }
            r = requests.post("http://127.0.0.1:8000/face-recognition/", data=json.dumps(data), verify=False).json()

            return Response("no!")

    def get(self, request):
        img_dir = os.path.join("media", str(datetime.datetime.now().year), request._user.username)
        pathDir = Path(img_dir)
        # img_num = 1
        data = []
        if os.path.isdir(img_dir):
            for person in pathDir.iterdir():
                if person.is_file():
                    img = cv2.imread(str(person))
                    # 非图片文件或读取文件失败
                    if img is None:
                        continue
                    height, width = img.shape[:2]
                    img_small = cv2.resize(img, (240 * width // height, 240))
                    from Share.helper import base64_encode_image
                    img_encode = base64_encode_image(img_small)
                    img_data = {}
                    img_data['name'] = person.name
                    img_data['img'] = img_encode
                    # img_num += 1
                    data.append(img_data)
        return JsonResponse({'results': data})

    def delete(self, request):
        body = json.loads(request.body)
        img_name = body['name']
        img_dir = os.path.join("media", str(datetime.datetime.now().year), request._user.username, img_name)
        try:
            md5 = helper.GetFileMd5(img_dir)
            os.remove(img_dir)
            data = {
                'md5': md5,
                'name': request._user.username,
            }
            r = requests.post("http://127.0.0.1:8000/face-delete/", data=json.dumps(data), verify=False).json()
            return JsonResponse({'results': "Yes"})
        except:
            return JsonResponse({'results': "No"})


class TokenToUser(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        json = {'isSuperUser': request.user.is_superuser}
        return JsonResponse(json)


class IsImageUploadThisYear(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        json = {'IsImageUploadThisYear': os.path.exists('media/' + str(datetime.datetime.now().year))}
        return JsonResponse(json)


class AuthUser(APIView):
    def post(self, request):
        from django.contrib.auth.models import User
        from django.contrib.auth.hashers import make_password
        uusername = request.data["username"]
        ppassword = request.data["password"]
        if Student.objects.filter(id_number=uusername).count() > 0:
            User.objects.create(
                username=str(uusername),
                password=make_password(ppassword, None, 'pbkdf2_sha256')
            )
        return JsonResponse({'re': 'ok'})


class WelcomeDataShow(APIView):
    def get(self, request):
        data = {
            'water_percent_data': {
                'percent': 0,
            },
            'map_data': {
                'rows': []
            },
            'college_process_data': {
                'rows': []
            },
            'process_order_data': {
                'rows': []
            }
        }
        # 获取报道信息
        year_event = YearCheckInEvent.objects.first()
        year_data = year_event.yearcheckindata_set.all()
        # 获取学院信息
        college_list = College.objects.all()
        # 统计地区人数
        student_list = Student.objects.filter(stu_number__gt=2017000000)
        province_list = [stu['province'] for stu in student_list.values('province').distinct()]
        for pro in province_list:
            row = {
                '位置': pro,
                '人数': student_list.filter(province=pro).count()
            }
            data['map_data']['rows'].append(row)
        # 统计报道情况
        student_count_all = year_data.count()
        student_checked_count_all = year_data.filter(checked=True).count()
        data['water_percent_data']['percent'] = student_checked_count_all // student_count_all
        # 统计学院报道人数
        for college in college_list:
            row = {
                '学院': college.name,
                '学院人数': student_list.filter(college=college).count(),
                '报道人数': year_data.filter(student__college=college, checked=True).count(),
            }
            row['报道率'] = row['报道人数'] / row['学院人数']
            data['college_process_data']['rows'].append(row)
        # 统计报道率
        for dat in data['college_process_data']['rows']:
            row = {
                '学院': dat['学院'],
                '百分': 100,
                '报道率': dat['报道率']
            }
            data['process_order_data']['rows'].append(row)
        # return JsonResponse(json.dumps(data),safe=False)
        return JsonResponse(data)
