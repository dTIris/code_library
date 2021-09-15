# -*- coding:utf-8 -*-
# author: iris
# date: 2019/01/30
# desc: 统计今天关键词m和wap域名下的监控数据排名并与昨天的做对比
# 	做成xls表格文件存放于keyword_sort下

import xlwt
import time
import datetime
import config as CONFIG

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def compare_data(cur):
	global count
	global datas
	data = []
	keyword = cur['_id']
	#print keyword, '\t',
	data.append(keyword)
	# wap域名
	rankings = cur.get('rankings', {})

	# m域名的点击统计	
	m_cur = mtoday_set.find_one({'_id': keyword})
	if m_cur:
		mrankings = m_cur.get('rankings', {})
	else:
		mrankings = {}
	
	# 前一天的数据对比
	# wap域名下
	cursor = yesterday_set.find_one({'_id': keyword})
	if cursor:
		old_rankings = cursor.get('rankings', {})
	else:
		old_rankings = {}

	# m域名
	mcursor = myesterday_set.find_one({'_id': keyword})
	if mcursor:
		old_mrankings = mcursor.get('rankings', {})
	else:
		old_mrankings = {}

	# 合并wap和m的排名并排序--yesterday
	old = []
	for rank in old_rankings:
		rank = int(rank)
		if rank not in old:
			old.append(rank)
	for rank in old_mrankings:
		rank = int(rank)
		if rank not in old:
			old.append(rank)
	old.sort()

	# 若有多个，则只取出前两个
	old_dict = {}
	if old:
		sub_all = ''
		i = 0
		for sub in old:
			if i > 1:
				break
			sub_all += (str(sub) + '、')
			#print str(sub), type(sub), '、',
			old_dict[i] = sub
			i += 1
		#print sub_all,
                data.append(sub_all)
	else:
                #print '无排名',
		data.append('无排名')
	#print '\t',

	# 合并wap和m的排名并排序--today
	new = []
	for rank in rankings:
		rank = int(rank)
		if rank not in new:
			new.append(rank)
	for rank in mrankings:
		rank = int(rank)
		if rank not in new:
			new.append(rank)
	new.sort()

	# 若有多个，则只取出前两个
	new_dict = {}
	if new:
		sub_all = ''
		i = 0
		for sub in new:
			if i > 1:
				break
			sub_all += (str(sub) + '、')
			#print str(sub), type(sub), '、',
			new_dict[i] = sub
			i += 1
		#print sub_all,
		data.append(sub_all)
	else:
		#print '无排名',
		data.append('无排名')
	#print '\t',

	# 对比
	sub_num = ''
	for i in range(2):
		new_sub = new_dict.get(i, 0)
		
		old_sub = old_dict.get(i, 0)

		if new_sub and old_sub:
			num = old_sub - new_sub
		elif new_sub and not old_sub:
			num = 21 - new_sub
		elif not new_sub and old_sub:
			num = old_sub - 21
		else:
			num = 0
		#num = old_sub - new_sub
		if num > 0:
			if count.get('add'+str(i)):
				count['add'+str(i)] += 1
			else:
				count['add'+str(i)] = 1
		elif num < 0:
			if count.get('minus'+str(i)):
				count['minus'+str(i)] += 1
			else:
				count['minus'+str(i)] = 1
		else:
			if count.get('same'+str(i)):
				count['same'+str(i)] += 1
			else:
				count['same'+str(i)] = 1
		sub_num += str(num) + '、'
		#print old_sub, '-', new_sub, str(num) + '、',
	#print sub_num
	data.append(sub_num)
	datas.append(data)

def write_in_sheet():
	global datas
	
	try:
		datas.sort(key=lambda x:(int(x[3].split('、')[0])+int(x[3].split('、')[1])))
	except Exception, e:
		print e

	datas.insert(0, [])
	row_count = len(datas)
	for row in range(1, row_count):
    		col_count = len(datas[row])
    		for col in range(0, col_count):
			sheet.write(row, col, datas[row][col])

if __name__ == '__main__':
	db = CONFIG.hot_wap2019
	db_m = CONFIG.hot_m2019
	
	today = datetime.date.today()
	#today = today + datetime.timedelta(days = -1)
        yesterday = today + datetime.timedelta(days = -1)

	today_set = db[str(today).replace('-', '')]
	yesterday_set = db[str(yesterday).replace('-', '')]
	mtoday_set = db_m[str(today).replace('-', '')]
	myesterday_set = db_m[str(yesterday).replace('-', '')]

	count = {}
	filename = (CONFIG.file_dir+str(today)+u'监控排名.xls')
	wb = xlwt.Workbook(encoding='utf8')
	sheet = wb.add_sheet('sheet1', cell_overwrite_ok=False)
	
	datas = []

	print today, 'and', yesterday
	print '关键词\t' + str(yesterday) + '排名\t' + str(today) + '排名\t对比'
	title = ['关键词', str(yesterday) + '排名', str(today) + '排名', '对比']
	#datas.append(title)
	sheet.write(0, 0, title[0])
	sheet.write(0, 1, title[1])
	sheet.write(0, 2, title[2])
	sheet.write(0, 3, title[3])
	sum_ = 0
	#for cur in today_set.find().limit(10):
	#for cur in today_set.find():
	for line in open(CONFIG.hot_path):
		cur = today_set.find_one({'_id': line.strip()})
		if not cur:
			continue
		compare_data(cur)
		sum_ += 1
	write_in_sheet()

	# 将统计结果存入数据库中
	save_set = db['compare_data']
	doc = {'_id': str(today)}
	doc['sum'] = sum_
	doc['add0'] = count.get('add0')
	doc['add1'] = count.get('add1')
	doc['miuns0'] = count.get('minus0')
	doc['miuns1'] = count.get('minus1')
	doc['same0'] = count.get('same0')
	doc['same1'] = count.get('same1')
	
	try:
		save_set.insert(doc)
	except Exception, e:
		save_set.update({'_id': str(today)}, {'$set': {
				'sum': sum_, 'add0': count.get('add0'),
				 'add1': count.get('add1'), 
				'miuns0': count.get('minus0'), 
				'miuns1': count.get('minus1'),
				'same0': count.get('same0'), 
				'same1': count.get('same1')}
				}
			)
		print e
	
	print '总计：', sum_,
	#sheet.write(sum_+3, 0, '总计：' + str(sum_))

	print '\t第1个排名+的个数：↑', count.get('add0'),
	#sheet.write(sum_+3, 1, '第1个排名+的个数：↑'+str(count.get('add0')))

	print '\t第2个排名+的个数：↑', count.get('add1')
	#sheet.write(sum_+3, 2, '第2个排名+的个数：↑'+str(count.get('add1')))

	print ' \t第1个排名-的个数：↓', count.get('minus0'),
	#sheet.write(sum_+4, 1, '第1个排名-的个数：↓'+str(count.get('minus0')))

	print '\t第2个排名-的个数：↓', count.get('minus1')
	#sheet.write(sum_+4, 2, '第2个排名-的个数：↓'+str(count.get('minus1')))

	print ' \t第1个排名0的个数：', count.get('same0'),
	#sheet.write(sum_+5, 1, '第1个排名0的个数：'+ str(count.get('same0')))

	print '\t第2个排名0的个数：', count.get('same1')
	#sheet.write(sum_+5, 2, '第2个排名0的个数：'+ str(count.get('same1')))

	wb.save(filename)

