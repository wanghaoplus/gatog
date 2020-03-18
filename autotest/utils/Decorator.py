#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/4 21:18
# @Author  : shaochanghong
# @Site    : 
# @File    : decorator.py
# @Software: PyCharm
import functools
from collections import OrderedDict


def singleton(cls):
    _instance = {}

    def _singleton(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]
    return _singleton


def AutoPrint(isPublish=False):
    from autotest.core.logger import LogPrint
    
    def _wrapper(func):
        @functools.wraps(func)
        def _inner(*args, **kwargs):
            if isPublish:
                pass
            params_str = getParams(args, kwargs, func)
            LogPrint.PRINTI('----->' + func.__name__ + '(%s)' % params_str)
            ret = func(*args, **kwargs)
            LogPrint.PRINTI('<-----' + func.__name__ + '(%s)' % str(ret))
            return ret
        return _inner
    return _wrapper


def getParams(args, kwargs, func):
    default_list = func.__defaults__
    params_count = func.__code__.co_argcount
    params_name_list = func.__code__.co_varnames[:params_count]
    params_dict = OrderedDict()
    for i in range(len(args)):
        if ("__main__" not in str(args[i])) and ("object at" not in str(args[i])):
            params_dict[params_name_list[i]] = str(args[i])
    if kwargs:
        for key in params_name_list:
            if key in kwargs:
                params_dict[key] = str(kwargs[key])
    if default_list:
        default_name_ist = params_name_list[-len(default_list):]
        for i in range(len(default_name_ist)):
            if default_name_ist[i] in params_dict:
                continue
            params_dict[default_name_ist[i]] = str(default_list[i])
    params_str = ','.join(list(params_dict.values()))
    return params_str
