#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/1 21:00
# @Author  : wanghao
# @Site    : 
# @File    : USBBase.py

from ctypes import *
import os
import time


def pyInitUSB():
    global classDll
    addr = os.getcwd()
    path = addr + "\\"
    classDll = CDLL(path + r"Usb_Interface.dll")
    iusbtotal = classDll.InitUsb()
    return iusbtotal

class CCUSBport:
    global classDll
    handle = 0

    def __init__(self, USBnum):
        addr = os.getcwd()
        path = addr + "\\"
        self.classDll = CDLL(path + r"Usb_Interface.dll")
        self.handle = self.classDll.gConnectToDriver(USBnum)

    def close(self):
        self.classDll.gDisConToDriver(self.handle)

    def usb_read(self, readnum):
        readbufPoint = (c_char * 4096)()
        ireadnum = int()
        self.classDll.ReadFromDriver.argtypes = [c_int, c_char_p, c_int]
        ireadnum = self.classDll.ReadFromDriver(self.handle, readbufPoint, readnum)
        readbuf = string_at(readbufPoint, ireadnum)#byte
        del readbufPoint
        return readbuf#bytes
        #return readbuf.decode()#string


    def usb_write(self, writedata):
        a = (c_char * len(writedata))()
        for i in range(0, len(writedata)):
            a[i] = writedata[i]
        self.classDll.WriteToDriver( self.handle, byref(a),  len(a))
        del a


if __name__ == "__main__":
    iusbtotal = int()
    hd = int()
    x = 0
    sendcold = [0xF1, 0xD9, 0x06, 0x40, 0x01, 0x00, 0x01, 0x48, 0x22]

    iusbtotal = pyInitUSB()
    if iusbtotal > 0:
        port0 = CCUSBport(0)
    if port0.handle <= 0:
        print("port open failed")

    #time.sleep(1000000)
    while 1:
        readbuf = port0.usb_read(4096)
        x = x+1
        if x == 5:
            port0.usb_write(sendcold)
        print(readbuf)
        time.sleep(1)
    port0.close()

