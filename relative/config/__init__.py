# -*-coding:utf-8 -*-

import os
import posixpath
import jieba
from jieba import analyse as JANALYSE
import json
import redis
from pymongo import MongoClient
from elasticsearch import Elasticsearch

dir_entry = "./config"


jieba.load_userdict(os.path.join(dir_entry, "jk.all.big"))
JANALYSE.set_stop_words(os.path.join(dir_entry, "stopwords.txt"))
lexicon = json.loads(open(os.path.join(dir_entry, "jk.all.json"), "r").read())
disease = json.loads(open(os.path.join(dir_entry, "jk.disease.json"), "r").read())
stopwords = json.loads(open(os.path.join(dir_entry, "stopwords.json"), "r").read())

# 查询es
es_new ={'host': "host", 'port': port}
es_old ={'host': "host", 'port': port}

#存入redis，需修改
redis_set = redis.Redis(host='host', port=, password='', db=0)

index_new = "ask_real"
baike_index = "jk_new_baike"
old_index_new = "jk_old_news"
new_index_new = "jk_brand_news"
recommend_index = "jk_recommend"

# 搜索中的问答数据,需修改为线上
mongo_conn = MongoClient('host', port)
data_ = mongo_conn.analysis_data
data_.authenticate()
ask_good = data_.ask_good
ask_bad = data_.ask_bad

# 查询线上数据
mongo_save = MongoClient("host", port)
data = mongo_save.real_analysis_data
data.authenticate()
real_good = data.ask_good
ask_paid = data.ask_paid

# 一次性存储的数据库,线下，不需修改
mongo_save = MongoClient('host', port)
rela = mongo_save.iris_relatives
asks = rela.asks
flow_news = rela.flow_news
news = rela.news
recommends = rela.recommends

# 每天跑入的数据库, 需修改
mongo_new = MongoClient('host', port)
rela_new = mongo_new.real_relatives
rela_new.authenticate()
asks_new = rela_new.asks
news_new = rela_new.news
recommends_new = rela_new.recommends

#线上运行insert_service.py的ip，需修改
insert_service_url = host
use_service_url = host
insert_service_port = port1
use_service_port = port2

