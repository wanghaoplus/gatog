#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/1 17:43
# @Author  : shaochanghong
# @Site    : 
# @File    : CaseConfig.py
# @Software: PyCharm
import os
import xlrd
from autotest.utils.Decorator import singleton
from autotest.core.modle.Variable import VAR
from autotest.core.modle.CustomException import NoSuchCaseException
HEADR_DICT = {'Feature':0, 'ChildFeature':1, 'TestcaseNumber':2, 'SceneID':3, 'TestcaseEnvType':4,
              'HardwarePlatform':5, 'TestcaseExcutePlatform':6, 'Voltage':7}


@singleton
class GroupTestCase(object):
    foundedCaseDict = {}
    
    def groupTestCase(self, fileName='testcase.xlsx'):
        '''
        @summary: 将用例根据使用的仪表类型和场景编号分类
        @attention: 同一仪表类型的用例一次顺序执行完，减少仪表的占用时间
        '''
        filePath = os.path.join(VAR.CurProject.RootPath, 'resource', fileName)
        if not os.path.exists(filePath):
            raise FileNotFoundError('%s不存在' % fileName)
        excelRead = xlrd.open_workbook(filePath)
        for sheetName in excelRead.sheet_names():
            sheetData = excelRead.sheet_by_name(sheetName)
            totalCases = sheetData.col_values(HEADR_DICT['TestcaseNumber'])
            for runTestCase in VAR.CurSuit.CaseList:
                runCaseName = runTestCase.__name__
                if self.foundedCaseDict.get(runCaseName, False):
                    continue
                self.foundedCaseDict[runCaseName] = False
                if runCaseName in totalCases:
                    self.foundedCaseDict[runCaseName] = True
                    rowNum = totalCases.index(runCaseName)
                    envType = sheetData.cell(rowNum, HEADR_DICT['TestcaseEnvType']).value
                    sceneId = sheetData.cell(rowNum, HEADR_DICT['SceneID']).value
                    hardwarePlatform = sheetData.cell(rowNum, HEADR_DICT['HardwarePlatform']).value
                    excutePlatform = sheetData.cell(rowNum, HEADR_DICT['TestcaseExcutePlatform']).value
                    voltage = sheetData.cell(rowNum, HEADR_DICT['Voltage']).value
                    VAR.CurSuit.CaseConfig.addNode(runCaseName)
                    VAR.CurSuit.CaseConfig[runCaseName]['TestcaseEnvType'] = envType
                    VAR.CurSuit.CaseConfig[runCaseName]['SceneID'] = sceneId
                    VAR.CurSuit.CaseConfig[runCaseName]['HardwarePlatform'] = hardwarePlatform
                    VAR.CurSuit.CaseConfig[runCaseName]['TestcaseExcutePlatform'] = excutePlatform
                    VAR.CurSuit.CaseConfig[runCaseName]['Voltage'] = voltage
                    if envType not in VAR.CurSuit.CaseDict:
                        VAR.CurSuit.CaseDict.addNode(envType)
                    if sceneId not in VAR.CurSuit.CaseDict[envType]:
                        VAR.CurSuit.CaseDict[envType][sceneId] = []
                    VAR.CurSuit.CaseDict[envType][sceneId].append(runTestCase)
        for testCaseName, isFounded in self.foundedCaseDict.items():
            if isFounded is False:
                raise NoSuchCaseException(('has no such case: %s in testcase.xlsx' % testCaseName))
        VAR.CurSuit.CaseList.clear()

