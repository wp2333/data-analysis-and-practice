from dis import findlabels
from bs4 import BeautifulSoup
import re
import urllib.request,urllib.error
import xlwt
import json
import time
import my_neo4j

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
# findRating=re.compile(r'<strong class="ll rating_num" property="v:average">(.*)</strong>')
# findl=re.compile(r'((https|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|])')

# def fun1():
#     depth,end=1,2
#     # base_url = "https://movie.douban.com/top250?start="
#     base_url = "https://movie.douban.com/subject/1292052/"
#     save_path = "result.json"
#     base1="https://movie.douban.com/subject/1293839/?from=subject-page"
#     search_movie(base1,depth,end)
#     # askURL(base_url)
#     return 0

def askURL(url):
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
             Chrome/99.0.4844.51 Safari/537.36"
    }
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
    return html

# def getData(base_url):
#     datalist = []
#     for i in range(0,10):
#         url = base_url + str(i*25)
#         html = askURL(url)

#     return datalist

def saveData(dict,path):
    with open(path,"a",encoding='utf-8') as f:
        json.dump(dict, f, ensure_ascii=False, indent=4)
        f.write('\n')
    return

def search_movie(url,depth,end):
    # 通过豆瓣编号检查是否已搜索过
    No=re.findall(findNo,url)[0]
    if No in searched:
        return No
    searched.append(No)

    # 延迟防止IP被封
    time.sleep(1)
    # t1 =time.time()

    # 获取网页
    html=askURL(url)
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

    # 保存数据
    saveData(data,save_path)
    print('No.'+str(ctr)+' finished!\n')
    
    # 获取子节点URL
    links=bs.find_all(class_="recommendations-bd")
    links=str(links)
    link_list=re.findall(findLink,links)
    
    # 递归搜索,深度优先
    if depth<end:
        for link in link_list:
            # print(link_list[i])
            # print(link)
            recommend=search_movie(link,depth+1,end)
    
    # t3=time.time()
    # print(t3-t2)
    return data["豆瓣编号"]

if __name__ =="__main__":
    depth,end,ctr=1,2,0
    begin="https://movie.douban.com/subject/1291561/"
    save_path="result.json"
    searched=[]
    app=my_neo4j.neo_login()
    search_movie(begin,depth,end)
    app.close()