#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/03/07 12:00
# @Author  : wanghao
# @Site    : 
# @File    : BF_TTFF_static_130_L1L2_Hot_0001.py
# @Software: Eclipse
from aw.LbsTestCase import LbsTestCase


class BF_TTFF_static_130_L1L2_Hot_0001(LbsTestCase):

    def __init__(self):
        super(BF_TTFF_static_130_L1L2_Hot_0001, self).__init__()
        self.TestCaseList = ["BF_TTFF_static_130_L1L2_Hot_0001"]
        self.scenePath = ""
        
    def setup(self):
        super(BF_TTFF_static_130_L1L2_Hot_0001, self).setup()
        self.sceneFile = r'D:\posapp\Scenarios\Test Case\TestCase_For_Report\Statics_ALL_L1\Statics_ALL_L1.scn'
        self.latRef = 40
        self.lonRef = 116
        self.altRef = 100
        
        self.setupStep('7000设备初始化')
        self.assertSuc(self.aw_initGss7000())
        
        self.setupStep("选择要播放场景")
        self.assertSuc(self.gss7000.aw_GSS7000SelectScenario(self.sceneFile))
        
        self.setupStep("开始播放场景")
        self.assertSuc(self.gss7000.aw_GSS7000RunScenario())
        
        self.testStep('模拟器信号设置 -130dBm')
        self.assertSuc(self.gss7000.aw_Gss7000SetSignalLevel(-130))
        
        self.setupStep("发起冷启动定位，使芯片的utc切换到当前场景时间")
        self.assertSuc(self.lbs.aw_startLocation('cold', checkGGA=False))
        self.assertSuc(self.lbs.aw_checkLocationSuccess(300, recordData=False))
        
    def BF_TTFF_static_130_L1L2_Hot_0001(self):
        startTime = self.assertSuc(self.gss7000.aw_GSS7000GetStartTime())
        
        for loopId in range(1, 101):
            self.testStep('第%s次循环' % loopId)
            
            self.testStep('发起冷启动定位')
            self.assertSuc(self.lbs.aw_startLocation('hot'))
            
            self.testStep('检查60s内定位成功')
            self.lbs.aw_checkLocationSuccess(60)
            
            self.testStep('重置测试数据')
            self.lbs.aw_resetTestData()
            
        endTime = self.assertSuc(self.gss7000.aw_GSS7000GetCurrentTime())
            
        self.testStep("7000停止播放")
        self.gss7000.aw_GSS7000EndScenario()
            
        self.testStep('停止读取nmea信息')
        self.assertSuc(self.lbs.aw_stopReadPort())
        
        self.testStep('测试结果分析')
        self.lbs.aw_nmeanalysis(startTime, endTime, None, self.lonRef, self.latRef, self.altRef)
        
    def teardown(self):
        super(BF_TTFF_static_130_L1L2_Hot_0001, self).teardown()
        self.teardownStep("7000停止播放")
        self.gss7000.aw_GSS7000EndScenario()
        
