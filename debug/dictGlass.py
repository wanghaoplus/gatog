#!/usr/bin/env python
#!_*_ coding: utf-8 -*-

class cat(object):
    bar = 1
    name = 'hh'
    def __init__(self, name , bar):
        self.name = name
        self.bar = bar

    def __getattribute__(self, item):
        print('拦截')
        try:
            return super().__getattribute__(item)
            if item == "a":
                print('----%s----')
                return ('%s is get' % item)
            else:
                return object.__getattribute__(self, item)
        except AttributeError:
            print("have no attribute of %s" % item)

t = cat("wan", 20)
print(t.name, t.bar)

print(t.ss)