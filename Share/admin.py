import datetime
import sys
import traceback

from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.utils.encoding import force_text
from import_export.admin import ImportExportModelAdmin, ExportMixin
from import_export import resources
from import_export.fields import Field
from django.contrib import admin
import django.forms as forms
from import_export.widgets import Widget

from Share.models import Test, Student, Dormitory, Class, College, YearCheckInEvent, YearCheckInData, PublicInfo, \
    PostCard, Comment


class TestAdmin(ImportExportModelAdmin):
    list_display = ("name", "age",)
    search_fields = ("name", "age",)
    list_filter = ("name", "age",)


class StudentResources(resources.ModelResource):
    class Meta:
        model = Student
        fields = ("stu_number", "province", "class_stu", "college", "name", "gender", "id_number", "dormitory")
        import_id_fields = ('stu_number',)


class StudentAdmin(ImportExportModelAdmin):
    list_display = ("name", "gender", "id_number", "college", "class_stu", 'dormitory',)
    search_fields = ("name", "gender", "id_number", "college", "class_stu", 'dormitory',)
    list_filter = ("gender", "college", "class_stu", 'dormitory',)
    resource_class = StudentResources


class DormitoryResources(resources.ModelResource):
    class Meta:
        model = Dormitory
        fields = ("name",)
        import_id_fields = ('name',)


class DormitoryAdmin(ImportExportModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    list_filter = ("name",)
    resource_class = DormitoryResources


class ClassResources(resources.ModelResource):
    class Meta:
        model = Class
        fields = ("name", "college",)
        import_id_fields = ('name',)


class ClassAdmin(ImportExportModelAdmin):
    list_display = ("name", "college",)
    search_fields = ("name", "college",)
    list_filter = ("name", "college",)
    resource_class = ClassResources


class CollegeResources(resources.ModelResource):
    class Meta:
        model = College
        fields = ("name",)
        import_id_fields = ('name',)


class CollegeAdmin(ImportExportModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    list_filter = ("name",)
    resource_class = CollegeResources


class YearCheckInDataInline(admin.TabularInline):
    model = YearCheckInData
    extra = 1


class YearCheckInEventAdminForm(forms.ModelForm):
    stus = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(),
        widget=FilteredSelectMultiple('Student', False))

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            initial = kwargs.setdefault('initial', {})
            try:
                initial['stus'] = [t.student.pk for t in kwargs['instance'].yearcheckindata_set.all()]
            except:
                pass
        forms.ModelForm.__init__(self, *args, **kwargs)

    def save(self, commit=True):
        instance = forms.ModelForm.save(self, commit)

        old_save_m2m = self.save_m2m

        def save_m2m():
            old_save_m2m()

            stus = [s for s in self.cleaned_data['stus']]
            for mf in instance.yearcheckindata_set.all():
                if mf.student not in stus:
                    mf.delete()
                else:
                    stus.remove(mf.student)

            for stu in stus:
                YearCheckInData.objects.create(student=stu, year_check_in_event=instance)

        self.save_m2m = save_m2m

        return instance

    class Meta:
        model = Student
        fields = "__all__"


class YearCheckInEventAdmin(ImportExportModelAdmin):
    list_display = ("year", "start_time", "end_time",)
    search_fields = ("year", "start_time", "end_time",)
    list_filter = ("year", "start_time", "end_time",)
    form = YearCheckInEventAdminForm


def ChangeData(modeladmin, request, queryset):
    queryset.update(checked=True,time=datetime.datetime.now())


ChangeData.short_description = "一键签到"


class YearCheckInDataAdmin(ImportExportModelAdmin):
    list_display = ("year_check_in_event", "student", "time",)
    search_fields = ("year_check_in_event", "student", "time",)
    list_filter = ("year_check_in_event", "time",)
    actions = [ChangeData, ]


class PublicInfoAdmin(ImportExportModelAdmin):
    list_display = ("title", "text",)
    search_fields = ("title", "text",)
    list_filter = ("title", "text",)


class PostCardAdmin(ImportExportModelAdmin):
    list_display = ("student", "title", "text", "time",)
    search_fields = ("student", "title", "text", "time",)
    list_filter = ("student", "title", "text", "time",)


class CommentAdmin(ImportExportModelAdmin):
    list_display = ("student", "text", "time",)
    search_fields = ("student", "text", "time",)
    list_filter = ("student", "text", "time",)


admin.site.site_header = 'F A C E'  # 此处设置页面显示标题
admin.site.site_title = 'FACE'  # 此处设置页面头部标题

admin.site.register(Test, TestAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Dormitory, DormitoryAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(College, CollegeAdmin)
admin.site.register(YearCheckInEvent, YearCheckInEventAdmin)
admin.site.register(YearCheckInData, YearCheckInDataAdmin)
admin.site.register(PublicInfo, PublicInfoAdmin)
admin.site.register(PostCard, PostCardAdmin)
admin.site.register(Comment, CommentAdmin)

# class PasswordWidget(Widget):
#     def clean(self, value):
#         return make_password(value, None, 'pbkdf2_sha256')
#
#     def render(self, value, obj):
#         return force_text(value)
#
#
# class UserResource(resources.ModelResource):
#     password = Field(column_name='password', attribute='password', widget=PasswordWidget())
#
#     class Meta:
#         model = User
#         fields = ('password', 'id', 'username',)
#         import_id_fields = ('id',)
#
#     def before_import(self, dataset, using_transactions, dry_run, **kwargs):
#         lastId = User.objects.latest('id')
#         col = []
#         for i in range(dataset.height):
#             col.append(lastId.id + i + 1)
#         # for data in dataset:
#         #     data[0] = make_password(data[0])
#         dataset.insert_col(0, col=col, header="id")
#
#
# class UserrAdmin(ImportExportModelAdmin, UserAdmin):
#     resource_class = UserResource
#
#
# admin.site.unregister(User)
# admin.site.register(User, UserrAdmin)
