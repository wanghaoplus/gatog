# coding:utf-8


import os, time, sys
import traceback
from aw.utils.nmeanalysis.GetResource2DB import GetResource2DB
from aw.utils.nmeanalysis.AresInput import PRINTI
from aw.utils.nmeanalysis.AresInput import PRINTE
from aw.utils.nmeanalysis.AresInput import DT_FAIL
from aw.utils.nmeanalysis.AresInput import DT_SUC
from aw.utils.nmeanalysis.AresInput import LBSDector
from aw.utils.nmeanalysis.creatHigeo2KML import createKML
from aw.utils.nmeanalysis.AnalyzeModule import analyze_main
from aw.core.Input import isSuc
print(sys.argv[1:])
reportPath = r"D:\NmeanalysisReport\%s" % time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
if sys.argv[1:]:
    casePath = sys.argv[1]
    sceneId =sys.argv[2]
    reportPath = os.path.join(casePath, sceneId)
print(reportPath)
if not os.path.exists(reportPath):
        os.makedirs(reportPath)


class AnalyzeNMEA(object):
    def __init__(self, dbPath, config):
        self.dbPath = dbPath
        db_file_path = os.path.join(self.dbPath, "logDB")
        if not os.path.exists(db_file_path):
            os.makedirs(db_file_path)
        db_path = os.path.join(db_file_path , 'lbs.db')
        self.write2db = GetResource2DB(db_path, config)
        
    @staticmethod
    def getAnalyzeNMEAObj(pwd, *arg):
        AnalyzeNMEA.checkLicense(pwd)
        return AnalyzeNMEA(*arg)
    
    @staticmethod
    def checkLicense(pwd):
        return

    @LBSDector(True)
    def getKmz2DB(self, devceInfo):
        try:
            for value in devceInfo:
                if value.get("tech", None) == "novatel" and value.get("type", None) == "standard":
                    file_path = value["file_path"]
                    timeZone = value["timeZone"]
                    if file_path.endswith('.kmz'):
                        self.write2db.getNovatelKmz2DB(file_path, timeZone)
                    elif file_path.endswith('.txt'):
                        self.write2db.getNMEA2DB(file_path, 'novatel', timeZone)
                    return DT_SUC, ""
            return DT_FAIL, "can, not find novatel log file"
        except:
            return DT_FAIL, traceback.format_exc()
    
    @LBSDector(True)
    def getDevicesNMEA2DB(self, deviceInfo):
        try:
            removeDevice = []
            for device in deviceInfo:
                devicename = device.get("tech", "")
                feature = device["feature"]
                type = device["type"]
                nmea_path = device["file_path"]
                timeZone = device.get("timeZone", 0)
                if feature == "nmea" and type != "standard" and devicename != "":
                    try:
                        self.write2db.getNMEA2DB(nmea_path, devicename, timeZone)
                        self.write2db.writeNMEATrackError(devicename)
                    except:
                        removeDevice.append(device)
                        PRINTE("the device[%s] get data error" % devicename)
                        PRINTE(traceback.format_exc())
                        continue
                else:
                    PRINTI("feature[%s], type[%s], devicename[%s]" % (feature, type, devicename))
            if removeDevice:
                for device in removeDevice:
                    deviceInfo.remove(device)
                if not deviceInfo :
                    return  DT_FAIL, 'fail'
            return DT_SUC, ""
        except:

            return DT_FAIL, traceback.format_exc()
    
    def getDevicesSingleLocationDB(self, config, deviceInfo):
        
        self.write2db.writeDevicesSingleDynamicLocationDB(config, deviceInfo)
        pass
        
    def setConfig(self, testlog, timeZone=0, feature="nmea", mtype="test"):
        if not isinstance(testlog, list):
            return DT_FAIL, "入参错误"
        if len(testlog) == 0:
            return DT_FAIL, "没有生成nmealog"
        deviceslist = []
        for filepath in testlog:
            devicename = filepath.split("_")[-1]
            filepath = os.path.join(filepath, "Ares_LBS_NMEA.txt")
            deviceinfo = {"timeZone": timeZone,
                     "feature": feature,
                     "type": mtype,
                     "tech": devicename,
                     "file_path": filepath}
            deviceslist.append(deviceinfo)
        return DT_SUC, deviceslist
    
def analysis_nmea(reportPath, config, testlog):
    db_path = os.path.join(reportPath, "logDB", 'lbs.db')
    analyze = AnalyzeNMEA(reportPath, config)
#     ret = analyze.setConfig(testlog)
#     print('2222', ret)
#     if ret[0] != DT_SUC:
#         return ret
    deviceInfo = config['deviceInfo']
    print(deviceInfo)
    analyze.getKmz2DB(deviceInfo)
    isSuc(analyze.getDevicesNMEA2DB(deviceInfo))
    if (config['is_need_single_analysis'] == True) and (os.path.exists(config['singleReportPath'])):
        analyze.getDevicesSingleLocationDB(config, deviceInfo)
    if os.path.exists(db_path):
        createKML(db_path, os.path.join(reportPath, 'report'), deviceInfo)
    print(deviceInfo)
    config['deviceInfo'] = deviceInfo
    return analyze_main(reportPath, config)

def aw_analy_checkKPI(test, standard, KPI='PositionYield'):
    if float(test[KPI]) > float(standard):
        return DT_FAIL, {'test':test[KPI], 'standard':standard}
    return DT_SUC, {'test':test[KPI], 'standard':standard}


def main():
    from aw.utils.nmeanalysis.config import config
    analysis_nmea(reportPath, config, 'testlog')
    
        
if __name__ == "__main__":
    
    import datetime
    import time
    import sys
    
    main()
    
    
    
    
