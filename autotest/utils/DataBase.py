#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/3 23:15
# @Author  : shaochanghong
# @Site    : 
# @File    : DataBase.py
# @Software: PyCharm

import os
import sqlite3
from autotest.core.modle.Variable import VAR
from autotest.core.logger import LogPrint
from autotest.utils.Decorator import singleton


class SqliteController(object):

    def __init__(self, dbPath):
        self.__dbPath = dbPath
        self.__connectDb()

    @property
    def conn(self):
        return self.__conn

    @property
    def cursor(self):
        return self.__cursor

    def __connectDb(self):
        self.__conn = sqlite3.connect(self.__dbPath)
        self.__cursor = self.__conn.cursor()

    def execute(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except:
            LogPrint.PRINTTRAC()
            self.conn.rollback()

    def createTable(self, tableName, columns):
        columns = ",".join([" ".join(column) for column in columns])
        sql = 'CREATE TABLE {0} ({1})'.format(tableName, columns)
        self.execute(sql)

    def addData2Table(self, tableName, dataDict):
        columns, values = zip(*dataDict.items())
        columns = ','.join(columns)
        values = str(list(values)).strip('[').strip(']')
        sql = "INSERT INTO {0} ({1}) VALUES ({2})".format(tableName, columns, values)
        self.execute(sql)
        
    def getDataFromTable(self, tableName, columns):
        columns = ",".join(columns)
        sql = 'SELECT {1} FROM {0}'.format(tableName, columns)
        self.cursor.execute(sql)
        values = self.cursor.fetchall()
        return values

    def __del__(self):
        self.conn.close()


@singleton
class TestResultDB(object):

    def __init__(self):
        self.__controller = None

    @property
    def controller(self):
        if self.__controller is None:
            from autotest.core.modle.Variable import VAR
            dbPath = os.path.join(VAR.CurProject.ReportRootPath, VAR.CurProject.TaskId)
            if not os.path.exists(dbPath):
                os.makedirs(dbPath)
            dbFilePath = os.path.join(dbPath, 'report.db')
            self.__controller = SqliteController(dbFilePath)
        return self.__controller

    def createProjectTable(self):
        columns = [('loop', 'INT'),
                   ('startTime', 'VARCHAR(20)'),
                   ('endTime', 'VARCHAR(20)'),
                   ('caseTotal', 'INT'),
                   ('notRun', 'INT'),
                   ('pass', 'INT'),
                   ('fail', 'INT'),
                   ('block', 'INT'),
                   ('unavailable', 'INT'),
                   ('logUrl', 'VARCHAR(100)')]
        self.controller.createTable('project', columns)

    def createCaseTable(self):
        columns = [('loop', 'INT'),
                   ('caseName', 'VARCHAR(50)'),
                   ('startTime', 'VARCHAR(20)'),
                   ('endTime', 'VARCHAR(20)'),
                   ('result', 'VARCHAR(10)'),
                   ('pass', 'INT'),
                   ('fail', 'INT'),
                   ('logUrl', 'VARCHAR(100)')]
        self.controller.createTable('testcase', columns)

    def addProjectResult(self):
        tableName = 'project'
        dataDict = {'loop': VAR.CurProject.CurLoopTime,
                    'startTime': VAR.CurProject.StartTime,
                    'endTime': VAR.CurProject.EndTime,
                    'caseTotal': len(VAR.CurSuit.CaseList),
                    'notRun': VAR.CurProject.NotRun,
                    'pass': VAR.CurProject.Pass,
                    'fail': VAR.CurProject.Fail,
                    'block': VAR.CurProject.Block,
                    'unavailable': VAR.CurProject.Unavailable,
                    'logUrl': os.path.join(VAR.CurProject.ReportPath, 'test_run_detail.log')}
        self.controller.addData2Table(tableName, dataDict)

    def addCaseResult(self):
        tableName = 'testcase'
        caseName = VAR.CurCase.CaseName
        dataDict = {'loop': VAR.CurProject.CurLoopTime,
                    'startTime': VAR.CurCase.StartTime,
                    'endTime': VAR.CurCase.EndTime,
                    'caseName': caseName,
                    'result': VAR.CurCase.CaseResult,
                    'pass': VAR.CurCase.LoopPassTotal,
                    'fail': VAR.CurCase.LoopFailTotal,
                    'logUrl': os.path.join(VAR.CurProject.ReportPath, 'log', caseName, caseName + '.log')}
        self.controller.addData2Table(tableName, dataDict)
        
    def getCaseResult(self):
        tableName = 'testcase'
        columns = ['loop', 'caseName', 'startTime', 'endTime', 'result', 'logUrl']
        return self.controller.getDataFromTable(tableName, columns)

