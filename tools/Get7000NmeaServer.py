# -*- coding: utf-8 -*-
import os
import time
import shutil
import socket

CONNECT_TIMEOUT = 5
MAX_BACKLOG = 5000
POS_APP_LOG_PATH = r'D:\posapp\logs'
DST_PATH = r'C:\posapp\logs'


class AutoSocketServer(object):
    __server = None

    def __init__(self, host='', port=9998):
        self.__host = host
        self.__port = port
        self.__server = self._bind()

    def _bind(self):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((self.__host, self.__port))
            server.listen(MAX_BACKLOG)
            return server
        except:
            server.close()
            raise

    def start_server(self):
        print('satrt server')
        while 1:
            conn, addr = self.__server.accept()
            msg = conn.recv(1024)
            recvMsg = msg.decode()
            if len(recvMsg) == 0:
                continue
            sceneId = eval(recvMsg).get('sceneId')
            print(sceneId)
            ret = self.get7000StandardNMEA(sceneId, False)
            if ret:
                conn.send(str({'state':'okay'}).encode('utf-8'))
            else:
                conn.send(str({'state':'fail'}).encode('utf-8'))
                
    def get7000StandardNMEA(self, sceneId, rmSrcFlag=True):
        logDirList = os.listdir(os.path.join(POS_APP_LOG_PATH, sceneId))
        logDirList.sort(reverse=True)
        srcPath = os.path.join(POS_APP_LOG_PATH, sceneId, logDirList[0], 'nmea.txt')
        if not os.path.exists(os.path.join(DST_PATH, sceneId)):
            os.makedirs(os.path.join(DST_PATH, sceneId))
        dstPath = os.path.join(DST_PATH, sceneId, 'nmea.txt')
        if not os.path.exists(srcPath):
            return False
        shutil.copyfile(srcPath, dstPath)
        if rmSrcFlag:
            shutil.rmtree(os.path.join(POS_APP_LOG_PATH, sceneId, logDirList[0]))
        return True

    
class AutoSocketClient(object):
    __client = None

    def __init__(self, host=None, port=None):
        self.__host = host
        self.__port = port
        self.__client = self._connect()

    @property
    def client(self):
        return self.__client

    def _connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(CONNECT_TIMEOUT)
        try:
            s.connect((self.__host, self.__port))
            return s
        except:
            s.close()
            raise

    def send(self, cmd={}):
        cmd = str(cmd).encode("utf-8")
        self.client.send(cmd)
        recvMsg = ''
        endTime = time.time() + 120
        while time.time() < endTime:
            try:
                msg = self.client.recv(1024)
                recvMsg = msg.decode()
                break
            except:
                time.sleep(2)
        print(recvMsg)

    def close(self):
        if self.client:
            self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()


if __name__ == '__main__':
    AutoSocketServer().start_server()
