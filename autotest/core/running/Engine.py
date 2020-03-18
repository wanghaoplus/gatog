#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/5 22:43
# @Author  : shaochanghong
# @Site    : 
# @File    : Engine.py
# @Software: PyCharm
import functools
from autotest.core.logger import LogPrint
from autotest.core.modle.CustomException import ErrorScriptException


def loadModule(modulePath):
    # modulePath的格式为package.module
    try:
        moduleName = modulePath.split('.')[-1]
        return __import__(modulePath, fromlist=[moduleName])
    except ImportError:
        raise ErrorScriptException('Not Found {0}.py'.format(modulePath.replace('.', '\\')))


def loadClassFromModule(module, className):
    try:
        return getattr(module, className)
    except AttributeError:
        raise ErrorScriptException('Not Found {0} In {1}.py'.format(className, module.__name__.replace('.', '\\')))


def loadScriptFromModule(modulePath):
    module = loadModule(modulePath)
    className = modulePath.split('.')[-1]
    return loadClassFromModule(module, className)


def LoopTest(times=1):

    def loop(func):

        @functools.wraps(func)
        def _loop(*args, **kwargs):
            for _ in range(times):
                try:
                    func(*args, **kwargs)
                except:
                    pass

        return _loop

    return loop


def SetupStep(msg):
    LogPrint.PRINTI("预置条件: " + str(msg))


def TestStep(msg):
    LogPrint.PRINTI("测试步骤: " + str(msg))


def CheckPoint(msg):
    LogPrint.PRINTI("检测点: " + str(msg))


def TeardownStep(msg):
    LogPrint.PRINTI("环境恢复: " + str(msg))

