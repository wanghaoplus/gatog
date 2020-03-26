# -*- coding: utf-8 -*-
# @Time    : 2020/2/19 14:19
# @Author  : wanghao
# @Site    :
# @File    : UserModeFWUpgrade.py
import os
import time
import gzip
import hashlib
from aw.core.Input import PRINTI
from aw.core.Input import PRINTTRAC
from aw.core.Input import AutoPrint
from aw.utils.deviceupgrade.UpgradeBase import SerialBase
from aw.utils.deviceupgrade.UpgradeBase import SocketClient

ACK_WAIT_TIME=5
NACK_CMD_ID = 0x0500
MON_VER_ID = 0x0A04
ACK_CMD_ID = 0x0501
MSG_ID_WRITE_FLASH = 0xF405
ERASE_FLAH_8020 = [0x00, 0x00, 0x00, 0x90, 0x00, 0x00]
ERASE_FLAH_8040 = [0x00, 0x00, 0x10, 0x00, 0x00, 0x00]

class UpgradeForBoot(object):
    fastbootObj=None
    
    def __init__(self, connectType, port, ip=None):
        if connectType.lower() == "socket":
            self.fastbootObj = SocketClient(host=ip, port=int(port))
        elif connectType.lower() == 'usb':
            self.fastbootObj = SerialBase(port)
        else:
            raise Exception('参数有误')
        self.fastbootObj.connect()
        
    def sendCommand(self,cmd):
        self.fastbootObj.send(cmd)
        
    def close(self):
        self.fastbootObj.close()
        
    def reciver(self,bufSize=1024):
        return self.fastbootObj.reciver(bufSize)
    
    def read2Buffer(self, filename):
        buf = bytearray(os.path.getsize(filename))
        with open(filename, 'rb') as f:
            f.readinto(buf)
        return buf
    
    def reset(self):
        from aw.utils.deviceupgrade.UpgradeBase import binary_gen_packet
        MSG_ID_RESET = 0xF420
        send_data = binary_gen_packet(MSG_ID_RESET, bytearray([0x01]))
        self.sendCommand(send_data)
        time.sleep(0.1)
        self.sendCommand(send_data)
        time.sleep(0.1)
        
    def binary_send_packet(self, cmd_id, src_data):
        from aw.utils.deviceupgrade.UpgradeBase import binary_gen_packet
        send_data = binary_gen_packet(cmd_id, src_data)
        self.sendCommand(send_data)
        return
        
    def send_set_command(self, command_id, src_data):
        from aw.utils.deviceupgrade.UpgradeBase import binary_check_packet
        # retry 5 times
        for retry in range(0,5):
            # send command
            test_time = time.time()
            self.binary_send_packet(command_id, src_data)
            
            # wait for reply and check result
            result = 0
            recv_data = bytearray(0)
            while ((time.time() - test_time) < ACK_WAIT_TIME):
                recv_data += self.reciver()
                for i in range(0, len(recv_data)):
                    cmd_id, data_length = binary_check_packet(recv_data[i:])
                    if (data_length > 0):
                        temp_cmd = recv_data[i:(i+data_length)]
                        # ack or nack received
                        if(((cmd_id == ACK_CMD_ID) or (cmd_id == NACK_CMD_ID)) and (data_length == 10) and (temp_cmd[7] + (temp_cmd[6]<<8) == command_id)):
                            return cmd_id
            print("set command retry 0x%04X %d" % (command_id, retry + 1))
        return 0
        
    def eraseFlash(self, send_data):
        send_data = bytearray(send_data)
        self.send_set_command(MSG_ID_WRITE_FLASH, send_data)
        
    def fastboot(self,chipType,path):
        if chipType.lower().startswith('hd802'):
            cmdBOOTERASE = ERASE_FLAH_8020
        elif chipType.lower().startswith('hd804'):
            cmdBOOTERASE = ERASE_FLAH_8040
        else:
            return -1,'没有此芯片类型：%s'%chipType
        cyfm_file = self.read2Buffer(path)
        if (cyfm_file[0] != 0x0A or cyfm_file[1] != 0x11):
            PRINTI("Fail, cyfm file invalid: 01", 1)
            return -1,'升级失败'
        out = open("temp_file", "wb")
        out.write(cyfm_file[12:])  # extract .gz file
        out.close()
    
        try:
            with gzip.open("temp_file", 'rb') as f:
                file_content = bytearray(f.read())
        except:
            PRINTI("Fail, cyfm file invalid: 02", 1)
            return -1,'升级失败'
    
        # verify MD5
        file_md5 = hashlib.md5(file_content[16:]).digest()
        if (file_md5 != file_content[0:16]):
            PRINTI("Fail, cyfm file invalid: 03", 1)
            return -1,'升级失败'
    
        print("Verify MDS")
        firmware_file = file_content[16:]  # firmware to be loaded
        firmware_length = len(firmware_file)
        f.close()
        os.remove("temp_file")
        print("erase flash...")
        self.eraseFlash(cmdBOOTERASE)
        
        print("Flashing...")
        send_ptr = 0     
        packet_id = 1
        firmware_length_temp = firmware_length
        progress_status = 0
        
        while (firmware_length_temp > 0):
            send_data = binary_gen_flash_header(send_ptr, packet_id)
            
            # remaining file larger than 2048
            if (firmware_length_temp > 2048):
                if (send_ptr == 0):
                    for i in range(0, 64):
                        send_data += bytearray([0xFF])
                    send_data += firmware_file[send_ptr+64 : send_ptr+2048]
                else:
                    send_data += firmware_file[send_ptr : send_ptr+2048]
                result = self.send_set_command(MSG_ID_WRITE_FLASH, send_data)
                send_ptr += 2048
                firmware_length_temp -= 2048
            # remaining file smaller than 2048
            else:
                send_data += firmware_file[send_ptr : send_ptr+firmware_length_temp]
                result = self.send_set_command(MSG_ID_WRITE_FLASH, send_data)
                send_ptr = firmware_length
                firmware_length_temp = 0        
            
            packet_id += 1
            
            # print flash progress
            percentage_done = int((10*send_ptr/firmware_length))%10
            if(percentage_done > progress_status):
                progress_status = percentage_done
                print(str(percentage_done*10)+"%")
            
            # check ack
            if(result == 0):
                return -1,"Caution: flash fail"
        
        # flash first 64 byte
        send_data = binary_gen_flash_header(0, packet_id)
        send_data += firmware_file[0:64]
        result = self.send_set_command(MSG_ID_WRITE_FLASH, send_data)
        if(result == 0):
            return -1,"Caution: flash fail"
        print("100%")
        return 0, 'boot升级结束'
        
def binary_gen_flash_header(start_address, packet_id):
    temp_address = 0x100000 + start_address
    output_buf = bytearray(6)
    output_buf[0] = temp_address&0xFF
    output_buf[1] = (temp_address>>8)&0xFF
    output_buf[2] = (temp_address>>16)&0xFF
    output_buf[3] = (temp_address>>24)&0xFF
    output_buf[4] = packet_id&0xFF
    output_buf[5] = (packet_id>>8)&0xFF
    return output_buf
    
if __name__=='__main__':
    from aw.utils.deviceupgrade.Config import FASTBOOT_CONF
    for devieDict in FASTBOOT_CONF:
        startTime=time.time()
        ip = devieDict.get('ip')
        port = devieDict.get('port')
        firmware = devieDict.get('firmware')
        fastboot=UpgradeForBoot('socket',port,ip)
        fastboot.writeFlash('hd8040', firmware)
        fastboot.reset()
    
    