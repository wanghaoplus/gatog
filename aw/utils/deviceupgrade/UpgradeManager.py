# -*- coding: utf-8 -*-
import os
import time
import xlrd
from aw.core.Input import SUC
from aw.core.Input import FAIL
from aw.core.Input import isSuc
from aw.core.Input import PRINTE
from aw.core.Input import AutoPrint
from aw.core.Input import getResourcePath
from aw.utils.deviceupgrade.UpgradeForUser import UpgradeForUser
from aw.utils.deviceupgrade.UpgradeForBoot import UpgradeForBoot
COMPITIVE_DEVICE = ['ublox', 'mtk', 'sony']


class UpgradeManager(object):
    
    def __init__(self):
        self.envList = []
        self.failDeviceList = []
        isSuc(self.aw_getConfMsg())
        
    def aw_checkAllPortsRight(self):
        wrongFlag=False
        for env in self.envList:
            try:
                ip = env['IP']
                port = env['Port']
                connectType = env['connectType']
                upgMode = env['upgMode']
                if upgMode.lower() == 'user':
                    UpgradeForUser(connectType, port, ip)
            except:
                wrongFlag=True
                PRINTE('IP:%s port:%s --->被占用' % (ip, str(port)))
        if wrongFlag:
            raise
            return FAIL,'fail'
        return SUC,'OK'
        
    @AutoPrint(True)
    def aw_startFastboot(self):
        '''
        @summary: 开始升级
        @attention: 设备信息、升级版本、星系组合等在resource/envconfig.xls配置
        '''
        for env in self.envList:
            upgFlag = env['upgFlag']
            if upgFlag.upper() == 'N':
                continue
            ip = env['IP']
            port = env['Port']
            versionFile = env['Firmware']
            connectType = env['connectType']
            upgMode = env['upgMode']
            if upgMode.lower() == 'user':
                fastboot=UpgradeForUser(connectType, port, ip)
                ret = fastboot.fastboot(versionFile)[0]
                if ret == FAIL:
                    self.failDeviceList.append(env)
                    PRINTE('IP:%s port:%s --->升级失败' % (ip, str(port)))
                fastboot.close()
                del fastboot
            elif upgMode.lower() == 'boot':
                chipType = env['chipType']
                fastboot=UpgradeForBoot(connectType, port, ip)
                ret = fastboot.fastboot(chipType, versionFile)[0]
                if ret == FAIL:
                    self.failDeviceList.append(env)
                    PRINTE('IP:%s port:%s --->升级失败' % (ip, str(port)))
                fastboot.close()
                del fastboot
        return SUC,'OK'
            
    @AutoPrint(True)
    def aw_checkUpgradeSuc(self):
        for env in self.envList:
            upgFlag = env['upgFlag']
            if upgFlag.upper() == 'N':
                continue
            ip = env['IP']
            port = env['Port']
            versionFile = env['Firmware']
            connectType = env['connectType']
            hardwareSplit=os.path.split(versionFile)[-1].split('.')
            hardware='.'.join([hardwareSplit[0],hardwareSplit[-4]+hardwareSplit[-3]])
            sucFlag=False
            for _ in range(10):
                fastboot=UpgradeForUser(connectType, port, ip)
                fastboot.sendCommand(bytes.fromhex('F1 D9 0A 04 00 00 0E 34'))
                time.sleep(2)
                ret=fastboot.reciver()
                fastboot.close()
                del fastboot
                if hardware in str(ret):
                    sucFlag=True
                    break
            if sucFlag is False:
                self.failDeviceList.append(env)
        if self.failDeviceList:
            PRINTE(self.failDeviceList)
            return FAIL,[(env['IP'],env['Port']) for env in self.failDeviceList]
        return SUC, 'OK'
    
    @AutoPrint(True)
    def aw_setSatellite(self):
        '''
        @summary: 设置星系组合
        @attention: 设备信息、升级版本、星系组合等在resource/envconfig.xls配置
        '''
        for env in self.envList:
            chipType = env['chipType']
            if chipType.lower() in COMPITIVE_DEVICE:
                continue
            ip = env['IP']
            port = env['Port']
            connectType = env['connectType']
            cmdSat = env['cmdSatellite']
            fastboot = UpgradeForUser(connectType, port, ip)
            fastboot.sendCommand(bytes.fromhex(cmdSat))
            time.sleep(0.1)
            fastboot.close()
            del fastboot
        return SUC, 'OK'
    
    @AutoPrint(True)
    def aw_openDebugLog(self):
        '''
        @summary: 开启debug日志输出
        @attention: 设备信息、升级版本、星系组合等在resource/envconfig.xls配置
        '''
        for env in self.envList:
            chipType = env['chipType']
            if chipType.lower() in COMPITIVE_DEVICE:
                continue
            ip = env['IP']
            port = env['Port']
            connectType = env['connectType']
            fastboot = UpgradeForUser(connectType, port, ip)
            # 打开debug日志输出
            fastboot.sendCommand(bytes.fromhex('F1 D9 02 01 01 00 01 05 12'))
            time.sleep(0.1)
            # 保存配置信息
            fastboot.sendCommand(bytes.fromhex('F1 D9 06 09 08 00 00 00 00 00 2F 00 00 00 46 B7'))
            time.sleep(0.1)
            fastboot.close()
            del fastboot
        return SUC, 'OK'
        
    @AutoPrint(True)
    def aw_getConfMsg(self, fileName='envconfig.xlsx', sheetName='envconfig'):
        '''
        @summary: 读取环境配置表
        '''
        filePath = os.path.join(getResourcePath(), fileName)
        if not os.path.exists(filePath):
            return FAIL, '%s不存在' % fileName
        excelRead = xlrd.open_workbook(filePath)
        envSheet = excelRead.sheet_by_name(sheetName)
        header = envSheet.row_values(0)
        for rowNum in range(1, envSheet.nrows):
            envData = envSheet.row_values(rowNum)
            self.envList.append(dict(zip(header, envData)))
        if self.envList:
            return SUC, 'ok'
        return FAIL, 'config is wrong.'
    
    
if __name__ == '__main__':
    fastboot = UpgradeManager()
    fastboot.aw_checkAllPortsRight()
    fastboot.aw_startFastboot()
    fastboot.aw_checkUpgradeSuc()
    fastboot.aw_setSatellite()
    fastboot.aw_openDebugLog()
