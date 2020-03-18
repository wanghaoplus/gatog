#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/8 22:49
# @Author  : shaochanghong
# @Site    : 
# @File    : CustomException.py
# @Software: PyCharm


class CustomException(Exception):

    def __init__(self, error):
        super(CustomException, self).__init__()
        self.errorMsg = error

    def __str__(self):
        return self.errorMsg


class NoTestCaseException(Exception):
    """has no testcase exception"""
    pass


class NoSuchCaseException(Exception):
    pass


class ErrorScriptException(Exception):
    pass


class NoProjectConfigException(Exception):
    """has no ProjectConfig exception"""
    pass


class NoConfigRunCaseException(Exception):
    pass


class ErrorConfigException(Exception):
    pass
