import asyncio
import json
import time

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.http.response import JsonResponse


def getData():
    time.sleep(20)

    from Share.models import YearCheckInEvent, College, Student
    while True:
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
        data['water_percent_data']['percent'] = student_checked_count_all / student_count_all
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
                '报道率': dat['报道率'] * 100
            }
            data['process_order_data']['rows'].append(row)

        # return JsonResponse(json.dumps(data),safe=False)
        # channel_layer =
        data = json.dumps(data)
        async_to_sync(get_channel_layer().group_send)(
            'welcomeData',
            {
                'type': 'welcome.data',
                'message': data
            }
        )
        time.sleep(10)
