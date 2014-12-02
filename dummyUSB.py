#-*- coding: utf-8 -*- 
#!/usr/bin/env python

## dummy class to replace usbio class
class I2C(object):
    def __init__(self,module,slave):
        pass
        
    def searchI2CDev(self,begin,end):
        pass
        
    def write_register(self, reg, data):
        pass
        
#    def I2C(self,module,slave,channel):
#        pass
        
def autodetect():
    pass

def setup():
    pass
