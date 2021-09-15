# -*-coding:utf-8 -*-
# author:iris
# date:2018/11/14
# desc:根据新数据生成相关-1

import tornado.ioloop
import tornado.web
import tornado.httpserver
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
import config as CONFIG
import callbacks.analyse_ask as ANALYSE_ASK
import callbacks.analyse_new as ANALYSE_NEW


from elasticsearch import Elasticsearch
import redis
import jieba
import json


class BaseHandler(tornado.web.RequestHandler):
        executor = ThreadPoolExecutor(32)

class AskHandler(BaseHandler):
        @run_on_executor
        def post(self):
		try:
			param = {}
                        params = json.loads(self.request.body)
                        param["id"] = params.get('id_', "")
                except Exception, e:
                        param = None
			print params,e
			self.finish({})
			#return self.redirect('/')
			return ''
		try:
			id_ = int(param['id'])
		except:
			id_ = param['id']
			
		if type(id_) == int:
                        cur = CONFIG.ask_good.find_one({'_id': id_})
	                if not cur:
        	                cur = CONFIG.ask_bad.find_one({'_id': id_})
			if not cur:
				cur = CONFIG.real_good.find_one({'_id': id_})
		else:
	                cur = CONFIG.ask_paid.find_one({'_id': id_})
        	        if not cur:
				cur = CONFIG.real_good.find_one({'_id': id_})
		if not cur:
			self.finish({})
			#return self.redirect('/')
			return ''

		title = cur.get('title', '')
		content = cur.get('content', '')
		answers = cur.get('machine_answer', '')

		query_tags, baikes, baike_key = ANALYSE_ASK.analyse_query(title, content)

		titles_count = 15
		question_titles = []
		all_ids = {id_: 0}
		ask_query = {
        		"query": {
            			"bool": {
                			"must": [{"multi_match": {"query": "", "fields": ["title"], "minimum_should_match": "75%"}}]
                		}
	        	},
        		"from":0,
        		"size":titles_count + 5
    		}
		ask_query["query"]["bool"]["must"][0]["multi_match"]["query"] = title
		weight = 30
	
		if len(query_tags) > 0:
			ask_query["query"]["bool"]["should"]=[{"match": {"title": {"query": "".join(query_tags), "boost": weight}}}]

		es_res = es.search(index=CONFIG.index_new, body=ask_query, request_timeout = 60)
		hits = es_res["hits"]["hits"]

		count = 1
		for hit in hits:
			if count == (titles_count+1):
				break
			doc = {}
			es_id = int(hit["_id"])
			if es_id in all_ids:
            			continue

			all_ids[es_id] = 0
			source = hit["_source"]
			doc['id'] = es_id
			doc['title'] = source["title"]
			doc['content'] = source['content']
			ask_res = CONFIG.ask_good.find_one({"_id": es_id})
			if not ask_res:
				ask_res = CONFIG.ask_bad.find_one({"_id": es_id})
			if not ask_res:
				print 'error', es_id, 'can find it'
            			continue
			sub = source['sub']
			doc['answer'] = ask_res['answer'][sub]
			doc['date'] = ask_res['date']
			doc['display'] = 1
		
			if len(question_titles) <= 5:
				question_titles.append(doc)
			else:
				question_titles.append({"id": es_id,"title":source["title"],"display":1})

			count += 1
		# 问题如果没有15个就继续找
		ask_query["size"] = titles_count - len(question_titles)
		if ask_query["size"]:
			if ask_query["size"] == titles_count:
				pass
			else:
				ask_query["size"] += 1
			print 'again', ask_query["size"]
	                for index in range(len(query_tags),0,-1):
				if len(question_titles) >= titles_count:
					break
		    		the_query  = "".join(query_tags[:index])
	    		        ask_query["query"]["bool"]["must"][0]["multi_match"]["query"] = the_query
        			es_res = es.search(index=CONFIG.index_new, body=ask_query, request_timeout=60)
            			hits = es_res["hits"]["hits"]
            			for hit in hits:
                			doc = {}
					if len(question_titles) >= titles_count:
						break
 			               	es_id = int(hit["_id"])
                			if es_id in all_ids:
                    				continue
			                all_ids[es_id] = 0

			                doc['id'] = es_id
        			        source = hit["_source"]
                			doc['title'] = source["title"]
                			doc['content'] = source['content']


	 		               	ask_res = CONFIG.ask_good.find_one({"_id": es_id})
        		        	if not ask_res:
						ask_res = CONFIG.ask_bad.find_one({"_id": es_id})
        		        	if not ask_res:
                		    		print 'error', es_id, 'can find it'
                    				continue
		                	sub = source['sub']
	        		        doc['answer'] = ask_res['answer'][sub]
        	        		doc['date'] = ask_res['date']
                			doc['display'] = 1
					if len(question_titles) <= 5:
                        			question_titles.append(doc)
		                	else:
        			                question_titles.append({"id": es_id,"title":source["title"],"display":1})

		if not baikes and answers:
			#for answer in answers:
			#tags = jieba.cut(answer["answer_bqfx"])
			tags = jieba.cut(answers)
			for tag in tags:
				if type(tag) == str:
	                                tag = tag.decode('utf-8')
				if tag in CONFIG.disease and not baikes:
					baikes = CONFIG.disease[tag]
					break
				if tag in CONFIG.lexicon and not baike_key:
		                        baike_key = tag
		relative_baikes = []
		baike_query = {
 			"query":
        			{
            			"bool": {
                			"must": [{
                            			"multi_match":
                                			{
                                    				"query": "",
                                    				"fields": ["title", "symptom"]
                                			}
                        			}],
                			"disable_coord": "true"
                			}
            			},
 	   		"from":0,
    			"size":3
  		}

		if baikes:
			baike_query["query"]["bool"]["must"][0]["multi_match"]["query"] = baikes["title"]
			es_res = es_old.search(index=CONFIG.baike_index, body=baike_query, request_timeout=60)
			hits = es_res["hits"]["hits"]
			for hit in hits:
				if hit["_source"]["title"] != baikes["title"]:
					relative_baikes.append({
	        	                        "name":hit["_source"]["name"],
        		                        "title": hit["_source"]["title"],
	               	                	"thumb": hit["_source"]["thumb"]
                              		})
			baikes['relative_baike'] = relative_baikes
		
		elif baike_key:
			baike_query["query"]["bool"]["must"][0]["multi_match"]["query"] = baike_key
			es_res = es_old.search(index=CONFIG.baike_index, body=baike_query, request_timeout=60)
                        hits = es_res["hits"]["hits"]
                        for hit in hits:
				baikes["title"] = hit["_source"]["title"]
	            		baikes["description"] = hit["_source"]["description"]
        		    	baikes["name"] = hit["_source"]["name"]
	        	    	baikes["thumb"] = hit["_source"]["thumb"]
				break
			if baikes:
				baike_query["query"]["bool"]["must"][0]["multi_match"]["query"] = baikes["title"]
				es_res = es_old.search(index=CONFIG.baike_index, body=baike_query, request_timeout=60)
				hits = es_res["hits"]["hits"]
				for hit in hits:
        	                        if hit["_source"]["title"] != baikes["title"]:
                	                        relative_baikes.append({
                        	                        "name":hit["_source"]["name"],
                                	                "title": hit["_source"]["title"],
                                        	        "thumb": hit["_source"]["thumb"]
                                        	})
	                        baikes['relative_baike'] = relative_baikes
		else:
			pass
		
		self.finish({"questions":question_titles, "baike":baikes})
		
class NewsHandler(BaseHandler):
	@run_on_executor
	def post(self):
		try:
			param = {}
                        params = json.loads(self.request.body)
                        param["id"] = params.get('id_', "")
                except Exception, e:
                        param = None
			print params,e
			self.finish({})
			#return self.redirect('/')
			return ''
		try:
			id_ = int(param['id'])
		except:
			id_ = param['id']
			
		if type(id_) == int:
                        cur = CONFIG.ask_good.find_one({'_id': id_})
	                if not cur:
        	                cur = CONFIG.ask_bad.find_one({'_id': id_})
			if not cur:
				cur = CONFIG.real_good.find_one({'_id': id_})
		else:
	                cur = CONFIG.ask_paid.find_one({'_id': id_})
        	        if not cur:
				cur = CONFIG.real_good.find_one({'_id': id_})

		if not cur:
			print 'id_', id_, 'not in paid'
			self.finish({})
			#return self.redirect('/')
			return ''

		title = cur.get('title', '')
		content = cur.get('content', '')
		answers = cur.get('machine_answer', '')

		labels = ANALYSE_NEW.get_labels(title, content, answers)
		relative_news = []
		query = "".join(labels[:3])
		news_query = {
			"query": {"bool": {
        	         	"must": [{"multi_match": {"query": "", "fields": ["title"], "minimum_should_match": "65%"}}],
	                   	"should": [{"match_phrase": {"title": {"query": "", "slop": 2}}}]}
                          },
                	"from": 0,
                	"size": 25
            	}
		if len(labels) == 0:
			self.finish({})
			print id_, title, 'no label'
			return ''

		news_query["query"]["bool"]["must"][0]["multi_match"]["query"] = query
            	news_query["query"]["bool"]["should"][0]["match_phrase"]["title"]["query"] = query
	        news_query["query"]["bool"]["should"].append({"match": {"title": {"query": "".join(labels[:2]), "boost": 30}}})

		# old news
		titles = []
		es_res = es_old.search(index=CONFIG.old_index_new, body=news_query, request_timeout = 60)
		hits = es_res["hits"]["hits"]
            	for hit in hits:
                	if len(relative_news) < 5:
                    		if len(hit["_source"]["title"]) >= 3 and hit["_source"]["title"] not in titles:
                        		titles.append(hit["_source"]["title"])
                        		relative_news.append(hit["_source"])
		news_data = {"_id": id_, "labels": labels, "old_news": relative_news}

		# new news
		new_news_query = {
                	"query": {
                    		"bool": {
                        		"must": [{"multi_match": {"query": "", "fields": ["title"], "minimum_should_match": "45%"}}],
                        		"should": [{"match_phrase": {"title": {"query": "", "slop": 3}}}]
                    		}
                	},
                	"from": 0,
                	"size": 25
            	}

		new_news_query["query"]["bool"]["must"][0]["multi_match"]["query"] = query
		new_news_query["query"]["bool"]["should"][0]["match_phrase"]["title"]["query"] = query
		new_news_query["query"]["bool"]["should"].append({"match": {"title": {"query": "".join(labels[:2]), "boost": 45}}})
		es_res = es_old.search(index=CONFIG.new_index_new, body=new_news_query, request_timeout = 60)
		relative_news = []
            	hits = es_res["hits"]["hits"]
            	for hit in hits:
                	if len(relative_news) < 5:
                    		if len(hit["_source"]["title"]) >= 3 and hit["_source"]["title"] not in titles:
                        		titles.append(hit["_source"]["title"])
                        		relative_news.append(hit["_source"])
		news_data["news"] = relative_news

		# recommends
		recommend_query = {
            		"query": {
                		"bool": {
                    			"must": [
                        			{"multi_match": {"query": "", "fields": ["title"], "minimum_should_match": "75%"}}]
                		}
            		},
            		"_source": ["title"],
            		"from": 0,
            		"size": 10
        	}
		recommend_query["query"]["bool"]["must"][0]["multi_match"]["query"] = title
		print title,
		print 'table:',
		if len(labels) > 0:
			recommend_query["query"]["bool"]["should"] = {"match": {"title": {"query": "".join(labels[:2]), "boost": 10}}}
			print ''.join(labels[:2]),

		es_res = es_old.search(index=CONFIG.recommend_index, body=recommend_query, request_timeout=60)
		hits = es_res["hits"]["hits"]
		recommends = set()
		for hit in hits:
			recommends.add(hit["_source"]["title"])
			#print hit["_source"]["title"]

		if len(recommends) < 3:
			print 'find again'
			recommend_query["query"]["bool"]["must"][0]["multi_match"]["minimum_should_match"] = "35%"
			es_res = es_old.search(index=CONFIG.recommend_index, body=recommend_query, request_timeout=60)
			hits = es_res["hits"]["hits"]
			for hit in hits:
				if len(recommends) > 9:
					break
                                recommends.add(hit["_source"]["title"])
				#print hit["_source"]["title"]


		self.finish({"news_data":news_data, "recommends":list(recommends)})

class TestHandler(tornado.web.RequestHandler):
        def get(self):
                print 'index'
                self.write('hello iris, your has visit test newask')

application = tornado.web.Application([
        (r"/newask/", AskHandler),
	(r'/new_news/', NewsHandler),
       	(r'/.*', TestHandler),
])

if __name__ == '__main__':
	es = Elasticsearch([CONFIG.es_new])
	es_old = Elasticsearch([CONFIG.es_old])
        http_server = tornado.httpserver.HTTPServer(application)
        print 'come on'
        http_server.listen(CONFIG.insert_service_port)
        tornado.ioloop.IOLoop.instance().start()


