#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/17 13:12
# @Author  : shaochanghong
# @Site    : 
# @File    : DeviceManager.py
# @Software: PyCharm
from autotest.components.device.android.adb import AdbClient


class AdbManager(object):
    def __init__(self):
        pass

    @staticmethod
    def execShellCmd(sn, cmd):
        return AdbClient().shell(sn, cmd)


class AndroidManager(object):
    def __init__(self):
        pass

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


class IosManager(object):
    pass