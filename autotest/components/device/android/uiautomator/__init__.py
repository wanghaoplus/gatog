# -*- coding: utf-8 -*-

__author__ = 'shaochanghong'
__summary__ = 'uiautomator模块'

import re
from .connect import PORT12306
from .connect import UiClient

ip_pattern = re.compile('\d+.\d+.\d+.\d+')


class Device(object):
    ui = None

    def __init__(self, addr=None):
        """
        :param addr: None/手机sn/IP
        """
        if addr is not None:
            if re.match(ip_pattern, addr):
                self.ui = UiClient((addr, PORT12306))
        else:
            self.ui = UiClient(addr)
        self.ui.connect(addr)

    def click(self, x, y):
        pass

    def clickById(self, id):
        pass

    def clickByText(self, text):
        pass

    def clickByImage(self, image):
        pass

    def screenOn(self):
        pass

    def screenOff(self):
        pass

    def goBack(self):
        pass

    def goHome(self):
        pass

    def press(self, keyCode):
        pass

    def getTextById(self, id):
        pass


if __name__ == '__main__':
    Device()
