#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import shutil
from aw.core.Input import getCurCaseName
from aw.core.Input import getLbsCaseLogPath
from aw.core.Input import SUC
from aw.core.Input import FAIL
from aw.core.Input import isSuc

Archive = r'\\10.100.5.139\Product\2020'

class ReportArchive():
    
    
    def __init__(self):
        pass
    
    def copyLogToServer(self, week):
        '''
        @summary: 拷贝文件到归档路径'''
        srcPath = getLbsCaseLogPath()
        archivePath = os.path.join(Archive, week, 'test_log')
#         if os.path.exists(os.path.join(archivePath, senceName)):
#             return FAIL, 'file exists'
        testNameLogList = os.listdir(srcPath)
        
        for temp in  testNameLogList:
            scenePath = os.path.join(getLbsCaseLogPath(), temp)
            if os.path.isdir(scenePath):
                isSuc(self.copyFile2dstPath(scenePath, archivePath))
                testNameLogList.remove(temp)
                break
        for temp in  testNameLogList:    
            isSuc(self.copyFile2dstPath(os.path.join(srcPath, temp), os.path.join(archivePath, 'nmea_log')))
        return SUC, 'ok'
            
        
    
    def copyFile2dstPath(self, srcPath, dstPath, symlinks=False):
        '''
        @summary: 拷贝文件
        @param srcPath: 源文件路径
        @param dstPath: 要拷贝的路径
        '''
        if os.path.exists(dstPath):
            return FAIL, 'folder exists'
            
        if symlinks and os.path.islink(srcPath):
            linkto = os.readlink(srcPath)
            os.symlink(linkto, dstPath)
        elif os.path.isdir(srcPath):
            shutil.copytree(srcPath, dstPath)
            
        else:
            shutil.copyfile(srcPath, dstPath)
        return SUC, 'OK'
        
        
        
        
        
        
        
        
        