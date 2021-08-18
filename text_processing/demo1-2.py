#!user/bin/env python3
# -*- coding:utf-8 -*-
# __author__ = Iris
# __create__ = 2021/08/18
# __update__ = 2021/08/19
# __desc__ = "
#   读取文件test.txt(大文件)；
#   去除所有标点符号和换行符，并把所有大写变成小写；
#   合并相同的词，统计每个词出现的频率，并按照词频从大到小排序；
#   将结果按行输出到文件 out.txt。
#   "

import re
from typing import List, Dict

# 文本解析，返回列表
def textparse(text:str) -> List[str]:
    text = re.sub(r'[^\w ]', ' ', text)

    text = text.lower()

    text_list = text.split(' ')

    text_list = filter(None, text_list)

    return text_list

# 根据词频排序,返回字典
def sort_cnt(word_list: List[str]):
    global word_cnt
    for word in word_list:
        if word in word_cnt:
            word_cnt[word] += 1
        else:
            word_cnt[word] = 1

def main():
    with open('test.txt', 'r') as f:
        for line in f.readlines():
            word_list = textparse(line)
            sort_cnt(word_list)

    word_freq = sorted(word_cnt.items(), key=lambda key: key[1], reverse=True)

    with open('demo1-2.txt', 'w') as f:
        for word, freq in word_freq:
            f.write('{}: {} \n'.format(word, freq))
            print(word, ':', freq)

if __name__ == "__main__":
    word_cnt = {}
    main()