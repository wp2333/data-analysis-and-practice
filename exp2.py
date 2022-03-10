from random import random
from bs4 import BeautifulSoup
import re
import urllib.request,urllib.error
import json
import time
import my_neo4j
import requests
from file_clear import del_file
from fake_useragent import UserAgent


# 正则匹配式
findLink=re.compile(r'<a href="(.*)">')
findImgSrc=re.compile(r'<img.*src="(.*?)"')
findTitle=re.compile(r'<span property="v:itemreviewed">(.*?)</span>')
findDirector=re.compile(r'<a href=".*" rel="v:directedBy">(.*?)</a>')
findSW_1=re.compile(r'<span class="pl">编剧.*<span class="attrs">(.*?)</span>')
findSW_2=re.compile(r'<a href=".*?">(.*?)</a>')
findStar=re.compile(r'<a href="/.*?" rel="v:starring">(.*?)</a>')
findType=re.compile(r'<span property="v:genre">(.*?)</span>')
findPlace=re.compile(r'<span class="pl">制片国家/地区:</span> (.*?)<br/>',re.S)
findLanguage=re.compile(r'<span class="pl">语言:</span> (.*?)<br/>')
findDate=re.compile(r'<span content="(.*?)" property="v:initialReleaseDate">')
findLength=re.compile(r'<span content=".*?" property="v:runtime">(.*?)<br/>')
findNo=re.compile(r'([0-9]+)')
findCover=re.compile(r'rel="v:image" src="(.*?)"',re.S)

def askURL(url):
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
             Chrome/99.0.4844.51 Safari/537.36"
    }

    # 代理
    proxies = {
        "http": "http://10.10.1.10:3128",
        "https": "http://10.10.1.10:1080",
    }
    # proxy = 

    req = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(req)
        html = response.read().decode("utf-8")
        #print(html)
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
    response.close()
    return html

def askURL2(url):
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
             Chrome/99.0.4844.51 Safari/537.36"
    }
    fake_headers = {"User-Agent":UserAgent().random}
    response = sess.get(url=url, headers=fake_headers)
    return response.content

def saveData(dict,path):
    with open(path,"a",encoding='utf-8') as f:
        json.dump(dict, f, ensure_ascii=False, indent=4)
        f.write('\n')
    return

def saveCover(url,name):
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
             Chrome/99.0.4844.51 Safari/537.36"
    }
    with open(name, 'wb') as f:
        f.write(sess.get(url=url, headers=head).content)

def search_movie(url,depth,end):
    # 通过豆瓣编号检查是否已搜索过
    No=re.findall(findNo,url)[0]
    if No in searched:
        if mode == 'tree':
            return '$'
        elif mode == 'map':
            return No
    searched.append(No)

    # 延迟防止IP被封
    time.sleep(2*random())
    # t1 =time.time()

    # 获取网页
    html=askURL2(url)
    # t2=time.time()
    # print(t2-t1)

    # 创建BS类实体
    bs=BeautifulSoup(html,"html.parser")
    # 主要目标文本
    content=bs.find(id="content")
    content=str(content)

    # 电影数据
    global ctr
    ctr+=1
    data={'搜索序号':ctr, '豆瓣编号':No}
    # 获取片名
    title=re.findall(findTitle,content)
    data["片名"]=title[0].replace('amp;','')
    # 获取导演
    director=re.findall(findDirector,content)
    data["导演"]=director[0]
    # 获取编剧
    scriptwriters=re.findall(findSW_1,content)
    scriptwriters=re.findall(findSW_2,scriptwriters[0])
    data["编剧"]=[]
    for i in range(len(scriptwriters)):
        data["编剧"].append(scriptwriters[i])
    # 获取主演
    bs.find(rel="v:starring")
    stars=re.findall(findStar,content)
    data["主演"]=[]
    for i in range(len(stars)):
        if i>4:
            break
        data["主演"].append(stars[i])
    # 获取类型
    data["类型"]=[]
    movie_type=re.findall(findType,content)
    for i in range(len(movie_type)):
        if i>4:
            break
        data["类型"].append(movie_type[i])
    # 获取制片国家/地区
    place=re.findall(findPlace,content)
    data["制片国家/地区"]=place[0]
    # 获取语言
    languages=re.findall(findLanguage,content)
    languages=languages[0].split(' / ')
    data["语言"]=[]
    for i in range(len(languages)):
        if i>4:
            break
        data["语言"].append(languages[i])
    # 获取上映日期
    dates=re.findall(findDate,content)
    data["上映日期"]=[]
    for i in range(len(dates)):
        if i>4:
            break
        data["上映日期"].append(dates[i])
    # 获取片长
    movie_length=re.findall(findLength,content)
    movie_length=re.sub(r'</span>','',movie_length[0])
    movie_length=movie_length.split(' / ')
    data["片长"]=[]
    for i in range(len(movie_length)):
        data["片长"].append(movie_length[i])
    # 获取评分
    rating=bs.find(class_="ll rating_num").string
    rating=float(rating)
    data["评分"]=rating
    
    # 获取封面
    cover_path=re.findall(findCover,content)[0]
    # print(cover[0])
    cover_name="covers/"+str(ctr)+'-'+data["片名"]+".jpg"
    # urllib.request.urlretrieve(cover_path, cover_name)
    saveCover(cover_path, cover_name)

    # 保存数据
    saveData(data,save_path)
    print('\nNo.'+str(ctr)+' finished!')

    # 创建neo4j节点
    app.create_movie(data["片名"], data["豆瓣编号"])
    
    # 获取子节点URL
    links=bs.find_all(class_="recommendations-bd")
    links=str(links)
    link_list=re.findall(findLink,links)
    
    # 递归搜索,深度优先
    if depth<end:
        for link in link_list:
            recommend=search_movie(link,depth+1,end)
            if mode == 'tree':
                if recommend=='$':
                    continue
                app.create_movie_recommendation(data["豆瓣编号"],recommend)
            elif mode == 'map':
                app.create_movie_recommendation(data["豆瓣编号"],recommend)
    
    # t3=time.time()
    # print(t3-t2)
    return data["豆瓣编号"]

if __name__ =="__main__":
    mode="tree"# 'tree'模式产生搜索树,'map'模式产生有环推荐图
    cover_file = r'D:\data analysis and pratice\covers'
    del_file(cover_file)# 清空covers文件夹
    depth,end,ctr=1,8,0
    begin="https://movie.douban.com/subject/1292064/"
    save_path="result.json"
    open(save_path, "w").close()# 清空result.json
    searched=[]
    app=my_neo4j.neo_login()
    app.delete_all()# 清空数据库
    sess = requests.session()
    search_movie(begin,depth,end)
    app.close()