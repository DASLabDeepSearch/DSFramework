import PageParser as PP
import time
import datetime
import sohu_crawler
import sina_crawler
import threading
import sys

class MainThread(threading.Thread):
    def __init__(self,func,args=None):
        super(MainThread,self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(self.args) if self.args is not None else self.func()

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

print("参数列表", str(sys.argv))
if sys.argv[1] == "collect":
    print("收集sohu新闻")
    sohu_crawler.start()
elif sys.argv[1] is None or sys.argv[1] == "merge":
    t1 = MainThread(sohu_crawler.merge)
    t2 = MainThread(sina_crawler.start)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    sohu_file_path = t1.get_result()
    sina_file_path = t2.get_result()

    print("数据抓取完成，开始解析网页数据并写入数据库")
    try:
        parser = PP.PageParser()
        t1 = MainThread(parser.parseFile, sohu_file_path)
        t2 = MainThread(parser.parseFile, sina_file_path)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        print("全部任务完成", datetime.datetime.now())
    except:
        print("解析失败，检查文件是否存在或数据库是否启动或是否安装正确版本的浏览器内核")