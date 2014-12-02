#-*- coding: utf-8 -*- 
#!/usr/bin/env python

## dummy class to replace ULI class
class I2C(object):
    def __init__(self,module,slave,channel):
        pass
        
    def searchI2CDev(self,begin,end):
        pass
        
    def write_register(self, reg, data):
        pass
        
#    def I2C(self,module,slave,channel):
#        pass
        
