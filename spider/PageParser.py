import pymongo
import socket
import json
import threading
from bs4 import BeautifulSoup
from urllib import request


class DBThread(threading.Thread):
    '''
        将解析结果写入数据库
        暂时不确定每个线程链接一次DB好还是维持一个链接好
    '''
    def __init__(self, page_list):
        self.page_list = page_list
        with open('config.json') as f:
            config = json.load(f)

        self.client = pymongo.MongoClient(host=config.get("db_address"), port= int(config.get("db_port")))
        self.db = self.client[config.get("db_database")] # 数据库名
        self.collection = self.db[config.get("db_port")] # 集合名 
        self.lock = threading.Lock()

    def run(self):
        '''
        暂时不考虑加锁， 同时写入又怎样？
        '''
        # self.lock.acquire() # 防止写入磁盘速度（比request+解析页面还）慢 导致多用户写入
        self.collection.insert_many(self.page_list) 
        # self.lock.release()

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
        self.chunk_size = 200 # 每解析chunk_size条数据 写入一次数据库

    def parse(self):
        # 1. 读取input.txt
        # 2. 逐行request
        # 3. 每次new一个Page对象
        # 4. 依次解析所有元素
        # 5. TODO 保存到数据库（后期可以 先存到列表 然后开一个线程保存到数据库）
        page_chunk = []
        line = 0
        for url in open(self.config.get("input_file")):
            if(line > self.chunk_size):
                line = 0 # 重新计数 
                thread = DBThread(page_chunk)
                thread.start()
                page_chunk = [] # '清空'缓冲区
            page = {}
            page["url"] = url
            page["html"] = self.requestUrl(url) 
            page["title"], page["description"], page["published_time"], page["source"] = self.getMetaInfo()
            page["content"] = self.getContent()
            page["img_urls"] = self.getImgs()
            page["video_urls"] = []
            # p.video_urls = p.getVideos()
            page_chunk.append(page)
        return page_chunk

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

    def getVideos(self):
        pass

    def getContent(self):
        if self.soup == None:
            return None
        raw_contents = self.soup.select(".article p")
        contents = []
        for para in raw_contents:
            contents.append(para.text.strip())# 删除前后的<p>标签/删除前后的空格
        return "\n".join(contents)