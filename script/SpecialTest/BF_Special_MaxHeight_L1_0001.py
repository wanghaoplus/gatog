#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/3 23:37
# @Author  : shaochanghong
# @Site    : 
# @File    : BF_Special_MaxSpeed_L1_0001.py
# @Software: PyCharm
from aw.LbsTestCase import LbsTestCase


class BF_Special_MaxSpeed_L1_0001(LbsTestCase):

    def __init__(self):
        super(BF_Special_MaxSpeed_L1_0001, self).__init__()
        self.TestCaseList = ["BF_Special_MaxSpeed_L1_0001"]

    def setup(self):
        super(BF_Special_MaxSpeed_L1_0001, self).setup()
        self.sceneFile = r'D:\posapp\Scenarios\Test Case\TestCase_For_Report\maxheight_L1\maxheight_L1.scn'
        self.sceneId = 'maxheight_L1'
        self.maxHeight = 18000
        
        self.setupStep('7000设备初始化')
        self.assertSuc(self.aw_initGss7000())
        
        self.setupStep("选择要播放场景")
        self.assertSuc(self.gss7000.aw_GSS7000SelectScenario(self.sceneFile))
        
        self.setupStep("开始播放场景")
        self.assertSuc(self.gss7000.aw_GSS7000RunScenario())
        
    def BF_Special_MaxSpeed_L1_0001(self):
        self.testStep("将信号调节到-130dbm")
        self.assertSuc(self.gss7000.aw_Gss7000SetSignalLevel(-130))
        
        self.testStep("等待场景运行到xxs")
        self.assertSuc(self.gss7000.aw_GSS7000Wait2Time(1000))
        
        self.testStep("停止读取nmea信息")
        self.assertSuc(self.lbs.aw_stopReadPort())
        
        self.testStep("7000停止播放")
        self.gss7000.aw_GSS7000EndScenario()
        
        self.testStep("获取7000模拟器标准nmea文件")
        self.assertSuc(self.gss7000.aw_GSS7000GetStandardNMEA(self.sceneId))
        
        self.checkPoint("最大支持是否到18000m，超过18000m检查是否失去定位")
        self.assertSuc(self.lbs.aw_checkMaxAltitude(self.maxHeight))

    def teardown(self):
        super(BF_Special_MaxSpeed_L1_0001, self).teardown()
        self.teardownStep("7000停止播放")
        self.gss7000.aw_GSS7000EndScenario()
        
