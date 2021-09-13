# -*- coding:utf-8 -*-
# python：2
# author：Iris
# desc：将用户数据以表格形式发送邮件

import os
import xlwt
import time
import MySQLdb
import smtplib
import datetime
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import config as CONFIG

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class MyEmail:
	def __init__(self):
		self.user = None
		self.passwd = None
		self.sender = None
		self.to_list = []
		self.cc_list = []
		self.tag = None
		#self.text = None
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
		'''
		# 邮件内容
		if self.text is not None:
				text = self.text
				#if not isinstance(text,unicode):
				#       text = unicode(text)
				puretext = MIMEText(text, 'html', 'utf-8')
				attach.attach(puretext)
		'''
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


def get_data(agent_):
	if agent_ == '':
		filename = (CONFIG.filepath+str(yesterday).replace('-', '')+CONFIG.xls_filename)
	else:
		filename = (CONFIG.filepath+str(yesterday).replace('-', '')+agent_+CONFIG.xls_filename_all)
        wb = xlwt.Workbook(encoding='utf8')
        sheet = wb.add_sheet('sheet1', cell_overwrite_ok=False)
	
	sheet.col(0).width = 256 * 13
	sheet.col(1).width = 256 * 28
	sheet.col(2).width = 256 * 23

	titles = CONFIG.titles

	i = 0
	for title in titles:
		sheet.write(0, i, title)
		i += 1
        datas = []
	sql = ''
	if agent_ == '':
		sql = "SELECT * FROM adyygroup WHERE status > '0' and end_time >= (SELECT DATE_ADD(now(), INTERVAL -1 MONTH));"
	else:
		sql = "SELECT * FROM adyygroup WHERE status > '0' and agent='%s'" % agent_
	try:
		cursor.execute(sql)
		results = cursor.fetchall()
	except Exception ,e:
		print "Error:{}".format(e)
		return str(e)
	sql = ''
	
	rows = 0
	for result in results:
		data = []
		id_ = result[0]
		name = result[1]
		#agent = result[2]
		#agent_email = result[3]
		status = result[4]
		end_time = result[5]

		# 判定条件
		end_time_ = end_time.date()
		if end_time_ == '0000-00-00':
			print 'Error', datas[row][1], datas[row][2]
			continue

		#新增倒计时
		remain_time = result[6]
		if status !=2:
			delta = int((end_time_ - yesterday).days)
			end_time = str(end_time)
		else:
			delta = int(remain_time / 3600 / 24)
			end_time = "暂停"

		sql_ = "SELECT * FROM yygroupday WHERE group_id = {} and inputtime = '{}'".format(id_, yesterday)
		#print sql_
		cursor.execute(sql_)
		results_ = cursor.fetchall()
		if len(results_) == 1:
			result_ = results_[0]
			showpv = result_[2]
			clickpv = result_[3]
			clickip = result_[4]
			clickuv = result_[5]
			inputtime = result_[6]
			
			data.append(str(inputtime))
			data.append(name)
			#data.append(agent)
			data.append(end_time)
			data.append(delta)
			#data.append(showpv)
			data.append(clickpv)
			pv_rate = float(clickpv)/showpv
			pv_rate = round(pv_rate, 4)
			pv_rate *= 100
			data.append(str(pv_rate)+'%')
			data.append(clickip)
			ip_rate = float(clickip)/showpv
			ip_rate = round(ip_rate, 4)
			ip_rate *= 100
			data.append(str(ip_rate) +'%')
			data.append(clickuv)
			datas.append(data)
		else:
			data.append(str(yesterday))
			data.append(name)
			data.append(end_time)
			data.append(delta)
			data.append(0)
			data.append(0)
			data.append(0)
			data.append(0)
			data.append(0)
			datas.append(data)

		rows += 1
	
        try:
			datas.sort(key=lambda x:(x[3]))
			#datas.reverse()
        except Exception, e:
			print e

	datas.insert(0, [])
	row_count = len(datas)
	for row in range(1, row_count):
	del_time = datas[row][3]

	col_count = len(datas[row])
	for col in range(0, col_count):
		if del_time < 7:
			sheet.write(row, col, datas[row][col], style)
		else:
			sheet.write(row, col, datas[row][col])
	
	wb.save(filename)
	print filename
	del wb
	return filename

if __name__ == '__main__':

	connect = MySQLdb.connect(host=CONFIG.host,user="iris",passwd=CONFIG.db_password,port=CONFIG.port, db=CONFIG.test_db, charset='utf8')

	cursor = connect.cursor()

	today = datetime.date.today()
	#today = today + datetime.timedelta(days = -8)
	yesterday = today + datetime.timedelta(days = -1)

	print today
	style = xlwt.XFStyle()
	font = xlwt.Font()
	font.name = u'微软雅黑'
	font.colour_index = 2
	font.bold = True
	style.font = font
	sql = ''
	#sql = "select agent from adyygroup where agent<>''"
	#cursor.execute(sql)
	names = set()
	#for result in cursor.fetchall():
	#        names.add(result[0])
	names.add('')
	for name in names:
		filename = get_data(name)
		if name in filename:
			if name:
				continue
			else:
				email = CONFIG.myemail
				email += ';'+CONFIG.Toemail
			my = MyEmail()
			my.user = CONFIG.myemail
			my.passwd = CONFIG.mypasswd
			my.sender = CONFIG.mysender
			my.to_list = email.split(';')
			my.tag = filename.split('/')[-1].replace('广告', '')
			my.doc = filename
			my.send()
			print "Already send to", ''.join(email)
		else:
			print filename

