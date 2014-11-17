#-*- coding: utf-8 -*- 
#!/usr/bin/env python
import visa
import time
import datetime
import os

import serial2i2c
#try:
#    import uli
#    import usbio.usbio as usbio
#except:
#    import dummyULI as uli 
#    import dummyUSB as usbio

class powersupply(object):
    PSU=False
    rm=False
    setvolt=3.7
    def __init__(self,resourcemanager,gpib):
        try:
            self.rm=resourcemanager
            self.PSU = self.rm.get_instrument("GPIB0::"+gpib+"::INSTR")
            self.PSU.write('INST P6V')
            self.PSU.write('CURR 1e0;:VOLT '+"3.7"+';')
        except:
            raise
            pass

    def SetVoltage(self,volt):
        self.PSU.write('VOLT '+volt)
        self.setvolt=volt
        return True

    def SetCurrent(self,current):
        self.PSU.write('CURR '+current)
        return True

    def disconnect(self,visalib):
        try:
            visa.VisaLibrary.gpib_control_ren(visalib, self.PSU.session,6)
            visa.VisaLibrary.close(visalib, self.PSU.session)
        except:
            pass

    def output(self,on=False):
        if on:
            self.PSU.write('OUTPut 1')
        else:
            self.PSU.write('OUTPut 0')

    def read(self):
        return self.setvolt

class kikusui(object):
    PLZ=False
    rm=False
    setcurrent=0.0
    isUse=False

    def __init__(self,resourcemanager,gpib,isUSB=True,isuse=False):
        self.isUse=isuse
        if self.isUse == True:
            self.rm=resourcemanager
            try:
                if isUSB:
                    self.PLZ = self.rm.get_instrument("USB0::0x0957::0x1A07::"+gpib+"::INSTR")#USB0::0x0957::0x1A07::SN????????::INSTR
                else:
                    self.PLZ = self.rm.get_instrument("GPIB0::"+gpib+"::INSTR")
            except:
                raise

    def SetCurrent(self,current):
        if self.isUse == True:
            self.PLZ.write("CURRent:LEVel:IMMediate:AMPLitude %g" % current)

    def output(self,on=False):
        if self.isUse == True:
            if on:
                self.PLZ.write("OUTPut:STATe:IMMediate ON")
            else:
                self.PLZ.write("OUTPut:STATe:IMMediate OFF")

    def disconnect(self,visalib):
        if self.isUse == True:
            visa.VisaLibrary.gpib_control_ren(visalib, self.PLZ.session,6)
            visa.VisaLibrary.close(visalib, self.PLZ.session)
        return True

    def SetCurrentRange (self, range='LOW'):
        if self.isUse == True:
            self.PLZ.write(':CURR:RANG %s' % range)

    def SetVoltageRange (self, range='LOW'):
        self.instrument.ask(':VOLT:RANG %s' % range)
        pass

    def ReadVoltage (self):
        return "dummy"

    def ReadCurrent (self):
        return "dummy"

class sourcemeter(object):
    SMU=False
    rm=False
    setvolt=3.7
    setcurrent=0.0
    isUse=False
    def __init__(self,resourcemanager,gpib,isuse=False):
        self.isUse=isuse
        self.rm=resourcemanager
        try:
            if self.isUse == True:
                self.SMU = self.rm.get_instrument("GPIB0::"+gpib+"::INSTR")
                self.reset()
                self.SMU.write(':DISP:DIG %d' % int(digits) )
        except:
            raise

    def disconnect(self,visalib):
        if self.isUse == True:
            visa.VisaLibrary.gpib_control_ren(visalib, self.SMU.session,6)
            visa.VisaLibrary.close(visalib, self.SMU.session)

    def reset (self):
        if self.isUse == True:
            self.SMU.write('*RST')

    def output_enable (self, channel = 1):
        if self.isUse == True:
            if (channel == 1):
                self.SMU.write(':OUTP:STAT 1;:INIT')
            else:
                raise Exception("Invalid channel selection CH{0}" .format(channel))

    def output_disable (self, channel = 1):
        if self.isUse == True:
            self.SMU.write(':OUTP:STAT 0')
            if (channel != 1):
                raise Exception("Invalid channel selection CH{0}" .format(channel))

    def output(self,on=False):
        if self.isUse == True:
            if on:
                self.output_enable(1)
            else:
                self.output_disable(1)

    # Set Out V
    def SetVoltage (self, voltage, channel = 1):
        if self.isUse == True:
            if (channel == 1):
                self.SMU.write(":SOUR:FUNC VOLT")
                self.SMU.write(":SOUR:VOLT:MODE FIX")
                self.SMU.write(":SOUR:VOLT %f"%(voltage))
            else:
                raise Exception("Invalid channel selection CH{0}" .format(channel))

    # Set Out I
    def SetCurrent (self, current, channel = 1):
        if self.isUse == True:
            if (channel == 1):
                self.SMU.write(":SOUR:FUNC CURR")
                self.SMU.write(":SOUR:CURR:MODE FIX")
                self.SMU.write(":SOUR:CURR %f"%(current))
            else:
                raise Exception("Invalid channel selection CH{0}" .format(channel))

    # Set Out V Limit
    def SetVoltageLimit (self, voltage, channel = 1):
        if self.isUse == True:
            if (channel == 1):
                self.SMU.write(":SOUR:FUNC CURR")
                self.SMU.write(":SOUR:CURR:MODE FIX")
                self.SMU.write(":SENS:VOLT:DC:PROT:LEV %f"%(voltage))
            else:
                raise Exception("Invalid channel selection CH{0}" .format(channel))

    # Set Out I Limit
    def SetCurrentLimit (self, current, channel = 1):
        if self.isUse == True:
            if (channel == 1):
                self.SMU.write(":SOUR:FUNC VOLT")
                self.SMU.write(":SOUR:VOLT:MODE FIX")
                self.SMU.write(":SENS:CURR:DC:PROT:LEV %f"%(current) )
            else:
                raise Exception("Invalid channel selection CH{0}" .format(channel))

    # Set V Range
    def SetVoltageRange (self, voltage, channel = 1, mode = 'source'):
        if self.isUse == True:
            if (channel == 1):
                if (mode == 'sense'):
                    if (voltage != 'auto'):
                        self.SMU.write(':SENS:VOLT:RANG %f' % voltage)
                    else:
                        self.SMU.write(':SENS:VOLT:DC:RANGE:AUTO 1')

                elif (mode == 'source'):
                    if (voltage != 'auto'):
                        self.SMU.write(":SOUR:FUNC VOLT")
                        self.SMU.write(":SOUR:VOLT:MODE FIX")
                        self.SMU.write(":SOUR:VOLT:RANG %f"%(voltage))
                    else:
                        self.SMU.write(':SOUR:VOLT:DC:RANGE:AUTO 1')

                else:
                    raise Exception('Invalid Mode Selection ("source" or "sense")')

            else:
                raise Exception("Invalid channel selection CH{0}" .format(channel))

    # Set I Range
    def SetCurrentRange (self, current, channel = 1, mode = 'source'):
        if self.isUse == True:
            if (channel == 1):
                if (mode == 'sense'):
                    if (current != 'auto'):
                        self.SMU.write(':SENS:CURR:RANG %f' % current)
                    else:
                        self.SMU.write(':SENS:CURR:DC:RANGE:AUTO 1')

                elif (mode == 'source'):
                    if (current != 'auto'):
                        self.SMU.write(":SOUR:FUNC CURR")
                        self.SMU.write(":SOUR:CURR:MODE FIX")
                        self.SMU.write(":SOUR:CURR:RANG %f"%(current) )
                    else:
                        self.SMU.write(':SOUR:CURR:DC:RANGE:AUTO 1')

                else:
                    raise Exception('Invalid Mode Selection ("source" or "sense")')

            else:
                raise Exception("Invalid channel selection CH{0}" .format(channel))

    def sample(self,mode="voltage"):
        if self.isUse == True:
            if mode == "voltage":
                pass
            elif mode == "current":
                pass

    # Read V
    def ReadVoltage (self, samples = 1, channel = 1, avg_mode = 'MOV', filt = 'ON', nplc = 1):
        if self.isUse == True:
            if (channel == 1):
                self.SMU.write("*CLS")
                self.SMU.write(":ABOR")
                self.SMU.write(":ARM:COUN 1;SOUR TIM")
                self.SMU.write(":FUNC 'VOLT:DC';:VOLT:NPLC %f;:AVER:TCON %s;COUN %d;STAT %s"%(nplc, avg_mode, samples, flit))
                self.SMU.write(":FORM:ELEM:SENS VOLT")
                self.SMU.write(":INIT")

                self.SMU.ask('*OPC?')

                return float(self.SMU.ask(':SENSE:DATA:LAT?'))
            else:
                raise Exception("Invalid channel selection CH{0}" .format(channel))

    # Read I
    def ReadCurrent (self, samples = 1, channel = 1, avg_mode = 'MOV', filt = 'ON', nplc = 1):
        if self.isUse == True:
            if (channel == 1):
                self.SMU.write("*CLS")
                self.SMU.write(":ABOR")
                self.SMU.write(":ARM:COUN 1;SOUR TIM")
                self.SMU.write(":FUNC 'CURR:DC';:CURR:NPLC %f;:AVER:TCON %s;COUN %d;STAT %s"%(nplc, avg_mode, samples, filt))
                self.SMU.write(":FORMAT:ELEMENTS:SENSE CURR")
                self.SMU.write(":INIT")

                self.SMU.ask('*OPC?')

                return float(self.SMU.ask(':SENSE:DATA:LAT?'))

            else:
                raise Exception("Invalid channel selection CH{0}" .format(channel))

    #Set I range for the display
    def set_range_display (self, digits = 7, channel = 1):
        if self.isUse == True:
            if (channel == 1):
                self.SMU.write(':DISP:DIG %d' % int(digits) )

                return

            else:
                raise Exception("Invalid channel selection CH{0}" .format(channel))

        def error_query(self):
            ''' the error queue hold error and status messages
            '''
            print self.SMU.ask('SYST:ERR?')

class multimeter(object):
    VOLTMETER=""
    rm=""
    def __init__(self,resourcemanager,gpib,isUSB=False):
        self.rm=resourcemanager
        try:
            if isUSB==False:
                self.VOLTMETER = self.rm.get_instrument("GPIB0::"+gpib+"::INSTR")
            else:
                self.VOLTMETER = self.rm.get_instrument("USB0::0x0957::0x1A07::"+gpib+"::INSTR")#USB0::0x0957::0x1A07::SN????????::INSTR
            self.VOLTMETER.write("INP:IMP:AUTO ON")
        except:
            raise
            
    def sample(self):
        read=self.VOLTMETER.ask('READ?')
        return read

    def disconnect(self,visalib):
        visa.VisaLibrary.gpib_control_ren(visalib, self.VOLTMETER.session,6)
        visa.VisaLibrary.close(visalib, self.VOLTMETER.session)
        return True

class multimeter2(object):
    VOLTMETER2=""
    channels="(@101)"
    rm=""
    isUse=False
    def __init__(self,resourcemanager,gpib=10,isuse=False):
        self.isUse=isuse
        self.rm=resourcemanager
        if self.isUse == True:
            try:
                self.VOLTMETER2 = self.rm.get_instrument("GPIB0::"+gpib+"::INSTR")
                read=self.VOLTMETER2.ask('*IDN?')
                self.VOLTMETER2.write('*RST')
            except:
                raise

    def sample(self):
        if self.isUse == True:
            self.VOLTMETER2.write('SENS:FUNC "VOLT:DC", '+self.channels    )
            self.VOLTMETER2.write('INP:IMP:AUTO ON,'+self.channels    )#

            self.VOLTMETER2.write('SENS:VOLT:DC:NPLC 2, '+self.channels    )
            self.VOLTMETER2.write('SENS:VOLT:DC:RANG:AUTO ON, '+self.channels    )
            self.VOLTMETER2.write('TRIG:SOUR IMM')
            self.VOLTMETER2.write('TRIG:COUNT 1.0e0')
            self.VOLTMETER2.write('INIT')
            read=self.VOLTMETER2.ask("*OPC?")
            read=self.VOLTMETER2.ask('READ?')#
            return read
        return 0

    def setChannel(self,chanlist):
        if self.isUse == True:
            self.channels = chanlist
            self.VOLTMETER2.write('CONF:VOLT:DC 10,1.0e-5,'+chanlist)
            self.VOLTMETER2.write('ROUT:SCAN '+chanlist)
            self.VOLTMETER2.write('ROUT:CHAN:DEL:AUTO OFF, '+chanlist    )
            self.VOLTMETER2.write('ROUT:CHAN:DEL 2e-1, '+chanlist    )
            self.VOLTMETER2.write('FORM:READ:TIME:TYPE ABS')
            self.VOLTMETER2.write('FORM:READ:CHAN ON')
            self.VOLTMETER2.write('SENS:FUNC "VOLT:DC", '+self.channels    )
            self.VOLTMETER2.write('INP:IMP:AUTO ON,'+self.channels    )#
        return True

    def disconnect(self,visalib):
        if self.isUse == True:
            visa.VisaLibrary.gpib_control_ren(visalib, self.VOLTMETER2.session,6)
            visa.VisaLibrary.close(visalib, self.VOLTMETER2.session)
        return True

class chamber(object):
    isCtrl=False
    CHAMBER=""
    def __init__(self,resourcemanager,gpib=16,isctrl=False):
        isCtrl=isctrl
        self.rm=resourcemanager
        try:
            self.CHAMBER = self.rm.get_instrument("GPIB0::"+gpib+"::INSTR")
            self.CHAMBER.ask('ROM?')
            self.CHAMBER.ask("MODE, STANDBY")
            if isCtrl == True:
                self.CHAMBER.ask("MODE, CONSTANT")
        except:
            raise

    def getTemp(self):
        read=self.CHAMBER.ask("TEMP?")
        return read.split(',')

    def setTemp(self,temp):
        read=self.CHAMBER.ask("TEMP,s"+temp)
        return read

    def close(self):
        self.CHAMBER.ask("MODE, STANDBY")
        return True

    def disconnect(self,visalib):
        self.close()
        visa.VisaLibrary.gpib_control_ren(visalib, self.CHAMBER.session,6)
        visa.VisaLibrary.close(visalib, self.CHAMBER.session)
        return True

class serial_i2c(object):
    isUse=False
    Channel=0
    Slave=[0x90,0x90,0x90,0x90]
    I2C=0
    def __init__(self, port='com3', baud='115200', isuse=False):
        self.isUse = isuse
        
        if self.isUse == True:
            try:
                self.I2C=serial2i2c.serial2i2c(port,baud)
            except:
                raise
        
    def setBase(self, channel=0, base=0x90):
        if self.isUse == True:
            self.Slave[channel]=base

    def getBase(self, channel=0):
        if self.isUse == True:
            return self.Slave[channel]

    def regWrite(self, slave=0x90, reg=0x00, data=0x00):
#        packet=['S','P']
        packet=[]
        if self.isUse == True:
            slave=self.I2C.convert_hex_to_ascii2(slave,mask=0xa0)
            reg=self.I2C.convert_hex_to_ascii2(reg,mask=0xb0)
            data=self.I2C.convert_hex_to_ascii2(data,mask=0xc0)
            length=self.I2C.convert_hex_to_ascii2(len(reg)/2+len(data)/2,mask=0xd0)
            
            slave.reverse()
            length.reverse()
            reg.reverse()
            data.reverse()
    
            packet.extend(slave)
            packet.extend(length)
            packet.extend(reg)
            packet.extend(data)
    
            packet.insert(0,'S')
            packet.append('P')
            for hoge in packet:
                self.I2C.raw_write(hoge)

        return packet
        
    def setChannel(self, channel=0):
        if self.isUse == True:
            self.Channel=channel
            self.I2C.setChannel(channel)
        pass

    def getChannel(self):
        channel=-1
        if self.isUse == True:
            channel = self.Channel
        return channel

class dummy(object):
    def __init__(self):
        pass 

    def SetVoltage(self,volt):
        pass

    def SetCurrent(self,current):
        pass

    def output(self,on=False):
        pass

    def disconnect(self,visalib):
        pass

    def read(self):
        return -3640

    def sample(self):
        return -34401

    def setChannel(self,chanlist):
        pass

    def getChannel(self):
        return -1

    def setBase(self,channel,base):
        pass

    def getBase(self, channel=0):
        return 0x00

    def regWrite(self,reg,data):
        pass

    def getTemp(self):
        return ['-241','-241','limit+','limit-']

    def setTemp(self,temp):
        return "dummy"

    def reset (self):
        pass

#    def sense_4W(self,on=False):
#        pass

    def SetVoltageLimit (self, voltage, channel = 1):
        pass

    def SetCurrentLimit (self, current, channel = 1):
        pass

    def SetVoltageRange (self, voltage, channel = 1, mode = 'source'):
        pass

    def SetCurrentRange (self, current, channel = 1, mode = 'source'):
        pass

    def ReadVoltage (self, samples = 1, channel = 1, avg_mode = 'MOV', filt = 'ON', nplc = 1):
        return "dummy"

    def ReadCurrent (self, samples = 1, channel = 1, avg_mode = 'MOV', filt = 'ON', nplc = 1):
        return "dummy"

    def SetVoltage (self, voltage, channel = 1):
        pass

    def SetCurrent (self, current, channel = 1):
        pass

