from django.http import response
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from django.apps import AppConfig
import psycopg2
from django.db import connection
import json
import time
from datetime import datetime

class AppConfig(AppConfig):
    name = 'app'

playlist_num=10
cursor=connection.cursor()
class User():
    # 用户类
    def __init__(self,usrname,password,birth,sex,request):
        global playlist_num
        print(playlist_num)
        self.usrname=usrname
        self.password=password
        self.birth=birth
        self.sex=sex
        try:
            # 触发器
            print(1)
            playlist_num=playlist_num+1
            print(playlist_num)
            sql="insert into playlist(playlist_id,playlist_name,num) values('{}','{}','{}')".format(playlist_num,'我喜欢',0)
            try:
                cursor.execute(sql)
                connection.commit()
                print("我喜欢歌单插入成功")
            except:
                connection.rollback()
                print("我喜欢歌单触发器失效")
            print(datetime.now().date())
            sql="insert into playlist_belong(playlist_id,usrname,create_time) values('{}','{}','{}')".format(playlist_num,usrname, datetime.now().date())
            try:
                print(1)
                cursor.execute(sql)
                connection.commit()
                print("歌单关系触发器成功")
            except:
                print(2)
                connection.rollback()
                print("歌单关系触发器失败")
            print(playlist_num)
        except:
            connection.rollback()
            print("插入失败")