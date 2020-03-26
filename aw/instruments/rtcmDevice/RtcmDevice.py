#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/03/26 12:00
# @Author  : wanghao
# @Site    : 
# @File    : RtcmData.py
# @Software: Vscode

from aw.core.SerialBase import SerialBase
from aw.core.Input import SUC
from aw.core.Input import FAIL
from aw.core.Input import PRINTTRAC
from aw.core.Input import getLbsCaseLogPath
from aw.core.Input import isSuc


class RtcmDevice(object):
    '''
        链接方式 serial ntrip socket
        IP、用户、密码
    '''
    isRecvSign = 0
    recvData = ""

    def __init__(self, connectType, ip = "127.0.0.0", port = 0, deviceNode = "", user = "", passwd = ""):
        self.connectType = connectType
        self.ip = ip
        self.port = port
        self.deviceNode = deviceNode
        self.user = user
        self.passwd = passwd
        self.socHandle = None
        
    def __DeviceConnect(self):
        if self.connectType == 'socket':
            import socket
            self.socHandle = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socHandle.settimeout(3)
            try:
                self.socHandle.connect((self.ip, self.port))
            except:
                PRINTTRAC('please check server right.')
                self.socHandle.close()
                return FAIL, 'please check server right.'

        elif self.connectType == 'serial':
            pass
        elif self.connectType == 'ntrip':
            pass

    def run(self):
        self.__DeviceConnect()
        import threading
        threadHandle = threading.Thread(target=self.receive, args=())
        threadHandle.setDaemon(True)
        threadHandle.start() 
 
    def send(self, msg):
        pass

    def receive(self):
        while True:
            if self.connectType == 'socket':
                self.recvData = self.socHandle.recv(4096)
                self.isRecvSign = 1
            elif self.connectType == 'serial':
                pass
            elif self.connectType == 'ntrip':
                pass

    