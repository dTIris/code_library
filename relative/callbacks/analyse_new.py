# -*- coding:utf-8 -*-

import config as CONFIG
import jieba

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def get_labels(title, content, answers, tags_size=3):
	labels = []

        if title:
                tags = jieba.cut(title, cut_all=True)
                for tag in tags:
                        if not tag:
                                continue
                        if type(tag) == str:
                                tag = tag.decode('utf-8')
			if (tag in CONFIG.disease or tag in CONFIG.lexicon) and tag not in CONFIG.stopwords and tag not in labels:
                                labels.append(tag.strip().replace("\r\n", ""))
			if len(labels) >= tags_size:
                    		return labels

        if content and len(content) > 0:
                tags = jieba.cut(content, cut_all=True)
                for tag in tags:
                        if type(tag) == str:
                                tag = tag.decode('utf-8')
			if (tag in CONFIG.disease or tag in CONFIG.lexicon) and tag not in CONFIG.stopwords and tag not in labels and tag:
                                labels.append(tag)
			if len(labels) >= tags_size:
                    		return labels
	'''
	for answer in answers:
		tags = jieba.cut(answer["answer_bqfx"])
		for tag in tags:
			if (tag in CONFIG.disease or tag in CONFIG.lexicon) and tag not in CONFIG.stopwords and tag and tag not in labels:
				labels.append(tag)
			if len(labels) >= tags_size:
                    		return labels
	'''
	if answers:
		tags = jieba.cut(answers)
		for tag in tags:
                        if type(tag) == str:
                                tag = tag.decode('utf-8')
			if (tag in CONFIG.disease or tag in CONFIG.lexicon) and tag not in CONFIG.stopwords and tag not in labels and tag:
                                labels.append(tag)
                        if len(labels) >= tags_size:
                                return labels

	if len(labels) < tags_size:
		if title:
			title_tags = jieba.analyse.extract_tags(title, topK = tags_size)
			for tag in title_tags:
				if type(tag) == str:
					tag = tag.decode('utf-8')
				if len(labels) >= tags_size:
					return labels
				if tag not in labels and tag not in CONFIG.stopwords:
					labels.append(tag)

	return labels





