# -*- coding:utf-8 -*-

import config as CONFIG
import jieba

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def analyse_query(title, content, tags_size=3):
        query_tags = []
        content_tags = []
	baikes = {}
	baike_key = ""

        if title:
                tags = jieba.cut(title, cut_all=True)
                for tag in tags:
                        if not tag:
                                continue
                        if type(tag) == str:
                                tag = tag.decode('utf-8')
			if not baike_key and tag in CONFIG.lexicon:
				baike_key = tag

                        if tag in CONFIG.lexicon and tag not in CONFIG.stopwords and tag not in query_tags:
				if not baikes and tag in CONFIG.disease:
					baikes = CONFIG.disease[tag]
                                query_tags.append(tag.strip())
                        if len(query_tags) >= tags_size:
                                break

        if content and len(content) > 0:
                tags = jieba.cut(content, cut_all=True)
                for tag in tags:
                        if type(tag) == str:
                                tag = tag.decode('utf-8')
			if not baike_key and tag in CONFIG.lexicon:
		                baike_key = tag
                        if tag in CONFIG.lexicon and tag not in content_tags and tag not in query_tags and tag not in CONFIG.stopwords:
				if not baikes and tag in CONFIG.disease:
                                        baikes = CONFIG.disease[tag]
                                content_tags.append(tag)

        if len(query_tags) < tags_size:
                query_tags.extend(content_tags)

        if query_tags and len(query_tags) >= tags_size:
                query_tags = query_tags[:tags_size]
        else:
                if title:
                        title_tags = jieba.analyse.extract_tags(title, topK = tags_size)
                        for tag in title_tags:
                                if type(tag) == str:
                                        tag = tag.decode('utf-8')
                                if not tag:
                                        continue
                                if len(query_tags) >= tags_size:
                                        break
                                if tag not in query_tags and tag not in CONFIG.stopwords:
                                        query_tags.append(tag)
        return query_tags, baikes, baike_key





