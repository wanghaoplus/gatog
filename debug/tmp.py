
#!/usr/bin/env python
#-*- coding: utf-8 -*-


class cat(object):
    name = "tmp"
    age = 22

    def __init__(self, name, age):
        self.name = name
        self.age = age
        
    
    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            return print("have no attribute of %s" % attr)


awang = cat("wanghao", 31)
print(awang.name)
print(awang.gender)
