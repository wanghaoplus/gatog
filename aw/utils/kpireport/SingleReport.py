#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/02/28 12:57
# @Author  : shaochanghong

import os
import math
from aw.core.Input import SUC
from aw.core.Input import FAIL
from aw.core.Input import getLbsReportPath
from aw.core.Input import getLbsCaseLogPath
from aw.core.Input import getCurCaseName
from aw.utils.kpireport.ReportBase import ReportExcelBase
SingleReportObj = None
SingleCaseReportObj = None


class SingleCaseReport(ReportExcelBase):
    '''
    @summary: 单点定位报告数据
    '''
    
    @staticmethod
    def getInstance():
        global SingleCaseReportObj
        if SingleCaseReportObj is None:
            SingleCaseReportObj = SingleCaseReport()
        return SingleCaseReportObj
    
    def __init__(self):
        super(SingleCaseReport, self).__init__()
        self.curCaseName = getCurCaseName()
        self.curTimes = 0
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
        @see: SingleCaseReport.getInstance().aw_writeRow('FirstFixCepTTFF',['DeviceSN', 'Times', 'StartTime', 'FixTime', 'Lat', 'Lon', 'Alt'])
        @attention: 
        '''
        if sheetName not in ['FirstFixCepTTFF']:
            return FAIL, 'has no this sheet %s' % sheetName
        if self.curCaseName != getCurCaseName():
            self.resetWorkBook()
            self.aw_writeHeader()
            self.curTimes = 1
            self.curCaseName = getCurCaseName()
        dataList.insert(1, self.curTimes)
        self.writeRow(sheetName, dataList)
        
    def aw_writeHeader(self):
        self.writeHeader('FirstFixCepTTFF', ['DeviceSN', 'Times', 'StartTime', 'FixTime', 'Lat', 'Lon', 'Alt', 'FixFlag'])
        return SUC, 'OK'
    
    def aw_save(self):
        self.save(self.caseReportPath)
        

class SingleReport(object):
    '''
    @summary: 计算单点定位的TTFF和CEP
    '''
    
    @staticmethod
    def getInstance():
        global SingleReportObj
        if SingleReportObj is None:
            SingleReportObj = SingleReport()
        return SingleReportObj
    
    def __init__(self):
        super(SingleReport, self).__init__()
    
    @property
    def caseReportPath(self):
        return os.path.join(getLbsCaseLogPath(), getCurCaseName() + '.xls')
      
    @property
    def summReportPath(self):
        return os.path.join(getLbsReportPath(), getCurCaseName() + '.xls')
    
    def calculateCepTTFFKPI(self, latRef, lonRef, altRef):
        import pandas as pd
        from pandas import DataFrame
        pdWriter = pd.ExcelWriter(self.summReportPath)
        testData = pd.read_excel(self.caseReportPath, sheet_name='FirstFixCepTTFF', dtype=str)
        testData['TTFF'] = testData.apply(lambda row: self.__calculateTTFF(row), axis=1)
        testData['Cep2D'] = testData.apply(lambda row: self.__calculateDistance(lonRef, latRef, row[5], row[4]), axis=1)
        testData['Cep3D'] = testData.apply(lambda row: self.__calculateDistance3D(lonRef, latRef, altRef, row[5], row[4], row[6]), axis=1)
        testData['CepAlt'] = testData.apply(lambda row: self.__calculateDistanceAlt(altRef, row[6]), axis=1)
        testData.to_excel(pdWriter, sheet_name='Detail', index=False, header=True)
        
        dataList = []
        for deviceName in set(testData['DeviceSN']):
            deviceData = testData[testData['DeviceSN'] == deviceName]
            deviceData.drop(index=(deviceData.loc[(deviceData['FixFlag']==1)].index))
            ttffMin = self.__calculateMin(deviceData['TTFF'])
            ttffMax = self.__calculateMax(deviceData['TTFF'])
            ttffMean = self.__calculateMean(deviceData['TTFF'])
            ttff50 = self.__calculate(deviceData['TTFF'], 50)
            ttff68 = self.__calculate(deviceData['TTFF'], 68)
            ttff95 = self.__calculate(deviceData['TTFF'], 95)
            ttff98 = self.__calculate(deviceData['TTFF'], 98)
            ttffSTD = self.__calculateSTD(deviceData['TTFF'])
            
            cep2DMin = self.__calculateMin(deviceData['Cep2D'])
            cep2DMax = self.__calculateMax(deviceData['Cep2D'])
            cep2DMean = self.__calculateMean(deviceData['Cep2D'])
            cep2D50 = self.__calculate(deviceData['Cep2D'], 50)
            cep2D68 = self.__calculate(deviceData['Cep2D'], 68)
            cep2D95 = self.__calculate(deviceData['Cep2D'], 95)
            cep2D98 = self.__calculate(deviceData['Cep2D'], 98)
            cep2DSTD = self.__calculateSTD(deviceData['cep2D'])
            
            cep3DMin = self.__calculateMin(deviceData['Cep3D'])
            cep3DMax = self.__calculateMax(deviceData['Cep3D'])
            cep3DMean = self.__calculateMean(deviceData['Cep3D'])
            cep3D50 = self.__calculate(deviceData['Cep3D'], 50)
            cep3D68 = self.__calculate(deviceData['Cep3D'], 68)
            cep3D95 = self.__calculate(deviceData['Cep3D'], 95)
            cep3D98 = self.__calculate(deviceData['Cep3D'], 98)
            cep3DSTD = self.__calculateSTD(deviceData['cep3D'])
            
            cepAltMin = self.__calculateMin(deviceData['CepAlt'])
            cepAltMax = self.__calculateMax(deviceData['CepAlt'])
            cepAltMean = self.__calculateMean(deviceData['CepAlt'])
            cepAlt50 = self.__calculate(deviceData['CepAlt'], 50)
            cepAlt68 = self.__calculate(deviceData['CepAlt'], 68)
            cepAlt95 = self.__calculate(deviceData['CepAlt'], 95)
            cepAlt98 = self.__calculate(deviceData['CepAlt'], 98)
            cepAltSTD = self.__calculateSTD(deviceData['CepAlt'])
            
            fixRate = self.__calculateFixRate(deviceData['FixFlag'])
            rowData = [deviceName, fixRate, ttff50, ttff68, ttff95, ttff98, ttffMin, ttffMax, ttffMean, ttffSTD,
                   cep2D50, cep2D68, cep2D95, cep2D98, cep2DMin, cep2DMax, cep2DMean, cep2DSTD,
                   cep3D50, cep3D68, cep3D95, cep3D98, cep3DMin, cep3DMax, cep3DMean, cep3DSTD,
                    cepAlt50, cepAlt68, cepAlt95, cepAlt98, cepAltMin, cepAltMax, cepAltMean, cepAltSTD]
            dataList.append(rowData)
        summaryData = pd.DataFrame(dataList, columns=['DeviceSN', 'FixRate', 'firstFixTTFF50', 'firstFixTTFF68', 'firstFixTTFF95', 'firstFixTTFF98', 'firstFixTTFFMin', 'firstFixTTFFMax', 'firstFixTTFFMean', 'firstFixTTFFSTD', 
                                            'firstFixCep2D50', 'firstFixCep2D68', 'firstFixCep2D95', 'firstFixCep2D98', 'firstFixCep2DMin', 'firstFixCep2DMax', 'firstFixCep2DMean', 'firstFixCep2DSTD',
                                            'firstFixCep3D50', 'firstFixCep3D68', 'firstFixCep3D95', 'firstFixCep3D98', 'firstFixCep3DMin', 'firstFixCep3DMax', 'firstFixCep3DMean', 'firstFixCep3DSTD',
                                            'firstFixCepAlt50', 'firstFixCepAlt68', 'firstFixCepAlt95', 'firstFixCepAlt98', 'firstFixCepAltMin', 'firstFixCepAltMax', 'firstFixCepAltMean', 'firstFixCepAltSTD'])
        summaryData.to_excel(pdWriter, sheet_name='Summary', index=False, header=True)
        pdWriter.save()
        return SUC, 'OK'
    
    def __calculateFixRate(self, columnData):
        fixList = [value for value in list(columnData) if int(value) == 1]
        fixRate = 100 * len(fixList) / len(columnData)
        return str(round(fixRate, 2)) + '%'

    def __calculate(self, columnData, mType):
        index = int(mType * len(columnData) / 100)
        columnData = [value for value in list(columnData) if float(value) != -10]
        columnData = list(columnData)
        columnData.sort()
        return round(columnData[index], 3)
    
    def __calculateMin(self, columnData):
        columnData = [value for value in list(columnData) if float(value) != -10]
        columnData = list(columnData)
        return round(min(columnData), 3)
    
    def __calculateMax(self, columnData):
        columnData = [value for value in list(columnData) if float(value) != -10]
        columnData = list(columnData)
        return round(max(columnData), 3)
    
    def __calculateMean(self, columnData):
        columnData = [value for value in list(columnData) if float(value) != -10]
        columnData = list(columnData)
        return round(sum(columnData) / len(columnData), 3)
        
    def __calculateTTFF(self, row):
        startUtc = str(row[2])
        endUtc = str(row[3])
        if startUtc and endUtc:
            startTime = int(startUtc[:2]) * 3600 + int(startUtc[2:4]) * 60 + int(startUtc[4:6]) + float(startUtc.split('.')[-1]) / 1000
            endTime = int(endUtc[:2]) * 3600 + int(endUtc[2:4]) * 60 + int(endUtc[4:6]) + float(endUtc.split('.')[-1]) / 1000
            ttff = endTime - startTime
            return ttff
        return -10
    def __calculateSTD(self, columnData):
        import numpy as np
        columnData = [value for value in list(columnData) if float(value) != -10]
        columnData = list(columnData)
        return round(np.std(columnData, ddof=1), 3)
        
    
    def __convertdmmmmmm2d(self, titude):
        '''
        @titude 原始的符合dmm.mmmm规则的经纬度，小数点前至少3位数字，小数点后必须1位数字
        @return 小数的经纬度字符串
        '''
        import re
        titude = str(titude)
        if not re.match("^\d{3,}\.\d{1,}$", titude):
            return ''
        dmm, mmmm = titude.split('.')
        d = dmm[:-2]
        mm = dmm[-2:]
        titude_f = float(d) + float('%s.%s' % (mm, mmmm)) / 60
        return titude_f
    
    def __calculateDistanceAlt(self, altStart, altEnd):
        if not (altStart and altEnd):
            return -10
        altStart = float(altStart)
        altEnd = float(altEnd)
        return round(altEnd - altStart, 3)
    
    def __calculateDistance3D(self, lonStart, latStart, altStart, lonEnd, latEnd, altEnd):
        if not (altStart and altEnd):
            return -10
        altStart = float(altStart)
        altEnd = float(altEnd)
        HorErr = self.__calculateDistance(lonStart, latStart, lonEnd, latEnd)
        Distance3D = math.sqrt(HorErr * HorErr + (altStart - altEnd) * (altStart - altEnd))
        return round(Distance3D, 3)
    
    def __calculateDistance(self, lon_start, lat_start, lon_end, lat_end):
        if not (lon_end and lat_end):
            return -10
        import math
        GEO_RADIUS_O_FEARTH = 6370856
        COE_DEG2RAD = 0.0174532925
        lon_start = float(lon_start)
        lat_start = float(lat_start)
        lon_end = self.__convertdmmmmmm2d(lon_end)
        lat_end = self.__convertdmmmmmm2d(lat_end)

        lon_start = lon_start * COE_DEG2RAD
        lat_start = lat_start * COE_DEG2RAD
        lon_end = lon_end * COE_DEG2RAD
        lat_end = lat_end * COE_DEG2RAD

        rel_xy_1 = (lon_end - lon_start) * GEO_RADIUS_O_FEARTH * math.cos(lat_start)
        rel_xy_2 = (lat_end - lat_start) * GEO_RADIUS_O_FEARTH

        distance = math.sqrt(rel_xy_1 * rel_xy_1 + rel_xy_2 * rel_xy_2)
        return round(distance, 2)
    

if __name__ == '__main__':
    SingleReport.getInstance().calculateCepTTFFKPI(22.6324465, 114.0637045, 117.1)
