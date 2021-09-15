# -*- coding:utf-8 -*-
# auhtor: iris
# date: 2019-06-10
# desc: 爬取成语
import re
import time
import random
import requests
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from pymongo import MongoClient
from fake_useragent import UserAgent

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def spider(url):
	header = {"User-Agent": ua.random}
	try:
		req = requests.get(url, headers=header, timeout=5)
	except requests.RequestException as e:
		print 'Error: ', e
		return 'connent error'

	req.encoding = 'utf-8'
	html = req.text
	if not html:
		return 'spider error'
	return html

def compare(datas):
	data = '：'.join(datas.split('：')[1:])
	value = html_re.sub('', data)

	return value


def parse(html, id_):
	doc = {}
	
	soup = BeautifulSoup(html, 'html.parser')
	#soup = BeautifulSoup(open('4.html', 'r'), 'html.parser')
	explanation = soup.find(text=re.compile(u'【解释】'))
	if explanation:
		print explanation
		value = compare(explanation)
		if value:
			doc['explanation'] = value

	derivation = soup.find(text=re.compile(u'【出自】'))
	if derivation:
		print derivation
		value = compare(derivation)
		if value:
			doc['derivation'] = value

	example = soup.find(text=re.compile(u'【示例】'))
	if example:
		value = compare(example)
		if value:
			doc['example'] = value
	
	same_idioms = soup.find('label', text=re.compile(u'近义词'))
	doc['synonym'] = []
	if same_idioms and same_idioms.get_text():
		for same_idiom in same_idioms.next_siblings:
			if isinstance(same_idiom, NavigableString):
				continue
			datas = same_idiom.find_all('a')
			if datas:
				for data in datas:
					text = data.get_text()
					doc['synonym'].append(text.strip())

	pinyin = soup.find('dt', class_="pinyin")
	if pinyin:
		pinyin_text = pinyin.get_text()
		doc['pinyin'] = pinyin_text.replace(']','').replace('[', '').strip()
		if 'explanation' not in doc:
			for exp in pinyin.next_siblings:
				if isinstance(exp, NavigableString):
					continue
				data = exp.find('p')
				if data:
					text = data.get_text()
					doc['explanation'] = text.strip()
			

	if doc.get('explanation', ''):
		doc['_id'] = id_
		doc['word'] = id_
		doc['synonym'] = '、'.join(doc.get('synonym', ''))

		try:
			idiom_set.insert(doc)
			print 'insert'
		except Exception, e:
			print e
	else:
		print 'no_doc'

def main():
	url = 'https://hanyu.baidu.com/s?wd={}&from=zici'
	for id_ in open('new.txt', 'r'):
		id_ = id_.strip()
		if idiom_set.find_one({'_id': id_.strip()}):
			continue
		html = spider(url.format(id_))
		if html not in ['spider error', 'connent error']:
			print id_, '-:',
			#print html
			parse(html, id_)
		else:
			print cur['_id'], 'cant find'
		time.sleep(random.uniform(0.03,0.1))

if __name__ == '__main__':

	client = MongoClient()
	db = client['imperial_idiom']
	idiom_set = db['idioms']

	ua = UserAgent()

	html_re = re.compile('<[^>]+>')
	main()
	#parse('', '')
