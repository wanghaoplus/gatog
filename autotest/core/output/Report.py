# -*- coding: utf-8 -*-
import os
import time
from autotest.core.output import Template
from autotest.core.modle.Variable import VAR


class Report(object):
    
    def __init__(self):
        self.__wFile = None
    
    @property
    def wFile(self):
        if self.__wFile is None:
            self.__wFile = open(os.path.join(VAR.CurProject.ReportPath, 'report.html'), 'a')
        return self.__wFile
    
    def output(self):
        self.wFile.write('<html>\n')
        self.wFile.write(Template.HEADER)
        self.wFile.write(Template.BODY_HEADER)
        self.wFile.write(Template.BODY_JS.format(**{'jsFunction':Template.JS_SHOW}))
        self.wFile.write(self.addBody())
        self.wFile.write(Template.BODY_FOOTER)
        self.wFile.write('/<html>')
        self.wFile.close()
    
    def addBody(self):
        summaryData = self.addSummaryData()
        detailData = self.addDetailData()
        dataDict = {'summaryData':summaryData, 'detailData':detailData}
        return Template.BODY_CONTENT.format(**dataDict)
    
    def addSummaryData(self):
        taskId = VAR.CurProject.TaskId
        testTotal = VAR.CurProject.Total
        testPass = VAR.CurProject.Pass
        testFail = VAR.CurProject.Fail
        testBlock = testTotal - testPass - testFail
        startTime = VAR.CurProject.StartTime
        endTime = VAR.CurProject.EndTime
        end_time = time.mktime(time.strptime(VAR.CurProject.EndTime, '%Y-%m-%d %H:%M:%S'))
        start_time = time.mktime(time.strptime(VAR.CurProject.StartTime, '%Y-%m-%d %H:%M:%S'))
        totalTime = str(round((end_time - start_time) / 60, 2)) + 'min'
        dataDict = {'taskId':taskId, 'testAll':testTotal, 'testPass':testPass,
                    'testFail':testFail, 'testBlock':testBlock, 'startTime':startTime,
                    'endTime':endTime, 'totalTime':totalTime}
        summaryData = Template.SUMMARY_DATA_HEADER + Template.SUMMARY_DATA_CONTENT.format(**dataDict) + Template.SUMMARY_DATA_FOOTER
        return summaryData
    
    def addDetailData(self):
        detailTitle = self.addDetailDataTitle()
        detailFilter = self.addDetailDataFilter()
        caseDataList = self.getTestCaseMsg()
        detailBodyContent = ''
        for caseData in caseDataList:
            detailBodyContent += self.addDetailBodyConetent(caseData)
        dataDict = {'detailDataTitle':detailTitle, 'detailDataFilter':detailFilter, 'detailBodyContent':detailBodyContent}
        return Template.DETAIL_DATA.format(**dataDict)
    
    def addDetailDataTitle(self):
        return Template.DETAIL_DATA_TITLE
    
    def addDetailDataFilter(self, backgroundColor='${color-banner}'):
        detailSummaryLable = self.addDetailSummaryLable()
        dataDict = {'detailSummaryLable':detailSummaryLable, 'backgroundColor':backgroundColor}
        return Template.DETAIL_DATA_FILTER.format(**dataDict)
    
    def addDetailSummaryLable(self):
        testTotal = VAR.CurProject.Total
        testPass = VAR.CurProject.Pass
        testFail = VAR.CurProject.Fail
        testBlock = testTotal - testPass - testFail
        dataDict = {'filterAll':testTotal, 'filterOk':testPass,
                    'filterFail':testFail, 'filterBlock':testBlock}
        return Template.DETAIL_SUMMARY_LABLE.format(**dataDict)
    
    def addDetailBodyConetent(self, caseData):
        loopId = caseData[0]
        caseName = caseData[1]
        startTime = caseData[2]
        endTime = caseData[3]
        testResult = caseData[4]
        caseLog = caseData[5]
        end_time = time.mktime(time.strptime(endTime, '%Y-%m-%d %H:%M:%S'))
        start_time = time.mktime(time.strptime(startTime, '%Y-%m-%d %H:%M:%S'))
        dataDict = {'caseName':caseName, 'startTime':startTime, 'endTime':endTime,
                    'totalTime':str(end_time - start_time) + 's', 'kpiReport':'',
                    'testResult':testResult, 'caseLog':caseLog}
        return Template.DETAIL_BODY_CONTENT.format(**dataDict)
    
    def getTestCaseMsg(self):
        from autotest.utils.DataBase import TestResultDB
        return TestResultDB().getCaseResult()

    
if __name__ == '__main__':
    Report().output()
