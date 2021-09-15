# -*- coding:utf-8 -*-
# author: iris
# date: 2018/12/05
# desc: 每天获取新增付费问诊的数据,调用接口插入数据库中-3

import time
import json
import redis
import datetime
import requests
import config as CONFIG
from pymongo import MongoClient

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def spider_(send_data):
        data = json.dumps(send_data)
        start = time.time()
        try:
                rep = requests.post(url, data=data)
        except requests.RequestException as e:
                print 'error', e
                return ''
        rep.encoding = 'utf-8'
        try:
                text = json.loads(rep.text)
        except:
                print rep.text
                return ''
        if not text:
                print 'None'
                return ''
        return text

if __name__ == '__main__':
        #url = 'http://10.15.0.64:8103/paid_id/'
	url = 'http://{}:{}/paid_id/'.format(CONFIG.use_service_url, CONFIG.use_service_port)

	today = datetime.date.today()
	yesterday = today + datetime.timedelta(days = -1)

	redis_set2 = redis.Redis(host='10.5.0.10', port=6300, password='123123', db=13)
	redis_set = redis.Redis(host='10.5.0.10', port=6300, password='123123', db=14)
	#fid = open('/home/iris/newid/'+str(yesterday)+'.txt', 'r')
	print yesterday
	#print today
	i = 0
	#for line in fid.readlines():
		#line = line.strip()
		#id_ = line.split(' ')[0]
	#for id_ in redis_set2.keys():
	id_ = '55ea8c4151d0039ebc42cb6cd5c4a0e2'
	if id_:
		#count =  redis_set.get(id_)
		#if count:
		#	continue
		#count_ = redis_set2.get(id_)
		#if int(count_) < 3:
			#print id_, count_
		#	continue
		#print i, id_, count_
		#i += 1
                #continue

		send_data = {
        		'_id': id_,
	                }

		start = time.time()
		data = spider_(send_data)
		print data,
                if 'html' in data:
                       #break
			print data

		print 'times:', time.time() - start
                #time.sleep(0.03)

