import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import datetime

def sohucrawler():
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument("--start-maximized");
    driver = webdriver.Chrome()
    
    
    # 加载界面,由搜狐新闻跳转至搜狐国际新闻
    #driver.get("http://www.sohu.com/c/8/1461?spm=smpc.news-home.top-subnav.3.1571803717603cW05u0g")
    driver.get("http://news.sohu.com/")
    driver.find_elements_by_css_selector('.news-nav li a[data-spm-data="3"]')[0].click()
    all_window=driver.window_handles
    driver.switch_to.window(all_window[-1])
    time.sleep(3)
    
    # 获取页面初始高度
    js = "return action=document.body.scrollHeight"
    height = driver.execute_script(js)
    
    # 将滚动条调整至页面底部
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
    
    #定义初始时间戳（秒）
    t1 = int(time.time())
    
    #定义循环标识，用于终止while循环
    status = True
        
    while status:
        t2 = int(time.time())
        if t2-t1 < 3:
            new_height = driver.execute_script(js)
            if new_height > height :
                time.sleep(1)
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                # 重置初始页面高度
                height = new_height
                # 重置初始时间戳，重新计时
                t1 = int(time.time())
        else:    # 超时并超过重试次数，程序结束跳出循环，并认为页面已经加载完毕！
            print("滚动条已经处于页面最下方！")
            status = False
            break

    url_time=[]
    for i in driver.find_elements_by_css_selector(".news-wrapper div[data-role=news-item] .time"):
        url_time.append(i.text[:2])
    url=[]
    j=0
    for i in driver.find_elements_by_css_selector(".news-wrapper div[data-role=news-item] h4 a"):
        if(url_time[j]=='昨天'):#保留前一天新闻的url
            url.append(i.get_attribute('href').split('?')[0])
        j+=1
    url=set(url)
    driver.quit()
    return url

def get_today_url():
    today=datetime.datetime.now()
    today=datetime.datetime(today.year,today.month,today.day)
    try:
        new=sohucrawler()
        f=open('./inputs/sohu_'+str(today.year)+str(today.month)+str(today.day)+'.txt','w')
        for i in new:
            f.write(i+'\n')
        f.close()
        
    except:
        print("Crawl failure")
    else:
        print("Crawl succeed")
