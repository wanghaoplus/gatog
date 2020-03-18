# -*- coding: utf-8 -*- 


DT_SUC = 0
DT_FAIL = -1

import logging
import functools
from collections import OrderedDict
from aw.utils.nmeanalysis.LbsLogPrint import PRINTI, PRINTE, PRINTC, PRINTW, PRINTD, PRINTTRACE

    
def LBSDector(isPublish=False):
    def _wrapper(func):
        @functools.wraps(func)
        def _inner(*args, **kwargs):
            if isPublish:
                pass
            params_str = getParams(args, kwargs, func)
            PRINTI('----->' + func.__name__ + '(%s)' % params_str)
            ret = func(*args, **kwargs)
            PRINTI('<-----' + func.__name__ + '(%s)' % str(ret))
            return ret
        return _inner
    return _wrapper

def getParams(args, kwargs, func):
    default_list = func.__defaults__
    params_name_list = func.__code__.co_varnames
    params_dict = OrderedDict()
    for i in range(len(args)):
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

DT_FAIL = -1
DT_SUC = 0

