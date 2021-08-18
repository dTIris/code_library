#!usr/bin/env python
# -*- coding:utf-8 -*-
# __author__ = Iris
# __create__ = 2021/07/14
# __update__ = 2021/07/14
# __desc__ = "观察者模式"

# 通知者基类
class Employer(object):
    def add_employee(self, class_):
        pass
    def del_employee(self, class_):
        pass
    def notify(self):
        pass

# 观察者基类
class Employee(object):
    def __init__(self, name=""):
        self.name = name

    def work(self):
        pass

# 通知者
class Boss(Employer):
    def __init__(self):
        self.employees = []

    def add_employee(self, class_):
        self.employees.append(class_)

    def del_employee(self, class_):
        print(class_.name, "已离职")
        self.employees.remove(class_)

    def notify(self):
        for item in self.employees:
            item.work()

# 观察者
class Cooker(Employee):
    def work(self):
        print(self.name, "-开始做饭")

class Waiter(Employee):
    def work(self):
        print(self.name, "-点菜")

class Cashier(Employee):
    def work(self):
        print(self.name, "-收银")

def main():
    boss = Boss()
    waiter1 = Waiter("花花")
    waiter2 = Waiter("娜娜")
    cook1 = Cooker("小何")
    cook2 = Cooker("小高")
    boss.add_employee(waiter1)
    boss.add_employee(waiter2)
    boss.add_employee(cook1)
    boss.add_employee(cook2)
    cashier = Cashier("阿发")
    boss.add_employee(cashier)
    boss.notify()
    boss.del_employee(cook2)
    boss.notify()

if __name__ == "__main__":
    main()