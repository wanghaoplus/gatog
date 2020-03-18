# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/2/9 13:06
# @Author  : shaochanghong
# @Site    : 
# @File    : FTPBase.py

import os
from ftplib import FTP
from aw.core.Input import SUC
from aw.core.Input import FAIL
from aw.core.Input import PRINTTRAC
from aw.core.Input import AutoPrint
from aw.core.Input import singleton


@singleton
class FTPBase(object):
    
    _host = None
    _userName = None
    _pwd = None
    _port = None
    __ftp = None

    def __init__(self, host, userName, pwd, port=21):
        self._host = host
        self._userName = userName
        self._pwd = pwd
        self._port = port
        
    def __del__(self):
        self.quitFTP()
        
    def __connectFtp(self):
        try:
            ftp = FTP()
            ftp.connect(self._host, self._port)
            ftp.login(self._userName, self._pwd)
            return ftp
        except:
            PRINTTRAC('FTP服务器连接失败')
            
    def quitFTP(self):
        if self.__ftp is not None:
            self.__ftp.quit()
            self.__ftp = None
    
    @property
    def ftp(self):
        if self.__ftp is None:
            self.__ftp = self.__connectFtp()
        return self.__ftp
    
    @AutoPrint(True)
    def downloadFile(self, remoteFile, localFile):
        '''
        @summary: 下载文件
        '''
        try:
            dirList=[]
            remoteSplit=remoteFile.split(self._host)[-1].split('/')[1:]
            if len(remoteSplit)>1:
                dirList=remoteSplit[:-1]
                for dirName in dirList:
                    self.ftp.cwd(dirName)
            fileName=remoteSplit[-1]
            fp = open(localFile, 'wb')
            self.ftp.retrbinary('RETR ' + fileName, fp.write, 1024)
            fp.close()
            for dirName in dirList:
                self.ftp.cwd('..')
            return SUC, localFile
        except:
            PRINTTRAC('下载失败')
            return FAIL, '请检查文件路径是否正确'
        
    def uploadFile(self, remoteFile, localFile):
        '''
        @summary: 上传文件
        '''
        try:
            dirList=[]
            remoteSplit=remoteFile.split(self._host)[-1].split('/')[1:]
            if len(remoteSplit)>1:
                dirList=remoteSplit[:-1]
                for dirName in dirList:
                    self.ftp.cwd(dirName)
            fileName=remoteSplit[-1]
            fp = open(localFile, 'rb')
            self.ftp.storbinary('STOR ' + fileName, fp, 1024)
            fp.close()
            for dirName in dirList:
                self.ftp.cwd('..')
            return SUC, localFile
        except:
            PRINTTRAC('上传失败')
            return FAIL, '上传失败'
        
    def downloadDir(self, remoteDicr, localDir):
        '''
        @summary: 下载文件夹
        @attention: 未完成，不可使用
        '''
        try:
            if not os.path.exists(localDir):
                os.makedirs(localDir)        
            self.ftp.cwd(remoteDicr)        
            remoteNames = self.ftp.nlst()        
            for file in remoteNames:            
                local = os.path.join(localDir, file)
                if file.find(".") == -1:
                    if not os.path.exists(local):
                        os.makedirs(local)
                        self.downloadDir(local, file)
                else:
                    self.downloadFile(local, file)
                    self.ftp.cwd("..")
                    return
        except:
            PRINTTRAC('下载失败')
            return FAIL, '下载失败'


if __name__ == "__main__":
    remoteFile='ftp://agnss.hdbds.com/ephemeris/HD_GPS_BDS.hdb'
    localFile = os.path.join(r'D:\LbsEphemeris', 'HD_GPS_BDS.hdb')
    FTPBase('agnss.hdbds.com', 'wangchao', 'Demo_123!', 21).downloadFile(remoteFile, localFile)
