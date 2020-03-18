#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/8/4 22:07
# @Author  : shaochanghong
# @Site    : 
# @File    : test.py
# @Software: PyCharm

# robot/libdoc.py : 自带的文档生成工具，用于生成api文档
import socket

# client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client.connect(('127.0.0.1', 8100))
# client.send(b'')
# client.close()

try:
    a = __import__('utils.AutoSocket', fromlist=['AutoSocket'])
    a = getattr(a, 'AutoSocketClient', None)
except ImportError:
    print('hh')


class A():
    TEST = 1
    class B(object):
        LOOP = 1
    def say(self):
        pass

for i in range(1,1):
    print('HHHHHHHHHHHHH')
print(a.__name__, a.__module__)
print(A().say.__name__)
print('a'.__dict__)
print(isinstance(A, type), isinstance('', type))