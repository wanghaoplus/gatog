#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/27 21:01
# @Author  : shaochanghong
# @Site    : 
# @File    : GSS6425.py
# @Software: PyCharm
import time
from aw.core.Input import SUC
from aw.core.Input import FAIL


class GSS6425(object):
    IP = None
    URL_FORMAT = "http://%s/shm_%s.shtml?%s"
    
    def __init__(self, ip):
        GSS6425.IP = ip
        
    def __gss6425(self, cmd):
        try:
            from urllib import request
            response = request.urlopen(cmd)
            ret = response.read().decode('utf-8')
            return ret.replace('\n', ' ').replace('\r', ' ')
        except:
            return
        
    def aw_gss6425MuteSet(self, isMute):
        if isMute:
            cmd = GSS6425.URL_FORMAT%(GSS6425.IP, 'put', '-a31,-wA')
            self.__gss6425(cmd)
            cmd = GSS6425.URL_FORMAT%(GSS6425.IP, 'get', '-a')
            ret = self.__gss6425(cmd)
            if "-a 31" in ret:
                return SUC, ret
            return FAIL, ret
        cmd = GSS6425.URL_FORMAT%(GSS6425.IP, 'put', '-a0,-wA')
        self.__gss6425(cmd)
        cmd = GSS6425.URL_FORMAT%(GSS6425.IP, 'get', '-a')
        ret = self.__gss6425(cmd)
        if "-a 0" in ret:
            return SUC, ret
        return FAIL, ret
    
    def aw_gss6425StopPlay(self):
        """
        @summary: 停止播放场景
        """
        cmd = GSS6425.URL_FORMAT%(GSS6425.IP, 'get', '-m')
        ret = self.__gss6425(cmd)
        if "STOPPED" in ret:
            return SUC, ''
        cmd = GSS6425.URL_FORMAT%(GSS6425.IP, 'put', '-wS')
        ret = self.__gss6425(cmd)
        time.sleep(5)
        cmd = GSS6425.URL_FORMAT%(GSS6425.IP, 'get', '-m')
        ret = self.__gss6425(cmd)
        if "STOPPED" in ret:
            return SUC, 'success'
        return FAIL, 'fail'
    
    def aw_gss6425Play(self, fileName, moment=0):
        """
        @summary: 播放场景
        @param fileName: 场景文件名称
        @param moment: 场景播放偏移量
        """
        if fileName is None:
            return FAIL, "has no this file"
        cmd = GSS6425.URL_FORMAT%(GSS6425.IP, "get", "-m")
        ret = self.__gss6425(cmd)
        if "PLAYING" in ret:
            cmd = GSS6425.URL_FORMAT%(GSS6425.IP, "put", "-wS")
            self.__gss6425(cmd)
            time.sleep(7)
        cmd = GSS6425.URL_FORMAT%(GSS6425.IP, "put", "-f"+fileName+',-o'+moment+',-wP')
        self.__gss6425(cmd)
        time.sleep(2)
        cmd = GSS6425.URL_FORMAT%(GSS6425.IP, "get", "-m")
        ret = self.__gss6425(cmd)
        if "PLAYING" in ret:
            return SUC,'success'
        return FAIL, 'fail'
    
    def aw_gss6425ATTN(self, value=0):
        """
        @summary: 调节信号大小
        @param value: 
        """
        cmd = GSS6425.URL_FORMAT%(GSS6425.IP, "put", "-a"+str(value)+"-wA")
        ret = self.__gss6425(cmd)
        cmd = GSS6425.URL_FORMAT%(GSS6425.IP, "get", "-a")
        ret = self.__gss6425(cmd)
        if str(value) in ret:
            return SUC, ''
        return FAIL, ''

if __name__ == '__main__':
    GSS7000(ip='10.100.5.230').aw_GSS7000CheckExpectedStatus(SIMU_STATUS_DICT['Ready'])
    
    