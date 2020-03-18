#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/27 21:01
# @Author  : shaochanghong
# @Site    : 
# @File    : Labsat.py
# @Software: PyCharm
import time
from telnetlib import Telnet
from aw.core.Input import LBSException
from aw.core.Input import SUC
from aw.core.Input import FAIL
from aw.core.Input import AutoPrint


class GssLabsat(object):
    tn = None
    IP = None
    port = None
    connectTimes = 0
    LabsatType = None
    LABSAT = "LABSAT"
    WIDEBAND = "WIDEBAND"
    FINISH_CODE = {LABSAT:"LABSATV3 >", WIDEBAND:"LABSAT_V3 >\r\r\n"}
    
    def __init__(self, ip="LABSATV3_039168", port=23):
        if "LABSAT" in ip.upper():
            GssLabsat.IP = ip.split("_")[1]
            GssLabsat.port = port
            GssLabsat.LabsatType = GssLabsat.LABSAT
        elif "WIDEBAND" in ip.upper():
            GssLabsat.IP = ip.split("_")[1]
            print(ip.upper(), port)
            GssLabsat.port = port
            GssLabsat.LabsatType = GssLabsat.WIDEBAND
        else:
            raise LBSException("set is not labsat,please check it.")
            
    def __del__(self):
        if GssLabsat.tn is not None:
            GssLabsat.tn.write("quit\r\n".encode("gbk"))
            GssLabsat.tn.close()
            GssLabsat.tn = None
            time.sleep(1)
            
    def __labsatConnect(self):
        if GssLabsat.tn is None:
            GssLabsat.tn = Telnet(GssLabsat.IP, GssLabsat.port)
            time.sleep(1)
            return GssLabsat.tn.read_very_eager()
        
    def aw_labsatDisconnect(self):
        if GssLabsat.tn is not None:
            GssLabsat.tn.write("quit\r\n".encode("gbk"))
            GssLabsat.tn.close()
            GssLabsat.tn = None
            time.sleep(1)
        return SUC, ''
    
    def __labsatSendCmd(self, cmd):
        msg = None
        for _ in range(2):
            if GssLabsat.tn is None:
                self.__labsatConnect()
            try:
                msg = self.__sendCmd(cmd)
                if "ERR" in msg:
                    continue
                elif "Connection is already in use by" in msg:
                    raise LBSException(msg)
                return msg
            except:
                self.aw_labsatDisconnect()
        return msg
    
    def __sendCmd(self, cmd):
        try:
            finishCode = GssLabsat.FINISH_CODE[GssLabsat.LabsatType]
            cmd = cmd + "\r\n"
            GssLabsat.tn.write(cmd.encode("gbk"))
            msg = GssLabsat.tn.read_until(finishCode.encode("gbk"), 60).decode("gbk")
            msg = msg.replace('\x1b[32m', '').replace('\r\n', '').replace('\x1b\x96', '').replace('\x1b[0m', '').replace('\x1b[22m', '').replace('\x1b[1m', '').replace('\x1b[31m', '')
        except:
            self.aw_labsatDisconnect()
        return msg
    
    def __checkCommandResult(self, msg, expect='OK'):
        if "ERR" in msg:
            self.aw_labsatDisconnect()
            return FAIL, "expect is %s,but result is %s" % (expect, msg)
        if expect in msg:
            return SUC, msg
        finishCode = GssLabsat.FINISH_CODE[GssLabsat.LabsatType]
        msg = GssLabsat.tn.read_until(finishCode.encode("gbk"), 60).decode("gbk")
        msg = msg.replace('\x1b[32m', '').replace('\r\n', '').replace('\x1b\x96', '').replace('\x1b[0m', '').replace('\x1b[22m', '').replace('\x1b[1m', '').replace('\x1b[31m', '')
        if expect in msg:
            return SUC, msg
        return FAIL, msg
    
    def __labsatGetPlayState(self, state="IDLE"):
        msg = self.__labsatSendCmd("PLAY:?")
        self.__checkCommandResult(msg, "PLAY")
        if state in msg:
            return True
        return False
    
    def aw_labsatMuteSet(self, isMute):
        cmd = "MUTE:Y" if isMute else "MUTE:N"
        msg = self.__labsatSendCmd(cmd)
        return self.__checkCommandResult(msg, "OK")
    
    def aw_labsatStopPlay(self, timeout=30):
        """
        @summary: 停止播放场景
        """
        endTime = time.time() + timeout
        while time.time() < endTime:
            msg = self.__labsatSendCmd("PLAY:STOP")
            if msg is "":
                time.sleep(5)
            if "OK" in msg:
                return SUC, 'success'
        return FAIL, "fail"
    
    @AutoPrint(True)
    def aw_labsatPlay(self, fileName, moment=0, duration=0):
        """
        @summary: 播放场景
        @param fileName: 场景文件名称
        @param moment: 场景播放偏移量
        """
        if fileName is None:
            return FAIL, "has no this file"
        if not self.__labsatGetPlayState("IDLE"):
            if self.aw_labsatStopPlay()[0] == FAIL:
                return FAIL, "can not stop signal"
        if GssLabsat.LabsatType == GssLabsat.WIDEBAND:
            for i in range(2):
                msg = self.__labsatSendCmd("MEDIA:LIST")
                print("MEDIA:LIST", msg)
                if fileName in msg:
                    break
                elif fileName not in msg and i==1:
                    msg = self.__labsatSendCmd("MEDIA:CHDIR:..") 
                    print("MEDIA:CHDIR:..", msg)
                    break
                elif fileName not in msg and i==2:
                    return FAIL, "not find scene"
                
        for i in range(2):
            if duration != 0:
                msg = self.__labsatSendCmd("PLAY:FILE:" + fileName + ":FROM:" + str(moment) + ":FOR:" + str(duration))
            else:
                msg = self.__labsatSendCmd("PLAY:FILE:" + fileName + ":FROM:" + str(moment))
            print(msg)
            time.sleep(2)
            if GssLabsat.LabsatType == GssLabsat.WIDEBAND:
                if self.__labsatGetPlayState(fileName):
                    return SUC, 'start play signal'
            else:
                if self.__checkCommandResult(msg, "OK")[0] == SUC and self.__labsatGetPlayState("PLAY:" + fileName):
                    return SUC, 'start play signal'
        return FAIL, 'play fail'
    
    def aw_labsatAddNoise(self, value):
        """
        @summary: 添加噪声
        @param value: 噪声大小
        """
        msg = self.__labsatSendCmd("NOISE:" + str(value))
        return self.__checkCommandResult(msg, "OK")

    def aw_labsatATTN(self, value=0):
        """
        @summary: 调节信号大小
        @param value: 
        """
        msg = self.__labsatSendCmd("ATTN:" + str(value))
        return self.__checkCommandResult(msg, "OK")
    
