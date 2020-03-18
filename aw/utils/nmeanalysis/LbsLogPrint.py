#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/15 18:23
# @Author  : shaochanghong
# @Site    : 
# @File    : LogUtil.py
# @Software: PyCharm


import logging
import sys, os
import datetime, time
import random
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass
DT_SUC = 0
DT_FAIL = -1


gLoggerObj = None
class AresLogPrint(object):

    vLogAbsPath = None
    
    '''日志打印输出'''
    def __init__(self):
        self.logger = None
        self.step = 1
        self.caseLogHandler = None
           
    @staticmethod
    def aresaw_logger_getObj():
        global gLoggerObj
        if None != gLoggerObj:
            return DT_SUC, gLoggerObj
        gLoggerObj = AresLogPrint()
        gLoggerObj.ares_logger_init()
        return DT_SUC, gLoggerObj
    
    def ares_logger_init(self):
        '''关键代码1段-----开始'''
        if None != self.logger:
            return
        # 获取logger实例，如果参数为空则返回root logger
        self.logger = logging.getLogger('powerTest')
        # 指定logger输出格式
        formatter = logging.Formatter('%(asctime)s [%(thread)s]%(levelname)-8s: %(message)s')
        # 文件日志

        if  len(self.logger.handlers) > 0:
            return
        '''关键代码1段-----结束'''
        '''下面这段代码不能放在上面去--开始'''

        '''上面面这段代码不能放在上面关键代码1段之前--结束'''
        
        if sys.platform == "win32":
            # 控制台日志
            from aw.utils.nmeanalysis.AnalysisNMEA import reportPath
            self.vLogAbsPath = reportPath
            if not os.path.isdir(self.vLogAbsPath):
                os.makedirs(self.vLogAbsPath)
            self.logAbsPath = os.path.join(self.vLogAbsPath, 'nmeanalysis_details.log')
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.formatter = formatter  # 也可以直接给formatter赋值
            self.logger.addHandler(console_handler)
        else:
            if not os.path.exists(reportPath):
                os.makedirs(reportPath)
            t = str(time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time())))
            print(reportPath)
            self.logAbsPath = os.path.join(reportPath, 'test_run_details.log')
            print(self.logAbsPath)
            self.__aresMoveFile(self.logAbsPath, os.path.join(reportPath, 'test_run_details_%s.log' % t))
            
        file_handler = logging.FileHandler(self.logAbsPath, mode='w', encoding='utf-8')
        file_handler.setFormatter(formatter)  # 可以通过setFormatter指定输出格式
        # 为logger添加的日志处理器
        self.logger.addHandler(file_handler)
        
        # 指定日志的最低输出级别，默认为WARN级别
        self.logger.setLevel(logging.INFO)
    
    def __aresMoveFile(self, src, dst):
        import shutil
        try:
            shutil.move(src, dst)
        except:
            print('move log error')
    
    def ares_case_log_control(self, CaseName):
        if self.caseLogHandler:
            self.logger.removeHandler(self.caseLogHandler)
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
        caseLogPath = os.path.join(self.scriptLogPaht, CaseName + ".log")
        self.caseLogHandler = logging.FileHandler(caseLogPath)
        self.caseLogHandler.setFormatter(formatter)
        self.logger.addHandler(self.caseLogHandler)
    
    def ares_log_printInfo(self, msg=''):
        if self.logger == None:
            self.ares_logger_init()
        self.logger.info(msg)

    def ares_log_printError(self, msg=''):
        if self.logger == None:
            self.ares_logger_init()
        self.logger.error(msg)
        
    def ares_log_printCritical(self, msg=''):
        if self.logger == None:
            self.ares_logger_init()
        self.logger.critical(msg)
        
    def ares_log_printWarn(self, msg=''):
        if self.logger == None:
            self.ares_logger_init()
        self.logger.warn(msg)

    def ares_log_printDebug(self, msg=''):
        if self.logger == None:
            self.ares_logger_init()
        self.logger.debug(msg)
        
    def ares_log_printTrace(self, msg=''):
        if self.logger == None:
            self.ares_logger_init()
        self.logger.exception(msg)
    
    def ares_log_printStep(self, msg=''):
        if self.logger == None:
            self.ares_logger_init()
        self.logger.info("Step %d:%s" % (self.step, msg))
        self.step += 1
        
def ADDCASELOG(caseName):
    logger = AresLogPrint.aresaw_logger_getObj()[1]
    logger.ares_case_log_control(caseName)


def PLATFORM_PRINTTRACE(msg=''):
    logger = AresLogPrint.aresaw_logger_getObj()[1]
    logger.ares_log_printTrace(msg)
    
def PLATFORM_PRINTD(msg=""):
    logger = AresLogPrint.aresaw_logger_getObj()[1]
    logger.ares_log_printInfo(str(msg))
    
def PLATFORM_PRINE(msg=""):
    logger = AresLogPrint.aresaw_logger_getObj()[1]
    logger.ares_log_printError(str(msg))

def PRINTI(msg=''):
    logger = AresLogPrint.aresaw_logger_getObj()[1]
    logger.ares_log_printInfo(msg)

def PRINTE(msg=''):
    logger = AresLogPrint.aresaw_logger_getObj()[1]
    logger.ares_log_printError(msg)

def PRINTC(msg=''):
    logger = AresLogPrint.aresaw_logger_getObj()[1]
    logger.ares_log_printCritical(msg)

def PRINTW(msg=''):
    logger = AresLogPrint.aresaw_logger_getObj()[1]
    logger.ares_log_printWarn(msg)

def PRINTD(msg=''):
    logger = AresLogPrint.aresaw_logger_getObj()[1]
    logger.ares_log_printDebug(msg)

def PRINTTRACE(msg=''):
    logger = AresLogPrint.aresaw_logger_getObj()[1]
    logger.ares_log_printTrace(msg)
    
if __name__ == '__main__':
    
    from aw.utils.nmeanalysis.config import config
    import datetime
    import time
    
     