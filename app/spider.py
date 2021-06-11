# -*- coding: utf-8 -*-
"""
@author: CoderYYN
@Email:  coderyyn@qq.com
"""

'''
目标：爬取酷狗音乐全站所有歌曲

解决方案 ：网页端与App端结合
'''

from typing import Counter
import requests
import psycopg2
import urllib3

urllib3.disable_warnings()
import time
import hashlib
import random


class KuGo_Spider(  object  ):
    def __init__(self):
        self.db = psycopg2.connect(database='music_listener',user='postgres',password='123456',host='localhost',port='5432')
        # 搜索歌曲
        self.get_search('七里香')
        # 获取歌手列表信息  按照26个英文字母索引
        self.get_singers()
        # 获取歌手信息简介
        self.get_singer_info()
        # 获取每个歌手的所有歌曲
        self.get_singer_song()
#        self.download_music('EDF51D44748256B7C455B53E25E56C1E')
        self.db.close()
    
    #获取每个歌手的所有歌曲
    def get_singer_song(self):
        sql="select singer_singerid,singer_singername from kugou_singer where singer_sindex='热门'"# and sindex='热门'" 
        singers=self.connect_mysql(sql,None)
        for singer in singers[31:]:#循环每个歌手
            print(singer[1])
            datas=[]
            for page in range(1,10):
                url='http://mobilecdn.kugou.com/api/v3/singer/song?page=%s&pagesize=1000&sorttype=1&area_code=1&version=9156&singerid=%s&identity=3&plat=0&with_res_tag=1'%(page,singer[0])
                response=requests.get(url)
                result=response.text.replace('<!--KG_TAG_RES_END-->','').replace('<!--KG_TAG_RES_START-->','').replace('null','None')
                try:
                    result=eval(result)#将字符串类型转化字典类型
                except:
                    break
                if result['error']=='没有更多信息':#返回值为空集合代表爬完 跳出循环
                    break
                #统计每个歌手的歌曲总数
#                total=result['data']['total']
#                sql="update KuGo_singer_info set musiccount='%s' where singerid='%s'"%(total,singer[1])
#                self.connect_mysql(sql,None)
#                print(singer[0],total)
                for song in result['data']['info']:
                    Hash=song['hash']
                    data=self.download_music(Hash)
                    if(len(datas)>10):
                        break
                    if data!=[]:
                        datas.append(data)
            sql="INSERT INTO public.musicsystem_info(name, singer, \"time\", url) VALUES (%s, %s, %s, %s);"
            self.connect_mysql(sql,datas)
            # sql="update KuGo_singer set flag='1' where id='%s'"%singer[0]
            # self.connect_mysql(sql,None)
                    
            
    #下载歌曲信息  参数hash
    def download_music(self,Hash):
        tracker_url='https://www.kugou.com/yy/index.php?r=play/getdata&hash=%s'%Hash
        ###################加密部分
        #生成md5加密后的cookie
        #创建md5对象
        md5= hashlib.md5()
        #随机生成4位随机的字符列表 范围为a-z 0-9
        n=random.sample('abcdefghijklmnopqrstuvwxyz0123456789',4)
        #将列表元素拼接为字符串
        n=''.join(n)
        #将字符串编码后更新到md5对象里面
        md5.update(n.encode())
        #调用hexdigest获取加密后的返回值
        kg_mid=md5.hexdigest()
        # kg_mid='0a69e52271c767c43a2c6700b59387cd'
        headers={
            'Cookie':'kg_mid=%s'%kg_mid,
        }
        ###################加密部分
        response=requests.get(tracker_url,headers=headers,timeout=5)
        result=response.json()
        #相关信息
        if result['data']==[]:
            return []
        else:
            author_name=result['data']['author_name']#歌手名
            song_name=result['data']['song_name']#歌曲名
            timelength=result['data']['timelength']#时长  单位：毫秒   ms  /1000 秒
            timelength=timelength/1000
            play_url=result['data']['play_url']#音频地址
            if author_name=="" or song_name=="" or int(timelength/60)<2 or play_url=="":
                return []
            else :
                timelength=str(int(timelength/60))+':'+str(int(timelength%60))#几分几秒
                data=[song_name,author_name,timelength,play_url]
                return data    
        
    #搜索歌曲api
    def get_search(self,word):
        #电脑端
        url='https://songsearch.kugou.com/song_search_v2?keyword='+word+'&page=1&pagesize=30&userid=-1&platform=WebFilter&filter=2&iscorrection=1'
        response=requests.get(url)
        result=response.json()
        lists=result['data']['lists']
        for i in lists[:10]:
            Hash=i['FileHash']#参数hash   hash  FileHash
            data=self.download_music(Hash)
            sql="insert into KuGo_music (author_id,author_name,audio_id,audio_name,song_name,hash_code,filesize,timelength,have_album,album_id,album_name,have_mv,video_id,privilege,privilege2,play_url,img,lyrics) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            self.connect_mysql(sql,data)
            
    #获取歌手列表信息  按照26个英文字母索引
    def get_singers(self):
        classifications={'1':'华语','2':'欧美','3':'日韩','5':'日本','6':'韩国'}#特殊  4:'其他'  sextype=0
        sextypes={'1':'男歌手','2':'女歌手','3':'组合'}
        for classification in classifications:
            for sextype in sextypes:
                datas=[]
                name=classifications[classification]+sextypes[sextype]#分类名称
                url='http://mobilecdn.kugou.com/api/v5/singer/list?musician=0&type=%s&showtype=2&sextype=%s&with_res_tag=1'%(classification,sextype)#分类链接
                response=requests.get(url)
                print(name)
                time.sleep(1)
                result=response.text.replace('<!--KG_TAG_RES_END-->','').replace('<!--KG_TAG_RES_START-->','')
                result=eval(result)#将字符串类型转化字典类型
                #得到信息列表，列表里面有按歌手的姓氏首字母搜索的26个以及热门与未知字符总共28个
                infos=result['data']['info']
                for info in infos:
                    index=info['title']#索引：热门 A B....
                    singers=info['singer']
                    for i in singers:
                        data=[name,index,i['singername'],i['singerid'],i['imgurl']]
                        datas.append(data)
                sql="insert into kugou_singer (singer_class_name,singer_sindex,singer_singername,singer_singerid,singer_imgurl) values (%s,%s,%s,%s,%s)"
                self.connect_mysql(sql,datas)
        
    #获取歌手信息简介
    def get_singer_info(self):
        sql='select singer_singerid from kugou_singer'
        singerids=self.connect_mysql(sql,None)
        for singerid in singerids:
            print(singerid)
            url='http://mobilecdn.kugou.com/api/v3/singer/info?singerid=%s&version=1&with_listener_index=1&with_res_tag=1'%singerid[0]
            response=requests.get(url)
            result=response.text.replace('<!--KG_TAG_RES_END-->','').replace('<!--KG_TAG_RES_START-->','')
            result=eval(result)#将字符串类型转化字典类型
            singername=result['data']['singername']#歌手名字
            singerid=result['data']['singerid']#歌手id
            albumcount=result['data']['albumcount']#mv数量
            mvcount=result['data']['mvcount']#专辑数量
            intro=result['data']['intro']#歌手简介
            data=[singername,singerid,albumcount,mvcount,intro]
            sql="INSERT INTO public.\"KuGo_singer_info\"(singername, singerid, albumcount,mvcount, introduction) VALUES (%s,%s,%s,%s,%s);"
            self.connect_mysql(sql,data)

    
    #连接模块
    def connect_mysql(self,sql,data):
        cursor =  self.db.cursor()
        try:
            result=None
            if data:
                if isinstance(data[0],list):
                    cursor.executemany(sql,data)
                else:
                    cursor.execute(sql,data)
            else:
                cursor.execute(sql)
                result=cursor.fetchall()
        except Exception as e:
            print(e)
            self.db.rollback();
        finally:
            cursor.close()
            self.db.commit(); #提交操作
            return result

if __name__=='__main__':
    KuGo_Spider()
