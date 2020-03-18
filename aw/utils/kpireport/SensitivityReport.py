#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/02/28 12:57
# @Author  : shaochanghong
# @Site    : 
# @File    : SensitivityReport.py
import os
from aw.core.Input import SUC
from aw.core.Input import FAIL
from aw.core.Input import getLbsReportPath
from aw.utils.kpireport.ReportBase import ReportExcelBase
SensitivityReportObj = None


class SensitivityReport(ReportExcelBase):
    '''
    @summary: 灵敏度报告模块
    '''
    
    @staticmethod
    def getInstance():
        global SensitivityReportObj
        if SensitivityReportObj is None:
            SensitivityReportObj = SensitivityReport()
        return SensitivityReportObj
    
    def __init__(self):
        super(SensitivityReport, self).__init__()
        self.aw_writeHeader()
    
    @property
    def sensReportPath(self):
        return os.path.join(getLbsReportPath(), 'SensitivityReport.xls')
    
    def aw_writeRow(self, sheetName, dataList):
        '''
        @summary: 将测试数据写入指定sheet页
        @param sheetName: sheet页名称,GeneralStandard or HdbdStandard
        @param dataList: 待写入的数据
        @return: (SUC, 'OK')
        @author: shaochanghong
        @see: SensitivityReport.getInstance().aw_writeRow('GeneralStandard',['DeviceSN', 'TestCase', 'TTFF', 'DBM'])
        @attention: 
        '''
        if sheetName not in ['GeneralStandard', 'HdbdStandard']:
            return FAIL, 'has no this sheet %s' % sheetName
        self.writeRow(sheetName, dataList)
        self.save(self.sensReportPath)
        
    def aw_writeHeader(self):
        self.writeHeader('GeneralStandard', ['DeviceSN', 'TestCase', 'TTFF', 'DBM'])
        self.writeHeader('HdbdStandard', ['DeviceSN', 'TestCase', 'TTFF', 'DBM'])
        return SUC, 'OK'
    

if __name__ == '__main__':
    SensitivityReport.getInstance().aw_writeRow('GeneralStandard', ['abc', 'test001', 8, 20])
    SensitivityReport.getInstance().aw_writeRow('HdbdStandard', ['abc', 'test001', 8, 20])
        
