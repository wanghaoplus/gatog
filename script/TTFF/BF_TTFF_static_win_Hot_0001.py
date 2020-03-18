#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from aw.LbsTestCase import LbsTestCase


class BF_TTFF_static_win_Hot_0001(LbsTestCase):

    def __init__(self):
        super(BF_TTFF_static_win_Hot_0001, self).__init__()
        self.TestCaseList = ["BF_TTFF_static_win_Hot_0001"]

    def setup(self):
        super(BF_TTFF_static_win_Hot_0001, self).setup()
        self.latRef = 22.6325521803272
        self.lonRef = 114.064212917882
        self.altRef = 94.6353411981836
        
    def BF_TTFF_static_win_Hot_0001(self):
        testStartTime = self.assertSuc(self.lbs.aw_getUTCtime())
        for loopId in range(1, 101):
            self.testStep('第%s次循环' % loopId)
            
            self.testStep('发起冷启动定位')
            self.assertSuc(self.lbs.aw_startLocation('cold'))
            
            self.testStep('检查60s内定位成功')
            self.lbs.aw_checkLocationSuccess(60)
            
            self.testStep('随机等待1-30秒')
            self.sleep(minTime=1,maxTime=30)
            
            self.testStep('重置测试数据')
            self.lbs.aw_resetTestData()
            
        self.testStep('停止读取nmea信息')
        self.assertSuc(self.lbs.aw_stopReadPort())
        
        self.testStep('测试结果分析')
        testEndTime = self.assertSuc(self.lbs.aw_getUTCtime())
        
        from aw.utils.kpireport.SingleReport import SingleReport
        SingleReport.getInstance().calculateCepTTFFKPI(self.latRef, self.lonRef, self.altRef)
        self.lbs.aw_nmeanalysis(testStartTime, testEndTime,lonRef=self.lonRef, latRef=self.latRef, altRef=self.altRef)
        
    def teardown(self):
        super(BF_TTFF_static_win_Hot_0001, self).teardown()
        
