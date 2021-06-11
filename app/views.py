import re
from django import http
from django.http import response
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators import csrf
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import psycopg2
from django.db import connection
import json
import time
from datetime import datetime

# Create your views here.


cursor=connection.cursor()
@require_http_methods(["POST","GET"])
def login(request):
    print("进入login函数")
    response_text=HttpResponse()
    if(request.method =="GET"):
        return render(request,"login.html")
    elif(request.method =="POST"):
        print(request.POST)
        usrname=request.POST.get("usrname")
        password=request.POST.get("password")
        rank=request.POST.get("rank")
        if rank=="super":
            # 超级管理员
            sql="select password from super_user_info where usrname='{}'".format(usrname)
            print(sql)
            cursor.execute(sql)
            real_password=dictfetchall(cursor)
            # 从数据库获取密码
            if len(real_password)==0 or password !=real_password[0]["password"] :
                response_text="用户名或密码错误，请重新输入"
                return render(request,"login.html",{'response':response_text})
            else:
                res=HttpResponseRedirect('/superadmin')
                res.set_cookie('usrname',usrname,36000)
                return res
            # return render(request,"superadmin.html")
        else: 
            sql="select password from user_info where usrname='{}'".format(usrname)
            print(sql)
            cursor.execute(sql)
            real_password=dictfetchall(cursor)
            # 从数据库获取密码
            if len(real_password)==0 or password !=real_password[0]["password"]:
                response_text="密码错误，请重新输入"
                return render(request,"login.html",{'response':response_text})
            else:
                res=HttpResponseRedirect('/hello')
                res.set_cookie('usrname',usrname,36000)
                return res
                # return render(request,"hello.html",{'usrname':usrname,'myplaylist':my_playlist,'recommand':recommend_playlist})
@csrf_exempt
def hello(request):
    tk=request.COOKIES.get('usrname')
    if not tk:
        return redirect('/login')
    else:
        sql="select playlist_name,num,playlist_id from playlist  where usrname='{}'".format(tk)
        print(sql)
        cursor.execute(sql)
        res_my=dictfetchall(cursor)
        sql="select playlist_id,playlist_name,num,usrname from  playlist_recommend natural join playlist"
        print(sql)
        cursor.execute(sql)
        res_re=dictfetchall(cursor)
        print(res_re)
        info={'usrname':tk,'my_playlist':res_my,'recommend_playlist':res_re}
        return render(request,"hello.html",info)

def superadmin(request):
    tk=request.COOKIES.get('usrname')
    if not tk:
        return redirect('/login')
    else:
        sql="select usrname,birth,sex from user_info except select usrname,birth,sex from super_user_info"
        cursor.execute(sql)
        usr_info=dictfetchall(cursor)
        for user in usr_info:
            user['birth']=str(user['birth'])
        print(usr_info)
        sql="select playlist_id,playlist_name,num,usrname,create_time,is_recommend from playlist"
        cursor.execute(sql)
        playlist_info=dictfetchall(cursor)
        for playlist in playlist_info:
            playlist['create_time']=str(playlist['create_time'])
        print(playlist_info)
        res={"usr_info":usr_info,"playlist_info":playlist_info}
        return render(request,"superadmin.html",res)

@csrf_exempt
def comments(request):
    print('进入comments')
    url=request.POST.get('url')
    sql="select comments_id,comment_text,usrname,name,url from comments natural join musicsystem_info where url='{}'".format(url)
    print(sql)
    cursor.execute(sql)
    res=dictfetchall(cursor)
    print(res)
    return JsonResponse(res,safe=False)

@csrf_exempt
def drop_song(request):
    print("进入drop_song")
    url=request.POST.get('url')
    singer=request.POST.get('singer')
    info=request.POST.get('info')
    # 按照歌手查询
    if info==None:
        print('按照歌手删除')
        sql="(select name,url,time,singer from musicsystem_info where singer='{}') except (select name,url,time,singer from musicsystem_info where url='{}')".format(singer,url)
        cursor.execute(sql)
        res=dictfetchall(cursor)
        sql="update playlist set num=num-1 where playlist_id in (select playlist_id from playlist natural join music_belong where url='{}')".format(url)
        # 触发器，在超级管理员删除某一首歌后，拥有该歌曲的歌单歌曲数量减少
        cursor.execute(sql)
        sql="delete from musicsystem_info where url='{}'".format(url)
        cursor.execute(sql)
        return JsonResponse(res,safe=False)
    else:
        print("按照歌名删除")
        sql="select name,singer,time,url from musicsystem_info where name like '%{}%' union select name,singer,time,url from musicsystem_info where singer like '%{}%'".format(info,info)
        print(sql)
        cursor.execute(sql)
        res=dictfetchall(cursor)
        sql="update playlist set num=num-1 where playlist_id in (select playlist_id from playlist natural join music_belong where url='{}')".format(url)
        # 触发器，在超级管理员删除某一首歌后，拥有该歌曲的歌单歌曲数量减少
        cursor.execute(sql)
        sql="delete from musicsystem_info where url='{}'".format(url)
        cursor.execute(sql)
        return JsonResponse(res,safe=False)
        
@csrf_exempt
def new_song(request):
    print("进入new_song")
    url=request.POST.get('url')
    singer=request.POST.get('singer')
    name=request.POST.get('name')
    time=request.POST.get('time')
    sql="INSERT INTO public.musicsystem_info(name, singer, \"time\", url) VALUES ('{}','{}', '{}', '{}');".format(name,singer,time,url)
    print(sql)
    try:
        cursor.execute(sql)
        res=HttpResponse("歌曲添加成功")
        return res
    except:
        res=HttpResponse("歌曲添加失败")
        return res

@csrf_exempt
def delete_comments(request):
    print("进入delete_comments")
    comments_id=request.POST.get('comments_id')
    print(comments_id)
    sql="(select comment_text,usrname,comments_id from comments where url in (select url from comments where comments_id={})) except (select comment_text,usrname,comments_id from comments where comments_id={})".format(comments_id,comments_id)
    print(sql)
    cursor.execute(sql)
    res=dictfetchall(cursor)
    print(res)
    sql="delete from comments where comments_id={}".format(comments_id)
    print(sql)
    cursor.execute(sql)
    return JsonResponse(res,safe=False)

@csrf_exempt
def make_comments(request):
    print("进入make_comments")
    url=request.POST.get('url')
    text=request.POST.get('text')
    usrname=request.POST.get('usrname')
    sql="insert into comments (comments_id,comment_text,usrname,url) values(default,'{}','{}','{}')".format(text,usrname,url)
    print(sql)
    cursor.execute(sql)
    sql="select comments_id, comment_text ,usrname from comments where url='{}'".format(url)
    print(sql)
    cursor.execute(sql)
    res=dictfetchall(cursor)
    return JsonResponse(res,safe=False)

@csrf_exempt
def set_recommend(request):
    playlist_id=request.POST.get('playlist_id')
    is_recommend=request.POST.get("is_recommend")
    recommend_usrname=request.COOKIES.get("usrname")
    print(recommend_usrname)
    print(playlist_id)
    print(is_recommend)
    if is_recommend=='false':
        sql="insert into playlist_recommend(playlist_id,recommend_date,recommend_usrname) values('{}','{}','{}')".format(playlist_id,datetime.now().date(),recommend_usrname)
        print(sql)
        cursor.execute(sql)
        sql="update playlist set is_recommend=TRUE where playlist_id='{}'".format(playlist_id)
        print(sql)
        cursor.execute(sql)
        sql="select playlist_id,playlist_name,num,usrname,create_time,is_recommend from playlist"
        cursor.execute(sql)
        playlist_info=dictfetchall(cursor)
        return JsonResponse(playlist_info,safe=False)
    else:
        sql="delete from playlist_recommend where playlist_id='{}'".format(playlist_id)
        print(sql)
        cursor.execute(sql)
        sql="update playlist set is_recommend=False where playlist_id='{}'".format(playlist_id)
        print(sql)
        cursor.execute(sql)
        sql="select playlist_id,playlist_name,num,usrname,create_time,is_recommend from playlist"
        cursor.execute(sql)
        playlist_info=dictfetchall(cursor)
        return JsonResponse(playlist_info,safe=False)

def playlist(request,p_id):
    print(p_id)
    print("进入歌单")
    usrname=request.COOKIES.get('usrname')
    print(usrname)
    sql="select usrname from playlist where playlist_id={}".format(p_id)
    cursor.execute(sql)
    res=dictfetchall(cursor)
    belong_usr=res[0]['usrname']
    print(belong_usr)
    sql="select count(*) from super_user_info where usrname='{}'".format(usrname)
    cursor.execute(sql)
    res=dictfetchall(cursor)
    print(res)
    # 本人进入或者超级管理员进入
    if usrname==belong_usr or res[0]['count']!=0:
        sql="select name,singer,time,url from music_belong natural join musicsystem_info where playlist_id={}".format(p_id)
        print(sql)
        cursor.execute(sql)
        res=dictfetchall(cursor)
        print(res)
        return render(request,"playlist.html",{'id':p_id,'res':res,'usrname':usrname})
    # 别人进入
    else :
        sql="select name,singer,time,url from music_belong natural join musicsystem_info where playlist_id={}".format(p_id)
        print(sql)
        cursor.execute(sql)
        res=dictfetchall(cursor)
        print(res)
        return render(request,"recommend_playlist.html",{'id':p_id,'res':res,'usrname':usrname})

@csrf_exempt
def get_song(request):
    print("进入get_song")
    singer=request.POST
    singer_name=singer.get("singer_name")
    sql="select name,singer,time,url from musicsystem_info where singer='{0}'".format(singer_name)
    cursor.execute(sql)
    song_info=dictfetchall(cursor)
    sql="select singername,singerid,introduction from public.\"KuGo_singer_info\" where singername='{}'".format(singer_name)
    cursor.execute(sql)
    singer_info=dictfetchall(cursor)
    res={"song_info":song_info,"singer_info":singer_info}
    return JsonResponse(res,safe=False)

@csrf_exempt
def get_song_by_name(request):
    print("进入get_song_by_name")
    name=request.POST.get('song_info')
    print(name)
    sql="select name,singer,time,url from musicsystem_info where name like '%{}%' union select name,singer,time,url from musicsystem_info where singer like '%{}%'".format(name,name)
    print(sql)
    cursor.execute(sql)
    res=dictfetchall(cursor)
    print(res)
    return JsonResponse(res,safe=False)

@csrf_exempt
def delete_user(request):
    print("进入find_usrname")
    usrname=request.POST.get('usrname')
    print(usrname)
    sql="delete from user_info where usrname='{}'".format(usrname)
    cursor.execute(sql)
    sql="select usrname,birth,sex from user_info except select usrname,birth,sex from super_user_info"
    print(sql)
    cursor.execute(sql)
    res=dictfetchall(cursor)
    print(res)
    return JsonResponse(res,safe=False)


@csrf_exempt
def add_song(request):
    print("进入add_song")
    url=request.POST.get('url')
    playlist_id=request.POST.get('playlist_id')
    print(playlist_id)
    sql="insert into music_belong(playlist_id,url) values('{}','{}')".format(playlist_id,url)
    print(sql)
    try:
        cursor.execute(sql)
        sql="select name,singer,time,url from music_belong natural join musicsystem_info where playlist_id='{}'".format(playlist_id)
        print(sql)
        cursor.execute(sql)
        res=dictfetchall(cursor)
        # 触发器，插入歌曲后歌单歌曲数量加
        sql="update playlist set num=num+1 where playlist_id='{}'".format(playlist_id)
        cursor.execute(sql)
        return JsonResponse(res,safe=False)
    except:
        res="添加失败，同一歌单无法添加同一首歌哦"
        return JsonResponse({'text':res},safe=False)

@csrf_exempt
def delete_song(request):
    playlist_id=request.POST.get('playlist_id')
    url=request.POST.get('url')
    sql="delete from music_belong where url='{}' and playlist_id='{}' ".format(url,playlist_id)

    cursor.execute(sql)
    sql="select name,singer,time,url from music_belong natural join musicsystem_info where playlist_id='{}'".format(playlist_id)

    cursor.execute(sql)
    res=dictfetchall(cursor)
    # 触发器，删除歌曲后歌单歌曲数量减
    sql="update playlist set num=num-1 where playlist_id='{}'".format(playlist_id)
    cursor.execute(sql)
    return JsonResponse(res,safe=False)

@csrf_exempt
def create_playlist(request):
    print("进入create_playlist")
    playlist_name=request.POST.get("playlist_name")
    print(playlist_name)
    usrname=request.COOKIES.get("usrname")
    print(usrname)
    sql="insert into playlist(playlist_id,playlist_name,num,usrname,create_time,is_recommend) values(default,'{}','{}','{}','{}',default)".format(playlist_name,0,usrname,datetime.now().date())
    print(sql)
    try:
        print("进入try")
        cursor.execute(sql)
        ressql="select playlist_name,num,playlist_id from playlist  where usrname='{}'".format(usrname)
        print(ressql)
        cursor.execute(ressql)
        res=dictfetchall(cursor)
        print(res)
        return JsonResponse(res,safe=False)
    except:
        print("失败")
        return JsonResponse({"msg":"创建失败,换个歌单名试试吧"},safe=False)

@csrf_exempt
def delete_playlist(request):
    print("进入delete_playlist")
    playlist_id=request.POST.get("playlist_id")
    print(playlist_id)
    usrname=request.COOKIES.get("usrname")
    print(usrname)
    sql='select playlist_name from playlist where playlist_id={}'.format(playlist_id)
    cursor.execute(sql)
    test=dictfetchall(cursor)
    sql="select count(*) as num from super_user_info where usrname='{}'".format(usrname)
    cursor.execute(sql)
    is_super=dictfetchall(cursor)
    print(is_super[0]['num'])
    # 判断是否是超级用户
    if is_super[0]['num']==0:
        if test[0]['playlist_name']=='我喜欢' :
            print(1)
            return JsonResponse({"msg":"默认歌单无法删除"},safe=False)
        else:
            sql="delete from playlist where playlist_id='{}'".format(playlist_id)
            print(sql)
            try:
                print("进入try")
                cursor.execute(sql)
                ressql="select playlist_name,num,playlist_id from playlist  where usrname='{}'".format(usrname)
                print(ressql)
                cursor.execute(ressql)
                res=dictfetchall(cursor)
                print(res)
                return JsonResponse(res,safe=False)
            except:
                print("失败")
                return JsonResponse({"msg":"删除失败"},safe=False)
    else:
            sql="delete from playlist where playlist_id='{}'".format(playlist_id)
            print(sql)
            try:
                print("进入try")
                cursor.execute(sql)
                sql="select playlist_id,playlist_name,num,usrname,create_time,is_recommend from playlist"
                cursor.execute(sql)
                playlist_info=dictfetchall(cursor)
                print(playlist_info)
                return JsonResponse(playlist_info,safe=False)
            except:
                print("失败")
                return JsonResponse({"msg":"删除失败"},safe=False)

def dictfetchall(cursor):
    desc=cursor.description
    return [dict(zip([col[0] for col in desc],row))
    for row in cursor.fetchall()]

@require_http_methods(["POST","GET"])
def register(request):
    response_text=HttpResponse()
    if(request.method == "GET"):
        return render(request,"register.html")
    elif(request.method =="POST"):
            usrname=request.POST.get('usrname')
            password=request.POST.get('password')
            birth=request.POST.get('birth')
            sex=request.POST.get('sex')
            if sex=='男':
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
                    response_text.content=""
                    sql="insert into playlist(playlist_id,playlist_name,num,usrname,create_time,is_recommend) values(default,'{}','{}','{}','{}',default)".format('我喜欢',0,usrname,datetime.now().date())
                    try:
                        cursor.execute(sql)
                        connection.commit()
                        print("我喜欢歌单插入成功")
                    except:
                        connection.rollback()
                        print("我喜欢歌单触发器失效")
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
