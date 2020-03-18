#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/1 21:00
# @Author  : wanghao
# @Site    : 
# @File    : TestBoard.py
import time
from aw.core.Input import SUC
from aw.core.Input import AutoPrint
from aw.core.SerialBase import SerialBase
from aw.core.SocketBase import SocketClient


class TestBoard():
    
    def __init__(self, connectType, testBoard, baud=115200):
        self.boardObj = None
        self.initTestBoard(connectType, testBoard, baud)
        
    def initTestBoard(self, connectType, testBoard, baud):
        
        if connectType.lower() == "socket":
            ip = testBoard.split('_')[0]
            port = int(testBoard.split('_')[1])
            sock = SocketClient(host=ip, port=port)
            sock.connect()
            self.boardObj = sock
        elif connectType.lower() == 'usb':
            serl = SerialBase(testBoard, baud)
            serl.connect()
            self.boardObj = serl
            
#     @AutoPrint(True)            
    def aw_testBoardPowerSet(self,  mode, dutNum, pwrStatus = 0, pwrDelayTime = 0):
        '''
        @summary: 设置测试板断电上电方式
        @param pwrType:电源模式选择
        @param main:主电
        @param back:备电
        @param boot:调试模式
        @param reset: reset gpio 拉低
        @param prtrg: prtrg gpio 拉低
        @param dutNum: 0-15 选择对应的dut 16 全部dut
        @param pwrStatus: 0 下电  1 上电
        @param pwrDelayTime:
        @param reset:  延迟时间   单位毫秒
        '''
        cmd = self.powerCommand(mode, dutNum, pwrStatus, pwrDelayTime)
        self.boardObj.send(cmd)
        time.sleep(1)
        self.boardObj.close()
        return SUC, 'OK'

    
    def binaryGenCrc(self, src_data):
        checksum1 = 0
        checksum2 = 0
        length = len(src_data)
        for i in range(0, length):
            checksum1 += src_data[i]
            checksum2 += checksum1
        checksum2 &= 0xFF
        result = ((checksum1 << 8) + checksum2)&0xFFFF
        return result
    
    def powerCommand(self, pwrType ,dutNum , pwrStatus = 0, pwrDelayTime = 0):
        '''
        @summary: 设置测试板断电上电方式
        @param pwrType:电源模式选择
        @param main:主电
        @param back:备电
        @param boot:调试模式
        @param reset: reset gpio 拉低
        @param prtrg: prtrg gpio 拉低
        @param dutNum: 0-15 选择对应的dut 16 全部dut
        @param pwrStatus: 0 下电  1 上电
        @param pwrDelayTime:
        @param reset:  延迟时间   单位毫秒
        '''
        print(pwrType, dutNum, pwrStatus)
        if(pwrType != 'main' and pwrType != 'back' and  pwrType != 'boot' and pwrType != 'reset' and pwrType != 'prtrg'):
            print("Please choice the power type!")
            return
        row = 0x0
        module = 0x0
        pwrMode = 0x00
        pwrNum = 0x00
    
        if(pwrStatus == 0):
            pwrMode = 0x00
        elif(pwrStatus == 1):
            pwrMode = 0x01
        elif (pwrStatus == 3):
            pwrMode = 0x03
        if (pwrType == 'main' or pwrType == 'back'):
            send_data = bytearray(10)
            if (dutNum < 4):
                row = 0x1
            elif (dutNum < 8):
                row = 0x2
            elif (dutNum < 12):
                row = 0x3
            elif (dutNum < 16):
                row = 0x4
            elif (dutNum == 16):
                row = 0xF
    
            tmpnum = dutNum % 4
            if (dutNum == 16):
                module = 0xF
            elif (tmpnum == 0):
                module = 0x1
            elif (tmpnum == 1):
                module = 0x2
            elif (tmpnum == 2):
                module = 0x3
            elif (tmpnum == 3):
                module = 0x4
            pwrNum = (row << 4) | module
    
            send_data[0] = 0xF1
            send_data[1] = 0xD9
            send_data[2] = 0xFC
            if(pwrType == 'main'):
                send_data[3] = 0x01
            elif(pwrType == 'back'):
                send_data[3] = 0x02
            send_data[4] = 0x02
            send_data[5] = 0x00
            send_data[6] = pwrNum
            send_data[7] = pwrMode
            crc = self.binaryGenCrc(send_data[2:8])
            send_data[8] = (crc>>8)&0xFF
            send_data[9] = crc&0xFF
    
        elif(pwrType == 'boot'):
            send_data = bytearray(9)
            send_data[0] = 0xF1
            send_data[1] = 0xD9
            send_data[2] = 0x06
            send_data[3] = 0x21
            send_data[4] = 0x01
            send_data[5] = 0x00
            send_data[6] = dutNum
            crc = self.binaryGenCrc(send_data[2:7])
            send_data[7] = (crc >> 8) & 0xFF
            send_data[8] = crc & 0xFF
    
        elif (pwrType == 'reset'):
            send_data = bytearray(11)
            send_data[0] = 0xF1
            send_data[1] = 0xD9
            send_data[2] = 0x06
            send_data[3] = 0x23
            send_data[4] = 0x03
            send_data[5] = 0x00
            send_data[6] = dutNum
            send_data[7] = pwrDelayTime & 0xFF
            send_data[8] = pwrDelayTime >>8
            crc = self.binaryGenCrc(send_data[2:9])
            send_data[9] = (crc >> 8) & 0xFF
            send_data[10] = crc & 0xFF
        elif (pwrType == 'prtrg'):
            send_data = bytearray(10)
    
            send_data[0] = 0xF1
            send_data[1] = 0xD9
            send_data[2] = 0x06
            send_data[3] = 0x26
            send_data[4] = 0x02
            send_data[5] = 0x00
            send_data[6] = dutNum
            send_data[7] = pwrMode
            crc = self.binaryGenCrc(send_data[2:8])
            send_data[8] = (crc>>8)&0xFF
            send_data[9] = crc&0xFF
    
        return (bytes(send_data))
        
        

if __name__ == "__main__":
#     print(bytes.fromhex('F1 D9 FC 02 02 00 FF 00 FF F8'))
    print(TestBoard('aaa', 'COM31').powerCommand('back', 16, 1))
    pass
#     cmd_pwr_main_all_on = power_command('main', 16, pwrStatus=1)
#     cmd_pwr_back_all_on = power_command('back', 16, pwrStatus=1)
#     cmd_pwr_main_all_off = power_command('main', 16, pwrStatus=0)
#     cmd_pwr_back_all_off = power_command('back', 16, pwrStatus=0)
#     cmd_reset_100_all = power_command('reset', 16, pwrDelayTime=100)
#     cmd_reset_500_all = power_command('reset', 16, pwrDelayTime=500)
#     cmd_prtrg_on_all = power_command('prtrg', 16, pwrStatus=1)
#     cmd_prtrg_off_all = power_command('prtrg', 16, pwrStatus=0)
#     cmd_boot_all = power_command('boot', 16)
#     cmd_prtrg_input_all = power_command('prtrg', 16, pwrStatus=3)

    
