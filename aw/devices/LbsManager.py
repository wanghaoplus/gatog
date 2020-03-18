#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/24 09:02
# @Author  : wangdelei
# @Site    :
# @File    : DeviceManager.py
# @Software: ecplise
import os
import xlrd
from aw.core.Input import SUC
from aw.core.Input import isSuc
from aw.core.Input import FAIL
from aw.core.Input import getProjectPath
from aw.core.Input import getResourcePath
from aw.core.Input import getCurCaseName
from aw.core.Input import getLbsCaseLogPath
from aw.devices.LbsManagerBase import LbsManagerBase

LbsManagerObj = None


class LbsManager(object):

    def __init__(self):
        self.manager = LbsManagerBase()
        self.manager.initDevice()
        self.manager.setDebugInfo('open')
        self.deviceList = self.manager.deviceList
        

    @staticmethod
    def getLbsManagerobj():
        global LbsManagerObj
        if LbsManagerObj is None:
            LbsManagerObj = LbsManager()
        return LbsManagerObj
    
    def aw_stopReadPort(self):
        '''
        @summary: 停止读取串口信息
        @return: (SUC, 'ok')
        @see: self.lbs.aw_stopReadPort()
        @author: shaochanghong
        @attention: 
        '''
        return self.manager.stopReadPort()
        
    def aw_startLocation(self, mode='cold', timeout=60):
        '''
        @summary: 发起冷/热/温启动定位
        @param mode: 启动方式 cold/warm/hot
        @param timeout: 超时时间
        @return: (SUC, success info) or (FAIL, fail info)
        @see: self.lbs.startLocation('cold', 60)
        @author: shaochanghong
        @attention: 接口内做对标gga信息处理，并记录冷启动时的gga时间作为启动定位开始时间
        '''
        return self.manager.startLocation(mode, timeout)
    
    def aw_checkLocationSuccess(self, timeout=120, isTracking=False):
        '''
        @summary: 检查设备是否定位成功
        @param timeout: 超时时间
        @param isTracking: 是否是tracking测试
        @return: (SUC, success info) or (FAIL, fail info)
        @see: self.lbs.aw_checkLocationSuccess(120)
        @author: shaochanghong
        @attention: 如果是tracking测试，定位成功后会将queue队列关闭
        '''
        return self.manager.checkLocationSuccess(timeout,isTracking)
        
    def aw_calculateTTFF(self):
        '''
        @summary: 计算ttff
        @return: (SUC, success info) or (FAIL, fail info)
        @see: self.manager.calculateTTFF()
        @author: shaochanghong
        @attention: 
        '''
        return self.manager.calculateTTFF()
    
    def aw_calculateFisrtLocationCep(self, latRef, lonRef, altRef=None, cepType='2D'):
        '''
        @summary: 计算首次定位的cep
        @param latRef: 参考位置纬度
        @param lonRef: 参考位置经度
        @param altRef: 参考位置高度
        @return: (SUC, {'COM1':8.9})
        @see: self.manager.calculateFisrtLocationCep(31.56, 112.39, 89.6, '3D')
        @author: shaochanghong
        @attention: 对tracking场景不适用
        '''
        return self.manager.calculateFisrtLocationCep(latRef, lonRef, altRef, cepType)
    
    def aw_calculateCurrentCep(self, latRef, lonRef, altRef=None, cepType='2D'):
        '''
        @summary: 计算当前位置与参考位置cep
        @param latRef: 参考纬度
        @param lonRef: 参考经度
        @param altRef: 参考高度
        @param cepType: cep误差类型，2D/3D
        @return: (SUC, success info) or (FAIL, fail info)
        @see: self.manager.calculateCurrentCep(31.56, 112.39, 89.6, '3D')
        @author: shaochanghong
        @attention: 对tracking场景不适用
        '''
        return self.manager.calculateCurrentCep(latRef, lonRef, altRef, cepType)
        
    def aw_resetTestData(self):
        '''
        @summary: 重置测试数据
        @return: (SUC, success info) or (FAIL, fail info)
        @see: self.manager.resetTestData()
        @author: shaochanghong
        @attention: 
        '''
        return self.manager.resetTestData()
    
    def aw_checkCepTtffStandard(self, testData:dict, standard=20):
        '''
        @summary: 检查cep/ttff是否超出阈值界限
        @param testData: 测试数据
        @param standard: 阈值界限
        @return: (SUC, success info) or (FAIL, fail info)
        @see: self.lbs.aw_checkCepTtffStandard({'COM1':19},20)
        @author: shaochanghong
        @attention: 
        '''
        return self.manager.checkCepTtffStandard(testData, standard)

    def aw_checkMaxSpeed(self, speed, timeout=1800):
        '''
        @summary: 检查速度极限对定位的影响
        @param speed: 速度极限，单位m/s
        @param timeout: 超时时间
        @return: (SUC, success info) or (FAIL, fail info)
        @see: self.lbs.aw_checkMaxSpeed(515)
        @author: shaochanghong
        @attention: 
        '''
        return self.manager.checkMaxSpeed(speed, timeout)
    
    def aw_checkMaxAltitude(self, alt, timeout=1800):
        '''
        @summary: 检查高度极限对定位的影响
        @param alt: 高度极限，单位m
        @param timeout: 超时时间
        @return: (SUC, success info) or (FAIL, fail info)
        @see: self.lbs.aw_checkMaxAltitude(18000)
        @author: shaochanghong
        @attention: 
        '''
        return self.manager.checkMaxAltitude(alt, timeout)
    
    def aw_setPowerEnable(self, isEnable):
        return self.manager.setPowerEnable(isEnable)

    def aw_reset(self):
        return self.manager.reset()

    def aw_setFactory(self):
        return self.manager.setFactory()

    def aw_setSleepMode(self, mode='Sleep', time=0):
        return self.manager.setSleepMode(mode, time)
    
    def aw_powerAllOff(self, device='all'):
        '''
        @summary: 全部断电
        @param device:测试设备名称 '''
        return self.manager.powerAllOff(device)
    
    def aw_powerMainOff(self, device='all'):
        '''
        @summary: 断设备主电
        @param device:测试设备名称 '''
        return self.manager.powerMainOff(device)
        
        
    def aw_setDebugInfo(self, mode):
        return self.manager.setDebugInfo(mode)
    
    def aw_nmeanalysis(self, starttime, endtime,  sceneId=None, lonRef=None, latRef=None, altRef=None, isSingle=False):
        '''
        @summary: 调用分析工具分析
        @param starttime:场景开始 
        @param endtime:场景结束时间
        @param fileName:场景文件名
        @param sceneId:场景编号 
        @param latRef: 经度值
        @param lonRef: 纬度值  
        @param altRef: 高度值
        '''
        config = isSuc(self._getnmeanalysisconfig(starttime, endtime, lonRef, latRef, altRef, isSingle))
        path = getLbsCaseLogPath()
        if not sceneId:
            sceneId = getCurCaseName()
        
        try:
            configPath = os.path.join(getProjectPath(), 'aw', 'utils', 'nmeanalysis', 'config.py')
            with open(configPath, 'w') as f:
                f.write('#!/usr/bin/env python\n# -*- coding: utf-8 -*-\n')
                f.write('config = ' + str(config))
            f.close()
            nmeaAnalysisPath = os.path.join(getProjectPath(), 'aw', 'utils', 'nmeanalysis', 'AnalysisNMEA.py')
            cmd = r"python " + nmeaAnalysisPath +' ' + path + ' ' + sceneId
            print(cmd)
            os.system(cmd)
        except Exception as e:
            return FAIL, e
        
        return SUC, 'OK'
    def _getnmeanalysisconfig(self, starttime, endtime, lonRef=None, latRef=None, altRef=None, isSingle=False):
        '''
        @summary: 分析工具写配置文件
        @param starttime:场景开始 
        @param endtime:场景结束时间
        @param latRef: 经度值
        @param lonRef: 纬度值  
        @param altRef: 高度值
        '''
        path = getLbsCaseLogPath()
        comDict = isSuc(self._getSerialConfig())
        config = {
        'timeSlicing': {'starttime': '2020-01-07 06:26:18', 'endtime': '2020-01-07 09:35:39'},
        'is_need_single_analysis': False,
        'is_need_static_kpi': False,
        'singleReportPath':'',
        'static_kpi_values': {'ref_longitude': 116, 'ref_alt': 0, 'ref_speed': 0, 'ref_heading': 0, 'ref_latitude': 40},
        'satelliteInfo':{},
        'deviceInfo': []}

        config['timeSlicing']['starttime'] = starttime
        config['timeSlicing']['endtime'] = endtime
        config['satelliteInfo'] = comDict
        if latRef and lonRef and altRef:
            config['is_need_single_analysis'] = True
            config['is_need_static_kpi'] = True
            config['static_kpi_values']['ref_longitude'] = lonRef
            config['static_kpi_values']['ref_latitude'] = latRef
            config['static_kpi_values']['ref_alt'] = altRef
            if os.path.exists(os.path.join(path, getCurCaseName()+'.xls')):
                config['singleReportPath'] = os.path.join(path, getCurCaseName()+'.xls')
                
        if isSingle == True:
            config['is_need_single_analysis'] = True
            if os.path.exists(os.path.join(path, getCurCaseName()+'.xls')):
                config['singleReportPath'] = os.path.join(path, getCurCaseName()+'.xls')
                
        file_list = os.listdir(path)
        deviceInfo = {}
        for temp in file_list:
            deviceInfo = {}
            if temp.endswith('.kmz'):
                deviceInfo['timeZone'] = -18
                deviceInfo['feature'] = 'kmz'
                deviceInfo['tech'] = 'novatel'
                deviceInfo['type'] = 'standard'
                deviceInfo['file_path'] = os.path.join(path, temp)
                config['deviceInfo'].append(deviceInfo)
                
            elif temp.split('.')[0] == 'novatel':
                deviceInfo['timeZone'] = 0
                deviceInfo['feature'] = 'nmea'
                deviceInfo['tech'] = 'novatel'
                deviceInfo['type'] = 'standard'
                deviceInfo['file_path'] = os.path.join(path, temp)
                config['deviceInfo'].append(deviceInfo)
                
            elif temp.endswith('.txt') and temp.split('.')[0] != 'novatel':
                deviceInfo['timeZone'] = 0
                deviceInfo['feature'] = 'nmea'
                deviceInfo['tech'] = temp.split('_')[0]
                deviceInfo['type'] = 'test'
                deviceInfo['file_path'] = os.path.join(path, temp)
                config['deviceInfo'].append(deviceInfo)
            else:
                continue
        
        return SUC, config
    
    def _getSerialConfig(self, fileName='comConfig.xlsx', sheetName='comConfig'):
        '''
        @summary: 获取串口配置信息
        @param fileName:串口配置信息表
         '''
        serialDict = {}
        filePath = os.path.join(getResourcePath(), fileName)
        if not os.path.exists(filePath):
            return FAIL, '%s不存在' % fileName
        excelRead = xlrd.open_workbook(filePath)
        comSheet = excelRead.sheet_by_name(sheetName)
        for rowNum in range(comSheet.nrows):
            satelliteInfo = comSheet.cell_value(rowNum, 1)
            comInfo = 'COM'+ str(int(comSheet.cell_value(rowNum, 2)))
            serialDict[comInfo] = satelliteInfo
            
        return SUC, serialDict
    
    
   
        
            
if __name__ == '__main__':
    pass
    
