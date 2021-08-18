#!usr/bin/dev python
# -*- coding:utf-8 -*-
# __author__ = Iris
# __create__ = 2021/07/16
# __update__ = 2021/07/16
# __desc__ = "工厂模式"

import abc

class Dog(object):
    def __repr__(self):
        return "汪汪汪"

class Cat(object):
    def __repr__(self):
        return "喵喵喵"

# 简单工厂模式：将所有动物的实例化封装在一起
class SimpleFactory(object):

    @staticmethod # 静态方法
    def buy_animal(name):
        if name == "Cat" or name == "cat":
            return Cat()
        if name == "Dog" or name == "dog":
            return Dog()

# 工厂模式:将简单工厂抽象出来成不同工厂，每个工厂对应生成自己的产品
# 用abc实现抽象基类，不可以被实例化
class NormalFactory(metaclass=abc.ABCMeta):
    # 子类必须实现以下方法，否则实例化子类时解释器要报错
    @abc.abstractmethod
    def buy_animal(self):
        pass

class CatFactory(NormalFactory):
    def buy_animal(self):
        return Cat()

class DogFactory(NormalFactory):
    def buy_animal(self):
        return Dog()

# 抽象工厂模式：让一个工厂可以生产同一类的多个产品
class AbstractFactory(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def buy_male(self):
        pass

    @abc.abstractmethod
    def bug_female(self):
        pass

class Cats(AbstractFactory):
    def buy_male(self):
        return Cat()

    def bug_female(self):
        return Cat()


class Dogs(AbstractFactory):
    def buy_male(self):
        return Dog()

    def bug_female(self):
        return Dog()

# 简单工厂模式实例化
def simple():
    cat = SimpleFactory().buy_animal("cat")
    dog = SimpleFactory().buy_animal("dog")
    print(cat)
    print(dog)

# 工厂模式实例化
def normal():
    cat = CatFactory().buy_animal()
    dog = DogFactory().buy_animal()
    print(cat)
    print(dog)

# 抽象工厂模式实例化
def abstract():
    cat1 = Cats().buy_male()
    cat2 = Cats().bug_female()
    dog1 = Dogs().buy_male()
    dog2 = Dogs().bug_female()
    print(cat1, cat2)
    print(dog1, dog2)

def main():
    # simple()
    # normal()
    abstract()

if __name__ == "__main__":
    main()