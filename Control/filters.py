import django_filters
from django_filters import rest_framework as filters
from Share.models import *


class StudentFilters(filters.FilterSet):
    class Meta:
        model = Student
        fields = "__all__"


class YearCheckInEventFilters(filters.FilterSet):
    class Meta:
        model = YearCheckInEvent
        fields = ['year', ]


class YearCheckInDataFilters(filters.FilterSet):
    ordering_fields = ('time', 'id')

    class Meta:
        model = YearCheckInData
        fields = "__all__"


class PublicInfoFilters(filters.FilterSet):
    class Meta:
        model = PublicInfo
        fields = "__all__"


class PostCardFilters(filters.FilterSet):
    class Meta:
        model = PostCard
        fields = "__all__"


class CommentFilters(filters.FilterSet):
    class Meta:
        model = Comment
        fields = "__all__"
