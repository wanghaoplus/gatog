# -*- coding: utf-8 -*-
# @Time    : 2020/02/26 16:14
# @Author  : wangdelei
# @Site    : 
# @File    : BF_FieldTest_Car_0001.py
# @Software: PyCharm
from aw.LbsTestCase import LbsTestCase
import time
from aw.core.Input import *
import threading

class BF_FieldTest_Car_0001(LbsTestCase):

    def __init__(self):
        super(BF_FieldTest_Car_0001, self).__init__()
        self.TestCaseList = ["BF_FieldTest_Car_0001"]

    def setup(self):
        self.setupStep('labsat')
        super(BF_FieldTest_Car_0001, self).setup()
        self.aw_initLabsat()
        loopTimes = self.data.LoopTimes
        sceneId = self.data.sceneId
        print(self.sceneData)
        
        
    def BF_FieldTest_Car_0001(self):
        self.testStep("开始测试")
        
        self.testStep("labsat开始播放场景")
        self.labsat.aw_labsatPlay(self.sceneData["fileName"], self.sceneData['startTime'], self.sceneData['duarTime'])
        
        self.testStep('发起冷启动定位')
        self.assertSuc(self.lbs.aw_startLocation('cold'))
        
        self.testStep('检查60s内定位成功')
        self.lbs.aw_checkLocationSuccess(60)
        
        self.testStep("labsat开始播放场景")
        self.labsat.aw_labsatPlay(self.sceneData["fileName"], self.sceneData['startTime'], self.sceneData['duarTime'])
        time.sleep(self.sceneData['duarTime'])
        
        self.testStep("labsat停止播放场景")
        self.labsat.aw_labsatStopPlay()
        print(self.sceneData['utcStartTime'], self.sceneData['utcEndTime'])
        
        self.testStep("停止数据录入")
        self.lbs.aw_stopReadPort()
        
        self.testStep("开始分析数据")
        self.lbs.aw_nmeanalysis(self.sceneData['utcStartTime'], self.sceneData['utcEndTime'], sceneId=self.sceneData['sceneId'])
        
        
    def teardown(self):
        self.teardownStep("ֹͣ测试结束")