#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/2/9 11:06
# @Author  : shaochanghong
# @Site    : 
# @File    : SocketBase.py
import socket
from aw.core.Input import PRINTE
from aw.core.Input import PRINTTRAC
from aw.core.parselog.ParseLog import LogChangeListner
CONNECT_TIMEOUT = 5
CONNECT_RETRY_TIMES = 10
BUFSIZE = 1024


class SocketClient(LogChangeListner):
    __host = None
    __port = None
    __client = None
    stopRecvFlag = False

    def __init__(self, host=None, port=None):
        super(SocketClient, self).__init__()
        self.__host = host
        self.__port = port
        self.deviceSN = host + "_" + str(port)

    @property
    def client(self):
        if (self.__client is None) and (self.stopRecvFlag is False):
            self.__client = self._connect()
        return self.__client
    
    def _connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for connTimes in range(1, CONNECT_RETRY_TIMES + 1):
            try:
                s.connect((self.__host, self.__port))
                return s
            except:
                s.close()
                PRINTE('第%s次连接失败...' % connTimes)
                if connTimes == CONNECT_RETRY_TIMES:
                    PRINTTRAC('请检查网络是否异常')
                    raise
                
    def connect(self):
        if self.__client is None:
            self.__client = self._connect()

    def send(self, cmd):
        print(cmd)
        self.client.send(cmd)
        
    def startReciver(self):
        while self.stopRecvFlag is False:
            try:
                recvData = self.client.recv(BUFSIZE)
                self.parseData(recvData)
            except:
                pass
            
    def parseData(self, msg):
        self.onLogChange(msg)
    
    def stopReciver(self):
        self.stopRecvFlag = True
        self.close()

    def close(self):
        if self.client:
            self.client.close()
            self.__client = None
            
    def __del__(self):
        self.close()

if __name__ == '__main__':
    so = SocketClient('10.100.5.225', 4003)
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
#     time.sleep(10)
    
    