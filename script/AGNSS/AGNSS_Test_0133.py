# -*- coding: utf-8 -*-
# @Time    : 2020/02/21 22:14
# @Author  : wangdelei
# @Site    : 
# @File    : AGNSS_Test_0133.py
# @Software: PyCharm
from aw.LbsTestCase import LbsTestCase
import time
from aw.core.Input import *
import threading

class AGNSS_Test_0133(LbsTestCase):

    def __init__(self):
        super(AGNSS_Test_0133, self).__init__()
        self.TestCaseList = ["AGNSS_Test_0133"]

    def setup(self):
        self.setupStep('labsat')
        super(AGNSS_Test_0133, self).setup()
        self.aw_initLabsat()
        loopTimes = self.data.LoopTimes
        sceneId = self.data.sceneId
        print(self.sceneData)
        
        
    def AGNSS_Test_0133(self):
        self.testStep("开始测试")
        self.testStep("播放labsat场景")
        self.labsat.aw_labsatPlay(self.sceneData["fileName"], self.sceneData['startTime'], self.sceneData['duarTime'])
        
        
        time.sleep(self.sceneData['duarTime'])
        
        self.testStep("停止labsat播放")
        self.labsat.aw_labsatStopPlay()
        
        self.testStep("停止串口读取")
        self.lbs.aw_stopReadPort()
        
        self.testStep("分析Nmea数据")
        self.lbs.aw_nmeanalysis(self.sceneData['utcStartTime'], self.sceneData['utcEndTime'], sceneId=self.sceneData['sceneId'])
        
        
    def teardown(self):
        self.teardownStep("ֹͣ测试结束")