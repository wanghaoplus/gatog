# coding:utf-8
# coding:utf-8

import visa
import pyvisa
import threading
import time
import csv
import os
from aw.core.Input import SUC
from aw.core.Input import getLbsCaseLogPath, getCurCaseName


class Battery(object):
    current_value_list = []
    
    def __init__(self, ip):
        
        self.ip = "TCPIP::{}::INSTR".format(ip)
        self.visa_data = visa.ResourceManager()
        self.inst = self.visa_data.open_resource("TCPIP::10.100.5.112::INSTR")
        self.status = False
        
    def start_record_current(self):
        csvpath = os.path.join(getLbsCaseLogPath, getCurCaseName + '.csv')
        self.f = open(csvpath, 'w', 'a')
        self.csvWrite = csv.writer(self.f)
        self.status = True
        self.setSampCount()
        thd = threading.Thread(target=self.readCurrentFtch, args=(self.csvWrite))
        thd.setDaemon(True)
        thd.start()
        
        
    def getCurrentValue(self):
        i = 1
        end = time.time() + 10
        while time.time() < end:
            self.inst.write("READ?")
            VALUE = self.inst.read()
            i += 1
            print(VALUE)
        
            
    def write_command(self, command=None):
        self.status = False
        if command:
            ret = self.inst.write(command)
        return SUC, ret
    
    def setNplcDC(self, nplc = 0.2):
        '''
        @summary: 设置nplc
        @param nplc:设置的nplc
        '''
        cmd = 'CONF:CURR:DC'
        self.write_command(cmd)
        cmd = 'CURR:DC:NPLC %s' % nplc
        self.write_command(cmd)
    
    def setDCAccuracy(self, acc=0.1):
        '''
        @summary: 设置精度
        @param nplc:设置的精度值
        '''
        cmd = 'CONF:CURR:DC %s 0.001' % acc
        self.write_command(cmd)
        
    def uploadFileToPC(self, fileName):
        '''
        @summary: 下载文件到电脑
        @param fileName: 要下载的文件名
        '''
        
        cmd = r'MMEM:UPL? "USB:\%s.csv"' %  fileName
        now = time.localtime(time.time())
        ret = self.write_command(cmd)
        VALUE = self.inst.read()
        self.current_value_list.append(VALUE.split(',')[0:7])
        f = open(fileName + '.txt', 'w')
        f.write(VALUE)
        f.close
        print(len(VALUE.split(',')))
    
    def saveFileToUSB(self, fileName):
        '''
        @summary: 保存文件到USB
        @param fileName: 要下载的文件名
        '''
        import datetime
        now = time.localtime(time.time())
        cmd = r'MMEM:STOR:DATA RDG_STORE,"USB:\%s.csv"' %  fileName
        ret = self.write_command(cmd)
        print(ret)
    
    def setSampCount(self, COUNT=5000):
        '''
        @summary: 设置采集次数
        @param count:要采集的次数 
        '''
        ret = self.inst.write("SAMP:COUNT 5000")
        ret = self.inst.write("TRIG:COUNT 1")
        ret = self.inst.write("INIT")
        
    def readCurrentFtch(self, csvWrite):
        i = 0
        while self.status:
            ret = self.inst.write("R? 300")
            VALUE = self.inst.read()
            self.csvWrite.rows(VALUE.split(','))
            i += len(VALUE.split(','))
            print(len(VALUE.split(',')))
        print(i)    
        
    def stopReadCurrent(self):
        '''
        @summary: 停止连接
        '''
        self.status = False
        self.inst.close()
        self.visa_data.close()
        self.f.close()
        
        
if __name__=="__main__":
    rm = visa.ResourceManager()
    inst = rm.open_resource("TCPIP::192.168.1.103::INSTR")
    inst.set_visa_attribute(pyvisa.constants.VI_ATTR_TMO_VALUE, 2000000000)
    # inst.set_visa_attribute( pyvisa.constants.VI_ATTR_TMO_VALUE, pyvisa.constants.VI_TMO_INFINITE )
    # print( inst.get_visa_attribute( pyvisa.constants.VI_ATTR_TMO_VALUE) )

    for i in range(0,100000):
        inst.write("*idn?")
        str = inst.read()
        if ( len(str) < 16 ):
            raise Exception("error on %d" % (i) )
        # print( inst.read() )
    inst.close()
    rm.close()