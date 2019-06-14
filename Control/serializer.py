# django rest framework 序列化
from rest_framework import serializers
from Share.models import *


class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = "__all__"


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = "__all__"


class StudentSerializer(serializers.ModelSerializer):
    class_info = ClassSerializer(source='class_stu', read_only=True)
    college_info = CollegeSerializer(source='college', read_only=True)

    class Meta:
        model = Student
        fields = "__all__"


class YearCheckInEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = YearCheckInEvent
        fields = "__all__"


class YearCheckInDataSerializer(serializers.ModelSerializer):
    student_info = StudentSerializer(source='student', read_only=True)

    class Meta:
        model = YearCheckInData
        fields = "__all__"


class PublicInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicInfo
        fields = "__all__"


class PostCardSerializer(serializers.ModelSerializer):
    student_info = StudentSerializer(source='student', read_only=True)

    class Meta:
        model = PostCard
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    postcard_info = PostCardSerializer(source='postcard', read_only=True)
    student_info = StudentSerializer(source='student', read_only=True)

    class Meta:
        model = Comment
        fields = "__all__"
