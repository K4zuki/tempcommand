import visa
import time
import datetime
import os

import textwrap

#import instruments

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
#            self.PSU.write('VOLT:PROT:STATE ON;:VOLT:PROT 5.6;')
        except:
            pass

    def SetVoltage(self,volt):
        try:
            self.PSU.write('VOLT '+volt)
            self.setvolt=volt
            return True
        except:
            pass

    def SetCurrent(self,current):
        try:
            self.PSU.write('CURR '+current)
#            self.setvolt=volt
            return True
        except:
            pass

    def disconnect(self,visalib):
        try:
            visa.VisaLibrary.gpib_control_ren(visalib, self.PSU.session,6)
            visa.VisaLibrary.close(visalib, self.PSU.session)
        except:
            pass
        
    def output(self,on=False):
        if on:
            self.PSU.write('OUTPut 1')
#            self.PSU.write('OUTPut ON')
        else:
            self.PSU.write('OUTPut 0')
#            self.PSU.write('OUTPut OFF')
#        pass

    def read(self):
        return self.setvolt

class sourcemeter(object):
    SMU=False
    rm=False
    setvolt=3.7
    setcurrent=0.0
    def __init__(self,resourcemanager,gpib):
        self.rm=resourcemanager
        self.SMU = self.rm.get_instrument("GPIB0::"+gpib+"::INSTR")
#        print self.SMU
        self.reset()

    def disconnect(self,visalib):
        try:
            visa.VisaLibrary.gpib_control_ren(visalib, self.SMU.session,6)
            visa.VisaLibrary.close(visalib, self.SMU.session)
        except:
            pass

    # Resets Equipment
    def reset (self):
        self.SMU.write('*RST')

    # Controls Beeper
#    def beep (self, beeper = 'ON'):
#        self.SMU.write(':SYST:BEEP:STAT %s' % beeper)

    # Enable Outputs
    def output_enable (self, channel = 1):
        if (channel == 1):
            self.SMU.write(':OUTP:STAT 1;:INIT')
        else:
            raise Exception("Invalid channel selection CH{0}" .format(channel))
    # Disable outputs
    def output_disable (self, channel = 1):
        self.SMU.write(':OUTP:STAT 0')
        if (channel != 1):
            raise Exception("Invalid channel selection CH{0}" .format(channel))
    def output(self,on=False):
        if on:
            self.output_enable(1)
        else:
            self.output_disable(1)

    def sense_4W_enable (self):
        self.SMU.write(':SYST:RSEN ON')

    def sense_4W_disable (self):
        self.SMU.write(':SYST:RSEN OFF')
    def sense_4W(self,on=False):
        if on:
            self.sense_4W_enable()
        else:
            self.sense_4W_disable()

    # Set Out V
    def set_v (self, voltage, channel = 1):
        if (channel == 1):
            self.SMU.write(":SOUR:FUNC VOLT")
            self.SMU.write(":SOUR:VOLT:MODE FIX")
            self.SMU.write(":SOUR:VOLT %f"%(voltage))
#            :SOUR:FUNC VOLT
#            :SOUR:VOLT:MODE FIX
#            :SOUR:VOLT %f
#            '''%(voltage) ))
        else:
            raise Exception("Invalid channel selection CH{0}" .format(channel))

    # Set Out I
    def set_i (self, current, channel = 1):
        if (channel == 1):
            self.SMU.write(":SOUR:FUNC CURR")
            self.SMU.write(":SOUR:CURR:MODE FIX")
            self.SMU.write(":SOUR:CURR %f"%(current))
#            self.SMU.write(textwrap.dedent ('''
#            :SOUR:FUNC CURR
#            :SOUR:CURR:MODE FIX
#            :SOUR:CURR %f
#            '''%(current) ))
        else:
            raise Exception("Invalid channel selection CH{0}" .format(channel))

    # Set Out V Limit
    def set_v_limit (self, voltage, channel = 1):
        if (channel == 1):
            self.SMU.write(":SOUR:FUNC CURR")
            self.SMU.write(":SOUR:CURR:MODE FIX")
            self.SMU.write(":SENS:VOLT:DC:PROT:LEV %f"%(voltage))
#            self.SMU.write(textwrap.dedent ('''
#            :SOUR:FUNC CURR
#            :SOUR:CURR:MODE FIX
#            :SENS:VOLT:DC:PROT:LEV %f
#            '''%(voltage) ))
        else:
            raise Exception("Invalid channel selection CH{0}" .format(channel))

    # Set Out I Limit
    def set_i_limit (self, current, channel = 1):
        if (channel == 1):
            self.SMU.write(textwrap.dedent ('''
            :SOUR:FUNC VOLT
            :SOUR:VOLT:MODE FIX
            :SENS:CURR:DC:PROT:LEV %f
            '''%(current) ))
        else:
            raise Exception("Invalid channel selection CH{0}" .format(channel))

    # Set V Range
    def set_v_range (self, voltage, channel = 1, mode = 'source'):
        if (channel == 1):
            if (mode == 'sense'):
                if (voltage != 'auto'):
                    self.SMU.write(':SENS:VOLT:RANG %f' % voltage)
                else:
                    self.SMU.write(':SENS:VOLT:DC:RANGE:AUTO 1')

            elif (mode == 'source'):
                if (voltage != 'auto'):
                    self.SMU.write(textwrap.dedent ('''
                    :SOUR:FUNC VOLT
                    :SOUR:VOLT:MODE FIX
                    :SOUR:VOLT:RANG %f
                    '''%(voltage) ))
                else:
                    self.SMU.write(':SOUR:VOLT:DC:RANGE:AUTO 1')

            else:
                raise Exception('Invalid Mode Selection ("source" or "sense")')

        else:
            raise Exception("Invalid channel selection CH{0}" .format(channel))

    # Set I Range
    def set_i_range (self, current, channel = 1, mode = 'source'):
        if (channel == 1):
            if (mode == 'sense'):
                if (current != 'auto'):
                    self.SMU.write(':SENS:CURR:RANG %f' % current)
                else:
                    self.SMU.write(':SENS:CURR:DC:RANGE:AUTO 1')

            elif (mode == 'source'):
                if (current != 'auto'):
                    self.SMU.write(textwrap.dedent ('''
                    :SOUR:FUNC CURR
                    :SOUR:CURR:MODE FIX
                    :SOUR:CURR:RANG %f
                    '''%(current) ))
                else:
                    self.SMU.write(':SOUR:CURR:DC:RANGE:AUTO 1')

            else:
                raise Exception('Invalid Mode Selection ("source" or "sense")')

        else:
            raise Exception("Invalid channel selection CH{0}" .format(channel))

    # Read V
    def read_v (self, samples = 1, channel = 1, avg_mode = 'MOV', filt = 'ON', nplc = 1):
        if (channel == 1):
            self.SMU.write(textwrap.dedent ('''
                *CLS
                :ABOR
                :ARM:COUN 1;SOUR TIM
                :FUNC 'VOLT:DC';:VOLT:NPLC %f;:AVER:TCON %s;COUN %d;STAT %s
                :FORM:ELEM:SENS VOLT
                :INIT
                ''' %(nplc, avg_mode, samples, filt)))

            self.SMU.ask('*OPC?')

            return float(self.SMU.ask(':SENSE:DATA:LAT?'))
        else:
            raise Exception("Invalid channel selection CH{0}" .format(channel))

    # Read I
    def read_i (self, samples = 1, channel = 1, avg_mode = 'MOV', filt = 'ON', nplc = 1):
        if (channel == 1):
            self.SMU.write(textwrap.dedent ('''
            *CLS
            :ABOR
            :ARM:COUN 1;SOUR TIM
            :FUNC 'CURR:DC';:CURR:NPLC %f;:AVER:TCON %s;COUN %d;STAT %s
            :FORMAT:ELEMENTS:SENSE CURR
            :INIT
            ''' %(nplc, avg_mode, samples, filt)))

            self.SMU.ask('*OPC?')

            return float(self.SMU.ask(':SENSE:DATA:LAT?'))

        else:
            raise Exception("Invalid channel selection CH{0}" .format(channel))

    # Read W
#    def read_w (self, samples=1, channel=1):
#        if (channel == 1):
#            self.SMU.write(textwrap.dedent ('''
#            :CALC:MATH:NAME "POWER"
#            :CALC:STAT ON
#            :INIT
#            ''' ))
#
#            return float(self.SMU.ask(":CALC:DATA?"))
#
#        else:
#            raise Exception("Invalid channel selection CH{0}" .format(channel))

    #Set I range for the display
    def set_range_display (self, digits = 7, channel = 1):
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
        if isUSB==False:
            self.VOLTMETER = self.rm.get_instrument("GPIB0::"+gpib+"::INSTR")
        else:
            self.VOLTMETER = self.rm.get_instrument("USB0::0x0957::0x1A07::"+gpib+"::INSTR")#USB0::0x0957::0x1A07::SN????????::INSTR

            self.VOLTMETER.write("INP:IMP:AUTO ON")
            
#        self.VOLTMETER = self.rm.get_instrument("SENS:VOLT:IMP:AUTO ON")
#        self.VOLTMETER = self.rm.get_instrument(gpib)#debug code

    def sample(self):
        read=self.VOLTMETER.ask('READ?')
#        read=self.VOLTMETER.read()
        #print( ">>>" +read+'\n')
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
            self.VOLTMETER2 = self.rm.get_instrument("GPIB0::"+gpib+"::INSTR")
            read=self.VOLTMETER2.ask('*IDN?')
#            read=self.VOLTMETER2.read()
            #print( ">>>" +self.VOLTMETER2.read()+'\n')
            self.VOLTMETER2.write('*RST')
            #print(self.channels)

    def sample(self):
        if self.isUse == True:
            self.VOLTMETER2.write('SENS:FUNC "VOLT:DC", '+self.channels    )
            self.VOLTMETER2.write('INP:IMP:AUTO ON,'+self.channels    )#
    
            self.VOLTMETER2.write('SENS:VOLT:DC:NPLC 2, '+self.channels    )
            self.VOLTMETER2.write('SENS:VOLT:DC:RANG:AUTO ON, '+self.channels    )
            self.VOLTMETER2.write('TRIG:SOUR IMM')
#            self.VOLTMETER2.write('TRIG:TIM MIN')
            self.VOLTMETER2.write('TRIG:COUNT 1.0e0')
            self.VOLTMETER2.write('INIT')
#            self.VOLTMETER2.write('*OPC?')
            read=self.VOLTMETER2.ask("*OPC?")
            #print( ">>>" + self.VOLTMETER2.read()+'\n')
            read=self.VOLTMETER2.ask('READ?')#
#            read=self.VOLTMETER2.read()
            #print( ">>>" + read+'\n')
            return read
        return 0

    def setChannel(self,chanlist):
        if self.isUse == True:
            self.channels = chanlist
#            self.VOLTMETER2.write('SYST:PRES')
            self.VOLTMETER2.write('CONF:VOLT:DC 10,1.0e-5,'+chanlist)
            self.VOLTMETER2.write('ROUT:SCAN '+chanlist)
            self.VOLTMETER2.write('ROUT:CHAN:DEL:AUTO OFF, '+chanlist    )
            self.VOLTMETER2.write('ROUT:CHAN:DEL 2e-1, '+chanlist    )
            self.VOLTMETER2.write('FORM:READ:TIME:TYPE ABS')
#            self.VOLTMETER2.write('FORM:READ:ALAR OFF')
            self.VOLTMETER2.write('FORM:READ:CHAN ON')
#            self.VOLTMETER2.write('FORM:READ:TIME OFF')
#            self.VOLTMETER2.write('FORM:READ:UNIT OFF')
            self.VOLTMETER2.write('SENS:FUNC "VOLT:DC", '+self.channels    )
            self.VOLTMETER2.write('INP:IMP:AUTO ON,'+self.channels    )#
    
#            self.VOLTMETER2.write('SENS:VOLT:DC:NPLC 2, '+self.channels    )
#            self.VOLTMETER2.write('SENS:VOLT:DC:RANG:AUTO ON, '+self.channels    )
#            self.VOLTMETER2.write('TRIG:SOUR IMM')
#            self.VOLTMETER2.write('TRIG:TIM MIN')
#            self.VOLTMETER2.write('TRIG:COUNT 1.0e0')

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
        self.CHAMBER = self.rm.get_instrument("GPIB0::"+gpib+"::INSTR")
        self.CHAMBER.ask('ROM?')
        #print( ">>>" + self.CHAMBER.read()+'\n')
#        self.CHAMBER.read()
        self.CHAMBER.ask("MODE, STANDBY")
#        self.CHAMBER.read()
        #print( ">>>" + self.CHAMBER.read()+'\n')
        if isCtrl == True:
            self.CHAMBER.ask("MODE, CONSTANT")
#            self.CHAMBER.read()
            #print(">>>"+self.CHAMBER.read()+'\n')
        
    def getTemp(self):
#        self.CHAMBER.write("TEMP?")
        read=self.CHAMBER.ask("TEMP?")
        #print( ">>>" + read+'\n')
        return read.split(',')

    def setTemp(self,temp):
        read=self.CHAMBER.ask("TEMP,s"+temp)
#        self.CHAMBER.read()
        #print( ">>>" + self.CHAMBER.read()+'\n')
        return read
        
    def close(self):
        self.CHAMBER.ask("MODE, STANDBY")
#        self.CHAMBER.read()
        #print( ">>>" + self.CHAMBER.read()+'\n')
        return True
    
    def disconnect(self,visalib):
        self.close()
        visa.VisaLibrary.gpib_control_ren(visalib, self.CHAMBER.session,6)
        visa.VisaLibrary.close(visalib, self.CHAMBER.session)
        return True

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

    def getTemp(self):
        return ['-241','-241','limit+','limit-']

    def setTemp(self,temp):
        return "dummy"
        
    def reset (self):
        pass
    
    def sense_4W(self,on=False):
        pass
        
    def set_v_limit (self, voltage, channel = 1):
        pass

    def set_i_limit (self, current, channel = 1):
        pass

    def set_v_range (self, voltage, channel = 1, mode = 'source'):
        pass

    def set_i_range (self, current, channel = 1, mode = 'source'):
        pass

    def read_v (self, samples = 1, channel = 1, avg_mode = 'MOV', filt = 'ON', nplc = 1):
        return "dummy"

    def read_i (self, samples = 1, channel = 1, avg_mode = 'MOV', filt = 'ON', nplc = 1):
        return "dummy"

    def set_v (self, voltage, channel = 1):
        pass

    def set_i (self, current, channel = 1):
        pass
        
