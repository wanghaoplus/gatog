#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/16 21:39
# @Author  : shaochanghong
# @Site    : 
# @File    : AutoHandler.py
# @Software: PyCharm
from logging import StreamHandler, FileHandler


class AutoStreamHandler(StreamHandler):
    """
    function:自定义控制台输出handler，方便以后扩展
    """


class AutoFileHandler(FileHandler):
    """
    function:自定义控制台输出handler，方便以后扩展
    """
