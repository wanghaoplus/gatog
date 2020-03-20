#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/03/20 17:00
# @Author  : wanghao
# @Site    : 
# @File    : Test_003_longtime.py
# @Software: VSCode

from aw.LbsTestCase import LbsTestCase

class Test_003_longtime(LbsTestCase):

    def __init__(self):
        super(Test_003_longtime, self).__init__()
        self.TestCaseList = ["Test_003_longtime"]

    def setup(self):
        super(Test_003_longtime, self).setup()
        self.lat = 39.9633233333333
        self.lon = 116.317156666667
        self.hgt = 96.8593729287386

        
    def Test_003_longtime(self):
        self.testStep('发起冷启动定位')
        self.assertSuc(self.lbs.aw_startLocation('hot'))
        
        self.sleep(200)

        self.testStep('停止读取nmea信息')
        self.assertSuc(self.lbs.aw_stopReadPort())

        self.testStep('测试结果分析')

        self.sceneData['utcEndTime'] = self.sceneData['utcStartTime'] + 200
        self.lbs.aw_nmeanalysis( self.sceneData['utcStartTime'], self.sceneData['utcEndTime'], None, self.lon, self.lat, self.hgt)
    def teardown(self):
        super(Test_003_longtime, self).teardown()
        
    