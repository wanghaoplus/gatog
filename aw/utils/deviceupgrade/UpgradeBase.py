#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2020/2/19 14:19
# @Author  : wanghao
# @Site    :
# @File    : UserModeFWUpgrade.py
import socket
import serial
from aw.core.Input import PRINTE
from aw.core.Input import PRINTTRAC
CONNECT_TIMEOUT = 5
CONNECT_RETRY_TIMES = 1
BUFSIZE = 1024


class SocketClient(object):
    __host = None
    __port = None
    __client = None
    stopRecvFlag = False

    def __init__(self, host=None, port=None):
        super(SocketClient, self).__init__()
        self.__host = host
        self.__port = port

    @property
    def client(self):
        if self.__client is None:
            self.__client = self._connect()
        return self.__client
    
    def _connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for connTimes in range(1, CONNECT_RETRY_TIMES + 1):
            try:
                s.connect((self.__host, self.__port))
                s.timeout=2
                return s
            except:
                PRINTE('第%s次连接失败...' % connTimes)
                if connTimes == CONNECT_RETRY_TIMES:
#                     PRINTTRAC('请检查网络是否异常')
                    raise
                
    def connect(self):
        if self.__client is None:
            self.__client = self._connect()

    def send(self, cmd):
        self.client.send(cmd)
        
    def reciver(self, bufsize=BUFSIZE):
        return self.client.recv(bufsize)
        
    def close(self):
        if self.__client:
            self.__client.close()
            self.__client = None
            
    def __del__(self):
        self.close()
        

class SerialBase(object):
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
        self.serialObj.write(cmd)
        
    def reciver(self,bufsize=None):
        if bufsize:
            return self.serialObj.read(bufsize)
        return self.serialObj.readline()
        
    def close(self):
        if self.__serObj is not None:
            self.__serObj.close()
            self.__serObj = None
            
    def __del__(self):
        self.close()
        
if __name__=='__main__':
    print(bytes.fromhex('F1 D9 0A 04 00 00 0E 34'))
    obj=SocketClient('10.100.5.225',4011)
    obj.send(bytes.fromhex('F1 D9 0A 04 00 00 0E 34'))
    for _ in range(100):
        print([obj.reciver()])