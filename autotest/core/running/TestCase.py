#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/2 20:23
# @Author  : shaochanghong
# @Site    : 
# @File    : TestCaseBase.py
# @Software: PyCharm
"""
测试用例基类，所有测试类的父类，其函数皆为空实现，子类可根据自己的业务重写每一个函数实现
"""
from autotest.core.running.BaseTest import BaseTestCase


class TestCase(BaseTestCase):

    def __init__(self):
        pass

    def setupStart(self):
        pass

    def setup(self):
        pass

    def setupEnd(self):
        pass

    def testStart(self):
        pass

    def testEnd(self):
        pass

    def teardownStart(self):
        pass

    def teardown(self):
        pass

    def teardownEnd(self):
        pass


if __name__ == '__main__':
    test = TestCase()
    test.setupStart()
    test.setupEnd()
    test.testStart()
    test.testEnd()
    test.teardownStart()
    test.teardownEnd()