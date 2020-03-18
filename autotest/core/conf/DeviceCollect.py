#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/02/14 16:41
# @Author  : shaochanghong
# @Site    : 
# @File    : DeviceCollect.py
import os
import xlrd
from autotest.utils.Decorator import singleton
from autotest.core.modle.Variable import VAR
from autotest.core.modle.Variable import DEVICE
from autotest.core.modle.CustomException import CustomException


@singleton
class DeviceCollect(object):
    '''
    @summary: 查找满足执行条件的测试设备
    '''

    def __init__(self):
        self.__envSheet = None
    
    @property
    def envSheet(self):
        if self.__envSheet is None:
            self.__envSheet = self.openEnvConfigExcel()
        return self.__envSheet
    
    def openEnvConfigExcel(self):
        envExcelPath = os.path.join(VAR.CurProject.RootPath, 'resource', 'envconfig.xlsx')
        if os.path.exists(envExcelPath):
            raise FileNotFoundError('%s不存在' % envExcelPath)
        workBook = xlrd.open_workbook(envExcelPath)
        sheetObj = workBook.sheet_by_name('envconfig')
        return sheetObj
    
    def collectTestDevice(self):
        self.resetDevice()
        curCaseConfig = VAR.CurCase.Config
        hardwareDict = eval(curCaseConfig.HardwarePlatform)
        if not hardwareDict:
            raise CustomException('硬件平台信息配置错误')
        for hdVersion, valueDict in hardwareDict.items():
            for chipType, value1Dict in valueDict.items():
                for galaxy, value2Dict in value1Dict.items():
                    deviceCount = value2Dict.get('count', 1)
                    self.findTestDevice(hdVersion, chipType, galaxy, deviceCount)
        
    def findTestDevice(self, hdVersion, chipType, galaxy, deviceCount):
        if '没有找到可用设备':
            raise CustomException('没有找到可用设备：%s,%s,%s,%s' % (hdVersion, chipType, galaxy, deviceCount))
        device = {'ip':'', 'port':'', 'connectType':'socket', 'deviceType':'hdbd'}
        self.addTestDevice(device)
    
    def addTestDevice(self, device):
        if 'TestDevices' not in DEVICE:
            DEVICE['TestDevices'] = []
        DEVICE['TestDevices'].append(device)
        
    def resetDevice(self):
        if 'TestDevices' in DEVICE:
            DEVICE['TestDevices'].clear()
