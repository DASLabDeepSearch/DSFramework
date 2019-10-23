#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author : Du Qinghua
# @time : 2019/10/22 19:46
# @file : sina.py
# 爬取新浪国际新闻链接

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import datetime
import os

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

    # set去重网页链接
    url = set(url)
    # 打印链接(调试)
    #print(url)
    # 打印链接个数(调试)
    #print(len(url))
    # 关闭浏览器
    driver.quit()

    '''
    读取备份文件内容——剔除重复url
    若文件存在，则比较内容，只保留差集部分
    若文件不存在，全部保留
    '''
    #备份文件路径
    file_path_sum = 'e:/sina/sina.txt'
    try:
        if (os.path.isfile(file_path_sum)):
            with open(file_path_sum, "r") as f:
                for line in f:
                    line = line.strip('\n')
                    u.append(line)
        u = set(u)
    except EOFError as e:
        print("read txt Error! ")

    #差集，剔除重复url
    url=url.difference(u)


    dateT = datetime.datetime.now().strftime("%Y%m%d")
    #当日文件路径
    file_path = 'e:/sina/sina_' + dateT + '.txt'
    try:
        #存入txt文件
        file_write_obj = open(file_path, 'w')
        #追加到备份文件
        file_write_obj2 = open(file_path_sum, 'a')
        for var in url:
            file_write_obj.writelines(var)
            file_write_obj.write('\n')
            file_write_obj2.writelines(var)
            file_write_obj2.write('\n')
        file_write_obj.close()
        file_write_obj2.close()
    except EOFError as e:
        print("wrote txt Error! ")


if __name__ == '__main__':
    #爬取结果标志
    sucF=False
    #尝试次数
    count=0
    #尝试次数小于五次且未爬取成功
    while(count<5 and sucF==False):
        try:
            get_news()
            sucF = True
        except Exception as a:
            count+=1
    if(count>=5 or sucF==False):
        print("A network outage or other problem has occurred！！！")
    else:
        print("Success!!!!!!!!!!!!!!!")
