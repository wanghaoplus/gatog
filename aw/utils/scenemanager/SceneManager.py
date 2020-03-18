#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/02/11 16:41
# @Author  : shaochanghong
# @Site    : 
# @File    : SceneManager.py
import time
import xlrd
import shutil
import ctypes
import os
import platform
import sys
from aw.core.Input import SUC
from aw.core.Input import FAIL
from aw.core.Input import isSuc
from aw.core.Input import AutoPrint
from aw.core.Input import getResourcePath, getLbsCaseLogPath
from scipy.signal._peak_finding import peak_prominences

SCENE_PATH = r'\\10.100.5.163'
# SCENE_PATH = r'\\10.100.5.139\Test_department'


class SceneManager(object):
    
    def __init__(self):
        self.sceneData = {}
        self.sceneList = []
    
    @AutoPrint(True)
    def aw_getSceneMsg(self, sceneId, fileName='scenedata.xlsx', sheetName='scnlist'):
        filePath = os.path.join(getResourcePath(), fileName)
        if not os.path.exists(filePath):
            return FAIL, '%s不存在' % fileName
        excelRead = xlrd.open_workbook(filePath)
        sceneSheet = excelRead.sheet_by_name(sheetName)
        header = sceneSheet.row_values(0)
        for rowNum in range(1, sceneSheet.nrows):
            sceneData = sceneSheet.row_values(rowNum)
            if sceneId in sceneData:
                return SUC, dict(zip(header, sceneData))
#                 self.sceneList.append(dict(zip(header, sceneData)))
#         if self.sceneList:
#             return SUC, 'ok'
        return FAIL, 'has no found this scene.'
    
    @AutoPrint(True)
    def aw_copySceneFromServer2PC(self, srcPath, dstPath):
        return SUC, dstPath
    
    @AutoPrint(True)
    def aw_copyFile2dstPath(self, srcPath, dstPath, symlinks=False):
        if not os.path.exists(srcPath):
            return FAIL, 'scene not exists'
        if not os.path.isdir(dstPath):
            os.makedirs(dstPath)
        
        try:
            if symlinks and os.path.islink(srcPath):
                linkto = os.readlink(srcPath)
                os.symlink(linkto, dstPath)
            elif os.path.isdir(srcPath):
#                 shutil.copytree(srcPath, dstPath)
                cmd = "xcopy /s %s %s /y"% (srcPath, dstPath)
                print(cmd)
                os.system(cmd)
            else:
#                 shutil.copy(srcPath, dstPath)
                cmd = "copy %s %s"% (srcPath, dstPath)
                print(cmd)
                os.popen(cmd)
        except IOError as err:
            return FAIL, 'copy file fail'
        return SUC, dstPath
    
    @AutoPrint(True)
    def aw_copySceneFromSerevr2Labsat(self, sceneId, labsatPath=''):
        """
        @summary:  拷贝要播放的场景到labsat
        @param sceneId:场景编号
        @return: 
        """
        sceneData = isSuc(self.aw_getSceneMsg(sceneId))
        sceneTimeData = isSuc(self.aw_formatSceneTime(sceneData))
        self.sceneData.update(sceneData)
        self.sceneData.update(sceneTimeData)
        print(self.sceneData)
        fileName = sceneData['fileName']
        filePath = os.path.join(SCENE_PATH, sceneData['memoryLocation'], fileName)
        print(filePath, os.path.join(labsatPath, fileName))
        if not os.path.exists(os.path.join(labsatPath, fileName)):
            spaceMB = isSuc(self.getFreeSpaceMB(labsatPath))
            realSize = isSuc(self.getDocRealSize(filePath))
            if realSize < spaceMB -5:
                isSuc(self.aw_copyFile2dstPath(filePath, os.path.join(labsatPath, fileName)))
            else:
                listSenceFile = os.listdir(labsatPath)
                for senceFile in listSenceFile:
                    shutil.rmtree(os.path.join(labsatPath, senceFile)) 
                    spaceMB = isSuc(self.getFreeSpaceMB(labsatPath))
                    if realSize < spaceMB -5:
                        isSuc(self.aw_copyFile2dstPath(filePath, os.path.join(labsatPath, fileName)))
                        break
        isSuc(self.aw_copySceneSpanFromServer(sceneData, fileName))
        return SUC, self.sceneData
    
    @AutoPrint(True)
    def aw_getAndformatSceneData(self):
        '''
        @summary: 暂时弃用
        '''
        childSceneList = []
        for sceneData in self.sceneList:
            if sceneData['sceneId'] not in self.sceneData:
                self.sceneData['sceneId'] = sceneData['sceneId']
                self.sceneData['memoryLocation'] = sceneData['memoryLocation']
            sceneData.pop('sceneId')
            sceneTimeData = isSuc(self.aw_formatSceneTime(sceneData))
            sceneData.update(sceneTimeData)
            childSceneList.append(sceneData)
        self.sceneData['childSceneList'] = childSceneList
        return SUC, self.sceneData
    
    @AutoPrint(True)
    def aw_formatSceneTime(self, sceneData):
        '''
        @summary: 格式化场景开始、结束时间
        '''
        recordTime = sceneData['recordTime']
        recordDate = recordTime[:8]
        startTime = sceneData['startTime']
        utcStartTime = recordDate + startTime.split('\n')[-1][1:-1]
        relaStartTimes = startTime.split('\n')[0].split(':')
        if len(relaStartTimes) != 3 or len(utcStartTime) != 14:
            return FAIL, '场景配置中时间格式不正确'
        startTimeSec = 3600 * int(relaStartTimes[0]) + 60 * int(relaStartTimes[1]) + int(relaStartTimes[1])
        
        endTime = sceneData['endTime']
        utcEndTime = recordDate + endTime.split('\n')[-1][1:-1]
        relaEndTimes = endTime.split('\n')[0].split(':')
        if len(relaEndTimes) != 3 or len(utcEndTime) != 14:
            return FAIL, '场景配置中时间格式不正确'
        endTimeSec = 3600 * int(relaEndTimes[0]) + 60 * int(relaEndTimes[1]) + int(relaEndTimes[1])
        duarTime = endTimeSec - startTimeSec
        utcStartTime = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(utcStartTime, '%Y%m%d%H%M%S'))
        utcEndTime = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(utcEndTime, '%Y%m%d%H%M%S'))
        
        timeKeys = ['startTime', 'endTime', 'utcStartTime', 'utcEndTime', 'duarTime']
        timeValues = [startTimeSec, endTimeSec, utcStartTime, utcEndTime, duarTime]
        return SUC, dict(zip(timeKeys, timeValues))
    
    @AutoPrint(True)
    def aw_copySceneSpanFromServer(self, sceneData, fileName):
        filePath = os.path.join(SCENE_PATH, sceneData['memoryLocation'], 'span', fileName, 'span')
        fileList = os.listdir(filePath)
        spanPath = None
        for file in fileList:
            if file.endswith('.kmz'):
                spanPath = os.path.join(filePath, file)
                isSuc(self.aw_copyFile2dstPath(spanPath, getLbsCaseLogPath()))
                return SUC, 'ok'
        return FAIL, 'has no found this span.'
    
    @AutoPrint(True)
    def getFreeSpaceMB(self, folder):
        """ Return folder/drive free space (in bytes)
        """
        if platform.system() == 'Windows':
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
            size = free_bytes.value/1024/1024/1024
        else:
            st = os.statvfs(folder)
            size = st.f_bavail * st.f_frsize/1024/1024
        
        return SUC, size
        
    @AutoPrint(True)
    def getDocRealSize(self, p_doc):
        size = 0.0
        for root, dirs, files in os.walk(p_doc):
            size += sum([os.path.getsize(os.path.join(root, file)) for file in files])
        size = round(size/1024/1024/1024, 2)
        return SUC, size

            
if __name__ == '__main__':
    scene = SceneManager()
    scene.aw_getSceneMsg('1_Dual_514_4sys_191219')
    scene.aw_copySceneFromSerevr2Labsat('1_Dual_514_4sys_191219')
    srcPath = '6_RTK_Dual_4sys_190530'
#     if os.path.exists(os.path.join(LABSAT_PATH,srcPath)):
#         print('666')
    
