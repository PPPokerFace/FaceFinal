from django.db import models


# Create your models here.
class Test(models.Model):
    """测试类"""

    class Meta:
        verbose_name_plural = '测试'

    name = models.CharField(max_length=16)
    age = models.IntegerField()


class Student(models.Model):
    """学生类"""

    class Meta:
        verbose_name_plural = '学生管理'
        verbose_name = '学生'

    stu_number = models.CharField(max_length=10, verbose_name='学号', primary_key=True)
    province = models.CharField(max_length=10, verbose_name='省份')
    class_stu = models.ForeignKey('Class', on_delete=models.CASCADE, verbose_name='班级')
    college = models.ForeignKey('College', on_delete=models.CASCADE, verbose_name='学院')
    name = models.CharField(max_length=16, verbose_name='姓名')
    GENGER_CHOLICE = (
        ('男', '男'),
        ('女', '女'),
    )
    gender = models.CharField(max_length=2, choices=GENGER_CHOLICE, verbose_name='性别')
    id_number = models.CharField(max_length=18, verbose_name='身份证')
    dormitory = models.ForeignKey('Dormitory', on_delete=models.CASCADE, verbose_name='宿舍')

    def __str__(self):
        return str(self.stu_number)


class Dormitory(models.Model):
    """宿舍楼"""

    class Meta:
        verbose_name_plural = '宿舍管理'
        verbose_name = '宿舍'

    name = models.CharField(max_length=20, primary_key=True)

    def __str__(self):
        return str(self.name)


# class DormitoryNumber(models.Model):
#     """宿舍号"""
#     number = models.IntegerField()
#     dormitory = models.ForeignKey('Dormitory', on_delete=models.CASCADE)
#     def __str__(self):
#         return str(self.dormitory.number)+"-"+str(self.number)


class Class(models.Model):
    """班级"""

    class Meta:
        verbose_name_plural = '班级管理'
        verbose_name = '班级'

    name = models.CharField(max_length=16, primary_key=True)
    college = models.ForeignKey('College', on_delete=models.CASCADE)
    # master = models.CharField(max_length=16, null=True)  # 班主任
    # instructor = models.CharField(max_length=16, null=True)  # 辅导员

    def __str__(self):
        return self.name


class College(models.Model):
    """学院"""

    class Meta:
        verbose_name_plural = '学院管理'
        verbose_name = '学院'

    name = models.CharField(max_length=16, primary_key=True)
    # president = models.CharField(max_length=16, null=True)

    def __str__(self):
        return self.name


class YearCheckInEvent(models.Model):
    """每年的签到事件"""

    class Meta:
        verbose_name_plural = '签到事件管理'
        verbose_name = '签到事件'

    year = models.IntegerField(unique=True,verbose_name='年份')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    student = models.ManyToManyField(Student, through='YearCheckInData', verbose_name='学生')

    def __str__(self):
        return str(self.year)


class YearCheckInData(models.Model):
    """每年的签到事件数据"""

    class Meta:
        verbose_name_plural = '签到数据管理'
        verbose_name = '签到数据'

    year_check_in_event = models.ForeignKey('YearCheckInEvent', on_delete=models.CASCADE, blank=True, null=True,verbose_name='年份')
    student = models.ForeignKey('Student', on_delete=models.CASCADE, blank=True, null=True,verbose_name='学生')
    time = models.DateTimeField(blank=True, null=True,verbose_name='签到时间')
    checked = models.BooleanField(default=False,verbose_name='是否签到')

    def __str__(self):
        return str(self.student)


class PublicInfo(models.Model):
    """信息公示"""

    class Meta:
        verbose_name_plural = '信息公示管理'
        verbose_name = '公告'

    title = models.CharField(max_length=50)
    text = models.CharField(max_length=100)


class PostCard(models.Model):
    """帖子"""

    class Meta:
        verbose_name_plural = '帖子管理'
        verbose_name = '帖子'

    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    title = models.CharField(max_length=20)
    text = models.CharField(max_length=100)
    time = models.DateTimeField()


class Comment(models.Model):
    """评论"""

    class Meta:
        verbose_name_plural = '评论管理'
        verbose_name = '评论'

    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    post_card = models.ForeignKey('PostCard', on_delete=models.CASCADE)
    text = models.CharField(max_length=100)
    time = models.DateTimeField()
