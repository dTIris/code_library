#!/usr/bin/python
# -*- coding:utf-8 -*-

from pymongo import MongoClient
from xml.dom import minidom
import time
import datetime
import redis
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class data(object):
	
	def connect(self, ip, port):
		conn = MongoClient(ip, port)
		
		if conn == None:
			print(ip + "error connect")
		return conn

	def get_data(self):
		#问答大库
		oldconn = self.connect()
		ask_db = oldconn["analysis_data"]
		ask_db.authenticate()
		
		conn = self.connect()
		iris_db = conn['iris_360']

		#问答集合
		self.olddb_good = ask_db["ask_good"]
		self.doctor = iris_db["ask_doctor"]
	def generate_xml(self):
		file1 = open('id1.txt', 'r')
		times = 0 #记录文件数
		coin = 0  #控制文件数
		nouse = 0 #掠过的id数
		#统计找不到的id
		self.notin = 0
		self.f1 = open('no_id.txt', 'w')
		time_start = time.time()
		while 1:
			self.dom = minidom.Document()
			#根节点
			root = self.dom.createElement('urlset')
			root.setAttribute()
			self.dom.appendChild(root)
			
			# 退出
			if coin < 0:
				break

			#记录文档数
			i = 0
			#当文档数到达3300时退出
			#print 'coin=',coin
			coin += 1
			while i < 3300:
				line = file1.readline()
				line = line.strip()
				if not line:
					coin = -10
					print 'not line'
					break
				print 'line=',line
				result = self.xml_url(line, root)
				if result:
					i += 1
				else:
					nouse += 1	
			times += 1
			name = 'datas/data_1_' + str(times) + '.xml'
			self.file_write(name)
			print '第', times, '次, times:', time.time() - time_start
			#break
		time_end = time.time()
		print '无效id为：', self.notin, '个'
		print '掠过了', nouse, '个id'
		print '共花了：', time_end - time_start, '时间'
		self.f1.close()
	def xml_url(self, x_id, root):
		#根据id找出文档
		try:
			x_id = int(x_id)
		except Exception,e:
			print x_id, 'not int'

		x = self.olddb_good.find_one({'_id': x_id})

		if not x:
			print '此id：', x_id,type(x_id), '不存在'
			self.notin += 1
			self.f1.write(str(x_id))
			x = None
			return 0
		
		post = x.get('best_score_subscript', 0)

		answer = x.get('answer', [])

		if not len(answer):
			print '此id: ', x_id, 'no answer'
			return 0

		doc_id = x['answer'][post]['id']
                doctor_ = self.doctor.find_one({'_id': doc_id})
		
		if not doctor_:
			p = post
			i = 0
			#遍历该答案，跳过判断过的最佳答案，若答案的医院在redis存在，则输出
			for answer in x.get('answer'):
				if i == p:
					i += 1
					continue
				doc_id = answer['id']
				doctor_ = self.doctor.find_one({'_id': doc_id})
				if doctor_:
					break
				i += 1

		if not doctor_:
			print '此id: ', x_id, '该医生', doc_id, '不行'
			return 0
            	hospital = doctor_.get("hospital", '')
			

		#url节点
		url = self.dom.createElement('url')
		#url下面的子节点

		#loc
		loc_e = self.dom.createElement('loc')
                loc = 'https://www.打码.com/question/' + str(x['_id']) + '.html'
		loc_text = self.dom.createTextNode(loc)
		loc_e.appendChild(loc_text)
		url.appendChild(loc_e)

		#lastmod
		lastmod_e = self.dom.createElement('lastmod')				
		lastmod = x['answer'][post]['answer_date'].replace(' ', 'T')
		if lastmod:
			lastmod_text = self.dom.createTextNode(lastmod)
			lastmod_e.appendChild(lastmod_text)
			url.appendChild(lastmod_e)

		#changefreq
		changefreq_e = self.dom.createElement('changefreq')
		changefreq = 'always'
		changefreq_text = self.dom.createTextNode(changefreq)
		changefreq_e.appendChild(changefreq_text)
		url.appendChild(changefreq_e)

		#priority
		priority_e = self.dom.createElement('priority')
		priority = '0.8'
		priority_text = self.dom.createTextNode(priority)
		priority_e.appendChild(priority_text)
		url.appendChild(priority_e)

		#data
		data_e = self.dom.createElement('data')
		url.appendChild(data_e)

		#display
		display = self.dom.createElement('display')
		data_e.appendChild(display)

		#headline
		headline_e = self.dom.createElement('headline')
		headline = x['title'].replace('"', '”').replace('\b','').replace('\t', '').replace('\n', '').strip()
		if len(headline) < 5:
			print '此id: ', x_id, 'title', headline, '太短'
			return 0
		if headline:
			headline_text = self.dom.createTextNode(headline)
			headline_e.appendChild(headline_text)
			display.appendChild(headline_e)

		#waplink
		waplink_e = self.dom.createElement('waplink')
		waplink = 'https://m.打码.com/question/' + str(x['_id']) + '.html'
		waplink_text = self.dom.createTextNode(waplink)
		waplink_e.appendChild(waplink_text)
		display.appendChild(waplink_e)

		#pclink
		pclink_e = self.dom.createElement('pclink')
		pclink = 'https://www.打码.com/question/' + str(x['_id']) + '.html'
		pclink_text = self.dom.createTextNode(pclink)
		pclink_e.appendChild(pclink_text)
		display.appendChild(pclink_e)

		#answer
		special_chars=u'[\u3000,\x08,\xa0,\x3000,\x20,\x14,\x01,\x00,\x04,\x1a,\x1b,\x11,\x00-\x08\x0b-\x0c\x0e-\x1f]'
		answer_e = self.dom.createElement('answer')
		answer_bqfx = x['answer'][post]['answer_bqfx']
		answer_zdyj = x['answer'][post]['answer_zdyj']
		answer_other = x['answer'][post]['answer_other']
		answer_summary = x['answer'][post]['answer_summary']
		answers = (answer_bqfx + answer_zdyj + answer_other + answer_summary)
		dr = re.compile(r'<[^>]+>', re.S)
		answers = dr.sub('', answers)
		answers = re.sub('\s', '', re.sub(special_chars, u'', answers.strip()))
		#answer = re.sub(r'<a href\=\"(http:\/\/[a-zA-Z0-9\.\/?]+)\">', '', answers)
		answer = answers.replace('<br>', '').replace('</a>', '').replace('"', '”').replace('&', '').replace(' ', '').replace('<', '《').replace('>', '》')
		if answer:
			answer_text = self.dom.createTextNode(answer)
			answer_e.appendChild(answer_text)
			display.appendChild(answer_e)

		# print 'answer=',answer,'\n',answer_text,'\n',answer_e

		#answer_cnt
		answer_cnt_e = self.dom.createElement('answer_cnt')
		answer_cnt = str(x['ans_num'])
		answer_cnt_text = self.dom.createTextNode(answer_cnt)
		answer_cnt_e.appendChild(answer_cnt_text)
		display.appendChild(answer_cnt_e)

		#doctor
		
		doctor_e = self.dom.createElement('doctor')
		doctor_n = x['answer'][post]['name']
		re_name = re.compile(u"[\u4e00-\u9fa5]+")
		doctor_group = re_name.search(doctor_n, 0)
		if not doctor_group:
			print x_id, doctor_n, 'not name'
			return 0
		doctor = doctor_group.group()
		if not doctor or len(doctor) <2:
                	print x_id, doctor_n, 'too short'
			return 0
		doctor_text = self.dom.createTextNode(doctor_n)
		doctor_e.appendChild(doctor_text)
		display.appendChild(doctor_e)

		#hospital
		hospital_e = self.dom.createElement('hospital')
	
		# print '--',type(hospital)
		hospital_text = self.dom.createTextNode(hospital)
		hospital_e.appendChild(hospital_text)
		display.appendChild(hospital_e)

		#department
		department_e = self.dom.createElement('department')	
		department = doctor_["department"]
		if department:
			department_text = self.dom.createTextNode(department)
			department_e.appendChild(department_text)
			display.appendChild(department_e)

		#doctor_title
		doctor_title_e = self.dom.createElement('doctor_title')
		doctor_title = x['answer'][post]['position']
		doctor_title_text = self.dom.createTextNode(doctor_title)
		doctor_title_e.appendChild(doctor_title_text)
		display.appendChild(doctor_title_e)
		
		#doctor_pic  
		doctor_pic_e = self.dom.createElement('doctor_pic')

		img_name = doctor_['img_name']
	
		if not img_name:
			img_name = doc_id
		doctor_pic = 'http://tcdn.打码.com/newimages/doctor/' + img_name
		doctor_pic_text = self.dom.createTextNode(doctor_pic)
		doctor_pic_e.appendChild(doctor_pic_text)
		display.appendChild(doctor_pic_e)

		#from
		from_e = self.dom.createElement('from')
		from_ = '打码'
		from_text = self.dom.createTextNode(from_)
		from_e.appendChild(from_text)
		display.appendChild(from_e)
		
		#time
		time_e = self.dom.createElement('time')
		time_ = x['date'].strip()
		time1 = time_.split(' ')[0]
		try:
			d1 = datetime.datetime.strptime(time1, '%Y-%m-%d')
		except Exception, e:
			print '此id：', x_id, time_, time1, 'date error'
			
			return 0		
		time_text = self.dom.createTextNode(time1)
		time_e.appendChild(time_text)
		display.appendChild(time_e)
		
		#showurl
		showuel_e = self.dom.createElement('showurl')
		showuel = '打码.com'
		showuel_text = self.dom.createTextNode(showuel)
		showuel_e.appendChild(showuel_text)
		display.appendChild(showuel_e)

		root.appendChild(url)
		return 1
		
	def file_write(self, filename):

		f = open(filename, 'w')
		self.dom.writexml(f, addindent='\t', newl='\n', encoding = 'utf-8')
		f.close()

	def run(self):
		d.get_data()
		d.generate_xml()

if __name__ == '__main__':
	d = data()
	d.run()	
		
