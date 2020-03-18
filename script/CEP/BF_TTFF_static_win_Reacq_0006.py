#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from aw.LbsTestCase import LbsTestCase


class BF_TTFF_static_win_Reacq_0006(LbsTestCase):

    def __init__(self):
        super(BF_TTFF_static_win_Reacq_0006, self).__init__()
        self.TestCaseList = ["BF_TTFF_static_win_Reacq_0006"]

    def setup(self):
        super(BF_TTFF_static_win_Reacq_0006, self).setup()
        self.aw_initLabsat()
        loopTimes = self.data.LoopTimes
        sceneId = self.data.sceneId
        self.latRef = 22.6324465
        self.lonRef = 114.0637045
        self.altRef = 117.1
        
    def BF_TTFF_static_win_Reacq_0006(self):
        
        self.testStep("labsat开始播放场景")
        self.labsat.aw_labsatPlay(self.sceneData["fileName"], self.sceneData['startTime'], self.sceneData['duarTime'])
        
        for i in range(1, 31):
            
            self.testStep("下发RF off")
            self.labsat.aw_labsatMuteSet(True)
            self.sleep(2*60)
            
            self.testStep("下发RF on")
            self.labsat.aw_labsatMuteSet(False)
            startReaqUTC = time.time()
            
            self.testStep('检查60s内定位成功')
            self.lbs.aw_checkLocationSuccess(60)
            
            self.testStep('重置测试数据')
            self.lbs.aw_resetTestData()
            
        self.testStep('停止读取nmea信息')
        self.assertSuc(self.lbs.aw_stopReadPort())
        
        
        self.testStep("开始分析数据")
        self.lbs.aw_nmeanalysis(self.sceneData['utcStartTime'], self.sceneData['utcEndTime'], sceneId=self.sceneData['sceneId'], lonRef=self.lonRef, latRef=self.latRef, altRef=self.altRef)
        
    def teardown(self):
        super(BF_TTFF_static_win_Reacq_0006, self).teardown()
        
