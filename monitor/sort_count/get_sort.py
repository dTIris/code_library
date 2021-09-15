# -*- coding:utf-8 -*-
# author:iris
# date:
# desc: 读取每日的日志文件，提取ask和wap_ask的关键词数据
#	提取新访问的id数据

import os
import gzip
import time
import shutil
import urllib
import tarfile
import datetime
import config as CONFIG
from os import path as Path
from pymongo import MongoClient

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# 解压tar文件：20190514.tar.gz
def unzip_data(day):
	print day
	tar = tarfile.open(Path.join(CONFIG.base_dir, day+".tar.gz"))
	names = tar.getnames()
	for name in names:
		if '/ask/' in name:
			print name
			tar.extract(name,path=CONFIG.save_dir)
		elif 'wap_ask/' in name:
			print name
			tar.extract(name,path=CONFIG.save_dir)
		else:
			pass
	tar.close()
	
#解压gz文件：20190514/ask/ask_access05142200.log.gz
def gzipfile(day, name):
	# 读取目录文件，遍历解压
	dir_path = Path.join(CONFIG.save_dir,'{}/{}/'.format(day, name))
	for line in open(Path.join(dir_path,'filelist.txt')):
		path = Path.join(dir_path, line.strip())

		try:
			g = gzip.GzipFile(mode='rb', fileobj=open(path+'.gz', 'rb'))
		except:
			continue
		open(path, 'wb').write(g.read())
		os.remove(path+'.gz')

# 提取关键词数据,并存入数据库中
# 若需要存入文件，需创建keys文件夹于同级目录下
def get_data(day,name):
	start = time.time()
	dir_path = Path.join(CONFIG.save_dir,'{}/{}/'.format(day, name))
	try:
		with open(Path.join(dir_path,'filelist.txt')) as fi:
			file_paths = fi.readlines()
		#f = open(Path.join(CONFIG.filepath, day+name+'.txt'), 'w')
	except Exception, e:
		print day, name, 'error', e
		return ''

	# 遍历name文件下的目录文件，获得文件路径
	for file_path in file_paths:
		path = Path.join(dir_path, file_path.strip())
		print path, time.time()-start, '秒'
		try:
			with open(path, 'rb') as fi:
				lines = fi.readlines()
		except Exception, e:
			print file_path.strip(), 'error', e
			continue
		i = 0
		# 遍历数据文件
		for line in lines:
			line = line.strip()
			if not line:
				continue
			urls = line.split('|')
			if len(urls) < 10:
				print ','.join(urls)
			url = urls[9]
			sub = url.find('keyword')
			if sub > 0:
				key = url[sub+8:]
				end = key.find('&')
				key = key[:end]
				key_ = urllib.unquote(key)
				if key:
					#f.write(str(key_+'\n'))
					CONFIG.keyword_redis_set.incr(key_)
			i += 1
	#f.close()
# 提取关键词数据,并存入数据库中
def get_id(day, name):
        start = time.time()
        dir_path = Path.join(CONFIG.save_dir,'{}/{}/'.format(day, name))
        i = 1
        try:
                with open(Path.join(dir_path,'filelist.txt')) as fi:
                        file_paths = fi.readlines()
        except Exception, e:
                print day, name, 'error', e
                return ''
	# 遍历name文件下的目录文件，获得文件路径
        for file_path in file_paths:
                path = Path.join(dir_path, file_path.strip())
                print path, time.time()-start, '秒'
		try:
                        with open(path, 'rb') as f:
                                lines = f.readlines()
                except Exception, e:
                        print file_path.strip(), 'error', e
                        continue
		# 遍历数据文件
                for line in lines:
                        line = line.strip()
                        if not line:
				continue
                        urls = line.split('|')
                        if 'www.打码.com' not in urls[5]:
                                i += 1
                                continue
                        if '200' != urls[7].strip():
                                i += 1
                                continue
                        url = urls[6]
                        sub = url.find('question')
                        if sub > 0:
                                key = url[sub+9:]
                                end = key.find('.html')
                                key = key[:end]
                                key_ = urllib.unquote(key)
				
				old = CONFIG.oldid_redis_set.get(key_)
				if not old:
					CONFIG.newid_redis_set.incr(key_)
                                i += 1

# 读取数据文件夹，解析后存入数据库中
def read_and_insert_data():
	global today

	#unzip_data(str(today).replace('-', ''))

	# 调用shell脚本，将日志文件复制到此目录下
	code = os.system(Path.join(CONFIG.save_dir, 'move.sh'))
	#print 'code', code
	# 清空数据库
	CONFIG.keyword_redis_set.flushdb()

	# 解压后存入redis中
	gzipfile(str(today).replace('-', ''), 'ask')
	get_data(str(today).replace('-', ''), 'ask')

	CONFIG.newid_redis_set.flushdb() # 清空数据库
	get_id(str(today).replace('-', ''), 'ask')

	gzipfile(str(today).replace('-', ''), 'wap_ask')
	get_data(str(today).replace('-', ''), 'wap_ask')

	# 完成后删除该数据文件夹
	shutil.rmtree(Path.join(CONFIG.save_dir,'{}/'.format(str(today).replace('-', ''))))

def statistics_data():
	hits = 0
	no_hit = 0
	for line in open(CONFIG.hotpath, 'r'):
		line = line.strip()
		if CONFIG.keyword_redis_set.exists(line):
			hits += int(CONFIG.keyword_redis_set.get(line))
		else:
			no_hit +=1
	try:
		save_set.update({'_id':  str(today)}, {'$set': {'hits': hits, 'no_hit': no_hit, 'count': len(CONFIG.keyword_redis_set.keys())}})
		print today, 'hits', hits, 'no_hit', no_hit, 'all_key', len(CONFIG.keyword_redis_set.keys())
	except Exception, e:
		print e


if __name__ == '__main__':

	today = datetime.date.today()
	# 获取前一天的数据，days需和shell脚本的保持一致，不然就报错
	today = today + datetime.timedelta(days = -1)

	save_set = CONFIG.compare_data

	#read_and_insert_data()

	statistics_data()

