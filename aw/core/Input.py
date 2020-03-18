#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/18 13:06
# @Author  : shaochanghong
# @Site    : 
# @File    : Input.py
# @Software: PyCharm
"""工程中所有对框架的引用必须经过此文件，不允许直接从框架中引用"""

import os
import time
from queue import Queue
from autotest.function import Log
from autotest.utils.Decorator import AutoPrint
from autotest.utils.Decorator import singleton
from autotest.function.LbsTestCaseBase import LoopTest
from autotest.function.LbsTestCaseBase import LbsTestCaseBase
from autotest.core.modle.Variable import VariableContainer

SUC = 0
FAIL = -1
NMEA_DATA_QUEUE = Queue()
THREAD_VAR = VariableContainer()


class LBSException(Exception):
    """LBS自定义异常类"""
    pass


def newThreadFunc(func=None, name=None, args=(), kwargs=None, daemon=True):
    import threading
    th = threading.Thread(target=func, args=args, kwargs=kwargs)
    if name is not None:
        th.setName(name)
        THREAD_VAR[name] = th
    if daemon is True:
        th.setDaemon(True)
    th.start()


def PRINTD(msg):
    Log.PRINTD(msg)


def PRINTI(msg):
    Log.PRINTI(msg)


def PRINTW(msg):
    Log.PRINTW(msg)


def PRINTE(msg):
    Log.PRINTE(msg)


def PRINTTRAC(msg=''):
    Log.PRINTTRAC(msg)


def PRINTC(msg):
    Log.PRINTC(msg)


def getProjectPath():
    """获取工程路径"""
    from autotest.core.modle.Variable import VAR
    return VAR.CurProject.RootPath


def getResourcePath():
    '''获取资源文件路径'''
    return os.path.join(getProjectPath(), 'resource')


def getCurCaseName():
    """获取当前用例名称"""
    from autotest.core.modle.Variable import VAR
    return VAR.CurCase.CaseName


def getCurCaseConfig():
    '''获取当前执行用例的配置信息'''
    from autotest.core.modle.Variable import VAR
    return VAR.CurCase.Config


def getCaseResult():
    """获取用例执行结果"""
    from autotest.core.modle.Variable import VAR
    return VAR.CurCase.CaseResult


def getCaseLoopTime():
    """获取用例当前是第几次循环"""
    from autotest.core.modle.Variable import VAR
    return VAR.CurCase.CurLoopTime


def getLbsCaseLogPath():
    from autotest.core.modle.Variable import VAR
    return os.path.join(VAR.CurProject.ReportPath, 'log', VAR.CurCase.CaseName)


def getLbsReportPath():
    from autotest.core.modle.Variable import VAR
    return VAR.CurProject.ReportPath


def getDevices():
    from autotest.core.modle.Variable import DEVICE
    return DEVICE


def getInstruments():
    from autotest.core.modle.Variable import INSTRUMENT
    return INSTRUMENT


def isSuc(ret):
    if ret[0] == FAIL:
        raise LBSException("interface return fail.")
    return ret[1]


if __name__ == '__main__':
    print('end')

