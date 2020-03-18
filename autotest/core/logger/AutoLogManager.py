#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/16 21:40
# @Author  : shaochanghong
# @Site    : 
# @File    : AutoLogManager.py
# @Software: PyCharm
import os
import sys
import logging
from autotest.core.logger.AutoLogger import AutoLogger
from autotest.core.logger.AutoHandler import AutoFileHandler, AutoStreamHandler
from autotest.core.logger.AutoFormatter import AutoFileFormatter, AutoStreamFormatter
from autotest.utils.Decorator import singleton


@singleton
class AutoLogManager(object):
    PROJECT_HANDLER = 'projectHandler'
    CONSOLE_HANDLER = 'consoleHandler'
    CASE_HANDLER = 'caseHandler'
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    ERROR = logging.ERROR
    NOTSET = logging.NOTSET
    WARNING = logging.WARNING
    CRITICAL = logging.CRITICAL

    def __init__(self):
        self.autoLogger = self.getLogger()
        # 添加控制台日志
        consoleLogLevel = self.DEBUG
        self.addStreamHandler(self.PROJECT_HANDLER, consoleLogLevel)

    def beginProjectLog(self, projectLogPath, level):
        if not os.path.exists(projectLogPath):
            os.makedirs(projectLogPath)
        projectLogFileAbs = os.path.join(projectLogPath, 'test_run_detail.log')
        self.addFileHandler(projectLogFileAbs, self.PROJECT_HANDLER, level)

    def beginCaseLog(self, caseLogPath, caseName, level):
        logPath = os.path.join(caseLogPath, caseName)
        if not os.path.exists(logPath):
            os.makedirs(logPath)
        caseLogFileAbs = os.path.join(logPath, caseName + '.log')
        self.addFileHandler(caseLogFileAbs, self.CASE_HANDLER, level)

    def endCaseLog(self):
        self.removeCaseHandler()

    def endProjectLog(self):
        try:
            logging.shutdown()
        except:
            self.PRINTE('')

    def getLogger(self):
        logging.setLoggerClass(AutoLogger)
        root_logger = logging.getLogger('log')
        root_logger.manager = AutoManager(root_logger)
        return root_logger

    def addFileHandler(self, filePath, handlerName, level):
        fh = AutoFileHandler(filePath, encoding='utf-8')
        fh.name = handlerName
        fh.setLevel(level)
        formatter = AutoFileFormatter()
        fh.setFormatter(formatter)
        self.autoLogger.addHandler(fh)

    def addStreamHandler(self, handlerName, level):
        ch = AutoStreamHandler(sys.stdout)
        ch.name = handlerName
        ch.setLevel(level)
        formatter = AutoStreamFormatter()
        ch.setFormatter(formatter)
        self.autoLogger.addHandler(ch)

    def removeCaseHandler(self):
        for handler in self.autoLogger.handlers:
            if handler.name.startswith('case'):
                try:
                    handler.flush()
                    handler.close()
                finally:
                    self.autoLogger.removeHandler(handler)

    def PRINTD(self, msg):
        self.autoLogger.autoLog(self.DEBUG, str(msg))

    def PRINTI(self, msg):
        self.autoLogger.autoLog(self.INFO, str(msg))

    def PRINTW(self, msg):
        self.autoLogger.autoLog(self.WARNING, str(msg))

    def PRINTE(self, msg):
        self.autoLogger.autoLog(self.ERROR, str(msg))

    def PRINTC(self, msg):
        self.autoLogger.autoLog(self.CRITICAL, str(msg))


class AutoManager(logging.Manager):
    """
    @summary:自定义Manager，方便以后扩展
    """


if __name__ == "__main__":
    import time
    starttime = time.time()
    log = AutoLogManager()
    # print(log.autoLogger.handlers)
    log.PRINTD('hhhhhh')
    log.PRINTI('ss')
    log.PRINTE('ss')
    print(time.time() - starttime)
    print((time.time() - starttime) * 1000)
