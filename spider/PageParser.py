import pymongo
import socket
import json
from bs4 import BeautifulSoup
from urllib import request
'''
class Pages:
    url = ''
    html = ''
    title = ''
    description = ''
    published_time = ''
    source = ''
    content = ''
    img_urls = []
    video_urls = []
'''

class UrlParser:
    '''
        目前的解析仅针对 新浪国际新闻
        从 configure.json中读取配置信息（输入文件的路径）
        从输入文件中逐行获取新闻URL并进行解析
        暂时以dict形式返回网页内容，后续加上DB后再链接
    '''
    def __init__(self):
        with open('config.json') as f:
           self.config = json.load(f)

        #self.client = pymongo.MongoClient (host=self.config.get('db_address'), port=self.config.get("db_port"))
        #self.db = self.client.Web # 选择数据库
        #self.collection = self.db.Pages # 选择集合（表）
        self.soup = None

    def parse(self):
        # 1. 读取input.txt
        # 2. 逐行request
        # 3. 每次new一个Page对象
        # 4. 依次解析所有元素
        # 5. 保存到数据库（后期可以 先存到列表 然后开一个线程保存到数据库）
        tmp_pages = []
        for url in open(self.config.get("input_file")):
            page = {}
            page["url"] = url
            page["html"] = self.requestUrl(url) 
            page["title"], page["description"], page["published_time"], page["source"] = self.getMetaInfo()
            page["content"] = self.getContent()
            page["img_urls"] = self.getImgs()
            # p.video_urls = p.getVideos()
            tmp_pages.append(page)
        return tmp_pages

    def getMetaInfo(self):
        return self.getTitle(), self.getDescription(), self.getPubtime(), self.getSource()
    
    def requestUrl(self, url):
        socket.setdefaulttimeout(20)
        requests = request.Request(url)
        res = request.urlopen(requests) # 官网说最好不用get() ？
        html = res.read()
        self.soup = BeautifulSoup(html, 'html.parser')
        return html
    
    def getTitle(self):
        if self.soup == None:
            return None
        title = self.soup.find("meta", property="og:title")
        return title["content"]
    
    def getDescription(self):
        if self.soup == None:
            return None
        desc = self.soup.find("meta", property="og:description")
        return desc["content"]
    
    def getPubtime(self):
        if self.soup == None:
            return None
        time = self.soup.find("meta", property="article:published_time")
        return time["content"]

    def getSource(self):
        if self.soup == None:
            return None
        source = self.soup.find("meta", property="article:author")
        return source["content"]
    
    def getImgs(self):
        if self.soup == None:
            return None
        imgs = self.soup.select(".img_wrapper img")
        img_urls = []
        for img in imgs:
            img_urls.append("https:" + img["src"])
        return img_urls

    def getContent(self):
        if self.soup == None:
            return None
        raw_contents = self.soup.select(".article p")
        contents = []
        for para in raw_contents:
            contents.append(para.text.strip())# 删除前后的<p>标签/删除前后的空格
        return "\n".join(contents)