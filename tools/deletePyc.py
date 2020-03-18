#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/3 23:52
# @Author  : shaochanghong
import os
import shutil


def deletePyc(mPath):
    for root, dirName, fileList in os.walk(mPath):
        for fileName in fileList:
            if fileName.endswith('.pyc'):
                os.remove(os.path.join(root, fileName))
        if os.path.exists(os.path.join(root, '__pycache__')):
            shutil.rmtree(os.path.join(root, '__pycache__'))


deletePyc(r'D:\workspace\LBS_new')
