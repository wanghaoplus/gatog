#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2020/2/19 14:19
# @Author  : wanghao
# @Site    :
# @File    : UserModeFWUpgrade.py
import time
import socket
import serial
from aw.core.Input import PRINTE
from aw.core.Input import PRINTTRAC
from aw.core.Input import AutoPrint
CONNECT_TIMEOUT = 5
CONNECT_RETRY_TIMES = 1
BUFSIZE = 1024
ACK_WAIT_TIME=5
NACK_CMD_ID = 0x0500
MON_VER_ID = 0x0A04


class SocketClient(object):
    __host = None
    __port = None
    __client = None
    stopRecvFlag = False

    def __init__(self, host=None, port=None):
        super(SocketClient, self).__init__()
        self.__host = host
        self.__port = port

    @property
    def client(self):
        if self.__client is None:
            self.__client = self._connect()
        return self.__client
    
    def _connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for connTimes in range(1, CONNECT_RETRY_TIMES + 1):
            try:
                s.connect((self.__host, self.__port))
#                 s.settimeout(2)
                return s
            except:
                PRINTE('第%s次连接失败...' % connTimes)
                if connTimes == CONNECT_RETRY_TIMES:
#                     PRINTTRAC('请检查网络是否异常')
                    raise
                
    def connect(self):
        if self.__client is None:
            self.__client = self._connect()

    def send(self, cmd):
        self.client.send(cmd)
        
    def reciver(self, bufsize=BUFSIZE):
        return self.client.recv(bufsize)
        
    def close(self):
        if self.__client:
            self.__client.close()
            self.__client = None
            
    def __del__(self):
        self.close()
        

class SerialBase(object):
    __port = None
    __baud = None
    __timeout = 2
    __serObj = None
    stopRecvFlag = False

    def __init__(self, port, baud=115200, readTimeOut=1):
        super(SerialBase, self).__init__()
        self.__port = port
        self.__baud = baud
#         self.__timeout = readTimeOut
        
    @property
    def serialObj(self):
        if (self.__serObj is None) and (self.stopRecvFlag is False):
            self.__serObj = self.__connect()
        return self.__serObj
    
    def __connect(self):
        for connTimes in range(1, CONNECT_RETRY_TIMES + 1):
            try:
                serObj = serial.Serial()
                serObj.port = self.__port
                serObj.baudrate = self.__baud
#                 serObj.timeout = self.__timeout
                serObj.open()
                serObj.flushInput()
                serObj.flushOutput()
                return serObj
            except:
                PRINTE('第%s次连接失败...' % connTimes)
                if connTimes == CONNECT_RETRY_TIMES:
                    PRINTTRAC('请检串口连接是否异常')
                    raise
    
    def connect(self):
        if self.__serObj is None:
            self.__serObj = self.__connect()
               
    def send(self, cmd):
        self.serialObj.write(cmd)
        
    def reciver(self,bufsize=None):
        if bufsize:
            return self.serialObj.read(bufsize)
        return self.serialObj.readline()
        
    def close(self):
        if self.__serObj is not None:
            self.__serObj.close()
            self.__serObj = None
            
    def __del__(self):
        self.close()
        
def binary_gen_crc(src_data):
    checksum1 = 0
    checksum2 = 0
    length = len(src_data)
    for i in range(0, length):
        checksum1 += src_data[i]
        checksum2 += checksum1
    checksum2 &= 0xFF
    result = ((checksum1 << 8) + checksum2)&0xFFFF
    return result

def binary_check_packet(src_data):
    # check length
    if(len(src_data) < 8):
        return 0, 0
    # check header
    if ((src_data[0] != 0xF1) or (src_data[1] != 0xD9)):
        return 0, 0
    # check length
    length = src_data[4] + (src_data[5] << 8)
    if(len(src_data) < (length + 8)):
        return 0, 0
    #check crc
    packet_crc = (src_data[length+6]<<8) + src_data[length+7]
    crc = binary_gen_crc(src_data[2:(length+6)])
    if(packet_crc != crc):
        return 0, 0
    cmd_id = src_data[3] + (src_data[2] << 8)
    return cmd_id, (length+8)

def binary_gen_packet(cmd_id, src_data):
    write_ptr = 0
    length = len(src_data)
    send_data = bytearray(length + 6)
    # header + ID
    send_data[0] = 0xF1
    send_data[1] = 0xD9
    send_data[2] = (cmd_id>>8)&0xFF
    send_data[3] = cmd_id&0xFF
    # length
    send_data[4] = length&0xFF
    send_data[5] = (length>>8)&0xFF
    #data
    write_ptr = 6
    for i in range(0, length):
        send_data[write_ptr] = src_data[i]
        write_ptr += 1
    # crc
    checksum = binary_gen_crc(send_data[2:])
    send_data.append((checksum>>8)&0xFF)
    send_data.append(checksum&0xFF)
    return send_data

def binary_send_packet(obj, cmd_id, src_data):
    send_data = binary_gen_packet(cmd_id, src_data)
    obj.sendCommand(send_data)
    return

def send_poll_command(obj, command_id, src_data):
    # retry 5 times
    for retry in range(0,5):
        # send command
        test_time = time.time()
        binary_send_packet(obj, command_id, src_data)

        # wait for reply and check result
        result = 0
        recv_data = bytearray(0)
        while((time.time() - test_time) < ACK_WAIT_TIME):
            recv_data += obj.reciver()
            for i in range(0, len(recv_data)):
                cmd_id, data_length = binary_check_packet(recv_data[i:])
                if(data_length > 0):
                    temp_cmd = recv_data[i:(i+data_length)]
                    # poll success
                    if(cmd_id == command_id):
                        return cmd_id, temp_cmd
                    # nack received
                    elif((cmd_id == NACK_CMD_ID) and (data_length == 10) and (temp_cmd[7] + (temp_cmd[6]<<8) == command_id)):
                        return cmd_id, []
        print("send poll command retry 0x%04X %d" % (command_id, retry + 1))
        #print(binascii.hexlify(recv_data), "\r\n\r\n")
    return -1, []

def poll_command(obj, command_id, src_data, expect_recv_length):
    cmd_id, recv_cmd = send_poll_command(obj, command_id, src_data)
    if((cmd_id == command_id) and (len(recv_cmd) == expect_recv_length)):
        return recv_cmd
    else:
        return []

@AutoPrint(True)
def get_version(obj):
    version_cmd = poll_command(obj, MON_VER_ID, [], 40)
    if(len(version_cmd) == 0):
        PRINTE("get version fail")
    version = "Version: [%s], [%s]\r\n" % (version_cmd[22:38].decode("utf8"), version_cmd[6:22].decode("utf8"))
    return version.replace("\0", "")
        
if __name__=='__main__':
    print(bytes.fromhex('F1 D9 0A 04 00 00 0E 34'))
    obj=SocketClient('10.100.5.220',5004)
    obj.send(bytes.fromhex('F1 D9 0A 04 00 00 0E 34'))
    for _ in range(100):
        print([obj.reciver()])