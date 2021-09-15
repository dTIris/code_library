# 2018-2019年项目

### 发送附件邮件：

* 链接：[sendbyemail](https://github.com/dTIris/code_library/tree/master/sendbyemail)
* 时间：2018-11-20
* 描述：从mongo数据库和redis数据库中查询数据制作成xls表格并发送到指定邮箱（outlook）
* 技术栈：xls库xlwt模块，邮件email模块以及smtplib模块（简单邮件传输协议）

### 自然语言处理-敏感词搜寻：

* 链接：[censor](https://github.com/dTIris/code_library/tree/master/censor)
* 时间：2018-08-27
* 描述：根据接收到的请求解析请求体中的字符串，返回是否包含敏感词的结果
* 技术栈：使用tornado作为web框架，json用来解析请求体和将结果编码后作为响应返回

### 自然语言处理-智能推荐系统：

* 链接：[relative](https://github.com/dTIris/code_library/tree/master/relative)
* 时间：2018-11-10至2018-11-16
* 描述：根据用户的新提问，分析并生成相关数据，过滤重复数据后返回相关
* 技术栈：使用tornado作为web框架，elasticsearch作为搜索和数据分析引擎，通过jieba分词模块处理提问数据后提取相关的关键词并赋予不同权重，采用多重匹配技术和分批多次查询来获取相关结果

### 后台配置系统-医生分配问题：

* 链接：[doctor_api](https://github.com/dTIris/code_library/tree/master/doctor_api)
* 时间：2019-01-14
* 描述：提供后台给产品配置参数，将问题分配给医生回答
* 技术栈：使用tornado做web框架，json模块进行解析压缩数据包

### 小游戏开发-成语填空（重构前）：

* 链接：[wcgame](https://github.com/dTIris/code_library/tree/master/wcgame)
* 时间：2019-06-15至2019-06-20
* 描述：根据成语等级和挖空个数随机生成成语布局
* 技术栈：用多重数组表示地图，使用numpy和random模块

### 数据监测系统

* 链接：[monitor](https://github.com/dTIris/code_library/tree/master/monitor)
* 时间：2019-01-30
* 描述：根据关键词去爬取搜索排名，保存并与前一天做对比后将结果发送邮件
* 技术栈：使用Selenium/webdriver+pyvirtualdisplay来模拟浏览器访问页面进行爬取

### 爬虫

* 链接：[spider_py](https://github.com/dTIris/code_library/tree/master/spider_py)
* 时间：2019-06-10
* 描述：爬取网页
* 技术栈：爬取网页并解析使用BeautifulSoup，requests模块，随机ua使用fake_useragent模块



### 数据文本处理，xml和json

* 链接：[data_type](https://github.com/dTIris/code_library/tree/master/data_type)
* 时间：2018-06至2019-07
* 描述：将数据根据要求制作成xml文件和json文件



## 设计模式

简单例子：[design_pattern](https://github.com/dTIris/code_library/tree/master/design_pattern)



## 创建型设计模式



#### 解决对象创建问题一般用[工厂模型](https://github.com/dTIris/code_library/blob/master/design_pattern/factory_model.py)

解决对象创建问题，解耦对象的创建和使用，包括工厂方法和抽象工厂

\- 简单工厂模式适用于需创建的对象较少，不会造成工厂方法中的业务逻辑太过复杂的情况下，而且用户只关心那种类型的实例被创建，并不关心其初始化过程时，比如多种数据库(MySQL/MongoDB)的实例，多种格式文件的解析器(XML/JSON)等。

\- 工厂方法模式继承了简单工厂模式的优点又有所改进，其不再通过一个工厂类来负责所有产品的创建，而是将具体创建工作交给相应的子类去做，这使得工厂方法模式可以允许系统能够更高效的扩展。实际应用中可以用来实现系统的日志系统等，比如具体的程序运行日志，网络日志，数据库日志等都可以用具体的工厂类来创建。。

\- 抽象工厂模式在工厂方法基础上扩展了工厂对多个产品创建的支持，更适合一些大型系统，比如系统中有多于一个的产品族，且这些产品族类的产品需实现同样的接口，像很多软件系统界面中不同主题下不同的按钮、文本框、字体等等。



## 结构型设计模式



装饰器模式：无需子类化扩展对象功能



## 行为型模式



#### 当对象间存在一对多关系时，会使用[观察者模型](https://github.com/dTIris/code_library/blob/master/design_pattern/observer_model.py)（Observer）用于对象发生改变的时候，观察者执行相应的动作，自动通知依赖它的对象。

### 优点：

1、观察者和被观察者是抽象耦合的。 

2、建立一套触发机制。

#### 缺点：

1、如果一个被观察者对象有很多的直接和间接的观察者的话，将所有的观察者都通知到会花费很多时间。

2、如果在观察者和观察目标之间有循环依赖的话，观察目标会触发它们之间进行循环调用，可能导致系统崩溃。

3、观察者模式没有相应的机制让观察者知道所观察的目标对象是怎么发生变化的，而仅仅只是知道观察目标发生了变化。



## 自然文本处理例子：

#### [text_processing](https://github.com/dTIris/code_library/tree/master/text_processing)

该NLP 任务为：

* 读取文件；
* 去除所有标点符号和换行符，并把所有大写变成小写；
* 合并相同的词，统计每个词出现的频率，并按照词频从大到小排序；
*  将结果按行输出到文件 out.txt。

如果是小文件，则可参照[演示1](https://github.com/dTIris/code_library/blob/master/text_processing/demo1.py)

大文件或未知大小的文件的读取，需按行或按字节数来读取，参照[演示1-2](https://github.com/dTIris/code_library/blob/master/text_processing/demo1-2.py)