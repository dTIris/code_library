# -*- coding:utf-8 -*-
# author = Iris
# create = 2018/08/27

import time
import urllib
import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado.escape import json_decode
import json
import chardet

import sys
reload(sys)
sys.setdefaultencoding('utf8')

ugly = {}
with open('word_ugly.txt', 'r') as f:
	while True:
		line = f.readline()
		if not line:
			break
		line = line.strip()
		first = line.split(":")[0].decode('utf-8')
		if line.split(":")[1]:
			other = []
                        for o in line.split(":")[1].split(","):
				if o == '':
                                        continue
                                other.append(o.decode('utf-8'))
                        ugly[first] = other

		else:
			ugly[first] = ['',]

class MainHandler(tornado.web.RequestHandler):
	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        	self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
	def get(self):
		self.write('You use error way,Please post data!!!')
	def options(self):
		self.write('You use error way,Please post data!!!')
	def post(self):
		#i = 0
		self.set_header("Content-Type", "application/json;charset=utf-8")
		#jsentence = self.request.body
		try:
			body = self.request.body.replace('\t', '').replace(' ', '').replace('\n', '').replace('\r', '').replace('-','').replace('~', '').strip()
			jsentence = json_decode(body)
			sentence = jsentence['sentence']
			print sentence
			sentence = urllib.unquote(sentence)
		except Exception, e:
			sentence = self.request.body + 'is not json type'
			print 'body is ', self.request.body
			print 'error: ', e
		print sentence, '-encoding:', type(sentence)
		sub = 1
		time_ = time.time()
		msg = 'It is OK!'
		#result = {}
		result = 1 # 默认通过，1
		# 遍历句子
		for s in sentence:
			# 若含有敏感词的第一个字则进行查询
			if s in ugly:
				other = ugly[s]
				# 若无other，则该单字为敏感词，停止循环并输出
				if not other[0]:
					msg = 'The word is not allow:' + s.encode('utf-8')
					#result = {"state": 1, "massage": msg, "time": time.time()-time_}
					result = 0
					print msg
					break
				# 若有other，则遍历该列表，直到找到相同的单词 
				else:
					for o in other:
						length = len(o) + sub
						if sentence[sub:length] == o:
							msg = 'The word is not allow:' + s.encode('utf-8') + o.encode('utf-8')
							#result = {"state": 1, "massage": msg, "time": time.time()-time_}
							result = 0
							print msg
							break
				# 需要退出第一层遍历
				#if result:
				if not result:
					break
			sub += 1
		#if not result:
		if result:
			result = 1
			#result = {"state": 0, "massage": msg, "time": time.time()-time_}
			print msg
		#i += 1
		#print '第', i, '次'
		jresult = json.dumps(result)
		self.write(jresult+'\n')
		with open('sentence.log', 'a+') as f:
			f.write(sentence.encode('utf-8')+msg+'\n')
		#self.write(result)
class TestHandler(tornado.web.RequestHandler):
	def get(self):
		self.write('Hello, This is Iris Test!')

if __name__ == '__main__':
	application = tornado.web.Application([
		(r'/index', TestHandler),
		(r'/sentence/', MainHandler),
	],
		#debug=True
	)
	http_server = tornado.httpserver.HTTPServer(application)
	print 'start'
	http_server.listen(8181)
	tornado.ioloop.IOLoop.instance().start()

