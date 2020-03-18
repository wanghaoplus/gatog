#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/3 23:37
# @Author  : shaochanghong
# @Site    :
# @File    : Test_001.py
# @Software: PyCharm

from aw.LbsTestCase import LbsTestCase, LoopTest
from aw.instruments.labsat.Labsat import GssLabsat
import time


class Test_002(LbsTestCase):

    def __init__(self):
        super(Test_002, self).__init__()
        self.TestCaseList = ["Test_002"]
        self.Labsat = GssLabsat(ip='LABSATV3_169.254.92.68', port=23)

    def setup(self):
        super(Test_002, self).setup()
        print('setup start', self.data.scene)
        self.setupStep('打开LABSAT开关')
        self.lbsAW.aw_openSerial()
        self.lbsAW.aw_startColdLocation(port='COM4')
        ret = self.Labsat.aw_labsatPlay(self.data.scene, moment=60, duration=0)
        print(ret)

#     @LoopTest(2)
    def Test_002(self):
        print('test start')
#         self.testStep("发起定位")
#         self.lbsAW.aw_startColdLocation(port='COM4')
        time.sleep(180)
#         self.assertSuc(self.lbsAW.aw_checkLocationSucess(port='COM4'))

    def teardown(self):
        print('teardown start')
        self.Labsat.aw_labsatStopPlay()
        self.lbsAW.aw_closeSerial()
        self.teardownStep("关闭gps开关")
        
        
