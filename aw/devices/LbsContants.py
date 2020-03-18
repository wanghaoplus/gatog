#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/24 21:48
# @Author  : shaochanghong
# @Site    : 
# @File    : LbsContants.py
# @Software: PyCharm

import struct

class CMD(object):

    class HDBD():
        # cold start 
        CMD_COLD_START = b'\xF1\xD9\x06\x40\x01\x00\x01\x48\x22'
        CMD_WARM_START = bytes.fromhex('F1 D9 06 40 01 00 02 49 23')
        CMD_HOT_START = bytes.fromhex('F1 D9 06 40 01 00 03 4A 24')
        SLEEP_1S=bytes.fromhex('F1 D9 06 42 14 00 02 FF 32 00 E8 03 00 00 00 00 00 00 00 00 00 00 00 00 00 00 7A 7C')
        SLEEP_EXIT=bytes.fromhex('F1 D9 06 42 14 00 00 FF 32 00 E8 03 00 00 00 00 00 00 00 00 00 00 00 00 00 00 78 54')
        SET_GPS_L1 = bytes.fromhex('F1 D9 06 0C 04 00 01 00 00 00 17 A0')
        SAVE_DEBUG_CONFIG = bytes.fromhex('F1 D9 06 09 08 00 00 00 00 00 2F 00 00 00 46 B7')
        
        POWER_OFF_ALL = bytes.fromhex('F1 D9 06 20 02 00 10 00 38 EC')
        POWER_ON = bytes.fromhex('F1 D9 06 20 02 00 10 11 49 FD')
        
        POWER_MAIN_OFF = bytes.fromhex('F1 D9 06 20 02 00 10 10 48 FC')
    
    class UBLOX():
        CMD_COLD_START = b'\xb5\x62\x06\x04\x04\x00\xff\xff\x02\x79\x87\xda'
        CMD_HOT_START = b'\xb5\x62\x06\x04\x04\x00\x00\x00\x02\x79\x89\xe1'
        
    class BRCM():
        CMD_COLD_START = ''
        
    class SONY():
        CMD_COLD_START = '@GCD\r\n'.encode()
        
        
    class MTK():
        CMD_COLD_START = '$PMTK104*37'.encode()
        CMD_HOT_START = '$PMTK101*32'.encode()
        CMD_WARM_START = '$PMTK102*31'.encode()
        
    # 二进制校验
    def binary_gen_crc(self, src_data):
        checksum1 = 0
        checksum2 = 0
        length = len(src_data)
        for i in range(0, length):
            checksum1 += src_data[i]
            checksum2 += checksum1
        checksum2 &= 0xFF
        result = ((checksum1 << 8) + checksum2) & 0xFFFF
        return result
    
    # 设置sleep时间，模式
    def sleepCommand(self, sleepType , slpDelayTime=0):
        if(sleepType != 'Sleep' and sleepType != 'Deep' and  sleepType != 'MianPowerDown' and sleepType != 'RTCStandOnly'):
            return
        send_data = bytearray(13)
        send_data[0] = 0xF1
        send_data[1] = 0xD9
        send_data[2] = 0x06
        send_data[3] = 0x41
        send_data[4] = 0x05
        send_data[5] = 0x00
    
        send_data[6] = (slpDelayTime >> 0) & (0xFF)
        send_data[7] = (slpDelayTime >> 8) & (0xFF)
        send_data[8] = (slpDelayTime >> 16) & (0xFF)
        send_data[9] = (slpDelayTime >> 24) & (0xFF)
    
        if sleepType == 'Sleep':
            send_data[10] = 0x00
        elif sleepType == 'Deep':
            send_data[10] = 0x01
        elif sleepType == 'MainPowerDown':
            send_data[10] = 0x03
        elif sleepType == 'RTCStandOnly':
            send_data[10] = 0x04
    
        crc = self.binary_gen_crc(send_data[2:11])
        send_data[11] = (crc >> 8) & 0xFF
        send_data[12] = crc & 0xFF
    
        return (bytes(send_data))
    
    # 设置波特率
    def setBaudrate(self, port, baud):
        if port != 0 and port != 1:
            return -1
    
        send_data = bytearray(16)
        send_data[0] = 0xF1
        send_data[1] = 0xD9
        send_data[2] = 0x06
        send_data[3] = 0x00
        send_data[4] = 0x08
        send_data[5] = 0x00
    
        if port == 1:
            send_data[6] = 0x01
        elif port == 0:
            send_data[6] = 0x00
    
        send_data[7] = 0x00
        send_data[8] = 0x00
        send_data[9] = 0x00
    
        send_data[10] = (baud >> 0) & (0xFF)
        send_data[11] = (baud >> 8) & (0xFF)
        send_data[12] = (baud >> 16) & (0xFF)
        send_data[13] = (baud >> 24) & (0xFF)
    
        crc = self.binary_gen_crc(send_data[2:14])
        send_data[14] = (crc >> 8) & 0xFF
        send_data[15] = crc & 0xFF
    
        return (bytes(send_data))

    # AGNSS 位置注入
    def AGNSSPos(self, lat, lon, hgt, posType = 'LLA'):
        '''
        Wanghao 20200313
        :param lat: 纬度
        :param lon: 精度
        :param hgt: 高程
        :param posType: 坐标类型，默认为LLA
        '''
        if lat < 0 or lon < 0:
            return 0

        lat16 = (int(lat * 10 ** 7))
        lon16 = (int(lon * 10 ** 7))
        if hgt >= 0:
            hgt16 = (int(hgt * 100))
        else:
            hgt16 = (((1 << 32) - 1) & int(hgt * 100))#补码

        send_data = bytearray(25)
        send_data[0] = 0xF1
        send_data[1] = 0xD9
        send_data[2] = 0x0B
        send_data[3] = 0x10
        send_data[4] = 0x11
        send_data[5] = 0x00

        if posType == "LLA":
            send_data[6] = 0x01
        elif posType == "ECEF":
            send_data[6] = 0x00

        send_data[7] = (lat16 >> 0) & (0xFF)
        send_data[8] = (lat16 >> 8) & (0xFF)
        send_data[9] = (lat16 >> 16) & (0xFF)
        send_data[10] = (lat16 >> 24) & (0xFF)

        send_data[11] = (lon16 >> 0) & (0xFF)
        send_data[12] = (lon16 >> 8) & (0xFF)
        send_data[13] = (lon16 >> 16) & (0xFF)
        send_data[14] = (lon16 >> 24) & (0xFF)

        send_data[15] = (hgt16 >> 0) & (0xFF)
        send_data[16] = (hgt16 >> 8) & (0xFF)
        send_data[17] = (hgt16 >> 16) & (0xFF)
        send_data[18] = (hgt16 >> 24) & (0xFF)

        send_data[19] = 0x00
        send_data[20] = 0x00
        send_data[21] = 0x00
        send_data[22] = 0x00

        crc = self.binary_gen_crc(send_data[2:23])
        send_data[23] = (crc >> 8) & 0xFF
        send_data[24] = crc & 0xFF

        #print(send_data)
        return (bytes(send_data))

    # AGNSS 时间注入
    def AGNSSTime(self, aLeapSecond, year, mouth, day, hour, minute, second, secNs=0, taccS=0, taccNs=0, timeType = "UTC"):
        '''
        :param aLeapSecond: 闰秒
        :param year:    年
        :param mouth:   月
        :param day:     日
        :param hour:    时
        :param minute:  分
        :param second:  秒
        :param secNs:   秒小数位
        :param taccS:   时间精度，一般为0
        :param taccNs:  时间精度小数位，一般0
        :param timeType: 时间模式，一般为 UTC
        :return:
        '''
        secNs16 = (int(secNs * 10 ** 9))
        taccNs16 = (int(taccNs * 10 ** 9))

        send_data = bytearray(28)
        send_data[0] = 0xF1
        send_data[1] = 0xD9
        send_data[2] = 0x0B
        send_data[3] = 0x11
        send_data[4] = 0x14
        send_data[5] = 0x00

        if timeType == "TOW":
            send_data[6] = 0x01
        elif timeType == "UTC":
            send_data[6] = 0x00

        send_data[7] = 0x00  # reserved
        send_data[8] = aLeapSecond
        send_data[9] = (year >> 0) & (0xFF)
        send_data[10] = (year >> 8) & (0xFF)
        send_data[11] = mouth
        send_data[12] = day
        send_data[13] = hour
        send_data[14] = minute
        send_data[15] = int(second)
        send_data[16] = (secNs16 >> 0) & (0xFF)
        send_data[17] = (secNs16 >> 8) & (0xFF)
        send_data[18] = (secNs16 >> 16) & (0xFF)
        send_data[19] = (secNs16 >> 24) & (0xFF)
        send_data[20] = (taccS >> 0) & (0xFF)
        send_data[21] = (taccS >> 8) & (0xFF)
        send_data[22] = (taccNs16 >> 0) & (0xFF)
        send_data[23] = (taccNs16 >> 8) & (0xFF)
        send_data[24] = (taccNs16 >> 16) & (0xFF)
        send_data[25] = (taccNs16 >> 24) & (0xFF)

        crc = self.binary_gen_crc(send_data[2:26])
        send_data[26] = (crc >> 8) & 0xFF
        send_data[27] = crc & 0xFF

        #print(send_data)
        return (bytes(send_data))


    # 设置debuginfo打开关闭
    @staticmethod
    def setDebugInfo(mode):
        if mode == 'open':
            return b'\xF1\xD9\x02\x01\x01\x00\x01\x05\x12'
        elif mode == 'close':
            return b'\xF1\xD9\x02\x01\x01\x00\x00\x04\x11'

DEVICE_CMD = {'hdbd':CMD.HDBD,
            'ublox':CMD.UBLOX,
            'brcm':CMD.BRCM,
            'sony':CMD.SONY}


if __name__ == '__main__':
    cmd = CMD()
    temp = ' ' + 'F1 D9 06 40 01 00 01 48 22'
    print(b'\xb5\x62\x06\x04\x04\x00\xff\xff\x02\x79\x87\xda')
    print(bytes(temp.replace(' ', '\\x'),  encoding = "utf8"))
#     print(type(bytes(str_binary('F1 D9 06 40 01 00 01 48 22')), encoding = "utf8"))
#     print(type(b'\xF1\xD9\x02\x01\x01\x00\x00\x04\x11'))
