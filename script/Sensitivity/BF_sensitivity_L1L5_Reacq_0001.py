# !/usr/bin/env python
# -*- coding: utf-8 -*-
from aw.LbsTestCase import FAIL
from aw.LbsTestCase import SUC
from aw.LbsTestCase import LbsTestCase
from aw.core.Input import getCurCaseName
from aw.utils.kpireport.SensitivityReport import SensitivityReport


class BF_sensitivity_L1L5_Reacq_0001(LbsTestCase):

    def __init__(self):
        super(BF_sensitivity_L1L5_Reacq_0001, self).__init__()
        self.TestCaseList = ["BF_sensitivity_L1L5_Reacq_0001"]

    def setup(self):
        super(BF_sensitivity_L1L5_Reacq_0001, self).setup()
        self.sceneFile = r'D:\posapp\Scenarios\Test Case\TestCase_For_Report\Statics_ALL_L1L5\Statics_ALL_L1L5.scn'
        self.latRef = 40
        self.lonRef = 116
        self.altRef = 100
        self.threshold = 60
        
        self.setupStep('6700设备初始化')
        self.assertSuc(self.aw_initGss7000())
        
        self.setupStep("选择要播放场景")
        self.assertSuc(self.gss7000.aw_GSS7000SelectScenario(self.sceneFile))
         
        self.setupStep("开始播放场景")
        self.assertSuc(self.gss7000.aw_GSS7000RunScenario())
        
    def BF_sensitivity_L1L5_Reacq_0001(self):
        resultHdbdDict = {}  # 北斗办标准测试结果
        resultDict = {}  # 非北斗办标准测试结果
        curDBM = -130
        stepDBM = 1
        
        self.testStep('模拟器信号设置 %sdBm' % str(curDBM))
        self.assertSuc(self.gss7000.aw_Gss7000SetSignalLevel(curDBM))
        
        self.testStep('获取当前时间')
        self.assertSuc(self.lbs.aw_getStartTTFFFromPC())
        
        self.testStep('定位成功后等待120s')
        self.assertSuc(self.lbs.aw_checkLocationSuccess(300))
        self.sleep(120)
         
        self.testStep('获取ttff')
        ttffDict = self.lbs.aw_calculateTTFF()[1]
        lastTestData = {'ttff':ttffDict, 'dbm':curDBM}
        
        while True:
            self.testStep('关闭信号输出')
            self.assertSuc(self.vam.aw_muteMultiChannel(True))
            
            self.testStep('重置测试数据')
            self.assertSuc(self.lbs.aw_resetTestData())
             
            self.testStep('检查是否失去定位')
            self.assertSuc(self.lbs.aw_checkLocationFail(120))
            
            self.testStep('将信号衰减1db，模拟器信号设置 %sdBm' % str(curDBM))
            curDBM -= stepDBM
            self.assertSuc(self.gss7000.aw_Gss7000SetSignalLevel(curDBM))
            
            self.testStep('重置测试数据')
            self.assertSuc(self.lbs.aw_resetTestData())
            
            self.testStep('打开信号输出')
            self.assertSuc(self.vam.aw_muteMultiChannel(False))
            
            self.testStep('获取当前时间')
            self.assertSuc(self.lbs.aw_getStartTTFFFromPC())
             
            self.testStep('检查60s内定位成功')
            locStatu, locRet = self.lbs.aw_checkLocationSuccess(60)
             
            self.testStep('获取ttff')
            ttffDict = self.lbs.aw_calculateTTFF()[1]
            
            if locStatu == FAIL:
                for device in locRet:
                    if device not in resultHdbdDict:
                        ttff = lastTestData.get('ttff', {}).get(device, -1)
                        dbm = lastTestData.get('dbm')
                        resultHdbdDict[device] = {'ttff':ttff, 'dbm':dbm}
                        dataList = [device, getCurCaseName(), ttff, dbm]
                        SensitivityReport.getInstance().aw_writeRow('HdbdStandard', dataList)
                    if device not in resultDict:
                        ttff = lastTestData.get('ttff', {}).get(device, -1)
                        dbm = lastTestData.get('dbm')
                        resultDict[device] = {'ttff':ttff, 'dbm':dbm}
                        dataList = [device, getCurCaseName(), ttff, dbm]
                        SensitivityReport.getInstance().aw_writeRow('GeneralStandard', dataList)
            for _ in range(10):
                self.sleep(1)
                cepDict = self.lbs.aw_calculateCurrentCep(self.latRef, self.lonRef, self.altRef, '2D')[1]
                cepStatu, failCepDict = self.lbs.aw_checkCepTtffStandard(cepDict, self.threshold)
                if cepStatu == SUC:
                    continue
                else:
                    for device, cep in failCepDict.items():
                        if device not in resultHdbdDict:
                            ttff = lastTestData.get('ttff', {}).get(device, -1)
                            dbm = lastTestData.get('dbm')
                            resultHdbdDict[device] = {'ttff':ttff, 'dbm':dbm}
                            dataList = [device, getCurCaseName(), ttff, dbm]
                            SensitivityReport.getInstance().aw_writeRow('HdbdStandard', dataList)
                            
            lastTestData = {'ttff':ttffDict, 'dbm':curDBM}
            
            self.testStep('检查是否所有设备都已经失败')
            if len(resultDict) == len(self.lbs.deviceList):
                break
            
        self.testStep('停止读取nmea信息')
        self.assertSuc(self.lbs.aw_stopReadPort())
        
    def teardown(self):
        super(BF_sensitivity_L1L5_Reacq_0001, self).teardown()
        self.teardownStep("6700停止播放")
        self.gss7000.aw_GSS7000EndScenario()
        
