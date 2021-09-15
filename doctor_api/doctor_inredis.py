# -*- coding:utf-8 -*-
# date:2019-01-14
# author:iris
# desc: 医生审核系统增加分发配置，redis中存储问题的指定医生数据

import time
import json
import config as CONFIG

import tornado.ioloop
import tornado.web
import tornado.httpserver

import sys
reload(sys)
sys.setdefaultencoding('utf8')

class UpdateHandler(tornado.web.RequestHandler):
	def post(self):
		global count
		try:
			body = self.request.body
			param = json.loads(self.request.body)
			source = param.get("source", "")
			price = int(param.get("price", 0))
			department = param.get("department", "")
			nums = param.get("nums", "")
			#data_nos = param.get('no_group')
			if nums >= 1:
				data_good = param.get('good_group')
			else:
				data_good = None
			if nums >= 2:
				data_normal = param.get('normal_group')
			else:
				data_normal = None
			if nums >= 3:
				data_other = param.get('other_group')
			else:
				data_other = None

		except Exception, e:
			print 'body is None', body
			source = None
			price = None
			print e

		doc_ids = set() #设置医生id集合，方便查重

		if not department or not source or not price:
			self.finish(json.dumps({'msg': "must have department, source and price", 'error_code': 1003}))
			return
		else:
			print 'department', department, 'price', price, 'source', source, 'nums', nums 
		'''
		# 未分组数据
		if data_nos:
			for data_no in data_nos:
				doc_ids.add(data_no['_id'])
		else:
			self.finish(json.dumps({'msg': "no_group doctor repeat", 'error_code': 1004}))
			return 
		'''
		def cnki_doc_ip(data_docs):
			#global doc_ids
			ids = []
			for data_doc in data_docs:
 	                	doc_id = data_doc['_id']
				ids.append(doc_id)
				if doc_id in doc_ids:
					return False
				else:
					doc_ids.add(doc_id)
			return ids

		# 优质组
		if data_good:
			if data_good.get('doctor', []):
				good_docs = data_good['doctor']
				status = cnki_doc_ip(good_docs)
				if status == False:
					self.finish(json.dumps({'msg': "good_group doctor id repeat", 'error_code': 1004}))
					print 'data_good id repeat'
					return 
				else:
					good_ids = status
			else:
				good_ids = []

		# 普通组
		if data_normal:
			if data_normal.get('doctor', []):
				normal_docs = data_normal['doctor']
				status = cnki_doc_ip(normal_docs)
				if status == False:
					self.finish(json.dumps({'msg': "normal_group doctor id repeat", 'error_code': 1004}))
					print 'data_normal id repeat'
	                        	return 
				else:
					normal_ids = status
			else:
				normal_ids = []

		# 其他组
		if data_other:
			if data_other.get('doctor', []):
				other_docs = data_other['doctor']
				status = cnki_doc_ip(other_docs)
				if status == False:
                        		self.finish(json.dumps({'msg': "other_group doctor id repeat", 'error_code': 1004}))
					print 'data_other id repeat'
	                        	return 
				else:
					other_ids = status
			else:
				other_ids = []
		
		#cur = CONFIG.doc_set.find_one({'department':department, 'source':source, 'price':price, 'group_name': 'no_group'})
		#if not cur:
		#	print 'department', department, 'source', source, 'price', price
		#	self.finish(json.dumps({'msg': "department,source,price may error", 'error_code': 1003}))
                #       return

		#id_ = cur['_id']
		#CONFIG.doc_set.update({'_id': id_}, {'$set': {'doctor': data_nos['doctor']}})

		num = 0
		redis_id = source + '_' + department + '_' + str(price) + '_1'
		if nums >= 1 and data_good:
			if data_good.get('doctor',[]):
				num += 1
			cur = CONFIG.doc_set.find_one({'department':department, 'source':source, 'price':price, 'group_name': 'good_group'})
			if cur:
				id_ = cur['_id']
				CONFIG.doc_set.update({'_id': id_}, {'$set': {'time': int(data_good.get('time', 0)), 'name':data_good['name'], 'doctor': data_good.get('doctor',[])}})
			else:
				#count = CONFIG.doc_set.count() + 1
				id_ = source + '_' + department + '_' + str(price) + '_1'
				try:
					CONFIG.doc_set.insert({'_id': id_, 'department':department, 'source':source, 'price':price, 'time': int(data_good.get('time', 0)), 'name':data_good['name'], 'group_name': 'good_group', 'doctor': data_good.get('doctor',[])})
				except Exception, e:
					print id_, e
					return
				count += 1

			if good_ids:
				redis_doc = {'doctor': good_ids, 'time': data_good['time']}
				print redis_id, 'good_ids', good_ids
				CONFIG.redis_set.hmset(redis_id, redis_doc)
		else:
			CONFIG.redis_set.delete(redis_id)

		redis_id = source + '_' + department + '_' + str(price) + '_2'
		if nums >= 2 and data_normal:
			if data_normal.get('doctor', []):
				num += 1
			cur = CONFIG.doc_set.find_one({'department':department, 'source':source, 'price':price, 'group_name': 'normal_group'})
			if cur:
				id_ = cur['_id']
				CONFIG.doc_set.update({'_id': id_}, {'$set': {'time': int(data_normal.get('time', 0)), 'name': data_normal['name'], 'doctor': data_normal.get('doctor', [])}})
			else:
				#count = CONFIG.doc_set.count() + 
				id_ = source + '_' + department + '_' + str(price) + '_2'
				try:
					CONFIG.doc_set.insert({'_id': id_, 'department':department, 'source':source, 'price':price, 'time': int(data_normal.get('time', 0)), 'name': data_normal['name'], 'group_name': 'normal_group', 'doctor': data_normal.get('doctor',[])})
				except Exception, e:
					print id_, e
					return
			if normal_ids:
				redis_doc = {'doctor': normal_ids, 'time': data_normal['time']}
				print redis_id, 'normal_ids', normal_ids
				CONFIG.redis_set.hmset(redis_id, redis_doc)
		else:
			CONFIG.redis_set.delete(redis_id)
				

		redis_id = source + '_' + department + '_' + str(price) + '_3'
		if nums >= 3 and data_other:
			if data_other.get('doctor', []):
				num += 1
			cur = CONFIG.doc_set.find_one({'department':department, 'source':source, 'price':price, 'group_name': 'other_group'})
			if cur:
				id_ = cur['_id']
				CONFIG.doc_set.update({'_id': id_}, {'$set': {'time': int(data_other.get('time', 0)), 'name': data_other['name'], 'doctor': data_other.get('doctor', [])}})
			else:
				#count = CONFIG.doc_set.count() + 1
				id_ = source + '_' + department + '_' + str(price) + '_3'
				CONFIG.doc_set.insert({'_id': id_, 'department':department, 'source':source, 'price':price, 'time': int(data_other.get('time', 0)), 'name': data_other['name'], 'group_name': 'other_group', 'doctor': data_other.get('doctor', [])})

			if other_ids:
				redis_doc = {'doctor': other_ids, 'time': data_other['time']}
				print redis_id, 'other_ids', other_ids
				CONFIG.redis_set.hmset(redis_id, redis_doc)
		else:
			CONFIG.redis_set.delete(redis_id)

		redis_ids = source + '_' + department + '_' + str(price)
		CONFIG.redis_set.hset(redis_ids, 'nums', num)

		self.finish(json.dumps({'msg': "succeed", 'error_code': 0}))


class FindHandler(tornado.web.RequestHandler):
	def get(self):
		print 'FindHandler get', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
		self.write('Please send data(json type) by https://rightname/doctorsend/doctor/category/find')
	
	def post(self):

		try:
			body = self.request.body
			param = json.loads(self.request.body)
			#source = self.get_argument("source")
			#price = int(self.get_argument("price"))
			#department = self.get_argument("department").strip()
			#id_list = body.getlist("id_list")
			source = param.get("source", "")
			price = int(param.get("price", 0))
			department_find = param.get("department_find", "")
			department = param.get("department", "")
			id_list = param.get("id_list", [])
			
		except Exception, e:
			print 'body is None', body
			source = None
			price = None
			print e

		if not source or not price:
			self.finish(json.dumps({"data": '', 'error_code': 1003}))
			return

		print 'department', department, 'price', price, 'source', source, 'id_list', id_list, 'department_find',department_find
			
		doctors = {}
		id_has = []
		if department_find:# 配置按钮，返回科室的医生，然后在未分组中分到其他组的医生
			cursors = CONFIG.doc_set.find({"source": source, "price": price, "department": department_find})
			id_has = []
			for cursor in cursors:
				group_name = cursor.get('group_name', '')
				name = cursor.get('name', '')
				if group_name == 'no_group':
					if group_name in doctors:
						doctors[group_name].extend(cursor.get('doctor'))
					else:
						doctors[group_name] = cursor.get('doctor')
				else:
					if group_name in doctors:
						doctors[group_name]['doctor'].extend(cursor.get('doctor', []))
					else:
						group = {"time": cursor.get('time', 0), "name": name, "doctor":  cursor.get('doctor', [])}
						doctors[group_name] = group
						id_has.extend([doctor.get('_id', '') for doctor in cursor.get('doctor', [])])# 将其他分组的id存起来
			if id_has:
				print 'id_has', id_has
				doctors["no_group"] = [doctor for doctor in doctors["no_group"] if doctor.get('_id', '') not in id_has]
			else:
				pass
			if not doctors:
				print 'doctor no data'
				self.finish(json.dumps({"data": "", 'error_code': 1005}))
				return
			self.finish(json.dumps({"data": doctors, 'error_code': 0}))
		elif department:# 筛选按钮，未分组医生需要除去参数id_list中的id，其他分组返回department的医生
			cursor = CONFIG.doc_set.find_one({"source": source, "price": price, "department": department, 'group_name': 'no_group'})
			group_name = cursor.get('group_name', '')
			name = cursor.get('name', '')
			if group_name in doctors:
				doctors[group_name].extend(cursor.get('doctor'))
			else:
				doctors[group_name] = cursor.get('doctor')
			if id_list: # 未分组除去id_list的id
				print 'id_list', id_list
				no_group = [doctor for doctor in doctors["no_group"] if doctor['_id'] not in id_list]
			else:
				no_group = doctors.get("no_group",'')
			doctors["no_group"] = no_group
			if not doctors:
				print 'doctor no data'
				self.finish(json.dumps({"data": "", 'error_code': 1005}))
				return
			self.finish(json.dumps({"data": doctors, 'error_code': 0}))

		else:
			print 'department', department, 'department_find', department_find
			self.finish(json.dumps({"data": '', 'error_code': 1003}))
			return

class DelHandler(tornado.web.RequestHandler):
	def get(self):
		print 'FindHandler get', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
		self.write('Please send data by https://rightname/doctorsend/doctor/delgroup')

	def post(self):
		try:
			source = self.get_argument("source")
			price = int(self.get_argument("price"))
			department = self.get_argument("department").strip()
			group_name = self.get_argument("group_name")
		except:
			self.finish(json.dumps({"msg": "param error", 'error_code': 1003}))
			print 'body', self.request.body
			return

		
		cursor = CONFIG.doc_set.find_one({"source": source, "price": price, "department": department, "group_name": group_name})
		if cursor:
			'''
			if cursor["doctor"]:
				CONFIG.doc_set.update({"source": source, "price": price, "department": department, "group_name": "no_group"}, {"$addToSet": {'doctor': cursor["doctor"]}})
			'''
			try:
				CONFIG.doc_set.remove({'_id': cursor['_id']})
				if group_name == "good_group":
					redis_id = source + '_' + department + '_' + str(price) + '_1'
				elif group_name == "normal_group":
					redis_id = source + '_' + department + '_' + str(price) + '_2'
				elif group_name == "other_group":
					redis_id = source + '_' + department + '_' + str(price) + '_3'
				else:
					pass
				CONFIG.redis_set.delete(redis_id)
				print CONFIG.redis_set.hincrby(source + '_' + department + '_' + str(price), "nums", -1)
				print 'DelHandler has del ', source, department, price, group_name, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
			except Exception, e:
				self.finish(json.dumps({"msg": str(e), 'error_code': 1005}))
				return
		else:
			#self.finish(json.dumps({"msg": "no cursor", 'error_code': 1004}))
			self.finish(json.dumps({"msg": "succeed", 'error_code': 0}))
			return
		self.finish(json.dumps({"msg": "succeed", 'error_code': 0}))

class CateHandler(tornado.web.RequestHandler):
        def get(self):
		cate = []
		for cur in CONFIG.cate_set.find({'pid': {'$ne': 2}}):
			if cur['name'] == u'偏方秘方':
				continue
			cate.append(cur['name'].decode('utf-8'))
		result = json.dumps({"data":cate, 'error_code':0})
		self.finish(result)
	def post(self):
		try:
			params = json.loads(self.request.body)
			source = params.get('source', '')
			price = params.get('price', 0)
		except Exception, e:
			print e
			self.finish(json.dumps({"error_code":1003, "msg": str(e)}))
			return
		if not source or not price:
			self.finish(json.dumps({"error_code": 1003, "msg": "not source or not price"}))
			return
		cate = []
		print 'CateHandler post'
		for cur in CONFIG.cate_set.find({'$or': [{'pid':0}, {"pid":1}, {'pid':2}]}):
			if cur['name'] == u'偏方秘方':
				continue
			department = cur.get('name')
			redis_ids = source + '_' + department + '_' + str(price)
			nums = CONFIG.redis_set.hget(redis_ids, 'nums')
			doc_num = 0
			if nums:
				for i in range(int(nums)):
					redis_id = redis_ids + '_' + str(i+1)
					doc_str = CONFIG.redis_set.hget(redis_id, 'doctor')
					if doc_str:
						doc_str = doc_str.replace(']', '').replace('[', '')
						doc_list = doc_str.split(',')
						#print doc_list, len(doc_list), type(doc_list)
						doc_num += len(doc_list)
					
				data = {"name": cur.get('name'.decode('utf-8')), "group_num": nums, "doc_num": doc_num}
			else:
				data = {"name": cur.get('name'.decode('utf-8')), "group_num": '0', "doc_num": '0'}
			cate.append(data)
			#print data
		result = json.dumps({"data":cate, 'error_code':0})
		self.finish(result)
		
class NewHandler(tornado.web.RequestHandler):
	def update_data(self, source, departments):
		set_count = CONFIG.doc_set.count()
		if set_count:
			id_ = (set_count + 1)
		else:
			id_ = 1
		name = 'no_group'
		if source == '已打码':
			prices = [8, 10, 25, 30]
		else:
			prices = [3, 5]
		print 'update-time: ', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
		for department in departments:
			for price in prices:
				if price == 3:
					cursors = CONFIG.doc_message.find({'department': department, 'hospital_level': '二级甲等'})
				elif price == 5:
					cursors = CONFIG.doc_message.find({'department': department, 'hospital_level': '三级甲等'})
				elif price == 8:
					cursors = CONFIG.doc_message.find({'department': department})
				elif price == 10:
					cursors = CONFIG.doc_message.find({'department': department, '$or':[{'hospital_level': '二级甲等'}, {'hospital_level': {"$regex": '三级'}}]})
				else:
					cursors = CONFIG.doc_message.find({'department': department, 'hospital_level': '三级甲等'})
	
				print id_, department, price
				group = []
				for cursor in cursors:
					#if cursor.get('is_test') == 1:
						#	continue
					data = {'name': cursor.get('name', '')}
			                data['_id'] = cursor.get('_id', '')
        			        data['hospital_level'] = cursor.get('hospital_level', '')
					data['clinical_title'] = cursor.get('clinical_title', '')
					group.append(data)
					print data['name'], data['clinical_title'], data['hospital_level']
				
				doc = {
						'_id': id_,
						'department': department,
						'price': price,
						'source': source,
						'group_name': name,
						'doctor': group,
					}

				try:
					#CONFIG.doc_set.save(doc)
					if CONFIG.doc_set.find_one({"source": source, "price": price, "department": department, 'group_name': 'no_group'}):
						CONFIG.doc_set.update({"source": source, "price": price, "department": department, 'group_name': 'no_group'}, {'$set': {'doctor': group}})
					else:
						CONFIG.doc_set.save(doc)
					id_ += 1
				except Exception, e:
					print e
					return e
					
		return 'succeed'
	def get(self):
		departments = []
		for cur in CONFIG.cate_set.find({'$or': [{'pid':0}, {"pid":1}, {'pid':2}]}):
			if cur.get('name') == u'偏方秘方':
				continue
			departments.append(cur.get('name'))
			#print cur.get('name')
		source = '已打码'
		res = self.update_data(source, departments)
		print source, 'update now', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
		source = 'sogou'
		res_ = self.update_data(source, departments)
		print source, 'update now', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
		if res == 'succeed' and res_ == 'succeed':
			self.write(json.dumps({"error_code":0, 'msg': 'succeed'}))
		else:
			if not res:
				res = ''
			else:
				res = str(res)
			if not res_:
				res_ = ''
			else:
				res_ = str(res_)
			#self.write('已打码' + res + '\nsogou' + res_)
			self.finish(json.dumps({"error_code":1003, "msg": '已打码' + res + '\nsogou' + res_}))
		

class TestHandler(tornado.web.RequestHandler):
	def get(self):
		print 'TestHandler get', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
		self.write('Please ask data by https://rightname/doctorsend/doctor/category or new')
	def post(self):
		print 'TestHandler post', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
		self.write('Please send data(json type) by https://rightname/doctorsend/doctor/find')

	
application = tornado.web.Application([
	(r'/doctorsend/doctor/update', UpdateHandler),
	(r'/doctorsend/doctor/find', FindHandler),
	(r'/doctorsend/doctor/category', CateHandler),
	(r'/doctorsend/doctor/delgroup', DelHandler),
	(r'/doctorsend/doctor/new', NewHandler),
        (r'.*', TestHandler),
])

if __name__ == '__main__':
	count = 100
	http_server = tornado.httpserver.HTTPServer(application)
	print 'come on'
	http_server.listen(port)
	tornado.ioloop.IOLoop.instance().start()
	

