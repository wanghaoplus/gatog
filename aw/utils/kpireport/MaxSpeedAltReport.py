#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/02/28 12:57
# @Author  : shaochanghong
import os
import re
import pandas as pd
from collections import OrderedDict
from aw.core.Input import SUC
from aw.core.Input import FAIL
from aw.core.Input import isSuc
from aw.core.Input import AutoPrint
from aw.core.Input import getLbsCaseLogPath
from aw.core.Input import getCurCaseName
from aw.utils.kpireport.ReportBase import ReportExcelBase
MaxSpeedAltReportObj = None


class MaxSpeedAltReport(ReportExcelBase):
    
    @staticmethod
    def getInstance():
        global MaxSpeedAltReportObj
        if MaxSpeedAltReportObj is None:
            MaxSpeedAltReportObj = MaxSpeedAltReport()
        return MaxSpeedAltReportObj
    
    def __init__(self):
        super(MaxSpeedAltReport, self).__init__()
        self.curCaseName = getCurCaseName()
        self.aw_writeHeader()
    
    @property
    def caseReportPath(self):
        return os.path.join(getLbsCaseLogPath(), getCurCaseName() + '.xls')
    
    def aw_writeRow(self, sheetName, dataList):
        '''
        @summary: 将测试数据写入指定sheet页
        @param sheetName: sheet页名称,FirstFixCepTTFF
        @param dataList: 待写入的数据
        @return: (SUC, 'OK')
        @author: shaochanghong
        @attention: 
        '''
        if sheetName not in ['MaxSpeedAlt']:
            return FAIL, 'has no this sheet %s' % sheetName
        if self.curCaseName != getCurCaseName():
            self.resetWorkBook()
            self.aw_writeHeader()
            self.curCaseName = getCurCaseName()
        self.writeRow(sheetName, dataList)
        
    def aw_writeHeader(self):
        self.writeHeader('Novatel', ['Utc', 'Alt', 'Speed'])
        self.writeHeader('MaxSpeedAlt', ['DeviceSN', 'Utc', 'Lat', 'Lon', 'Alt', 'Speed', 'FixFlag'])
        return SUC, 'OK'
    
    def aw_save(self):
        self.save(self.caseReportPath)
    
    def getnovatelMatchTime(self, mType, expect):
        '''
        @summary: 匹配符合期望高度或速度的时间
        @param mType: speed或alt
        @param expect: 速度或高度极限值
        @attention: 适用于高速和探空场景
        '''
        novatel = os.path.join(getLbsCaseLogPath(), 'novatel.txt')
        if not os.path.exists(novatel):
            return FAIL, 'novatel.txt不存在'
        novatelDict = {'speed':0, 'alt':0}
        with open(novatel, 'r') as fileObj:
            utc = None
            startTime = None
            for line in fileObj:
                if 'RMC' in line:
                    rmcList = line.split(',')
                    if not (rmcList[1] and rmcList[9]):continue
                    utc = rmcList[1]
                    if startTime is None:
                        startTime = (rmcList[9], rmcList[1])
                    if rmcList[7]:novatelDict['speed'] = float(rmcList[7]) * 0.514444
                elif 'GGA' in line:
                    ggaList = line.split(',')
                    utc = ggaList[1]
                    if not utc:continue
                    if ggaList[9]:novatelDict['alt'] = float(ggaList[9]) + float(ggaList[10])
                if novatelDict[mType] > expect:
                    dataList = [utc, novatelDict['alt'], novatelDict['speed']]
                    self.aw_writeRow('Novatel', dataList)
                    return SUC, (utc, startTime)
            return FAIL, '最大值：%s' % str(novatelDict[mType])
        
    def getTestNmeaData(self, device, startTime):
        snFixDict = OrderedDict()  # {'utc':}
        fileName = device.get('sn') + 'nmea.txt'
        startFlag = False
        with open(os.path.join(getLbsCaseLogPath(), fileName), 'rb') as rf:
            for line in rf:
                if startFlag is False:
                    if (startTime[0] in line) and (startTime[1] in line):
                        startFlag = True
                        continue
                if re.search('G.GGA', str(line)):
                    ggaList = str(line).split('GGA,')[1]
                    utc = ggaList[1]
                    if not utc:continue
                    if ggaList[5] == '1':
                        ggaData = {'Lat':ggaList[2], 'Lon':ggaList[4], 'Alt':float(ggaList[9]) + float(ggaList[10]), 'FixFlag':SUC}
                    else:
                        ggaData = {'Lat':-1, 'Lon':-1, 'Alt':-1, 'FixFlag':FAIL}
                        
                    if utc not in snFixDict:
                        snFixDict[utc] = ggaData
                    else:
                        snFixDict[utc].update(ggaData)
                elif re.search('G.RMC', str(line)):
                    rmcList = str(line).split('RMC,')[1]
                    utc = rmcList[1]
                    if not utc:continue
                    speed = float(rmcList[7]) * 0.514444 if rmcList[7] else -1
                    if utc in snFixDict:
                        snFixDict[utc]['speed'] = speed
                    else:snFixDict[utc] = {'speed':speed}
        for utc, msgDict in snFixDict.items():
            dataList = [device.get('sn'), utc, msgDict['Lat'], msgDict['Lon'], msgDict['Alt'], speed, msgDict['FixFlag']]
            self.aw_writeRow('MaxSpeedAlt', dataList)
        self.aw_save()
    
    @AutoPrint(True) 
    def checkMaxSpeed(self, maxSpeed, standardTime):
        resultFailList = []
        standardUtc = int(standardTime[:2]) * 3600 + int(standardTime[2:4]) * 60 + int(standardTime[4:6])
        dataFrame = pd.read_excel(self.caseReportPath, sheet_name='MaxSpeedAlt', dtype=str)
        self.aw_writeRow('Summary', ['DeviceSN', 'StandardSpeed', 'RealSpeed', 'MatchSpeedFlag', 'UnderSpeedFixFlag', 'OverSpeedFixFlag'])
        for deviceName in set(dataFrame['DeviceSN']):
            deviceData = dataFrame[dataFrame['DeviceSN'] == deviceName]
            underSpeedFixFlag = SUC
            overSpeedFixFlag = SUC
            matchSpeedFlag = FAIL
            speed = 0
            for index, row in deviceData.iterrows():
                utcStr = row['Utc']
                utc = int(utcStr[:2]) * 3600 + int(utcStr[2:4]) * 60 + int(utcStr[4:6])
                if standardUtc == utc:
                    speed = row['Speed']
                    if speed >= maxSpeed:
                        matchSpeedFlag = SUC
                        if row['FixFlag'] == '1' and speed > maxSpeed:
                            overSpeedFixFlag = FAIL
                elif standardUtc > utc and (standardUtc - utc) < 2:
                    if row['FixFlag'] == '0':
                        underSpeedFixFlag = FAIL
                elif standardUtc < utc:
                    if row['FixFlag'] == '1':
                        overSpeedFixFlag = FAIL
            if FAIL in [matchSpeedFlag, underSpeedFixFlag, overSpeedFixFlag]:
                resultFailList.append(row['DeviceSN'])
            dataList = [row['DeviceSN'], maxSpeed, speed, matchSpeedFlag, underSpeedFixFlag, overSpeedFixFlag]
            self.aw_writeRow('Summary', dataList)
        self.aw_save()
        if resultFailList:
            return FAIL, '失败设备：%s' % str(resultFailList)
        return SUC, '所有设备都符合标准'
    
    @AutoPrint(True) 
    def checkMaxHeight(self, maxHeight, standardTime):
        resultFailList = []
        standardUtc = int(standardTime[:2]) * 3600 + int(standardTime[2:4]) * 60 + int(standardTime[4:6])
        dataFrame = pd.read_excel(self.caseReportPath, sheet_name='MaxSpeedAlt', dtype=str)
        self.aw_writeRow('Summary', ['DeviceSN', 'StandardAlt', 'RealAlt', 'MatchAltFlag', 'UnderAltFixFlag', 'OverAltFixFlag'])
        for deviceName in set(dataFrame['DeviceSN']):
            deviceData = dataFrame[dataFrame['DeviceSN'] == deviceName]
            underAltFixFlag = SUC
            overAltFixFlag = SUC
            matchAltFlag = FAIL
            height = 0
            for index, row in deviceData.iterrows():
                utcStr = row['Utc']
                utc = int(utcStr[:2]) * 3600 + int(utcStr[2:4]) * 60 + int(utcStr[4:6])
                if standardUtc == utc:
                    height = row['Alt']
                    if height >= maxHeight:
                        matchAltFlag = SUC
                        if row['FixFlag'] == '1' and height > maxHeight:
                            overAltFixFlag = FAIL
                elif standardUtc > utc and (standardUtc - utc) < 2:
                    if row['FixFlag'] == '0':
                        underAltFixFlag = FAIL
                elif standardUtc < utc:
                    if row['FixFlag'] == '1':
                        overAltFixFlag = FAIL
            if FAIL in [matchAltFlag, underAltFixFlag, overAltFixFlag]:
                resultFailList.append(row['DeviceSN'])
            dataList = [row['DeviceSN'], maxHeight, height, matchAltFlag, underAltFixFlag, overAltFixFlag]
            self.aw_writeRow('Summary', dataList)
        self.aw_save()
        if resultFailList:
            return FAIL, '失败设备：%s' % str(resultFailList)
        return SUC, '所有设备都符合标准'

        
if __name__ == '__main__':
    a = pd.read_excel(r'D:\workspace\BF_TTFF_static_roof_Hot_0001.xls', 'Detail')
    print(a)
