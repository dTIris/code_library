# -*- coding:utf-8 -*-
# author:iris
# date:2019/06/26
# desc: 随机生成昵称和图片存入数据库，根据要求给出随机数值的数组

import pandas
import random
from pymongo import MongoClient


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def get():
	excel_data = pandas.read_excel('./name.xlsx')

	datas = excel_data.to_dict(orient="records")

	for data in datas:
		if not data.get(u'昵称', ''):
			continue
		print data.get(u'昵称', '')
def main():
	i = 1
	base = 'i{}.png'
	for line in open('name.txt'):
		try:
			save_set.insert({'_id': i, 'name': line.strip(), 'img': base.format(random.randint(9200,10001))})
		except Exception, e:
			print e
			break
		i += 1

def score():
	def random_index(rate):#{{{
		start = 0
		randnum = random.randint(1, sum(rate))
		for index, scope in enumerate(rate):
			start += scope
			if randnum <= start:
				break
		return index
#}}}

	# 确定总分数#{{{
	rate = [3,5,2]
	score_rate = random_index(rate)
	if score_rate == 0:
		score_max = random.randint(5,10)
	elif score_rate == 1:
		score_max = random.randint(10,15)
	else:
		score_max = random.randint(15,25)
	print 'score_max', score_max*20
#}}}

	# 先确定最后一个end end_second#{{{
	end_value =[i for i in range(5, score_max+1 if score_max <= 10 else 11)]
	if score_max <= 20:
		end_value.append(0)
	end = random.choice(end_value)
	score_max -= end
	if end in [6,7,8,9,10]:
		end_second = 11 - end
	elif end == 0:
		end_second = random.randint(1,9)
	else:
		end_second = random.randint(6,9)

	#print 'end', end_second, 'score', end#}}}

	# 初始化其他四个#{{{
	#'''
	temp = 0
	scores = [0]*4
	max_ = 5 if score_max - temp >= 5 else score_max - temp
	if score_max:
		for i in range(4):
			score = random.randint(0, max_)
			temp += score
			scores[i] = score
			if temp >= score_max:
				break
			max_ = 5 if score_max - temp >= 5 else score_max - temp
	#print '可选值', scores
	#'''#}}}

	# 补足分数#{{{
	diff = 0
	if sum(scores) < score_max:
		diff = score_max-sum(scores)
		while diff>0:
			for i in range(4):
				if diff == 0:
					break
				elif scores[i] == 5:
					continue
				elif diff + scores[i]>5:
					max_ = 5-scores[i]
				else:
					max_ = diff
				add = random.randint(1, max_)
				scores[i] += add
				diff -= add
	#if diff:			
	#	print '调整后', scores
#}}}

	# 乱序#{{{
	#random.shuffle(scores)
	#print '乱序后', scores

	#scores.append(end)
	#print '加上末尾', scores
#}}}

	# 给出最终数组#{{{
	datas = []
	for score in scores:
		if score == 1:
			datas.append([random.randint(5,9), score*20])
		elif score == 0:
			datas.append([random.randint(1,9), score*20])
		else:
			datas.append([6-score, score*20])
	datas.append([end_second, end*20])

	for data in datas:
		print data
#}}}

	return datas

if __name__ == '__main__':
	client = MongoClient('10.5.0.10', 38000)
	db = client['test_games']
	save_set = db['idiom_ai']

	score()
