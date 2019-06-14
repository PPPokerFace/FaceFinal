"""FaceV1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path, include
import xadmin
from django.contrib import admin
from Control.views import *
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
# django官方文档
from rest_framework.documentation import include_docs_urls
from FaceDL.views import FaceRecognition, ObjectDetectionMetrics, FaceDelete

router = DefaultRouter()
# 学生列表ViewSet
router.register('students', StudentViewSet)
router.register('yearcheckinevent', YearCheckInEventViewSet)
router.register('yearcheckindata', YearCheckInDataViewSet)
router.register('publicinfo', PublicInfoViewSet)
router.register('postcard', PostCardViewSet)
router.register('comment', CommentViewSet)
urlpatterns = [
    path('admin/', admin.site.urls),
    # path('admin/', xadmin.site.urls),
    # 注册Router
    path('', include(router.urls)),
    # official
    path('docs/', include_docs_urls(title="FaceV")),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', views.obtain_auth_token),
    # 额外的
    path('upload-image/', UploadImage.as_view()),
    path('token-to-user/', TokenToUser.as_view()),
    path('is-image-upload-this-year/', IsImageUploadThisYear.as_view()),
    path('auth-user/', AuthUser.as_view()),
    path('welcome-data-show/', WelcomeDataShow.as_view()),

    path('face-recognition/', FaceRecognition.as_view()),
    path('face-delete/', FaceDelete.as_view()),
    path('object-detection-metrics/', ObjectDetectionMetrics.as_view()),
]
