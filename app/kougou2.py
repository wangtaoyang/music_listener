#导入库
import requests
import re
import os
#设置好一些变量
timer = 0 #设置一个计算歌曲顺序的机器
song_urls = {}
names = {}
songs = input("请输入歌曲名：")
url = 'https://songsearch.kugou.com/song_search_v2?callback=jQuery112409090559630919017_1585358668138&keyword=%s&page=1&pagesize=30&userid=-1&clientver=&platform=WebFilter&tag=em&filter=2&iscorrection=1&privilege_filter=0&_=1585358668140'%songs
texts = requests.get(url).text
song_hashes = re.findall('"FileHash":"(.*?)"',texts)
print("请稍等...")for i in song_hashes:
    information_url = 'https://wwwapi.kugou.com/yy/index.php?r=play/getdata&callback=jQuery19104610954889760035_1585364074033&hash=%s&album_id=0&dfid=2SSGs60RKO9P0bAzIe0xF4Us∣=5a959954d2f99fc1438fe2efb7596511&platid=4&_=1585364074034'%i
    information = requests.get(information_url).text
    song_url = re.findall('"play_url":"(.*?)"',information)
    song_names = bytes(re.findall('"audio_name":"(.*?)"',information)[0],encoding='ascii').decode('unicode-escape')
    singers = bytes(re.findall('"author_name":"(.*?)"',information)[0],encoding='ascii').decode('unicode-escape')if song_names not in names.values():
    names[str(timer)] = song_namesprint("%d.%s"%(timer,song_names))
    print("作者：%s"%singers)
    print()
    timer += 1if song_url[0] not in song_urls.values():
    song_urls[str(timer-1)] = song_url[0]
    print('输入n就不下载，若要下载多首歌曲，请用英文符号","隔开')
    choice = input('请输入要下载歌曲的编号：').split(',')if choice == "n":exit()else:
    path = input("请输入要保存的路径：")
    has_path = os.path.exists(path)
    while has_path == False:print("路径不存在！！")
    path = input("请输入要保存的路径：")
    has_path = os.path.exists(path)
    for i in choice:
    song_url = song_urls[i].replace('\\/','/')
    song = requests.get(song_url).content
    save_name = names[i]
    with open(path + '/' + save_name + '.mp3','wb') as f:f.write(song) print("保存完成！")