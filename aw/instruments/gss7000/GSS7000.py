#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/27 21:01
# @Author  : shaochanghong
# @Site    : 
# @File    : GSS7000.py
# @Software: PyCharm
import os
import time
import shutil
from telnetlib import Telnet
from aw.core.Input import SUC
from aw.core.Input import FAIL
from aw.core.Input import isSuc
from aw.core.Input import PRINTE
from aw.core.Input import PRINTTRAC
from aw.core.Input import AutoPrint
from aw.core.Input import getInstruments
from aw.core.Input import getLbsCaseLogPath

SIMU_STATUS_DICT = {"No scenario specified": 0,
                    "Loading": 1,
                    "Ready": 2,
                    "Arming": 3,
                    "Armed": 4,
                    "Running": 5,
                    "paused": 6,
                    "Ended": 7}
TRIGGER_MODE = {"SoftwareTrigger": 0,
                "Exit trigger immediately": 1,
                "Exit trigger on edge of next ipps": 2}


class GSS7000(object):
    tn = None
    ip = None
    port = None

    def __init__(self, ip="127.0.0.1", port=15650):
        GSS7000.ip = ip
        GSS7000.port = port

    def __del__(self):
        self.__close()

    def __close(self):
        if GSS7000.tn is not None:
            GSS7000.tn.close()
            GSS7000.tn = None

    def __connectGSS7000(self):
        if GSS7000.tn is None:
            GSS7000.tn = Telnet(GSS7000.ip, GSS7000.port)
            msg = self.__GSS7000SendCommand("*IDN?")
            time.sleep(2)
            data = msg.split("data")[1]
            ret = data.split(">")[1].split("<")[0]
            if "Spirent" not in ret:
                raise Exception("connect GSS7000 fail.")

    def __GSS7000SendCommand(self, command):
        try:
            self.__connectGSS7000()
            try:
                GSS7000.tn.write(command.encode("ascii"))
            except:
                self.__close()
                self.__connectGSS7000()
                GSS7000.tn.write(command.encode("ascii"))
            msg = GSS7000.tn.read_until("</msg>".encode("ascii")).decode("ascii")
            time.sleep(0.1)
        except:
            PRINTTRAC()
        if "error" in msg or "fatal" in msg:
            PRINTE("status error,please check it")
        return msg

    def __GSS7000GetStatus(self):
        msg = self.__GSS7000SendCommand("NULL")
        time.sleep(2)
        status = msg.split('status')[1]
        ret = status.split(">")[1].split("<")[0]
        return int(ret)
    
    @AutoPrint(True)
    def aw_GSS7000CheckExpectedStatus(self, expectStatus, expectStatus1=None, timeout=10):
        endTime = time.time() + timeout
        while time.time() < endTime:
            curStatus = self.__GSS7000GetStatus()
            if curStatus in [expectStatus, expectStatus1]:
                return SUC, curStatus
        return FAIL, curStatus

    def aw_GSS7000EnsureReady(self):
        """
        @summary:  确保当前为ready状态
        :return:
        """
        curStatus = self.__GSS7000GetStatus()
        if curStatus == SIMU_STATUS_DICT["Ready"]:
            return SUC, curStatus
        if curStatus == SIMU_STATUS_DICT["Armed"]:
            self.aw_GSS7000RunScenario()
            self.aw_GSS7000EndScenario(1)
        elif curStatus == SIMU_STATUS_DICT["Running"]:
            self.aw_GSS7000EndScenario(1)
        elif curStatus == SIMU_STATUS_DICT["Ended"]:
            self.aw_GSS7000RewindScenario()
        return self.aw_GSS7000CheckExpectedStatus(SIMU_STATUS_DICT["Ready"])

    def aw_GSS7000SelectScenario(self, fileName):
        """
        @summary:  选择要播放的场景
        @param fileName:场景名称
        @return: 
        """
        ret = self.aw_GSS7000CheckExpectedStatus(SIMU_STATUS_DICT["No scenario specified"], SIMU_STATUS_DICT["Ready"])
        if ret[0] != SUC:
            isSuc(self.aw_GSS7000EnsureReady())
        self.__GSS7000SendCommand("SC," + fileName)
        return self.aw_GSS7000CheckExpectedStatus(SIMU_STATUS_DICT["Ready"])

    def aw_GSS7000GetScenarioName(self):
        """
        @summary: 获取当前被加载的场景名称
        :return:
        """
        msg = self.__GSS7000SendCommand("SC_NAME,includepath")
        data = msg.split("data")[1]
        name = data.split(">")[1].split("<")[0]
        return SUC, name

    @AutoPrint(True)
    def aw_GSS7000GetScenarioDuration(self):
        """
        @summary: 获取当前场景时长
        @return:
        """
        msg = self.__GSS7000SendCommand("SC_DURATION")
        data = msg.split("data")[1]
        duration = data.split('>')[1].split('<')[0][:-1][1:]
        import re
        if re.match('\d+:\d+:\d+',duration):
            sec = int(duration.split(":")[-1])
            minute = int(duration.split(":")[-2])
            hour = int(duration.split(":")[-3])
            totalSeconds = sec + minute * 60 + hour * 3600
        else:
            sec = int(duration.split(" ")[-1].split(":")[-1])
            minute = int(duration.split(" ")[-1].split(":")[-2])
            hour = int(duration.split(" ")[-1].split(":")[-3])
            days = int(duration.split(" ")[-2])
            totalSeconds = sec + minute * 60 + hour * 3600 + days * 24 * 3600
        return SUC, totalSeconds

    def aw_GSS7000SetScenarioTrigger(self, mode):
        """
        @summary: 设置场景的trigger mode，必须在running前设置
        @param mode:0/1/2三种模式
        @return:
        """
        curStatus = self.__GSS7000GetStatus()
        if curStatus == SIMU_STATUS_DICT["Armed"]:
            self.aw_GSS7000RunScenario()
            self.aw_GSS7000EndScenario(1)
        elif curStatus == SIMU_STATUS_DICT["Running"]:
            self.aw_GSS7000EndScenario(1)
        elif curStatus == SIMU_STATUS_DICT["Ended"]:
            self.aw_GSS7000RewindScenario()
        isSuc(self.aw_GSS7000CheckExpectedStatus(SIMU_STATUS_DICT["Ready"], SIMU_STATUS_DICT["No scenario specified"]))
        return SUC, self.__GSS7000SendCommand("TR," + str(mode))

    def aw_GSS7000ArmScenario(self):
        """
        @summary: 准备播放场景
        @return:
        """
        isSuc(self.aw_GSS7000EnsureReady())
        self.__GSS7000SendCommand("AR")
        time.sleep(2)
        return self.aw_GSS7000CheckExpectedStatus(SIMU_STATUS_DICT["Arming"], SIMU_STATUS_DICT["Armed"])

    def aw_GSS7000ArmScenarioNoWait(self):
        """
        @summary: 仿真当前场景，且使得在场景仿真期间可运行其他命令
        @return:
        """
        isSuc(self.aw_GSS7000EnsureReady())
        self.__GSS7000SendCommand("AR_NOWAIT")
        time.sleep(2)
        return self.aw_GSS7000CheckExpectedStatus(SIMU_STATUS_DICT["Arming"], SIMU_STATUS_DICT["Armed"])

    def aw_GSS7000RunScenario(self):
        """
        @summary: 开始播放场景
        :return:
        """
        self.__GSS7000SendCommand("RU")
        return self.aw_GSS7000CheckExpectedStatus(SIMU_STATUS_DICT["Running"])

    def aw_GSS7000RunScenarioNoWait(self):
        """
        @summary: 立即播放场景
        :return:
        """
        self.__GSS7000SendCommand("RU_NOWAIT")
        return self.aw_GSS7000CheckExpectedStatus(SIMU_STATUS_DICT["Running"])

    def aw_GSS7000EndScenario(self, endType=1, logOption=None, timestamp="-"):
        """
        @summary: 终止播放
        :param endType:
        :param logOption:
        :param timestamp:
        :return:
        """
        cmd = timestamp + ",EN"
        if endType is not None:
            cmd = cmd + "," + str(endType)
        if logOption is not None:
            cmd = cmd + "," + str(logOption)
        self.__GSS7000SendCommand(cmd)
        return self.aw_GSS7000CheckExpectedStatus(SIMU_STATUS_DICT["Ended"], SIMU_STATUS_DICT["Ready"])

    def aw_GSS7000RewindScenario(self):
        """

        :return:
        """
        self.__GSS7000SendCommand("RW")
        return self.aw_GSS7000CheckExpectedStatus(SIMU_STATUS_DICT["Ready"])

    def aw_GSS7000SendMessage(self, remoteName, msg, level='Debug'):
        """
        @summary: 发信息到simGen的消息文件
        :param remoteName:
        :param msg:
        :param level:
        :return:
        """
        cmd = "MESSAGE," + str(remoteName) + "," + str(level) + "," + str(msg)
        return SUC, self.__GSS7000SendCommand(cmd)
    
    def aw_GSS7000SetScenarioInitPosition(self, vehMot, lat, lon, height, timestamp):
        """
        @summary: 设置静态场景初始化位置
        @param vehMot: 
        @param lat: 
        @param lon: 
        @param height: 
        """
        cmd = ','.join([timestamp, 'INIT_POS', str(vehMot), str(lat), str(lon), str(height)])
        isSuc(self.aw_GSS7000EnsureReady())
        return SUC, self.__GSS7000SendCommand(cmd)
    
    def aw_GSS7000SetScenarioStart(self, timeStr, duration, satLoc):
        """
        @summary: 设置场景开始和持续时间
        @param timeStr: 
        @param duration: 
        @param satLoc: 
        """
        isSuc(self.aw_GSS7000EnsureReady())
        cmd = 'START_TIME,' + timeStr
        if duration is not None:
            cmd = cmd + ',' + str(duration)
        if satLoc is not None:
            cmd = cmd + ',' + str(satLoc)
        return SUC, self.__GSS7000SendCommand(cmd)
    
    def aw_GSS7000TurnPowOn(self, state, signalType, vehAnt='v1_a1', id='0', multiIndex='0', mode='1', allFlag='1', timestamp='-', allTxType='1'):
        """
        @summary: 打开或关闭RF信号
        @param vehAnt: 
        @param state: 0关闭，1打开
        @param signalType: 
        @param id: 
        @param multiIndex: 
        @param mode: 
        @param allFlag: 
        @param timestamp: 
        @param allTxType: 0表示某一特定信道，1表示所有信道
        """
        cmd = ','.join([timestamp, 'POW_ON', vehAnt, state, signalType, id, multiIndex, mode, allFlag, allTxType])
        return SUC, self.__GSS7000SendCommand(cmd)
    
    @AutoPrint(True)
    def aw_GSS7000SetPowerEnable(self, isEnable, signalList=['GPS', 'BEIDOU', 'GLONASS', 'IRNSS', 'GALILEO']):
        for signalType in signalList:
            satte = '1' if isEnable else '0'
            self.aw_GSS7000TurnPowOn(satte, signalType)
        return SUC, 'OK'
    
    def aw_GSS7000SetPowMode(self, vehAnt, state, signalType, id, multiIndex, mode, allFlag, timestamp='-', allTxType=None):
        """
        @summary: 修改功率模式
        @param vehAnt: 
        @param state: 
        @param signalType: 
        @param id: 
        @param multiIndex: 
        @param mode: 
        @param allFlag: 
        @param timestamp: 
        @param allTxType: 
        """
        cmd = ','.join([timestamp, 'POW_MODE', vehAnt, state, signalType, id, multiIndex, mode, allFlag])
        if allTxType is not None:
            cmd = cmd + ',' + allTxType
        return SUC, self.__GSS7000SendCommand(cmd)
    
    def aw_GSS7000SetRelativePowLevCh(self, vehAnt, level, signalType, id="0", multiIndex="0", mode="0", align="0", timestamp='-', allFlag=1):
        """
        @summary: 修改指定信道相对功率大小，当id为0时为修改所有信道
        @param vehAnt: 
        @param level: 
        @param signalType: 
        @param id: 
        @param multiIndex: 
        @param mode: 
        @param align: 
        @param timestamp: 
        @param allFlag: 
        """
        cmd = ','.join([timestamp, 'POW_LEV', vehAnt, level, signalType, id, multiIndex, mode, allFlag, "0", align, "1"])
        return SUC, self.__GSS7000SendCommand(cmd)
    
    @AutoPrint(True)
    def aw_GSS7000SetAbsolutePowLevCh(self, level, signalType, vehAnt='v1_a1', id="0", multiIndex="0", mode="0", allFlag="1", allTxType="1", timestamp='-'):
        """
        @summary: 修改指定信道绝对功率大小，当id为0时为修改所有信道
        @param vehAnt: 载体和天线信息，单输出口为v1_a1，多输出口的模拟器会区分不同值
        @param level: 信号强度
        @param signalType: 信号源
        @param id: channel or svid,由mode确定
        @param multiIndex: incident signal/number of multipath starting at 1 - only applies in SVID mode
        @param mode: 0表示svid模式，1表示channel模式
        @param allFlag: 0 apply to specified channel/SVID,1 apply to all channel/SVID
        @param allTxType: 0表示修改某一channel或svid，1表示修改所有channel或svid
        @param timestamp: 
        """
        cmd = ','.join([timestamp, 'POW_LEV', vehAnt, str(level), signalType, id, multiIndex, mode, allFlag, "1", "1", allTxType])
        return SUC, self.__GSS7000SendCommand(cmd)
    
    @AutoPrint(True)
    def aw_Gss7000SetSignalLevel(self, level, loss=1, signalList=['GPS', 'BEIDOU', 'GLONASS', 'IRNSS','GALILEO']):
        '''
        @summary: 设置信号大小
        @param level: 需要设置到的信号大小
        @param signalList: 信号源
        '''
        signalDict = {'GPS':0, 'BEIDOU':3, 'GLONASS':1, 'IRNSS':0, 'GALILEO':-2}
        for signalType in signalList:
            signalLevel = 130 + level + loss + signalDict[signalType]
            self.aw_GSS7000SetAbsolutePowLevCh(signalLevel, signalType)
        time.sleep(2)
        return SUC, 'ok'
    
    def aw_GSS7000SetRefLev(self, level):
        """
        @summary: 设置参考信号大小
        @param level: 
        """
        return SUC, self.__GSS7000SendCommand("REF_DBM," + str(int(level)))
    
    def aw_GSS7000SetSatOffset(self, signalType, svid, offset, timestamp='-'):
        """
        @summary: 设置指定卫星的信号大小
        @param signalType: 
        @param svid: 
        @param offset: 
        @param timestamp: 
        """
        if float(offset) > 4 or float(offset) < -60:
            return FAIL, 'offset is out of limitation.'
        cmd = ','.join([timestamp, "SAT_POW_OFFSET", signalType, svid, offset])
        return SUC, self.__GSS7000SendCommand(cmd)
    
    def aw_GSS7000LoadAlmanac(self, fileName, weekNum, network):
        """
        @summary: 加载星历文件
        @param fileName: 
        @param weekNum: 
        @param network: 
        """
        cmd = ','.join(["LOAD_ALMANAC", fileName, weekNum, network])
        msg = self.__GSS7000SendCommand(cmd)
        if "Cannot find the specified file" in msg:
            return FAIL, msg
        return SUC, msg
    
    def aw_GSS7000SwitchLMM(self, vehicleId, category, timestamp='-'):
        """
        @summary: 
        @param vehicleId: 
        @param environment: 
        @param category: 
        @param timestamp: 
        """
        cmd = ','.join([timestamp, 'SWITCH_LMM', vehicleId, category])
        return SUC, self.__GSS7000SendCommand(cmd)
    
    def aw_GSS7000GetGpsTime(self, timestamp='-'):
        """
        @summary: 获取gps秒数，从1980年1月6日算起
        @param timestamp: 
        """
        msg = self.__GSS7000SendCommand(timestamp + ",GPS_TIME")
        data = msg.split("data")[1]
        sec = data.split(">")[1].split("<")[0]
        return SUC, int(sec)
    
    @AutoPrint(True)
    def aw_GSS7000GetRunTime(self, timestamp='-'):
        """
        @summary: 获取场景运行的时间
        @param timestamp: 
        """
        msg = self.__GSS7000SendCommand(timestamp + ",TIME")
        data = msg.split("data")[1]
        runTime = data.split(">")[1].split("<")[0].strip()
        if 'scenario is loading or has ended' in str(runTime):
            runTime=isSuc(self.aw_GSS7000GetScenarioDuration())
        return SUC, float(runTime)

    @AutoPrint(True)
    def aw_GSS7000Wait2Time(self, duration):
        '''
        @summary: 等待场景播放多长时间
        '''

        runTime = isSuc(self.aw_GSS7000GetRunTime())
        while runTime < duration:
            time.sleep(1)
            runTime = isSuc(self.aw_GSS7000GetRunTime())
        startTime = isSuc(self.aw_GSS7000GetStartTime())
        startTime=time.mktime(time.strptime(startTime,"%Y-%m-%d %H:%M:%S"))
        curTime = startTime + runTime
        curDateTime = time.strftime("%Y%m%d%H%M%S", time.localtime(curTime))
        return SUC, curDateTime
    
    @AutoPrint(True)
    def aw_GSS7000GetCurrentTime(self):
        runTime = isSuc(self.aw_GSS7000GetRunTime())
        startTime = isSuc(self.aw_GSS7000GetStartTime())
        startTime=time.mktime(time.strptime(startTime,"%Y-%m-%d %H:%M:%S"))
        curTime = startTime + runTime
        curDateTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(curTime))
        return SUC, curDateTime

    @AutoPrint(True)
    def aw_GSS7000GetStartTime(self):
        '''
        @summary: 获取场景开始播放时间
        '''
        msg = self.__GSS7000SendCommand("STTIME")
        data = msg.split("data")[1]
        startTime = data.split(">")[1].split("<")[0].strip()
        startTime=time.mktime(time.strptime(startTime,'%d-%b-%Y %H:%M:%S'))
        startTime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(startTime))
        return SUC, startTime
    
    def aw_GSS7000LoadAct(self, actFile):
        """
        @summary: 加载用户行为，只能场景打开为ready to run的情况下加载
        @param actFile: 
        """
        if self.__GSS7000GetStatus() == SIMU_STATUS_DICT["Running"]:
            return FAIL, 'The scenario is running, load act is forbidden'
        msg = self.__GSS7000SendCommand("LOAD_ACT," + actFile)
        if "Cannot find the specified file" in msg:
            return FAIL, msg
        return SUC, msg
    
    def aw_GSS7000LoadUcd(self, ucdFile):
        """
        @summary: 加载用户命令
        @param actFile: 
        """
        if self.__GSS7000GetStatus() == SIMU_STATUS_DICT["Running"]:
            return FAIL, 'The scenario is running, load ucd is forbidden'
        msg = self.__GSS7000SendCommand("LOAD_UCD," + ucdFile)
        if "Cannot find the specified file" in msg:
            return FAIL, msg
        return SUC, msg
    
    def aw_GSS7000LoadUmt(self, umtFile):
        """
        @summary: 加载用户命令
        @param umtFile: 
        """
        if self.__GSS7000GetStatus() == SIMU_STATUS_DICT["Running"]:
            return FAIL, 'The scenario is running, load ucd is forbidden'
        msg = self.__GSS7000SendCommand("LOAD_UMT," + umtFile)
        if "Cannot find the specified file" in msg:
            return FAIL, msg
        return SUC, msg
    
    def aw_GSS7000EnableTurbo(self, enable, speed):
        """
        @summary: 进入加速模式
        @param enable: 
        @param speed: 
        """
        msg = self.__GSS7000SendCommand("GET_DUMMY_RUN_MODE")
        data = msg.split("data")[1]
        info = data.split(">")[1].split("<")[0]
        if info.find("ON") == -1:
            return FAIL, "simGEN is not in dummy run mode,cannot proccess turbo command"
        return SUC, self.__GSS7000SendCommand("TURBO," + enable + "," + speed)
    
    def aw_GSS7000PrRamp(self, txNet, svid, allFlag, startTime, useStart, state, offset, uptime, holdTime, downTime, timestamp='-'):
        """
        @summary: 修改伪距
        @param txNet: 
        @param svid: 
        @param allFlag: 
        @param startTime: 
        @param useStart: 
        @param state: 
        @param offset: 
        @param uptime: 
        @param holdTime: 
        @param downTime: 
        @param timestamp: 
        """
        cmd = ",".join([timestamp, "PR_RAMP", txNet, svid, state, allFlag, startTime, useStart, state, offset, uptime, holdTime, downTime])
        return SUC, self.__GSS7000SendCommand(cmd)

    def aw_GSS7000PrErrors(self, network, svid, allFlag, errorType, start, timestamp='-'):
        """
        @summary: 设置一个伪距错误
        """
        cmd = ",".join([timestamp, "PR_ERRORS", network, svid, allFlag, errorType, start])
        return SUC, self.__GSS7000SendCommand(cmd)
    
    def aw_GSS7000GenerateAM(self, vehAnt, interfererId, refLevel, level, RF_on, centreFreq, wave, rate, depth, timestamp='-'):
        """
        @summary: 产生AM信号
        """
        cmd = ",".join([timestamp, "AM", vehAnt, interfererId, refLevel, level, RF_on, centreFreq, wave, rate, depth])
        return SUC, self.__GSS7000SendCommand(cmd)

    @AutoPrint(True)
    def aw_GSS7000GetStandardNMEA(self, sceneId, rmSrcFlag=True):
        '''
        @summary: 获取6700/7000模拟器生成的标准nmea文件
        @param sceneId: 场景编号
        @param rmSrcFlag: 获取后是否删除标准nmea文件
        @return: (SUC, success info) or (FAIL, fail info)
        @see: self.lbs.aw_checkCepTtffStandard({'COM1':19},20)
        @author: shaochanghong
        @attention: 
        '''
        posAppLogPath = getInstruments().get('Gss7000', {}).get('posAppLogPath')
        gssType = getInstruments().get('Gss7000', {}).get('type')
        if not os.path.exists(posAppLogPath):
            return FAIL, 'please check posAppLogPath.'
        if '7000' in gssType:
            ip = posAppLogPath.split(os.sep)[2]
            isSuc(self.sendMsg2Gss7000Server({'sceneId':sceneId}, ip, 9998))
        srcPath = os.path.join(posAppLogPath, sceneId, 'nmea.txt')
        dstPath = os.path.join(getLbsCaseLogPath(), 'novatel.txt')
        if not os.path.exists(srcPath):
            return FAIL, 'has no nmea.txt'
        shutil.copyfile(srcPath, dstPath)
        if rmSrcFlag:
            os.remove(os.path.join(posAppLogPath, sceneId, 'nmea.txt'))
        return SUC, dstPath

    @AutoPrint(True)
    def sendMsg2Gss7000Server(self, cmd, ip, port):
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        try:
            s.connect((ip, port))
            s.send(str(cmd).encode("utf-8"))
            endTime = time.time() + 120
            while time.time() < endTime:
                try:
                    msg = s.recv(1024)
                    recvMsg = eval(msg.decode())
                    if recvMsg.get('state') == 'okay':
                        return SUC, 'okay'
                    else:
                        return FAIL, 'please check server right.'
                except:
                    time.sleep(2)
        except:
            PRINTTRAC('please check server right.')
            s.close()
            return FAIL, 'please check server right.'

    
if __name__ == '__main__':

    # print(GSS7000(ip='10.100.5.230').aw_GSS7000CheckExpectedStatus(SIMU_STATUS_DICT['Ready']))
    GSS7000(ip='10.110.8.251').aw_GSS7000GetScenarioDuration()
