#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/1 17:41
# @Author  : shaochanghong
# @Site    : 
# @File    : AnalyseConfig.py
# @Software: PyCharm
from autotest.core.conf.ProjectConfig import ProjectConfig
from autotest.core.conf.CaseConfig import CaseConfig
from autotest.core.conf.GroupTestCase import GroupTestCase


def initProjectReportPath():
    ProjectConfig().initReportPath()


def parseProjectSetting():
    ProjectConfig().parseProjectConfig()


def parseScriptConfig(scriptModule):
    CaseConfig.parseScriptConfig(scriptModule)


def getRunCases():
    CaseConfig.getScriptFromProjectSetting()
    

def groupTestCase():
    GroupTestCase().groupTestCase()

    
def collectTestDevice():
    from autotest.core.conf.DeviceCollect import DeviceCollect
    DeviceCollect().collectTestDevice()
