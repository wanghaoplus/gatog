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
cmdSETFRQ = [0xf1, 0xd9, 0xf4, 0x00, 0x04, 0x00, 0x80, 0xba, 0x8c, 0x01, 0xbf, 0xff]
cmdBOOTERASE_8020 = [0xf1, 0xd9, 0xf4, 0x05, 0x06, 0x00, 0x00, 0x00, 0x00, 0x90, 0x00, 0x00, 0x8f, 0x95]
cmdBOOTERASE_8040 = [0xf1, 0xd9, 0xf4, 0x05, 0x06, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x0f, 0x25]
cmdCFGRST = [0xf1, 0xd9, 0x06, 0x40, 0x01, 0x00, 0x00, 0x47, 0x21]
cmdBOOTBAUD = [0xf1, 0xd9, 0xf4, 0x03, 0x08, 0x00, 0x00, 0xc2, 0x01, 0x00, 0x00, 0xc2, 0x01, 0x00, 0x85, 0x7d]
cmdFLASHUNLOK = [0xF1, 0xD9, 0xF4, 0x08, 0x04, 0x00, 0x00, 0x02, 0x00, 0x80, 0x82, 0x76]

class UpgradeForBoot(object):
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
    
    def read2Buffer(self, filename):
        buf = bytearray(os.path.getsize(filename))
        with open(filename, 'rb') as f:
            f.readinto(buf)
        return buf
    
    def sendfwboot(self, addr, cnt, data, lenth):
        cmd = [0xF1, 0xD9, 0xF4, 0x05, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        ck = [0, 0]
        ck1 = 0
        ck2 = 0
        lenth_full = lenth + 6
        cmd[4] = lenth_full & 0xFF
        cmd[5] = (lenth_full >> 8) & 0xFF
        cmd[6] = addr & 0xFF
        cmd[7] = (addr >> 8) & 0xFF
        cmd[8] = (addr >> 16) & 0xFF
        cmd[9] = (addr >> 24) & 0xFF
        cmd[10] = cnt & 0xFF
        cmd[11] = (cnt >> 8) & 0xFF
        for i in range(0, 12):
            if (i > 1):
                ck1 += cmd[i]
                ck2 += ck1
    
        for i in range(0, lenth):
            ck1 += data[i]
            ck2 += ck1
    
        ck[0] = ck1 & 0xFF
        ck[1] = ck2 & 0xFF
    
        self.sendCommand(bytes(bytearray(cmd)))
        self.sendCommand(bytes(bytearray(data)))
        self.sendCommand(bytes(bytearray(ck)))
    
    def fw_update_boot(self, data, lenth, address):
        progress_status = 0
        count = int(lenth / 1024)
        for i in range(1, count):
            self.sendfwboot(address + i * 0x400, i, data[i * 1024:(i + 1) * 1024], 1024)
            time.sleep(0.01)
            recv = self.reciver(10)
    #        print(str(recv))
            percentage_done = int((10*i/count))%10
            if(percentage_done > progress_status):
                progress_status = percentage_done
                print(str(percentage_done*10)+"%")
        last = count * 1024
        self.sendfwboot(address + count * 0x400, count, data[last: lenth], lenth - last)
        recv = self.reciver(10)
        print(str(100)+"%")
    #    print(str(recv))
        count += 1
        self.sendfwboot(address, count, data[0:1024], 1024)
        recv = self.reciver(10)
    #    print(str(recv))
    
        self.sendCommand(bytes(bytearray(cmdCFGRST)))
        self.sendCommand(bytes(bytearray(cmdBOOTBAUD)))
    
    def fastboot(self, chipType, path ):
        if chipType.startswith('hd802'):
            address = 0x90000000
            cmdBOOTERASE = cmdBOOTERASE_8020
    
        elif chipType.startswith('hd804'):
            address = 0x100000
            cmdBOOTERASE = cmdBOOTERASE_8040
        else:
            return -1,'没有此芯片类型：%s'%chipType
        cyfm_file = self.read2Buffer(path)
    
        if (cyfm_file[0] != 0x0A or cyfm_file[1] != 0x11):
            PRINTI("Fail, cyfm file invalid: 01", 1)
            return -1,'升级失败'
        out = open("temp_file", "wb")
        out.write(cyfm_file[12:])  # extract .gz file
        out.close()
    
        try:
            with gzip.open("temp_file", 'rb') as f:
                file_content = bytearray(f.read())
        except:
            PRINTI("Fail, cyfm file invalid: 02", 1)
            return -1,'升级失败'
    
        # verify MD5
        file_md5 = hashlib.md5(file_content[16:]).digest()
        if (file_md5 != file_content[0:16]):
            PRINTI("Fail, cyfm file invalid: 03", 1)
            return -1,'升级失败'
    
        print("Verify MDS")
        firmware_file = list(file_content[16:])  # firmware to be loaded
        firmware_length = len(firmware_file)
        f.close()
        os.remove("temp_file")
    
        self.sendCommand(bytes(bytearray(cmdMONVER)))
        time.sleep(0.02)
        print("MONVER")
    
        self.sendCommand(bytes(bytearray(cmdFLASHUNLOK)))
        time.sleep(0.1)
        print("Flash unlock")
        self.sendCommand(bytes(bytearray(cmdSETFRQ)))
        time.sleep(0.02)
        print("Set frequency")
        self.sendCommand(bytes(bytearray(cmdBOOTERASE)))
        time.sleep(0.2)
        print("Boot erase")
    
        self.fastbootObj.reset_input_buffer()
        self.fastbootObj.reset_output_buffer()
    
        self.fw_update_boot(firmware_file, firmware_length, address)
        self.close()
        PRINTI("Firmware download completed!", 0)
        return 0,'boot升级结束'
    
    