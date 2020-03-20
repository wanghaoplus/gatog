#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2020/2/24 21
# @Author  : wanghao
# @Site    :
# @File    : UserModeFWUpgrade.py

import os
import os.path
import sys
import array
import binascii
import serial
import time
import sys
import random
import hashlib
import gzip
#from usb_Interface import *

dut_port = 3

cmdMONVER = [0xf1, 0xd9, 0x0a, 0x04, 0x00, 0x00, 0x0e, 0x34]
cmdSETFRQ = [0xf1, 0xd9, 0xf4, 0x00, 0x04, 0x00, 0x80, 0xba, 0x8c, 0x01, 0xbf, 0xff]
cmdBOOTERASE_8020 = [0xf1, 0xd9, 0xf4, 0x05, 0x06, 0x00, 0x00, 0x00, 0x00, 0x90, 0x00, 0x00, 0x8f, 0x95]
cmdBOOTERASE_8040 = [0xf1, 0xd9, 0xf4, 0x05, 0x06, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x0f, 0x25]
cmdCFGRST = [0xf1, 0xd9, 0x06, 0x40, 0x01, 0x00, 0x00, 0x47, 0x21]
cmdBOOTBAUD = [0xf1, 0xd9, 0xf4, 0x03, 0x08, 0x00, 0x00, 0xc2, 0x01, 0x00, 0x00, 0xc2, 0x01, 0x00, 0x85, 0x7d]
cmdFLASHUNLOK = [0xF1, 0xD9, 0xF4, 0x08, 0x04, 0x00, 0x00, 0x02, 0x00, 0x80, 0x82, 0x76]

# 鍙戦�佹寚浠ゅ嚱鏁�
def send_command(port, cmd):
    port.write(cmd)


# BOOT妯″紡鍙戦��
def sendfwboot(port, addr, cnt, data, lenth):
    cmd = [0xF1, 0xD9, 0xF4, 0x05, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    ck = [0, 0]
    ck1 = 0
    ck2 = 0
    lenth_full = lenth + 6
    cmd[4] = lenth_full & 0xFF
    cmd[5] = (lenth_full >> 8) & 0xFF
    cmd[6] = addr & 0xFF
    cmd[7] = (addr >> 8) & 0xFF
    cmd[8] = (addr >> 16) & 0xFF
    cmd[9] = (addr >> 24) & 0xFF
    cmd[10] = cnt & 0xFF
    cmd[11] = (cnt >> 8) & 0xFF
    temp = len(data)
    # 璁＄畻鏍￠獙鍜�
    for i in range(0, 12):
        if (i > 1):
            ck1 += cmd[i]
            ck2 += ck1

    for i in range(0, lenth):
        ck1 += data[i]
        ck2 += ck1

    ck[0] = ck1 & 0xFF
    ck[1] = ck2 & 0xFF

    port.write(cmd)
    port.write(data)
    port.write(ck)


# BOOT 升级协议及升级
def fw_update_boot(port, data, lenth, address):
    progress_status = 0
    count = int(lenth / 1024)
    for i in range(1, count):
        sendfwboot(port, address + i * 0x400, i, data[i * 1024:(i + 1) * 1024], 1024)
        time.sleep(0.01)
        recv = port.read(10)
#        print(str(recv))
        percentage_done = int((10*i/count))%10
        if(percentage_done > progress_status):
            progress_status = percentage_done
            print(str(percentage_done*10)+"%")
    last = count * 1024
    sendfwboot(port, address + count * 0x400, count, data[last: lenth], lenth - last)
    recv = port.read(10)
    print(str(100)+"%")
#    print(str(recv))
    count += 1
    sendfwboot(port, address, count, data[0:1024], 1024)
    recv = port.read(10)
#    print(str(recv))

    send_command(port, cmdCFGRST)
    send_command(port, cmdBOOTBAUD)


# Load a file image to buffer
def read_into_buffer(filename):
    buf = bytearray(os.path.getsize(filename))
    with open(filename, 'rb') as f:
        f.readinto(buf)
    return buf

def terminate_program(msg, val):
    print(msg)
    sys.exit(val)


#主函数
def BootModeFWUpgrade(dut_port, device, path ):

    cyfm_file = read_into_buffer(path)
    
    if dut_port < 0:
        return -1

    if device == "8020":
        address = 0x90000000
        cmdBOOTERASE = cmdBOOTERASE_8020

    if device == "8040":
        address = 0x100000
        cmdBOOTERASE = cmdBOOTERASE_8040

    dut_port = int(dut_port)
    comport = serial.Serial("COM" + str(dut_port), 115200, timeout=60)

    if (cyfm_file[0] != 0x0A or cyfm_file[1] != 0x11):
        terminate_program("Fail, cyfm file invalid: 01", 1)
    out = open("temp_file", "wb")
    out.write(cyfm_file[12:])  # extract .gz file
    out.close()

    # wait for file closed
    while (out.closed == False):
        pass
    print("File closed")

    try:
        with gzip.open("temp_file", 'rb') as f:
            file_content = bytearray(f.read())
    except:
        terminate_program("Fail, cyfm file invalid: 02", 1)

    # verify MD5
    file_md5 = hashlib.md5(file_content[16:]).digest()
    if (file_md5 != file_content[0:16]):
        terminate_program("Fail, cyfm file invalid: 03", 1)

    print("Verify MDS")
    firmware_file = list(file_content[16:])  # firmware to be loaded
    firmware_length = len(firmware_file)
    f.close()
    # wait for file closed
    while (f.closed == False):
        pass
    os.remove("temp_file")

    # 鍙戦�丮ONVER
    send_command(comport, cmdMONVER)
    time.sleep(0.02)
    print("MONVER")

    #FLASH瑙ｉ攣
    send_command(comport, cmdFLASHUNLOK)
    time.sleep(0.1)
    print("Flash unlock")
    # 鍙戦�丼ETFRQ
    send_command(comport, cmdSETFRQ)
    time.sleep(0.02)
    print("Set frequency")
    # 鍙戦�丅OOTERASE
    send_command(comport, cmdBOOTERASE)
    time.sleep(0.2)
    print("Boot erase")


    comport.reset_input_buffer()
    comport.reset_output_buffer()

    fw_update_boot(comport, firmware_file, firmware_length, address)
    comport.close()
    terminate_program("Firmware download completed!", 0)
    
    return 0
    
if __name__ == '__main__':
    
    path = "D:\\app_GPS_BD_5887f64c1.cyfm"
    device = '8040'

    BootModeFWUpgrade(3, device, path)


    