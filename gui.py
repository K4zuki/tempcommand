#-*- coding: utf-8 -*- 
#!/usr/bin/env python
import instr_local
import monthname
import tempcommand

import npyscreen
import visa
import usbio.usbio
import time
import datetime
import os,sys,stat
import uli


class TempCtrl(npyscreen.NPSAppManaged):
    def onStart(self):
        self.mainform=self.addForm("MAIN", MainForm, name="\tTemerature Control and measurement\t",color="GOOD" , )

    def change_form(self, name):
        self.switchForm(name)
        self.resetHistory()


class MainForm(npyscreen.ActionForm,tempcommand.tempcommand):
    TCrun=False
    isSuspend=False
    hoge=None
    outfile=None
    logfile=None
    i2c=False
    cypressbase=0x90
    uli2c=[False,False]
    cypress=-99
    def create(self): 
        self.commandset={}
        self.add_command("EOF",     self._eof)
        self.add_command("TEMP",    self._temp)
        self.add_command("SAMPLE",  self._sample)
        self.add_command("SUSPEND", self._suspend)
        self.add_command("VOLT",    self._volt)
        self.add_command("DELY",    self._delay)
        self.add_command("KIKU",    self._kikusui)
        self.add_command("BASE",    self._base)
        self.add_command("REG",     self._register)
        self.add_command("UBASE",   self._ulibase)
        self.add_command("UREG",   self._uliregister)
        self.add_command("CHAN",    self._chanset)

        self.add_command("FOR",    self._for)
        self.add_command("LOOP",    self._loop)
        
        self.scrfilename = self.add(npyscreen.TitleFilename, name = "Filename:",
            value="W:\\Tokyo\\Data\\Design Center\\Nori2\\Evaluation\\new2.txt")
        self.psu  = self.add(npyscreen.TitleText, name = "PSU:", value="24")
        self.chamber = self.add(npyscreen.TitleText, name = "Chamber:", value="16")
        self.isctrl_chamber = self.add(npyscreen.CheckBox, value = False, name="Control Temp")
        self.dmm1 = self.add(npyscreen.TitleText, name = "Multimeter1:", value="2")
        self.isUSB_dmm1= self.add(npyscreen.CheckBox, value = False, name="34461A")
        self.dmm2 = self.add(npyscreen.TitleText, name = "Multimeter2:", value="10")
        self.isuse_dmm2 = self.add(npyscreen.CheckBox, value = False, name="Use")
        self.Tcurrent = self.add(npyscreen.TitleFixedText,  name = "current temp:",
            value="    27.0 oC    >>>",max_width=40, editable=False)
        self.nextrely-=1
        self.Ttarget = self.add(npyscreen.TitleFixedText, name = "target temp:",
            value="27.0 oC", editable=False,relx=40)
        self.processing = self.add(npyscreen.TitleFixedText, name = "In process:",
            value="---",editable=False )
        self.shell = self.add(npyscreen.MultiLineEdit, scroll_end=True, value = ">>>\n", name="log:",
            multiline=True, editable=False)
        
    def shellResponse(self,string):
        self.shell.value = ">>> "+str(string)+"\n"+self.shell.value
        self.display()

    def change_forms(self, *args, **keywords):
        self.shellResponse("hoge")
        
    def on_cancel(self):
        if self.TCrun:
            self.shellResponse( " ### cancel while TCrun: make SAFE closing! ### ")
            self.display()
            time.sleep(1)
            self.exit_application()
        else:
            self.shellResponse( " ### cancel before TCrun: just close ### ")
            self.display()
            time.sleep(1)
            self.exit_application()
    
    def on_ok(self):
        if self.TCrun:
            self.shellResponse( "ok while TCrun: do nothing")
        else:
            self.scrfilename.editable=False
            self.psu.editable=False
            self.dmm1.editable=False
            self.dmm2.editable=False
            self.isuse_dmm2.editable=False
            self.chamber.editable=False
            self.isctrl_chamber.editable=False
            #vvv debug code vvv
#            self.shellResponse( " ### ok before TCrun: start run ###")
#            self.shellResponse(self.psu.get_value())
#            self.shellResponse(self.chamber.get_value())
#            self.shellResponse(self.dmm1.get_value())
#            self.shellResponse(self.dmm2.get_value())
#            self.shellResponse(str(self.isuse_dmm2.value))
#            self.shellResponse(str(self.isctrl_chamber.value))
            #^^^ debug code ^^^
            self.TCrun=True
            self.tc_run()

    def exit_application(self):
        self.parentApp.NEXT_ACTIVE_FORM = None
        self.editing = False

    def tc_run(self):
        isdebug=False
        lib=rm=False
        todaydetail = datetime.datetime.today()
        todaydir= "C:\\Users\\Public\\Documents\\"+monthname.monthname()#todaydetail.strftime("%Y.%m%b.%d")
        if os.path.exists(todaydir) !=1:
            os.mkdir(todaydir)
        filename = todaydir+"\\"+todaydetail.strftime("%H.%M.%S")+".chamber.csv"

        self.outfile = open( filename,'a' )
        self.outfile.write( os.environ['COMPUTERNAME']+"\n" )
        self.outfile.write( monthname.monthname()+"\\"+todaydetail.strftime("%H.%M.%S")+".chamber.csv"+"\n" )
        
        self.logfile=open(filename+".log",'a')

        try:
            self.cypress = usbio.usbio.autodetect()
            sys.stdout = sys.__stdout__
        except :
            npyscreen.notify_confirm(str(sys.exc_info()[1]),title="ERROR REPORT",editw=1)
            self.i2c =False
            self.cypress=-99
            self.shellResponse("no Cypress I2C connected")
        else:
            self.i2c  = usbio.usbio.I2C(self.cypress, 0x90)#0x48/7bit=0x90/8bit


        self.uli2c[0] = uli.I2C( 0, 0x90, 0)#0x48/7bit=0x90/8bit
        self.uli2c[1] = uli.I2C( 0, 0x90, 1)#0x48/7bit=0x90/8bit
        chan0=self.uli2c[0].searchI2CDev(0x90,0xFF)
        chan1=self.uli2c[1].searchI2CDev(0x90,0xFF)
        self.shellResponse(str(chan0))
        self.shellResponse(str(chan1))
        time.sleep(0.5)
        if(chan0==[]): self.uli2c[0]=False
        if(chan1==[]): self.uli2c[1]=False
        if(chan0==[] and chan1==[]):
            self.shellResponse("no SAM3U I2C connected")

        self.shellResponse( self.uli2c )
            
        self.shellResponse(self.cypress)

        try:
            lib = visa.VisaLibrary()
            rm = visa.ResourceManager()
        except :
            lib=rm=False
            self.shellResponse("no VISA connected")
            self.logfile.write("no VISA connected\n")
            
        self.display()
        currentvolt=3.7

        self.logfile.write( str( self.i2c )+"\n" )
        self.logfile.write( str(self.cypress)+"\n" )
        self.logfile.write( str( self.uli2c )+"\n" )
        self.logfile.write(str(chan0)+'\n')
        self.logfile.write(str(chan1)+'\n')
        try:
            self.E3640A = instr_local.powersupply(rm,self.psu.get_value())
            self.Chamber = instr_local.chamber(rm,self.chamber.get_value(),self.isctrl_chamber.value)
            self.A34401A = instr_local.multimeter(rm,self.dmm1.get_value(),self.isUSB_dmm1.value)
            self.A34970A = instr_local.multimeter2(rm,self.dmm2.get_value(),self.isuse_dmm2.value)
        except:
            self.E3640A = instr_local.dummy()
            self.Chamber = instr_local.dummy()
            self.A34401A = instr_local.dummy()
            self.A34970A = instr_local.dummy()
            npyscreen.notify_confirm(str(sys.exc_info()[1]),title="SUSPEND",editw=1)
            self.logfile.write("=-=-=-=-= using dummy instruments =-=-=-=-=\n")
        self.E3640A.output(True)
        
        scr = open(os.path.join(self.scrfilename.get_value()), 'r')
        script = scr.read()
        scr.close()
        self.parse(script,self.logfile)
#        self.make_list(script)
#        self.break_loop(self.commandList,self.argumentList)
#        self.parse_list(self.commandList,self.argumentList,self.logfile)
        todaydetail = datetime.datetime.today()
        self.outfile.write(todaydetail.strftime("%H.%M.%S")+" finished\n")
        self.outfile.close()
        self.logfile.close()
        os.chmod(filename,stat.S_IREAD)
        os.chmod(filename+".log",stat.S_IREAD)
        self.E3640A.disconnect(lib)
        self.Chamber.disconnect(lib)
        self.A34401A.disconnect(lib)
        self.A34970A.disconnect(lib)
        self.exit_application()

    def _eof(self,dummy=-1):
        if (self.isInLoop!=[]):#==True):
            self.shellResponse('EndOfFile triggered')
        return -1

    def _temp(self,temp=30):
        self.processing.value="TEMP"+str(temp)
        self.logfile.write( 'temperature set: '+temp+' oC\n')
        self.shellResponse( 'temperature set: '+temp+' oC')
        self.shellResponse( self.Chamber.setTemp(temp))
        time.sleep(10)
        i=0
        while 1:#release code
            i+=1#release code
            current,target,absolute,hoge = self.Chamber.getTemp()
            diff=abs(float(current)-float(target))
            self.logfile.write ( current+","+target+","+absolute+","+hoge+","+str(diff)+"\n")
            self.shellResponse ( str(i)+",\t current="+current+",\t target="+target+",\t limit="+absolute+","+hoge+",\t "+str(diff))
            if diff < 0.2:
                break
            time.sleep(10)#release code

        self.logfile.write( 'reached target')
        self.shellResponse( 'reached target')
        self.outfile.write(temp+"oC\n")
        return 0

#    def _temp(self,temp=30):
#        if (self.isInLoop!=[]):#==True):
#            self.lpContain.append("TEMP"+str(temp))
#        else:
#            self.__temp(temp)
#        return 0

    def _sample(self,dummy=-1):
        self.processing.value="SAMPLE"
        self.logfile.write( 'sample triggered')
        self.shellResponse( 'sample triggered')
        current,target,absolute,hoge = self.Chamber.getTemp()
        read=",,,"+current+","+str( self.E3640A.read())+","+str( self.A34401A.sample())+","+str( self.A34970A.sample())
        self.outfile.write(read+"\n")
        return 0

#    def _sample(self,dummy=-1):
#        if (self.isInLoop!=[]):#==True):
#            self.lpContain.append("SAMPLE")
#        else:
#            self.__sample(dummy)
#        return 0

    def _suspend(self,dummy=-1):
        self.logfile.write( 'suspend triggered->')
        self.shellResponse( 'suspend triggered')

        self.parentApp.change_form("SUB")
        npyscreen.notify_confirm("\n\t\t-=-=-=-SUSPEND-=-=-=-\n"+\
            "I would like more flexible popup which runs temp check in buckground but for now this is the solution as this works anyway..."
            ,title="SUSPEND",editw=1)

        self.logfile.write( 'popup end')
        self.shellResponse( 'return from popup')
        return 0

#    def _suspend(self,dummy=-1):
#        if (self.isInLoop!=[]):#==True):
#            self.lpContain.append("SUSPEND")
#        else:
#            self.__suspend(dummy)
#        return 0
    
    def _volt(self,volt=3.0):
        self.processing.value="VOLT"+str(volt)
        self.logfile.write( 'voltage set: '+volt+' V')
        self.shellResponse( 'voltage set: '+volt+' V')
        self.outfile.write(volt+'V\n')
        self.E3640A.SetVoltage(volt)
        return 0

#    def _volt(self,volt=3.0):
#        if (self.isInLoop!=[]):#==True):
#            self.lpContain.append("VOLT"+str(volt))
#        else:
#            self.__volt(volt)
#        return 0
        
    def _delay(self,delay=1):
        self.processing.value="DELY"+str(delay)
        self.shellResponse( 'wait for: '+delay+' minutes')
        for i in range(6 * int(delay)):
            current,target,absolute,hoge = self.Chamber.getTemp()
            self.shellResponse(str(i)+","+current+","+target+","+absolute+","+hoge)
            time.sleep(10)
        return 0

#    def _delay(self,delay=1):
#        if (self.isInLoop!=[]):#==True):
#            self.lpContain.append("DELY"+str(delay))
#        else:
#            self.__delay(delay)
#        return 0
    
    def _kikusui(self,current=0.001):
        self.logfile.write( 'current set: '+current+' A')
        self.shellResponse( 'current set: '+current+' A')
        return 0
    
    def _base(self,baseaddr=0x90):
        baseaddr=int(baseaddr)
        self.processing.value="BASE"+str(baseaddr)
        self.logfile.write( 'i2c slave address set: 0x'+str(baseaddr))
        self.shellResponse( 'i2c slave address set: 0x'+str(baseaddr))
        self.i2c = usbio.usbio.I2C(self.cypress, baseaddr)
        self.outfile.write("SLAVE = 0x"+str(baseaddr)+",(8it)\n")
        return 0
   
#    def _base(self,baseaddr=0x90):
#        if (self.isInLoop!=[]):#==True):
#            self.lpContain.append("BASE"+str(baseaddr))
#        else:
#            self.__base(baseaddr)
#        return 0

    def _register(self,argument):
        self.processing.value="REG"+str(argument)
        i2creg,i2cdata=argument.split('=')
        i2creg= int(i2creg ,16)
        i2cdata= int(i2cdata ,16)
        self.logfile.write( 'reg address = 0x%02X, data = 0x%02X' %( i2creg ,i2cdata ))
        self.shellResponse( 'reg address = 0x%02X, data = 0x%02X' %( i2creg ,i2cdata ))
        if self.cypress==-99 :pass
        else:
            self.i2c.write_register( i2creg, i2cdata )
        self.outfile.write( ',reg%02Xh =, 0x%02X\n' %( i2creg ,i2cdata ))
        return 0

#    def _register(self,argument):
#        if (self.isInLoop!=[]):#==True):
#            self.lpContain.append("REG"+str(argument))
#        else:
#            self.__register(argument)
#        return 0
        
    def _ulibase(self,argument):#UBASEx[+y]=zz -> channel=x[and y], baseaddress=zz
        self.processing.value="UBASE"+str(argument)
        ulichan,ulibase= argument.split('=')
        channels=ulichan.split('+')
        if len(channels)>1:
            ulichan = [channels[0], channels[1]]
        else:
            ulichan = [channels[0]]
        ulibase= int(ulibase, 16)
        for f in ulichan:
            if self.uli2c[int(f)]==False:
                pass
            else:
                self.uli2c[int(f)]= uli.I2C( 0, ulibase, int(f))#0x48/7bit=0x90/8bit
            self.outfile.write("SLAVE= 0x%02X,CH= %d (8bit)\n" %(ulibase, int(f)))
            self.shellResponse( 'i2c slave address set: 0x%02X of channel %d' %(ulibase, int(f)) )
            self.logfile.write( 'i2c slave address set: 0x%02X of channel %d\n' %(ulibase, int(f)))
        return 0

#    def _ulibase(self,argument):#UBASEx[+y]=zz -> channel=x[and y], baseaddress=zz
#        if (self.isInLoop!=[]):#==True):
#            self.lpContain.append("UBASE"+str(argument))
#        else:
#            self.__ulibase(argument)
#        return 0
        
    def _uliregister(self,argument):#UREGx[+y]:aa=bb -> channel=x[and y],reg=aa,data=bb
        self.processing.value="UREG"+str(argument)
        ulichan,i2cdata=argument.split(':')
        ulireg,ulidata=i2cdata.split('=')
        channels=ulichan.split('+')
#        self.logfile.write( str(channels)+'\n')
        if len(channels)>1:
            ulichan=[channels[0],channels[1]]
        else:
            ulichan=[channels[0]]
        ulireg= int(ulireg ,16)
        ulidata= int(ulidata ,16)
        for f in ulichan:
            if self.uli2c[int(f)]==False:
                pass
            else:
                self.uli2c[int(f)].write_register( ulireg, ulidata )
            self.outfile.write( 'channel %d,reg%02Xh =, 0x%02X\n' %( int(f), ulireg, ulidata ))
            self.shellResponse( 'channel = %d, reg address = 0x%02X, data = 0x%02X'     %( int(f), ulireg, ulidata ))
            self.logfile.write( 'channel = %d, reg address = 0x%02X, data = 0x%02X\n'   %( int(f), ulireg, ulidata ))
        return 0

#    def _uliregister(self,argument):#UREGx[+y]:aa=bb -> channel=x[and y],reg=aa,data=bb
#        if (self.isInLoop!=[]):#==True):
#            self.lpContain.append("UREG"+str(argument))
#        else:
#            self.__uliregister(argument)
#        return 0

    def _chanset(self,channels):
        self.processing.value="CHAN"+str(channels)
        self.logfile.write( 'set channels(@'+channels.replace('+',',')+')')
        self.shellResponse( 'set channels(@'+channels.replace('+',',')+')')
        self.A34970A.setChannel('(@'+channels.replace('+',',')+')')
        return 0
    
#    def _chanset(self,channels):
#        if (self.isInLoop!=[]):#==True):
#            self.lpContain.append("CHAN"+str(channels))
#        else:
#            self.__chanset(channels)
#        return 0

    def _for(self,argument=1):
#        self.isInLoop.append(True)
        self.logfile.write( str(self.isInLoop) )
        var=argument.split(";")
        self.logfile.write( str(var))
        lst=var[0].split("+")
        self.logfile.write( str(lst))
        for var[0] in lst:
            self.logfile.write( str(var[1])+str(var[0]))
            self.lpHeader.append(str(var[1])+str(var[0]))
        return 0

    def _loop(self,dummy=-1):
        if (self.isInLoop!=[]):#==True):
            self.isInLoop.pop()
            for head in self.lpHeader:
                self.parse(head,self.logfile)
                for commd in self.lpContain:
                    self.parse(commd,self.logfile)
                
            self.logfile.write( 'end of loop')
        return 0
    

if __name__ == '__main__':
    TC = TempCtrl()
    TC.run()
    sys.stdout = sys.__stdout__
    raw_input("\t -------- measurement finished (Enter key to exit) --------\n\n\n\n\n\n\n\n\n\n\n")

