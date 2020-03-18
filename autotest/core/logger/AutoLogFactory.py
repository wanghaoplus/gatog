#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/16 21:41
# @Author  : shaochanghong
# @Site    : 
# @File    : AutoLogFactory.py
# @Software: PyCharm
import os
import logging
from autotest.utils.Decorator import singleton
from autotest.core.logger.AutoLogManager import AutoLogManager
from autotest.core.modle.Variable import VAR


@singleton
class AutoLogFactory(object):
    LOG_FACTORY = None
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    ERROR = logging.ERROR
    NOTSET = logging.NOTSET
    WARNING = logging.WARNING
    CRITICAL = logging.CRITICAL

    def beginProjectLog(self):
        # 添加日志文件输出
        logLevel = self.INFO
        self.logFactory.beginProjectLog(VAR.CurProject.ReportPath, logLevel)

    def endProjectLog(self):
        self.logFactory.endProjectLog()

    def beginCaseLog(self):
        caseName = VAR.CurCase.CaseName
        caseLogPath = os.path.join(VAR.CurProject.ReportPath, 'log')
        logLevel = self.INFO
        self.logFactory.beginCaseLog(caseLogPath, caseName, logLevel)

    def endCaseLog(self):
        self.logFactory.endCaseLog()

    @property
    def logFactory(self):
        if self.LOG_FACTORY:
            return self.LOG_FACTORY
        return AutoLogManager()

    def PRINTD(self, msg):
        self.logFactory.PRINTD(msg)

    def PRINTI(self, msg):
        self.logFactory.PRINTI(msg)

    def PRINTE(self, msg):
        self.logFactory.PRINTE(msg)

    def PRINTW(self, msg):
        self.logFactory.PRINTW(msg)

    def PRINTC(self, msg):
        self.logFactory.PRINTC(msg)
