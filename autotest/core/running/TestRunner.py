#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/2 23:27
# @Author  : shaochanghong
# @Site    : 
# @File    : TestCaseRunner.py
# @Software: PyCharm
import time
from autotest.core.logger import LogPrint
from autotest.core.modle.Variable import VAR
from autotest.core.modle.Variable import VariableContainer
from autotest.core.modle.CustomException import NoTestCaseException, NoSuchCaseException


class TestRunner(object):
    ResultNotRun = 'NotRun'
    ResultPass = 'Passed'
    ResultFail = 'Failed'
    ResultBlock = 'Block'
    ResultUnavailable = 'Unavailable'
    LoopPassTotal = 0
    LoopFailTotal = 0
    PrintHeader = '*********'
    DEFAULT_LOOP_TIMES = 1

    def run(self, testCaseModule):
        try:
            scriptFilePath = '.'.join([testCaseModule.__module__.replace('.', '/'), 'py'])
            LogPrint.PRINTI('Prepare to Start: %s' % scriptFilePath)
            if VAR.CurProject.IsHandleDevice == 'true':
                from autotest.core.conf import AnalyseConfig
                AnalyseConfig.collectTestDevice()
            testCase = testCaseModule()
            subTestCaseList = getattr(testCase, "TestCaseList")
            if not subTestCaseList:
                raise NoTestCaseException('has no testcase in TestCaseList, please check it.')
        except:
            LogPrint.PRINTTRAC()
            return
        # 让用户可以在脚本中以self.data.xx获取脚本配置文件中的数据
        setattr(testCase, "data", VAR.CurCase.Config)
        # 开始子用例测试
        for subTestCaseName in subTestCaseList:
            # 用例开始前准备工作
            self.beforeSubCaseStart(subTestCaseName)
            # 检查用例是否存在且有效
            subTestCase = self._checkSubTestCaseExist(testCase, subTestCaseName)
            if subTestCase is None:
                VAR.CurCase.CaseResult = TestRunner.ResultUnavailable
            else:
                # 获取用例循环次数，并开始执行用例
                loopTimes = self._getSubCaseLoopTimes(subTestCaseName)
                for loopId in range(1, loopTimes + 1):
                    self.printHeaderAndFooter(subTestCaseName, 'Loop_%s Start' % loopId)
                    VAR.CurCase.CurLoopTime = loopId
                    if self._runSetup(testCase, subTestCaseName):
                        if self._runTest(subTestCase):
                            VAR.CurCase.LoopPassTotal += 1
                        else:
                            VAR.CurCase.CaseResult = TestRunner.ResultFail
                    else:
                        VAR.CurCase.CaseResult = TestRunner.ResultFail
                    self._runTeardown(testCase, subTestCaseName)
                    self.printHeaderAndFooter(subTestCaseName, 'Loop_%s End' % loopId)
            VAR.CurCase.EndTime = time.strftime("%Y-%m-%d %H:%M:%S")
            self._changeProjectVAR()
            # 将用例执行结果写入数据库
            self._writeCaseResult()
            # 用例结束后的复位操作
            self.afterSubCaseEnd(subTestCaseName)

    def _checkSubTestCaseExist(self, testCase, subTestCaseName):
        try:
            self.printHeaderAndFooter(subTestCaseName, 'Start')
            subTestCase = getattr(testCase, subTestCaseName, None)
            if subTestCase is None:
                raise NoSuchCaseException('has no such case: %s' % subTestCaseName)
        except NoSuchCaseException:
            LogPrint.PRINTTRAC()
        return subTestCase

    def _runSetup(self, testCase, subTestCaseName):
        try:
            self.printHeaderAndFooter(subTestCaseName, 'Setup Start')
            testCase.setupStart()
            testCase.setup()
            testCase.setupEnd()
            self.printHeaderAndFooter(subTestCaseName, 'Setup Passed')
            return True
        except:
            LogPrint.PRINTTRAC()
            self.printHeaderAndFooter(subTestCaseName, 'Setup Failed')
            return False

    def _runTest(self, subTestCase):
        try:
            self.printHeaderAndFooter(subTestCase.__name__, 'Test Start')
            subTestCase()
            self.printHeaderAndFooter(subTestCase.__name__, 'Test Passed')
            return True
        except:
            LogPrint.PRINTTRAC()
            self.printHeaderAndFooter(subTestCase.__name__, 'Test Failed')
            return False

    def _runTeardown(self, testCase, subTestCaseName):
        try:
            self.printHeaderAndFooter(subTestCaseName, 'Teardown Start')
            testCase.teardownStart()
            testCase.teardown()
            testCase.teardownEnd()
            self.printHeaderAndFooter(subTestCaseName, 'Teardown Passed')
        except:
            LogPrint.PRINTTRAC()
            self.printHeaderAndFooter(subTestCaseName, 'Teardown Failed')

    def _getSubCaseLoopTimes(self, subTestCaseName):
        loopTimes = self.DEFAULT_LOOP_TIMES
        if isinstance(VAR.CurCase.Config, VariableContainer):
            return loopTimes
        if hasattr(VAR.CurCase.Config, 'LoopTimes'):
            loopTimes = VAR.CurCase.Config.LoopTimes
        if hasattr(VAR.CurCase.Config, subTestCaseName):
            subTestCase = getattr(VAR.CurCase.Config, subTestCaseName)
            if hasattr(subTestCase, 'LoopTimes'):
                loopTimes = subTestCase.LoopTimes
        return int(loopTimes)

    def printHeaderAndFooter(self, testCaseName, msg):
        LogPrint.PRINTI(''.join([self.PrintHeader, testCaseName, ': ', msg]))

    def beforeSubCaseStart(self, subCaseName):
        VAR.CurCase.CaseName = subCaseName
        VAR.CurCase.CaseResult = TestRunner.ResultPass
        VAR.CurCase.LoopPassTotal = TestRunner.LoopPassTotal
        VAR.CurCase.LoopFailTotal = TestRunner.LoopFailTotal
        VAR.CurCase.StartTime = time.strftime("%Y-%m-%d %H:%M:%S")
        LogPrint.addCaseLog()

    def afterSubCaseEnd(self, subCaseName):
        LogPrint.PRINTI('Test Case End: %s' % subCaseName)
        LogPrint.removeCaseLog()
        VAR.CurCase.CurLoopTime = 0
        VAR.CurCase.CaseName = None
        VAR.CurCase.CaseResult = TestRunner.ResultNotRun

    def _writeCaseResult(self):
        from autotest.utils.DataBase import TestResultDB
        TestResultDB().addCaseResult()

    def _changeProjectVAR(self):
        VAR.CurProject.Total += 1
        if VAR.CurCase.CaseResult == TestRunner.ResultFail:
            VAR.CurProject.Fail += 1
        elif VAR.CurCase.CaseResult == TestRunner.ResultPass:
            VAR.CurProject.Pass += 1
        elif VAR.CurCase.CaseResult == TestRunner.ResultUnavailable:
            VAR.CurProject.Unavailable += 1
        elif VAR.CurCase.CaseResult == TestRunner.ResultBlock:
            VAR.CurProject.Block += 1
        else:
            VAR.CurProject.NotRun += 1

