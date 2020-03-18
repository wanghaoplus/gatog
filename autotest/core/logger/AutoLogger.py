#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/18 21:28
# @Author  : shaochanghong
# @Site    : 
# @File    : AutoLogger.py
# @Software: PyCharm
import logging


class AutoLogger(logging.Logger):
    """
    @summary:自定义Logger，方便以后扩展
    """
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    ERROR = logging.ERROR
    NOTSET = logging.NOTSET
    WARNING = logging.WARNING
    CRITICAL = logging.CRITICAL
    
    def __init__(self, name, level=NOTSET):
        super(AutoLogger, self).__init__(name, level)
        self.addLevelName()

    def addLevelName(self):
        logging.addLevelName(self.NOTSET, 'N')
        logging.addLevelName(self.DEBUG, 'D')
        logging.addLevelName(self.INFO, 'I')
        logging.addLevelName(self.WARNING, 'W')
        logging.addLevelName(self.ERROR, 'E')
        logging.addLevelName(self.CRITICAL, 'C')

    def autoLog(self, level, msg):
        self.setLevel(level)
        self.log(level, str(msg))
