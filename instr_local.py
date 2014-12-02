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

## power supply class
# for Agilent/Keysight E3640A
class powersupply(object):
    _PSU = False
    _rm = False
    _setvolt = '3.7'

    ## constructor
    # @param resourcemanager resource manager object
    # @param gpib GPIB address
    def __init__(self, resourcemanager, gpib):
        try:
            self._rm=resourcemanager
            self._PSU = self._rm.get_instrument("GPIB0::"+gpib+"::INSTR")
            self._PSU.write('INST P6V')
            self._PSU.write('CURR 1e0;:VOLT '+"3.7"+';')
        except:
            raise
            pass

    ## sets output voltage
    # @param volt voltage to set
    def SetVoltage(self, volt):
        self._PSU.write('VOLT '+volt)
        self._setvolt=volt
        return True

    ## sets current limit
    # @param current limit current in [A]
    def SetCurrent(self, current):
        self._PSU.write('CURR '+current)
        return True

    ## disconnect machine from bus
    # @param visalib visa library object
    def disconnect(self, visalib):
        try:
            visa.VisaLibrary.gpib_control_ren(visalib, self._PSU.session,6)
            visa.VisaLibrary.close(visalib, self._PSU.session)
        except:
            pass

    ## output disable/enable
    # @param on True to set output on, False to set off
    def output(self,on=False):
        if on:
            self._PSU.write('OUTPut 1')
        else:
            self._PSU.write('OUTPut 0')

    ## returns current voltage set
    def read(self):
        return self._setvolt

## Kikusui electro load class
# for Kikusui PLZ164WL
class kikusui(object):
    _PLZ = False
    _rm = False
    _setcurrent = '0.0'
    _isUse = False

    ## constructor
    # @param resourcemanager resource manager object
    # @param gpib GPIB address
    # @param isUSB True if under USB connection, False if GPIB connection
    # @param isuse True if in use, False if not
    def __init__(self, resourcemanager, gpib, isUSB=True, isuse=False):
        self._isUse=isuse
        if self._isUse == True:
            self._rm=resourcemanager
            try:
                if isUSB:
                    self._PLZ = self._rm.get_instrument("USB0::0x0957::0x1A07::"+gpib+"::INSTR")#USB0::0x0957::0x1A07::SN????????::INSTR
                else:
                    self._PLZ = self._rm.get_instrument("GPIB0::"+gpib+"::INSTR")
                self.SetCurrentRange()
                self.SetVoltageRange()
                self.SetCurrent('0',False)
            except:
                raise

    ## sets output current
    # @param current load current
    # @param on True to set load on, False to set off
    def SetCurrent(self, current="0.0", on=False):
        if self._isUse == True:
            self._PLZ.write("CURRent:LEVel:IMMediate:AMPLitude "+current)
            self.output(on)

    ## output disable/enable
    # @param on True to set output on, False to set off
    def output(self,on=False):
        if self._isUse == True:
            if on:
                self._PLZ.write("OUTPut:STATe:IMMediate ON")
            else:
                self._PLZ.write("OUTPut:STATe:IMMediate OFF")

    ## disconnect machine from bus
    # @param visalib visa library object
    def disconnect(self,visalib):
        if self._isUse == True:
            self.SetCurrent('0',False)
            visa.VisaLibrary.gpib_control_ren(visalib, self._PLZ.session,6)
            visa.VisaLibrary.close(visalib, self._PLZ.session)
        return True

    ## sets load current range
    # @param range 'LOW' < 0.5A
    def SetCurrentRange (self, range='LOW'):
        if self._isUse == True:
            self._PLZ.write(':CURR:RANG' +range)

    ## sets load voltage range
    # @param range 'LOW' < 3.0V
    def SetVoltageRange (self, range='LOW'):
        if self._isUse == True:
            self.instrument.ask(':VOLT:RANG ' +range)

    ## dummy function to read voltage
    # @return "dummy"
    def ReadVoltage (self):
        return "dummy"

    ## dummy function to read current
    # @return "dummy"
    def ReadCurrent (self):
        return "dummy"

## KEITHLEY soucemeter class
# for KEITHLEY 2400 SMU (K2400)
class sourcemeter(object):
    _SMU = False
    _rm = False
    _setvolt = '1.0'
    _setcurrent = '0.0'
    _isUse = False
    
    ## constructor
    # @param resourcemanager resource manager object
    # @param gpib GPIB address
    # @param isuse True if in use, False if not
    def __init__(self, resourcemanager, gpib, isuse=False):
        self._isUse=isuse
        self._rm=resourcemanager
        try:
            if self._isUse == True:
                self._SMU = self._rm.get_instrument("GPIB0::"+gpib+"::INSTR")
                self.reset()
                self._SMU.write(':DISP:DIG 6')
                self.SetVoltageRange()
                self.SetCurrentRange()
                self.SetCurrentLimit()
                self.SetVoltage('1')
        except:
            raise

    ## disconnect machine from bus
    # @param visalib visa library object
    def disconnect(self,visalib):
        if self._isUse == True:
            visa.VisaLibrary.gpib_control_ren(visalib, self._SMU.session,6)
            visa.VisaLibrary.close(visalib, self._SMU.session)

    ## resets machine status
    def reset (self):
        if self._isUse == True:
            self._SMU.write('*RST')

    ## enables output
    def _output_enable (self): #, channel = 1):
        if self._isUse == True:
#            if (channel == 1):
            self._SMU.write(':OUTP:STAT 1;:INIT')
#            else:
#                raise Exception("Invalid channel selection CH{0}" .fo_rmat(channel))

    ## disables output
    def _output_disable (self): #, channel = 1):
        if self._isUse == True:
            self._SMU.write(':OUTP:STAT 0')
#            if (channel != 1):
#                raise Exception("Invalid channel selection CH{0}" .fo_rmat(channel))

    ## output disable/enable
    # @param on True to set output on, False to set off
    def output(self,on=False):
        if self._isUse == True:
            if on:
                self._output_enable()
            else:
                self._output_disable()

    ## sets output voltage
    # @param volt voltage to set
    def SetVoltage (self, volt='1.0'): #, channel = 1):
        if self._isUse == True:
#            if (channel == 1):
            self._SMU.write(":SOUR:FUNC VOLT")
            self._SMU.write(":SOUR:VOLT:MODE FIX")
            self._SMU.write(":SOUR:VOLT " +volt)
#            else:
#                raise Exception("Invalid channel selection CH{0}" .fo_rmat(channel))

    ## sets output current if current source mode; NOT IN USE 
    def SetCurrent (self, current='1e-6'): #, channel = 1):
        if self._isUse == True:
#            if (channel == 1):
            self._SMU.write(":SOUR:FUNC CURR")
            self._SMU.write(":SOUR:CURR:MODE FIX")
            self._SMU.write(":SOUR:CURR " +current)
#            else:
#                raise Exception("Invalid channel selection CH{0}" .fo_rmat(channel))

    ## sets voltage limit if current source mode; NOT IN USE
    def SetVoltageLimit (self, voltage): #, channel = 1):
        if self._isUse == True:
#            if (channel == 1):
            self._SMU.write(":SOUR:FUNC CURR")
            self._SMU.write(":SOUR:CURR:MODE FIX")
            self._SMU.write(":SENS:VOLT:DC:PROT:LEV " +voltage)
#            else:
#                raise Exception("Invalid channel selection CH{0}" .fo_rmat(channel))

    ## sets current limit if voltage source mode
    # @param current current to set
    def SetCurrentLimit (self, current='1e-6'): #, channel = 1):
        if self._isUse == True:
#            if (channel == 1):
            self._SMU.write(":SOUR:FUNC VOLT")
            self._SMU.write(":SOUR:VOLT:MODE FIX")
            self._SMU.write(":SENS:CURR:DC:PROT:LEV " +current)
#            else:
#                raise Exception("Invalid channel selection CH{0}" .fo_rmat(channel))

    ## sets output voltage range
    # @param volt 'auto' if autorange
    def SetVoltageRange (self, volt='auto'): #, channel = 1, mode = 'source'):
        if self._isUse == True:
#            if (channel == 1):
#                if (mode == 'sense'):
#                    if (voltage != 'auto'):
#                        self._SMU.write(':SENS:VOLT:RANG %f' % voltage)
#                    else:
#                        self._SMU.write(':SENS:VOLT:DC:RANGE:AUTO 1')
#
#                elif (mode == 'source'):
            if (voltage != 'auto'):
                self._SMU.write(":SOUR:FUNC VOLT")
                self._SMU.write(":SOUR:VOLT:MODE FIX")
                self._SMU.write(":SOUR:VOLT:RANG %f"%(volt))
            else:
                self._SMU.write(':SOUR:VOLT:DC:RANGE:AUTO 1')

#                else:
#                    raise Exception('Invalid Mode Selection ("source" or "sense")')

#            else:
#                raise Exception("Invalid channel selection CH{0}" .fo_rmat(channel))

    ## sets output current range
    # @param current 'auto' if autorange
    def SetCurrentRange (self, current): #, channel = 1, mode = 'source'):
        if self._isUse == True:
#            if (channel == 1):
#                if (mode == 'sense'): # reads current
            if (current != 'auto'):
                self._SMU.write(':SENS:CURR:RANG %f' % current)
            else:
                self._SMU.write(':SENS:CURR:DC:RANGE:AUTO 1')

#                elif (mode == 'source'): # sources current
#                    if (current != 'auto'):
#                        self._SMU.write(":SOUR:FUNC CURR")
#                        self._SMU.write(":SOUR:CURR:MODE FIX")
#                        self._SMU.write(":SOUR:CURR:RANG %f"%(current) )
#                    else:
#                        self._SMU.write(':SOUR:CURR:DC:RANGE:AUTO 1')

#                else:
#                    raise Exception('Invalid Mode Selection ("source" or "sense")')

#            else:
#                raise Exception("Invalid channel selection CH{0}" .fo_rmat(channel))

    ## reads output depends on mode
    # @param mode 'current' to read current in [A]
    def sample(self, mode="current"):
        if self._isUse == True:
            if mode == "voltage":
                pass
            elif mode == "current":
                return self.ReadCurrent()
                pass

    ## Read V if current source mode; NOT IN USE
    def ReadVoltage (self, samples = 1, channel = 1, avg_mode = 'MOV', filt = 'ON', nplc = 1):
        if self._isUse == True:
            if (channel == 1):
                self._SMU.write("*CLS")
                self._SMU.write(":ABOR")
                self._SMU.write(":ARM:COUN 1;SOUR TIM")
                self._SMU.write(":FUNC 'VOLT:DC';:VOLT:NPLC %f;:AVER:TCON %s;COUN %d;STAT %s"%(nplc, avg_mode, samples, flit))
                self._SMU.write(":FORM:ELEM:SENS VOLT")
                self._SMU.write(":INIT")

                self._SMU.ask('*OPC?')

                return float(self._SMU.ask(':SENSE:DATA:LAT?'))
            else:
                raise Exception("Invalid channel selection CH{0}" .fo_rmat(channel))

    ## reads current
    def ReadCurrent (self): #, samples = 1, channel = 1, avg_mode = 'MOV', filt = 'ON', nplc = 1):
        if self._isUse == True:
            samples = 1
            channel = 1
            avg_mode = 'MOV'
            filt = 'ON'
            nplc = 1
#            if (channel == 1):
            self._SMU.write("*CLS")
            self._SMU.write(":ABOR")
            self._SMU.write(":ARM:COUN 1;SOUR TIM")
            self._SMU.write(":FUNC 'CURR:DC';:CURR:NPLC %f;:AVER:TCON %s;COUN %d;STAT %s"%(nplc, avg_mode, samples, filt))
            self._SMU.write(":FORMAT:ELEMENTS:SENSE CURR")
            self._SMU.write(":INIT")

            self._SMU.ask('*OPC?')

            return float(self._SMU.ask(':SENSE:DATA:LAT?'))

#            else:
#                raise Exception("Invalid channel selection CH{0}" .fo_rmat(channel))

    #Set I range for the display
    def set_range_display (self, digits = 7): #, channel = 1):
        if self._isUse == True:
#            if (channel == 1):
            self._SMU.write(':DISP:DIG %d' % int(digits) )
            return

#            else:
#                raise Exception("Invalid channel selection CH{0}" .fo_rmat(channel))

        def error_query(self):
            ''' the error queue hold error and status messages
            '''
            print self._SMU.ask('SYST:ERR?')

## multimeter class
# for Agilent/Keysight 34401A, 34461A
class multimeter(object):
    _VOLTMETER=""
    _rm=""
    
    ## constructor
    # @param resourcemanager resource manager object
    # @param gpib GPIB address
    # @param isUSB True if under USB connection, False if GPIB connection
    def __init__(self, resourcemanager, gpib, isUSB=False):
        self._rm=resourcemanager
        try:
            if isUSB==False:
                self._VOLTMETER = self._rm.get_instrument("GPIB0::"+gpib+"::INSTR")
            else:
                self._VOLTMETER = self._rm.get_instrument("USB0::0x0957::0x1A07::"+gpib+"::INSTR")#USB0::0x0957::0x1A07::SN????????::INSTR
            self._VOLTMETER.write("INP:IMP:AUTO ON")
        except:
            raise

    ## reads voltage
    # @return read voltage in string
    def sample(self):
        read=self._VOLTMETER.ask('READ?')
        return read

    ## disconnect machine from bus
    # @param visalib visa library object
    def disconnect(self,visalib):
        visa.VisaLibrary.gpib_control_ren(visalib, self._VOLTMETER.session,6)
        visa.VisaLibrary.close(visalib, self._VOLTMETER.session)
        return True

## multi channel multimeter class
# for Agilent/Keysight 34970A
class multimeter2(object):
    _VOLTMETER2=""
    _channels="(@101)"
    _rm = False
    _isUse = False
    
    ## constructor
    # @param resourcemanager resource manager object
    # @param gpib GPIB address
    # @param isuse True if in use, False if not
    def __init__(self, resourcemanager, gpib='10', isuse=False):
        self._isUse=isuse
        self._rm=resourcemanager
        if self._isUse == True:
            try:
                self._VOLTMETER2 = self._rm.get_instrument("GPIB0::"+gpib+"::INSTR")
                read=self._VOLTMETER2.ask('*IDN?')
                self._VOLTMETER2.write('*RST')
            except:
                raise

    ## reads voltage
    # @return read voltage and channel in string
    def sample(self):
        if self._isUse == True:
            self._VOLTMETER2.write('SENS:FUNC "VOLT:DC", '+self._channels    )
            self._VOLTMETER2.write('INP:IMP:AUTO ON,'+self._channels    )#

            self._VOLTMETER2.write('SENS:VOLT:DC:NPLC 2, '+self._channels    )
            self._VOLTMETER2.write('SENS:VOLT:DC:RANG:AUTO ON, '+self._channels    )
            self._VOLTMETER2.write('TRIG:SOUR IMM')
            self._VOLTMETER2.write('TRIG:COUNT 1.0e0')
            self._VOLTMETER2.write('INIT')
            read=self._VOLTMETER2.ask("*OPC?")
            read=self._VOLTMETER2.ask('READ?')#
            return read
        return 0

    ## sets channel(s) to use
    # @param chanlist channel list
    def set_Channel(self, chanlist):
        if self._isUse == True:
            self._channels = chanlist
            self._VOLTMETER2.write('CONF:VOLT:DC 10,1.0e-5,' +self._channels)
            self._VOLTMETER2.write('ROUT:SCAN ' +self._channels)
            self._VOLTMETER2.write('ROUT:CHAN:DEL:AUTO OFF, ' +self._channels)
            self._VOLTMETER2.write('ROUT:CHAN:DEL 2e-1, ' +self._channels)
            self._VOLTMETER2.write('FORM:READ:TIME:TYPE ABS')
            self._VOLTMETER2.write('FORM:READ:CHAN ON')
            self._VOLTMETER2.write('SENS:FUNC "VOLT:DC", ' +self._channels)
            self._VOLTMETER2.write('INP:IMP:AUTO ON,' +self._channels)
        return True

    ## disconnect machine from bus
    # @param visalib visa library object
    def disconnect(self,visalib):
        if self._isUse == True:
            visa.VisaLibrary.gpib_control_ren(visalib, self._VOLTMETER2.session,6)
            visa.VisaLibrary.close(visalib, self._VOLTMETER2.session)
        return True

## temperature chamber class
# for Espec SU-241
class chamber(object):
    _isCtrl=False
    _CHAMBER=""

    ## constructor
    # @param resourcemanager resource manager object
    # @param gpib GPIB address
    # @param isctrl True if controls temperature, False if read only
    def __init__(self, resourcemanager, gpib='16', isctrl=False):
        _isCtrl=isctrl
        self._rm=resourcemanager
        try:
            self._CHAMBER = self._rm.get_instrument("GPIB0::"+gpib+"::INSTR")
            self._CHAMBER.ask('ROM?')
            self._CHAMBER.ask("MODE, STANDBY")
            if _isCtrl == True:
                self._CHAMBER.ask("MODE, CONSTANT")
        except:
            raise

    ## gets current ambient temperature
    # @return current temp, target temp and limits as list
    def getTemp(self):
        read=self._CHAMBER.ask("TEMP?")
        return read.split(',')

    ## sets target temperature
    # @param temp target temp as string
    # @return response from machne as string
    def setTemp(self, temp):
        read=self._CHAMBER.ask("TEMP,s"+temp)
        return read

    ## sets to standby mode
    def close(self):
        self._CHAMBER.ask("MODE, STANDBY")
        return True

    ## disconnect machine from bus
    # @param visalib visa library object
    def disconnect(self, visalib):
        self.close()
        visa.VisaLibrary.gpib_control_ren(visalib, self._CHAMBER.session,6)
        visa.VisaLibrary.close(visalib, self._CHAMBER.session)
        return True

## serial to I2C converter class
# for mbed LPC11U35(1ch)/LPC1768(2ch)/LPC824(4ch)
class serial_i2c(object):
    _isUse = False
    _Channel=0
    _Slave=[0x90,0x90,0x90,0x90]
    _I2C=0
    
    ## constructor
    # opens COM port for communication
    # @param port specify COM port which mbed is connected
    # @param baud baudrate
    # @param isuse True if in use, False if not
    def __init__(self, port='com3', baud='115200', isuse=False):
        self._isUse = isuse
        
        if self._isUse == True:
            try:
                self._I2C=serial2i2c.serial2i2c(port,baud)
            except:
                raise
            for hoge in range(4):
                self.set_Channel(hoge)
                self.setBase(hoge,0x90)

    ## sets base address of selected channel
    # @param channel selected channel
    # @param base base address in HEX
    def setBase(self, channel=0, base=0x90):
        if self._isUse == True:
            self._Slave[channel]=base

    ## gets base address of selected channel
    # @param channel selected channel
    # @return slave address in HEX
    def getBase(self, channel=0):
        slave=0
        if self._isUse == True:
            slave=self._Slave[channel]
        return slave

    ## writes data to register address in selected slave address
    # @param slave slave address in HEX
    # @reg register address in HEX
    # @data data in HEX
    # @return created packet
    def regWrite(self, slave=0x90, reg=0x00, data=0x00):
#        packet=['S','P']
        packet=[]
        if self._isUse == True:
            slave=self._I2C.convert_hex_to_ascii2(slave,mask=0xa0)
            reg=self._I2C.convert_hex_to_ascii2(reg,mask=0xb0)
            data=self._I2C.convert_hex_to_ascii2(data,mask=0xc0)
            length=self._I2C.convert_hex_to_ascii2(len(reg)/2+len(data)/2,mask=0xd0)
            
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
                self._I2C.raw_write(hoge)

        return packet

    ## sets I2C bus channel to use
    # @param channel selected channel
    # @return response from mbed as dummy
    def setChannel(self, channel=0):
        dummy=0
        if self._isUse == True:
            self._Channel=channel
            dummy=self._I2C.set_Channel(channel)
        return dummy

    ## gets I2C bus channel in use
    # @return channel in use
    def getChannel(self):
        channel=-1
        if self._isUse == True:
            channel = self._Channel
        return channel

    ## disconnect connection
    def disconnect(self):
        self._I2C.close()

## dummy class 
# for all instrument classes
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

    def SetVoltageLimit (self, voltage): #, channel = 1):
        pass

    def SetCurrentLimit (self, current): #, channel = 1):
        pass

    def SetVoltageRange (self, voltage): #, channel = 1, mode = 'source'):
        pass

    def SetCurrentRange (self, current): #, channel = 1, mode = 'source'):
        pass

    def ReadVoltage (self, samples = 1, channel = 1, avg_mode = 'MOV', filt = 'ON', nplc = 1):
        return "dummy"

    def ReadCurrent (self): #, samples = 1, channel = 1, avg_mode = 'MOV', filt = 'ON', nplc = 1):
        return "dummy"
