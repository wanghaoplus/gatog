#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/2/9 13:06
# @Author  : shaochanghong
# @Site    : 
# @File    : SerialBase.py
import serial
from aw.core.Input import PRINTE
from aw.core.Input import PRINTI
from aw.core.Input import PRINTTRAC
from aw.core.Input import THREAD_VAR
from aw.core.parselog.ParseLog import LogChangeListner

CONNECT_RETRY_TIMES = 5


class SerialBase(LogChangeListner):
    __port = None
    __baud = None
    __timeout = 2
    __serObj = None
    stopRecvFlag = False

    def __init__(self, port, baud=115200, readTimeOut=1):
        super(SerialBase, self).__init__()
        self.__port = port
        self.__baud = baud
        self.__timeout = readTimeOut
        self.deviceSN = port + '_'
        
    @property
    def serialObj(self):
        if (self.__serObj is None) and (self.stopRecvFlag is False):
            self.__serObj = self.__connect()
        return self.__serObj
    
    def __connect(self):
        for connTimes in range(1, CONNECT_RETRY_TIMES + 1):
            try:
                serObj = serial.Serial()
                serObj.port = self.__port
                serObj.baudrate = self.__baud
#                 serObj.timeout = self.__timeout
                serObj.open()
                serObj.flushInput()
                serObj.flushOutput()
                return serObj
            except:
                PRINTE('第%s次连接失败...' % connTimes)
                if connTimes == CONNECT_RETRY_TIMES:
                    PRINTTRAC('请检串口连接是否异常')
                    raise
    
    def connect(self):
        if self.__serObj is None:
            self.__serObj = self.__connect()
               
    def send(self, cmd):
#         cmd = bytes.fromhex(cmd)
        self.serialObj.write(cmd)
        
    def startReciver(self):
        while self.stopRecvFlag is False:
            try:
                recvData = self.serialObj.readline()
                self.parseData(recvData)
                
            except :
                pass
            
    def parseData(self, msg):
        self.onLogChange(msg)
    
    def stopReciver(self):
        
        self.stopRecvFlag = True
#         PRINTI(self.__port)
#         PRINTI(THREAD_VAR)
#         THREAD_VAR[self.__port].join()
        self.close()
        
    def close(self):
        if self.__serObj is not None:
            self.__serObj.close()
            self.__serObj = None
            
    def __del__(self):
        self.close()

if __name__ == '__main__':
    so = SerialBase('COM4')
    import threading
    import time
    so.connect()
    t1 = threading.Thread(target=so.startReciver, args=())  #
    t1.setDaemon(True)
    t1.start() 
    while True:
        ss = input('please:')
        if ss =='222':
#             send_data = 'F1 D9 06 41 05 00 88 13 00 00 01 E8 56'
            send_data = b'\xf1\xd9\x06A\x05\x00\x88\x13\x00\x00\x00\xe7U'
            so.send(send_data)
        
