# -*-coding:utf-8 -*-
# author:iris
# date:2018/11/29
# desc:访问相关数据接口，将得到的相关数据插入数据库中-2

import tornado.ioloop
import tornado.web
import tornado.httpserver
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
import config as CONFIG

from pymongo import MongoClient
import requests
import json
import time

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def spider_(url, send_data):
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
        return text

class BaseHandler(tornado.web.RequestHandler):
        executor = ThreadPoolExecutor(32)

class PaidHandler(BaseHandler):
        @run_on_executor
        def post(self):
                try:
			param = {}
                        params = json.loads(self.request.body)
			param['id'] = params.get('_id', '')
		except Exception, e:
                        param = None
                        print params,e
			self.finish({})
                        return ''
		try:
			ask_id = int(param['id'])
		except:
			ask_id = param['id']

		url1 = 'http://{}:{}/newask/'.format(CONFIG.insert_service_url, CONFIG.insert_service_port)
		url2 = 'http://{}:{}/new_news/'.format(CONFIG.insert_service_url, CONFIG.insert_service_port)
		

	   	if not ask_id:
                        self.finish({'status':0,'msg':'Please send id by json'})
                        return ''
		
		msg = ""
                send_data = {
      	                'id_': ask_id,
                }

		cur = CONFIG.ask_paid.find_one({'_id': ask_id})
		if not cur:
			cur = CONFIG.ask_good.find_one({'_id': ask_id})
		if not cur:
			cur = CONFIG.ask_bad.find_one({'_id': ask_id})
		if not cur:
			cur = CONFIG.real_good.find_one({'_id': ask_id})
		if not cur:
			self.finish({'status':0,'msg':'The id not in paid'+str(ask_id)})
                        return ''

		relatives = spider_(url1, send_data)
		doc = {}
		if relatives:
                       	doc['relatives'] = relatives
                        doc['_id'] = ask_id
                        doc['title'] = cur.get('title', '')
			try:
	                        CONFIG.asks_new.insert(doc)
	                        #CONFIG.asks.insert(doc)
				msg += "relatives is OK"
			except Exception, e:
				msg += ('asks_error' + str(e))
                else:
                        msg += "No relatives"
		

		doc = {}
		doc = spider_(url2, send_data)
		if doc:
			new = doc['news_data']
                        try:
                                CONFIG.news_new.insert(new)
                                #CONFIG.news.insert(new)
				msg += " news is OK"
                        except Exception,e:
                                print ask_id, 'error', e
				msg += (" news_error " + str(e))

                        recommend = {'_id':ask_id}
                        recommend['titles'] = doc['recommends']
                        if len(recommend['titles']) < 1:
                                print ask_id, 'no recommend'
				msg += 'recommends no title'
			else:
				msg += 'recommends is'
				
			try:
                                CONFIG.recommends_new.insert(recommend)
                                #CONFIG.recommends.insert(recommend)
				msg += " OK"
                        except Exception,e:
                                print ask_id, 'error', e
				msg += (" error " + str(e))
				
		else:
			msg += " No news and recommend"
		CONFIG.redis_set.set(str(ask_id), 1)
		
		self.finish({'status':1,'msg':msg})
		

class TestHandler(tornado.web.RequestHandler):
        def get(self):
                print 'index'
                self.write('hello iris, your has visit test paid_id')


application = tornado.web.Application([
        (r"/paid_id/", PaidHandler),
        (r'/.*', TestHandler),
])


if __name__ == '__main__':

        http_server = tornado.httpserver.HTTPServer(application)
        print 'come on'
        http_server.listen(CONFIG.use_service_port)
        tornado.ioloop.IOLoop.instance().start()

