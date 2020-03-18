#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/3 23:46
# @Author  : shaochanghong
# @Site    : 
# @File    : Variable.py
# @Software: PyCharm
import os
import time

__container_dirs__ = dir({})
__container_dirs__.append('addNode')
__container_dirs__.append('setVariableLock')
__container_dirs__.append('releaseVariableLock')
__container_dirs__.append('SetVariableLock')


class VariableContainer(dict):
    """
    function:Represents a set of variables.
        Contains methods for replacing variables from list, scalars, and strings.
        On top of ${scalar}, @{list} and &{dict} variables, these methods handle
        also %{environment} variables.
    """

    def __init__(self):
        object.__setattr__(self, 'SetVariableLock', False)

    def __setattr__(self, var, value):
        if self.SetVariableLock is False:
            self[var] = value

    def __getattribute__(self, var):
        if var in __container_dirs__:
            return object.__getattribute__(self, var)
        return self[var]

    def addNode(self, var):
        if var not in self:
            self.__setattr__(var, VariableContainer())

    def setVariableLock(self):
        self['SetVariableLock'] = True

    def releaseVariableLock(self):
        self['SetVariableLock'] = False


class TestProject(object):
    NotRun = 'NOT RUN'
    Running = 'RUNNING'
    End = 'END'
    RootPath = os.path.dirname(__file__).split('autotest')[0]
    TaskId = 'task_' + time.strftime('%Y%m%d_%H%M%S')
    ReportRootPath = r'D:\report'
    LoopTimes = 1


class TestSuit(object):
    CaseList = []


class TestCase(object):
    NotRun = 'Not Run'
    ResultPass = 'Passed'
    ResultFail = 'Failed'
    ResultBlock = 'Block'
    CaseName = None
    CurLoopTime = 0


VAR = VariableContainer()
VAR.addNode('CurProject')
VAR.addNode('CurCase')
VAR.addNode('CurSuit')
VAR.CurProject.ExecuteState = TestProject.NotRun
VAR.CurProject.RootPath = TestProject.RootPath
VAR.CurProject.TaskId = TestProject.TaskId
VAR.CurProject.ReportRootPath = TestProject.ReportRootPath
VAR.CurProject.LoopTimes = TestProject.LoopTimes

VAR.CurCase.CaseResult = TestCase.NotRun
VAR.CurCase.CaseName = TestCase.CaseName
VAR.CurCase.CurLoopTime = TestCase.CurLoopTime
VAR.CurCase.addNode('Config')

VAR.CurSuit.CaseList = TestSuit.CaseList
VAR.CurSuit.addNode('CaseDict')
VAR.CurSuit.addNode('CaseConfig')

DEVICE = VariableContainer()

INSTRUMENT = VariableContainer()

if __name__ == '__main__':
    print(DEVICE.HdbdDevices)
