#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/3 23:37
# @Author  : shaochanghong
# @Site    : 
# @File    : Test_001.py
# @Software: PyCharm
import time
from aw.LbsTestCase import LbsTestCase, LoopTest
from numpy import append


class Test_001(LbsTestCase):

    def __init__(self):
        super(Test_001, self).__init__()
        self.TestCaseList = ["Test_001"]

    def setup(self):
        super(Test_001, self).setup()
        self.setupStep('初始化')
        pass
#         self.sceneId = self.data.scene
#         self.setupStep('初始化labsat')
#         self.aw_initLabsat()
        
    def Test_001(self):
        
        result_cep_list = []
        result_ttff_list = {}
        start_time = time.time()
        for i in range(100):
            self.testStep("发起冷启动定位")
            self.lbs.aw_startLocation(mode='cold', timeout=20)   
            #self.sleep(90)
            
            self.testStep("获取是否定位成功")
            self.lbs.aw_checkLocationSuccess(timeout=120)
            
            self.testStep("获取ttff")
            ret1 = self.assertSuc(self.lbs.aw_calculateTTFF())
            result_ttff_list.append(ret1) 
            
            ret2 = self.assertSuc(self.lbs.aw_calculateFisrtLocationCep(latRef = 22.632462653 , lonRef = 114.063707467))
            result_cep_list.append(ret2) 
            ret3 = self.assertSuc(self.lbs.aw_calculateCurrentCep(latRef = 22.632462653 , lonRef = 114.063707467))
            time.sleep(10)
            
        self.sceneData['utcEndTime'] = self.sceneData['utcStartTime'] + (time.time() - start_time)
        self.lbs.aw_nmeanalysis(self.sceneData['utcStartTime'], self.sceneData['utcEndTime'], self.sceneData["fileName"], self.sceneData['sceneId'])
        
        
#             result_list.append(ret3)

    def teardown(self):
        self.teardownStep("停止播放")
#         self.labsat.aw_labsatStopPlay()
