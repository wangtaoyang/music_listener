from typing import Text
import requests
# 导入xpath模块
from lxml import etree
import re
from bs4 import BeautifulSoup
# 连接数据库的模块
import psycopg2
import urllib3

urllib3.disable_warnings()

# session = requests.Session()
# headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome"}
# req = session.get("https://www.kugou.com/yy/rank/home/1-31308.html?from=rank", headers=headers)
# music_list_html = BeautifulSoup(req.text)
music_info_url_list = []
music_download_url_list = []

# 榜单网页url
music_list_url = "https://www.kugou.com/yy/singer/home/3520.html"
# 榜单网页源代码
music_list_html = requests.get(music_list_url,stream=True,verify=False).text
music_list=[] #所有歌曲信息表（包括时间的）
# 获取歌手和歌曲名
def get_music_name():
    global music_list
    element = etree.HTML(music_list_html)
    # @title是提取li标签中title属性的内容  获取歌曲名称和歌手
    music_list_name_info = element.xpath('//div[@class="pc_temp_songlist "]/ul/li/@title')
    music_list_time_info = element.xpath('//div[@class="pc_temp_songlist "]/ul/li/span[@class="pc_temp_tips_r"]/span[@class="pc_temp_time"]/text()')
    for info in music_list_name_info:
        music_info={} #一首歌曲的信息（字典）
        music_info['name_singer']= info
        music_info['time'] = music_list_time_info[music_list_name_info.index(info)].replace('\t','').replace('\n','')
        music_list.append(music_info)
    return music_list

get_music_name()

# 获取存储音乐信息的网页url 存储到列表中 返回值为列表
def get_music_info_url():
    soup = BeautifulSoup(music_list_html,features="lxml")
    script = soup.find_all('script')[-1]
    # print(script)
    # print(type(script))
    # 查找符合正则表达式的字符串 此时script变量为bs4格式 我们需要将其转化为字符串格式
    info = re.findall(r'\[.*\]',str(script))[1]
    # print(info)
    # 替换符合正则表达式的字符串
    info = re.sub(r'\[|\]',"",info)
    # print(type(info))
    # 分割符合正则表达式的字符串
    info = re.split(r'\},\{',info)
    # print(info)
    for i in range(len(info)):
        # 获取hash属性值
        hash = re.findall(r'H.*?,',info[i])[0].split('"')[2]
        # 获取album_id属性值
        album_id = re.findall(r'album_id.*?,',info[i])[0].split(":")[1].replace(",","")
        # print(album_id)
        if len(hash) > 0 and len(album_id) > 0:
            music_info_url = "https://wwwapi.kugou.com/yy/index.php?r=play/getdata&hash=" + hash + "&album_id=" + album_id
        else:
            print(str(i) + "  " + "为空")
        # 将音乐信息网页地址存储到列表中
        music_info_url_list.append(music_info_url)
    return music_info_url_list

# 获取音乐下载地址
def get_music_download_url():
    # 使用请求头 不然获取不到音乐信息
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    "cookie": "kg_mid=5177dda4cc5327932ceb0652b3abbdf4; kg_dfid=2AveiS1FiBds3dWdin1RsaQ6; kg_dfid_collect=d41d8cd98f00b204e9800998ecf8427e; Hm_lvt_aedee6983d4cfc62f509129360d6bb3d=1611227172; Hm_lpvt_aedee6983d4cfc62f509129360d6bb3d=1611237914"}
    # 循环得到的存储音乐信息的网页url
    for music_info_url in music_info_url_list:
        music_info_html = requests.get(music_info_url,headers=headers).text
        # print(music_info_url)
        # print(music_info_html)
        # 获取音乐下载地址
        music_download_url = re.findall(r'play_url.*?\.mp3',music_info_html)[0].split('"')[-1].replace("\\","")
        # print(music_download_url)
        # 将播放地址添加到列表中
        music_download_url_list.append(music_download_url)
    return music_download_url_list

# 将获取到的数据添加到数据库中
def put_info_to_mysql():
    # 连接数据库
    db = psycopg2.connect(database='music_listener',user='postgres',password='123456',host='localhost',port='5432')
    # 创建指针
    cursor = db.cursor()
    for i in range(len(music_download_url_list)):
        # print(music_name_list)
        # 歌曲名称
        name = music_list[i]['name_singer'].split(" - ")[1]
        # 歌手
        singer = music_list[i]['name_singer'].split(" - ")[0]
        # 歌曲时长
        time = music_list[i]['time']
        # 播放地址
        url = music_download_url_list[i]
        print(name + "  " + singer +"  "+ time +"  " + url)
        # 执行的SQL语句
        sql = "INSERT INTO public.musicsystem_info(name, singer, time, url) VALUES ('{}','{}','{}','{}');".format(name,singer,time,url) 
        # """insert into musicsystem_info(Name,Singer,Time,Url) values ('{}','{}','{}','{}')""".format(name,singer,"2020.1.22",url)
        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 提交
            db.commit()
            print("执行成功")
        except:
            # 添加失败时回滚
            db.rollback()
            print("执行失败")
    # 关闭数据库连接
    db.close()


# 主函数
def main():
    get_music_info_url()
    get_music_download_url()
    put_info_to_mysql()

if __name__ == '__main__':
    main()
