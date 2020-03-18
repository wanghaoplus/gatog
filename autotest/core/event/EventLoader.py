#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/12 0:02
# @Author  : shaochanghong
# @Site    : 
# @File    : EventPublisher.py
# @Software: PyCharm
from autotest.core.event.EventCollector import Event
from autotest.utils.Decorator import singleton


class EventBase(object):
    """
    Function:观察者模式中的被观察者基类，只能用来继承
    """
    def __init__(self):
        pass

    def registerEvent(self, observer):
        pass

    def removeEvent(self, observer):
        pass

    def notifyEvent(self, event):
        pass


@singleton
class EventLoader(EventBase):

    @staticmethod
    def registerEvent(eventProcessor):
        Event.addEvent(eventProcessor.__name__, eventProcessor)

    @staticmethod
    def removeEvent(eventProcessor):
        Event.removeEvent(eventProcessor.__name__)

    @staticmethod
    def notify(event):
        observer, method = event.split('.')
        observerObj = Event.get(observer)
        getattr(observerObj, method)()


