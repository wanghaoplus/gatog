#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/03/07 21:00
# @Author  : wanghao
# @Site    : 
# @File    : BF_dynamic_140_Cricle_1g_1000m_L1L5_0001.py
# @Software: Eclipse
from aw.LbsTestCase import LbsTestCase


class BF_dynamic_140_Cricle_1g_1000m_L1L5_0001(LbsTestCase):

    def __init__(self):
        super(BF_dynamic_140_Cricle_1g_1000m_L1L5_0001, self).__init__()
        self.TestCaseList = ["BF_dynamic_140_Cricle_1g_1000m_L1L5_0001"]
        self.scenePath = ""

    def setup(self):
        super(BF_dynamic_140_Cricle_1g_1000m_L1L5_0001, self).setup()
        self.sceneFile = r'D:\posapp\Scenarios\Test Case\TestCase_For_Report\circle_1g_radius_1000m_ALL_L1L5\circle_1g_radius_1000m_ALL_L1L5.scn'
        self.sceneId = 'circle_1g_radius_1000m_ALL_L1L5'
        
        self.setupStep('7000设备初始化')
        self.assertSuc(self.aw_initGss7000())
        
        self.setupStep("选择要播放场景")
        self.assertSuc(self.gss7000.aw_GSS7000SelectScenario(self.sceneFile))
        
        self.setupStep("开始播放场景")
        self.assertSuc(self.gss7000.aw_GSS7000RunScenario())
        
        self.testStep('模拟器信号设置 -140dBm')
        self.assertSuc(self.gss7000.aw_Gss7000SetSignalLevel(-140))
        
    def BF_dynamic_140_Cricle_1g_1000m_L1L5_0001(self):
        startTime = self.assertSuc(self.gss7000.aw_GSS7000GetStartTime())

        self.testStep('发起冷启动定位')
        self.assertSuc(self.lbs.aw_startLocation('cold'))

        self.testStep('检查60s内定位成功')
        self.lbs.aw_checkLocationSuccess(300, True)

        self.testStep('获取场景运行时长')
        sleepTime = self.assertSuc(self.gss7000.aw_GSS7000GetScenarioDuration())

        self.testStep('场景运行时长%d秒' % sleepTime)
        self.sleep(sleepTime)

        endTime = self.assertSuc(self.gss7000.aw_GSS7000GetCurrentTime())

        self.testStep("7000停止播放")
        self.gss7000.aw_GSS7000EndScenario()

        self.testStep('停止读取nmea信息')
        self.assertSuc(self.lbs.aw_stopReadPort())

        self.testStep("获取7000模拟器标准nmea文件")
        novatel = self.assertSuc(self.gss7000.aw_GSS7000GetStandardNMEA(self.sceneId))

        self.testStep('测试结果分析')
        self.lbs.aw_nmeanalysis(startTime, endTime, fileName=novatel)
    def teardown(self):
        super(BF_dynamic_140_Cricle_1g_1000m_L1L5_0001, self).teardown()
        self.teardownStep("7000停止播放")
        self.gss7000.aw_GSS7000EndScenario()
        
