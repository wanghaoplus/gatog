# !/usr/bin/env python
# -*- coding: utf-8 -*-
from aw.LbsTestCase import FAIL
from aw.LbsTestCase import SUC
from aw.LbsTestCase import LbsTestCase


class GSS6700_Test_Demo(LbsTestCase):

    def __init__(self):
        super(GSS6700_Test_Demo, self).__init__()
        self.TestCaseList = ["GSS6700_Test_Demo"]

    def setup(self):
        self.sceneId = self.data.sceneId
        self.latRef = ''
        self.lonRef = ''
        self.threshold = 20
        
        self.setupStep('6700设备初始化')
        self.assertSuc(self.aw_initGss7000())
        
        self.setupStep("选择要播放场景")
        self.assertSuc(self.gss7000.aw_GSS7000SelectScenario(self.sceneId))
        
        self.setupStep("开始播放场景")
        self.assertSuc(self.gss7000.aw_GSS7000RunScenario())
        
    def GSS6700_Test_Demo(self):
        resultDict = {}
        curDBM = -130
        while True:
            self.testStep('模拟器信号设置 %sdBm' % str(curDBM))
            self.assertSuc(self.gss7000.aw_GSS7000SetRefLev(curDBM))
            
            self.testStep('发起冷启动定位')
            self.assertSuc(self.lbs.aw_startLocation('cold'))
            
            self.testStep('检查300s内定位成功')
            locStatu, locRet = self.lbs.aw_checkLocationSuccess(300)
            if locStatu == SUC:
                cepStatu, cepDict = self.lbs.aw_checkCepThreshold(self.latRef, self.lonRef, self.threshold)
                if cepStatu == SUC:
                    curDBM -= 1
                    continue
                for device, cep in cepDict.items():
                    if device not in resultDict:
                        resultDict[device] = cep
        
    def teardown(self):
        self.teardownStep("6700停止播放")
        self.gss7000.aw_GSS7000EndScenario()
        
