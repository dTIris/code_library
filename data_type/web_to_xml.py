# -*- coding:utf-8 -*-
# author:iris
# 网站地图服务：接收id后写入xml文件中

import tornado.ioloop
import tornado.web
import tornado.httpserver

import time
from pymongo import MongoClient

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

client_ = MongoClient()
db_ = client_['iris_test']
sitemap = db_['sitemap']

sitemap_file = 'txt/sitemapline.txt'
base = 'site/sitemap_ask_'
base_ = 'site/sitemap_mask_'
sitemap_ask = 'site/sitemap_ask.xml'
sitemap_mask = 'site/sitemap_mask.xml'

# 读出sitemapline中的参数，存储着程序结束前最后一个文件最后一行
with open(sitemap_file, 'r+') as fid:
   	line_str = fid.readline()
	if line_str:
		line = int(line_str.split(':')[1])
		filenum = int(line_str.split(':')[0])
	else:
		line = 0
		filenum = 1134

#times = time.strftime('%Y-%m-%d',time.localtime(time.time()))
times = '2018-08-13'

firststring = '<?xml version="1.0" encoding="UTF-8"?>\n'
firststring += '<urlset xmlns="https://www.打码.org/schemas/sitemap/0.9">\n'
firststring+="""    <url>\n"""
firststring+="""        <loc>https://www.打码.com/</loc>\n"""
firststring+="""        <lastmod>"""
firststring+=times
firststring+="""</lastmod>\n"""
firststring+="""        <changefreq>always</changefreq>\n"""
firststring+="""        <priority>1.0</priority>\n"""
firststring+="""    </url>\n"""
firststring+="""</urlset>"""

firststring_ = '<?xml version="1.0" encoding="UTF-8"?>\n'
firststring_+= '<urlset xmlns="https://www.打码.org/schemas/sitemap/0.9"\n'
firststring_+="""        xmlns:mobile="http://m.baidu.com/schemas/sitemap-mobile/1/"> \n"""
firststring_+="""    <url>\n"""
firststring_+="""        <loc>https://m.打码.com/</loc>\n"""
firststring_+="""        <mobile:mobile type="mobile"/>\n"""
firststring_+="""        <lastmod>"""
firststring_+=times
firststring_+="""</lastmod>\n"""
firststring_+="""        <changefreq>always</changefreq>\n"""
firststring_+="""        <priority>1.0</priority>\n"""
firststring_+="""    </url>\n"""
firststring_+="""</urlset>"""

class TestHandler(tornado.web.RequestHandler):
        def get(self):
                self.write('hello iris')

class MainHandler(tornado.web.RequestHandler):
        def get(self, askid):
		id_ = str(askid)
		global line
     		global firststring
     		global firststring_
		global times
		global filenum

		repeat = sitemap.find_one({'_id':id_})
		if repeat:
			print id_, 'repeat'
			result = {'status':2, 'msg':'the id is repeat, ' + str(repeat)}
                        self.write(result)
		else:
			url_1 = 'https://www.打码.com/question/'
	                url_2 = '.html'
	                url = '%s%s%s'%(url_1,id_,url_2)
			mystring = ''
			mystring+="""    <url>\n"""
	                mystring+="""        <loc>"""
	                mystring+=url
	                mystring+="""</loc>\n"""
	                mystring+="""        <lastmod>"""
	               	mystring+=times
	                mystring+="""</lastmod>\n"""
	               	mystring+="""        <changefreq>always</changefreq>\n"""
	                mystring+="""        <priority>0.8</priority>\n"""
	                mystring+="""    </url>\n"""
			
			mystring_ = ''
			mystring_+="""    <url>\n"""
                        mystring_+="""        <loc>"""
                        mystring_+=url
                        mystring_+="""</loc>\n"""
                        mystring_+="""        <mobile:mobile type="mobile"/>\n"""
                        mystring_+="""        <lastmod>"""
                        mystring_+=times
                        mystring_+="""</lastmod>\n"""
                        mystring_+="""        <changefreq>always</changefreq>\n"""
                        mystring_+="""        <priority>0.8</priority>\n"""
                        mystring_+="""    </url>\n"""

	                file_name = base+str(filenum)+'.xml'
                        file_name_ = base_+str(filenum)+'.xml'
			#当写入的id达到设定值时，换新的文件		
			#if line == 40000:
			if line == 4:
				line = 0
				filenum += 1
		                file_name = base+str(filenum)+'.xml'
                                file_name_ = base_+str(filenum)+'.xml'

			if line == 0:
				askstring = '''    <sitemap>\n        <loc>'''
                                askstring+=file_name
                                askstring+='''</loc>\n'''
                                askstring+='''        <lastmod>'''
                                askstring+=times
                                askstring+='''</lastmod>\n    </sitemap>\n'''

                                askstring_ = '''    <sitemap>\n        <loc>'''
                                askstring_+=file_name_
                                askstring_+='''</loc>\n'''
                                askstring_+='''        <lastmod>'''
                                askstring_+=times
                                askstring_+='''</lastmod>\n    </sitemap>a\n'''

                               	with open(sitemap_ask,"r+") as ask:
                                        lines = ask.readlines()
                                        length = len(lines)
                                with open(sitemap_mask,"r+") as mask:
                                        lines_ = mask.readlines()
                                        length_ = len(lines_)

                                with open(sitemap_ask,"w+") as ask:
                                        lines.insert(length-1,askstring)
                                        for linea in lines:
                                                ask.write(linea)
                                with open(sitemap_mask,"w+") as mask:
                                        lines_.insert(length-1,askstring_)
                                        for line_ in lines_:
                                                mask.write(line_)

				f1 = open(file_name,"w+")
				f1.write(firststring)
				f1.close()

				f2 = open(file_name_,"w+")
                                f2.write(firststring_)
                                f2.close()
                                print file_name, file_name_, 'firststring'
			try:
				with open(file_name,"r+") as f1_r:
                                        lines1 = f1_r.readlines()
                                        length1 = len(lines1)
                                with open(file_name_,"r+") as f2_r:
                                        lines2 = f2_r.readlines()
                                        length2 = len(lines2)
                                        
	                        with open(file_name,"w") as f1:
		                    	lines1.insert(length1-1,mystring)
                                        for line1 in lines1:
                                                f1.write(line1)
				with open(file_name_,"w") as f2:
                                        lines2.insert(length2-1,mystring_)
                                        for line2 in lines2:
                                                f2.write(line2)

					print file_name, file_name_, 'line'
	                        line += 1
				sitemap.insert({'_id':id_,'filenum':filenum})
				result = {'status':0, 'msg':'success'}
				with open(sitemap_file, 'w+') as fid:
					fid.write(str(filenum) + ':' + str(line))
				self.write(result)
	               	except Exception, e:
	                        print 'error', e
				result = {'status':1, 'msg':str(e)}        
				self.write(result)
		
			

application = tornado.web.Application([
        (r'/index', TestHandler),
        (r"/ask/(?P<askid>\w*)", MainHandler),
])

if __name__ == "__main__":
        #application.listen(8181)
        http_server = tornado.httpserver.HTTPServer(application)
        #print 'come on'
        http_server.listen(8100)
        tornado.ioloop.IOLoop.instance().start()

