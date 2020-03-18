# -*- coding:utf-8 -*-
from typing import Union
from utils.Decorator import singleton
from utils.AutoSocket import AutoSocketClient
from components.device.android.adb import AdbClient

PORT10086 = 10086
PORT12306 = 12306


@singleton
class UiClient(object):
    gSocket = None

    def __init__(self, addr: Union[None, str, tuple]):
        self.addr = addr
        self.connect()

    def connect(self):
        """
        @summary:PC连接手机
        @param addr:手机sn号或者(ip,port)
        @attention :
        """
        if isinstance(self.addr, tuple):
            host, port = self.addr
            self._connect_wifi(host, port)
        self._connect_usb(self.addr)

    def _connect_usb(self, serial):
        adb_client = AdbClient()
        adb_client.must_one_device(serial)
        self._check_and_forward(adb_client, serial)

    def _check_and_forward(self, adb_client: AdbClient, serial=None):
        forward_list = adb_client.forward_list(serial)
        for forwardItem in forward_list:
            if forwardItem.serial == serial:
                port = forwardItem.local.split(':')[-1]
                self._connect_wifi('127.0.0.1', port)
        adb_client.forward(serial, PORT10086, PORT12306)
        self._connect_wifi('127.0.0.1', PORT10086)

    def _connect_wifi(self, host, port):
        self.gSocket = AutoSocketClient(host, port)

    def send_cmd(self, cmd):
        for i in range(3):
            try:
                self.gSocket.send(cmd)
                return
            except:
                self.gSocket.close()
                self.connect()


if __name__ == '__main__':
    ui = UiClient()
    ui.connect(('127.0.0.1',5037))