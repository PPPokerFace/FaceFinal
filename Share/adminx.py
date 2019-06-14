#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "FaceV1"
__date__ = "3/1/19 10:41"

import xadmin
from xadmin import views
from Share.models import *


class TestAdmin:
    list_display = ("name", "age",)
    search_fields = ("name", "age",)
    list_filter = ("name", "age",)


class StudentAdmin:
    list_display = ("name", "gender", "id_number", "college", "class_stu",)
    search_fields = ("name", "gender", "id_number", "college", "class_stu",)
    list_filter = ("name", "gender", "id_number", "college", "class_stu",)


# class DormitoryAdmin:
#     list_display = ("number",)
#     search_fields = ("number",)
#     list_filter = ("number",)


# class DormitoryNumberAdmin:
#     list_display = ("number", "dormitory",)
#     search_fields = ("number", "dormitory",)
#     list_filter = ("number", "dormitory",)


class ClassAdmin:
    list_display = ("name", "college",)
    search_fields = ("name", "college",)
    list_filter = ("name", "college",)


class CollegeAdmin:
    list_display = ("name",)
    search_fields = ("name",)
    list_filter = ("name",)


class YearCheckInEventAdmin:
    list_display = ("year", "start_time", "end_time",)
    search_fields = ("year", "start_time", "end_time",)
    list_filter = ("year", "start_time", "end_time",)


class YearCheckInDataAdmin:
    list_display = ("year_check_in_event", "student", "time",)
    search_fields = ("year_check_in_event", "student", "time",)
    list_filter = ("year_check_in_event", "student", "time",)


class PublicInfoAdmin:
    list_display = ("title", "text",)
    search_fields = ("title", "text",)
    list_filter = ("title", "text",)


class PostCardAdmin:
    list_display = ("student", "title", "text", "time",)
    search_fields = ("student", "title", "text", "time",)
    list_filter = ("student", "title", "text", "time",)


class CommentAdmin:
    list_display = ("student", "text", "time",)
    search_fields = ("student", "text", "time",)
    list_filter = ("student", "text", "time",)


class BaseSetting:
    enable_themes = False
    use_bootswatch = True
    site_title = "F A C E"
    site_footer = "@FACE 后台"


class GlobalSettings(object):
    site_title = "F A C E"
    site_footer = "FACE 后台"
    # menu_style = "accordion"


xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)
# 注册models
xadmin.site.register(Test, TestAdmin)
xadmin.site.register(Student, StudentAdmin)
# xadmin.site.register(Dormitory, DormitoryAdmin)
# xadmin.site.register(DormitoryNumber, DormitoryNumberAdmin)
xadmin.site.register(Class, ClassAdmin)
xadmin.site.register(College, CollegeAdmin)
xadmin.site.register(YearCheckInEvent, YearCheckInEventAdmin)
xadmin.site.register(YearCheckInData, YearCheckInDataAdmin)
xadmin.site.register(PublicInfo, PublicInfoAdmin)
xadmin.site.register(PostCard, PostCardAdmin)
xadmin.site.register(Comment, CommentAdmin)
