#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2020/2/19 14:19
# @Author  : wanghao
# @Site    :
# @File    : UserModeFWUpgrade.py
import os
import time
import gzip
import hashlib
from aw.core.Input import PRINTI
from aw.core.Input import PRINTTRAC
from aw.core.Input import AutoPrint
from aw.utils.deviceupgrade.UpgradeBase import SerialBase
from aw.utils.deviceupgrade.UpgradeBase import SocketClient

cmdMONVER = [0xf1, 0xd9, 0x0a, 0x04, 0x00, 0x00, 0x0e, 0x34]
cmdNMEAOFF = [0xf1, 0xd9, 0x06, 0x01, 0x03, 0x00, 0xf0, 0x00, 0x00, 0xfa, 0x0f,
              0xf1, 0xd9, 0x06, 0x01, 0x03, 0x00, 0xf0, 0x02, 0x00, 0xfc, 0x13,
              0xf1, 0xd9, 0x06, 0x01, 0x03, 0x00, 0xf0, 0x03, 0x00, 0xfd, 0x15,
              0xf1, 0xd9, 0x06, 0x01, 0x03, 0x00, 0xf0, 0x04, 0x00, 0xfe, 0x17,
              0xf1, 0xd9, 0x06, 0x01, 0x03, 0x00, 0xf0, 0x05, 0x00, 0xff, 0x19,
              0xf1, 0xd9, 0x06, 0x01, 0x03, 0x00, 0xf0, 0x06, 0x00, 0x00, 0x1b,
              0xf1, 0xd9, 0x06, 0x01, 0x03, 0x00, 0xf0, 0x07, 0x00, 0x01, 0x1d]
cmdCFGFWUP = [0xf1, 0xd9, 0x06, 0x50, 0x01, 0x00, 0x10, 0x67, 0x71, 0x00]
cmdCFGPRT = [0xf1, 0xd9, 0x06, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xc2, 0x01, 0x00, 0xd1, 0xe0]
cmdACKACK = [0xf1, 0xd9, 0x06, 0x40, 0x01, 0x00, 0x00, 0x47, 0x21]

data1st = [0x67, 0x6e, 0x73, 0x73, 0x32, 0x36, 0x72, 0x65, 0x6c, 0x31, 0x36, 0x2e, 0x67, 0x7a, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

datalast = [0] * 128

class UpgradeForUser(object):
    fastbootObj=None
    
    def __init__(self, connectType, port, ip=None):
        if connectType.lower() == "socket":
            self.fastbootObj = SocketClient(host=ip, port=int(port))
        elif connectType.lower() == 'usb':
            self.fastbootObj = SerialBase(port)
        else:
            raise Exception('参数有误')
        self.fastbootObj.connect()
    
    def sendCommand(self,cmd):
        self.fastbootObj.send(cmd)
        
    def close(self):
        self.fastbootObj.close()
        
    def reciver(self,bufSize=1024):
        return self.fastbootObj.reciver(bufSize)
    
#     @AutoPrint(True)
    def upgrade(self, data, lenth):
        count = int(lenth / 1024)
        self.userSendFW(0x01, 0x00, data1st, 128)
        recv = self.fastbootObj.reciver(7)
        print("recv", str(recv))
        for i in range(1, count+1):
            self.userSendFW(0x02, i, data[(i - 1) * 1024:(i) * 1024], 1024)
            recv = self.fastbootObj.reciver(1)
        last = count * 1024
        print("the last data")
        self.userSendFW(0x02, (count+1), data[last: lenth], lenth - last)
        time.sleep(0.05)
        recv = self.fastbootObj.reciver(1)
        ymodem_eot_cmd = "04"
        self.sendCommand(bytearray.fromhex(ymodem_eot_cmd))
        self.userSendFW(0x01, 0, datalast, 128)
        time.sleep(0.05)
        recv = self.fastbootObj.reciver(1)
    
    def userSendFW(self, cmd, cnt, data, lenth):
        if (lenth!=1024) and (lenth!=128):
            flag = 1
            lenth_tmp = 1024
        else:
            flag = 0
            lenth_tmp = lenth
        send_data = bytearray(lenth_tmp + 3)
        send_data[0]=cmd
        send_data[1]=cnt&0xFF
        send_data[2]= 0xFF - (cnt & 0xFF)
        write_ptr = 3
        for i in range(0, lenth):
            send_data[write_ptr] = data[i]
            write_ptr += 1
        if flag==1:
            for i in range(lenth, lenth_tmp):
                send_data[write_ptr] = 0x1a
                write_ptr += 1
        crc16 = self.calCrc(send_data[3:], lenth_tmp)
        # crc
        send_data.append((crc16>>8)&0xFF)
        send_data.append(crc16&0xFF)
        self.sendCommand(bytes(send_data))
    
    def calCrc(self,data, lenth):
        crc = int()
        crc = 0
        for i in range(0, lenth):
            crc = crc ^ (data[i] << 8)
            for j in range(0, 8):
                if ((crc & 0x8000) != 0):
                    crc = crc << 1 ^ 0x1021
                else:
                    crc = crc << 1
        return (crc & 0xFFFF)
    
    def read2Buffer(self, filename):
        buf = bytearray(os.path.getsize(filename))
        with open(filename, 'rb') as f:
            f.readinto(buf)
        return buf
    
    def analysisImg(self, cyfm_file):
        if (cyfm_file[0] != 0x0A or cyfm_file[1] != 0x11):
            PRINTI("Fail, cyfm file invalid: 01")
            return -1
        out = open("temp_file", "wb")
        out.write(cyfm_file[12:])  # extract .gz file
        out.close()
        # wait for file closed
        while (out.closed == False):
            pass
        print("File closed")
        #Gzip img
        try:
            with gzip.open("temp_file", 'rb') as f:
                file_content = bytearray(f.read())
                f.close()
                while (f.closed == False):
                    pass
        except:
            PRINTI("Fail, cyfm file invalid: 02")
            return -1
        # verify MD5
        file_md5 = hashlib.md5(file_content[16:]).digest()
        if (file_md5 != file_content[0:16]):
            PRINTI("Fail, cyfm file invalid: 03")
            return -1
        print("Verify MDS")
        os.remove("temp_file")
        return file_content
    
    @AutoPrint(True)
    def fastboot(self, versionFile):
        try:
            cyfm_file = self.read2Buffer(versionFile)
            file_content = self.analysisImg(cyfm_file)  #img 校验
            if file_content==-1:
                return -1,'img校验失败'
        
            # firmware to be loaded
            firmware_file = list(file_content[16:])  #升级包 内容
            firmware_length = len(firmware_file)        
        
            # 发送MONVER
            self.sendCommand(bytes(bytearray(cmdNMEAOFF)))
            time.sleep(1)
        
            PRINTI('发送命令让设备进入升级模式...')
            self.sendCommand(bytes(bytearray(cmdCFGFWUP)))
         
            PRINTI('监测进入升级模式...')
            recv = b'0'
            recvlast = b'1'
            recvCont = 0
            while (recv != b'C' and recvlast != b'C' and recvCont < 512):
                recvlast = recv
                recv = self.fastbootObj.reciver(1)
                recvCont += 1
            if(recvCont < 512):
                PRINTI("into fwup mode succses")
            else:
                PRINTI("into fwup mode failed")
                return -1,'进入升级模式失败'
        
            PRINTI('开始升级...')
            self.upgrade(firmware_file, firmware_length)
            self.sendCommand(bytes(bytearray(cmdACKACK)))
            self.sendCommand(bytes(bytearray(cmdCFGPRT)))
            self.sendCommand(bytes(bytearray(cmdMONVER)))
            self.close()
            return 0, '升级结束'
        except:
            PRINTTRAC()
            return -1,'升级失败'
    

if __name__ == '__main__':
    from aw.utils.deviceupgrade.Config import FASTBOOT_CONF
    for devieDict in FASTBOOT_CONF:
        startTime=time.time()
        #首先确保芯片为user模式
        ip = devieDict.get('ip')
        port = devieDict.get('port')
        firmware = devieDict.get('firmware')
        fastboot=UpgradeForUser('socket',port,ip)
        fastboot.fastboot(firmware)
        time.sleep(1)
        fastboot.checkFastbootSuc(firmware)
        print(time.time()-startTime)
