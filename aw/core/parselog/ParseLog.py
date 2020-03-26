#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/2/9 16:25
# @Author  : shaochanghong
# @Site    : 
# @File    : ParseLog.py
import os
import re
import time
from queue import Queue
from aw.core.Input import getLbsCaseLogPath
FLUSH_TIMEOUT = 10  # 缓存中最多保留10s的数据
# 测试设备命令返回值标志
CMD_MARK = {'hdbd':'TXT,02',
           'mtk':'PMTK010',
           'thaiduo':'THAIDUO',
           'unicore':'Unicore',
           'ublox':'G.TXT',
           'brcm':'PQVER',
           'sony':'GCD. Done'}


class LogChangeListner(object):

    def __init__(self):
        self.deviceSN = None  # 设备唯一标识
        self.__debugFile = None
        self.__nmeaFile = None
        self.__sensorFile = None
        self.startFlushTime = time.time()
        self.startParseFlag = False
        self.cmdMark = None
        self.endLine = ''
        self.queue = Queue()
        
    def setDeviceMsg(self, device):
        deviceType = device.get('deviceType', 'hdbd').lower()
        self.cmdMark = CMD_MARK.get(deviceType)
    
    @property
    def deviceLogPath(self):
        deviceLogPath = os.path.join(getLbsCaseLogPath())
        if not os.path.exists(deviceLogPath):
            os.makedirs(deviceLogPath)
        return deviceLogPath
    
    @property
    def debugFile(self):
        if self.__debugFile is None:
            self.__debugFile = open(os.path.join(self.deviceLogPath, self.deviceSN + '_debug.txt'), 'ab')
        return self.__debugFile
    
    @property
    def nmeaFile(self):
        if self.__nmeaFile is None:
            self.__nmeaFile = open(os.path.join(self.deviceLogPath, self.deviceSN + '_nmea.txt'), 'ab')
        return self.__nmeaFile
    
    @property
    def sensorFile(self):
        if self.__sensorFile is None:
            self.__sensorFile = open(os.path.join(self.deviceLogPath, self.deviceSN +'_sensor.txt'), 'ab')
        return self.__sensorFile
    
    def onLogChange(self, msg):
        self.parseMsg(msg)

    def parseMsg(self, msg):
        '''
        @summary: 解析接收的数据
        @param msg: 待解析的数据
        '''
        if self.startParseFlag:
            self.collectNmeaLog(msg)
        self.writeNmeaMsg(msg)
#         elif 'debug':
#             self.writeDebugMsg(msg)
#         elif 'sensor':
#             self.writeSensorMsg(msg)
        self.flush()
        
    def collectNmeaLog(self, line):
        line = self.endLine+str(line)[2:-1]
        lineSplit=line.split(r'\r\n')
        self.endLine=lineSplit[-1]
        for nemaLine in lineSplit[0:-1]:
            if re.search('GGA', nemaLine):
                ggaMsg = str(nemaLine).split('GGA,')[1]
                self.queue.put_nowait(('GGA', ggaMsg))
                
            elif re.search(self.cmdMark, str(nemaLine)):
                self.queue.put_nowait((self.cmdMark, str(nemaLine)))
            
    def setParseNmeaEnable(self, isEnable):
        self.startParseFlag = isEnable
    
    def writeDebugMsg(self, debugMsg):
        '''
        @summary: 将debug信息写入文件中
        @param debugMsg: debug信息
        '''
        self.debugFile.write(debugMsg)
        
    def writeNmeaMsg(self, nmeaMsg):
        '''
        @summary: 将nmea信息写入文件中
        @param nmeaMsg: nmea信息
        '''
        self.nmeaFile.write(nmeaMsg)
        
    def writeSensorMsg(self, sensorMsg):
        self.sensorFile.write(sensorMsg)
        
    def flush(self):
        '''
        @summary: 将缓存中的数据flush到文件中
        @attention: 缓存中只保留FLUSH_TIMEOUT时间长度内的数据
        '''
        if time.time() - self.startFlushTime < FLUSH_TIMEOUT:
            return
        if self.__debugFile is not None:
            self.__debugFile.flush()
        if self.__nmeaFile is not None:
            self.__nmeaFile.flush()
        if self.__sensorFile is not None:
            self.__sensorFile.flush()
        self.startFlushTime = time.time()
    
