#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/03/11 09:17
# @Author  : shaochanghong
# @Site    : 
# @File    : VAM.py
import time
from telnetlib import Telnet
from aw.core.Input import SUC
from aw.core.Input import FAIL
from aw.core.Input import AutoPrint
from aw.core.Input import PRINTTRAC


class JXVAM(object):
    tn = None
    ip = None
    port = None

    def __init__(self, ip="10.100.5.176", port=3000):
        JXVAM.ip = ip
        JXVAM.port = port
        
    def __del__(self):
        self.__close()

    def __close(self):
        if JXVAM.tn is not None:
            JXVAM.tn.close()
            JXVAM.tn = None

    def __connectJXVAM(self):
        if JXVAM.tn is None:
            JXVAM.tn = Telnet(JXVAM.ip, JXVAM.port)
            JXVAM.tn.write("*IDN?\r\n".encode())
            msg=JXVAM.tn.read_until('\r\n'.encode()).decode()
            time.sleep(1)
            if "Jiexi Tech" not in msg:
                raise Exception("connect vam fail.")
            
    def __vamSendCommand(self, command):
        try:
            self.__connectJXVAM()
            try:
                command=command+'\r\n'
                JXVAM.tn.write(command.encode())
            except:
                self.__close()
                self.__connectJXVAM()
                JXVAM.tn.write(command)
            msg = JXVAM.tn.read_until('\r\n'.encode()).decode().strip('\r\n')
        except:
            PRINTTRAC()
        return msg
    
    @AutoPrint(True)
    def aw_attSingleChannel(self, ch, value):
        '''
        @summary: 控制某通道的衰减值
        @param ch: 取值为1~256，值为正整数
        @param value: 取值0-62 62.5-93，步进为0.5即是0.5的整数倍，62.5-93代表关断状态
        @return: (SUC,'OK') or (FAIL,'设置失败')
        @author: shaochanghong
        '''
        attCmd = 'SET:%s:%s' % (str(ch), str(value))
        ret = self.__vamSendCommand(attCmd)
        if 'CMDERR' in ret:
            return FAIL, '输入的命令有误'
        elif 'FAIL' in ret:
            return FAIL, '设置失败'
        return SUC, 'OK'
    
    @AutoPrint(True)
    def aw_getSingleChannelDB(self, ch):
        '''
        @summary: 获取某通道的衰减值
        @param ch: 取值为1~256，值为正整数
        @return: (SUC,衰减值) or (FAIL,'设置失败')
        @author: shaochanghong
        '''
        attCmd = 'READ:%s' % str(ch)
        ret = self.__vamSendCommand(attCmd)
        if 'CMDERR' in ret:
            return FAIL, '输入的命令有误'
        elif 'FAIL' in ret:
            return FAIL, '获取失败'
        return SUC, ret.split(':')[-1]
    
    @AutoPrint(True)
    def aw_attMultiChannel(self, chDict:dict):
        '''
        @summary: 控制多个通道的衰减值
        @param ch: 取值为1~256，值为正整数
        @param value: 取值0-62或62.5-93，步进为0.5即是0.5的整数倍，62.5-93代表关断状态
        @return: (SUC,'OK') or (FAIL,'设置失败')
        @author: shaochanghong
        '''
        cmdList = [str(ch) + ',' + str(2 * value) for ch, value in chDict.items()]
        attCmd = 'SETM:' + ':'.join(cmdList)
        ret = self.__vamSendCommand(attCmd)
        if 'CMDERR' in ret:
            return FAIL, '输入的命令有误'
        elif 'FAIL' in ret:
            return FAIL, '设置失败'
        return SUC, 'OK'
    
    @AutoPrint(True)
    def aw_getMultiChannelDB(self, chList):
        '''
        @summary: 获取多个通道的衰减值
        @param ch: 取值为1~256，值为正整数
        @return: (SUC,衰减值) or (FAIL,'设置失败')
        @author: shaochanghong
        '''
        attCmd = 'READM:' + ':'.join([str(ch) for ch in chList])
        ret = self.__vamSendCommand(attCmd)
        if 'CMDERR' in ret:
            return FAIL, '输入的命令有误'
        elif 'FAIL' in ret:
            return FAIL, '获取失败'
        retDict = {}
        retSplit = ret.split(':')[1:]
        for msg in retSplit:
            ch = msg.split(',')[0]
            value = msg.split(',')[1]
            retDict[ch] = int(value)/2
        return SUC, retDict
    
    @AutoPrint(True)
    def aw_clearVamErrState(self):
        '''
        @summary: 清除设备错误状态记录
        @return: (SUC,'OK') or (FAIL,'fail')
        @author: shaochanghong
        '''
        cmd = '*CLS'
        ret = self.__vamSendCommand(cmd)
        if '0' in ret:
            return SUC, 'OK'
        return FAIL, 'fail'
    
if __name__=='__main__':
    JXVAM('10.100.5.176',3000).aw_getMultiChannelDB(['1','2','17'])
