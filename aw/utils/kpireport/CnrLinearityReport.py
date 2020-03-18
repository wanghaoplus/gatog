#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/02/28 12:57
# @Author  : shaochanghong
import os
import time
import pandas as pd
from datetime import datetime
from aw.core.Input import SUC
from aw.core.Input import FAIL
from aw.core.Input import getCurCaseName
from aw.core.Input import getLbsCaseLogPath
from aw.utils.kpireport.ReportBase import ReportExcelBase
CnrLinearityReportObj = None


class CnrLinearityReport(ReportExcelBase):
    '''
    @summary: 每种信号强度下的CNR平均值的线性走势图报告分析模块
    '''
    
    @staticmethod
    def getInstance():
        global CnrLinearityReportObj
        if CnrLinearityReportObj is None:
            CnrLinearityReportObj = CnrLinearityReport()
        return CnrLinearityReportObj
    
    def __init__(self):
        super(CnrLinearityReport, self).__init__()
        self.curCaseName = getCurCaseName()
        self.aw_writeHeader()
    
    @property
    def caseReportPath(self):
        return os.path.join(getLbsCaseLogPath(), 'CnrLinearityReport.xls')
    
    def aw_writeRow(self, dataList, sheetName='Detail'):
        '''
        @summary: 将测试数据写入指定sheet页
        @param sheetName: sheet页名称,Detail
        @param dataList: 待写入的数据
        @return: (SUC, 'OK')
        @author: shaochanghong
        @attention: 
        '''
        if sheetName not in ['Detail','Summary']:
            return FAIL, 'has no this sheet %s' % sheetName
        if self.curCaseName != getCurCaseName():
            self.resetWorkBook()
            self.aw_writeHeader()
            self.curCaseName = getCurCaseName()
        self.writeRow(sheetName, dataList)
        self.aw_save()
        
    def aw_writeHeader(self):
        self.writeHeader('Detail', ['DBM', 'StartTime', 'EndTime'])
        return SUC, 'OK'
    
    def aw_save(self):
        self.save(self.caseReportPath)
        
    def aw_calculateKPI(self):
        self.aw_writeRow(['DeviceSN', 'DBM', 'Cn0Mean'], 'Summary')
        testData = pd.read_excel(self.caseReportPath, sheet_name='Detail', dtype=str)
        for index, row in testData.iterrows():
            dbm = row['DBM']
            startTime = time.mktime(time.strptime(row['StartTime'], '%Y-%m-%d %H:%M:%S'))
            endTime = time.mktime(time.strptime(row['EndTime'], '%Y-%m-%d %H:%M:%S'))
            for nmeaLogName in os.listdir(getLbsCaseLogPath()):
                if 'COM' in nmeaLogName and nmeaLogName.endswith('.txt'):
                    deviceSn = nmeaLogName.split('_')[0]
                    cn0List = []
                    rmcStamp=None
                    startFlag=False
                    with open(os.path.join(getLbsCaseLogPath(), nmeaLogName), 'rb') as rf:
                        for line in rf:
                            if "RMC" in str(line):
                                rmcList = str(line).split('RMC')[-1].split(',')
                                rmcTime = rmcList[1]
                                rmcDate=rmcList[9]
                                if rmcTime and rmcDate:
                                    rmcTimeTuple = time.strptime(rmcDate + rmcTime.split('.')[0], '%d%m%y%H%M%S')
                                    rmcStamp = time.mktime(rmcTimeTuple) + 18
                            elif 'GSV' in str(line):
                                if rmcStamp is None: continue
                                if startTime > rmcStamp: continue
                                elif startTime < rmcStamp < endTime:
                                    startFlag=True
                                    cn0List.extend(self.__calculateViewSatellite(str(line)))
                                elif rmcStamp > endTime:
                                    if startFlag:
                                        break
                    if cn0List:
                        dataList = [deviceSn, dbm, round(sum(cn0List) / len(cn0List), 2)]
                    else:dataList = [deviceSn, dbm, -1]
                    self.aw_writeRow(dataList, 'Summary')
        return SUC, 'OK'
            
    def __calculateViewSatellite(self, line):
        # 解析可见卫星信息
        gsvList = line.split("*")[0].split(",")[4:]
        cn0List = []
        i = 0
        num = len(gsvList) - 1
        while i < num:
            IDNum = gsvList[i]
            if i + 3 > num:
                break
            cno = gsvList[i + 3]
            if IDNum is None or IDNum == '' or cno is None or cno == '':
                i = i + 4
                continue
            IDNum = float(IDNum)
            cn0List.append(float(cno))
            i = i + 4
        return cn0List
            

if __name__=='__main__':
    CnrLinearityReport.getInstance().aw_calculateKPI()