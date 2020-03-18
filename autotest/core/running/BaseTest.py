#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/1 16:41
# @Author  : shaochanghong
# @Site    : 
# @File    : BaseTest.py
# @Software: PyCharm


class BaseTestModel(object):
    ModelType = 'Model'

    def start(self):
        pass

    def end(self):
        pass

    def reportError(self):
        pass


class BaseTestCase(BaseTestModel):
    ModelType = 'Case'

    def INIT(self):
        pass

    def setupStart(self):
        pass

    def setup(self):
        pass

    def setupEnd(self):
        pass

    def teardownStart(self):
        pass

    def teardown(self):
        pass

    def teardownEnd(self):
        pass

    def testStart(self):
        pass

    def test(self):
        pass

    def testEnd(self):
        pass


class BaseTestSuit(BaseTestModel):
    ModelType = 'Suit'

    def suitUpdateStart(self):
        pass


class BaseTestProject(BaseTestModel):
    ModelType = 'Project'

    def setupStart(self):
        pass

    def setup(self):
        pass

    def setupEnd(self):
        pass

    def teardownStart(self):
        pass

    def teardown(self):
        pass

    def teardownEnd(self):
        pass

    def init(self):
        pass

    def run(self):
        pass
