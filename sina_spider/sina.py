#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author : Du Qinghua
# @time : 2019/10/22 19:46
# @file : sina.py
# 爬取新浪国际新闻链接，获取前一天的新闻

import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import datetime
from urllib import parse

#爬取操作函数
def get_news():
    # 创建chrome浏览器驱动，无头模式
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome()
    # 加载界面
    driver.get("https://news.sina.com.cn/world/")
    # 将滚动条调整至页面底部
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
    # 获取的url集合
    url = []
    # 当天新闻的url集合
    urlToday = []
    # txt读取的url集合
    u = []
    # 定义循环标识，用于终止爬取循环
    exc = True

    try:
        # 开始爬取
        while exc:
            # 获取页面初始高度
            js = "return action=document.body.scrollHeight"
            height = driver.execute_script(js)
            # 定义循环标识，用于终止页面上滑while循环
            status = True
            # 定义初始时间戳（秒）
            t1 = int(time.time())
            # 标志是否是第一次跳转后
            flag = 0
            while status:
                t2 = int(time.time())
                if t2 - t1 < 10:
                    new_height = driver.execute_script(js)
                    # 跳转到新页面或者新高度更大时下滑
                    if new_height > height or flag == 0:
                        flag = 1
                        time.sleep(2)
                        driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                        # 重置初始页面高度
                        height = new_height
                        # 重置初始时间戳，重新计时
                        t1 = int(time.time())
                else:
                    # 超时并超过重试次数，程序结束跳出循环，并认为页面已经加载完毕！
                    #print("滚动条已经处于页面最下方！")
                    status = False
                    break
            # 获取新闻链接
            for i in driver.find_elements_by_css_selector("#subShowContent1_static .news-item h2 a"):
                url.append(i.get_attribute('href'))
            # 判断是否已经不可拉动
            display = driver.find_element_by_xpath("//div[@class=\"load-more\"]")
            d = display.get_attribute('style')
            # 仍有可显示部分
            if (d == 'display: none;'):
                time.sleep(2)
                driver.find_element_by_class_name('pagebox_next').click()
                time.sleep(3)
            # 下拉无可显示部分
            else:
                exc = False
    except Exception as a:
        print('An error occurred！')
        raise RuntimeError('Error')

    # 打印链接(调试)
    #print(url)
    # 打印链接个数(调试)
    #print(len(url))
    # 关闭浏览器
    driver.quit()

    '''
    通过解析获取到的url，只保留前一天的新闻
    '''
    dateYestoday=datetime.date.today()-datetime.timedelta(days=1)

    for u in url:
        # url解码
        urldata = parse.unquote(u)
        # url结果
        result = parse.urlparse(urldata)
        #解析url获取时间  /w/2019-10-17/doc-iicezzrr2937406.shtml
        s = result.path
        #正则匹配日期
        m = re.search(r"(\d{4}-\d{1,2}-\d{1,2})",s)
        #未匹配到时间，根据新浪新闻url特点，可直接舍弃该url
        if(m is None):
            continue
        else:
            date2 = datetime.datetime.strptime(m.group(0),'%Y-%m-%d').date()
            #比较时间，获取前一天新闻
            if(date2==dateYestoday):
                urlToday.append(u)



    dateT = dateYestoday.strftime("%Y%m%d")
    #当日文件路径
    file_path = './sina_' + dateT + '.txt'
    try:
        #存入txt文件
        file_write_obj = open(file_path, 'w')
        for var in urlToday:
            file_write_obj.writelines(var)
            file_write_obj.write('\n')
        file_write_obj.close()
    except EOFError as e:
        print("wrote txt Error! ")

#开始爬取函数
def start():
    # 爬取结果标志
    sucF = False
    # 尝试次数
    count = 0
    # 尝试次数小于10次且未爬取成功
    while (count < 10 and sucF == False):
        try:
            get_news()
            sucF = True
        except Exception as a:
            count += 1
    if (count >= 5 or sucF == False):
        print("A network outage or other problem has occurred！！！")
    else:
        print("Success!!!!!!!!!!!!!!!")


start()

