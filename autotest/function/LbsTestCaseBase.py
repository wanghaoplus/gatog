#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/20 22:45
# @Author  : shaochanghong
# @Site    : 
# @File    : LbsTestCaseBase.py
# @Software: PyCharm
from autotest.core.running.TestCase import TestCase
from autotest.core.running.Engine import SetupStep
from autotest.core.running.Engine import TestStep
from autotest.core.running.Engine import CheckPoint
from autotest.core.running.Engine import TeardownStep
from autotest.core.running.Engine import LoopTest
from autotest.core.modle.Variable import DEVICE


class LbsTestCaseBase(TestCase):
    androidList = []
    iosList = []
    hdbdList = []

    def __init__(self):
        super(LbsTestCaseBase, self).__init__()
        if "AndroidDevices" in DEVICE:
            self.androidList = DEVICE.AndroidDevices
        if "IosDevices" in DEVICE:
            self.iosList = DEVICE.IosDevices
        if "HdbdDevices" in DEVICE:
            self.hdbdList = DEVICE.HdbdDevices
        

    def setupStart(self):
        super(LbsTestCaseBase, self).setupStart()

    def setup(self):
        super(LbsTestCaseBase, self).setup()

    def setupEnd(self):
        super(LbsTestCaseBase, self).setupEnd()

    def testStart(self):
        super(LbsTestCaseBase, self).testStart()

    def testEnd(self):
        super(LbsTestCaseBase, self).testEnd()

    def teardownStart(self):
        super(LbsTestCaseBase, self).teardownStart()

    def teardown(self):
        super(LbsTestCaseBase, self).teardown()

    def teardownEnd(self):
        super(LbsTestCaseBase, self).teardownEnd()

    def setupStep(self, msg):
        SetupStep(msg)

    def testStep(self, msg):
        TestStep(msg)

    def teardownStep(self, msg):
        TeardownStep(msg)

    def checkPoint(self, msg):
        CheckPoint(msg)


if __name__ == '__main__':
    test = LbsTestCaseBase()
    test.setup()
