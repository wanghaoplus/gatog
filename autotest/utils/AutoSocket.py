# -*- coding:utf-8 -*-
import socket

CONNECT_TIMEOUT = 5
MAX_BACKLOG = 5000


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

    def close(self):
        if self.client:
            self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()


class AutoSocketServer(object):
    __server = None

    def __init__(self, host=None, port=None):
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
        while 1:
            conn, addr = self.__server.accept()
            while 1:
                msg = conn.recv(1024)
                if len(msg) == 0:
                    break










