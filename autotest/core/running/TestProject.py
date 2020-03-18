#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/10 21:03
# @Author  : shaochanghong
# @Site    : 
# @File    : TestProject.py
# @Software: PyCharm
import os
import time
from autotest.core.conf import AnalyseConfig
from autotest.core.logger import LogPrint
from autotest.core.modle.Variable import VAR
from autotest.core.running.BaseTest import BaseTestProject
from autotest.core.running.TestSuit import TestSuit
from autotest.utils.DataBase import TestResultDB


class TestProject(BaseTestProject):
    FIXTURE_MODE = 0  # 顺序执行模式
    RANDOM_MODE = 1  # 随机执行模式

    def __init__(self):
        super(TestProject, self).__init__()

    def setup(self):
        # 初始化VAR信息
        initProjectVar()
        # 工程配置文件解析  projectconfig.json
        AnalyseConfig.parseProjectSetting()
        # 获取用例信息
        AnalyseConfig.getRunCases()
        # 将用例按场景分组
        if VAR.CurProject.GroupCaseEnable.lower() == 'true':
            AnalyseConfig.groupTestCase()
        # 注册Event事件

    def run(self):
        TestResultDB().createProjectTable()
        TestResultDB().createCaseTable()
        for loopId in range(1, VAR.CurProject.LoopTimes + 1):
            setProjectReportPath(loopId)
            VAR.CurProject.CurLoopTime = loopId
            self._run()

    def _run(self):
        VAR.CurProject.StartTime = time.strftime('%Y-%m-%d %H:%M:%S')
        # 开始记录工程执行日志
        LogPrint.addProjectLog()
        if VAR.CurProject.RunMode == TestProject.FIXTURE_MODE:
            TestSuit().runFixtureMode()
        elif VAR.CurProject.RunMode == TestProject.RANDOM_MODE:
            TestSuit().runRandomMode()
        VAR.CurProject.EndTime = time.strftime('%Y-%m-%d %H:%M:%S')
        TestResultDB().addProjectResult()
        from autotest.core.output.Report import Report
        Report().output()
        printProjectSummary()
        # 结束记录工程执行日志
        LogPrint.removeProjectLog()
        # 结束重置VAR信息
        resetProjectVar()

    def teardown(self):
        pass


def printProjectSummary():
    endTime = time.mktime(time.strptime(VAR.CurProject.EndTime, '%Y-%m-%d %H:%M:%S'))
    startTime = time.mktime(time.strptime(VAR.CurProject.StartTime, '%Y-%m-%d %H:%M:%S'))
    s = '\n测试结束！\n运行时间: {time}min\n共计执行用例数量：{count}\n执行成功用例数量：{Pass}' \
        '\n执行失败用例数量：{fail}\n无效用例数量：{unavailable}\n未执行用例数量：{notrun}\n'
    summary = s.format(
        time=round((endTime - startTime) / 60, 2),
        count=VAR.CurProject.Total,
        Pass=VAR.CurProject.Pass,
        fail=VAR.CurProject.Fail,
        unavailable=VAR.CurProject.Unavailable,
        notrun=VAR.CurProject.NotRun
    )
    LogPrint.PRINTI(summary)


def setProjectReportPath(loopId):
    if VAR.CurProject.LoopTimes is 1:
        VAR.CurProject.ReportPath = os.path.join(VAR.CurProject.ReportRootPath, VAR.CurProject.TaskId)
    else:
        VAR.CurProject.ReportPath = os.path.join(VAR.CurProject.ReportRootPath,
                                                 VAR.CurProject.TaskId, 'Loop_%s' % loopId)


def initProjectVar():
    VAR.CurProject.ExecuteState = 'RUNNING'
    VAR.CurProject.CurLoopTime = 1
    VAR.CurProject.Total = 0
    VAR.CurProject.NotRun = 0
    VAR.CurProject.RunEnd = 0
    VAR.CurProject.Block = 0
    VAR.CurProject.Pass = 0
    VAR.CurProject.Fail = 0
    VAR.CurProject.Unavailable = 0
    VAR.CurProject.StartTime = 0
    VAR.CurProject.EndTime = 0


def resetProjectVar():
    VAR.CurProject.NotRun = 0
    VAR.CurProject.RunEnd = 0
    VAR.CurProject.Block = 0
    VAR.CurProject.Pass = 0
    VAR.CurProject.Fail = 0
    VAR.CurProject.Unavailable = 0
    VAR.CurProject.StartTime = 0
    VAR.CurProject.EndTime = 0
