# -*- coding: utf-8 -*-
# @Time    : 2020/02/26 16:14
# @Author  : wangdelei
# @Site    : 
# @File    : AGNSS_Test_001.py
# @Software: PyCharm

import shutil
import os
import time

def aw_copyFile2dstPath(srcPath, dstPath, symlinks=False):
        if not os.path.exists(dstPath):
            os.makedirs(dstPath)
        
        
        if symlinks and os.path.islink(srcPath):
            linkto = os.readlink(srcPath)
            os.symlink(linkto, dstPath)
        elif os.path.isdir(srcPath):
#             shutil.copytree(srcPath, dstPath)
            cmd = "xcopy /s %s %s /y"% (srcPath, dstPath)
            os.system(cmd)
        else:
#                 shutil.copy(srcPath, dstPath)
            cmd = "copy %s %s"% (srcPath, dstPath)
            print(cmd)
            os.popen(cmd)

def copylog():
    for i in range(133, 163):
        dstPath = r'\\10.100.5.139\Product\2020\2020WK12\test_report'
        if i < 10:
            testName = 'AGNSS_Test_00' + '0' + str(i)
        elif i >10 and i < 100:
            testName = 'AGNSS_Test_00' + str(i)
        else:
            testName = 'AGNSS_Test_0' + str(i)
        testpath = os.path.join(r'D:\report\task_20200321_215645\log', testName)
        if not os.path.exists(testpath):
            continue
        testList = os.listdir(testpath)
        for temp in testList:
            if 'Car' in temp:
                srcpath = os.path.join(testpath, temp)
                dstPath = os.path.join(dstPath, temp)
                testList.remove(temp)
                break
        print(srcpath, dstPath)
        aw_copyFile2dstPath(srcpath, dstPath)
        for temp in testList:
            aw_copyFile2dstPath(os.path.join(testpath, temp), os.path.join(dstPath, 'nmea_log'))
            
    

if __name__ == '__main__':
    copylog()
    
    
    