# FaceFinal Backend

## Introduction
FaceFinal系统的后端系统，由Django框架编写。

本作品为毕业设计作品开源，核心功能模块不再维护更新。

除去本项目外，本系统还包括[前端](https://github.com/PPPokerFace/FaceVue)配置和[反向代理](https://github.com/PPPokerFace/FaceCaddy)配置项。

## Install 

0. Something
- 后端开启6379端口下的`Redis`服务，要求`Redis>=5.0.0`
- 后端开启3306端口下的`MySQL`服务，相关配置项由`settings.py`下`DATABASES`字段配置

1. Run
- `pip3 install -U -r requirements.txt` 
- `python manage.py makemigrations`
- `python manage.py migrate`
- `python manage.py createsuperuser`

2. Download the model 
- [google drive](https://drive.google.com/open?id=1KWzI2R1mXGnF6e2TVEKdhVFQuEkXkKzD)

3. Run
- `python manage.py runserver --noreload 8000`
- use the address: http://127.0.0.1:8000/
- admin page: http://127.0.0.1:8000/admin


## Recent Update
#### 2019.6.14
- 修复一些细微的bug
- 最终版本上传

#### 2019.6.4
- 毕业答辩版本上传

#### 2019.5.17
- 作品验收版本上传

#### 2019.5.4
- 增加了删除照片的功能
- 优化了消息队列的算法

#### 2019.5.2
- 支持单张图片多人脸的情况
- 引入了Redis-Stream作为消息队列

## Author
[zhaoyonghang](https://github.com/zhaoyonghang)
[ty](https://github.com/tyIceStream)