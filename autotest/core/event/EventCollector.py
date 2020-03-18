#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/8 22:10
# @Author  : shaochanghong
# @Site    : 
# @File    : EventCollector.py.py
# @Software: PyCharm
from autotest.core.event.AutoInput import CustomException
__event_dirs__ = dir({})
__event_dirs__.append('addEvent')
__event_dirs__.append('removeEvent')


class EventContainer(dict):

    def __setattr__(self, event, value):
        self[event] = value

    def __getattribute__(self, event):
        if event in __event_dirs__:
            return object.__getattribute__(self, event)
        if event in self:
            return self[event]
        raise CustomException("has no register {0} observer.".format(event))

    def addEvent(self, event, value):
        if event not in self:
            self.__setattr__(event, value)

    def removeEvent(self, event):
        if event in self:
            self.pop(event)


Event = EventContainer()
