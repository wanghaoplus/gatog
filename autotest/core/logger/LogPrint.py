#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/1 17:53
# @Author  : shaochanghong
# @Site    : 
# @File    : LogPrint.py
# @Software: PyCharm
import traceback
from autotest.core.logger.AutoLogFactory import AutoLogFactory


def addProjectLog():
    """读取工程配置文件后调用"""
    AutoLogFactory().beginProjectLog()


def removeProjectLog():
    """工程执行结束后调用"""
    AutoLogFactory().endProjectLog()


def addCaseLog():
    """用例开始前调用"""
    AutoLogFactory().beginCaseLog()


def removeCaseLog():
    """用例结束后调用"""
    AutoLogFactory().endCaseLog()


def PRINTD(msg):
    AutoLogFactory().PRINTD(msg)


def PRINTI(msg):
    AutoLogFactory().PRINTI(msg)


def PRINTE(msg):
    AutoLogFactory().PRINTE(msg)


def PRINTW(msg):
    AutoLogFactory().PRINTW(msg)


def PRINTC(msg):
    AutoLogFactory().PRINTC(msg)


def PRINTTRAC(msg=''):
    AutoLogFactory().PRINTE(traceback.format_exc()+msg)


