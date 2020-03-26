# coding:utf-8
import os, sys
import time, subprocess
import math
import datetime
from pandas import DataFrame
from math import radians
import pandas as pd
import numpy as np
import re
from aw.utils.nmeanalysis.ActionDB import ActionDB
from aw.utils.nmeanalysis.AresInput import PRINTI
from aw.utils.nmeanalysis.AresInput import PRINTE
from aw.utils.nmeanalysis.AresInput import LBSDector
from aw.utils.nmeanalysis.SatelliteInfoStructure import ViewSatelliteInfoStructure


nmea_head_list = ["$BDGGA", "$GPGGA", "$GNGGA",
     "$BDGSA", "$GPGSA", "$GNGSA",
     "$BDGSV", "$GPGSV", "$GNGSV", "$GLGSV", '$GAGSV'
     "$BDRMC", "$GPRMC", "$GNRMC",
     "$BDZDA", "$GPZDA", "$GNZDA",
     "PMTK", '$GNGST',
     "sim", "$GPTXT", "$BDTXT", "$GNTXT",
     "Version", "AGPS", "[20", "fix", "eph",
     "system", "ephemeris", "aid", "This"]
def ErrorInfo(msg):
    PRINTI("ERROR[{}]".format(msg))

class GetResource2DB(ActionDB):
    config = {}
    sensor_vendor = {}

    def __init__(self, DBPath, sceneConfig):
        super(GetResource2DB, self).__init__(DBPath)
        self.sceneconf = sceneConfig
        

    def getHigeoFTResource2DB(self, logPath, diviceName=None):
        if diviceName == None and os.path.isdir(logPath):
            diviceName = os.path.split(os.path.splitext(logPath)[0])[1]
        status, info = self.__writeFT2Table(logPath, diviceName)
        if not status:
            return status, info

        self.__writeFTSection2Table(diviceName, "50")

        self.__writeFTSection2Table(diviceName, "60")

        self.__writeFTSection2Table(diviceName, "62")

        self.__writeFTSection2Table(diviceName, "80")

        self.__writeFTSection2Table(diviceName, "90")

        self.__writeFTSection2Table(diviceName, "91")

        self.__writeFTSection2Table(diviceName, "92")

        self.__writeFTSection2Table(diviceName, "93")

        self.__writeFTSection2Table(diviceName, "94")

        self.__writeFTSection2Table(diviceName, "95")

        self.__writHigeoKPIError(diviceName, "50")

        self.__writHigeoKPIError(diviceName, "90")

        self.__writHigeoKPIError(diviceName, "92")

        return True, ''

    def __writeFTSection2Table(self, deviceName, Type):
        tablename = deviceName + "_" + Type
        starttime = time.time()
        list_type = self.fetchone(deviceName, "type", Type)
        if list_type == []:
            PRINTE("can not find [{}]".format(Type))
            return
        self.create_HIGEO_Track_TABLE(tablename)
        for line in list_type:
            utc = datetime.datetime.utcfromtimestamp(int(int(line[2]) / 1000)).strftime("%Y-%m-%d %H:%M:%S")
            elementlist = list(line)
            List = elementlist[0:2] + [utc] + elementlist[3:]
            self.add_HIGEO_Track_data(tablename, List)
        self.commit()
        writeend = time.time() - starttime
        PRINTI("write tabel[{}] finsh, used time [{}].".format(tablename, writeend))

    def getHigeoSIMResource2DB(self, resourceDB, logPath, deviceName):
        listDir = os.listdir(logPath)
        HigeoSessionLog = []
        for filename in listDir:
            if filename.find("GNSS_HIGEO_") != -1 and filename.endswith(".t"):
                HigeoSessionLog.append(filename)
            else:
                if filename != "EXCEPTION.t":
                    PRINTE(filename)
        if HigeoSessionLog == []:
            return -1, "no session"
        HigeoSessionLog = sorted(HigeoSessionLog, key=lambda d: int(d.split('_')[-1].split('.')[0]))
        HigeoSessionLog = sorted(HigeoSessionLog, key=lambda d: d[0:27])
        # check session

        if HigeoSessionLog != []:
            session = HigeoSessionLog[0][0:27]
            for element in HigeoSessionLog:
                if session not in element:
                    return -1, "more than one session"
        self.__writeSIM2Table(logPath, HigeoSessionLog, deviceName)

        if not self.__writHigeoKPIError(deviceName, "50", resourceDB):
            return 0, "no novatel's track."

        self.__writHigeoKPIError(deviceName, "90", resourceDB)

        self.__writHigeoKPIError(deviceName, "92", resourceDB)
        return 0, ""

    def __writeSIM2Table(self, logPath, HigeoSessionList, deviceName):
        List_50 = []
        List_62 = []
        List_80 = []
        List_90 = []
        List_91 = []
        List_92 = []
        List_93 = []
        List_94 = []
        List_95 = []
        for fileName in HigeoSessionList:
            filePath = os.path.join(logPath, fileName)
            fd = open(filePath, "r")
            File = fd.read()
            for line in File.splitlines():
                if " $PVTINFO,50," in line:
                    line = line.replace(" $PVTINFO", "")
                    line = line.split(",")
                    utc = datetime.datetime.utcfromtimestamp(int(int(line[2]) / 1000)).strftime("%Y-%m-%d %H:%M:%S")
                    List_50.append(line[0:2] + [utc] + line[3:])
                elif " $QTFWIFINLP,62," in line:
                    line = line.replace(" $QTFWIFINLP", "")
                    line = line.split(",")
                    utc = datetime.datetime.utcfromtimestamp(int(int(line[2]) / 1000)).strftime("%Y-%m-%d %H:%M:%S")
                    List_62.append(line[0:2] + [utc] + line[3:])
                elif " $CONTEXTRES,80," in line:
                    line = line.replace(" $CONTEXTRES", "")
                    line = line.split(",")
                    utc = datetime.datetime.utcfromtimestamp(int(int(line[2]) / 1000)).strftime("%Y-%m-%d %H:%M:%S")
                    List_80.append(line[0:2] + [utc] + line[3:])
                elif " $FUSIONRES,90," in line:
                    line = line.replace(" $FUSIONRES", "")
                    line = line.split(",")
                    utc = datetime.datetime.utcfromtimestamp(int(int(line[2]) / 1000)).strftime("%Y-%m-%d %H:%M:%S")
                    List_90.append(line[0:2] + [utc] + line[3:])
                elif " $FUSIONRES,91," in line:
                    line = line.replace(" $FUSIONRES", "")
                    line = line.split(",")
                    utc = datetime.datetime.utcfromtimestamp(int(int(line[2]) / 1000)).strftime("%Y-%m-%d %H:%M:%S")
                    List_91.append(line[0:2] + [utc] + line[3:])
                elif " $FUSIONRES,92," in line:
                    line = line.replace(" $FUSIONRES", "")
                    line = line.split(",")
                    utc = datetime.datetime.utcfromtimestamp(int(int(line[2]) / 1000)).strftime("%Y-%m-%d %H:%M:%S")
                    List_92.append(line[0:2] + [utc] + line[3:])
                elif " $FUSIONRES,93," in line:
                    line = line.replace(" $FUSIONRES", "")
                    line = line.split(",")
                    utc = datetime.datetime.utcfromtimestamp(int(int(line[2]) / 1000)).strftime("%Y-%m-%d %H:%M:%S")
                    List_93.append(line[0:2] + [utc] + line[3:])
                elif " $FUSIONRES,94," in line:
                    line = line.replace(" $FUSIONRES", "")
                    line = line.split(",")
                    utc = datetime.datetime.utcfromtimestamp(int(int(line[2]) / 1000)).strftime("%Y-%m-%d %H:%M:%S")
                    List_94.append(line[0:2] + [utc] + line[3:])
                elif " $QTFFUSION,95," in line:
                    line = line.replace(" $QTFFUSION", "")
                    line = line.split(",")
                    utc = datetime.datetime.utcfromtimestamp(int(int(line[2]) / 1000)).strftime("%Y-%m-%d %H:%M:%S")
                    List_95.append(line[0:2] + [utc] + line[3:])
                else:
                    pass
            fd.close()
        if List_50 != []:
            self.__writeSIMSection2Table(deviceName, "50", List_50)
        if List_62 != []:
            self.__writeSIMSection2Table(deviceName, "62", List_62)
        if List_80 != []:
            self.__writeSIMSection2Table(deviceName, "80", List_80)
        if List_90 != []:
            self.__writeSIMSection2Table(deviceName, "90", List_90)
        if List_91 != []:
            self.__writeSIMSection2Table(deviceName, "91", List_91)
        if List_92 != []:
            self.__writeSIMSection2Table(deviceName, "92", List_92)
        if List_93 != []:
            self.__writeSIMSection2Table(deviceName, "93", List_93)
        if List_94 != []:
            self.__writeSIMSection2Table(deviceName, "94", List_94)
        if List_95 != []:
            self.__writeSIMSection2Table(deviceName, "95", List_95)

    def __writeSIMSection2Table(self, deviceName, Type, data):
        tablename = deviceName + "_" + Type
        self.create_HIGEO_Track_TABLE(tablename)
        for element in data:
            self.add_HIGEO_Track_data(tablename, element)
        self.commit()

    @LBSDector(True)
    def getNovatelKmz2DB(self, fname, timeZone=-18):
        '''
        @param fname: kmz文件全路径
        @param timezone: 时区偏差或者闰秒偏差 
        '''
        if not fname.lower().endswith(".kmz") or not os.path.isfile(fname):
            PRINTE("NO kmz file[{}]".format(fname))
            return
        winRarExePath = self.__getAresAG_RunBat()
        if winRarExePath == None:
            PRINTE("NO WinRAR project.")
            return "NO WinRAR project."

        dirPath, _ = os.path.split(fname)
        cmd = '"' + winRarExePath + '" x -Y -ibck "' + fname + '"' + ' ' + '"' + dirPath + '"'
        #        PRINTI("the compress cmd is [{}]".format(cmd))
        returnCode = subprocess.call(cmd)
        if returnCode in [0, 1]:
            for fl in os.listdir(dirPath):
                if '.kml' in fl.lower():
                    kmlPath = os.path.join(dirPath, fl)
                    input_file = open(kmlPath, 'r', encoding='utf8')

                    TrackList = []
                    currline = input_file.readline()
                    while currline != "":
                        if currline.find("<Placemark>") != -1:
                            currline = input_file.readline()
                            UTC = None
                            lon = None
                            lat = None
                            alt = None
                            speed = None
                            heading = None
                            ACC = None
                            usedSV = None
                            Top5CN = None
                            HDOP = None
                            VDOP = None
                            PDOP = None
                            GPSsv = None
                            GLNsv = None
                            GALsv = None
                            BDSsv = None
                            SVCount = None
                            GPSsa = None
                            GLNsa = None
                            GALsa = None
                            BDSsa = None
                            QZsa = None
                            SACount = None

                            while currline.find("</Placemark>") == -1:
                                if currline.find(">Time:<") != -1:
                                    UTC = self.__getNovatelPointTime(currline, timeZone)
                                elif currline.find("<Point>") != -1:
                                    currline = input_file.readline()
                                    lon, lat, alt = self.__getNovatelPoint(currline)
                                elif currline.find("nSats") != -1:
                                    usedSV = self.__getNovatelSVCount(currline)
                                elif currline.find("Vel") != -1:
                                    speed = self.__getNovatelSpeed(currline)
                                elif currline.find("Att") != -1:
                                    heading = self.__getNovatelHeading(currline)
                                elif currline.find("PosMiscl:") != -1:
                                    ACC = self.__getNovatelACCValue(currline)
                                elif currline.find("DOPs(P,H,V)") != -1:
                                    PDOP, HDOP, VDOP = self.__getNovatelDOP(currline)
                                else:
                                    pass
                                currline = input_file.readline()
                                
                                if speed == None:
                                    speed = -10.0
                                if heading == None:
                                    heading = -10.0
                                if usedSV == None:
                                    usedSV = -10.0
                                if ACC == None:
                                    ACC = -10.0

                            if UTC and lon != None and lat != None and speed != None and heading != None and usedSV != None:
                                PointList = [UTC, lon, lat, alt, speed, heading, usedSV, Top5CN, ACC, HDOP, VDOP, PDOP,
                                             GPSsv, GLNsv, GALsv, BDSsv, SVCount, GPSsa, GLNsa, GALsa, BDSsa, QZsa,
                                             SACount, GPSsa, GLNsa, GALsa, BDSsa, QZsa, "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
                                #                                print(PointList)
                                TrackList.append(PointList)

                        # -----end of if-----
                        currline = input_file.readline()

                        # -----end of while-----
                    input_file.close()
                    #                    os.remove(kmlPath)
                    if TrackList:

                        self.create_NMEA_Info_Table("novatel")
                        for element in TrackList:
                            self.add_NMEA_Info_data("novatel", element)
                        self.commit()
                    break
        self.__writeNMEAMileage2DB('novatel')

    def _readNMEAlog(self, line):
        try:
            line = str(line, encoding='utf-8')
            is_valid_nmea_line, nmea_line = check_is_valid_nmea_line(line)
            nmea_line += '\r\n'
        except:
            nmea_line = self._remove_binary(line)
            return nmea_line
        if not is_valid_nmea_line:
            nmea_line = self._remove_binary(line)
        return nmea_line


    def _remove_binary(self, line):
        f_log = str(line)  # read file by line
        nema = 'd'
        ss = ''
        ss = ss + f_log
        while 1:
            for i in range(len(nmea_head_list)):
                index = ss.find(nmea_head_list[i])  # find index key in ss

                if index >= 0:
                    nmea_head = nmea_head_list[i]
                    break
            if index < 0:
                return None
            nmea_end = ss.find('\\n')  # line end symbol
            if nmea_end < 0:  # if the line not end
                ss = ss[index:]
                break
            if nmea_end < index:
                for i in range(100):
                    ss = ss[nmea_end + 1:]
                    nmea_end = ss.find('\\n')
                    index = ss.find(nmea_head)
                    if nmea_end > index:
                        break

            nema = ss[index:nmea_end + 1]  # save log form index to end

            if len(nema) > 5:
                nmea_end2 = nema.find('\\')
                if nmea_end2 > 0:
                    return nema[:nmea_end2] + "\r\n"
            return None


    @LBSDector(True)
    def getNMEA2DB(self, logPath, deviceName, timeZone=None):
        '''
        @param fname: kmz文件全路径
        @param deviceName: 设备名称，保存到数据库是以该名称保存 
        @param timezone: 时区偏差或者闰秒偏差 
        @param date: log采集日期，格式[%Y-%m-%d],例如：“2017-08-08”
        '''
        if not os.path.isfile(logPath):
            ErrorInfo("the NMEA file path[{}] is wrong".format(logPath))
            return
        with open(logPath, "rb") as rd:
            PositionList = []
            DATE = ""  # rmc time + gga Time
            Time = ""  # gga time
            lastTime = ""
            first = ""
            vodp_list = []

            UTC = ""
            lon = ""  # gga
            lat = ""  # gga
            alt = ""  # gga
            speed = ""  # rmc
            heading = ""  # rmc
            ACC = ""
            usedSV = ""  # gga
            Top5CN = []  # todo 应该用gsa里面的usedSV
            HDOP = ""  # gsa 水平精度因子
            VDOP = ""  # gsa 垂直精度因子
            PDOP = ""  # gsa
            GPSNumSet = set()
            GLNNumSet = set()
            GALNumSet = set()
            BDSNumSet = set()
            QZNumSet = set()
            # hu
            GPSL5NumSet = set()
            QZL5NumSet = set()
            GALE5ANumSet = set()

            gps_view_satellite_info = ViewSatelliteInfoStructure()
            gln_view_satellite_info = ViewSatelliteInfoStructure()
            gal_view_satellite_info = ViewSatelliteInfoStructure()
            bds_view_satellite_info = ViewSatelliteInfoStructure()
            qz_view_satellite_info = ViewSatelliteInfoStructure()
            # hu
            gpsl5_view_satellite_info = ViewSatelliteInfoStructure()
            qzl5_view_satellite_info = ViewSatelliteInfoStructure()
            gale5a_view_satellite_info = ViewSatelliteInfoStructure()

            # 用于计算新的gngsa协议
            GNGPSList = []
            GLNList = []
            GALList = []
            BDList = []
            # 如果是1，表示gps，里边的number都是gps卫星号
            # 2是glonass，3是galileo， 5是BDS
            fixed = False
            for line in rd:
                line = self._readNMEAlog(line)
                if line is None:
                    continue
                is_valid_nmea_line , nmea_line = check_is_valid_nmea_line(line)
                if not is_valid_nmea_line:
                    continue
                line = nmea_line

                if ("GGA" in line) and line.count(",") == 14:
                    vodp_list = []
                    
                    if first == "GGA":
                        if lastTime != Time:
                            if fixed:
                                DATE_ALL = "20" + DATE[4:] + "-" + DATE[2:4] + "-" + DATE[:2] + " " + Time
                                UTC = self.__covertlocaltime2utctime(DATE_ALL, timeZone)
                                Top5CNAvg = self.__getTop5Cn0Avg(Top5CN)
                                SVCount = gps_view_satellite_info.get_satellite_count() + gln_view_satellite_info.get_satellite_count() \
                                          + gal_view_satellite_info.get_satellite_count() + bds_view_satellite_info.get_satellite_count() + qz_view_satellite_info.get_satellite_count()
                                gps_top5_cno_satellite_list, gps_top5_ave_value = gps_view_satellite_info.get_top5_cno_satellite_info()
                                gln_top5_cno_satellite_list, gln_top5_ave_value = gln_view_satellite_info.get_top5_cno_satellite_info()
                                gal_top5_cno_satellite_list, gal_top5_ave_value = gal_view_satellite_info.get_top5_cno_satellite_info()
                                bds_top5_cno_satellite_list, bds_top5_ave_value = bds_view_satellite_info.get_top5_cno_satellite_info()
                                qz_top5_cno_satellite_list, qz_top5_ave_value = qz_view_satellite_info.get_top5_cno_satellite_info()
                                # hu 计算l5的cno数据
                                gpsl5_top5_cno_satellite_list, gpsl5_top5_ave_value = gpsl5_view_satellite_info.get_top5_cno_satellite_info()
                                qzl5_top5_cno_satellite_list, qzl5_top5_ave_value = qzl5_view_satellite_info.get_top5_cno_satellite_info()
                                gale5a_top5_cno_satellite_list, gale5a_top5_ave_value = gale5a_view_satellite_info.get_top5_cno_satellite_info()
                                # l1l5 top5 cn0
                                gpsl1l5_top5_cno_satellite_list, gpsl1l5_top5_ave_value = self.__get_cno_l1l5_satellite_info(gps_view_satellite_info, gpsl5_view_satellite_info)
                                qzl1l5_top5_cno_satellite_list, qzl1l5_top5_ave_value = self.__get_cno_l1l5_satellite_info(qz_view_satellite_info, qzl5_view_satellite_info)
                                gale51e5a_top5_cno_satellite_list, gale51e5a_top5_ave_value = self.__get_cno_l1l5_satellite_info(gal_view_satellite_info, gale5a_view_satellite_info)
                                SACount = len(GPSNumSet) + len(GNGPSList) + len(GLNNumSet) + len(GLNList) + len(GALNumSet) + len(GALList) + len(BDSNumSet) + len(BDList) + len(
                                    QZNumSet)
                                PositionList.append(
                                    [UTC, lon, lat, alt, speed, heading, usedSV, Top5CNAvg, ACC, HDOP, VDOP, PDOP,
                                     gps_view_satellite_info.get_satellite_count(), gln_view_satellite_info.get_satellite_count(),
                                     gal_view_satellite_info.get_satellite_count(), bds_view_satellite_info.get_satellite_count(), qz_view_satellite_info.get_satellite_count(), SVCount,
                                     gpsl5_view_satellite_info.get_satellite_count(), qzl5_view_satellite_info.get_satellite_count(), gale5a_view_satellite_info.get_satellite_count(),
                                     len(GPSNumSet) + len(GNGPSList), len(GLNNumSet) + len(GLNList),
                                     len(GALNumSet) + len(GALList), len(BDSNumSet) + len(BDList), len(QZNumSet), SACount,
                                     len(GPSL5NumSet), len(QZL5NumSet), len(GALE5ANumSet),
                                     str(GPSNumSet) + str(GNGPSList), str(GLNNumSet) + str(GLNList), str(GALNumSet) + str(GALList), str(BDSNumSet) + str(BDList), str(QZNumSet),
                                     str(GPSL5NumSet), str(QZL5NumSet), str(GALE5ANumSet),
                                     str(gps_view_satellite_info.get_satelliteID_list()), str(gln_view_satellite_info.get_satelliteID_list()), str(gal_view_satellite_info.get_satelliteID_list()), str(bds_view_satellite_info.get_satelliteID_list()), str(qz_view_satellite_info.get_satelliteID_list()),
                                     str(gpsl5_view_satellite_info.get_satelliteID_list()), str(qzl5_view_satellite_info.get_satelliteID_list()), str(gale5a_view_satellite_info.get_satelliteID_list()),
                                     str(gps_top5_cno_satellite_list), str(gln_top5_cno_satellite_list), str(gal_top5_cno_satellite_list), str(bds_top5_cno_satellite_list), str(qz_top5_cno_satellite_list), str(gpsl5_top5_cno_satellite_list),
                                     str(gpsl1l5_top5_cno_satellite_list), str(qzl5_top5_cno_satellite_list), str(qzl1l5_top5_cno_satellite_list), str(gale5a_top5_cno_satellite_list), str(gale51e5a_top5_cno_satellite_list),
                                     gps_top5_ave_value, gln_top5_ave_value, gal_top5_ave_value, bds_top5_ave_value, qz_top5_ave_value,
                                     gpsl5_top5_ave_value, gpsl1l5_top5_ave_value, qzl5_top5_ave_value, qzl1l5_top5_ave_value, gale5a_top5_ave_value, gale51e5a_top5_ave_value])
                                lastTime = Time
                            lon = ""
                            lat = ""
                            alt = ""
                            speed = ""
                            heading = ""
                            ACC = ""
                            usedSV = ""
                            Top5CN = []
                            HDOP = ""
                            VDOP = ""
                            PDOP = ""
                            gps_view_satellite_info.clear()
                            gln_view_satellite_info.clear()
                            gal_view_satellite_info.clear()
                            bds_view_satellite_info.clear()
                            qz_view_satellite_info.clear()
                            # hu
                            gpsl5_view_satellite_info.clear()
                            qzl5_view_satellite_info.clear()
                            gale5a_view_satellite_info.clear()

                            # GPSVNumSet = set()
                            # GLNVNumSet = set()
                            # GALVNumSet = set()
                            # BDSVNumSet = set()
                            # QZVNumSet = set()
                            GPSNumSet = set()
                            GLNNumSet = set()
                            GALNumSet = set()
                            BDSNumSet = set()
                            QZNumSet = set()
                            # hu
                            GPSL5NumSet = set()
                            QZL5NumSet = set()
                            GALE5ANumSet = set()
                            GNGPSList = []
                            GLNList = []
                            GALList = []
                            BDList = []
                    posList = line.split(",")
                    if posList[1]:
                        Time = posList[1][:2] + ":" + posList[1][2:4] + ":" + posList[1][4:6]

                    if posList[6] != "0" and posList[6] != "":
                        fixed = True
                    else:
                        fixed = False
                        continue
                    if first == "":
                        first = "GGA"
                    if posList[3] == "N":
                        latNorth = 1
                    else:
                        latNorth = -1
                    if posList[5] == "E":
                        lonEast = 1
                    else:
                        lonEast = -1
                    lat = str(latNorth * self.__convertdmmmmmm2d(posList[2]))
                    lon = str(lonEast * self.__convertdmmmmmm2d(posList[4]))
                    if posList[9] and posList[11]:
                        alt = float(posList[9]) + float(posList[11])
                    else:
                        alt = posList[9]
                    usedSV = posList[7]
                elif ("RMC" in line) and (line.count(",") == 12 or line.count(",") == 13 or line.count(",") == 11):
                    if first == "RMC":
                        if lastTime != Time:
                            if fixed:
                                DATE_ALL = "20" + DATE[4:] + "-" + DATE[2:4] + "-" + DATE[:2] + " " + Time
                                UTC = self.__covertlocaltime2utctime(DATE_ALL, timeZone)
                                Top5CNAvg = self.__getTop5Cn0Avg(Top5CN)
                                SVCount = gps_view_satellite_info.get_satellite_count() + gln_view_satellite_info.get_satellite_count() \
                                          + gal_view_satellite_info.get_satellite_count() + bds_view_satellite_info.get_satellite_count() + qz_view_satellite_info.get_satellite_count()
                                gps_top5_cno_satellite_list, gps_top5_ave_value = gps_view_satellite_info.get_top5_cno_satellite_info()
                                gln_top5_cno_satellite_list, gln_top5_ave_value = gln_view_satellite_info.get_top5_cno_satellite_info()
                                gal_top5_cno_satellite_list, gal_top5_ave_value = gal_view_satellite_info.get_top5_cno_satellite_info()
                                bds_top5_cno_satellite_list, bds_top5_ave_value = bds_view_satellite_info.get_top5_cno_satellite_info()
                                qz_top5_cno_satellite_list, qz_top5_ave_value = qz_view_satellite_info.get_top5_cno_satellite_info()
                                # hu 计算l5的cno数据
                                gpsl5_top5_cno_satellite_list, gpsl5_top5_ave_value = gpsl5_view_satellite_info.get_top5_cno_satellite_info()
                                qzl5_top5_cno_satellite_list, qzl5_top5_ave_value = qzl5_view_satellite_info.get_top5_cno_satellite_info()
                                gale5a_top5_cno_satellite_list, gale5a_top5_ave_value = gale5a_view_satellite_info.get_top5_cno_satellite_info()
                                # l1l5 top5 cn0
                                gpsl1l5_top5_cno_satellite_list, gpsl1l5_top5_ave_value = self.__get_cno_l1l5_satellite_info(gps_view_satellite_info, gpsl5_view_satellite_info)
                                qzl1l5_top5_cno_satellite_list, qzl1l5_top5_ave_value = self.__get_cno_l1l5_satellite_info(qz_view_satellite_info, qzl5_view_satellite_info)
                                gale51e5a_top5_cno_satellite_list, gale51e5a_top5_ave_value = self.__get_cno_l1l5_satellite_info(gal_view_satellite_info, gale5a_view_satellite_info)
                                SACount = len(GPSNumSet) + len(GNGPSList) + len(GLNNumSet) + len(GLNList) + len(GALNumSet) + len(GALList) + len(BDSNumSet) + len(BDList) + len(
                                    QZNumSet)
                                PositionList.append(
                                    [UTC, lon, lat, alt, speed, heading, usedSV, Top5CNAvg, ACC, HDOP, VDOP, PDOP,
                                     gps_view_satellite_info.get_satellite_count(), gln_view_satellite_info.get_satellite_count(),
                                     gal_view_satellite_info.get_satellite_count(), bds_view_satellite_info.get_satellite_count(), qz_view_satellite_info.get_satellite_count(), SVCount,
                                     gpsl5_view_satellite_info.get_satellite_count(), qzl5_view_satellite_info.get_satellite_count(), gale5a_view_satellite_info.get_satellite_count(),
                                     len(GPSNumSet) + len(GNGPSList), len(GLNNumSet) + len(GLNList),
                                     len(GALNumSet) + len(GALList), len(BDSNumSet) + len(BDList), len(QZNumSet), SACount,
                                     len(GPSL5NumSet), len(QZL5NumSet), len(GALE5ANumSet),
                                     str(GPSNumSet) + str(GNGPSList), str(GLNNumSet) + str(GLNList), str(GALNumSet) + str(GALList), str(BDSNumSet) + str(BDList), str(QZNumSet),
                                     str(GPSL5NumSet), str(QZL5NumSet), str(GALE5ANumSet),
                                     str(gps_view_satellite_info.get_satelliteID_list()), str(gln_view_satellite_info.get_satelliteID_list()), str(gal_view_satellite_info.get_satelliteID_list()), str(bds_view_satellite_info.get_satelliteID_list()), str(qz_view_satellite_info.get_satelliteID_list()),
                                     str(gpsl5_view_satellite_info.get_satelliteID_list()), str(qzl5_view_satellite_info.get_satelliteID_list()), str(gale5a_view_satellite_info.get_satelliteID_list()),
                                     str(gps_top5_cno_satellite_list), str(gln_top5_cno_satellite_list), str(gal_top5_cno_satellite_list), str(bds_top5_cno_satellite_list), str(qz_top5_cno_satellite_list),
                                     str(gpsl5_top5_cno_satellite_list), str(gpsl1l5_top5_cno_satellite_list), str(qzl5_top5_cno_satellite_list), str(qzl1l5_top5_cno_satellite_list), str(gale5a_top5_cno_satellite_list), str(gale51e5a_top5_cno_satellite_list),
                                     gps_top5_ave_value, gln_top5_ave_value, gal_top5_ave_value, bds_top5_ave_value, qz_top5_ave_value,
                                     gpsl5_top5_ave_value, gpsl1l5_top5_ave_value, qzl5_top5_ave_value, qzl1l5_top5_ave_value, gale5a_top5_ave_value, gale51e5a_top5_ave_value])
                                lastTime = Time
                            lon = ""
                            lat = ""
                            alt = ""
                            speed = ""
                            heading = ""
                            ACC = ""
                            usedSV = ""
                            Top5CN = []
                            HDOP = ""
                            VDOP = ""
                            PDOP = ""
                            gps_view_satellite_info.clear()
                            gln_view_satellite_info.clear()
                            gal_view_satellite_info.clear()
                            bds_view_satellite_info.clear()
                            qz_view_satellite_info.clear()
                            # hu
                            gpsl5_view_satellite_info.clear()
                            qzl5_view_satellite_info.clear()
                            gale5a_view_satellite_info.clear()
                            # GPSVNumSet = set()
                            # GLNVNumSet = set()
                            # GALVNumSet = set()
                            # BDSVNumSet = set()
                            # QZVNumSet = set()
                            GPSNumSet = set()
                            GLNNumSet = set()
                            GALNumSet = set()
                            BDSNumSet = set()
                            QZNumSet = set()
                            # hu
                            GPSL5NumSet = set()
                            QZL5NumSet = set()
                            GALE5ANumSet = set()

                            GNGPSList = []
                            GLNList = []
                            GALList = []
                            BDList = []
                    rmclist = line.split(",")
                    if rmclist[1]:
                        Time = rmclist[1][:2] + ":" + rmclist[1][2:4] + ":" + rmclist[1][4:6]
                    if rmclist[2] == "V":
                        speed = "-10"
                        heading = "-10"
                        continue
                    else:
                        if rmclist[7]:
                            speed = str(float(rmclist[7]) * 0.5144444)
                        else:
                            speed = "-10"
                        heading = rmclist[8]
                        if not heading:
                            heading = "-10"
                        DATE = rmclist[9]
                    if first == "":
                        first = "RMC"
                elif ("GSA" in line):
                    pattern = re.compile("G.GSA")
                    if pattern.search(line) or "BDGSA" in line or "QZGSA" in line:
                        self.__calculateUsedSatellite(GPSNumSet, GLNNumSet, GALNumSet, BDSNumSet, QZNumSet, line, GLNList, GALList, BDList, GPSL5NumSet, QZL5NumSet, GALE5ANumSet, vodp_list)
                        gsaList = line.split("*")[0].split(",")[-3:]
                        HDOP = gsaList[1]
                        VDOP = gsaList[2]
                        PDOP = gsaList[0]
                elif ("GSV" in line):
                    pattern = re.compile("G.GSV")
                    if pattern.search(line) or "BDGSV" in line or "QZGSV" in line or "PQGSV" in line:
                        Top5CN += self.__getCN0FromGSV(line)
                        self.__calculateViewSatellite(gps_view_satellite_info, gln_view_satellite_info, gal_view_satellite_info, bds_view_satellite_info, qz_view_satellite_info,
                                                      gpsl5_view_satellite_info, qzl5_view_satellite_info, gale5a_view_satellite_info, line, vodp_list, GPSNumSet,  GALNumSet,  QZNumSet, GPSL5NumSet, QZL5NumSet, GALE5ANumSet, GALList)
            rd.close()
        if PositionList:
            self.create_NMEA_Info_Table(deviceName)
            for element in PositionList:
                self.add_NMEA_Info_data(deviceName, element)
            self.commit()
        self.__writeNMEAMileage2DB(deviceName)

    def __getGNSSNumber(self, line):
        return int(line.split(",")[3])

    def __getCN0FromGSV(self, line):
        cnList = []
        gsvList = line.split("*")[0].split(",")[4:]
        i = 0
        for element in gsvList:
            i += 1
            if i % 4 == 0 and element != "":
                cnList.append(int(float(element)))
        return cnList

    def __calculateViewSatellite(self, gps_view_satellite_info, gln_view_satellite_info, gal_view_satellite_info, bds_view_satellite_info, qz_view_satellite_info,
                                 gpsl5_view_satellite_info, qzl5_view_satellite_info, gale5a_view_satellite_info, line, vodp_list, GPSNumSet,  GALNumSet,  QZNumSet, GPSL5NumSet, QZL5NumSet, GALE5ANumSet, GALList):
        gsvList = line.split("*")[0].split(",")[4:]
        lastcno = line.split("*")[0].split(",")[-1]
        i = 0
        num = len(gsvList) - 1
        while i < num:
            IDNum = gsvList[i]
            if i + 3 > num:
                break
            cno = gsvList[i + 3]
            if IDNum is None or IDNum == '' or cno is None or cno == '':
                i = i + 4
                continue
            IDNum = float(IDNum)
            # GBGSV  GAGSV单独处理
            
            if "GBGSV" in line:
                bds_view_satellite_info.set_satellite_info(line, gsvList[i:i + 4])
                i = i + 4
                continue

            if "BDGSV" in line:
                bds_view_satellite_info.set_satellite_info(line, gsvList[i:i + 4])
                i = i + 4
                continue

            if "GAGSV" in line:
                gal_view_satellite_info.set_satellite_info(line, gsvList[i:i + 4])
                # hu cno = 1:GAL E5a
                if lastcno == '1' or lastcno == '2':
                    if (IDNum in GALList) or (IDNum in GALNumSet):
                        GALE5ANumSet.add(IDNum)
                    gale5a_view_satellite_info.set_satellite_info(line, gsvList[i:i + 4])
                i = i + 4
                continue
            
            if "QZGSV" in line:
                qz_view_satellite_info.set_satellite_info(line, gsvList[i:i + 4])
                # hu cno = 8:QZ L5
                if lastcno == '8':
                    if (IDNum in QZNumSet) or (IDNum in GPSNumSet):
                        QZL5NumSet.add(IDNum)
                    qzl5_view_satellite_info.set_satellite_info(line, gsvList[i:i + 4])
                i = i + 4
                continue
            if "PQGSV" in line:
                qz_view_satellite_info.set_satellite_info(line, gsvList[i:i + 4])
                if lastcno == '8':
                    if (IDNum in QZNumSet) or (IDNum in GPSNumSet):
                        QZL5NumSet.add(IDNum)
                    qzl5_view_satellite_info.set_satellite_info(line, gsvList[i:i + 4])
                i = i + 4
                continue

            if IDNum >= 1 and IDNum <= 32:
                # hu cno = 8:GPS L5
                if lastcno == '8':
                    if IDNum in GPSNumSet:
                            GPSL5NumSet.add(IDNum)
                    gpsl5_view_satellite_info.set_satellite_info(line, gsvList[i:i + 4])
                gps_view_satellite_info.set_satellite_info(line, gsvList[i:i + 4])
            elif IDNum >= 65 and IDNum <= 96:
                gln_view_satellite_info.set_satellite_info(line, gsvList[i:i + 4])
            elif IDNum >= 201 and IDNum <= 237:
                bds_view_satellite_info.set_satellite_info(line, gsvList[i:i + 4])

            elif IDNum >= 100 and IDNum <= 136:
                gal_view_satellite_info.set_satellite_info(line, gsvList[i:i + 4])
                if lastcno == '1' or lastcno == '2':
                    gale5a_view_satellite_info.set_satellite_info(line, gsvList[i:i + 4])
            elif IDNum >= 193 and IDNum <= 200:
                qz_view_satellite_info.set_satellite_info(line, gsvList[i:i + 4])
                if lastcno == '8':
                    if (IDNum in QZNumSet) or (IDNum in GPSNumSet):
                        QZL5NumSet.add(IDNum)
                    qzl5_view_satellite_info.set_satellite_info(line, gsvList[i:i + 4])
            i = i + 4

    def __calculateUsedSatellite(self, GPSNumSet, GLNNumSet, GALNumSet, BDSNumSet, QZNumSet, line, GLNList, GALList, BDList, GPSL5NumSet, QZL5NumSet, GALE5ANumSet, vodp_list):


        vdop = line.split("*")[0].split(",")[-1]
        if "GSA" in line:
            gngVersionFlag = line.split("*")[0].split(",")[-1]
            if gngVersionFlag is not "" and isinstance(eval(gngVersionFlag), int):
                gngVersionFlag = int(gngVersionFlag)
                uesdSatelliteIDs = line.split("*")[0].split(",")[3:-4]
                vaildUseSateLite = filter(isVaildID, uesdSatelliteIDs)
                # 如果是1，表示gps(gn里面的gps需要其他gsa里面gps去重)，里边的number都是gps卫星号
                # 2是glonass，3是galileo， 5是BDS
                if gngVersionFlag == 1:
                    for vaildID in vaildUseSateLite:
                        vaildID = int(vaildID)
                        if vaildID >= 1 and vaildID <= 32:
                            GPSNumSet.add(float(vaildID))
                        elif vaildID >= 193 and vaildID <= 199: 
                            QZNumSet.add(float(vaildID)) 
                elif gngVersionFlag == 2:
                    GLNList.extend(vaildUseSateLite)
                elif gngVersionFlag == 3:
                    GALList.extend(vaildUseSateLite)
                elif gngVersionFlag == 4:
                    BDList.extend(vaildUseSateLite)
                return

        uesdSatelliteIDs = line.split("*")[0].split(",")[3:-4]
        # qzgsa另外处理
        if "QZGSA" in line:
            for IDNum in uesdSatelliteIDs:
                if IDNum is None or IDNum == '':
                    continue
                IDNum = float(IDNum)
                if vdop == '8':
                    QZL5NumSet.add(IDNum)
                QZNumSet.add(IDNum)
            return

        for IDNum in uesdSatelliteIDs:
            if IDNum is None or IDNum == '':
                continue
            IDNum = float(IDNum)

            if IDNum >= 1 and IDNum <= 32:
                GPSNumSet.add(IDNum)
                if vdop == '8':
                    GPSL5NumSet.add(IDNum)
            elif IDNum >= 65 and IDNum <= 96:
                GLNNumSet.add(IDNum)
            elif IDNum >= 201 and IDNum <= 237:
                BDSNumSet.add(IDNum)
            elif IDNum >= 193 and IDNum <= 200:
                QZNumSet.add(IDNum)
                if vdop == '8':
                    QZL5NumSet.add(IDNum)
            elif IDNum >= 100 and IDNum <= 136:
                GALNumSet.add(IDNum)
                if vdop == '1':
                    GALE5ANumSet.add(IDNum)

    def __getTop5Cn0Avg(self, valueList):
        valueList = list(valueList)
        if len(valueList) == 0:
            return ""
        elif len(valueList) <= 5:
            sum = 0.0
            for element in valueList:
                sum += element
            return round(sum / len(valueList), 2)
        else:
            sum = 0.0
            valueList.sort(reverse=True)
            for element in valueList[:5]:
                sum += element
            return round(sum / 5, 2)

    def __convertdmmmmmm2d(self, titude):
        '''
        @titude 原始的符合dmm.mmmm规则的经纬度，小数点前至少3位数字，小数点后必须1位数字
        @return 小数的经纬度字符串
        '''
        titude = str(titude)
        if not re.match("^\d{3,}\.\d{1,}$", titude):
            return ''
        dmm, mmmm = titude.split('.')
        d = dmm[:-2]
        mm = dmm[-2:]
        titude_f = float(d) + float('%s.%s' % (mm, mmmm)) / 60
        return titude_f

    def getHiGeo10_2DB(self, logPath, deviceName):
        if os.path.isdir(logPath):
            xmlList = os.listdir(logPath)
        else:
            raise ("higeo 1.0 log path is wrong [{}]".format(logPath))
        higeoList = []
        for line in xmlList:
            if line.startswith("higeo_") and line.endswith(".xml"):
                higeoList.append(os.path.join(logPath, line))
        PositionList = []
        for filepath in higeoList:
            print(filepath)
            with open(filepath, "r") as rd:
                line = rd.readline()
                while line:
                    if line.find("<position") != -1:
                        UTC = None
                        lon = None
                        lat = None
                        alt = None
                        speed = ""
                        heading = ""
                        pos_unc = ""
                        source = ""
                        final = False
                        line = rd.readline()
                        while not "</position>" in line:
                            if line.find("<coordinate lat=") != -1:
                                if "lat" in line:
                                    lat = line.split("=")[1].split('"')[1]
                                if "lon" in line:
                                    lon = line.split("=")[2].split('"')[1]
                                if "alt" in line:
                                    alt = line.split("=")[3].split('"')[1]
                            elif line.find("<accuracy acc=") != -1:
                                pos_unc = line.split("=")[1].split('"')[1]
                            elif line.find("<velocity speed=") != -1:
                                if "speed" in line:
                                    speed = line.split("=")[1].split('"')[1]
                                if "heading" in line:
                                    heading = line.split("=")[2].split('"')[1]
                            elif "<outputTime time" in line:
                                temp = line.split("=")[1].split('"')[1]
                                if temp:
                                    UTC = int(int(temp) / 1000) + int(round(float(int(temp) % 1000) / 1000))
                                    UTC = datetime.datetime.utcfromtimestamp(UTC).strftime("%Y-%m-%d %H:%M:%S")
                            elif '<technology name="final"' in line:
                                if "source" in line:
                                    source = line.split("=")[2].split('"')[1]
                                final = True
                            line = rd.readline()

                        if final and UTC and lon and lat:
                            PositionList.append([UTC, lon, lat, alt, speed, heading, pos_unc, source])
                    line = rd.readline()
                rd.close()
        self.create_Track_TABLE(deviceName)
        for element in PositionList:
            self.add_Track_data(deviceName, element)
        self.commit()

#         self.__writeTrackError(deviceName)

    @LBSDector(True)
    def writeNMEATrackError(self, testTable, refTable="novatel"):
        refelement = ["UTC", "ref_longitude", "ref_latitude", "ref_alt", "ref_speed", "ref_heading"]
        testelement = ["UTC", "test_longitude", "test_latitude", "test_alt", "test_speed", "test_heading"]
        testList = self.getcolomFormDB(testTable, ["UTC", "longitude", "latitude", "altitude", "speed", "heading"])
        if not testList:
            return
        testFrame = DataFrame(testList, columns=testelement)
        
        refList = None
        if not self.sceneconf.get("is_need_static_kpi") == True:
            refList = self.getcolomFormDB(refTable, ["UTC", "longitude", "latitude", "altitude", "speed", "heading"])
            if not refList:
                return
            refFrame = DataFrame(refList, columns=refelement)
        else:
            refFrame = DataFrame(refList, columns=refelement)
            refFrame['UTC'] = testFrame['UTC']
            static_kpi_values = self.sceneconf.get("static_kpi_values")
            for kpi, value in static_kpi_values.items():
                refFrame.loc[:,[kpi]] = value


        ref_testList = pd.merge(refFrame, testFrame, on="UTC", how='inner')
        ref_testList = ref_testList.drop_duplicates(['UTC'])
        if len(ref_testList) == 0:
            return False
        ref_testList = ref_testList.sort_values(by='UTC')



        ref_testList["position_error"] = ref_testList.apply(lambda row: self.__calcute_distance(row), axis=1)
        ref_testList["alt_error"] = ref_testList.apply(lambda row: self.__calcute_altError(row), axis=1)
        ref_testList["speed_error"] = ref_testList.apply(lambda row: self.__calcute_speedError(row), axis=1)
        ref_testList["heading_error"] = ref_testList.apply(lambda row: self.__calcute_HeadingError(row), axis=1)

        ref_testList["along_error"] = ref_testList.apply(lambda row : self.__calcute_alongtrackError(row), axis=1)
        ref_testList["across_error"] = ref_testList.apply(lambda row : self.__calcute_crosstrackError(row), axis=1)
        ref_testList["shoot_error"] = ref_testList.apply(lambda row : self.__calcute_overshootError(row), axis=1)
        ref_testList['distance3D_error'] = ref_testList.apply(lambda row: self.__calcute_3DError(row), axis=1)

        ERRORList = ref_testList.loc[:, ["UTC", "position_error", "alt_error", "speed_error", "heading_error", "shoot_error", "along_error", "across_error", "distance3D_error"]]
        
        self.create_NMEAError_TABLE(testTable + "Error")
        for element in ERRORList.values:
            self.add_NMEA_Error_Data(testTable + "Error", element)
        self.commit()
    
    def __writeTrackError(self, testTable, refTable="novatel"):
        refelement = ["UTC", "ref_longitude", "ref_latitude", "ref_speed", "ref_heading"]
        testelement = ["UTC", "test_longitude", "test_latitude", "test_speed", "test_heading", "pos_unc"]
        refList = self.getcolomFormDB(refTable, ["UTC", "longitude", "latitude", "speed", "heading"])
        if not refList:
            return
        testList = self.getcolomFormDB(testTable, ["UTC", "longitude", "latitude", "speed", "heading", "pos_unc"])
        refFrame = DataFrame(refList, columns=refelement)
        testFrame = DataFrame(testList, columns=testelement)
        ref_testList = pd.merge(refFrame, testFrame, on="UTC", how='inner')
        ref_testList = ref_testList.drop_duplicates(['UTC'])
        ref_testList = ref_testList.reset_index(drop=True)
        ref_testList = ref_testList.sort_values(by='UTC')


        if len(ref_testList) == 0:
            return False

        ref_testList["position_error"] = ref_testList.apply(lambda row: self.__calcute_distance(row), axis=1)
        ref_testList["speed_error"] = ref_testList.apply(lambda row: self.__calcute_speedError(row), axis=1)
        ref_testList["heading_error"] = ref_testList.apply(lambda row: self.__calcute_HeadingError(row), axis=1)
        ref_testList["along_error"] = ref_testList.apply(lambda row: self.__calcute_alongtrackError(row), axis=1)
        ref_testList["across_error"] = ref_testList.apply(lambda row: self.__calcute_crosstrackError(row), axis=1)
        ref_testList["over_shoot"] = ref_testList.apply(lambda row: self.__calcute_overshootError(row), axis=1)
        sum_distance_list = []
        novatel_sum_distance_list = []
        for index, row in ref_testList.iterrows():
            if index == 0:
                sum_distance_list.append(0)
                novatel_sum_distance_list.append(0)
            else:
                last_value = sum_distance_list[index - 1]

                if last_value == -10:
                    search_index = index
                    while last_value == -10:
                        search_index = search_index - 1
                        if search_index >= 0 :
                            last_value = sum_distance_list[search_index]
                        else:
                            break
                    if search_index < 0:
                        sum_distance_list.append(0)
                        novatel_sum_distance_list.append(0)
                    else:
                        last_row = ref_testList.ix[search_index, :]
                        last_lon = last_row["test_longitude"]
                        last_lat = last_row["test_latitude"]
                        lon = row["test_longitude"]
                        lat = row["test_latitude"]

                        novatel_last_lon = last_row["ref_longitude"]
                        novatel_last_lat = last_row["ref_latitude"]
                        novatel_lon = row["ref_longitude"]
                        novatel_lat = row["ref_latitude"]

                        sum_distance = self.__calculate_track_distance(last_lon, last_lat, lon, lat)
                        sum_distance_list.append(sum_distance)
                        novatel_sum_distance = self.__calculate_track_distance(novatel_last_lon, novatel_last_lat, novatel_lon, novatel_lat)
                        novatel_sum_distance_list.append(novatel_sum_distance)

                elif row["position_error"] == -10:
                    sum_distance_list.append(-10)
                    novatel_sum_distance_list.append(-10)
                else:
                    last_row = ref_testList.ix[index - 1, :]
                    last_lon = last_row["test_longitude"]
                    last_lat = last_row["test_latitude"]
                    lon = row["test_longitude"]
                    lat = row["test_latitude"]

                    novatel_last_lon = last_row["ref_longitude"]
                    novatel_last_lat = last_row["ref_latitude"]
                    novatel_lon = row["ref_longitude"]
                    novatel_lat = row["ref_latitude"]

                    sum_distance = self.__calculate_track_distance(last_lon, last_lat, lon, lat)
                    sum_distance_list.append(sum_distance)
                    novatel_sum_distance = self.__calculate_track_distance(novatel_last_lon, novatel_last_lat, novatel_lon, novatel_lat)
                    novatel_sum_distance_list.append(novatel_sum_distance)
        ref_testList["track_distance"] = sum_distance_list
        ref_testList["novatel_track_distance"] = novatel_sum_distance_list

        ERRORList = ref_testList.loc[:, ["UTC", "position_error", "speed_error", "heading_error", "along_error", "across_error", "over_shoot", "track_distance", "novatel_track_distance"]]

        self.create_Error_TABLE(testTable + "Error")
        for element in ERRORList.values:
            self.add_Error_data(testTable + "Error", element)
        self.commit()
    
    def writeDevicesSingleDynamicLocationDB(self, config, deviceInfo):
        import pandas as pd
        from pandas import DataFrame    #TODO
        startTime = config['timeSlicing']['starttime']
        endTime = config['timeSlicing']['endtime']
        caseReportPath = config['singleReportPath']
        testData = pd.read_excel(caseReportPath, sheet_name='FirstFixCepTTFF', dtype=str)
        testData['firstFixStartUTC'] = testData.apply(lambda row: self.__calculateUTCTime(startTime, endTime, row[2]), axis=1)
        testData['firstFixUTC'] = testData.apply(lambda row: self.__calculateUTCTime(startTime, endTime, row[3]), axis=1)
        testData['firstFixTTFF'] = testData.apply(lambda row: self.__calculateTTFF(row), axis=1)
        
        
        for device in deviceInfo:
            devicename = device.get("tech", "")
            feature = device["feature"]
            type = device["type"]
            if feature == "nmea" and type != "standard" and devicename != "":
                if 'port' in devicename:
                    portListSN = testData['DeviceSN'].values.tolist()
                    for deviceSN in portListSN:
                        if devicename[4:] in deviceSN:
                            deviceData = testData[testData['DeviceSN'] == deviceSN]
                            break
                else:
                    deviceData = testData[testData['DeviceSN'] == devicename]
                    
                tab = devicename + 'Error'
                CEPerrorData = self.getcolomFormDB(tab, ["UTC", "position_error", "distance3D_error", "alt_error"], startTime, endTime)
                error_data_df = DataFrame(CEPerrorData, columns=["firstFixUTC", 'firstFixCep2D', 'firstFixCep3D', 'firstFixCepAlt'])[:].astype(str)
                
                deviceData = pd.merge(deviceData, error_data_df, on="firstFixUTC", how='left')
                deviceData['firstFixCep2D'].fillna(-10, inplace=True)
                deviceData['firstFixCep3D'].fillna(-10, inplace=True)
                deviceData['firstFixCepAlt'].fillna(-10, inplace=True)
                ERRORList = deviceData.loc[:,['Times' , 'StartTime', 'FixTime', 'Lat', 'Lon', 'Alt', 'FixFlag', 'firstFixTTFF', 'firstFixCep2D','firstFixCep3D',  'firstFixCepAlt', 'firstFixStartUTC', 'firstFixUTC']]
                
                self.create_single_TABLE(devicename + "single")
                for element in ERRORList.values:
                    self.add_single_data(devicename + "single", element)
                self.commit()
                
                    
                    
    def writeDevicesSingleLocationDB(self, config, deviceInfo):
        lonRef = config['static_kpi_values']['ref_longitude']
        latRef = config['static_kpi_values']['ref_latitude']
        altRef = config['static_kpi_values']['ref_alt']
        startTime = config['timeSlicing']['starttime']
        endTime = config['timeSlicing']['endtime']
        caseReportPath = config['singleReportPath']
        import pandas as pd
        from pandas import DataFrame    #TODO
        testData = pd.read_excel(caseReportPath, sheet_name='FirstFixCepTTFF', dtype=str)
        testData['firstFixTTFF'] = testData.apply(lambda row: self.__calculateTTFF(row), axis=1)
        testData['firstFixCep2D'] = testData.apply(lambda row: self.__calculateDistance(lonRef, latRef, row[5], row[4] , row[7]), axis=1)
        testData['firstFixCep3D'] = testData.apply(lambda row: self.__calculateDistance3D(lonRef, latRef, altRef, row[5], row[4], row[6], row[7]), axis=1)
        testData['firstFixCepAlt'] = testData.apply(lambda row: self.__calculateDistanceAlt(altRef, row[6], row[7]), axis=1)
        testData['firstFixStartUTC'] = testData.apply(lambda row: self.__calculateUTCTime(startTime, endTime, row[2]), axis=1)
        testData['firstFixUTC'] = testData.apply(lambda row: self.__calculateUTCTime(startTime, endTime, row[3]), axis=1)
        for device in deviceInfo:
            devicename = device.get("tech", "")
            feature = device["feature"]
            type = device["type"]
            if feature == "nmea" and type != "standard" and devicename != "":
                deviceData = testData[testData['DeviceSN'] == devicename]
                ERRORList = deviceData.loc[:,['Times' , 'StartTime', 'FixTime', 'Lat', 'Lon', 'Alt', 'FixFlag', 'firstFixTTFF', 'firstFixCep2D','firstFixCep3D',  'firstFixCepAlt', 'firstFixStartUTC', 'firstFixUTC']]
                self.create_single_TABLE(devicename + "single")
                for element in ERRORList.values:
                    self.add_single_data(devicename + "single", element)
            self.commit()
    

    def getQcomKml2DB(self, LogPath, deviceName, timeZone=None):
        if not os.path.isdir(LogPath):
            ErrorInfo("the LogPaht [{}] is wrong".format(LogPath))
        ListDir = os.listdir(LogPath)
        ListDir.sort()
        for fileName in ListDir:
            LogPath = os.path.join(LogPath, fileName)
            if not os.path.isfile(LogPath) or not LogPath.lower().endswith(".kml"):
                continue
            with open(LogPath, "r") as input_file:
                currline = input_file.readline()
                inFinal = False
                PointList = []
                while currline != "":

                    if currline.find("<Folder>") > 0:
                        currline = input_file.readline()  # name
                        currline = input_file.readline()  # description
                        folderName = self.__getValue(currline, 'description')

                        if folderName == 'All 0x1476 Final Fixes':
                            inFinal = True
                        else:
                            inFinal = False

                    if currline.find("</Folder>") > 0:

                        if inFinal == True:
                            break
                        else:
                            pass

                    if (currline.find("<Placemark>") > 0) and (inFinal == True):
                        currline = input_file.readline()

                        UTC = None
                        Lon = None
                        lat = None
                        alt = ""
                        Acc = None
                        speed = None
                        heading = None
                        other = ""
                        while currline.find("</Placemark>") < 0:
                            if currline.find("<TimeStamp>") > 0:
                                currline = input_file.readline()
                                localtime = self.__getValue(currline, 'when').replace("T", " ")
                                UTC = self.__covertlocaltime2utctime(localtime, timeZone)

                            elif currline.find("<Point>") > 0:
                                currline = input_file.readline()
                                coord = self.__getValue(currline, 'coordinates')
                                Lon = coord[:coord.find(',')]
                                temp = coord[coord.find(',') + 1:]
                                lat = temp[:temp.find(',')]

                            elif currline.find("HEPE") > 0:
                                Acc = self.__getValue(currline, 'HEPE')

                            elif currline.find("Heading") > 0:
                                heading = self.__getValue(currline, 'Heading')

                            elif currline.find("Speed") > 0:
                                currline = input_file.readline()
                                speed = self.__getValue(currline, 'Speed')
                            else:
                                pass

                            currline = input_file.readline()

                        # -----end of while-----
                        if UTC and Lon and lat:
                            PointList.append([UTC, Lon, lat, alt, speed, heading, Acc, other])

                    currline = input_file.readline()
                input_file.close()
            if len(PointList) > 0:
                self.create_Track_TABLE(deviceName)
                for element in PointList:
                    self.add_Track_data(deviceName, element)
                self.commit()
        self.__writeTrackError(deviceName)

    def __getValue(self, line, tag):
        try:
            if tag == 'nowrap':
                head = '<td nowrap>'
                tail = '</td>'
            elif tag == 'CN0':
                head = '<font color=\'blue\'>'
                tail = '</font>'
            elif tag == 'HEPE':
                head = '<dd>HEPE: '
                tail = ' (m)</dd>'
            elif tag == 'Heading':
                head = '<dd>Heading: '
                tail = ' (degrees)</dd>'
            elif tag == 'Speed':
                head = '<dd>Horizontal: '
                tail = ' (m/s)</dd>'
            else:
                head = '<' + tag + '>'
                tail = '</' + tag + '>'
            fromHead = line.find(head) + len(head)
            toTail = line.find(tail)
            return line[fromHead:toTail]
        except:
            return None

    def __writeFT2Table(self, logpath, deviceName):
        self.create_FT_TABLE(deviceName)

        # log file sort as cread time
        listDir = os.listdir(logpath)
        HigeoSessionLog = []
        HigeoOldLog = []
        for filename in listDir:
            if filename.find("GNSS_HIGEO_") != -1 and filename.endswith(".t"):
                if filename.count("_") == 2:
                    HigeoOldLog.append(filename)
                elif filename.count("_") == 4:
                    HigeoSessionLog.append(filename)
                else:
                    PRINTE(filename)
        HigeoOldLog = sorted(HigeoOldLog, key=lambda d: int(d.split('_')[-1].split('.')[0]), reverse=True)
        HigeoSessionLog = sorted(HigeoSessionLog, key=lambda d: int(d.split('_')[-1].split('.')[0]))
        HigeoSessionLog = sorted(HigeoSessionLog, key=lambda d: d[0:27])
        # check session
        if HigeoOldLog != [] and HigeoSessionLog != []:
            return False, 'more than one session'
        if HigeoSessionLog != []:
            session = HigeoSessionLog[0][0:27]
            for element in HigeoSessionLog:
                if session not in element:
                    return False, 'more than one session'

                    # start get log to db
        fileNameList = HigeoOldLog + HigeoSessionLog
        config = False
        replay = False
        gps_start = False
        lastLine = "$SENSORINFO,13,"
        for fileName in fileNameList:
            fileName = os.path.join(logpath, fileName)
            PRINTI(fileName)
            with open(fileName, "r") as fd:
                for line in fd:
                    line = line[:-1]
                    if not config:
                        self.__add_config(line)
                        if line.find("HiGeo starts to initialize all modules") != -1:
                            self.__writeConfig2DB(deviceName + "_config")
                            config = True
                        else:
                            continue
                    if not replay:
                        self.__add_sensor_vendor(line)

                    if line.find("$CONTEXTRES,84,") != -1:
                        if not replay:
                            self.__writeSensorVendor2DB(deviceName + "_vendor")
                            replay = True
                        self.__writeLogformat2DB(deviceName, line, " $CONTEXTRES,84,", 84)
                    elif line.find("$MMINFO,70,") != -1:
                        self.__writeLogformat2DB(deviceName, line, " $MMINFO,70,", 70)
                    elif line.find("$WIFIINFO,60,") != -1:
                        self.__writeLogformat2DB(deviceName, line, " $WIFIINFO,60,", 60)
                    elif line.find("$WIFIOTHER,61,") != -1:
                        self.__writeLogformat2DB(deviceName, line, " $WIFIOTHER,61,", 61)
                    elif line.find("$QTFWIFINLP,62,") != -1:
                        self.__writeLogformat2DB(deviceName, line, " $QTFWIFINLP,62,", 62)
                    elif line.find("$SENSORINFO,13,") != -1:
                        if not (lastLine == "$SENSORINFO,13," or lastLine == "$PVTINFO,50,"):
                            return False, "Missing Log in this section[{}] {}".format(line, fileName)
                        self.__writeLogformat2DB(deviceName, line, " $SENSORINFO,13,", 13)
                        lastLine = "$SENSORINFO,13,"
                    elif line.find("$SENSORINFO,14,") != -1:
                        if not (lastLine == "$SENSORINFO,13," or lastLine == "$SENSORINFO,14,"):
                            return False, "Missing Log in this section[{}] {}".format(line, fileName)
                        self.__writeLogformat2DB(deviceName, line, " $SENSORINFO,14,", 14)
                        lastLine = "$SENSORINFO,14,"
                    elif line.find("$SENSORINFO,15,") != -1:
                        if not (lastLine == "$SENSORINFO,14," or lastLine == "$SENSORINFO,15,"):
                            return False, "Missing Log in this section[{}] {}".format(line, fileName)
                        self.__writeLogformat2DB(deviceName, line, " $SENSORINFO,15,", 15)
                        lastLine = "$SENSORINFO,15,"
                    elif line.find("$PVTINFO,50,") != -1:
                        if lastLine != "$SENSORINFO,15," and gps_start:
                            return False, "Missing Log in this section[{}] {}".format(line, fileName)
                        if not gps_start:
                            gps_start = True
                        self.__writeLogformat2DB(deviceName, line, " $PVTINFO,50,", 50)
                        lastLine = "$PVTINFO,50,"
                    elif line.find("$CONTEXTRES,80,") != -1:
                        self.__writeLogformat2DB(deviceName, line, " $CONTEXTRES,80,", 80)
                    elif line.find("$FUSIONRES,90,") != -1:
                        self.__writeLogformat2DB(deviceName, line, " $FUSIONRES,90,", 90)
                    elif line.find("$FUSIONRES,90,") != -1:
                        self.__writeLogformat2DB(deviceName, line, " $FUSIONRES,90,", 90)
                    elif line.find("$FUSIONRES,91,") != -1:
                        self.__writeLogformat2DB(deviceName, line, " $FUSIONRES,91,", 91)
                    elif line.find("$FUSIONRES,92,") != -1:
                        self.__writeLogformat2DB(deviceName, line, " $FUSIONRES,92,", 92)
                    elif line.find("$FUSIONRES,93,") != -1:
                        self.__writeLogformat2DB(deviceName, line, " $FUSIONRES,93,", 93)
                    elif line.find("$FUSIONRES,94,") != -1:
                        self.__writeLogformat2DB(deviceName, line, " $FUSIONRES,94,", 94)
                    elif line.find("$QTFFUSION,95,") != -1:
                        self.__writeLogformat2DB(deviceName, line, " $QTFFUSION,95,", 95)
                    elif line.find("start_quickttff") != -1:
                        self.__writeStartQuickttff2DB(deviceName, line)
                    elif line.find("stop_quickttff") != -1:
                        self.__writeStopQuickttff2DB(deviceName, line)
                    elif line.find("Sensor Hub PDR step_count") != -1:
                        self.__writePdrStepCount2DB(deviceName, line)
                self.commit()
            fd.close()
        return True, ""

    def __add_config(self, line):
        if line.find("higeo_log_level") != -1:
            log_level = int(line.split(" = ")[-1].split(" ")[0])
            self.config.setdefault("higeo_log_level", log_level)
            systemTime = line[0:23]
            self.config.setdefault("systemTime", systemTime)
        elif line.find("higeo_enable") != -1:
            higeo_enable = int(line.split(" = ")[-1].split(" ")[0])
            self.config.setdefault("higeo_enable", higeo_enable)
        elif line.find("higeo_vdr_type") != -1:
            higeo_vdr_type = int(line.split(" = ")[-1].split(" ")[0])
            self.config.setdefault("higeo_vdr_type", higeo_vdr_type)
        elif line.find("higeo_vdr_always_on") != -1:
            higeo_vdr_always_on = int(line.split(" = ")[-1].split(" ")[0])
            self.config.setdefault("higeo_vdr_always_on", higeo_vdr_always_on)
        elif line.find("higeo_vdr_dead_reckoning_time") != -1:
            higeo_vdr_dead_reckoning_time = int(line.split(" = ")[-1].split(" ")[0])
            self.config.setdefault("higeo_vdr_dead_reckoning_time", higeo_vdr_dead_reckoning_time)
        elif line.find("higeo_pdr_enable") != -1:
            higeo_pdr_enable = int(line.split(" = ")[-1].split(" ")[0])
            self.config.setdefault("higeo_pdr_enable", higeo_pdr_enable)
        elif line.find("higeo_pdr_dead_reckoning_time") != -1:
            higeo_pdr_dead_reckoning_time = int(line.split(" = ")[-1].split(" ")[0])
            self.config.setdefault("higeo_pdr_dead_reckoning_time", higeo_pdr_dead_reckoning_time)
        elif line.find("higeo_wifi_enable") != -1:
            higeo_wifi_enable = int(line.split(" = ")[-1].split(" ")[0])
            self.config.setdefault("higeo_wifi_enable", higeo_wifi_enable)
        elif line.find("higeo_mm_enable") != -1:
            higeo_mm_enable = int(line.split(" = ")[-1].split(" ")[0])
            self.config.setdefault("higeo_mm_enable", higeo_mm_enable)
        elif line.find("higeo_fusion_ver") != -1:
            higeo_fusion_ver = line.split(" = ")[-1].split(" ")[0]
            self.config.setdefault("higeo_fusion_ver", higeo_fusion_ver)
        elif line.find("higeo_gps_vendor") != -1:
            higeo_gps_vendor = line.split(" = ")[-1].split(" ")[0]
            self.config.setdefault("higeo_gps_vendor", higeo_gps_vendor)
        elif line.find("higeo_quickttff_enable") != -1:
            higeo_quickttff_enable = int(line.split(" = ")[-1].split(" ")[0])
            self.config.setdefault("higeo_quickttff_enable", higeo_quickttff_enable)
        else:
            pass

    def __writeConfig2DB(self, tableName):
        self.create_HIGEO_config(tableName)
        table_value = []
        table_value.append(self.config.get("systemTime", "0000-00-00-00:00:00.000"))
        table_value.append(self.config.get("higeo_log_level", 1))
        table_value.append(self.config.get("higeo_enable", 1))
        table_value.append(self.config.get("higeo_vdr_type", 1))
        table_value.append(self.config.get("higeo_vdr_always_on", 1))
        table_value.append(self.config.get("higeo_vdr_dead_reckoning_time", 240))
        table_value.append(self.config.get("higeo_pdr_enable", 1))
        table_value.append(self.config.get("higeo_pdr_dead_reckoning_time", 240))
        table_value.append(self.config.get("higeo_wifi_enable", 1))
        table_value.append(self.config.get("higeo_mm_enable", 1))
        table_value.append(self.config.get("higeo_quickttff_enable", 1))
        table_value.append(self.config.get("higeo_fusion_ver", "1.5"))
        table_value.append(self.config.get("higeo_gps_vendor", "BC"))
        self.add_HIGEO_config_data(tableName, table_value)

    def __add_sensor_vendor(self, line):
        if line.find("sens_vendor") != -1:
            sensor_type = int(line.split(",")[0].split("=")[-1])
            sensor_vendor = line.split(",")[-1].split("=")[-1].split(" ")[0]
            self.sensor_vendor.setdefault(sensor_type, sensor_vendor)

    def __writeSensorVendor2DB(self, tableName):
        self.create_HIGEO_vendor(tableName)
        for key, value in self.sensor_vendor.items():
            self.add_HIGEO_vendor_data(tableName, [key, value])

    def __writeLogformat2DB(self, tableName, line, Format, Type):
        table_value = []
        systemTime, action = line.split(Format)
        table_value.append(systemTime)
        table_value.append(Type)
        actionlist = action.split(",")
        for element in actionlist:
            table_value.append(element)
        self.add_FT_data(tableName, table_value)

    def __writeStartQuickttff2DB(self, tableName, line):
        table_value = [line[0:23], "start_quickttff", '', '', '', '', '', '', '', '', '', '', '']
        self.add_FT_data(tableName, table_value)

    def __writeStopQuickttff2DB(self, tableName, line):
        table_value = [line[0:23], "stop_quickttff", '', '', '', '', '', '', '', '', '', '', '']
        self.add_FT_data(tableName, table_value)

    def __writePdrStepCount2DB(self, tableName, line):
        table_value = [line[0:23], "step_count", line.split("=")[-1], "1", "1", "1", "1", "1", "1", "1", "1", "1", "1"]
        self.add_FT_data(tableName, table_value)

    def __getAresAG_RunBat(self):
        sub_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\WinRAR.exe"
        itemName = ""
        import winreg as winReg
        try:
            main_key = winReg.HKEY_LOCAL_MACHINE
            key = winReg.OpenKey(main_key, sub_key)
            path = winReg.QueryValueEx(key, itemName)[0]
            return path
        except:
            import traceback
            PRINTE("getAresAG_RunBat Failed .error %s" % traceback.format_exc())
            return None

    def __getNovatelPointTime(self, line, timeZone=-18):
        try:
            elementlist = line.split("<TD>")
            timeformat = elementlist[-2][:8]
            hour, Min, sec = timeformat.split(":")
            allsec = int(hour) * 3600 + int(Min) * 60 + int(sec) + timeZone
            hour = int(allsec / 3600)
            Min = int((allsec - hour * 3600) / 60)
            sec = allsec % 60
            date_string = (elementlist[-1][:10]) + " " + str(hour) + ":" + str(Min) + ":" + str(sec)
            Format = "%m/%d/%Y %H:%M:%S"
            dateformat = datetime.datetime.strptime(date_string, Format)
            return dateformat
        except:
            PRINTE("GET novatel time fail, [{}]".format(line))
            return None

    def __getNovatelPoint(self, line):
        try:
            lon, lat, alt = line.split("<coordinates>")[-1].split("</coordinates>")[0].split(",")
            return lon, lat, alt
        except:
            PRINTE("GET novatel point fail, [{}]".format(line))
            return None, None, None

    def __getNovatelSVCount(self, line):
        try:
            svcount = line.split("<TD>")[1].split("</TD>")[0]
            return svcount
        except:
            return ""

    def __getNovatelACCValue(self, line):
        try:
            acc = line.split("<TD>")[1].split("</TD>")[0]
            unit = line.split("<TD>")[2].split("</TD>")[0]
            if unit == "m":
                return acc
            elif unit.lower() == "km":
                return str(float(acc) * 1000)
            else:
                PRINTE("ERROR: [{}]".format(unit))
                return "-10"
        except:
            return ""

    def __getNovatelDOP(self, line):
        try:
            PDOP = line.split("<TD>")[1].split("</TD>")[0]
            HDOP = line.split("<TD>")[2].split("</TD>")[0]
            VDOP = line.split("<TD>")[3].split("</TD>")[0]
            return PDOP, HDOP, VDOP
        except:
            PRINTE("GET novatel DOPs fail, [{}]".format(line))
            return None, None, None

    def __getNovatelSpeed(self, line):
        try:
            speedlist = line.split("<TD>")[1:-1]
            e = float(speedlist[0].split("</TD>")[0])
            n = float(speedlist[1].split("</TD>")[0])
            #        h = float(speedlist[2].split("</TD>")[0])
            speed = math.sqrt(e * e + n * n)
            return speed
        except:
            PRINTE("GET novatel speed fail, [{}]".format(line))
            return None

    def __getNovatelHeading(self, line):
        try:
            deg = line.split("<TD>")[-2].split("</TD>")[0]
            return deg
        except:
            PRINTE("GET novatel heading fail, [{}]".format(line))
            return None

    def __writHigeoKPIError(self, deviceName, Type, resourceDB=None, refTable="novatel"):
        testTable = deviceName + "_" + Type
        refelement = ["UTC", "ref_longitude", "ref_latitude", "ref_speed", "ref_heading"]
        testelement = ["UTC", "flag", "test_longitude", "test_latitude", "test_speed", "test_heading", "pos_unc"]
        if resourceDB:
            refList = resourceDB.getcolomFormDB(refTable, ["UTC", "longitude", "latitude", "speed", "heading"])
        else:
            refList = self.getcolomFormDB(refTable, ["UTC", "longitude", "latitude", "speed", "heading"])
        if not refList:
            return False
        testList = self.getcolomFormDB(testTable, ["UTC", "list2", "list3", "list4", "list6", "list7", "list8"])
        if not testList:
            return True
        refFrame = DataFrame(refList, columns=refelement)
        testFrame = DataFrame(testList, columns=testelement)
        ref_testList = pd.merge(refFrame, testFrame, on="UTC", how='inner')

        if len(ref_testList) == 0:
            return False

        ref_testList["position_error"] = ref_testList.apply(lambda row: self.__calcute_distance(row, True), axis=1)
        ref_testList["speed_error"] = ref_testList.apply(lambda row: self.__calcute_speedError(row, True), axis=1)
        ref_testList["heading_error"] = ref_testList.apply(lambda row: self.__calcute_HeadingError(row, True), axis=1)
        ref_testList["along_error"] = ref_testList.apply(lambda row: self.__calcute_alongtrackError(row, True), axis=1)
        ref_testList["across_error"] = ref_testList.apply(lambda row: self.__calcute_crosstrackError(row, True), axis=1)
        ref_testList["over_shoot"] = ref_testList.apply(lambda row: self.__calcute_overshootError(row, True), axis=1)

        ERRORList = ref_testList.loc[:,
                    ["UTC", "position_error", "speed_error", "heading_error", "along_error", "across_error",
                     "over_shoot"]]

        self.create_Error_TABLE(testTable + "Error")
        for element in ERRORList.values:
            if element[1] != "":
                self.add_Error_data(testTable + "Error", element)
        self.commit()
        return True
    
    def __calculateTTFF(self, row):
        try:
            startUtc = str(row[2])
            endUtc = str(row[3])
            if startUtc and endUtc:
                if (int(startUtc[:2]) == 23) and (int(endUtc[:2]) == 0):
                    startTime = int(startUtc[:2]) * 3600 + int(startUtc[2:4]) * 60 + int(startUtc[4:6]) + float(startUtc.split('.')[-1]) / 1000
                    endTime = (int(endUtc[:2]) * 3600 + int(endUtc[2:4]) * 60 + int(endUtc[4:6]) + float(endUtc.split('.')[-1]) / 1000 ) + 24*3600
                    ttff = endTime - startTime
                    return ttff
                else:
                    startTime = int(startUtc[:2]) * 3600 + int(startUtc[2:4]) * 60 + int(startUtc[4:6]) + float(startUtc.split('.')[-1]) / 1000
                    endTime = int(endUtc[:2]) * 3600 + int(endUtc[2:4]) * 60 + int(endUtc[4:6]) + float(endUtc.split('.')[-1]) / 1000
                    ttff = endTime - startTime
                    return ttff
        except:
            import traceback
            print(traceback.format_exc())
            return -10
        
    def __calculateUTCTime(self, startTime, endTime, Utc):
        from datetime import datetime, timedelta
        strstartTime = startTime
        strendTime = endTime
        try:
            if not Utc:
                return -10
                
            delta_time = timedelta(seconds=3600*24)
            startTime = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
            endTime = datetime.strptime(endTime,"%Y-%m-%d %H:%M:%S") 
            if (endTime -delta_time) > startTime:
                return -10
            Utc = strstartTime.split(' ')[0] + ' ' + Utc[:2] + ':' + Utc[2:4] + ':' + Utc[4:6]
            Utc = datetime.strptime(Utc, "%Y-%m-%d %H:%M:%S")
            if (Utc >= startTime) and (Utc <= endTime):
                return datetime.strftime(Utc,"%Y-%m-%d %H:%M:%S") 
            
            Utc = strendTime.split(' ')[0] + ' ' + Utc[:2] + ':' + Utc[2:4] + ':' + Utc[4:6]
            Utc = datetime.strptime(Utc, "%Y-%m-%d %H:%M:%S")
            if (Utc >= startTime) and (Utc <= endTime):
                return datetime.strftime(Utc,"%Y-%m-%d %H:%M:%S") 
            return -10
        except:
            import traceback
#             print(traceback.format_exc())
            return -10
        
    def __calculateDistanceAlt(self, altStart, altEnd, flag):
        if int(flag)==0:
            return -10
        if not (altStart and altEnd):
            return -10
        altStart = float(altStart)
        altEnd = float(altEnd)
        return round(altEnd - altStart, 3)
    
    def __calculateDistance3D(self, lonStart, latStart, altStart, lonEnd, latEnd, altEnd, flag):
        if int(flag) == 0:
            return -10
        if not (altStart and altEnd):
            return -10
        altStart = float(altStart)
        altEnd = float(altEnd)
        HorErr = self.__calculateDistance(lonStart, latStart, lonEnd, latEnd, flag)
        Distance3D = math.sqrt(HorErr * HorErr + (altStart - altEnd) * (altStart - altEnd))
        return round(Distance3D, 3)
    
    def __calculateDistance(self, lon_start, lat_start, lon_end, lat_end, flag):
        if int(flag) == 0:
            return -10
        if not (lon_end and lat_end):
            return -10
        import math
        GEO_RADIUS_O_FEARTH = 6370856
        COE_DEG2RAD = 0.0174532925
        lon_start = float(lon_start)
        lat_start = float(lat_start)
        lon_end = self.__convertdmmmmmm2d(lon_end)
        lat_end = self.__convertdmmmmmm2d(lat_end)

        lon_start = lon_start * COE_DEG2RAD
        lat_start = lat_start * COE_DEG2RAD
        lon_end = lon_end * COE_DEG2RAD
        lat_end = lat_end * COE_DEG2RAD

        rel_xy_1 = (lon_end - lon_start) * GEO_RADIUS_O_FEARTH * math.cos(lat_start)
        rel_xy_2 = (lat_end - lat_start) * GEO_RADIUS_O_FEARTH

        distance = math.sqrt(rel_xy_1 * rel_xy_1 + rel_xy_2 * rel_xy_2)
        return round(distance, 2)

    # 计算位置误差
    def __calcute_distance(self, row, testdevice=False):
        try:
            if testdevice and int(row["flag"]) == 0:
                return ""
            longitude_test = row['test_longitude']
            latitude_test = row['test_latitude']
            longitude_ref = row['ref_longitude']
            latitude_ref = row['ref_latitude']

            longitude_test = float(longitude_test)
            latitude_test = float(latitude_test)
            longitude_ref = float(longitude_ref)
            latitude_ref = float(latitude_ref)

            latSinSelf = math.sin(latitude_test * math.pi / 180)
            latSinref1 = math.sin(latitude_ref * math.pi / 180)

            latCosSelf = math.cos(latitude_test * math.pi / 180)
            latCosref1 = math.cos(latitude_ref * math.pi / 180)

            longSelf = longitude_test * math.pi / 180
            longStd = longitude_ref * math.pi / 180

            longCos = math.cos(longSelf - longStd)
            if longCos > 1.0:
                return 0
            distance = math.acos(latSinSelf * latSinref1 + latCosSelf * latCosref1 * longCos) * 6378137
            return round(distance, 3)
        except:
            import traceback
            print(traceback.format_exc())
            return -10

    def __calcute_altError(self, row, testdevice=False):
        try:
            if testdevice:
                if int(row["flag"]) == 0:
                    return ""
                if row["test_alt"] == "" or row["ref_alt"] == "":
                    return "-10"
            ref_alt = row['ref_alt']
            test_alt = row['test_alt']
            Sum = abs(float(test_alt) - float(ref_alt))
            return round(Sum, 2)
        except:
            return -10
        
    def __calcute_3DError(self, row, testdevice=False):
        
        position= self.__calcute_altError(row)
        alt = self.__calcute_distance(row)
        Distance3D = math.sqrt(position*position + alt*alt)
        
        return round(Distance3D, 2)
        

    def __calcute_speedError(self, row, testdevice=False):
        try:
            if testdevice:
                if int(row["flag"]) == 0:
                    return ""
                if int(float(row['test_speed'])) < 0:
                    return -10
            ref_speed = row['ref_speed']
            test_speed = row['test_speed']
            Sum = abs(float(test_speed) - float(ref_speed))
            return round(Sum, 3)
        except:
            return -10

    def __calcute_HeadingError(self, row, testdevice=False):
        try:
            if testdevice:
                if int(row["flag"]) == 0:
                    return ""
                if int(float(row['test_heading'])) > 360:
                    return -10
            ref_heading = row['ref_heading']
            test_heading = row['test_heading']
            Sum = abs(float(ref_heading) - float(test_heading))
            if 360 - Sum < Sum:
                Sum = 360 - Sum
            return round(abs(Sum), 3)
        except:
            return -10

    def __calcute_alongtrackError(self, row, testdevice=False, isHaveFlag=True):
        try:

            if testdevice:
                if isHaveFlag and int(row["flag"]) == 0:
                    return -10
            position_error = float(row['position_error'])
            test_lon = row['test_longitude']
            test_lat = row['test_latitude']
            ref_log = row['ref_longitude']
            ref_lat = row['ref_latitude']
            ref_heading = row['ref_heading']
            if ref_heading == "" or position_error < 0:
                return -10
            headingdiff = self.__calcute_headingdiff(ref_log, ref_lat, test_lon, test_lat, ref_heading)
            radian_heading_diff = radians(headingdiff)

            result = abs(position_error * np.cos(radian_heading_diff))
            return round(result, 3)
        except:
            import traceback
            PRINTE("__calcute_alongtrackError [{}]".format(traceback.format_exc()))
            return -10

    def __calcute_crosstrackError(self, row, testdevice=False, isHaveFlag=True):
        try:
            if testdevice:
                if isHaveFlag and int(row["flag"]) == 0:
                    return -10
            position_error = float(row['position_error'])
            test_lon = row['test_longitude']
            test_lat = row['test_latitude']
            ref_log = row['ref_longitude']
            ref_lat = row['ref_latitude']
            ref_heading = row['ref_heading']
            if ref_heading == "" or position_error < 0:
                return -10
            headingdiff = self.__calcute_headingdiff(ref_log, ref_lat, test_lon, test_lat, ref_heading)
            radian_heading_diff = radians(headingdiff)

            result = position_error * np.sin(radian_heading_diff)
            return round(result, 3)
        except:
            import traceback
            PRINTE("__calcute_crosstrackError [{}]".format(traceback.format_exc()))
            return -10

    def __calcute_overshootError(self, row, testdevice=False, isHaveFlag=True):
        try:
            if testdevice:
                if isHaveFlag and int(row["flag"]) == 0:
                    return ""
            position_error = float(row['position_error'])
            test_lon = row['test_longitude']
            test_lat = row['test_latitude']
            ref_log = row['ref_longitude']
            ref_lat = row['ref_latitude']
            ref_heading = row['ref_heading']
            if ref_heading == "" or position_error < 0:
                return ""
            headingdiff = self.__calcute_headingdiff(ref_log, ref_lat, test_lon, test_lat, ref_heading)
            radian_heading_diff = radians(headingdiff)

            result = position_error * np.cos(radian_heading_diff)
            return round(result, 3)
        except:
            import traceback
            PRINTE("__calcute_overshootError [{}]".format(traceback.format_exc()))
            return ""
        
    def __calcute_headingdiff(self, ref_lon, ref_lat, test_lon, test_lat, ref_heading):        
        longitude_test = float(test_lon)
        latitude_test = float(test_lat)
        longitude_ref = float(ref_lon)
        latitude_ref = float(ref_lat)
    
        heading_ref = float(ref_heading)
    
        # map points into radians
        lon1, lat1, lon2, lat2 = map(radians, [longitude_ref, latitude_ref, longitude_test, latitude_test])  
    
        dlon = lon2 - lon1   
        x = math.cos(lat2) * math.sin(dlon)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        headin_ref_latlon = math.degrees(math.atan2(x, y))  # return heading in degree
        if(headin_ref_latlon < 0):
            headin_ref_latlon = 360 + headin_ref_latlon

        headingdiff = abs(heading_ref - headin_ref_latlon)
        if(headingdiff > 180):
            headingdiff = 360 - headingdiff
    
        return headingdiff
    
    def __calculate_track_distance(self, lon_start, lat_start, lon_end, lat_end):
        try:
            GEO_RADIUS_O_FEARTH = 6370856
            COE_DEG2RAD = 0.0174532925
            lon_start = float(lon_start)
            lat_start = float(lat_start)
            lon_end = float(lon_end)
            lat_end = float(lat_end)
    
            lon_start = lon_start * COE_DEG2RAD
            lat_start = lat_start * COE_DEG2RAD
            lon_end = lon_end * COE_DEG2RAD
            lat_end = lat_end * COE_DEG2RAD
    
            rel_xy_1 = (lon_end - lon_start) * GEO_RADIUS_O_FEARTH * math.cos(lat_start)
            rel_xy_2 = (lat_end - lat_start) * GEO_RADIUS_O_FEARTH
    
            distance = math.sqrt(rel_xy_1 * rel_xy_1 + rel_xy_2 * rel_xy_2)
            return round(distance, 2)
        except Exception as e:
            # PRINTE("calculate_track_distance[{}]".format(traceback.format_exc()))
            PRINTE("calculate_track_distance[{},{},{},{}]".format(lon_start, lat_start, lon_end, lat_end))
            return -10

    def __covertlocaltime2utctime(self, localtime, timeZone):
        if not timeZone:
            return localtime
        try:
            datetimeArray = datetime.datetime.strptime(localtime, "%Y-%m-%d %H:%M:%S").timetuple()
            datetimeStamp = time.mktime(datetimeArray)
            timestamp = datetime.datetime.fromtimestamp(datetimeStamp + timeZone)
            return timestamp.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return ""
        
    @LBSDector(True)
    def __writeNMEAMileage2DB(self, testTable, refTable="novatel"):
        ement = ["UTC", "longitude", "latitude"]
        if testTable.lower().find('novatel') == -1:
            ref_testList = self.getcolomFormDB(testTable, ement)
            if not ref_testList:
                return
            ref_testList = DataFrame(ref_testList, columns=ement)
        else:
            if not self.sceneconf.get("is_need_static_kpi") == True:
                ref_testList = self.getcolomFormDB(refTable, ement)
                if not ref_testList:
                    return
                ref_testList = DataFrame(ref_testList, columns=ement)
            else:
                ref_testList = DataFrame(ref_testList, columns=ement)
                static_kpi_values = self.sceneconf.get("static_kpi_values")
                for kpi, value in static_kpi_values.items():
                    ref_testList[:, kpi] = value

        sum_distance_list = []
        for index, row in ref_testList.iterrows():
            if index == 0:
                sum_distance_list.append(0)
            else:
                last_value = sum_distance_list[index - 1]
   
                if last_value == -10:
                    search_index = index
                    while last_value == -10:
                        search_index = search_index - 1
                        if search_index >= 0 :
                            last_value = sum_distance_list[search_index]
                        else:
                            break
                    if search_index < 0:
                        sum_distance_list.append(0)
                    else:
                        last_row = ref_testList.loc[search_index]
                        last_lon = last_row["longitude"]
                        last_lat = last_row["latitude"]
                        lon = row["longitude"]
                        lat = row["latitude"]
   
                        sum_distance = self.__calculate_track_distance(last_lon, last_lat, lon, lat)
                        sum_distance_list.append(sum_distance)
#   
#                 elif row["position_error"] == -10:
#                     print("3*****************")
#                     sum_distance_list.append(-10)
                else:
                    last_row = ref_testList.loc[index - 1]
                    last_lon = last_row["longitude"]
                    last_lat = last_row["latitude"]
                    lon = row["longitude"]
                    lat = row["latitude"]
   
                    sum_distance = self.__calculate_track_distance(last_lon, last_lat, lon, lat)
                    sum_distance_list.append(sum_distance)
        ref_testList["mileage"] = sum_distance_list
         
        ERRORList = ref_testList.loc[:, ["UTC", 'mileage']]
 
        self.create_NMEAMileage_TABLE(testTable + "Mileage")
        for element in ERRORList.values:
            self.add_NMEA_Mileage_Data(testTable + "Mileage", element)
        self.commit()
        
    def __get_cno_l1l5_satellite_info(self, view_satellite_info, l5_view_satellite_info, cnType='top5'):
        l1_l5_top5_cno_list = []
        l1_l5_top5_cno_avar = 0
        view_satellite_dict = view_satellite_info.get_cno_satellite_info()
        l5_view_satellite_dict = l5_view_satellite_info.get_cno_satellite_info()
        if len(view_satellite_dict) != 0 and len(l5_view_satellite_dict) != 0:
            l5_view_satellite_list = sorted(l5_view_satellite_dict.items(), key=lambda x: x[1][-1], reverse=True)
            if len(l5_view_satellite_list) > 5 and cnType == 'top5':
                l5_view_satellite_list = l5_view_satellite_list[0:5]
            top5_cno_ids = [id[0] for id in l5_view_satellite_list]
            l1_l5_top5_cno_list += [[id] + view_satellite_dict[id] for id in top5_cno_ids if id in view_satellite_dict and view_satellite_dict[id][-1].isdigit()]
            l1_l5_top5_cno_avar = sum([float(value[-1]) for value in l1_l5_top5_cno_list]) / len(l1_l5_top5_cno_list)
        return l1_l5_top5_cno_list, l1_l5_top5_cno_avar
        
def dealSIMLog(resourceDBPath, simLogPath, higeoVersion, deviceInfo):
    PRINTI('dealSIMLog START')
    simLogDBPath = os.path.join(os.path.split(resourceDBPath)[0], higeoVersion + ".db")
    resourceDB = ActionDB(resourceDBPath)
    for deviceName, value in deviceInfo.items():
        if value.get("type") == "test":
            outputLogPath = os.path.join(simLogPath, higeoVersion, deviceName)
            simLogDB = GetResource2DB(simLogDBPath)
            ret = simLogDB.getHigeoSIMResource2DB(resourceDB, outputLogPath, deviceName)
            if ret[0] == -1:
                return False, ret[1]
    return True, ''


def check_is_valid_nmea_line(line):
    tag_count = line.count('$')
    if tag_count > 1:
        tag_first_index = line.find('$')
        tag_second_index = line.find('$', tag_first_index + 1)
        line = line[tag_second_index:]
    pattern = re.compile("\$.*\*\S*")
    nmea_line = pattern.search(line)
    if nmea_line is None:
        return False, None
    nmea_line = nmea_line.group()
    start_index = nmea_line.find("$")
    end_index = nmea_line.find("*")
    datas = nmea_line[start_index + 1 : end_index]
    check_value = nmea_line[end_index + 1:]
    if check_value.startswith('0') and len(check_value) > 1:
        check_value = check_value[1]

    checksum = 0
    for data in datas:
        data = ord(data)
        checksum = checksum ^ data
    checksum = hex(checksum).split("0x")[1].upper()
    if checksum == check_value.upper():
        return True, nmea_line
    else:
        return False, None


def ExitThread(code):
    PRINTE(code)
    sys.exit(code)

def isVaildID(ID):
    if ID is None or ID is "":
        return False
    else:
        return True

def encode(s):
    return ''.join([bin(ord(c)).replace('0b', '') for c in s])
if __name__ == "__main__":
    pattern = re.compile("\$G.GGA.*\*.*")
    print(hex(int(encode('0e'), 2)))
    t = '$GPRMC,121901.00,A,3114.5831,N,12130.2180,E,3.5,58.4,281117,0.0,E,A*0e'
    print(check_is_valid_nmea_line(t))
    # nmea_line = pattern.search(t)
    # if nmea_line:
    #     nmea_line = nmea_line.group()
    #     print nmea_line
    #     start_index = nmea_line.find("$")
    #     end_index = nmea_line.find("*")
    #     datas = nmea_line[start_index + 1 : end_index]
    #     check_value = nmea_line[end_index + 1:]
    #     checksum  = 0
    #     for data in datas:
    #         data = ord(data)
    #         checksum = checksum ^ data
    #     checksum = hex(checksum).split("0x")[1].upper()
    #     if checksum == check_value.upper():
    #         print("ccc",checksum)
    #
    #
    # else:
    #     print("not find")
