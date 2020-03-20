#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2020/2/19 14:19
# @Author  : wanghao
# @Site    :
# @File    : UserModeFWUpgrade.py

import os
import os.path
import serial
import time
import hashlib
import gzip

enDebug = True

cmdMONVER = [0xf1, 0xd9, 0x0a, 0x04, 0x00, 0x00, 0x0e, 0x34]
cmdNMEAOFF = [0xf1, 0xd9, 0x06, 0x01, 0x03, 0x00, 0xf0, 0x00, 0x00, 0xfa, 0x0f,
              0xf1, 0xd9, 0x06, 0x01, 0x03, 0x00, 0xf0, 0x02, 0x00, 0xfc, 0x13,
              0xf1, 0xd9, 0x06, 0x01, 0x03, 0x00, 0xf0, 0x03, 0x00, 0xfd, 0x15,
              0xf1, 0xd9, 0x06, 0x01, 0x03, 0x00, 0xf0, 0x04, 0x00, 0xfe, 0x17,
              0xf1, 0xd9, 0x06, 0x01, 0x03, 0x00, 0xf0, 0x05, 0x00, 0xff, 0x19,
              0xf1, 0xd9, 0x06, 0x01, 0x03, 0x00, 0xf0, 0x06, 0x00, 0x00, 0x1b,
              0xf1, 0xd9, 0x06, 0x01, 0x03, 0x00, 0xf0, 0x07, 0x00, 0x01, 0x1d]
cmdCFGFWUP = [0xf1, 0xd9, 0x06, 0x50, 0x01, 0x00, 0x10, 0x67, 0x71, 0x00]
cmdCFGPRT = [0xf1, 0xd9, 0x06, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xc2, 0x01, 0x00, 0xd1, 0xe0]
cmdACKACK = [0xf1, 0xd9, 0x06, 0x40, 0x01, 0x00, 0x00, 0x47, 0x21]

data1st = [
           0x67, 0x6e, 0x73, 0x73, 0x32, 0x36, 0x72, 0x65, 0x6c, 0x31, 0x36, 0x2e, 0x67, 0x7a, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

datalast = [0] * 128


# 发送指令函数
def sendCommand(port, cmd):
    port.write(cmd)


def cal_crc(data, lenth):
    crc = int()
    crc = 0
    for i in range(0, lenth):
        crc = crc ^ (data[i] << 8)
        for j in range(0, 8):
            if ((crc & 0x8000) != 0):
                crc = crc << 1 ^ 0x1021
            else:
                crc = crc << 1

    return (crc & 0xFFFF)


# Ymodem
def userSendFW(port, cmd, cnt, data, lenth):
    if (lenth!=1024) and (lenth!=128):
        flag = 1
        lenth_tmp = 1024
    else:
        flag = 0
        lenth_tmp = lenth
    send_data = bytearray(lenth_tmp + 3)
    send_data[0]=cmd
    send_data[1]=cnt&0xFF
    send_data[2]= 0xFF - (cnt & 0xFF)
    write_ptr = 3
    for i in range(0, lenth):
        send_data[write_ptr] = data[i]
        write_ptr += 1
    if flag==1:
        for i in range(lenth, lenth_tmp):
            send_data[write_ptr] = 0x1a
            write_ptr += 1
    crc16 = cal_crc(send_data[3:], lenth_tmp)
    # crc
    send_data.append((crc16>>8)&0xFF)
    send_data.append(crc16&0xFF)
    sendCommand(port, send_data)


# user固件烧写  Y
def userFWUpdate(port, data, lenth):
    if enDebug:
        print("lenth = ", type(lenth))
        print(lenth)
    count = int(lenth / 1024)
    if enDebug:
        print("count = ", count)
    userSendFW(port, 0x01, 0x00, data1st, 128)##########################
    recv = port.read(7)#######################################
    print("recv", str(recv))

    if enDebug:
        time.sleep(0)
    for i in range(1, count+1):
        userSendFW(port, 0x02, i, data[(i - 1) * 1024:(i) * 1024], 1024) #################
        recv = port.read(1)#######################
        print(str(recv))
        print("i = ", i)
    last = count * 1024
    print("the last data")
    userSendFW(port, 0x02, (count+1), data[last: lenth], lenth - last)####################
    time.sleep(0.05)
    recv = port.read(1)#######################
    print(str(recv))
    ymodem_eot_cmd = "04"
    sendCommand(port, bytearray.fromhex(ymodem_eot_cmd))######################
    userSendFW(port, 0x01, 0, datalast, 128)###################
    time.sleep(0.05)
    recv = port.read(1)#######################
    print(str(recv))


# Load a file image to buffer
def read_into_buffer(filename):
    buf = bytearray(os.path.getsize(filename))
    with open(filename, 'rb') as f:
        f.readinto(buf)
    return buf


def analysisImg(cyfm_file):
    if (cyfm_file[0] != 0x0A or cyfm_file[1] != 0x11):
        print("Fail, cyfm file invalid: 01")
        return -1
    out = open("temp_file", "wb")
    out.write(cyfm_file[12:])  # extract .gz file
    out.close()
    # wait for file closed
    while (out.closed == False):
        pass
    print("File closed")
    #Gzip img
    try:
        with gzip.open("temp_file", 'rb') as f:
            file_content = bytearray(f.read())
            f.close()
            while (f.closed == False):
                pass
    except:
        print("Fail, cyfm file invalid: 02")
        return -1
    # verify MD5
    file_md5 = hashlib.md5(file_content[16:]).digest()
    if (file_md5 != file_content[0:16]):
        print("Fail, cyfm file invalid: 03")
        return -1
    print("Verify MDS")
    os.remove("temp_file")
    return file_content

#主函数
def UserModeFWUpgrade(iPort, iImgFile):
    dut_port = iPort
    cyfm_file = read_into_buffer(iImgFile)
    file_content = analysisImg(cyfm_file)  #img 校验

    # 打开串口############################################################  ↓
    comport = serial.Serial("COM" + str(dut_port), 115200, timeout=60)
    if comport.is_open:
        print("Start to flash firmware\r\n")
    else:
        return -1
    ######################################################################  ↑

    # firmware to be loaded
    firmware_file = list(file_content[16:])  #升级包 内容
    firmware_length = len(firmware_file)        

    # 发送MONVER
    sendCommand(comport, cmdNMEAOFF)##################################
    time.sleep(1)

    # 清空串口缓存
    comport.flushInput()############################################去掉
    comport.flushOutput()

    # fwup 指令 （进入升级模式命令）
    sendCommand(comport, cmdCFGFWUP)#################################   sendCommand 需要改 

    # 监测进入升级模式
    recv = b'0'
    recvlast = b'1'
    recvCont = 0
    while (recv != b'C' and recvlast != b'C' and recvCont < 512):
        recvlast = recv
        recv = comport.read(1)       ####################################  改为接受函数 
        recvCont += 1
        print("recv type = ", type(recv), "recv = ", recv)
    if(recvCont < 512):
        print("into fwup mode succses")
    else:
        print("into fwup mode failed")
        return -1

    if enDebug:
        time.sleep(0)

    # 清空串口缓存
    comport.flushInput()    ####################################去掉
    comport.flushOutput()

    # 写入数据
    userFWUpdate(comport, firmware_file, firmware_length)   ############################ 升级函数  

    sendCommand(comport, cmdACKACK) ##########################

    sendCommand(comport, cmdCFGPRT) ###########################

    sendCommand(comport, cmdMONVER) #############################

    comport.close()

    return 0

if __name__ == '__main__':

    #首先确保芯片为user模式
    iPort = 4
    iImgFile = "C:\\Users\\wanghao\\Desktop\\20191229-V8416\\HD8040D.BDO.GN3.115200.8416.f8ff1.281219T.cyfm"
    rec = UserModeFWUpgrade(iPort, iImgFile)