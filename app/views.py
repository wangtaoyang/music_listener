from django.http import response
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

import psycopg2
from django.db import connection
import json
import time
from datetime import datetime

# Create your views here.


cursor=connection.cursor()
playlist_num=5
@require_http_methods(["POST","GET"])
def login(request):
    print("进入login函数")
    global playlist_num
    response_text=HttpResponse()
    if(request.method =="GET"):
        return render(request,"login.html")
    elif(request.method =="POST"):
        print(request.POST)
        usrname=request.POST.get("usrname")
        password=request.POST.get("password")
        if usrname=="superadmin" and password=="19307130147":
            # 超级管理员
            return render(request,"superadmin.html")
        else: 
            sql="select password from user_info where usrname='{}'".format(usrname)
            print(sql)
            cursor.execute(sql)
            real_password=cursor.fetchall()
            print(real_password[0][0])
            # 从数据库获取密码
            if password !=real_password[0][0]:
                response_text="密码错误，请重新输入"
                return render(request,"login.html",{'response':response_text})
            else:
                sql="select playlist_id,playlist_name,num from playlist_belong natural join playlist where usrname='{}'".format(usrname)
                cursor.execute(sql)
                my_playlist=cursor.fetchall()
                sql="select playlist_id,playlist_name,num,usrname from playlist_belong natural join playlist where is_recommend= true"
                cursor.execute(sql)
                recommend_playlist=cursor.fetchall()
                print(my_playlist)
                print(recommend_playlist)
                return render(request,"hello.html",{'usrname':usrname,'myplaylist':my_playlist,'recommand':recommend_playlist})

def hello(request):
    return render(request,"hello.html")

def superadmin(request):
    return render(request,"superadmin.html")

@require_http_methods(["POST","GET"])
def insert_usrinfo(request):
    global playlist_num
    response_text=HttpResponse()
    if(request.method == "GET"):
            return render(request,"register.html")
    elif(request.method =="POST"):
            print(request.POST)
            print(playlist_num)
            usrname=request.POST.get('usrname')
            password=request.POST.get('password')
            birth=request.POST.get('birth')
            sex=request.POST.get('sex')
            if sex=='m':
                sex='男'
            else:
                sex='女'
            if usrname==''  :
                response_text="请填写完整信息"
                return  render(request,'register.html',{'response':response_text})
            else :
                sql="INSERT INTO public.user_info(usrname,password,birth,sex) VALUES ('{}','{}','{}','{}')".format(usrname,password,birth,sex)
                try:
                    cursor.execute(sql)
                    connection.commit()
                    playlist_num=playlist_num+1
                    print(playlist_num)
                    response_text.content=""
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
                    print(response_text)
                    render(request,'register.html',{'response':response_text})
                    return render(request,'login.html',{'response':response_text})
                except:
                    connection.rollback()
                    response_text="执行失败,存在重复的用户名"
                    print(response_text)
                    return render(request,'register.html',{'response':response_text})




# 检查usrname是否在数据库中    
# def login_info(request):
#     print(request.GET)
#     name = request.GET.get('name')
#     password =request.GET.get('pwd')

#     if not all([name,password]):
#         return HttpResponse('数据不完整请重新输入')

#     try:
#         obj1=UserInfo2.objects.creat(name=name,password=password)
#     except Exception as e:
#         return HttpResponse('注册失败')
#     return HttpResponse('ok')



# def register(request):
#     if request== 'POST'
