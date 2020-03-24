# coding:utf-8
import os
# from common.utils import gl_var
import numpy as np
import time
from datetime import datetime
from pandas import DataFrame
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import csv
import xlrd
import xlwt
import random
import traceback
from aw.utils.nmeanalysis.ActionDB import ActionDB
from aw.utils.nmeanalysis.AresInput import PRINTI
from aw.utils.nmeanalysis.AresInput import PRINTE
from aw.utils.nmeanalysis.AresInput import LBSDector
from aw.utils.nmeanalysis.AresInput import DT_FAIL
from aw.utils.nmeanalysis.AresInput import DT_SUC
from aw.utils.nmeanalysis.html_report.htmlManager import HtmlManager
from scipy import stats
from matplotlib.ticker import FuncFormatter
from _operator import le

A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26

general_data_col = ['UTC', 'UsedSV', 'TOP5CN', 'HDOP', 'VDOP', 'PDOP', 'GPSCount', 'GLNCount', 'GALCount', 'BDSCount', 'QZSCount', 'SVCount', 'GPSL5VCount', 'QZL5VCount', 'GAL5VCount',
                    'GPSSACount', 'GLNSACount', 'GALSACount', 'BDSSACount', 'QZSACount', 'SACount', 'GPSL5ACount', 'QZL5ACount', 'GAL5ACount', 'GPSViewTop5CNAve', 'GLNViewTop5CNAve',
                    'GALViewTop5CNAve', 'BDSViewTop5CNAve', 'QZViewTop5CNAve', 'GPSL5ViewTop5CNAve', 'GPSL1L5ViewTop5CNAve', 'QZL5ViewTop5CNAve', 'QZL1L5ViewTop5CNAve', 'GAL5ViewTop5CNAve', 'GAL1L5ViewTop5CNAve']
error_data_col = ['UTC', 'position_error', 'heading_error', 'speed_error', 'alt_error', 'shoot_error', "along_error", "across_error", "distance3D_error"]
mileage_data_col = ['UTC', 'mileage']

single_error_col = ['firstFixTTFF', 'firstFixCep2D','firstFixCep3D',  'firstFixCepAlt']
single_error_list = ['firstFixTTFF', 'firstFixCep2D', 'firstFixCep3D', 'firstFixCepAlt', 'lostRate']

error_kpi_list = ['position_error', 'heading_error', 'speed_error', 'alt_error', 'overshoot_error', 'undershoot_error', "along_error", "across_error", "distance3D_error", "HDOP", "VDOP", "PDOP"]  # 画曲线用到
satellite_curve_chart_list = [['GPSCount', 'GLNCount', 'GALCount', 'BDSCount', 'QZSCount', 'SVCount', 'GPSL5VCount', 'QZL5VCount', 'GAL5VCount'],
                            ['GPSSACount', 'GLNSACount', 'GALSACount', 'BDSSACount', 'QZSACount', 'SACount', 'GPSL5ACount', 'QZL5ACount', 'GAL5ACount'],
                            ['GPSViewTop5CNAve', 'GLNViewTop5CNAve', 'GALViewTop5CNAve', 'BDSViewTop5CNAve', 'QZViewTop5CNAve', 'GPSL5ViewTop5CNAve', 'QZL5ViewTop5CNAve', 'GAL5ViewTop5CNAve']]

color_list = ['#FF0000', '#008000', '#FFA500', '#FFC0CB', '#000000', '#AFEEEE', '#FFD700', '#EE82EE', '#0000FF', '#808080', '#CD853F', '#FF00FF', '#D2691E', '#00FFFF', '#800000', '#A9A9A9', '#191970', '#FAF0E6', '#4B0082', '#FF4500', '#ADD8E6', '#FF69B4',
              '#556B2F', '#F5FFFA', '#FF7F50', '#F0F8FF', '#BC8F8F', '#9ACD32', '#9932CC', '#483D8B', '#FF1493', '#FAA460', '#40E0D0', '#FFF0F5', '#DDA0DD', '#808000', '#D8BFD8', '#FAFAD2', '#FFE4B5', '#00FF7F', '#DCDCDC', '#00BFFF', '#FFFAF0', '#B8860B',
              '#FFF8DC', '#708090', '#006400', '#8A2BE2', '#FF6347', '#90EE90', '#8B0000', '#3CB371', '#D3D3D3', '#7FFFD4', '#9370DB', '#BDB76B', '#CD5C5C', '#D2B48C', '#1E90FF', '#E9967A', '#FFEFD5', '#A0522D', '#6495ED', '#FFEBCD', '#008080', '#FFFFF0',
              '#8FBC8F', '#FA8072', '#00008B', '#778899', '#7FFF00', '#00FF00', '#32CD32', '#DB7093', '#A52A2A', '#4169E1', '#0000CD', '#FFFFE0', '#EEE8AA', '#B0E0E6', '#F8F8FF', '#66CDAA', '#DEB887', '#800080', '#00CED1', '#FFFF00', '#FF8C00', '#E6E6FA',
              '#00FA9A', '#FDF5E6', '#8B008B', '#4682B4', '#ADFF2F', '#FFB6C1', '#F0E68C', '#DAA520', '#DA70D6', '#FFE4E1', '#5F9EA0', '#2E8B57', '#FFA07A', '#87CEFA', '#B22222', '#FFDAB9', '#87CEEB', '#7B68EE', '#008B8B', '#228B22', '#FFDEAD', 
              '#F0FFF0', '#696969', '#F5DEB3', '#20B2AA', '#6B8E23', '#E0FFFF', '#DC143C', '#7CFC00', '#C71585', '#C0C0C0', '#000080', '#BA55D3', '#48D1CC', '#6A5ACD', '#F08080', '#8B4513', '#FFFACD', '#B0C4DE', '#98FB98', '#F0FFFF', '#9400D3', '#2F4F4F']



class AnalyzeModule():
    def __init__(self, reportPath, config):
        self.reportPath = reportPath
        self.config = config
        self.htm_mgr = HtmlManager(self.reportPath, self.config, color_list)
        self.excelObj = xlwt.Workbook(encoding='utf-8')
        self.excelRow = 0

    # 初始化数据结构，用于保存从数据库提取的数据，防止从数据库重复提取，影响性能
    def init_data_structure(self):
        for test_device, info in self.device_info.items():
            self.data_container[test_device] = {}
            self.single_report_data_container[test_device] = {}
        self.data_container['novatel'] = {}

        for kpi_error in error_kpi_list:
            self.statistics_dict[kpi_error] = {}
        
        self.statistics_dict['satelliteSV'] = {}
        self.statistics_dict['satelliteSA'] = {}
        self.statistics_dict['satellite_in_view_top5_ave'] = {}
        if self.config['singleReportPath'] and self.config['is_need_single_analysis'] == True:
            for kpi_error in single_error_list:
                self.statistics_dict[kpi_error] = {}
                
            
    
    def query_useful_data(self):
        noDataDrviceList = []
        if self.config['is_need_static_kpi'] == False:
            self.get_device_novatel_mileage('novatel')
        print(self.device_info, self.device_order)
        for test_device, info in self.device_info.items():
            try:
                if info.get('type') == 'standard':
                    continue
                self.get_device_general_data(test_device)
                self.get_device_error_data(test_device)
                if self.config['is_need_static_kpi'] == False:
                    self.get_device_novatel_mileage(test_device)
                self.get_device_table_error_kpi_data(test_device)
                self.get_device_table_satellite_data(test_device)
                self.get_device_table_satellite_in_view_top5_ave(test_device)
                if self.config['is_need_single_analysis'] == True:
                    if not os.path.exists(self.config['singleReportPath']):
                        print('path no exists')
                        raise
                        continue
                    self.get_device_Single_general_data(test_device)
                    self.get_device_Single_table_data(test_device)
                
            except Exception as e:
                noDataDrviceList.append(test_device)
                PRINTE('The test device %s no data' % test_device)
                PRINTE(traceback.format_exc())
                raise e
                
                
        if noDataDrviceList:
            print(noDataDrviceList, 666)
            for noDataDrvice in noDataDrviceList:
                self.device_info.pop(noDataDrvice)
                self.device_order.remove(noDataDrvice)
                self.data_container.pop(noDataDrvice)
            self.device_info.update()
            self.data_container.update()

    @LBSDector(True)
    def get_device_table_satellite_in_view_top5_ave(self, test_device):
        try:
            general_datas = self.data_container[test_device]['general_data']
            general_data = DataFrame(general_datas, columns=general_data_col)[:].astype(str)
            gps_top5_ave = self.calculate_top5_ave_for_satellite(general_data[['GPSViewTop5CNAve']].astype(float)['GPSViewTop5CNAve'].values.tolist())
            gln_top5_ave = self.calculate_top5_ave_for_satellite(general_data[['GLNViewTop5CNAve']].astype(float)['GLNViewTop5CNAve'].values.tolist())
            gal_top5_ave = self.calculate_top5_ave_for_satellite(general_data[['GALViewTop5CNAve']].astype(float)['GALViewTop5CNAve'].values.tolist())
            bds_top5_ave = self.calculate_top5_ave_for_satellite(general_data[['BDSViewTop5CNAve']].astype(float)['BDSViewTop5CNAve'].values.tolist())
            qz_top5_ave = self.calculate_top5_ave_for_satellite(general_data[['QZViewTop5CNAve']].astype(float)['QZViewTop5CNAve'].values.tolist())
            gpsl5_top5_ave = self.calculate_top5_ave_for_satellite(general_data[['GPSL5ViewTop5CNAve']].astype(float)['GPSL5ViewTop5CNAve'].values.tolist())
            gpsl1l5_top5_ave = self.calculate_top5_ave_for_satellite(general_data[['GPSL1L5ViewTop5CNAve']].astype(float)['GPSL1L5ViewTop5CNAve'].values.tolist())
            gal5_top5_ave = self.calculate_top5_ave_for_satellite(general_data[['GAL5ViewTop5CNAve']].astype(float)['GAL5ViewTop5CNAve'].values.tolist())
            gal1l5_top5_ave = self.calculate_top5_ave_for_satellite(general_data[['GAL1L5ViewTop5CNAve']].astype(float)['GAL1L5ViewTop5CNAve'].values.tolist())
            qzl5_top5_ave = self.calculate_top5_ave_for_satellite(general_data[['QZL5ViewTop5CNAve']].astype(float)['QZL5ViewTop5CNAve'].values.tolist())
            qzl1l5_top5_ave = self.calculate_top5_ave_for_satellite(general_data[['QZL1L5ViewTop5CNAve']].astype(float)['QZL1L5ViewTop5CNAve'].values.tolist())
            all_top5_ave = gps_top5_ave + gln_top5_ave + gal_top5_ave + bds_top5_ave + qz_top5_ave + gpsl5_top5_ave + gpsl1l5_top5_ave + gal5_top5_ave + gal1l5_top5_ave + qzl5_top5_ave + qzl1l5_top5_ave
            top5_ave_list = []
            top5_ave_list.append(gps_top5_ave)
            top5_ave_list.append(gln_top5_ave)
            top5_ave_list.append(gal_top5_ave)
            top5_ave_list.append(bds_top5_ave)
            top5_ave_list.append(qz_top5_ave)
            top5_ave_list.append(gpsl5_top5_ave)
            top5_ave_list.append(gpsl1l5_top5_ave)
            top5_ave_list.append(gal5_top5_ave)
            top5_ave_list.append(gal1l5_top5_ave)
            top5_ave_list.append(qzl5_top5_ave)
            top5_ave_list.append(qzl1l5_top5_ave)
            top5_ave_list.append(round(all_top5_ave, 2))
            top5_ave_list.append(self.statistics_dict['position_error'][test_device][4])
            self.statistics_dict['satellite_in_view_top5_ave'][test_device] = top5_ave_list
        except Exception as e:
            raise e

    
    def get_device_error_data(self, test_device):
        try:
            tab = test_device + 'Error'
            error_data = self.resource_action_db.getcolomFormDB(tab, error_data_col, self.start_time, self.end_time)
            error_data_df = DataFrame(error_data, columns=error_data_col)[:].astype(str)
    
            for kpi in error_kpi_list[0:-3]:
                if kpi == "overshoot_error":
                    data = error_data_df[['shoot_error', 'UTC']]
                    for i in range(len(data)):
                        if data['shoot_error'][i] == '':
                            data = data.drop(i)
    
                    # self.data_container[test_device][kpi] = data[data['shoot_error'].astype(float) >= 0][['UTC', 'shoot_error']].values.tolist()
                    self.data_container[test_device][kpi] = error_data_df[error_data_df['shoot_error'].astype(float) >= 0][['UTC', 'shoot_error']].values.tolist()
                    continue
                elif kpi == "undershoot_error":
                    # undershoot_data = data[data['undershoot_error'].astype(float) < 0].loc[:, ['UTC', 'shoot_error']]
                    undershoot_data = error_data_df[error_data_df['shoot_error'].astype(float) < 0].loc[:, ['UTC', 'shoot_error']]
                    undershoot_data['shoot_error'] = np.abs(undershoot_data['shoot_error'].astype(float))
                    self.data_container[test_device][kpi] = undershoot_data.values.tolist()
                    continue
                self.data_container[test_device][kpi] = error_data_df[['UTC', kpi]].values.tolist()
        except Exception as e:
            raise e
            
    @LBSDector(True)
    def get_device_novatel_mileage(self, test_device):
        try:
            tab_mileage = test_device + "Mileage"
            mileage_data = self.resource_action_db.getcolomFormDB(tab_mileage, mileage_data_col, self.start_time, self.end_time)
            mileage_data_df = DataFrame(mileage_data, columns=mileage_data_col)[:].astype(str)
            if test_device.lower().find('novatel') != -1:
                self.data_container[test_device]['novatel_mileage'] = mileage_data_df[['UTC', 'mileage']].values.tolist()
            else:
                self.data_container[test_device]['test_mileage'] = mileage_data_df[['UTC', 'mileage']].values.tolist()
        except Exception as e:
            raise e
    
    def get_device_Single_general_data(self, test_device):
        '''获取单点定位数据'''
        tab_single = test_device + 'single'
        deviceData = self.resource_action_db.getcolomFormDB(tab_single, single_error_col)
        deviceData = DataFrame(deviceData, columns=single_error_col)[:].astype(float)
        for kpi in single_error_col:
            self.data_container[test_device][kpi] = deviceData[kpi].values.tolist()
        
        self.data_container[test_device][single_error_list[-1]] = self.get_device_Single_lost_rate(test_device)

    def get_device_Single_lost_rate(self, test_device):
        tab_single = test_device + 'single'
        lost_rate_list = []
        lost_rate_col = ['firstFixStartUTC', 'firstFixUTC']
        deviceData = self.resource_action_db.getcolomFormDB(tab_single, lost_rate_col)
        deviceData = DataFrame(deviceData, columns=lost_rate_col)[:].astype(str)
        StartTimeList = deviceData['firstFixStartUTC'].values.tolist()
        firstFixUTCList = deviceData['firstFixUTC'].values.tolist()
        for index in range(len(StartTimeList)):
            if index != len(StartTimeList)-1:
                trackFixStartTime = firstFixUTCList[index]
                if len(trackFixStartTime) == 3:
                    lost_rate_list.append(-10)
                    continue
                trackFixendTime = StartTimeList[index+1]
                secondNum = self._get_tracking_second(trackFixStartTime ,trackFixendTime)
                fixNum = self.resource_action_db.getFixNum(test_device, trackFixStartTime ,trackFixendTime)
                lost_rate = float(1-int(fixNum[0][0])/secondNum)
                lost_rate_list.append(lost_rate)
        
        maxFixtime = self.resource_action_db.getFixMaxTime(test_device)

        fixNum = self.resource_action_db.getFixNum(test_device, firstFixUTCList[-1], maxFixtime[0][0])
        if len(firstFixUTCList[-1]) == 3:
            lost_rate_list.append(-10)
            return lost_rate_list
        secondNum = self._get_tracking_second(firstFixUTCList[-1], maxFixtime[0][0])
        lost_rate = float(1-int(fixNum[0][0])/secondNum)
        lost_rate_list.append(lost_rate)
        
        return lost_rate_list
                
    def _get_tracking_second(self, startTime, endTime):
        import datetime
        startTime2 = datetime.datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
        endTime2 = datetime.datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S")
        seconds = (endTime2 - startTime2).seconds  
        return int(seconds) +1    
            
    
    def get_device_Single_table_data(self, test_device):
        '''获取单点定位数据'''
        try:
            tab_single = test_device + 'single'
            positionData = self.resource_action_db.getcolomFormDB(tab_single, ['FixFlag'])
            positionData  = DataFrame(positionData, columns=['FixFlag'])[:].astype(float)
            columnData = positionData['FixFlag'].values.tolist()
            fixList = [value for value in list(columnData) if int(value) == 1]
            fixRate = 100 * len(fixList) / len(columnData)
            fixRate = str(round(fixRate, 2)) + '%'
            
            
            for kpi in single_error_list:
                tab_data_single_list = []
                col_data = self.data_container.get(test_device).get(kpi)
                col_data = [float(value) for value in list(col_data) if float(value) != -10]
                col_data = list(col_data)
                col_data.sort()
                tab_data_single_list = self._table_kpi_error_data(col_data)
                tab_data_single_list.append(fixRate)
                self.statistics_dict[kpi][test_device] = tab_data_single_list
           
        except Exception as e:
            raise e
        
    
            
    def get_device_general_data(self, test_device):

        general_data = self.resource_action_db.getcolomFormDB(test_device, general_data_col, self.start_time, self.end_time)
        general_data = DataFrame(general_data, columns=general_data_col)[:].astype(str)

        self.data_container[test_device]['general_data'] = general_data.values.tolist()
        for kpi in general_data_col:
            self.data_container[test_device][kpi] = general_data[['UTC', kpi]].values.tolist()

    def calculate_top5_ave_for_satellite(self, datas):
        data_len = len(datas)
        if data_len == 0:
            return None
        else:
            return round(sum(datas) / float(len(datas)), 2)

    @LBSDector(True)
    def get_device_table_error_kpi_data(self, test_device):
        for kpi in error_kpi_list:
            tab_data_kpi_list = []
            if kpi == 'position_error':
                self.get_device_position_error_kpi_data(test_device, kpi)
                continue

            col_data = self.data_container.get(test_device).get(kpi)
            col_data = DataFrame(col_data, columns=['UTC', kpi])
            if len(col_data) == 0:
                PRINTI('%s position_error data is empty' % test_device)
                self.statistics_dict[kpi][test_device] = ['NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE']
                continue
            col_data = col_data[[kpi]].astype(float)
            col_data = col_data.sort_values(by=kpi)[kpi].values.tolist()
            tab_data_kpi_list = self._table_kpi_error_data(col_data)

            
            # locate rate
            extra_data = self.data_container.get(test_device).get('general_data')
            if len(extra_data) == 0:
                tab_data_kpi_list.append('NONE')
            else:
                num = len(extra_data)
                temp_data = (1.0 - (self.time_difference - num) / self.time_difference) * 100
                temp_data = format(temp_data, '.2f')
                tab_data_kpi_list.append(temp_data)


            self.statistics_dict[kpi][test_device] = tab_data_kpi_list
            
    
    def _table_kpi_error_data(self, col_data):
        
            tab_data_list = []
            #
            data_len = int(len(col_data) * 0.5)
            temp_data = col_data[data_len]
            temp_data = round(temp_data, 2)
            temp_data = format(temp_data, '.2f')
            tab_data_list.append(temp_data)
            # 68
            data_len = int(len(col_data) * 0.68)
            temp_data = col_data[data_len]
            temp_data = round(temp_data, 2)
            temp_data = format(temp_data, '.2f')
            tab_data_list.append(temp_data)
            # 95
            data_len = int(len(col_data) * 0.95)
            temp_data = col_data[data_len]
            temp_data = round(temp_data, 2)
            temp_data = format(temp_data, '.2f')
            tab_data_list.append(temp_data)
            
            # 98
            data_len = int(len(col_data) * 0.98)
            temp_data = col_data[data_len]
            temp_data = round(temp_data, 2)
            temp_data = format(temp_data, '.2f')
            tab_data_list.append(temp_data)
            
            # min
            temp_data = min(col_data)
            temp_data = round(temp_data, 2)
            temp_data = format(temp_data, '.2f')
            tab_data_list.append(temp_data)
            
            # max
            temp_data = max(col_data)
            temp_data = round(temp_data, 2)
            temp_data = format(temp_data, '.2f')
            tab_data_list.append(temp_data)
            # mean
            temp_data = (sum(col_data)) / len(col_data)
            temp_data = round(temp_data, 2)
            temp_data = format(temp_data, '.2f')
            tab_data_list.append(temp_data)
            
            # sd
            temp_data = np.std(col_data, ddof=1)
            temp_data = round(temp_data, 2)
            temp_data = format(temp_data, '.2f')
            tab_data_list.append(temp_data)
            
            return tab_data_list


    # 位置误差表格需要展示的kpi多些,单独处理
    def get_device_position_error_kpi_data(self, test_device, kpi):
        col_data = self.data_container.get(test_device).get(kpi)
        col_data = DataFrame(col_data, columns=['UTC', kpi])
        tab_data_position_list = []
        if len(col_data) == 0:
            PRINTI('%s position_error data is empty 1111' % test_device)
            self.statistics_dict[kpi][test_device] = ['NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE']
            return
        col_data = col_data[[kpi]].astype(float)
        col_data = col_data.sort_values(by=kpi)[kpi].values.tolist()
        tab_data_position_list = self._table_kpi_error_data(col_data)
        

        extra_data = self.data_container.get(test_device).get('general_data')
        # ave top5
        top5_data = DataFrame(extra_data, columns=general_data_col)[['TOP5CN']]
        top5_data = top5_data[~top5_data['TOP5CN'].isin([''])]
        if len(top5_data) == 0:
            tab_data_position_list.append('NONE')
        else:
            top5_data = top5_data['TOP5CN'].astype(float).values.tolist()
            temp_data = sum(top5_data) / len(top5_data)
            temp_data = round(temp_data, 2)
            temp_data = format(temp_data, '.2f')
            tab_data_position_list.append(temp_data)
            
        # ave sat num
        uesdSV_data = DataFrame(extra_data, columns=general_data_col)[['SACount']]
        uesdSV_data = uesdSV_data[~uesdSV_data['SACount'].isin([''])]
        if len(uesdSV_data) == 0:
            tab_data_position_list.append('NONE')
        else:
            uesdSV_data = uesdSV_data['SACount'].astype(float).values.tolist()
            temp_data = sum(uesdSV_data) / len(uesdSV_data)
            temp_data = round(temp_data, 2)
            temp_data = format(temp_data, '.2f')
            tab_data_position_list.append(temp_data)
            
        # ave hdop
#         hdop_data = DataFrame(extra_data, columns=general_data_col)[['HDOP']]
#         hdop_data = hdop_data[~hdop_data['HDOP'].isin([''])]
#         if len(hdop_data) == 0:
#             tab_data_list.append('NONE')
#         else:
#             hdop_data = hdop_data['HDOP'].astype(float).values.tolist()
#             temp_data = sum(hdop_data) / len(hdop_data)
#             temp_data = round(temp_data, 2)
#             temp_data = format(temp_data, '.2f')
#             tab_data_list.append(temp_data)

        # locate rate
        if len(extra_data) == 0:
            tab_data_position_list.append('NONE')
        else:
            num = len(extra_data)
            temp_data = (1.0 - (self.time_difference - num) / self.time_difference) * 100
            temp_data = format(temp_data, '.2f')
            tab_data_position_list.append(temp_data)
            
        # undershoot
        undershoot_data = self.data_container.get(test_device).get('undershoot_error')
        undershoot_data = DataFrame(undershoot_data, columns=['UTC', 'undershoot_error'])
        undershoot_data = np.abs(undershoot_data["undershoot_error"].astype(float)).tolist()
        overshoot_data = self.data_container.get(test_device).get('overshoot_error')
        overshoot_data = DataFrame(overshoot_data, columns=['UTC', 'overshoot_error'])
        overshoot_data = overshoot_data["overshoot_error"].astype(float).tolist()
        if len(undershoot_data) == 0:
            tab_data_position_list += ['None', 'None']
        else:
            undershoot_rate = 100 * float(len(undershoot_data)) / (len(undershoot_data) + len(overshoot_data))
            undershoot_rate = round(undershoot_rate, 2)
            tab_data_position_list.append(undershoot_rate)
            undershoot_mean = sum(undershoot_data) / len(undershoot_data)
            undershoot_mean = round(undershoot_mean, 2)
            tab_data_position_list.append(undershoot_mean)
            
        # mileage
        test_mileage = self.data_container.get(test_device).get('test_mileage')
        test_mileage = DataFrame(test_mileage, columns=['UTC', 'test_mileage'])
        test_mileage = np.sum(test_mileage["test_mileage"].astype(float))
        test_mileage = round(test_mileage, 2)
        tab_data_position_list.append(test_mileage)
        novatel_mileage = self.data_container.get('novatel').get('novatel_mileage')
        novatel_mileage = DataFrame(novatel_mileage, columns=['UTC', 'novatel_mileage'])
        novatel_mileage = np.sum(novatel_mileage["novatel_mileage"].astype(float))
        novatel_mileage = round(novatel_mileage, 2)
        tab_data_position_list.append(novatel_mileage)
        
        # ratio (%)
        if novatel_mileage == 0:
            tab_data_position_list.append('NONE')
        else:
            ratio_mileage = 100 * (test_mileage - novatel_mileage) / novatel_mileage
            ratio_mileage = round(ratio_mileage, 2)
            tab_data_position_list.append(ratio_mileage)

        self.statistics_dict[kpi][test_device] = tab_data_position_list

    @LBSDector(True)
    def get_device_table_satellite_data(self, test_device):
        try:
            device_general_data = self.data_container.get(test_device).get('general_data')
            device_general_data = DataFrame(device_general_data, columns=general_data_col)
            tab_data_list = []
            for satellite_type in ['GPSCount', 'GLNCount', 'GALCount', 'BDSCount', 'QZSCount', 'GPSL5VCount', 'GAL5VCount', 'QZL5VCount', 'SVCount']:
                device_satellite_data = device_general_data[[satellite_type]]
                device_satellite_data = device_satellite_data[~device_satellite_data[satellite_type].isin([''])]
                if len(device_satellite_data) == 0:
                    tab_data_list.append('NONE')
                else:
                    device_satellite_data = device_satellite_data[satellite_type].astype(float).values.tolist()
                    temp_data = sum(device_satellite_data) / len(device_satellite_data)
                    temp_data = round(temp_data, 2)
                    temp_data = format(temp_data, '.2f')
                    tab_data_list.append(temp_data)
            self.statistics_dict['satelliteSV'][test_device] = tab_data_list
            tab_data_list = []
            for satellite_type in ['GPSSACount', 'GLNSACount', 'GALSACount', 'BDSSACount', 'QZSACount', 'GPSL5ACount', 'GAL5ACount', 'QZL5ACount', 'SACount']:
                device_satellite_data = device_general_data[[satellite_type]]
                device_satellite_data = device_satellite_data[~device_satellite_data[satellite_type].isin([''])]
                if len(device_satellite_data) == 0:
                    tab_data_list.append('NONE')
                else:
                    device_satellite_data = device_satellite_data[satellite_type].astype(float).values.tolist()
                    temp_data = sum(device_satellite_data) / len(device_satellite_data)
                    temp_data = round(temp_data, 2)
                    temp_data = format(temp_data, '.2f')
                    tab_data_list.append(temp_data)
            self.statistics_dict['satelliteSA'][test_device] = tab_data_list
        except Exception as e:
            raise e

    def get_locate_success_rate(self, test_device, is_need_flag=True):
        device_data_list = self.data_container.get(test_device).get('general_data')
        try:
            if is_need_flag:
                data_df = DataFrame(device_data_list, columns=['UTC', 'flag', 'alt', 'speed', 'heading'])
                data_valid_df = data_df[data_df['flag'] != 0]
                return (1.0 * len(data_valid_df) / len(data_df)) * 100
            else:
                num = len((device_data_list))
                if self.time_difference is None:
                    data_df = DataFrame(device_data_list, columns=['UTC', 'flag', 'alt', 'speed', 'heading'])
                    data_df = data_df.sort_values(by='UTC')
                    start_time = data_df.ix[0, ['c']]
                    end_time = data_df.ix[-1, ['c']]
                    date_start = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                    date_end = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
                    diff = time.mktime(date_end.timetuple()) - time.mktime(date_start.timetuple())
                    if diff >= 0:
                        diff = diff + 1
                    self.time_difference = diff
                return (1.0 - (self.time_difference - num) / self.time_difference) * 100
        except:
            return -1

    @LBSDector(True)
    def check_is_analyze(self, config):
        self.resource_db_path = os.path.join(self.reportPath, 'logDB', 'lbs.db')  # 与AnalysisNMEA对应
#        print self.resource_db_path
        if not os.path.exists(self.resource_db_path):
            return False, '%s is not exists' % self.resource_db_path
        
        deviceInfo = config.get('deviceInfo')
        self.device_info = {}
        self.device_order = []
        for info in deviceInfo:
            if info["type"] != "standard":
                self.device_info.setdefault(info["tech"], info)
                self.device_order.append(info["tech"])

        self.resource_action_db = ActionDB(self.resource_db_path)
        self.data_container = {}
        self.statistics_dict = {}  # 用与保存['68', '95', 'max', 'mean', 'yield'] 数据
        self.single_report_data_container = {}
        self.single_report_statistics_dict = {}
        self.init_data_structure()  # {'xxFT_xx': {'xx_error':[], 'xx_error':[], 'xxFT_xx':[]},'xxFT_xx': {'xx_error':[], 'xx_error':[], 'xxFTxx':[]}}
        
        self.start_time = None
        self.end_time = None
        self.time_difference = None
        timeSlicing = config.get('timeSlicing')
        if timeSlicing:
            self.start_time = timeSlicing.get('starttime')
            self.end_time = timeSlicing.get('endtime')
        else:
            device_data_list = self.resource_action_db.getcolomFormDB('novatel', ['UTC'])
            data_df = DataFrame(device_data_list, columns=['UTC'])
            self.start_time = data_df.min()['UTC']
            self.end_time = data_df.max()['UTC']

        # 与郁芬姐确认过，用户填写分段时间有首有尾，并且格式正确
        self.time_difference = get_time_difference(self.start_time, self.end_time)
        return True, 'check is ok'

    def write_error_info(self, info):
        reportPath = os.path.join(self.reportPath, "report")
        filePath = os.path.join(reportPath, 'error_report.txt')
        if not os.path.exists(reportPath):
            os.makedirs(reportPath)

        PRINTI('write,error,info')
        f = open(filePath, 'a')
        f.write(info)
        f.write('\n')
        f.close
    
    @LBSDector(True)
    def export_report(self, config):
        PRINTI("analyze module check start")
        status, info = self.check_is_analyze(config)
        PRINTI("analyze module check end")

        PRINTI('export_report start')
        if not status:
            PRINTI('export_report end')
            self.write_error_info(info)
            return

        self.query_useful_data()
        self.export_error_html()
        self.export_satellite_html()
        if self.config['singleReportPath'] and self.config['is_need_single_analysis']==True:
            if not os.path.exists(self.config['singleReportPath']):
                return
            self.export_single_html()
        
        self.excelObj.save(filename_or_stream=os.path.join(self.reportPath, 'excelReport'+ str(random.randint(1000, 9999)) + '.xls'))
    
    @LBSDector(True)
    def export_single_html(self):
        total_num_list= [i for i in range(1, 101)]
        """Error single report"""
        for kpi_error in single_error_list:
            curve_name_list, error_data_tuples = self._export_curve_htm(kpi_error)
            self.htm_mgr.write_single_kpi_error_curve_js(curve_name_list, error_data_tuples, kpi_error, total_num_list,  single_error_list,
                                                  js_file_name='ErrorSingleRelatedReports.js')

            kpi_error_df, df_name_list = self._export_curve_df(kpi_error, curve_name_list, error_data_tuples)
            error_data_tuples = self._export_curve_df_sketch(kpi_error, df_name_list, kpi_error_df)
            # self.htm_mgr.write_kpi_error_curve_js(curve_name_list, error_data_tuples, kpi_error, self.start_time,
            #                                        self.end_time, error_kpi_list,
            #                                        js_file_name='ErrorStatisticsRelatedReports.js')

            self._export_error_table_html(kpi_error)
        self.htm_mgr.write_html_report(html_file_name='ErrorSingleRelatedReports.html')

    @LBSDector(True)
    def export_error_html(self):
        """Error static report"""
        for kpi_error in error_kpi_list:

            # 统计表格
            curve_name_list, error_data_tuples = self._export_curve_htm(kpi_error)

            self.htm_mgr.write_kpi_error_curve_js(curve_name_list, error_data_tuples, kpi_error, self.start_time,
                                                  self.end_time, error_kpi_list,
                                                  js_file_name='ErrorStatisticsRelatedReports.js')

            kpi_error_df, df_name_list = self._export_curve_df(kpi_error, curve_name_list, error_data_tuples)
            error_data_tuples = self._export_curve_df_sketch(kpi_error, df_name_list, kpi_error_df)
            # self.htm_mgr.write_kpi_error_curve_js(curve_name_list, error_data_tuples, kpi_error, self.start_time,
            #                                        self.end_time, error_kpi_list,
            #                                        js_file_name='ErrorStatisticsRelatedReports.js')

            self._export_error_table_html(kpi_error)
        self.htm_mgr.write_html_report()

    @LBSDector(True)
    def _export_curve_htm(self, kpi_error):
            """获取设备曲线数据"""
            curve_name_list, error_data_tuples = self.get_curve_error_data(kpi_error)
            # kpi_error_df = self._export_curve_df(kpi_error, curve_name_list, error_data_tuples)
            return curve_name_list, error_data_tuples

    @LBSDector(True)
    def _export_curve_df(self, kpi_error, curve_name_list, error_data_tuples):
        kpi_error_df_class =[]
        df_name_list = []
        kpi_error_df = ''
        
        try:
            for index in range(len(curve_name_list)):
            
                if len(error_data_tuples[0][index]) < 6:
                    continue
                df_name_list.append(curve_name_list[index])
    
                kpi_error_df = DataFrame(error_data_tuples[0][index])
                columns_2 = curve_name_list[index] + '_' + kpi_error
    
                kpi_error_df = kpi_error_df.rename(columns={0:'UTC',1:columns_2})
                kpi_error_df[columns_2] = kpi_error_df[columns_2].apply(pd.to_numeric)
                kpi_error_df_class.append(kpi_error_df)
                
                if (len(df_name_list) > 1 ) and (len(kpi_error_df_class) > 1):
                    kpi_error_df = pd.merge(kpi_error_df_class[0], kpi_error_df_class[1], on='UTC')
                    kpi_error_df_class = []
                    kpi_error_df_class.append(kpi_error_df)
        except Exception as e:
            raise e
            return '', df_name_list

        return kpi_error_df, df_name_list
    
    @LBSDector(True)
    def _export_curve_df_sketch(self, kpi_error, df_name_list, kpi_error_df):
        import warnings
        # warnings.filterwarnings('error')
        max_value = []
        min_value = []
        cdf_data_list = []
        plt_color = ['r', 'b', 'c', 'm', 'y', 'k', 'w']
        plt.figure(figsize=(20, 6), dpi=80)
        if df_name_list:
            print(df_name_list)
            for index in range(len(df_name_list)):
                if df_name_list[index] == 'novatel':
                    color ='g'
                else:
                    if index <= len(color_list):
                        color = color_list[index]
                    elif index > len(color_list):
                        color = color_list[index % len(color_list)]
                    
                
                lab_x = df_name_list[index] + '_' + kpi_error
    
                kpi_error_df[lab_x] = kpi_error_df[lab_x].apply(pd.to_numeric)
    
                res = stats.relfreq(kpi_error_df[lab_x], numbins=100)
    
    
                x = res.lowerlimit + np.linspace(0, res.binsize * res.frequency.size, res.frequency.size)
    
                y = np.cumsum(res.frequency)    #获取累计函数积分的值
                plt.plot(x, y, color=color, label=lab_x)
                plt.legend(loc='best')
                max_value.append(kpi_error_df.max()[lab_x])

        try:
            max_num = sorted(max_value)[-1]
            x = [t for t in range(int(max_num)+1)]
            if int(max_num) >=200:
                d = int(int(max_num)/40)
            elif int(max_num) > 5 and int(max_num) <= 10:
                d = 2
            elif int(max_num) >=1 and int(max_num) <= 5:
                d=1
            elif float(max_num) < 1:
                num = int(int(str(int(str(max_num).split('.')[-1]))[0]))
                lenth = int(len(str(1/max_num).split('.')[0]))
                x = [t/10**lenth for t in range(int(num)+1)]
                d = 1
            else:
                d = 5

        except Exception as e:
            print('ssss', max_value, e)
            x = [t for t in range(10)]
            d = 1
        print(4444, df_name_list)
        if df_name_list:
            plt.xticks(x[::d], x[::d])
        plt.gca().yaxis.set_major_formatter(FuncFormatter(self.to_percent))
        plt.grid(True, linestyle='--', alpha=0.2)
        plt.xlabel("Distance Error (m)")
        plt.ylabel("percentage")
        if kpi_error == 'position_error':
            plt.title('Distance Error')
        else:
            plt.title(kpi_error + '_CDF')
        report_cdf_file = '%s.png' %  (kpi_error+'_CDF')
        report_path = os.path.join(self.reportPath, 'dist', 'img', report_cdf_file)
        plt.savefig(report_path)

    def to_percent(self, temp, position):
        return '%1.0f' % (100 * temp) + '%'


    def get_curve_error_data(self, error_name):
        if len(self.device_info) == 0:
            return [], []

        data_dict = {}
        curve_name_list = []
        order_data = []

        for test_device, info in self.device_info.items():
            if info.get('type') == 'test' or info.get('type') == 'competitive':
                datas = self.data_container.get(test_device).get(error_name)
                data_dict[test_device] = self.convertData2Datatuple(datas)
        for device_name in self.device_order:
            curve_name_list.append(device_name)
            order_data.append(data_dict.get(device_name))
        error_data_tuples = self.mergeMutilDatatuple(order_data)
        return curve_name_list, error_data_tuples

    @LBSDector(True)
    def export_satellite_html(self):
        for kpi in satellite_curve_chart_list[0]:
            curve_name_list, error_data_tuples = self._export_curve_htm(kpi)
            self.htm_mgr.write_kpi_error_curve_js(curve_name_list, error_data_tuples, kpi, self.start_time,
                                                  self.end_time, satellite_curve_chart_list[0],
                                                  js_file_name='SatelliteStatisticsRelatedReports.js')


        self.__export_satellite_html('satelliteSV')


        for kpi in satellite_curve_chart_list[1]:
            curve_name_list, error_data_tuples = self._export_curve_htm(kpi)
            self.htm_mgr.write_kpi_error_curve_js(curve_name_list, error_data_tuples, kpi, self.start_time,
                                                  self.end_time, satellite_curve_chart_list[1],
                                                  js_file_name='SatelliteStatisticsRelatedReports.js')
        self.__export_satellite_html('satelliteSA')
        for kpi in satellite_curve_chart_list[2]:

            curve_name_list, error_data_tuples = self._export_curve_htm(kpi)
            self.htm_mgr.write_kpi_error_curve_js(curve_name_list, error_data_tuples, kpi, self.start_time,
                                                  self.end_time, satellite_curve_chart_list[2],
                                                  js_file_name='SatelliteStatisticsRelatedReports.js')
        self.__export_satellite_cn_top5_ave()
        self.htm_mgr.write_html_report(html_file_name='SatelliteStatisticsRelatedReports.html')
    
    @LBSDector(True)
    def __export_satellite_cn_top5_ave(self):
        kpi_name_data = ['GPS_TOP5_CN(Mean)', 'GLN_TOP5_CN(Mean)', 'GAL_TOP5_CN(Mean)', 'BDS_TOP5_CN(Mean)', 'QZ_TOP5_CN(Mean)',
                         'GPS L5_TOP5_CN(Mean)', 'GPS L1L5_TOP5_CN(Mean)', 'GAL E5a_TOP5_CN(Mean)', 'GAL E51E5a_TOP5_CN(Mean)', 'QZ L5_TOP5_CN(Mean)', 'QZ L1L5_TOP5_CN(Mean)', 'ALL_TOP5_CN(Mean)']
        table_cols = ['LBS_KPI_Final_HE']
        col_datas, show_device_list = self._get_col_data(kpi_name_data, 'satellite_in_view_top5_ave')
        self.htm_mgr.export_kpi_error_js(col_datas, show_device_list, kpi_name_data, error_name='satellite_in_view_top5_ave')
        self._export_error_table_excel(col_datas, show_device_list, kpi_name_data, error_name='satellite_in_view_top5_ave')

    @LBSDector(True)
    def __export_satellite_html(self , satelliteType):
        kpi_name_data = ['GPS(Mean)', 'GLN(Mean)', 'GAL(Mean)', 'BDS(Mean)', 'QZ(Mean)', 'GPS L5(Mean)', 'GAL E5a(Mean)', 'QZ L5(Mean)', 'Total(Mean)']
        col_datas, show_device_list = self._get_col_data(kpi_name_data, satelliteType)
        table_name = 'satellite_in_view' if satelliteType == 'satelliteSV' else 'satellite_in_used'
        self.htm_mgr.export_kpi_error_js(col_datas, show_device_list, kpi_name_data, table_name)
        self._export_error_table_excel(col_datas, show_device_list, kpi_name_data, table_name)
        # self._export_kpi_error_csv(col_datas, show_device_list, satelliteType, file_name='satellite')
        
    @LBSDector(True)    
    def _get_col_data(self, kpi_name_data, data_type):
        try:
            PRINTI(data_type)
            PRINTI(len(kpi_name_data))
            table_cols = ['LBS_KPI_Final_HE']
            show_device_list = []
            print(self.device_info)
            for device_name in self.device_order:
                info = self.device_info.get(device_name)
                if info.get('type') == 'test' or info.get('type') == 'competitive':
                    show_device_list.append(device_name)
            table_cols.extend(show_device_list)
            
            col_datas = []
            PRINTI(self.config['satelliteInfo'])
            PRINTI(self.statistics_dict[data_type])
            for colName in show_device_list:
                col_data = []
                col_data.append(colName)
                if self.config['satelliteInfo']:
                    col_data.append(self.config['satelliteInfo'][colName])
                for index in range(len(kpi_name_data)):
                    col_data.append(self.statistics_dict[data_type][colName][index])
                col_datas.append(col_data)
        except Exception as e:
            raise e
        print(100)
            
        return col_datas, show_device_list

    @LBSDector(True)
    def export_position_error_table_html(self, error_name):
        kpi_name_data = ['50%', '68%', '95%', '98%', 'MIN', 'MAX', 'MEAN', 'STD', 'AVE_TOP5_CNO',
                         'AVE_SAT_NUM', 'Position Yield', 'undershoot (%)', 'undershoot mean', "test_mileage (m)", "novatel_mileage (m)", "ratio (%)"]
        col_datas, show_device_list = self._get_col_data(kpi_name_data, error_name)
        self.htm_mgr.export_kpi_error_js(col_datas, show_device_list, kpi_name_data, error_name)
        self._export_error_table_excel(col_datas, show_device_list, kpi_name_data, error_name)
#         self._export_kpi_error_csv(col_datas, show_device_list, error_name,file_name='kpi_error')

    def _export_kpi_error_csv(self, col_datas, show_device_list, error_name, file_name='kpi_error'):

        path = self.reportPath + '\\' + file_name + '.csv'
        show_device_list.insert(0, 'kpi_name')
        csvFile = open(path, "a", newline='')  # 创建csv文件
        writer = csv.writer(csvFile)  # 创建写的对象
        # 先写入columns_name
        writer.writerow([''])
        writer.writerow([error_name])
        writer.writerow(show_device_list)  # 写入列的名称
        # 写入多行用writerows                                #写入多行
        writer.writerows(col_datas)
        csvFile.close()

        tab_id = 'tab{0}'.format(error_name)
        tab_name = error_name

    @LBSDector(True)
    def _export_error_table_html(self, error_name):

        if error_name == 'position_error':
            self.export_position_error_table_html(error_name)
            return

        kpi_name_data = ['50%', '68%', '95%', '98%', 'MIN', 'MAX', 'MEAN', 'STD', 'Position Yield']
        col_datas, show_device_list = self._get_col_data(kpi_name_data, error_name)
        
        self.htm_mgr.export_kpi_error_js(col_datas, show_device_list, kpi_name_data, error_name)
        self._export_error_table_excel(col_datas, show_device_list, kpi_name_data, error_name)
    
    def _export_error_table_excel(self, col_datas, show_device_list, kpi_name_data, error_name):
        """数据写入表格"""
        
        sheetObj = self.excelObj.add_sheet(error_name, cell_overwrite_ok=True)
        
        for col in range(len(kpi_name_data)):
            sheetObj.write(0, col, kpi_name_data[col])
        
        for i in range(len(col_datas)):
            for col in range(len(col_datas[i])):
                sheetObj.write(i+1, col ,col_datas[i][col])
        
            

    def convertData2Datatuple(self, data):
        try:
            all_array = np.mat(data)
            all_array = all_array.astype(str)
            value_array = all_array[:, 1]  # 第一列拿出来
            value_array = np.mat(value_array, np.float32)  # 格式转换
            return ([all_array.tolist()], value_array.min(), value_array.max())
        except:
            return ([['-1', '-1']], -1, -1)

    def convertData2Formate(self, data):
        if not data:
            return data
        all_array = np.mat(data)
        all_array = all_array.astype(str)
        return all_array.tolist()

    def mergeMutilDatatuple(self, datatuple_list):
        '''
        @ datatuple_list 原始数据集合
        @ return 有效数据集合,min,max
        '''
        try:
            data_list = []
            min_list = []
            max_list = []
            for i in range(len(datatuple_list)):
                data_list.append(datatuple_list[i][0][0])
                min_list.append(datatuple_list[i][1])
                max_list.append(datatuple_list[i][2])
            return (data_list, min(min_list), max(max_list))
        except:
            return ([], -1, -1)


def get_sim_test_name(ft_name, dll_version):
    sim_name = ft_name + dll_version
    return sim_name
 
 
def get_time_difference(start_time, end_time):
    try:
        date_start = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        date_end = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        diff = time.mktime(date_end.timetuple()) - time.mktime(date_start.timetuple())
        if diff >= 0:
            diff = diff + 1
        return diff
    except:
        return None
 
 
def convert_list_2str(data_list):
    ret = []
    for data in data_list:
        ret.append(str(data))
    return ret
 
 
# 将二维数组里面uncode转化成str
def convert_list_mat_2str(data):
    if not data:
        return data
    all_array = np.mat(data)
    all_array = all_array.astype(str)
    return all_array.tolist()
 
 
def get_competitive_tests(device_list):
    competitive_tests = []
    for device, info in device_list.items():
        if info.get('type') == 'competitive':
            competitive_tests.append(device)
    return competitive_tests
 
 
def get_all_devices(device_list):
    all_device_list = {}
    for device, info in device_list.items():
        if info.get('type') == 'test':
            all_device_list[device] = {}
            all_device_list[device]['type'] = info.get('type')
        elif info.get('type') == 'competitive':
            all_device_list[device] = {}
            all_device_list[device]['type'] = info.get('type')
    return all_device_list


def analyze_main(reportPath, config):
    try:
        analyze_moudle = AnalyzeModule(reportPath, config)
        analyze_moudle.export_report(config)
        kpi_name_data = ['CEP68', 'CEP95', 'MAX', 'MEAN', 'AVE_TOP5_CNO', 'AVE_SAT_NUM', 'AVE_HDOP',
                      'PositionYield', 'undershoot', 'undershootMean', "test_mileage", "novatel_mileage", "ratio"]
        for key, value in analyze_moudle.statistics_dict['position_error'].items():
            if key.lower().find('huawei') != -1:
                return DT_SUC, dict(zip(kpi_name_data, value))
        # return DT_FAIL, ''
    except Exception as e:
        PRINTE(e)
        return DT_FAIL, ''

if __name__ == '__main__':
    from aw.utils.nmeanalysis.config import config
    reportPath = r"D:\Report33"
    

