#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/1 17:43
# @Author  : shaochanghong
# @Site    : 
# @File    : CaseConfig.py
# @Software: PyCharm
import os
from autotest.core.modle.Variable import VAR
from autotest.core.modle.CustomException import ErrorConfigException
from autotest.core.modle.CustomException import NoSuchCaseException
from autotest.core.running import Engine


class CaseConfig(object):

    @staticmethod
    def getScriptFromProjectSetting():
        """
        @summary:从project.txt中获取配置的脚本
        """
        runScriptPath = os.path.join(VAR.CurProject.RootPath, 'project.txt')
        if os.path.exists(runScriptPath):
            with open(runScriptPath, 'r') as runScriptIter:
                for script in runScriptIter.readlines():
                    script = script.strip()
                    if script.startswith('script') and script.endswith('.py'):
                        scriptImportPath = script.replace('/', '.').strip('.py')
                        scriptModule = Engine.loadScriptFromModule(scriptImportPath)
                        VAR.CurSuit.CaseList.append(scriptModule)
                    elif script.strip() == '':
                        pass
                    elif script.startswith('script'):
                        dirPath = os.path.join(VAR.CurProject.RootPath, os.sep.join(script.split('/')))
                        if not os.path.isdir(dirPath):
                            raise NoSuchCaseException('has no such dir: %s' % dirPath)
                        for rootPath, dirName, fileList in os.walk(dirPath):
                            for fileName in fileList:
                                if fileName.endswith('.py') and fileName.find('__init__') == -1:
                                    filePath = os.path.join(rootPath, fileName)
                                    scriptImportPath = 'script' + filePath.split('script')[-1].strip('.py').replace(os.sep, '.')
                                    scriptModule = Engine.loadScriptFromModule(scriptImportPath)
                                    VAR.CurSuit.CaseList.append(scriptModule)
                    else:
                        raise NoSuchCaseException('has no such case: %s' % script)
        else:
            raise ErrorConfigException('has no path: %s.' % runScriptPath)

    @staticmethod
    def parseScriptConfig(scriptModule):
        """
        @summary:解析脚本配置文件
        @param scriptModule:要解析的脚本
        """
        try:
            scriptClassName = scriptModule.__name__
            scriptConfImportPath = scriptModule.__module__.replace('script', 'script_config')
            scriptConfigModule = __import__(scriptConfImportPath, fromlist=[scriptClassName])
        except ImportError:
            if VAR.CurSuit.CaseConfig:
                VAR.CurCase.Config = VAR.CurSuit.CaseConfig[scriptClassName]
                VAR.CurSuit.CaseConfig.pop(scriptClassName)
            return
        scriptConfClass = getattr(scriptConfigModule, scriptClassName)
        if VAR.CurSuit.CaseConfig.get(scriptClassName):
            for key, value in VAR.CurSuit.CaseConfig[scriptClassName].items():
                setattr(scriptConfClass, key, value)
            VAR.CurSuit.CaseConfig.pop(scriptClassName)
        VAR.CurCase.Config = scriptConfClass
        

if __name__ == "__main__":
    a = {1:1}
    a.pop(1)
    print(a)
    CaseConfig.getScriptFromProjectSetting()
    CaseConfig.parseScriptConfig(VAR.CurSuit.CaseList[0])
    print(VAR.CurCase.Config.Test_001.loopTimes)
