#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aw.LbsTestCase import LbsTestCase
from aw.utils.kpireport.CnrLinearityReport import CnrLinearityReport


class BF_CNR_linearity_L1L5_0001(LbsTestCase):

    def __init__(self):
        super(BF_CNR_linearity_L1L5_0001, self).__init__()
        self.TestCaseList = ["BF_CNR_linearity_L1L5_0001"]

    def setup(self):
        super(BF_CNR_linearity_L1L5_0001, self).setup()
        self.sceneFile = r'D:\posapp\Scenarios\Test Case\TestCase_For_Report\Statics_ALL_L1L5\Statics_ALL_L1L5.scn'
        self.dbm = -120
        self.endDBM = -165
        
        self.setupStep('6700设备初始化')
        self.assertSuc(self.aw_initGss7000())
        
        self.setupStep("选择要播放场景")
        self.assertSuc(self.gss7000.aw_GSS7000SelectScenario(self.sceneFile))
        
        self.setupStep("开始播放场景")
        self.assertSuc(self.gss7000.aw_GSS7000RunScenario())
        
    def BF_CNR_linearity_L1L5_0001(self):
        
        while self.dbm > self.endDBM:
            self.testStep('模拟器信号设置 %sdBm' % str(self.dbm))
            self.assertSuc(self.gss7000.aw_Gss7000SetSignalLevel(self.dbm))
            
            startTime = self.assertSuc(self.gss7000.aw_GSS7000GetCurrentTime())
            
            self.testStep('等待2min')
            self.sleep(120)
            
            endTime = self.assertSuc(self.gss7000.aw_GSS7000GetCurrentTime())
            
            self.testStep('记录测试信息')
            CnrLinearityReport.getInstance().aw_writeRow([self.dbm, startTime, endTime])
            
            self.testStep('信号衰减1db')
            self.dbm -= 1
        
        self.testStep('停止读取nmea信息')
        self.assertSuc(self.lbs.aw_stopReadPort())

        self.testStep("7000停止播放")
        self.gss7000.aw_GSS7000EndScenario()
        
        self.testStep('测试结果分析')
        CnrLinearityReport.getInstance().aw_calculateKPI()
        
    def teardown(self):
        super(BF_CNR_linearity_L1L5_0001, self).teardown()
        self.teardownStep("7000停止播放")
        self.gss7000.aw_GSS7000EndScenario()
        
