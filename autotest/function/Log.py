#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/21 13:23
# @Author  : shaochanghong
# @Site    : 
# @File    : Log.py
# @Software: PyCharm
from autotest.core.logger import LogPrint


def PRINTD(msg):
    LogPrint.PRINTD(msg)


def PRINTI(msg):
    LogPrint.PRINTI(msg)


def PRINTW(msg):
    LogPrint.PRINTW(msg)


def PRINTE(msg):
    LogPrint.PRINTE(msg)


def PRINTTRAC(msg):
    LogPrint.PRINTTRAC(msg)


def PRINTC(msg):
    LogPrint.PRINTC(msg)
