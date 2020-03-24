#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/3 23:41
# @Author  : shaochanghong
# @Site    : 
# @File    : LbsTestCase.py
# @Software: PyCharm
import time
from aw.core.Input import LoopTest
from aw.core.Input import SUC
from aw.core.Input import FAIL
from aw.core.Input import PRINTTRAC
from aw.core.Input import PRINTI
from aw.core.Input import LBSException
from aw.core.Input import LbsTestCaseBase
from aw.core.Input import getInstruments
from aw.devices.LbsManager import LbsManager
from aw.utils.scenemanager.SceneManager import SceneManager
from aw.utils.reportarchive.ReportArchive import ReportArchive
from aw.core.Input import getCurCaseConfig


class LbsTestCase(LbsTestCaseBase):
    
    def __init__(self):
        super(LbsTestCase, self).__init__()
        self.lbs = None
        self.labsat = None
        self.gss7000 = None
        self.sceneData = {}

    def setup(self):
        super(LbsTestCase, self).setup()
        self.lbs = LbsManager()
    
    def aw_initLabsat(self):
        from aw.instruments.labsat.Labsat import GssLabsat
        try:
            instruments = getInstruments()
            labsatDict = instruments.get('Labsat')
            labsatType = labsatDict.get('type')
            labsatIp = labsatDict.get('ip')
            self.labsat = GssLabsat(labsatType + '_' + labsatIp)
            PRINTI('labsat初始化成功')
        except:
            PRINTTRAC('请检查工程配置文件project.json中，labsat配置是否正确')
            return FAIL, 'labsat初始化失败'
         
        PRINTI('检查场景是否在labsat中，如果没有，则将场景拷贝到labsat中')
        labsatPath = r'\\{}\Scenarios'.format(labsatIp)
        self.sence = SceneManager()
        self.sceneData = self.assertSuc(self.sence.aw_copySceneFromSerevr2Labsat(self.data.sceneId, labsatPath))
        
    def aw_initGss7000(self):
        from aw.instruments.gss7000.GSS7000 import GSS7000
        try:
            instruments = getInstruments()
            gss7000Dict = instruments.get('Gss7000')
            gss7000Ip = gss7000Dict.get('ip')
            self.gss7000 = GSS7000(gss7000Ip)
            return SUC, 'gss7000初始化成功'
        except:
            PRINTTRAC('请检查工程配置文件project.json中，gss7000配置是否正确')
            return FAIL, 'gss7000初始化失败'

    def teardown(self):
        super(LbsTestCase, self).teardown()
        self.lbs.aw_stopReadPort()
        if getCurCaseConfig()['isArchive'].lower() == 'true':
            ReportArchive().copyLogToServer(week=self.lbs.deviceList[1]['week'])
        

    def setupStep(self, msg):
        super(LbsTestCase, self).setupStep(msg)

    def testStep(self, msg):
        super(LbsTestCase, self).testStep(msg)

    def teardownStep(self, msg):
        super(LbsTestCase, self).teardownStep(msg)

    def checkPoint(self, msg):
        super(LbsTestCase, self).checkPoint(msg)

    def sleep(self, sleepTime=None,minTime=None,maxTime=None):
        if sleepTime is not None:
            time.sleep(sleepTime)
        elif minTime and maxTime:
            import random
            time.sleep(random.randrange(minTime,maxTime))
        else:
            time.sleep(1)

    def assertSuc(self, ret):
        if ret[0] == FAIL:
            raise LBSException("expect success,but fail.")
        return ret[1]

    def assertFail(self, ret):
        if ret[0] == SUC:
            raise LBSException("expect fail,but success.")
        return ret[1]
    
