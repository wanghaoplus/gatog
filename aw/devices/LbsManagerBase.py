#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/24 21:31
# @Author  : shaochanghong
# @Site    : 
# @File    : LbsManagerBase.py
# @Software: PyCharm
import os
import re
import time
import math
import shutil
from aw.core.Input import SUC
from aw.core.Input import FAIL
from aw.core.Input import isSuc
from aw.core.Input import PRINTI
from aw.core.Input import PRINTE
from aw.core.Input import AutoPrint
from aw.core.Input import getDevices
from aw.core.Input import newThreadFunc
from aw.core.Input import getInstruments
from aw.core.Input import getLbsCaseLogPath
from aw.devices.LbsContants import DEVICE_CMD
from aw.devices.LbsContants import CMD
from aw.core.SocketBase import SocketClient
from aw.core.SerialBase import SerialBase
LbsManagerBaseObj = None


class LbsManagerBase(object):
    deviceList = []  # 存储所有设备对象
    ttffStartTimeDict = {}  # 存储所有设备开始定位时间
    ttffEndTimeDict = {}  # 存储所有设备定位成功时间
    firstLocationDict = {}  # 存储所有设备首次定位位置

    def __init__(self):
        pass

    @staticmethod
    def getLbsManagerBaseObj():
        global LbsManagerBaseObj
        if LbsManagerBaseObj is None:
            LbsManagerBaseObj = LbsManagerBase()
        return LbsManagerBaseObj

    def initDevice(self):
        self.deviceList=[]
        deviceList = getDevices()
        for device in deviceList["TestDevices"]:
            if device["connectType"].lower() == "socket":
                ip = device["ip"]
                port = device['port']
                sock = SocketClient(host=ip, port=port)
                sock.setDeviceMsg(device)
                sn = str(ip) + '_' + str(port)
                deviceType = device.get('deviceType')
                self.deviceList.append({'sn':sn, 'deviceType':deviceType, 'obj':sock})
                sock.connect()
            elif device["connectType"].lower() == 'usb':
                serl = SerialBase(device['port'])
                serl.setDeviceMsg(device)
                sn = device['port']
                deviceType = device.get('deviceType')
                self.deviceList.append({'sn':sn, 'deviceType':deviceType, 'obj':serl})
                serl.connect()
        self.startReadPort()
        # 连接
        pass
    
    @AutoPrint(True)
    def startReadPort(self):
        """
        @summary: 开始读取串口信息
        @return: 成功，失败信息
        """
        for device in self.deviceList:
            sn = device.get('sn')
            deviceObj = device.get('obj')
            newThreadFunc(func=deviceObj.startReciver, name=sn , args=(), daemon=True)  #
        return SUC, 'start_success'
    
    @AutoPrint(True)
    def stopReadPort(self):
        """
        @summary: 开始读取串口信息
        @return: 成功，失败信息
        """
        for device in self.deviceList:
            deviceObj = device.get('obj')
            deviceObj.stopReciver()
        return SUC, 'stop_success'

    def sendCommand(self, cmd,deviceSn='all'):
        for device in self.deviceList:
            deviceObj = device.get('obj')
            if deviceSn=='all':
                deviceObj.send(cmd)
            elif deviceSn in device:
                deviceObj.send(cmd)
            
    def __startLocation(self, sn, deviceObj, deviceType, mode='cold', timeout=30):
        '''
        @summary: 单个设备发起冷/热/温启动定位
        @param sn: 设备编号
        @param deviceObj: 设备对象
        @param mode: 启动方式
        @param timeout: 超时时间
        @return: (SUC, success info) or (FAIL, fail info)
        @see: self.__startLocation('cold', 120)
        @author: shaochanghong
        @attention: 
        '''
        deviceObj.setParseNmeaEnable(True)
        startFlag = False
        endTime = time.time() + timeout
        while time.time() < endTime:
            if deviceObj.queue.empty():
                time.sleep(1)
                continue
            msgType, msg = deviceObj.queue.get_nowait()
            if msgType == 'GGA':
                utc = msg.split(',')[0]
                if utc:
                    if sn not in self.ttffStartTimeDict:
                        self.ttffStartTimeDict[sn] = {'utc':utc}
                    else:
                        self.ttffStartTimeDict[sn]['utc'] = utc
                    if startFlag:continue
                    if mode.lower() == 'cold':
                        deviceObj.send(DEVICE_CMD[deviceType].CMD_COLD_START)
                    elif mode.lower() == 'warm':
                        deviceObj.send(DEVICE_CMD[deviceType].CMD_WARM_START)
                    elif mode.lower() == 'hot':
                        deviceObj.send(DEVICE_CMD[deviceType].CMD_HOT_START)
                    startFlag = True
            else:
                if sn in self.ttffStartTimeDict:
                    self.ttffStartTimeDict[sn]['cmdState'] = SUC
                break
    
    @AutoPrint(True)          
    def startLocation(self, mode='cold', timeout=60):
        '''
        @summary: 发起冷/热/温启动定位
        @param mode: 启动方式
        @param timeout: 超时时间
        @return: (SUC, success info) or (FAIL, fail info)
        @see: self.hdbd.startLocation('cold', 120)
        @author: shaochanghong
        @attention: 
        '''
        if mode.lower() not in ['cold', 'warm', 'hot']:
            return FAIL, 'has no this mode:%s' % mode
        self.resetTestData()
        for device in self.deviceList:
            sn = device.get('sn')
            deviceObj = device.get('obj')
            deviceType = device.get('deviceType')
            newThreadFunc(self.__startLocation, args=(sn, deviceObj, deviceType, mode, timeout), daemon=True)
        
        sucDevices = []
        endTime = time.time() + timeout
        while time.time() < endTime:
            sucDevices.clear()
            for device in self.deviceList:
                sn = device.get('sn')
                if sn in self.ttffStartTimeDict:
                    if self.ttffStartTimeDict[sn].get('cmdState') == SUC:
                        sucDevices.append(sn)
            if len(sucDevices) == len(self.deviceList):
                return SUC, '所有设备发起定位成功'
            time.sleep(1)
        
        failDevices = []
        for device in self.deviceList:
            sn = device.get('sn')
            if sn not in sucDevices:
                failDevices.append(sn)
                PRINTE('%s:发起定位失败')
        return FAIL, '发起定位失败的设备：%s' % str(failDevices)
    
    @AutoPrint(True)
    def checkLocationSuccess(self, timeout=60,isTracking=False):
        '''
        @summary: 检查设备是否定位成功
        @param timeout: 超时时间
        @return: (SUC, success info) or (FAIL, fail info)
        @see: self.hdbd.checkLocationSuccess(120)
        @author: shaochanghong
        @attention: 对tracking场景不适用
        '''
        sucDeviceDict = {}

        def check(sn, deviceObj):
            endTime = time.time() + timeout
            while time.time() < endTime:
                if not deviceObj.queue.empty():
                    nmeaType, nmeaMsg = deviceObj.queue.get_nowait()
                    if nmeaType == 'GGA':
                        ggaMsgs = nmeaMsg.split(',')
                        if ggaMsgs[5] != '0' and ggaMsgs[5] != '':
                            sucDeviceDict[sn] = "GGA:" + nmeaMsg
                            self.ttffEndTimeDict[sn] = ggaMsgs[0]
                            self.firstLocationDict[sn] = {'lat':ggaMsgs[1], 'lon':ggaMsgs[3],
                                                          'alt':float(ggaMsgs[8]) + float(ggaMsgs[10])}
                            break
                else:
                    time.sleep(0.9)

        for device in self.deviceList:
            sn = device.get('sn')
            deviceObj = device.get('obj')
            deviceObj.setParseNmeaEnable(True)
            newThreadFunc(check, args=(sn, deviceObj), daemon=True)
        PRINTI("正在查询定位结果，请耐心等待...")
        
        endTime = time.time() + timeout
        while time.time() < endTime:
            if len(sucDeviceDict) == len(self.deviceList):
                break
            time.sleep(1)
        
        PRINTI("将首次定位信息写入表格")
        self.writeFirstFixLocationTTFF()
        if isTracking:
            for device in self.deviceList:
                sn = device.get('sn')
                deviceObj = device.get('obj')
                deviceObj.setParseNmeaEnable(False)
        
        if len(sucDeviceDict) == len(self.deviceList):
            return SUC,'所有设备定位成功'
            
        failDevices = []
        for device in self.deviceList:
            sn = device.get('sn')
            if sn in sucDeviceDict:
                PRINTI(sn + '[%s]' % sucDeviceDict.get(sn))
            else:
                failDevices.append(sn)
                PRINTE(sn + '[定位失败]')
        return FAIL, failDevices
    
    def writeFirstFixLocationTTFF(self):
        from aw.utils.kpireport.SingleReport import SingleCaseReport
        SingleCaseReport.getInstance().curTimes += 1
        for sn, valueDict in self.ttffStartTimeDict.items():
            lat = self.firstLocationDict.get(sn, {}).get('lat', '')
            lon = self.firstLocationDict.get(sn, {}).get('lon', '')
            alt = self.firstLocationDict.get(sn, {}).get('alt', '')
            fixTime = self.ttffEndTimeDict.get(sn, '')
            fixFlag = 1 if fixTime else 0
            dataList = [sn, valueDict['utc'], fixTime, lat, lon, alt, fixFlag]
            SingleCaseReport.getInstance().aw_writeRow("FirstFixCepTTFF", dataList)
        SingleCaseReport.getInstance().aw_save()
        
    @AutoPrint(True)
    def checkMaxSpeed(self, maxSpeed):
        from aw.utils.kpireport.MaxSpeedAltReport import MaxSpeedAltReport
        standardTime, startTime = isSuc(MaxSpeedAltReport.getInstance().getnovatelMatchTime('speed', maxSpeed))
        for device in self.deviceList:
            MaxSpeedAltReport.getInstance().getTestNmeaData(device, startTime)
        return MaxSpeedAltReport.getInstance().checkMaxSpeed(maxSpeed, standardTime)
    
    @AutoPrint(True)
    def checkMaxAltitude(self, maxHeight):
        from aw.utils.kpireport.MaxSpeedAltReport import MaxSpeedAltReport
        standardTime, startTime = isSuc(MaxSpeedAltReport.getInstance().getnovatelMatchTime('alt', maxHeight))
        for device in self.deviceList:
            MaxSpeedAltReport.getInstance().getTestNmeaData(device, startTime)
        return MaxSpeedAltReport.getInstance().checkMaxHeight(maxHeight, standardTime)
    
    @AutoPrint(True)
    def calculateTTFF(self):
        '''
        @summary: 计算ttff
        @return: (SUC, success info) or (FAIL, fail info)
        @see: self.hdbd.calculateTTFF()
        @author: shaochanghong
        @attention: 对tracking场景不适用
        '''
        ttffDict = {}
        for sn, valueDict in self.ttffStartTimeDict.items():
            startUtc = valueDict['utc']
            startTime = int(startUtc[:2]) * 3600 + int(startUtc[2:4]) * 60 + int(startUtc[4:6]) + float(startUtc.split('.')[-1]) / 1000
            if sn in self.ttffEndTimeDict:
                endUtc = self.ttffEndTimeDict[sn]
                endTime = int(endUtc[:2]) * 3600 + int(endUtc[2:4]) * 60 + int(endUtc[4:6]) + float(endUtc.split('.')[-1]) / 1000
                ttffDict[sn] = endTime - startTime
        return SUC, ttffDict
    
    @AutoPrint(True)
    def calculateFisrtLocationCep(self, latRef, lonRef, altRef=None, cepType='2D'):
        '''
        @summary: 计算首次定位的cep
        @param latRef: 参考位置纬度
        @param lonRef: 参考位置经度
        @param altRef: 参考位置高度
        @return: (SUC, {'COM1':8.9})
        @see: self.manager.calculateFisrtLocationCep(31.56, 112.39, 89.6, '3D')
        @author: shaochanghong
        @attention: 对tracking场景不适用
        '''
        cepDict = {}
        for sn, location in self.firstLocationDict.items():
            lat = self.__convertdmmmmmm2d(location['lat'])
            lon = self.__convertdmmmmmm2d(location['lon'])
            alt = float(location['alt'])
            if cepType == '2D':
                cep = self.calculateDistance(lonRef, latRef, lon, lat)
            elif cepType == '3D':
                cep = self.calculateDistance3D(lonRef, latRef, altRef, lon, lat, alt)
            else:
                cep = self.calculateDistanceAlt(altRef, alt)
            cepDict[sn] = cep
        return SUC, cepDict
    
    @AutoPrint(True)
    def checkCepTtffStandard(self, testValue:dict, standard=20):
        '''
        @summary: 检查cep或ttff是否达标
        @param tsetValue: 测试数据
        @param standard: 标准值
        @return: (SUC, success info) or (FAIL, fail info)
        @see: self.manager.checkCepTtffStandard({'COM1':19},20)
        @author: shaochanghong
        @attention: 对tracking场景不适用
        '''
        failDeviceDict = {}
        for device in self.deviceList:
            sn = device.get('sn')
            if sn in testValue:
                if testValue[sn] > standard:
                    failDeviceDict[sn] = testValue[sn]
            else:
                failDeviceDict[sn] = -1
        if failDeviceDict:
            return FAIL, failDeviceDict
        return SUC, '所有设备都符合标准'
    
    @AutoPrint(True)
    def calculateCurrentCep(self, latRef, lonRef, altRef, cepType='2D'):
        '''
        @summary: 计算当前位置与参考位置cep
        @param latRef: 参考纬度
        @param lonRef: 参考经度
        @param altRef: 参考高度
        @param cepType: cep误差类型，2D/3D
        @return: (SUC, success info) or (FAIL, fail info)
        @see: self.manager.calculateCurrentCep(31.56, 112.87, 20)
        @author: shaochanghong
        @attention: 对tracking场景不适用
        '''
        cepDict = {}
        for device in self.deviceList:
            sn = device.get('sn')
            deviceObj = device.get('obj')
            if not deviceObj.queue.empty():
                nmeaType, nmeaMsg = deviceObj.queue.get_nowait()
                if nmeaType == 'GGA':
                    ggaMsgs = nmeaMsg.split(',')
                    if ggaMsgs[5] == '1':
                        lat = self.__convertdmmmmmm2d(ggaMsgs[1])
                        lon = self.__convertdmmmmmm2d(ggaMsgs[3])
                        alt = float(ggaMsgs[8])+ float(ggaMsgs[10])
                        if cepType == '2D':
                            cep = self.calculateDistance(lonRef, latRef, lon, lat)
                        elif cepType == '3D':
                            cep = self.calculateDistance3D(lonRef, latRef, altRef, lon, lat, alt)
                        else:
                            cep = self.calculateDistanceAlt(altRef, alt)
                        cepDict[sn] = cep
        return SUC, cepDict
    
    @AutoPrint(True)
    def resetTestData(self):
        '''
        @summary: 重置测试数据
        @return: (SUC, success info) or (FAIL, fail info)
        @see: self.manager.resetTestData()
        @author: shaochanghong
        @attention: 对tracking场景不适用
        '''
        self.ttffStartTimeDict.clear()
        self.ttffEndTimeDict.clear()
        self.firstLocationDict.clear()
        for device in self.deviceList:
            deviceObj = device.get('obj')
            deviceObj.setParseNmeaEnable(False)
            deviceObj.queue.queue.clear()
        return SUC, 'OK'
    
    def calculateDistanceAlt(self, altStart, altEnd):
        '''
        @summary: 计算高程误差
        @param altStart:高程标准值
        @param altEnd: 测试得到高程数据 
        @return: 高程误差值
        @see: self.manager.calculateDistanceAlt()
        @author: wangdelei
        @attention: 对tracking场景不适用
        '''
        return round(altEnd - altStart, 3)
    
    def calculateDistance3D(self, lonStart, latStart, altStart, lonEnd, latEnd, altEnd):
        '''
        @summary: 计算3D误差
        @param lonStart: 参考纬度
        @param latStart: 参考经度
        @param altStart: 参考高度
        @param lonEnd: 参考纬度
        @param latEnd: 参考经度
        @param altEnd: 参考高度
        @return: 高程误差
        @see: self.manager.calculateDistance3D()
        @author: wangdelei
        @attention: 对tracking场景不适用
        '''
        HorErr = self.calculateDistance(lonStart, latStart, lonEnd, latEnd)
        Distance3D = math.sqrt(HorErr * HorErr + (altStart-altEnd) * (altStart-altEnd))
        return round(Distance3D, 3)
    
    def calculateDistance(self, lon_start, lat_start, lon_end, lat_end):
        GEO_RADIUS_O_FEARTH = 6370856
        COE_DEG2RAD = 0.0174532925
        lon_start = float(lon_start)
        lat_start = float(lat_start)
        lon_end = float(lon_end)
        lat_end = float(lat_end)

        lon_start = lon_start * COE_DEG2RAD
        lat_start = lat_start * COE_DEG2RAD
        lon_end = lon_end * COE_DEG2RAD
        lat_end = lat_end * COE_DEG2RAD

        rel_xy_1 = (lon_end - lon_start) * GEO_RADIUS_O_FEARTH * math.cos(lat_start)
        rel_xy_2 = (lat_end - lat_start) * GEO_RADIUS_O_FEARTH

        distance = math.sqrt(rel_xy_1 * rel_xy_1 + rel_xy_2 * rel_xy_2)
        return round(distance, 3)
    
    def __convertdmmmmmm2d(self, titude):
        '''
        @titude 原始的符合dmm.mmmm规则的经纬度，小数点前至少3位数字，小数点后必须1位数字
        @return 小数的经纬度字符串
        '''
        titude = str(titude)
        if not re.match("^\d{3,}\.\d{1,}$", titude):
            return ''
        dmm, mmmm = titude.split('.')
        d = dmm[:-2]
        mm = dmm[-2:]
        titude_f = float(d) + float('%s.%s' % (mm, mmmm)) / 60
        return titude_f
    
    def get7000StandardNMEA(self, sceneId, rmSrcFlag=True):
        posAppLogPath = getInstruments().get('Gss7000', {}).get('posAppLogPath')
        gssType = getInstruments().get('Gss7000', {}).get('gssType')
        if not os.path.exists(posAppLogPath):
            return FAIL, 'please check posAppLogPath.'
        if gssType == '7000':
            isSuc(self.sendMsg2Gss7000Server({'sceneId':sceneId}))
        srcPath = os.path.join(posAppLogPath, sceneId, 'nmea.txt')
        dstPath = os.path.join(getLbsCaseLogPath(), 'novatel.txt')
        if not os.path.exists(srcPath):
            return FAIL, 'has no nmea.txt'
        shutil.copyfile(srcPath, dstPath)
        if rmSrcFlag:
            shutil.rmtree(os.path.join(posAppLogPath, sceneId, 'nmea.txt'))
        return SUC, dstPath
    
    def sendMsg2Gss7000Server(self, cmd):
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        try:
            s.connect((self.__host, self.__port))
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
            s.close()
            return FAIL, 'please check server right.'
                
    def setPowerEnable(self, isEnable=True):

        if isEnable:
            pass
        else:
            pass

    def reset(self):
        pass

    def setFactory(self):
        
        pass
    def powerMainOff(self, device='all'):
        '''
        @summary: 断设备主电
        @param device:测试设备名称 '''
        cmd = DEVICE_CMD['hdbd'].POWER_OFF_ALL
        self.sendCommand(cmd, device)
        return SUC, 'OK'
    
    def powerAllOff(self, device):
        '''
        @summary: 全部断电
        @param device:测试设备名称 '''
        cmd = DEVICE_CMD['hdbd'].POWER_OFF_ALL
        self.sendCommand(cmd)
        return SUC, 'OK'

    def setSleepMode(self, sleepType , slpDelayTime):
        '''
        @summary: 
        @param sleepType: 休眠类型  Sleep Deep MianPowerDown RTCStandOnly
        @param slpDelayTime:休眠时间'''
        slpDelayTime = slpDelayTime * 1000
        cmd = DEVICE_CMD['hdbd'].sleepCommand(sleepType , slpDelayTime)
        self.sendCommand(cmd)
        return SUC, 'OK'

    def setDebugInfo(self, mode):
        '''
        @summary: 设置debug信息开关，
        @param mode:close, open '''
        cmd = CMD.setDebugInfo(mode)
        self.sendCommand(cmd)
        cmd = DEVICE_CMD['hdbd'].SAVE_DEBUG_CONFIG
        self.sendCommand(cmd)
        return SUC, 'OK'
    
    def downloadEphemeris(self, remoteFile):
        localPath=r'D:\LbsEphemeris'
        ephemeris = remoteFile.split('/')[-1]
        localFile = os.path.join(localPath, ephemeris)
        if not os.path.exists(localPath):
            os.makedirs(localPath)
        if os.path.exists(localFile):
            return SUC, localFile
        from aw.core.FTPBase import FTPBase
        return FTPBase('agnss.hdbds.com', 'wangchao', 'Demo_123!', 21).downloadFile(remoteFile, localFile)
    
    def injectEphemeris(self, remoteFile):
        ephFile = isSuc(self.downloadEphemeris(remoteFile))
        with open(ephFile,'rb') as rf:
            ephList=rf.read().split(b'\xf1\xd9')
        ephList=[b'\xf1\xd9'+msg for msg in ephList if msg]
        for device in self.deviceList:
            deviceType=device.get('deviceType')
            deviceObj=device.get('obj')
            if deviceType.lower()=='hdbd':
                for msg in ephList:
                    deviceObj.send(msg)
                    time.sleep(0.1)
                
    