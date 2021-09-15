# coding:utf-8
# author:iris
# date:2019/01/27
# 监控关键词在搜狗搜索页中m域名的排名

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import time
import argparse
import urlparse
from selenium import webdriver
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from pymongo import MongoClient
import datetime
from selenium.webdriver.chrome.options import Options

M_FIRSTPAGE="https://m.sogou.com/web/searchList.jsp?keyword={0}"
M_SECONDPAGE="https://m.sogou.com/web/search/ajax_query.jsp?keyword={0}&p=2"


def statistics(url, keyword, driver, step=0, rankings = None):
    '''
    :param url: the sogo page url
    :param keyword: 感冒了怎么办
    :param driver:  the instance of firefox driver
    :param page: 0,1
    :param rankings: as the following
    :return: rankings
    '''

    if rankings is None:
        rankings = {"_id":keyword, "rankings": {}, "m_wap": 0, "m_m":0,
                    "results": 0}
    count = 0
    driver.get(url.format(keyword))
    html = driver.execute_script("return document.documentElement.outerHTML")
    soup = BeautifulSoup(html, 'lxml')
    for item in soup.find_all("h3", class_="vr-tit"):
        for child in item.children:
            if child.name == "a":
                count += 1
                try:
                    url_quries = urlparse.parse_qs(urlparse.urlparse(child["href"]).query)
                except:
                    continue
  
                if "url" not in url_quries:
                    continue

                for url in url_quries["url"]:
                    if url.find("wap.169kang.com") != -1:
                        rankings["results"] += 1
                        rankings["rankings"][str(count+step)] = 2
                        rankings["m_wap"] += 1
		    if url.find("m.169kang.com") != -1:
                        rankings["results"] += 1
                        rankings["rankings"][str(count+step)] = 3
                        rankings["m_m"] += 1

    return rankings

if __name__ == "__main__":
    
    mongo_conn = MongoClient()
    db = mongo_conn[""]
    display = Display(visible=0, size=(800,600))
    display.start()
    user_agent = "Mozilla/5.0 (Windows NT 10.0;) Gecko/20100101 Firefox/60.0"
    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override", user_agent)
    driver = webdriver.Firefox(firefox_profile = profile, executable_path="filepath/monitor/geckodriver")
    today_str = datetime.datetime.now().strftime("%Y%m%d")
 
    start = time.time()
    with open("filepath/monitor/hot.txt") as f:
        for line in f:
            keyword = line.strip().replace("\r\n", "").replace("\n", "")
            rankings = statistics(M_FIRSTPAGE, keyword, driver)
            rankings = statistics(M_SECONDPAGE,keyword, driver, 10, rankings)
	    print line.strip(), rankings
	    try:
	            db[today_str].save(rankings)
	    except Exception, e:
		    print e

    print "ending time", time.time() - start
    driver.quit()
    display.stop()
