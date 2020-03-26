# !/usr/bin/env python
# -*- coding: utf-8 -*-
from aw.LbsTestCase import FAIL
from aw.LbsTestCase import SUC
from aw.LbsTestCase import LbsTestCase
from aw.core.Input import getCurCaseName
from aw.utils.kpireport.SensitivityReport import SensitivityReport


class BF_sensitivity_L1_Hot_0001(LbsTestCase):

    def __init__(self):
        super(BF_sensitivity_L1_Hot_0001, self).__init__()
        self.TestCaseList = ["BF_sensitivity_L1_Hot_0001"]

    def setup(self):
        super(BF_sensitivity_L1_Hot_0001, self).setup()
        self.sceneFile = r'D:\posapp\Scenarios\Test Case\TestCase_For_Report\Statics_ALL_L1\Statics_ALL_L1.scn'
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
        
        self.setupStep("发起冷启动定位，使芯片的utc切换到当前场景时间")
        self.assertSuc(self.lbs.aw_startLocation('cold', checkGGA=False))
        self.assertSuc(self.lbs.aw_checkLocationSuccess(300, recordData=False))
        
    def BF_sensitivity_L1_Hot_0001(self):
        resultHdbdDict = {}  # 北斗办标准测试结果
        resultDict = {}  # 非北斗办标准测试结果
        lastTestData = {}
        curDBM = -130
        
        self.testStep('模拟器信号设置 %sdBm' % str(curDBM))
        self.assertSuc(self.gss7000.aw_Gss7000SetSignalLevel(curDBM))
        
        self.testStep('定位成功后等待120s')
        self.assertSuc(self.lbs.aw_checkLocationSuccess(300))
        self.sleep(120)
        
        self.testStep('将信号衰减1db')
        curDBM -= 1
        
        while True:
            self.testStep('模拟器信号设置 %sdBm' % str(curDBM))
            self.assertSuc(self.gss7000.aw_Gss7000SetSignalLevel(curDBM))
            
            self.testStep('发起热启动定位')
            self.lbs.aw_startLocation('hot')
            
            self.testStep('检查120s内定位成功')
            locStatu, locRet = self.lbs.aw_checkLocationSuccess(120)
            
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
            
            self.testStep('将信号衰减1db')
            curDBM -= 1
            
            self.testStep('重置测试数据')
            self.lbs.aw_resetTestData()
            
        self.testStep('停止读取nmea信息')
        self.assertSuc(self.lbs.aw_stopReadPort())
        
    def teardown(self):
        super(BF_sensitivity_L1_Hot_0001, self).teardown()
        self.teardownStep("6700停止播放")
        self.gss7000.aw_GSS7000EndScenario()
        
