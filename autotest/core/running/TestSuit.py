#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/2 23:28
# @Author  : shaochanghong
# @Site    : 
# @File    : TestSuit.py
# @Software: PyCharm
import random
from autotest.utils.Decorator import singleton
from autotest.core.modle.Variable import VAR
from autotest.core.running.BaseTest import BaseTestSuit
from autotest.core.running.TestRunner import TestRunner
from autotest.core.conf import AnalyseConfig
from autotest.core.logger.LogPrint import PRINTTRAC


@singleton
class TestSuit(BaseTestSuit):
    DEFAULT_LOOP_TIMES = 1

    def __init__(self):
        pass
    
    def runFixtureMode(self):
        '''
        @summary: 顺序执行
        @author: shaochanghong
        '''
        if VAR.CurProject.GroupCaseEnable.lower() == 'true':
            # 用例分组后执行逻辑
            for envType, testCaseDict in VAR.CurSuit.CaseDict.items():
                for sceneId, testCaseList in testCaseDict.items():
                    for case in testCaseList:
                        self._runCase(case)
            
        else:  
            # 用例不分组后执行
            for case in VAR.CurSuit.CaseList:
                self._runCase(case)

    def runRandomMode(self):
        '''
        @summary: 将脚本顺序打乱随机执行
        @author: shaochanghong
        @attention: 弃用
        '''
        for case in random.shuffle(VAR.CurSuit.CaseList):
            self._runCase(case)

    def _runCase(self, case):
        '''
        @summary: 执行单个用例
        @author: shaochanghong
        '''
        AnalyseConfig.parseScriptConfig(case)
        TestRunner().run(case)
        
