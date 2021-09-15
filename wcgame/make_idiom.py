# auhtor: iris
# date: 2019-06-19
# desc: 生成成语布局

import sys
import numpy
import random
import config as CONFIG
from copy import deepcopy
from pymongo import MongoClient

# 成语
class Idiom():
	# 类属性#{{{
	word = ''						# 某关开头的第一个字
	word_id = 1						# 遍历字的位置
	word_used = {}					# 记录用过的成语数
	idiom_used = []					# 记录使用过的成语
	same_idioms = set()				# 记录相似成语
	word_max = 239					# 只有239个字拥有大于一百的成语数
#}}}

	# 初始化函数init#{{{
	def __init__(self):
		self.idiom = ''				# 成语
		self.idioms_pos = []		# 成语坐标
		self.direction = 0			# 成语方向，0为横向，1为竖向
		self.next_turn = -1			# 成语朝向，0为左上，1为右下
		self.edge = None			# 成语边缘
		self.words = {}				# 字-查找下标
		self.use_sub = -1			# 交叉过的下标
		self.last_sub = -1			# 上一个成语交叉的下标
		self.find_sub = -1			# 第一次遍历时随机查找的下标
		self.next_sub = -1			# 下一个成语被交叉的下标
		#self.hollow_subs = []		# 被挖空的下标们
		
#}}}

	# set_word:手动设置成语，参数word_id#{{{
	@classmethod
	def set_word(self, word_id):
		word_id = word_id
#}}}

	# get_idiom:获得成语#{{{
	def get_idiom(self, difficulty, word=None, sub=-1, use_idioms=[]):
		if difficulty == 'first':
			find_set = CONFIG.first_idiom_set
		elif difficulty == 'easy':
			find_set = CONFIG.easy_idiom_set
		elif difficulty == 'middle':
			find_set = CONFIG.middle_idiom_set
		elif difficulty == 'hard':
			find_set = CONFIG.hard_idiom_set
		else:
			print ('difficulty error:', difficulty)
			return 'false'
		# 当有参数时查找成语#{{{
		if word and sub >= 0:
			idiom_result = find_set.find_one({'_id': word})
			if not idiom_result:
				return 'false'

			sub = str(sub)
			idiom_list = idiom_result.get(sub, [])

			# 判断该字是否有效
			if len(idiom_list) < 1:
				return 'false'
			
			status = 0
			while True:
				if word in Idiom.word_used:
					if sub in Idiom.word_used[word]:
						if Idiom.word_used[word][sub] > len(idiom_list):
							#print (Idiom.word_used[word][sub], 'len', len(idiom_list))
							Idiom.word_used[word][sub] = 1
					else:
						Idiom.word_used[word][sub] = 1
				else:
					Idiom.word_used[word] = {}
					Idiom.word_used[word][sub] = 1

				idiom_sub = Idiom.word_used[word][sub]

				if status > 2:
					return 'false'

				if idiom_list[idiom_sub-1] in use_idioms or idiom_list[idiom_sub-1] in Idiom.same_idioms:
						Idiom.word_used[word][sub] += 1
						status += 1
						continue
					
				if idiom_list[idiom_sub-1] in Idiom.idiom_used:
					if set(idiom_list) < set(Idiom.idiom_used):
						for del_item in idiom_list:
							if del_item in use_idioms:
								continue
							Idiom.idiom_used.remove(del_item)
					else:
						Idiom.word_used[word][sub] += 1
						continue

				# 轮到要挑选成语的位置，需判断位置是否溢出
				self.idiom = idiom_list[idiom_sub-1] #下标从0开始
				same_cur = CONFIG.same_set.find_one({'_id': self.idiom})
				if same_cur:
					for same_idiom in same_cur.get('same', []):
						Idiom.same_idioms.add(same_idiom)

				Idiom.idiom_used.append(idiom_list[idiom_sub-1])
				return 'succeed'
#}}}

		# 遍历取出合适的成语#{{{#}}}#{{{
		while(True):
			# 获得成语word
			Idiom.word_id = Idiom.word_id % (Idiom.word_max+1)

			word_result = CONFIG.word_set.find_one({'_id': Idiom.word_id})
			if not word_result:
				Idiom.word_id += 1
				continue
				
			word = word_result.get('word','')

			# 获得首字为该字的成语列表idiom_list,长度list_0_length
			idiom_result = find_set.find_one({'_id': word})
			idiom_list = idiom_result.get('0', [])
			
			# 判断该字是否有效
			if len(idiom_list) < 1:
				Idiom.word_id += 1
				continue

			sub = '0'
			if word in Idiom.word_used:
				if sub in Idiom.word_used[word]:
					if Idiom.word_used[word][sub] < len(idiom_list):
						Idiom.word_used[word][sub] += 1
					else:
						Idiom.word_used[word][sub] = 1
				else:
					Idiom.word_used[word][sub] = 1
			else:
				Idiom.word_used[word] = {}
				Idiom.word_used[word][sub] = 1

			idiom_sub = Idiom.word_used[word][sub]

			Idiom.word_used[word][sub] -= 1
			break
#}}}

		# 获得成语idiom
		self.idiom = idiom_list[idiom_sub-1]
		Idiom.idiom_used.append(idiom_list[idiom_sub-1])
		same_cur = CONFIG.same_set.find_one({'_id': self.idiom})
		if same_cur:
			for same_idiom in same_cur.get('same', []):
				Idiom.same_idioms.add(same_idiom)

		Idiom.word_id += 1

		return 'new'
#}}}
	
	# get_idiom_pos:设置next_turn,edge,idioms_pos#{{{
	# 当成语紧贴墙壁时，edge等于贴住的轴线,next_turn左上为0
	def get_idiom_pos(self, x, y):
		if self.direction:
			type_ =  "竖向"
			self.idioms_pos = [(x,y),(x+1,y),(x+2,y),(x+3,y)]
			if y == 0:
				self.edge = 'y'
				self.next_turn = 0
			elif y == 8:
				self.edge = 'y'
				self.next_turn = 1
			else:
				self.edge = None
		else:
			type_ = "横向"
			self.idioms_pos = [(x,y),(x,y+1),(x,y+2),(x,y+3)]
			if x == 0:
				self.edge = "x"
				self.next_turn = 0
			elif x == 8:
				self.edge = "y"
				self.next_turn = 1
			else:
				self.edge = None
		return type_
#}}}
			
# 成语游戏地图
class IdiomLayout():
	# init_map:返回9*9空白矩阵#{{{
	def init_map(self):
		my_map = [[{"-1":0}]*9]*9
		#my_map = [['**']*9]*9
		return numpy.asarray(my_map)
		#return my_map
#}}}

	# set_first_area:返回x或y小于num的范围#{{{
	def set_first_area(self, num=9):
		#return [['']*9]*6
		area = []
		for x in range(9):
			for y in range(9):
				if y > num and x > num:
					continue
				area.append((x,y))
		return area
#}}}

	# 初始化函数init#{{{
	def __init__(self):
		self.maps = self.init_map() 		# 设置空白地图
		self.use_pos = []					# 记录地图使用过的位置
		self.words = []						# 记录挖空的字
		self.use_idioms = []				# 记录成语

		# 记录用过的成语数
		self.word_used = CONFIG.record_set.find_one({'_id': 'word_used'})
		# 记录使用过的成语
		self.idiom_used = CONFIG.record_set.find_one({'_id': 'idiom_used'}).get('idiom_used', [])
		# 记录使用过的成语数
		self.word_id = CONFIG.record_set.find_one({'_id': 'word_id'}).get('word_id', 1)

		self.count = 0				# 指定成语数
		self.mission = 0			# 指定关卡数
		self.word_counts = []		# 指定缺字数
		self.difficulty = ''		# 指定难易程度

		self.idioms_count = 0		# 已生成的成语数
		self.idioms = {}			# 成语实例#}}}

	# get_cross:获取交叉字下标,查找字下标,words#{{{
	def get_cross(self, idiom):
		# 第二层的成语，无交叉下标use_sub和上一个成语的交叉下标last_sub#{{{
		if idiom.use_sub == -1:
			word_pos = idiom.idioms_pos[0]
			# 成语在边线的话，只能选择两个交叉点
			if idiom.edge:
				cross_sub = [0,3]
				if idiom.next_turn == 1:
					next_idiom_sub = [3,3]
				else:
					next_idiom_sub = [0,0]
			elif idiom.direction == 1 and word_pos[1] in [0,1,2,6,7,8]:
				cross_sub = [0,3]
				if word_pos[1] in [6,7,8]:
					next_idiom_sub = [3,3]
				else:
					next_idiom_sub = [0,0]
			elif idiom.direction == 0 and word_pos[0] in [0,1,2,6,7,8]:
				cross_sub = [0,3]
				if word_pos[0] in [6,7,8]:
					next_idiom_sub = [3,3]
				else:
					next_idiom_sub = [0,0]
			else:
				cross_sub = random.choice([[0,1,3],[0,2,3],[0,2],[1,3]])
				next_idiom_sub = random.choice([[3,0,3],[0,3,0]])

			words = {}
			i = 0
			for sub in cross_sub:
				idiom.words['{}_{}'.format(sub,next_idiom_sub[i])] = idiom.idiom[sub]
				#print (idiom.idiom[sub], next_idiom_sub[i],';', end='')
				i += 1
			#print ('')
			return 'OK'
#}}}
		# 第三层到无回溯的成语，无随机查找的下标find_sub，和下一个成语的交叉下标next_sub#{{{
		elif idiom.find_sub == -1:
			word_pos = idiom.idioms_pos[idiom.use_sub]

			## 当两个成语的交叉点都在边缘区间内时，则跳过#{{{
			#if word_pos[0] in [0,1,2,6,7,8] and word_pos[1] in [0,1,2,6,7,8]:
			#	idiom.find_sub = 5
			#	return word_pos
#}}}

			#cross_sub = (0 if idiom.use_sub == 3 else 3)
			cross_sub= random.choice([sub for sub in range(4) if abs(sub-idiom.use_sub)>1])
			if idiom.direction == 1 and word_pos[1] in [0,1,2,6,7,8]:
				if word_pos[1] in [6,7,8]:
					idiom.words['{}_{}'.format(cross_sub, 3)] = idiom.idiom[cross_sub]
					#print (idiom.idiom[cross_sub], '3;')
				else:
					idiom.words['{}_{}'.format(cross_sub, 0)] = idiom.idiom[cross_sub]
					#print (idiom.idiom[cross_sub], '0;')
			elif idiom.direction == 0 and word_pos[0] in [0,1,2,6,7,8]:
				if word_pos[0] in [6,7,8]:
					idiom.words['{}_{}'.format(cross_sub, 3)] = idiom.idiom[cross_sub]
					#print (idiom.idiom[cross_sub], '3;')
				else:
					idiom.words['{}_{}'.format(cross_sub, 0)] = idiom.idiom[cross_sub]
					#print (idiom.idiom[cross_sub], '0;')
			elif idiom.last_sub in [0, 1]:
				idiom.words['{}_{}'.format(cross_sub, 3)] = idiom.idiom[cross_sub]
				#print (idiom.idiom[cross_sub], '3;')
			elif idiom.last_sub in [2, 3]:
				idiom.words['{}_{}'.format(cross_sub, 0)] = idiom.idiom[cross_sub]
				#print (idiom.idiom[cross_sub], '0;')
			return 'OK'
#}}}
		# 回溯成语寻找下标#{{{
		else:
			#print ("回溯", end='')
			cross_sub = [sub for sub in range(4)]
			if idiom.use_sub >= 0:
				cross_sub.pop(idiom.use_sub)
				#print ("{}:不需查找第{}位的成语".format(idiom.idiom,idiom.use_sub))
			#if idiom.find_sub >= 0:
			#	cross_sub.pop(idiom.find_sub)
			#	print ("{}:不需查找第{}位的成语".format(idiom.idiom,idiom.find_sub))
				

			word_pos = idiom.idioms_pos[idiom.use_sub]
			next_find_sub = [i for i in range(4)]
			if idiom.direction == 1:
				if word_pos[1] in [0,1] and idiom.last_sub == 0:
					next_find_sub = [0]
				if word_pos[1] in [7,8]:
					next_find_sub = [3]
			else:
				if word_pos[0] in [0,1] and idiom.last_sub == 0:
					next_find_sub = [0]
				if word_pos[0] in [7,8] and idiom.last_sub == 3:
					next_find_sub = [3]

			for sub in cross_sub:
				for i in next_find_sub:
					idiom.words['{}_{}'.format(sub, i)] = idiom.idiom[sub]
			
			return 'OK'
#}}}
			#}}}

	# write_map：将数据写入地图中#{{{
	def write_map(self, idiom, last_idiom=None):
		# 第一个成语，不挖空
		if idiom.use_sub < 0:
			words_sub = -1
		# 其他成语，挖空上一个交叉字个数
		else:
			words_sub = idiom.use_sub
			print ('挖空第{}个字：{}'.format(words_sub+1,idiom.idiom[words_sub]))
			
			# 记录挖空字和挖空的下标
			self.words.append(idiom.idiom[words_sub])
			#idiom.hollow_subs.append(words_sub)
			#last_idiom.hollow_subs.append(last_idiom.find_sub)

		# 在地图中写入成语，将交叉字挖空，并记录使用过的位置
		i = 0
		for pos in idiom.idioms_pos:
			if i != words_sub:
				self.maps[pos[0]][pos[1]] = {'1':idiom.idiom[i]}
			else:
				self.maps[pos[0]][pos[1]] = {'0':idiom.idiom[i]}
			self.use_pos.append(pos)
			i += 1

		self.idioms_count += 1

		#print (self.maps)
#}}}

	# make_mission:每个关卡生成的成语#{{{
	def make_mission(self):
		# 初始化#{{{
		self.idioms_count = 0
		self.idioms = {}
		self.maps = self.init_map()
		self.words = []
		self.use_pos = []
		self.use_idioms = []
		Idiom.same_idioms = set()

		level = 1
		relevel = 0#}}}
		
		#print (self.idioms_count, self.count, Idiom.word_id)
		while(self.idioms_count < self.count):
			#print ("第",level,"层: ", end='')
			# 第一个成语#{{{
			if not self.idioms:
				idiom = Idiom()
				res = idiom.get_idiom(self.difficulty)
				if not idiom.idiom:
					#print ("没有, 退出")
					break

				#print ("type:"+res, idiom.idiom, end=' ')
				#print ("核心成语:", idiom.idiom, end=' ')

				# 获取初选字的坐标
				idiom.direction = random.randint(0,1) # 随机
				#idiom.direction = 0
				if idiom.direction:
						x = random.randint(0,5)
						y = random.randint(0,8)
						
				else:
						x = random.randint(0,8)
						y = random.randint(0,5)
				#x = 7
				#y = 3

				type_ = idiom.get_idiom_pos(x, y)
				#print ('核心坐标：',(x,y), type_)

				if idiom.edge:
					text = "处于轴线{}".format(idiom.edge)
				else:
					text = ''

				#print ("{}{}:next_trun{}{}".format(idiom.idiom, idiom.idioms_pos, idiom.next_turn, text))
				self.write_map(idiom)
				self.idioms[level] = [idiom]
				self.use_idioms.append(idiom.idiom)
#}}}
			else:
				# 迭代生成其他成语#{{{
				i = 0
				if not self.idioms.get(level-1, []):
					#print (level-1, "层无数据")
					break
				state = False
				# 遍历上一层的数据
				for last_idiom in self.idioms.get(level-1, []):
					# 获取交叉字下标和坐标#{{{
					#print ('遍历 ' + last_idiom.idiom, '--', end='')
					res = self.get_cross(last_idiom)
					if res != 'OK':
						#print('由于', res, '处于边界中，跳过该成语')
						continue
	#}}}
					# 遍历words数据#{{{
					for subs in last_idiom.words:
						#print ('subs', subs, end='-')
						if self.idioms_count >= self.count:
							#print (self.idioms_count, self.count, '足够')
							break

						# 解析words数据#{{{
						word = last_idiom.words[subs]
						sub = int(subs.split('_')[0])					# 交叉字下标
						next_sub = int(subs.split('_')[1])				# 查找字下标
						word_pos = last_idiom.idioms_pos[sub]			# 交叉字坐标

						last_idiom.find_sub = sub						# 存入查找过的下标#}}}
						
						# 初始化成语对象,并设置方向与上一层相反#{{{
						new_idiom = Idiom()
						new_idiom.direction = int(last_idiom.direction == 0)
#}}}
	
						#调用get_idiom_pos方法，获得坐标#{{{

						x = word_pos[0]
						y = word_pos[1]
						if new_idiom.direction:
							x -= next_sub
						else:
							y -= next_sub

						type_ = new_idiom.get_idiom_pos(x,y)
						#print ("查找第{}位为{}的成语".format(next_sub, word), end=' ')
						#print ('坐标:', (x, y), type_, end=' ')#}}}

						# 检查异常情况并跳过#{{{
						
						# 判断成语是否重复出现
						if new_idiom.idiom in self.use_idioms:
								#print ('*成语', idiom.idiom, '重复，跳过')
								continue

						# 判断重复出现的坐标#{{{
						repeat_sub =[sub_ for sub_ in new_idiom.idioms_pos if sub_ in self.use_pos]
						if len(repeat_sub) > 1:
								#print ("*坐标", repeat_sub, "重复, 跳过")
								continue#}}}

						# 判断非法坐标#{{{
						error_sub = []
						for sub_ in new_idiom.idioms_pos:
							if sub_[0] < 0 or sub_[0] > 8:
									error_sub.append(sub_)
							elif sub_[1] < 0 or sub_[1] > 8:
									error_sub.append(sub_)

						if len(error_sub) > 0:
								#print ("*坐标", error_sub, "非法, 跳过")
								continue#}}}

						# 判断相邻坐标#{{{
						near_sub = []
						use_pos = set(self.use_pos)|set(new_idiom.idioms_pos)
						'''#{{{
						for x,y in new_idiom.idioms_pos:
							temp = set((x,y+1+i) for i in range(4))
							temp_ = set((x,y-1-i) for i in range(4))
							if temp <= use_pos or temp_ <= use_pos:
								near_sub.append((x,y))
								break

							temp = set((x+i+1,y) for i in range(4))
							temp_ = set((x-i-1,y) for i in range(4))
							if temp <= use_pos or temp_ <= use_pos:
								near_sub.append((x,y))
								break

						if not len(near_sub):
							temp_ = new_idiom.idioms_pos
							if new_idiom.direction:
								for i in range(3):
									if set([(temp_[i][0], temp_[i][1]+1), (temp_[i+1][0], temp_[i+1][1]+1)]) < use_pos:
										near_sub.append((temp_[i][0], temp_[i][1]))
										near_sub.append((temp_[i+1][0], temp_[i+1][1]))
										break
									if set([(temp_[i][0], temp_[i][1]-1), (temp_[i+1][0], temp_[i+1][1]-1)]) < use_pos:
										near_sub.append((temp_[i][0], temp_[i][1]))
										near_sub.append((temp_[i+1][0], temp_[i+1][1]))
										break
							else:
								for i in range(3):
									if set([(temp_[i][0]+1, temp_[i][1]), (temp_[i+1][0]+1, temp_[i+1][1])]) < use_pos:
										near_sub.append((temp_[i][0], temp_[i][1]))
										near_sub.append((temp_[i+1][0], temp_[i+1][1]))
										break
									if set([(temp_[i][0]-1, temp_[i][1]), (temp_[i+1][0]-1, temp_[i+1][1])]) < use_pos:
										near_sub.append((temp_[i][0], temp_[i][1]))
										near_sub.append((temp_[i+1][0], temp_[i+1][1]))
										break
						'''#}}}
						
						i = 0
						for x,y in new_idiom.idioms_pos:
							if i == next_sub:
								i += 1
								continue
							if new_idiom.direction:
								if (x, y+1) in use_pos:
									near_sub.append((x,y))
									break
								if (x, y-1) in use_pos:
									near_sub.append((x,y))
									break 
							else:
								if (x+1,y) in use_pos:
									near_sub.append((x,y))
									break

								if (x-1,y) in use_pos:
									near_sub.append((x,y))
									break
							i += 1


						use_pos_ = set(self.use_pos) | set(new_idiom.idioms_pos)
						for x,y in new_idiom.idioms_pos:
							temp = set((x,y+1+i) for i in range(4))
							temp_ = set((x,y-1-i) for i in range(4))
							if temp <= use_pos_ or temp_ <= use_pos_:
								near_sub.append((x,y))
								break

							temp = set((x+i+1,y) for i in range(4))
							temp_ = set((x-i-1,y) for i in range(4))
							if temp <= use_pos_ or temp_ <= use_pos_:
								near_sub.append((x,y))
								break
					   

						if len(near_sub) > 0:
								#print ("*坐标", near_sub, "相邻, 跳过")
								continue#}}}
#}}}

						res = new_idiom.get_idiom(self.difficulty, word, next_sub, self.use_idioms)
						if not new_idiom.idiom:
							print (word, next_sub, "找不到, 跳过")
							continue

						if new_idiom.edge:
							text = "处于轴线{}".format(new_idiom.edge)
						else:
							text = ''
						print ("{}:{}{}".format(new_idiom.idiom, new_idiom.idioms_pos, text), end=' ')

						state = True

						new_idiom.use_sub = next_sub
						last_idiom.next_sub = next_sub
						new_idiom.last_sub = sub
						self.write_map(new_idiom, last_idiom)
						self.idioms[level].append(new_idiom)
						#print (level, new_idiom.idiom)
						self.use_idioms.append(new_idiom.idiom)

					i += 1
				# 回溯
				if not state:
					if relevel>4:
						break
					elif relevel>0:
						level -= 1
					relevel += 1
					continue
				else:
					relevel = 0
					#}}}
#}}}
			level += 1
			if level not in self.idioms:
				self.idioms[level] = []
			#print ('use_pos', self.use_pos)
		#}}}

	# hollow_map:挖空成语地图#{{{
	def hollow_map(self):
		# 挖空字的随机数目列表
		num_list = [i for i in range(int(self.word_counts[0]),int(self.word_counts[-1])+1)]

		# 遍历成语
		for level in self.idioms:
			for idiom in self.idioms[level]:
				print (idiom.idiom, end=':')
				# 随机每个挖空字的个数
				word_num = int(random.choice(num_list))

				#遍历一下成语，记录挖空的下标
				hollow_subs = []
				sub = 0
				for idiom_ in idiom.idiom:
					pos = idiom.idioms_pos[sub]
					if '0' in self.maps[pos[0]][pos[1]]:
						hollow_subs.append(sub)
					sub += 1

				# 当挖空的字数不足时,需挖空其他地方
				if len(hollow_subs) < word_num:
					sub_list = [i for i in range(4)]
					for sub in hollow_subs:
						sub_list.remove(sub)
					words_sub = random.sample(sub_list, word_num-len(hollow_subs))
					for sub in words_sub:
						pos = idiom.idioms_pos[sub]
						self.maps[pos[0]][pos[1]] = {'0':idiom.idiom[sub]}
						self.words.append(idiom.idiom[sub])
						print (idiom.idiom, '挖空第{}个字：{}'.format(sub+1,idiom.idiom[sub]))

				# 当挖空的字超过最大个数时，应删去交叉字
				elif len(hollow_subs) > max(num_list):
					sub_list = hollow_subs
					words_sub = random.sample(sub_list, len(hollow_subs)-max(num_list))
					for sub in words_sub:
						pos = idiom.idioms_pos[sub]
						self.maps[pos[0]][pos[1]] = {'1':idiom.idiom[sub]}
						self.words.remove(idiom.idiom[sub])
						print (idiom.idiom, '补第{}个字：{}'.format(sub+1,idiom.idiom[sub]))
				else:
						print ('')
#}}}

	# make_layout主方法，生成指定关卡#{{{
	def make_layout(self, datas):
		less_time = 0

		# 初始化成语类的类属性
		Idiom.idiom_used = deepcopy(self.idiom_used)
		Idiom.word_used = deepcopy(self.word_used)
		Idiom.word_id = self.word_id

		for data in datas:
			self.mission = data.get('mission')
			self.count = data.get('idiom_counts')
			self.word_counts = data.get('word_counts')
			self.difficulty = data.get('difficulty')
			if self.difficulty not in ['easy', 'middle', 'hard']:
				return 'difficulty err'
			elif self.mission <= 700:		
				self.difficulty = 'first'


			while True:
				self.make_mission()

				if less_time > 100:
					break
				#print ('word', Idiom.word_id)
				# 如果没有达到目标数，则重新来
				if self.idioms_count < self.count:
					print (self.idioms_count, 'no', self.count)
					if not self.idioms:
						return 'error'
					Idiom.idiom_used = deepcopy(self.idiom_used)
					Idiom.word_used = deepcopy(self.word_used)
					Idiom.word_id = self.word_id
					less_time += 1
					continue
				else:
					self.hollow_map()
					self.idiom_used = deepcopy(Idiom.idiom_used)
					self.word_used = deepcopy(Idiom.word_used)
					self.word_id = Idiom.word_id
					break

			try:
				#print (self.maps)
				maps = self.maps.tolist()
				#print (maps)
				CONFIG.save_set.update({'_id': self.mission}, {'$set':{'maps': maps, 'words':self.words, 'use_idioms': self.use_idioms, 'idioms':[]}})
				print ('第{}关：查找次数{},成语个数{}'.format(self.mission, less_time,self.idioms_count-1),  end=' ')
				print ('words', self.words, end=' ')
				print ('use_idioms', self.use_idioms)
			except Exception as e:
				return 'err', e

			#self.mission += 1
			less_time = 1
		try:
			self.word_used['_id'] = 'word_used'
			#print ('idiom_used', self.idiom_used)
			#print ('word_used', self.word_used)
			#print ('word_id', self.word_id)
			print ('*'*80)
			CONFIG.record_set.save(self.word_used)
			CONFIG.record_set.update({'_id': 'idiom_used'}, {'$set': {'idiom_used': self.idiom_used}})
			CONFIG.record_set.update({'_id': 'word_id'}, {'$set': {'word_id': self.word_id}})
		except Exception as e:
			return e

		return 'succeed'

#}}}



