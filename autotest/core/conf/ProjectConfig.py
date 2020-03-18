#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/1 17:42
# @Author  : shaochanghong
# @Site    : 
# @File    : ProjectConfig.py
# @Software: PyCharm
import os
import json
from autotest.core.modle.Variable import VAR
from autotest.core.modle.Variable import DEVICE
from autotest.core.modle.CustomException import NoProjectConfigException
from autotest.core.modle.CustomException import ErrorConfigException
from autotest.utils.Decorator import singleton


@singleton
class ProjectConfig(object):
    RUN_MODE_LIST = [0, 1]

    def __init__(self):
        self.config = self.readConfig

    @property
    def readConfig(self):
        projectPath = os.path.join(VAR.CurProject.RootPath, 'projectconfig.json')
        if os.path.exists(projectPath):
            with open(projectPath, 'r') as projectFileObj:
                config = json.load(projectFileObj)
            return config
        else:
            raise NoProjectConfigException('has no project config file.')

    def initReportPath(self):
        reportPath = self.config.get('reportPath')
        if reportPath is not None:
            try:
                if not os.path.exists(reportPath):
                    os.makedirs(reportPath)
                VAR.CurProject.ReportRootPath = reportPath
            except:
                raise ErrorConfigException('project report path config error.')

    def initLoopTimes(self):
        try:
            loopTimes = int(self.config.get('loopTimes', 1))
            if 0 != loopTimes:
                VAR.CurProject.LoopTimes = loopTimes
        except:
            raise ErrorConfigException('project looptimes config error.')

    def initRunMode(self):
        runMode = int(self.config.get('runMode', 0))
        if runMode not in self.RUN_MODE_LIST:
            raise ErrorConfigException('project runMode config error.')
        else:
            VAR.CurProject.RunMode = runMode
            
    def initGroupCaseEnable(self):
        groupCaseEnable = self.config.get('isGroupCase', 'true')
        VAR.CurProject.GroupCaseEnable = groupCaseEnable
        
    def initHandleDevice(self):
        isHandleDevice = self.config.get('isHandleDevice', 'true')
        VAR.CurProject.IsHandleDevice = isHandleDevice

    def initDevices(self):
        devices = self.config.get('devices', {})
        if devices:
            enable = devices.get('enable', "true")
            if "true" != enable.lower():
                return
            androidDevices = devices.get('AndroidDevices', [])
            iosDevices = devices.get('IosDevices', [])
            testDevices = devices.get('TestDevices', [])
            if len(androidDevices) == 0 and len(iosDevices) == 0 and len(testDevices) == 0:
                raise ErrorConfigException('not found any device in project config, please check.')
            self.initAndroidDevices(androidDevices)
            self.initIosDevices(iosDevices)
            self.initTestDevice(testDevices)

    def initAndroidDevices(self, deviceList):
        if deviceList:
            DEVICE.addNode('AndroidDevices')
            DEVICE.AndroidDevices = deviceList

    def initIosDevices(self, deviceList):
        if deviceList:
            DEVICE.addNode('IosDevices')
            DEVICE.IosDevices = deviceList

    def initTestDevice(self, deviceList):
        if deviceList:
            DEVICE.addNode('TestDevices')
            DEVICE.TestDevices = deviceList
    
    def initInstrument(self):
        from autotest.core.modle.Variable import INSTRUMENT
        instruments = self.config.get('Instruments', {})
        for key, value in instruments.items():
            INSTRUMENT[key] = value

    def parseProjectConfig(self):
        self.initReportPath()
        self.initLoopTimes()
        self.initRunMode()
        self.initGroupCaseEnable()
        self.initHandleDevice()
        self.initDevices()
        self.initInstrument()


if __name__ == "__main__":
    config = ProjectConfig()
    config.parseProjectConfig()
    print(DEVICE)
    print(VAR, len(VAR))
