# coding:utf-8
import sqlite3
import os
import traceback
import random
import time
from aw.utils.nmeanalysis.AresInput import PRINTI
from aw.utils.nmeanalysis.AresInput import PRINTE

class ActionDB(object):
    SHOW_SQL = False
    conn = None
    cu = None
    DBPath = None
    def __init__(self, DBPath):
        self.DBPath = DBPath
        self.conn = self.__get_conn()
        self.cu = self.__get_cursor()
        
    def __get_conn(self):
        '''获取到数据库的连接对象，参数为数据库文件的绝对路径
        如果传递的参数是存在，并且是文件，那么就返回硬盘上面改
        路径下的数据库文件的连接对象；否则，返回内存中的数据接
        连接对象'''
        try:
            conn = sqlite3.connect(self.DBPath)
            if os.path.exists(self.DBPath) and os.path.isfile(self.DBPath):
#                PRINTI('资源路径:[{}]'.format(self.DBPath))
                return conn
            PRINTI('资源路径:[:memory:]')
            return sqlite3.connect(':memory:')
        except:
            PRINTI('资源路径:[:memory:]')
            return sqlite3.connect(':memory:')
        
    def __get_cursor(self):
        '''该方法是获取数据库的游标对象，参数为数据库的连接对象
        如果数据库的连接对象不为None，则返回数据库连接对象所创
        建的游标对象；否则返回一个游标对象，该对象是内存中数据
        库连接对象所创建的游标对象'''
        return self.conn.cursor()
    
    
    ###############################################################
    ####            创建|删除表操作     START
    ###############################################################
    def drop_table(self, table):
        '''如果表存在,则删除表，如果表中存在数据的时候，使用该
        方法的时候要慎用！'''
        
        if table is not None and table != '':
            sql = 'DROP TABLE IF EXISTS "%s"' % table
            self.executeSQL(sql)
            self.commit()
        else:
            PRINTI('the [{}] is empty or equal None!'.format(table))
    
    def create_FT_TABLE(self, TABLE_NAME, cover=True):
        '''创建仿真使用的数据库表'''
        create_table_sql = '''CREATE TABLE `%s` (
                              `timestamp` VARCHAR,
                              `type` VARCHAR,
                              `list1` VARCHAR,
                              `list2` VARCHAR,
                              `list3` VARCHAR,
                              `list4` VARCHAR,
                              `list5` VARCHAR,
                              `list6` VARCHAR,
                              `list7` VARCHAR,
                              `list8` VARCHAR,
                              `list9` VARCHAR,
                              `list10` VARCHAR,
                              `list11` VARCHAR,
                              `list12` VARCHAR
                            )''' % TABLE_NAME
        if cover:
            self.drop_table(TABLE_NAME)
        self.executeSQL(create_table_sql)
        
    def add_FT_data(self, TABLE_NAME, data):
        '''写入一行数据到仿真表格中'''
        sql = '''INSERT INTO "%s" values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''' % TABLE_NAME
        if len(data) == 13 and type(data) == list:
            data.append("")
            self.executeSQL(sql, data)
        elif len(data) == 14:
            self.executeSQL(sql, data)
        else:
            PRINTE("youre input [{}] is wrong!".format(data))
            
        
    def create_HIGEO_Track_TABLE(self, TABLE_NAME, cover=True):
        '''创建higeo1.5 KML使用的数据库表'''
        create_table_sql = '''CREATE TABLE `%s` (
                              `timestamp` VARCHAR,
                              `type` VARCHAR,
                              `UTC` VARCHAR,
                              `list2` VARCHAR,
                              `list3` VARCHAR,
                              `list4` VARCHAR,
                              `list5` VARCHAR,
                              `list6` VARCHAR,
                              `list7` VARCHAR,
                              `list8` VARCHAR,
                              `list9` VARCHAR,
                              `list10` VARCHAR,
                              `list11` VARCHAR,
                              `list12` VARCHAR
                            )''' % TABLE_NAME
        if cover:
            self.drop_table(TABLE_NAME)
        self.executeSQL(create_table_sql)
        self.conn.commit()

    def add_HIGEO_Track_data(self, TABLE_NAME, data):
        '''写入一行数据到仿真表格中'''
        sql = '''INSERT INTO "%s" values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''' % TABLE_NAME
        if len(data) == 13 and type(data) == list:
            data.append("")
            self.executeSQL(sql, data)
        elif len(data) == 14:
            self.executeSQL(sql, data)
        else:
            PRINTE("youre input [{}] is wrong!".format(data))
            
    def create_HIGEO_Context(self, TABLE_NAME, cover=True):
        '''创建higeo1.5 KML使用的数据库表'''
        create_table_sql = '''CREATE TABLE `%s` (
                              `UTC` INT,
                              `flag` INT,
                              `phone_motion` INT,
                              `carrier_activity` INT,
                              `environmental` INT,
                              `fusion_model` INT,
                              `sensor_hub_AR` INT,
                              `wifiScanStatus` INT,
                              `pdr_enable` INT,
                              `vdr_enable` INT,
                              `wifi_enable` INT,
                            )''' % TABLE_NAME
        if cover:
            self.drop_table(TABLE_NAME)
        self.executeSQL(create_table_sql)
        self.conn.commit()
        
    def add_HIGEO_Context_data(self, TABLE_NAME, data):
        '''写入一行数据到仿真表格中'''
        sql = '''INSERT INTO "%s" values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''' % TABLE_NAME
        if len(data) == 11:
            self.executeSQL(sql, data)
        else:
            PRINTE("youre input [{}] is wrong!".format(data))
            
    def create_HIGEO_config(self, TABLE_NAME, cover=True):
        '''创建higeo1.5 仿真使用的数据库表'''
        create_table_sql = '''CREATE TABLE `%s` (
                              `systemTime` VARCHAR,
                              `higeo_log_level` INT,
                              `higeo_enable` INT,
                              `higeo_vdr_type` INT,
                              `higeo_vdr_always_on` INT,
                              `higeo_vdr_dead_reckoning_time` INT,
                              `higeo_pdr_enable` INT,
                              `higeo_pdr_dead_rockoning_time` INT,
                              `higeo_wifi_enable` INT,
                              `higeo_mm_enable` INT,
                              `quickttff_enable` INT,
                              `higeo_fusion_ver` VARCHAR,
                              `higeo_gps_vendor` VARCHAR
                            )''' % TABLE_NAME
        if cover:
            self.drop_table(TABLE_NAME)
        self.executeSQL(create_table_sql)
        self.conn.commit()
        
    def add_HIGEO_config_data(self, TABLE_NAME, data):
        '''写入一行数据到仿真配置表格中'''
        sql = 'INSERT INTO "%s" values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)' % TABLE_NAME
        if len(data) == 13:
            self.executeSQL(sql, data)
        else:
            PRINTE("youre input [{}] is wrong!".format(data))
            
    def create_HIGEO_vendor(self, TABLE_NAME, cover=True):
        '''创建higeo1.5 仿真使用的数据库表'''
        create_table_sql = '''CREATE TABLE `%s` (
                              `sensor_type` INT,
                              `sensor_vendor` VARCHAR
                            )''' % TABLE_NAME
        if cover:
            self.drop_table(TABLE_NAME)
        self.executeSQL(create_table_sql)
        self.conn.commit()
        
    def add_HIGEO_vendor_data(self, TABLE_NAME, data):
        '''写入一行数据到仿真配置表格中'''
        sql = 'INSERT INTO "%s" values (?, ?)' % TABLE_NAME
        if len(data) == 2:
            self.executeSQL(sql, data)
        else:
            PRINTE("youre input [{}] is wrong!".format(data))


    def create_HIGEO_QTTFF_TABLE(self, TABLE_NAME, cover=True):
        '''创建higeo1.5 KML使用的数据库表'''
        create_table_sql = '''CREATE TABLE `%s` (
                              `UTC` INT,
                              `longitude` DOUBLE,
                              `latitude` DOUBLE,
                              `speed` DOUBLE,
                              `heading` DOUBLE,
                              `pos_unc` DOUBLE,
                              `MatchedAP` INT,
                              `ScannedAP` INT,
                              `UsedAP` INT,
                              `ScanAge` INT,
                              `source` INT,
                              `LocationSource` INT,
                            )''' % TABLE_NAME
        if cover:
            self.drop_table(TABLE_NAME)
        self.executeSQL(create_table_sql)
        self.conn.commit()
        
    def add_HIGEO_QTTFF_data(self, TABLE_NAME, data):
        '''写入一行数据到仿真表格中'''
        sql = 'INSERT INTO "%s" values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)' % TABLE_NAME
        if len(data) == 11:
            self.executeSQL(sql, data)
        else:
            PRINTE("youre input [{}] is wrong!".format(data))
        
    def create_Track_TABLE(self, TABLE_NAME, cover=True):
        '''创建竞品/标准轨迹等 KML使用的数据库表'''
        create_table_sql = '''CREATE TABLE `%s` (
                              `UTC` INT,
                              `longitude` DOUBLE,
                              `latitude` DOUBLE,
                              `altitude` DOUBLE,
                              `speed` DOUBLE,
                              `heading` DOUBLE,
                              `pos_unc` DOUBLE,
                              `other` VARCHAR
                            )''' % TABLE_NAME
        if cover:
            self.drop_table(TABLE_NAME)
        self.executeSQL(create_table_sql)
        self.conn.commit()
        
    def add_Track_data(self, TABLE_NAME, data):
        '''写入一行竞品track数据到表格中，用于生成kml'''
        sql = 'INSERT INTO "%s" values (?, ?, ?, ?, ?, ?, ?, ?)' % TABLE_NAME
        if len(data) == 8:
            self.executeSQL(sql, data)
        else:
            PRINTE("youre input [{}] is wrong!".format(data))
            
    def create_NMEA_Info_Table(self, TABLE_NAME, cover=True):
        '''创建竞品/标准轨迹等 KML使用的数据库表'''
        create_table_sql = '''CREATE TABLE `%s` (
                              `UTC` VARCHAR,
                              `longitude` VARCHAR,
                              `latitude` VARCHAR,
                              `altitude` VARCHAR,
                              `speed` VARCHAR,
                              `heading` VARCHAR,
                              `UsedSV` VARCHAR,
                              `TOP5CN` VARCHAR,
                              `ACC` VARCHAR,
                              `HDOP` VARCHAR,
                              `VDOP` VARCHAR,
                              `PDOP` VARCHAR,
                              `GPSCount` VARCHAR,
                              `GLNCount` VARCHAR,
                              `GALCount` VARCHAR,
                              `BDSCount` VARCHAR,
                              `QZSCount` VARCHAR,
                              `SVCount` VARCHAR,
                              `GPSL5VCount` VARCHAR,
                              `QZL5VCount` VARCHAR,
                              `GAL5VCount` VARCHAR,
                              `GPSSACount` VARCHAR,
                              `GLNSACount` VARCHAR,
                              `GALSACount` VARCHAR,
                              `BDSSACount` VARCHAR,
                              `QZSACount` VARCHAR,
                              `SACount` VARCHAR,
                              `GPSL5ACount` VARCHAR,
                              `QZL5ACount` VARCHAR,
                              `GAL5ACount` VARCHAR,
                              `GPSSAList` VARCHAR,
                              `GLNSAList` VARCHAR,
                              `GALSAList` VARCHAR,
                              `BDSSAList` VARCHAR,
                              `QZSAList` VARCHAR,
                              `GPSL5List` VARCHAR,
                              `QZL5List` VARCHAR,
                              `GAL5AList` VARCHAR,
                              `GPSViewIDList` VARCHAR,
                              `GLNViewIDList` VARCHAR,
                              `GALViewIDList` VARCHAR,
                              `BDSViewIDList` VARCHAR,
                              `QZViewIDList` VARCHAR,
                              `GPSL5ViewIDList` VARCHAR,
                              `QZL5ViewIDList` VARCHAR,
                              `GAL5ViewIDList` VARCHAR,
                              `GPSViewTop5CNList` VARCHAR,
                              `GLNViewTop5CNList` VARCHAR,
                              `GALViewTop5CNList` VARCHAR,
                              `BDSViewTop5CNList` VARCHAR,
                              `QZViewTop5CNList` VARCHAR,
                              `GPSL5ViewTop5CNList` VARCHAR,
                              `GPSL1L5ViewTop5CNList` VARCHAR,
                              `QZL5ViewTop5CNList` VARCHAR,
                              `QZL1L5ViewTop5CNList` VARCHAR,
                              `GAL5ViewTop5CNList` VARCHAR,
                              `GAL1L5ViewTop5CNList` VARCHAR,
                              `GPSViewTop5CNAve` VARCHAR,
                              `GLNViewTop5CNAve` VARCHAR,
                              `GALViewTop5CNAve` VARCHAR,
                              `BDSViewTop5CNAve` VARCHAR,
                              `QZViewTop5CNAve` VARCHAR,
                              `GPSL5ViewTop5CNAve` VARCHAR,
                              `GPSL1L5ViewTop5CNAve` VARCHAR,
                              `QZL5ViewTop5CNAve` VARCHAR,
                              `QZL1L5ViewTop5CNAve` VARCHAR,
                              `GAL5ViewTop5CNAve` VARCHAR,
                              `GAL1L5ViewTop5CNAve` VARCHAR
                            )''' % TABLE_NAME
        if cover:
            self.drop_table(TABLE_NAME)
        self.executeSQL(create_table_sql)
        self.conn.commit()
        
    def add_NMEA_Info_data(self, TABLE_NAME, data):
        '''写入一行竞品track数据到表格中，用于生成kml'''
        sql = 'INSERT INTO "%s" values (?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)' % TABLE_NAME
        if len(data) == 68:
            self.executeSQL(sql, data)
        else:
            PRINTE("youre input [{}] is wrong!".format(data))
            
    def create_NMEAError_TABLE(self, TABLE_NAME, cover=True):
        '''创建report使用的数据库表'''
        create_table_sql = '''CREATE TABLE `%s` (
                              `UTC` INT,
                              `position_error` DOUBLE,
                              `alt_error` DOUBLE,
                              `speed_error` DOUBLE,
                              `heading_error` DOUBLE,
                              `shoot_error` DOUBLE,
                              `along_error` DOUBLE,
                              `across_error` DOUBLE,
                              `distance3D_error` DOUBLE
                            )''' % TABLE_NAME
        if cover:
            self.drop_table(TABLE_NAME)
        self.executeSQL(create_table_sql)
        self.conn.commit()
        
    def create_NMEAMileage_TABLE(self, TABLE_NAME, cover=True):
        '''创建report使用的数据库表'''
        create_table_sql = '''CREATE TABLE `%s` (
                              `UTC` INT,
                              `mileage` DOUBLE
                            )''' % TABLE_NAME
        if cover:
            self.drop_table(TABLE_NAME)
        self.executeSQL(create_table_sql)
        self.conn.commit()

    def add_NMEA_Mileage_Data(self, TABLE_NAME, data):

        '''写入一行数据到仿真表格中'''
        sql = 'INSERT INTO "%s" values (?, ?)' % TABLE_NAME
        if len(data) == 2:
            self.executeSQL(sql, data)
        else:
            PRINTE("youre input [{}] is wrong!".format(data))
        
    def add_NMEA_Error_Data(self, TABLE_NAME, data):
        '''写入一行数据到仿真表格中'''
        sql = 'INSERT INTO "%s" values (?, ?, ?, ?, ?,?,?,?,?)' % TABLE_NAME
        if len(data) == 9:
            self.executeSQL(sql, data)
        else:
            PRINTE("youre input [{}] is wrong!".format(data))

    def create_Error_TABLE(self, TABLE_NAME, cover=True):
        '''创建report使用的数据库表'''
        create_table_sql = '''CREATE TABLE `%s` (
                              `UTC` INT,
                              `position_error` DOUBLE,
                              `speed_error` DOUBLE,
                              `heading_error` DOUBLE,
                              `along_error` DOUBLE,
                              `cross_error` DOUBLE,
                              `shoot_error` DOUBLE
                            )''' % TABLE_NAME
        if cover:
            self.drop_table(TABLE_NAME)
        self.executeSQL(create_table_sql)
        self.conn.commit()
    
    def create_single_TABLE(self, TABLE_NAME, cover=True):
        '''创建report使用的数据库表'''
        create_table_sql = '''CREATE TABLE `%s` (
                              `Times` INT,
                              `StartTime` DOUBLE,
                              `FixTime` DOUBLE,
                              `Lat` DOUBLE,
                              `Lon` DOUBLE,
                              `Alt` DOUBLE,
                              `FixFlag` INT,
                              `firstFixTTFF` DOUBLE,
                              `firstFixCep2D` DOUBLE,
                              `firstFixCep3D` DOUBLE,
                              `firstFixCepAlt` DOUBLE,
                              `firstFixStartUTC` INT,
                              `firstFixUTC` INT
                            )''' % TABLE_NAME
        if cover:
            self.drop_table(TABLE_NAME)
        self.executeSQL(create_table_sql)
        self.conn.commit()
        
    def add_Error_data(self, TABLE_NAME, data):
        '''写入一行数据到仿真表格中'''
        sql = 'INSERT INTO "%s" values (?, ?, ?, ?, ?, ?, ?)' % TABLE_NAME
        if len(data) == 7:
            self.executeSQL(sql, data)
        elif len(data) == 4:
            data += ["", "", ""]
            self.executeSQL(sql, data)
        else:
            PRINTE("youre input [{}] is wrong!".format(data))
    
    def get_dynamic_single_data(self, test_device, fixUTCtime):
        sql = 'select  longitude, latitude, altitude from novatel where UTC ={fixUTCtime}'.format(test_device=test_device, fixUTCtime=fixUTCtime)
        return self.__fetchdata(sql)
    
    def add_single_data(self, TABLE_NAME, data):
        '''写入一行单点定位数据到表格中'''
        sql = 'INSERT INTO "%s" values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)' % TABLE_NAME
        if len(data) == 13:
            self.executeSQL(sql, data)
        elif len(data) == 4:
            data += ["", "", ""]
            self.executeSQL(sql, data)
        else:
            PRINTE("youre input [{}] is wrong!".format(data))
            
            
    def __fetchdata(self, sql, *args):
        '''查询所有数据'''
        try:
            if sql is not None and sql != '':
                if self.SHOW_SQL:
                    print('执行sql:[{}]'.format(sql))
                self.cu.execute(sql, args)
                return self.cu.fetchall()
            else:
                PRINTE('the [{}] is empty or equal None!'.format(sql))
                return []
        except Exception as e:
            raise e
            
    
    
    def fetchall(self, TABLE_NAME):
        '''查询所有数据...'''
        sql = '''SELECT * FROM "%s"''' % TABLE_NAME
        return self.__fetchdata(sql)
    
    def fetchone(self, TABLE_NAME, key, value):
        '''查询一条记录...'''
        sql = 'SELECT * FROM "{}" WHERE {} = ? '.format(TABLE_NAME, key)
        return self.__fetchdata(sql, value)

    def executeSQL(self, sql, *arg):
        '''执行sql语句：'''
        if sql is not None and sql != '':
            if self.SHOW_SQL:
                PRINTI('执行sql:[{}]'.format(sql))
            for i in [0, 1, 2]:
                try:
                    self.cu.execute(sql, *arg)
                    return
                except sqlite3.OperationalError:
                    time.sleep(random.random())
                    if (i == 2):
                        PRINTE('执行sql:[{}] Error'.format(sql))
                        PRINTE(traceback.format_exc())
                except:
                        PRINTE('执行sql:[{}] Error'.format(sql))
                        PRINTE(traceback.format_exc())
        else:
            PRINTI('the [{}] is empty or equal None!'.format(sql))
    
    def getcolomFormDB(self, tableName, colList=None, startTime=None, endTime=None):
        try:
            sql = "SELECT "
            if not colList:
                sql = "SELECT * FROM '{}'".format(tableName)
            elif len(colList) == 1 and type(colList) == list:
                sql = "SELECT {} FROM '{}'".format(colList[0], tableName)
            elif len(colList) > 1 and type(colList) == list:
                sql = "SELECT {}".format(colList[0])
                for element in colList[1:]:
                    sql = sql + "," + element
                sql += " FROM '{}'".format(tableName)
            elif type(colList) == str:
                sql = "SELECT {} FROM '{}'".format(colList, tableName)
            filsql = []
            if startTime:
                filsql.append(" UTC >= \'%s\' " % startTime)
            if endTime:
                filsql.append(" UTC <= \'%s\' " % endTime)

            if len(filsql) > 0:
                sql += ' where ' + ' and '.join(filsql)
            tuplist = self.__fetchdata(sql)
            out = []
            for element in tuplist:
                out.append(list(element))
            return out
        except Exception as e:
            raise e
    
    def getFixNum(self, test_device, startTime=None, endTime=None):
        sql = "select count(UTC) from {test_device} where UTC>= '{startTime}' and UTC <= '{endTime}';".format(test_device=test_device, startTime=startTime, endTime=endTime)
        return self.__fetchdata(sql)
    
    def getFixMaxTime(self, test_device):
        sql = "select max(UTC) from {test_device}".format(test_device=test_device)
        return self.__fetchdata(sql)
            
        
    def getRows(self, tableName, offset=0, getLines=100000):
        sql = '''select * from "{}" where rowid between {} and {}'''.format(tableName, getLines * offset, getLines * (offset + 1))
        return self.__fetchdata(sql)
            
        
    def getCountOfTable(self, tableName, getLines=100000):
        import math
        sql = '''select count(*) from "{}"'''.format(tableName)
        self.cu.execute(sql)
        temp = self.cu.fetchone()
        return int(math.ceil(float(temp[0]) / getLines))
        
    

    def commit(self):
        self.conn.commit()
            
    def closeall(self):
        try:
            if self.cu is not None:
                self.cu.close()
                self.cu = None
        finally:
            if self.conn is not None:
                self.conn.close()
                self.conn = None
            
    def __del__(self):
        self.closeall()

if __name__ == '__main__':
    start = time.time()
    dbpath = r"C:\Users\z00285085\Desktop\Resource0823.db"
    testdb = ActionDB(dbpath)
    testdb.getRows("ALPFT", 22)
    print(time.time() - start)
    
