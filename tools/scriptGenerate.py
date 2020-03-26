# -*- coding: utf-8 -*-
# @Time    : 2020/02/21 22:14
# @Author  : wangdelei
# @Site    : 
# @File    : AGNSS_Test_0{num}.py
# @Software: PyCharm
import xlrd
import os
from aw.core.Input import FAIL

def aw_getSceneMsg(rowNum, fileName='scenedata.xlsx', sheetName='scnlist'):
        filePath = r'E:\workspace\LbsTestTools\LBS\resource\scenedata.xlsx'
        excelRead = xlrd.open_workbook(filePath)
        sceneSheet = excelRead.sheet_by_name(sheetName)
        header = sceneSheet.row_values(0)
#         print(sceneSheet.nrows)
        
        sceneData = sceneSheet.row_values(rowNum)
        return rowNum,  dict(zip(header, sceneData))
        

def writePython(num):
    
    aaa, senceDict= aw_getSceneMsg(num)
    for i in range(2, -1, -1):
        li = []
        rowNum =  (num *3 - i)
        senceId = senceDict['sceneId']
        if i ==2:
            senceId = senceDict['sceneId']
            ATNN = ''
        elif i == 1:
            li = senceDict['sceneId'].split('_')
            li.insert(-1, 'down10dB')
            senceId = '_'.join(li)
            
            ATNN = 'self.labsat.aw_labsatATTN(10)'
        elif i == 0:
            li = senceDict['sceneId'].split('_')
            li.insert(-1, 'down20dB')
            senceId = '_'.join(li)
            ATNN = 'self.labsat.aw_labsatATTN(20)'
            print(senceId)
        if rowNum < 10:
            rowNum = '00' + str(rowNum)
        elif rowNum >=10 and rowNum < 100:
            rowNum = '0' + str(rowNum)
        else:
            rowNum = str(rowNum)
        
            
        script = '''# -*- coding: utf-8 -*-
# @Time    : 2020/02/21 22:14
# @Author  : wangdelei
# @Site    : 
# @File    : AGNSS_Test_0{num}.py
# @Software: PyCharm
from aw.LbsTestCase import LbsTestCase
import time
from aw.core.Input import *
import threading
 
class AGNSS_Test_0{num}(LbsTestCase):
 
    def __init__(self):
        super(AGNSS_Test_0{num}, self).__init__()
        self.TestCaseList = ["AGNSS_Test_0{num}"]
 
    def setup(self):
        self.setupStep('labsat')
        super(AGNSS_Test_0{num}, self).setup()
        self.aw_initLabsat()
        loopTimes = self.data.LoopTimes
        sceneId = self.data.sceneId
        print(self.sceneData)
         
         
    def AGNSS_Test_0{num}(self):
        self.testStep("开始测试")
        self.testStep("播放labsat场景")
        self.labsat.aw_labsatPlay(self.sceneData["fileName"], self.sceneData['startTime'], self.sceneData['duarTime'])
        {ATNN}
        time.sleep(self.sceneData['duarTime'])
         
        self.testStep("停止labsat播放")
        self.labsat.aw_labsatStopPlay()
         
        self.testStep("停止串口读取")
        self.lbs.aw_stopReadPort()
         
        self.testStep("分析Nmea数据")
        self.lbs.aw_nmeanalysis(self.sceneData['utcStartTime'], self.sceneData['utcEndTime'], sceneId=self.sceneData['sceneId'])
         
         
    def teardown(self):
        self.teardownStep("ֹͣ测试结束")'''
        scriptPath = r'E:\scriptLibrary\labsat\AGNSS_Test_0%s.py' % rowNum
        print(scriptPath)
        with open(scriptPath, 'w', encoding='utf8') as f:
            f.write(script.format(num=rowNum, ATNN=ATNN))
         
        f.close()
        scriptConfig = '''# -*- coding: utf-8 -*-
     
class AGNSS_Test_0{num}(object):
    LoopTimes = 1
    sceneId = '{senceId}'
         
    class AGNSS_Test_0{num}():
        LoopTimes = 1'''
        configPath = r'E:\scriptLibrary\labsat\script_config\AGNSS_Test_0%s.py' % rowNum
        with open(configPath, 'w', encoding='utf8') as f:
            f.write(scriptConfig.format(num=rowNum, senceId=senceId))
         
        f.close()
 
         
def getSerialConfig( fileName='comConfig.xlsx', sheetName='comConfig'):
        serialDict = {}
        filePath = os.path.join(r'E:\project\LbsTestTools\LBS\resource', fileName)
        if not os.path.exists(filePath):
            return '%s不存在' % fileName
        excelRead = xlrd.open_workbook(filePath)
        comSheet = excelRead.sheet_by_name(sheetName)
        for rowNum in range(comSheet.nrows):
            satelliteInfo = comSheet.cell_value(rowNum, 1)
            comInfo = 'COM'+ str(int(comSheet.cell_value(rowNum, 2))) + '_' 
            serialDict[comInfo] = satelliteInfo
        return  serialDict



if __name__ == '__main__':
    for i in range(1, 62):
        writePython(i)
#     print([i for i in range(2, -1, -1)])
        

 
    
    
    
    
    