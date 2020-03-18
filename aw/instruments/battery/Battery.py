# coding:utf-8

import visa
import pyvisa
import threading

class Battery(object):
    current_value_list = []
    
    def __init__(self, ip):
        self.ip = "TCPIP::{}::INSTR".format(ip)
        self.visa_data = pyvisa.ResourceManager()
        inst_list = self.visa_data.list_resources()
        self.inst = self.visa_data.open_resource(self.ip)
        self.status = False
        
    def start_record_current(self):
#         self.inst.set_visa_attribute(pyvisa.constants.VI_ATTR_TMO_VALUE, 2000000000)
        self.status = True
        thd = threading.Thread(target=self.get_current_value, args=())
       
    def get_current_value(self):
        while self.status:
            self.inst.write("READ?")
            current = inst.read()
#             if (len(str) < 16):
#                 raise Exception("error on %d" % (i))
            try:
                current = '{:.6f}'.format(current)
            except Exception as e:
                print(e)
            self.current_value_list.append(current) 
            print(current)
            
    def write_command(self, command=None):
        self.status = False
        if command:
            self.inst.write(command)
            result = inst.read()
            
            
            
    def stop_read_current(self):
        self.status = False
        self.inst.close()
        self.visa_data.close()
        
        
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