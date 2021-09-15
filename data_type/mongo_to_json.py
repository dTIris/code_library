# -*- coding:utf-8 -*-

from pymongo import MongoClient
from collections import OrderedDict
import re
import json
import time

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# 问答数据
client_ = MongoClient()
db_ = client_['analysis_data']
db_.authenticate()
ask_good = db_['ask_good']
ask_doctor = db_['ask_doctor']

client = MongoClient()

db0 = client['relatives_cold_0']
db0.authenticate()
new0 = db0['news']

db1 = client['relatives_cold_1']
db1.authenticate()
new1 = db1['news']

db2 = client['relatives_cold_2']
db2.authenticate()
new2 = db2['news']

db3 = client['relatives_cold_3']
db3.authenticate()
new3 = db3['news']

db4 = client['relatives_cold_4']
db4.authenticate()
new4 = db4['news']

db = client['relatives_warm']
db.authenticate()
new = db['news']


ORDERED_TOTAL_KEYS = ['key', 'question', 'wapurl','url','queDesc', 'from', 'showurl', 'answer','tags', 'diseaseTags','answerMan', 'patient']

ORDERED_ANS_KEYS = ['name', 'level', 'hospital', 'hospitalLv', 'expertDescr', 'department', 'iconUrl']

ORDERED_PAT_KEYS = ['gender', 'ageKey', 'shortAppeal', 'city']


def special_sign(_str):
        _str = _str.decode('utf-8')
        _list = list(_str)
        n = len(_list)
        if n <= 1:
                return _str
        list1 = []
        for i in range(n-1):
                if _list[i] in u".!/_,$%^*(+\"'+——！，。？、~@#￥%……&*（）":
                        if _list[i] != _list[i+1]:
                                list1.append(_list[i])
                else:
                        list1.append(_list[i])
        list1.append(_list[-1])
        str1 = ''.join(list1)
        return str1

i = 0
kk = 0
with open('id1.txt', 'r') as f:
	lines = f.readlines()

startime = time.time()

base = 'sougou_medicine_1_'
f = open('json1/'+ base + '1.json', 'w')
num_file = 1
#for cur in ask_good.find().batch_size(3000):
for line in lines:
	line = line.strip()
	
	line = int(line)

	cur = ask_good.find_one({'_id': line})

	if not cur:
		print line, 'not cur'
		continue

	if i % 5000 == 0:
		print 'times:', time.time() - startime
	#if i == 2500:
	#	break
	id_ = cur.get('_id', 0)
	key = str(id_)

	dr = re.compile(r'<[^>]+>', re.S)

	question = cur.get('title', '')
	question = dr.sub('', question)
	queDesc = cur.get('content', '')
	queDesc = dr.sub('', queDesc)
	queDesc = queDesc.replace('BR>', '')
	if len(question) < 5 and len(queDesc) >= 15:
		ques = question
		question = queDesc[0:15]
		print id_, 'question', ques,'变成',question

	if not len(queDesc) and len(question):
		queDesc = question

	# 去除重复的符号而只保留一个
	#question = re.sub(r"。。".decode("utf8"), r"。".decode("utf8"),question)
	#question = re.sub(r"？？".decode("utf8"), r"？".decode("utf8"),question)
	question = special_sign(question)

	wapurl = "https://m.打码.com/question/" + key + ".html"
	url = "https://www.打码.com/question/" + key + ".html"
	#queDesc = re.sub(r"。。".decode("utf8"), r"。".decode("utf8"),queDesc)
	#queDesc = re.sub(r"？？".decode("utf8"), r"？".decode("utf8"),queDesc)
	queDesc = special_sign(queDesc)

	# question和queDesc 为非空字段
	if not queDesc or not question:
		print 'id', id_, '没有title和content字段'
		i += 1
		continue
	
	from_ = "打码"
	showurl = "www.打码.com"

	tags = []
	# 患者信息
	patient = {}
	gender = 0
	sex = cur.get('sex')
	if sex:
		sex = sex.strip()
		if sex == '男':
			gender = 1
		if sex == '女':
			gender = 2
	else:
		gender = 0
	patient['gender'] = gender
	if gender:
		tags.append(sex)

	num = 0
	age = cur.get('age')
	if '岁' in age:
		try:
			num = int(age.replace('岁', ''))
			if num >=1 and num < 3:
				num_ = 3
			if num >=3 and num < 6:
				num_ = 4
			if num >=6 and num < 12:
				num_ = 5
			if num >= 12 and num <20:
				num_ = 6
			if num >= 20 and num < 30:
				num_ = 7
			if num >= 30 and num < 40:
				num_ = 8
			if num >= 40 and num < 50:
				num_ = 9
			if num >= 50 and num < 60:
				num_ = 10
			if num >= 60:
				num_ = 11
		except Exception, e:
			print 'id', id_, 'age字段异常', age
			num_ = 0
	
	if '个月' in age:
		try:
			age_ = age.replace('个月', '').strip()
                        num = int(age_)
			if num == 0:
				num_ = 0
			else:
				num_ = num
                except Exception, e:
                        print 'id', id_, 'age字段异常', age, age_
			num_ = 0

	if num_:
		ageKey = num_
		tags.append(age)
	else:
		ageKey = 0
		#print id_, 'age', age
	patient['ageKey'] = ageKey	
	city = None
	
	patient['city'] = city

	# 答案
	best_answer = None
        if "best_score_subscript" in cur and cur["best_score_subscript"] >= 0:
		sub = cur["best_score_subscript"]
            	best_answer = cur["answer"][sub]
	elif len(cur["answer"]):
		best_answer = cur["answer"][0]
	else:
		best_answer = None
	# answer 为非空字段
        if best_answer is None:
		print 'id', id_, 'no best_score_subscript'
		i += 1
            	continue

	answer = best_answer["answer_bqfx"] + best_answer["answer_zdyj"] + best_answer["answer_summary"] +best_answer["answer_other"]
	answer = dr.sub('', answer)
	answer = answer.replace('\n', '').replace('\t', '').replace('\r', '').strip()
	#answer = re.sub(r"[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+".decode("utf8"), r"\1".decode("utf8"),answer)
	answer = special_sign(answer)

	doc_id = best_answer.get('id')
	doc = None
	if doc_id:
		doc = ask_doctor.find_one({'_id':doc_id})
	if not doc:
		print 'id', id_, 'no doctor or doctor can find by id in ask_doctor'
		i += 1
		continue

	answerMan = {}
	name = doc.get('name')	
	level = doc.get('position')
	hospital = doc.get('hospital')
	hospitalLv = doc.get('hospital_level')
	department = doc.get('department')
	expertDescr = doc.get('excel')
	icon = doc.get('img_name')
	iconUrl = 'https://tcdn.打码.com/newimages/doctor/' + icon

	hospitalLv = hospitalLv.replace(u'医院', u'丙等')
	
	# 以上几项皆不能为空
	if not level or not hospital or not hospitalLv:
		print 'id', id_, 'level', level, 'hospital', hospital, 'hospitalLv',hospitalLv
		i += 1
		continue
	if not department or not expertDescr or not icon:
		print 'id', id_, 'department', department, 'expertDescr', expertDescr, 'icon', icon
		i += 1
		continue
	name = name.replace(u'医生', '')
	re_name = re.compile(u"[\u4e00-\u9fa5]+")
	doctor_group = re_name.search(name, 0)
	if not doctor_group:
            	print 'id', id_, name, 'not doctor name'
               	continue
        doctor = doctor_group.group()
      	if not doctor or len(doctor) <2:
         	print 'id', id_, name, 'doctor name too short'
                continue


	answerMan['name'] = name
	answerMan['level'] = level
	answerMan['hospital'] = hospital
	answerMan['hospitalLv'] = hospitalLv
	answerMan['department'] = department
	answerMan['expertDescr'] = expertDescr
	answerMan['iconUrl'] = iconUrl

	if new.find_one({'_id': id_}):
		label = new.find_one({'_id': id_})
	else:
		ku = id_ % 5
		if ku == 0:
			label = new0.find_one({'_id': id_})
		elif ku == 1:
			label = new1.find_one({'_id': id_})
		elif ku == 2:
			label = new2.find_one({'_id': id_})
		elif ku == 3:
			label = new3.find_one({'_id': id_})
		elif ku == 4:
			label = new4.find_one({'_id': id_})
		else:
			label = None
			print 'id', id_, '库里找不到相关标签'
	if not label:
		print 'id', id_, 'no label'
		diseaseTags = []
	else:
		diseaseTags = label.get('labels',[])
	
	if len(tags) == 2 and diseaseTags and len(diseaseTags) > 0:
		tags.append(diseaseTags[0])
	elif len(tags) == 1 and diseaseTags and len(diseaseTags) > 1:
		tags.append(diseaseTags[0])
		tags.append(diseaseTags[1])
	elif diseaseTags:
		for diseaseTag in diseaseTags:
			tags.append(diseaseTag)
	else:
		pass

	# 患者描述
	#department = cur.get('department', '')
	#catid = int(cur.get('catid',0))
	#if catid >80 and catid != 578:
	#	shortAppeal = [department]
	#else:
	#	shortAppeal = None
	shortAppeal = None	
	patient['shortAppeal'] = shortAppeal

	# 患者资料本身可以置空
	if not shortAppeal and not city and not ageKey and not gender:
		patient_order = {}
	else:
		patient_order = OrderedDict((k,patient[k]) for k in ORDERED_PAT_KEYS)
	
	answerMan_order = OrderedDict((k,answerMan[k]) for k in ORDERED_ANS_KEYS)
	
	date = {}
	date['key'] = key
	date['question'] = question
	date['wapurl'] = wapurl
	date['url'] = url
	date['queDesc'] = queDesc
	date['from'] = from_
	date['showurl'] = showurl
	date['answer'] = answer
	date['tags'] = tags
	date['diseaseTags'] = None
	date['answerMan'] = answerMan_order
	date['patient'] = patient_order

	date_order = OrderedDict((k,date[k]) for k in ORDERED_TOTAL_KEYS)	

	i += 1
	kk += 1
	if kk == 10000:
		f.close()
		num_file += 1
		f = open('json1/'+ base + str(num_file) + '.json', 'w')
		print 'file: json1/'+ base + str(num_file) + '.json'
		kk = 0
	#print 'num', i, num_file
	jdate = json.dumps(date_order, ensure_ascii=False)
	f.write(jdate)
	f.write('\r\n')
	print i, key, '已完成'
		
