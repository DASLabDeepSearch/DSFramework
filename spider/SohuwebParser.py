import socket
import json
from bs4 import BeautifulSoup
from urllib import request
import re
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
def judgeUrl(url):
    '''
    :param url: 输入的url地址
    :return: 返回1，则使用新浪网页解析；返回2，则使用搜狐网页解析；若返回0，则为错误网页url
    '''
    if len(re.findall('.{1,100}.sina.{1,100}', str(url))) != 0:
        return 1
    if len(re.findall('.{1,100}.sohu.{1,100}', str(url))) != 0:
        return 2
    return 0

class SohuUrlParser:
    '''
        针对搜狐新闻
        从 configure.json中读取配置信息（输入文件的路径）
        从输入文件中逐行获取新闻URL并进行解析
        暂时以dict形式返回网页内容，后续加上DB后再链接
    '''

    def __init__(self):
        with open('config.json') as f:
            self.config = json.load(f)

        # self.client = pymongo.MongoClient (host=self.config.get('db_address'), port=self.config.get("db_port"))
        # self.db = self.client.Web # 选择数据库
        # self.collection = self.db.Pages # 选择集合（表）
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
            page["content"], page["img_urls"] = self.getContentandImgs()

            # p.video_urls = p.getVideos()
            tmp_pages.append(page)
        return tmp_pages

    def getMetaInfo(self):
        return self.getTitle(), self.getDescription(), self.getPubtime(), self.getSource()

    def requestUrl(self, url):
        socket.setdefaulttimeout(20)
        requests = request.Request(url)
        res = request.urlopen(requests)
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
        time = self.soup.find("meta", itemprop="datePublished")
        return time["content"]

    def getSource(self):
        if self.soup == None:
            return None
        source = self.soup.find('meta', attrs={'name': 'mediaid'})
        return source["content"]

    def getContentandImgs(self):
        if self.soup == None:
            return None
        raw_contents = self.soup.select(".article p")
        contents = []
        img_urls = []
        for para in raw_contents:
            if len(para.select('img')) != 0:
                pic_url = re.findall('http://.{1,100}.jpg|http://.{1,100}.png|http://.{1,100}.jpeg|http://.{1,100}.gif',
                                     str(para), re.IGNORECASE)
                img_urls.append(pic_url[0])
            else:
                contents.append(para.text.strip())
        return "\n".join(contents), img_urls
