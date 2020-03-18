#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/02/28 12:57
# @Author  : shaochanghong
# @Site    : 
# @File    : ReportBase.py
import xlwt
from aw.core.Input import SUC


class ReportExcelBase(object):

    def __init__(self):
        self.__workBook = None
        self.sheetDict = {}
        self.curRowNumDict = {}
    
    @property
    def workBook(self):
        if self.__workBook is None:
            self.__workBook = xlwt.Workbook()
        return self.__workBook
    
    def workSheet(self, sheetName):
        '''
        @summary: 获取sheet页对象
        @param sheetName: sheet页名称
        @author: shaochanghong
        '''
        if sheetName not in self.sheetDict:
            self.addSheet(sheetName)
        return self.sheetDict[sheetName]
    
    def addSheet(self, sheetName, overwrite=True):
        '''
        @summary: 添加sheet页
        @param sheetName: sheet页名称
        @param overwrite: 是否可覆盖写入
        @author: shaochanghong
        '''
        sheetObj = self.workBook.add_sheet(sheetName, overwrite)
        self.curRowNumDict[sheetName] = 0
        self.sheetDict[sheetName] = sheetObj
        
    def writeRow(self, sheetName, dataList):
        '''
        @summary: 将测试数据写入指定sheet页
        @param sheetName: sheet页名称
        @param dataList: 待写入的数据
        @return: (SUC, 'OK')
        @author: shaochanghong
        @attention: 
        '''
        for i in range(len(dataList)):
            self.workSheet(sheetName).write(self.curRowNumDict[sheetName], i, dataList[i])
        self.curRowNumDict[sheetName] += 1
        return SUC, 'OK'
        
    def writeHeader(self, sheetName, headList):
        '''
        @summary: 添加表头索引信息
        @param sheetName: sheet页名称
        @param headList: 待写入的数据
        @return: (SUC, 'OK')
        @author: shaochanghong
        @attention: 
        '''
        self.writeRow(sheetName, headList)
        return SUC, 'OK'
    
    def save(self, savePath):
        self.workBook.save(savePath)
        return SUC, 'OK'
    
    def resetWorkBook(self):
        self.__workBook = None
        self.sheetDict = {}
        self.curRowNumDict = {}
    
