import pymongo
import socket
import json
import re
import threading
from bs4 import BeautifulSoup
from urllib import request

class PageParser:
    '''
        目前的解析仅针对 新浪国际新闻
        从 configure.json中读取配置信息（输入文件的路径）
        从输入文件中逐行获取新闻URL并进行解析
        暂时以dict形式返回网页内容，后续加上DB后再链接
        接口：
        parseFile(filename=None)
            传入包含待解析URL的文件名（默认使用“input.txt”）
            返回值： 列表，列表元素为 字典形式的网页对象
            网页对象的属性：
                url, html, title, published_time
                description: 文章内容的概述
                source：消息来源（最初发表者）
                content: 新闻正文
                img_urls, video_urls：正文包含的所有图片，视频 的 URL

        parseURL(url)
            传入 单个 待解析的URL
            返回值： 单个字典形式的网页对象
    '''
    def __init__(self):
        with open('./config.json') as f:
            self.config = json.load(f)
        self.soup = None
        self.chunk_size = self.config.get("chunk_size") # 每解析chunk_size条数据 写入一次数据库

        self.client = pymongo.MongoClient(host=self.config.get("db_address"), port= int(self.config.get("db_port")))
        self.db = self.client[self.config.get("db_database")] # 数据库名
        self.collection = self.db[self.config.get("db_collection")] # 集合名 

    def judgeUrl(self, url):
        '''
        :param url: 输入的url地址
        :return: 返回1，则使用新浪网页解析；返回2，则使用搜狐网页解析；若返回0，则为错误网页url
        '''
        if len(re.findall('.{1,100}.sina.{1,100}', str(url))) != 0:
            return 1
        if len(re.findall('.{1,100}.sohu.{1,100}', str(url))) != 0:
            return 2
        return 0

    def parseFile(self, filename=None): # read from file
        ''' 
            1. 读取input.txt
            2. 逐行request
            3. 每次new一个Page对象
            4. 依次解析所有元素
            5. 保存到数据库
        '''
        for url in open(filename if filename != None else self.config.get("input_file")):
            try:
                page = self.parseURL(url)
                res = self.collection.insert_one(page)
                print(res.inserted_id)
            except Exception as e: # 有时候会request URL会超时导致抛出异常
                print("===== parseURL出现异常，URL：", url, "\n", e)
                pass

    def parseURL(self, url): # read from a specfic URL
        self.site = self.judgeUrl(url)
        if(self.site == 0):
            raise Exception("不受支持的URL地址")
        page = {}
        page["url"] = url
        page["html"] = self.requestUrl(url) 
        page["title"], page["description"], page["published_time"], page["source"] = self.getMetaInfo()
        page["content"] = self.getContent()
        page["img_urls"] = self.getImgs()
        page["video_urls"] = []
        return page


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
        time = self.soup.find("meta", property="article:published_time") if self.site == 1 else self.soup.find("meta", itemprop="datePublished")
        return time["content"]                              

    def getSource(self):
        if self.soup == None:
            return None
        source = self.soup.find("meta", property="article:author") if self.site == 1 else self.soup.find('meta', attrs={'name': 'mediaid'})
        return source["content"]
    
    def getImgs(self):
        if self.soup == None:
            return None
        img_urls = []
        if self.site == 1: # sina got a specfic class for imgs in a article
            imgs = self.soup.select(".img_wrapper img")
            for img in imgs:
                img_urls.append("https:" + img["src"])
        elif self.site == 2: # but sohu has not, we can just extract it from raw para
            raw_contents = self.soup.select(".article p")
            for para in raw_contents:
                if len(para.select('img')) != 0:
                    pic_url = re.findall('http://.{1,100}.jpg|http://.{1,100}.png|http://.{1,100}.jpeg|http://.{1,100}.gif',
                                        str(para), re.IGNORECASE)
                    img_urls.append(pic_url[0])
        return img_urls

    def getVideos(self):
        pass

    def getContent(self):
        if self.soup == None:
            return None
        raw_contents = self.soup.select(".article p")
        contents = []
        for para in raw_contents:
            contents.append(para.text.strip()) # 删除前后的<p>标签/删除前后的空格
        return "\n".join(contents)