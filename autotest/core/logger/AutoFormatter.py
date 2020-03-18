#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/16 21:39
# @Author  : shaochanghong
# @Site    : 
# @File    : AutoFormatter.py
# @Software: PyCharm
from logging import Formatter


class AutoFileFormatter(Formatter):
    """自定义log输出格式，方便以后扩展"""
    DEFAULT_FMT = '%(asctime)s [%(threadName)s][%(thread)d][%(levelname)s] %(message)s'

    def __init__(self):
        super(AutoFileFormatter, self).__init__(self.DEFAULT_FMT)


class AutoStreamFormatter(Formatter):
    """自定义log输出格式，方便以后扩展"""
    DEFAULT_FMT = '%(asctime)s [%(threadName)s][%(thread)d][%(levelname)s] %(message)s'

    def __init__(self):
        super(AutoStreamFormatter, self).__init__(self.DEFAULT_FMT)

