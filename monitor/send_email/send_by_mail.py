# -*- coding:utf-8 -*-
# author: iris
# date: 2019/01/30
# desc: 每天定时获取keyword_sort下的排名文件发送给sam

import os
import smtplib
import datetime
import config as CONFIG
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class MyEmail:
	def __init__(self):
		
		self.user = None
		self.passwd = None
		self.sender = None
		self.to_list = []
		self.cc_list = []
		self.tag = None
		self.text = None
		self.doc = None

	def send(self):
		"""
		send mail
		"""
		try:
			server = smtplib.SMTP_SSL('smtp.exmail.qq.com', port=465)
			server.login(self.user, self.passwd)
			server.sendmail("<%s>" % self.user, self.to_list, self.get_attach())
			server.close()
			print 'send email successful'
		except Exception, e:
			print 'send email failed %s' %e
	
	def get_attach(self):
		"""
		make mail
		"""
		attach = MIMEMultipart()
		#reload(sys)
		#sys.setdefaultencoding('gb18030')
		# 主题
		if self.tag is not None:
			subject = self.tag
			if not isinstance(subject,unicode):
			    	subject = unicode(subject)
			attach["Subject"] = subject
		# 发送人
		if self.user is not None:
			#from_  = "发件人姓名，可以自定义<%s>" % self.user
			from_ = self.sender
			if not isinstance(from_,unicode):
                            	from_ = unicode(from_)
			attach['From'] = from_
		# 收件人-列表
		if self.to_list:
			attach["To"] = ";".join(self.to_list)
		# 抄送-列表
		if self.cc_list:
			attach["Cc"] = ";".join(self.cc_list)
		# 邮件内容
		if self.text is not None:
			text = self.text
			#if not isinstance(text,unicode):
			#	text = unicode(text)
			puretext = MIMEText(text, 'html', 'utf-8')
			attach.attach(puretext)
		# 邮件附件
		if self.doc:
			name = os.path.basename(self.doc).encode('gbk')
			f = open(self.doc, 'rb')
			doc = MIMEText(f.read(), "base64", "gb2312")
			doc["Content-Type"] = 'application/octet-stream'
			doc["Content-Disposition"] = 'attachment; filename="' + name +'"'
			attach.attach(doc)
			f.close()
		return attach.as_string()

def get_text():
	cursor = data.find_one({'_id': str(today)})
	cursor2 = data.find_one({'_id': str(yesterday)})
	cursor3 = data.find_one({'_id': str(yesterday + datetime.timedelta(days = -1))})
	
	mytext = '<html>'
	mytext += '<div>'
	if cursor and cursor2:
		if cursor3:
			mytext += str(today) + 'and' + str(yesterday) + ' 排名统计结果,'
			mytext += '总计：'+str(cursor.get('sum', 0))+'<br/>'
			#mytext += '第1个排名+的个数：<font color="#EE0000"><b>↑</b></font>'+str(cursor.get('add0'))+','
			mytext += '第1个排名+的个数：'+str(cursor.get('add0', 0))+','
			#mytext += '第2个排名+的个数：<font color="#EE0000"><b>↑</b></font>'+str(cursor.get('add1'))+'<br/>'
			mytext += '第2个排名+的个数：'+str(cursor.get('add1', 0))+'<br/>'
			#mytext += '第1个排名-的个数：<font color="#66CD00"><b>↓</b></font>'+str(cursor.get('miuns0'))+','
			mytext += '第1个排名-的个数：'+str(cursor.get('miuns0', 0))+','
			#mytext += '第2个排名-的个数：<font color="#66CD00"><b>↓</b></font>'+str(cursor.get('miuns1'))+'<br/>'
			mytext += '第2个排名-的个数：'+str(cursor.get('miuns1', 0))+'<br/>'
			mytext += '第1个排名0的个数：'+ str(cursor.get('same0', 0))+','
			mytext += '第2个排名0的个数：'+ str(cursor.get('same1', 0))+'<br/>'
			mytext += '<br/>'
			
			# 对比
			mytext += '排名对比结果<br/>'
			#mytext += '    '
			mytext += '今天<br/>'
			rate_1 = float(cursor.get('add0')-cursor.get('miuns0'))/cursor.get('add0')
			if rate_1 > 0:
				rate_1 *= 100
				rate_1 = round(rate_1, 2)
				mytext += '第1个排名+的个数同比排名-的个数上涨：'+str(rate_1)+'%<font color="#EE0000"><b>↑</b></font><br/>'
			else:
				rate_1 *= -100
				rate_1 = round(rate_1, 2)
				mytext += '第1个排名+的个数同比排名-的个数下降：'+str(rate_1)+'%<font color="#66CD00"><b>↓</b></font><br/>'

			rate_2 = float(cursor.get('add1')-cursor.get('miuns1'))/cursor.get('add1')
			if rate_2 > 0:
				rate_2 *= 100
				rate_2 = round(rate_2, 2)
				mytext += '第2个排名+的个数同比排名-的个数上涨：'+str(rate_2)+'%<font color="#EE0000"><b>↑</b></font><br/>'
			else:
				rate_2 *= -100
				rate_2 = round(rate_2, 2)
				mytext += '第2个排名+的个数同比排名-的个数下降：'+str(rate_2)+'%<font color="#66CD00"><b>↓</b></font><br/>'


			"""
			mytext += '昨天<br/>'
			rate_1 = 0
			rate_1 = float(cursor2.get('add0')-cursor2.get('miuns0'))/cursor2.get('add0')
                        if rate_1 > 0:
                                rate_1 *= 100
                                rate_1 = round(rate_1, 2)
                                mytext += '第1个排名+的个数同比排名-的个数上涨：'+str(rate_1)+'%<font color="#EE0000"><b>↑</b></font><br/>'
                        else:
                                rate_1 *= -100
                                rate_1 = round(rate_1, 2)
                                mytext += '第1个排名+的个数同比排名-的个数下降：'+str(rate_1)+'%<font color="#EE0000"><b>↑</b></font><br/>'

			rate_2 = 0
                        rate_2 = float(cursor2.get('add1')-cursor2.get('miuns1'))/cursor2.get('add1')
                        if rate_2 > 0:
                                rate_2 *= 100
                                rate_2 = round(rate_2, 2)
                                mytext += '第2个排名+的个数同比排名-的个数上涨：'+str(rate_2)+'%<font color="#EE0000"><b>↑</b></font><br/>'
                        else:
                                rate_2 *= -100
                                rate_2 = round(rate_2, 2)
                                mytext += '第2个排名+的个数同比排名-的个数下降：'+str(rate_2)+'%<font color="#EE0000"><b>↑</b></font><br/>'

			mytext += '前天<br/>'
                        rate_1 = 0
                        rate_1 = float(cursor3.get('add0')-cursor3.get('miuns0'))/cursor3.get('add0')
                        if rate_1 > 0:
                                rate_1 *= 100
                                rate_1 = round(rate_1, 2)
                                mytext += '第1个排名+的个数同比排名-的个数上涨：'+str(rate_1)+'%<font color="#EE0000"><b>↑</b></font><br/>'
                        else:
                                rate_1 *= -100
                                rate_1 = round(rate_1, 2)
                                mytext += '第1个排名+的个数同比排名-的个数下降：'+str(rate_1)+'%<font color="#EE0000"><b>↑</b></font><br/>'

                        rate_2 = 0
                        rate_2 = float(cursor3.get('add1')-cursor3.get('miuns1'))/cursor3.get('add1')
                        if rate_2 > 0:
                                rate_2 *= 100
                                rate_2 = round(rate_2, 2)
                                mytext += '第2个排名+的个数同比排名-的个数上涨：'+str(rate_2)+'%<font color="#EE0000"><b>↑</b></font><br/>'
                        else:
                                rate_2 *= -100
                                rate_2 = round(rate_2, 2)
                                mytext += '第2个排名+的个数同比排名-的个数下降：'+str(rate_2)+'%<font color="#EE0000"><b>↑</b></font><br/>'

			rate_add = float(cursor.get('add0')-cursor2.get('add0'))/cursor2.get('add0')
			if rate_add > 0:
				rate_add *= 100
				rate_add = round(rate_add, 2)
				mytext += '第1个排名+的个数同比昨日上涨：'+str(rate_add)+'%<font color="#EE0000"><b>↑</b></font><br/>'
			else:
				rate_add *= -100
				rate_add = round(rate_add, 2)
				mytext += '第1个排名+的个数同比昨日下降：'+str(rate_add)+'%<font color="#66CD00"><b>↓</b></font><br/>'

			#mytext += '    '
			rate_add2 = float(cursor.get('add1')-cursor2.get('add1'))/cursor2.get('add1')
                        if rate_add2 > 0:
                                rate_add2 *= 100
				rate_add2 = round(rate_add2, 2)
                                mytext += '第2个排名+的个数同比昨日上涨：'+str(rate_add2)+'%<font color="#EE0000"><b>↑</b></font><br/>'
                        else:
                                rate_add2 *= -100
				rate_add2 = round(rate_add2, 2)
                                mytext += '第2个排名+的个数同比昨日下降：'+str(rate_add2)+'%<font color="#66CD00"><b>↓</b></font><br/>'

			#mytext += '    '
			rate_miuns = float(cursor.get('miuns0')-cursor2.get('miuns0'))/cursor2.get('miuns0')
                        if rate_miuns > 0:
                                rate_miuns *= 100
				rate_miuns = round(rate_miuns, 2)
                                mytext += '第1个排名-的个数同比昨日上涨：'+str(rate_miuns)+'%<font color="#EE0000"><b>↑</b></font><br/>'
                        else:
                                rate_miuns *= -100
				rate_miuns = round(rate_miuns, 2)
                                mytext += '第1个排名-的个数同比昨日下降：'+str(rate_miuns)+'%<font color="#66CD00"><b>↓</b></font><br/>'

			#mytext += '    '
                        rate_miuns2 = float(cursor.get('miuns1')-cursor2.get('miuns1'))/cursor2.get('miuns1')
                        if rate_miuns2 > 0:
                                rate_miuns2 *= 100
				rate_miuns2 = round(rate_miuns2, 2)
                                mytext += '第2个排名-的个数同比昨日上涨：'+str(rate_miuns2)+'%<font color="#EE0000"><b>↑</b></font><br/>'
                        else:
                                rate_miuns2 *= -100
				rate_miuns2 = round(rate_miuns2, 2)
                                mytext += '第2个排名-的个数同比昨日下降：'+str(rate_miuns2)+'%<font color="#66CD00"><b>↓</b></font><br/>'

			#mytext += '    '
			rate_same = float(cursor.get('same0')-cursor2.get('same0'))/cursor2.get('same0')
                        if rate_same > 0:
                                rate_same *= 100
				rate_same = round(rate_same, 2)
                                mytext += '第1个排名0的个数同比昨日上涨：'+str(rate_same)+'%<font color="#EE0000"><b>↑</b></font><br/>'
                        else:
                                rate_same *= -100
				rate_same = round(rate_same, 2)
                                mytext += '第1个排名0的个数同比昨日下降：'+str(rate_same)+'%<font color="#66CD00"><b>↓</b></font><br/>'

			#mytext += '    '
                        rate_same2 = float(cursor.get('same1')-cursor2.get('same1'))/cursor2.get('same1')
                        if rate_same2 > 0:
                                rate_same2 *= 100
				rate_same2 = round(rate_same2, 2)
                                mytext += '第2个排名0的个数同比昨日上涨：'+str(rate_same2)+'%<font color="#EE0000"><b>↑</b></font><br/>'
                        else:
                                rate_same2 *= -100
				rate_same2 = round(rate_same2, 2)
                                mytext += '第2个排名0的个数同比昨日下降：'+str(rate_same2)+'%<font color="#66CD00"><b>↓</b></font><br/>'
			"""
			mytext += '<br/>'

			# 流量关键词对比结果
			mytext += str(yesterday) + 'and' + str(yesterday + datetime.timedelta(days = -1)) + ' 点击量统计结果:<br/>'
			#mytext += '    '
			mytext += str(yesterday) + '流量关键词个数：' + str(cursor2.get('count')) + '<br/>'
			#mytext += '    '
			mytext += str(yesterday + datetime.timedelta(days = -1)) + '流量关键词个数：' + str(cursor3.get('count')) + '<br/>'
			#mytext += '        '
			count_rate = float(cursor2.get('count') - cursor3.get('count')) / cursor2.get('count')
			if count_rate > 0:
				count_rate *= 100
				count_rate = round(count_rate, 2)
				mytext += '同比昨日上涨' + str(count_rate) + '%<font color="#EE0000"><b>↑</b></font><br/>'
			else:
				count_rate *= -100
				count_rate = round(count_rate, 2)
				mytext += '同比昨日下降' + str(count_rate) + '%<font color="#66CD00"><b>↓</b></font><br/>'

			mytext += '<br/>'
			#mytext += '    '
			mytext += str(yesterday) + '热门词点击量总和：' + str(cursor2.get('hits')) + '<br/>'
			#mytext += '    '
			mytext += str(yesterday + datetime.timedelta(days = -1)) + '热门词点击量总和：' + str(cursor3.get('hits')) + '<br/>'
			#mytext += '        '
			hits_rate = float(cursor2.get('hits') - cursor3.get('hits')) / cursor2.get('hits')
			if hits_rate > 0:
				hits_rate *= 100
				hits_rate = round(hits_rate, 2)
				mytext += '同比昨日上涨' + str(hits_rate) + '%<font color="#EE0000"><b>↑</b></font><br/>'
			else:
				hits_rate *= -100
				hits_rate = round(hits_rate, 2)
				mytext += '同比昨日下降' + str(hits_rate) + '%<font color="#66CD00"><b>↓</b></font><br/>'

			mytext += '<br/>'
			#mytext += '    '
			mytext += str(yesterday) + '热门词无点击量的个数总和：' + str(cursor2.get('no_hit')) + '<br/>'
			#mytext += '    '
			mytext += str(yesterday + datetime.timedelta(days = -1)) + '热门词无点击量的个数总和：' + str(cursor3.get('no_hit')) + '<br/>'
			#mytext += '        '
			no_rate = float(cursor2.get('no_hit') - cursor3.get('no_hit')) / cursor2.get('no_hit')
			if no_rate > 0:
				no_rate *= 100
				no_rate = round(no_rate, 2)
				mytext += '同比昨日上涨' + str(no_rate) + '%<font color="#EE0000"><b>↑</b></font><br/>'
			else:
				no_rate *= -100
				no_rate = round(no_rate, 2)
				mytext += '同比昨日下降' + str(no_rate) + '%<font color="#66CD00"><b>↓</b></font><br/>'
	mytext += '</div>'
	mytext += '</html><br/>'
	return mytext

if __name__ == '__main__':
	today = datetime.date.today()
	today = today + datetime.timedelta(days = -1)
	yesterday = today + datetime.timedelta(days = -1)

	data = CONFIG.hot_wap2019['compare_data']

	print today
	my = MyEmail()

	my.user = "Iris@打码.com"
	my.passwd = ""
	my.sender = "关键词排名监控系统"
	my.to_list = CONFIG.send_list
	my.cc_list = ["", ]
	my.tag = "关键词监控排名" + str(today)
	my.text = get_text()
	my.doc = CONFIG.file_dir + str(today) + u'监控排名.xls'
	my.send()
	print "send to ", ''.join((my.to_list))
