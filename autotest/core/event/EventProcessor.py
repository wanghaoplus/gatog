#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/11 23:56
# @Author  : shaochanghong
# @Site    : 
# @File    : Observer.py
# @Software: PyCharm
from autotest.core.event.AutoInput import LogPrint
from autotest.core.event.AutoInput import VAR


class EventProcessor(object):
    """
    Function:观察者模式中的观察者基类，只能用来继承
    """
    def __init__(self):
        pass

    def eventHandler(self, event):
        pass

