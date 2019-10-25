import PageParser as PP
import time
import datetime
import sohu_crawler
import sina_crawler

sohu_file_path = sohu_crawler.start()
sina_file_path = sina_crawler.start()
print("数据抓取完成，开始解析网页数据并写入数据库")
try:
    parser = PP.PageParser()
    res = parser.parseFile(sohu_file_path)
    print("搜狐解析完成")
    res = parser.parseFile(sina_file_path)
    print("新浪解析完成")
    print("全部任务完成", datetime.datetime.now())
except:
    print("解析失败，检查文件是否存在或数据库是否启动或是否安装正确版本的浏览器内核")