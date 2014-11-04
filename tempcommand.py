import npyscreen
import time
import sys
import traceback

class tempcommand():
    commandset={}
    isInLoop=[]
    lpContain=[]
    lpHeader=[]
    commandList=[]
    argumentList=[]
    def __init__(self):
        self.commandset={}
    
    def perse(self,script,logfile):
#        pass
        execute=-1
        for line in script.split('\n'):
#            if self.cypress==0:  self.i2c  = usbio.usbio.I2C(self.cypress, 0x90)
            
            for words in line.split('//')[0].split(','):
                word=["".join(words.split())]
#                word=["".join(word)]
#                print words,word
                for command in word:
                    time.sleep(0.1)
                    command=command.upper()
                    if command.split()==[]:continue
                    for comd, func in self.commandset.iteritems():
                        read=command.split(comd)
                        if(read[0])=='':
                            try:
                                execute=self.commandset[comd][0](read[1])
                            except:
                                #raw_input(str(comd)+": "+str(sys.exc_info()[1]))

                                npyscreen.notify_confirm(str(comd)+str(read[1])+": "+str(traceback.print_tb(sys.exc_info()[2],None,logfile)),title="SUSPEND",editw=1)

                            logfile.write('\n')
                            if execute==-1:break
                    else: continue
                    break
                    
                else:
                    continue
                break
            else:
                continue
            break
            
        return True

    def make_list(self,script):
#        execute=-1
        for line in script.split('\n'):
            for words in line.split('//')[0].split(','):
                word=["".join(words.split())]
                for command in word:
                    command=command.upper()
                    if command.split()==[]:continue
#                    self.List.append(command)
                    for comd, func in self.commandset.iteritems():
                        read=command.split(comd)
                        if(read[0])=='':
                            try:
#                                print comd
                                self.commandList.append(comd)
                                self.argumentList.append(read[1])
                                #execute=self.commandset[comd][0](read[1])
                            except:
                                npyscreen.notify_confirm(str(comd)+": "+str(sys.exc_info()[1]),title="SUSPEND",editw=1)

#                            logfile.write('\n')
#                            if execute==-1:break
                    else: continue
                    break
                    
                else:
                    continue
                break
            else:
                continue
            break
            
        return True
        
    def perse_list(self,comlist,arglist,logfile):
        execute=-1
        cnt=0
        isincludeloop=True
        reverse=comlist[:]
        reverse.reverse()
        lpcom=[]
        lparg=[]
        try:
            hitp=comlist.index('FOR')
            hitn=reverse.index('LOOP')
            lpcom=commandList[hitp+1:-1*(hitn+1)]
            lparg=argumentList[hitp+1:-1*(hitn+1)]
        except:
            isincludeloop=False

        for command in comlist:
            try:
                #print command
#                        self.commandList.append(comd)
#                        self.argumentList.append(read[1])
                execute=self.commandset[command][0](arglist[cnt])
            except:
                npyscreen.notify_confirm(str(command)+": "+str(sys.exc_info()[1]),title="SUSPEND",editw=1)

            logfile.write('\n')
            if execute==-1:break
            cnt+=1

        return True

    def add_command(self,command,func):
        self.commandset[command] = [func]
    
    def _eof(self,dummy=-1):
        print 'EndOfFile'
        return -1
        
    commandset["EOF"]=[_eof]
    
    def _temp(self,temp=30):
        print 'set temp: '+temp+' oC'
        return 0
        
    commandset["TEMP"]=[_temp]
    
    def _sample(self,dummy=-1):
        print 'Sample'
        return 0
        
    commandset["SAMPLE"]=[_sample]
    
    def _suspend(self,dummy=-1):
        print 'Suspend'
        return 0
        
    commandset["SUSPEND"]=[_suspend]
    
    def _volt(self,v=3.0):
        print 'set voltage: '+v
        return 0
        
    commandset["VOLT"]=[_volt]
    
    def _delay(self,_wait=1):
        print 'wait for: '+_wait+' minutes'
        return 0
        
    commandset["DELY"]=[_delay]
    
    def _kikusui(self,current=0.001):
        print 'set current: '+current+' A'
        return 0
        
    commandset["KIKU"]=[_kikusui]
    
    def _base(self,baseaddr=0x90):
        print 'set base address: 0x'+baseaddr
        return 0
        
    commandset["BASE"]=[_base]
    
    def _ulibase(self,argument):
        ulichan,ulibase= argument.split('=')
        print 'i2c slave address set: 0x%X of channel %d'%(int(ulibase,16),int(ulichan,16))
        return 0
        
    commandset["UBASE"]=[_ulibase]
    
    def _register(self,argument):
        i2creg,i2cdata=argument.split('=')
        print 'reg address = 0x%03X, data = 0x%02X' %( int(i2creg,16),int(i2cdata,16) )
        return 0
        
    commandset["REG"]=[_register]
    
    def _chanset(self,channels):
        print 'set channels @'+channels
        return 0
        
    commandset["CHAN"]=[_chanset]
    
    def _repeat(self,times=1):
        print 'repeat '+times+' times'
        return 0
        
    commandset["REPEAT"]=[_repeat]
    
    def _loop(self,dummy=-1):
        print 'loop'
        return 0
        
    commandset["LOOP"]=[_loop]
    
    #print commandset["LOOP"]
    
if __name__ == '__main__':
    import tempcommand
    def _temp(temp=30):
        print 'set temp: '+str(temp)+' oC'
        return 0

    def _for(times=1):
        global perser,logfile
#        print perser,perser.perse
        perser.isInLoop.append(True)
#        print perser.isInLoop
        var=times.split(";")
#        print var
        lst=var[0].split("+")
#        print lst
        for var[0] in lst:
            print str(var[1])+str(var[0])
            perser.lpHeader.append(str(var[1])+str(var[0]))
#            perser.perse(str(var[2])+str(var[1]),logfile)
#        print 'repeat for '+times+' :'
        return 0

    def _loop(dummy=-1):
        global perser,logfile
        print perser.lpHeader
        print perser.lpContain
        if (perser.isInLoop[0]==True):
            perser.isInLoop.pop(0)
            for head in perser.lpHeader:
                perser.perse(head,logfile)
                for commd in perser.lpContain:
                    perser.perse(commd,logfile)
                
            print 'end of loop'
#        print perser.isInLoop

#        print 'loop'
        return 0

    def _sample(dummy=-1):
        global perser
#        print perser.lpContain
        if (perser.isInLoop!=[]):
            perser.lpContain.append("SAMPLE")
            print 'Sample in loop'
        else:
            print 'Sample'
        return 0

    def _register(argument):
        global perser
        i2creg,i2cdata=argument.split('=')
#        print perser.lpContain
        if (perser.isInLoop!=[]):
            perser.lpContain.append("REG"+argument)
            print 'reg address = 0x%03X, data = 0x%02X in inner loop' %( int(i2creg,16),int(i2cdata,16) )
        else:
            print 'reg address = 0x%03X, data = 0x%02X' %( int(i2creg,16),int(i2cdata,16) )
        return 0
        
    def _chanset(channels):
        global perser
#        print 'set channels @'+channels
        if (perser.isInLoop!=[]):
            perser.lpContain.append("CHAN"+channels)
            print 'set channels @'+channels
        else:
            print 'set channels @'+channels
        return 0
        
    def _delay(_wait=1):
        global perser
#        print 'set channels @'+channels
        if (perser.isInLoop!=[]):
            perser.lpContain.append("DELY"+_wait)
            print 'wait for: '+_wait+' minutes'
        else:
            print 'wait for: '+_wait+' minutes'
        return 0

    def _repeat(times=1):
        print 'repeat '+times+' times'
        return 0

    try:
        perser=tempcommand.tempcommand()
        logfile=open("hoge.log",'a')
        perser.add_command("TEMP",_temp)
        perser.add_command("EOF",perser._eof)
        perser.add_command("FOR",_for)
        perser.add_command("SAMPLE",_sample)
        perser.add_command("LOOP",_loop)
        perser.add_command("REG",_register)
        perser.add_command("CHAN",_chanset)
        perser.add_command("DELY",_delay)
#        perser.add_command("REPEAT",_repeat)
        print perser.commandList
        print perser.argumentList
#        script=
        perser.make_list(
            """chan105
            reg00=ff
            for -40+-20+0+20+30+40+60+80+100+120+140; TEMP
                dely1
                sample
                for 00+02+04+06+08+0a+0c+0e; reg00=
                    sample
                LOOP
                suspend
                temp20
            LOOP
            suspend
            sample
            EOF
            """
        )
        print perser.commandList
#        print perser.argumentList
        reverse=perser.commandList[:]
        reverse.reverse()
        print reverse
#        print ""
        hitp=perser.commandList.index('FOR')
        hitn=reverse.index('LOOP')
#        print perser.commandList[hitp+1:-1*(hitn+1)]
#        print perser.argumentList[hitp+1:-1*(hitn+1)]
        perser.perse(
            """
            for -40+-20+0+20+30+40+60+80+100+120+140; TEMP
                dely1
                chan105,reg00=ff,SAMPLE
                chan106,regff=00,SAMPLE
            loop
            EOF
            """,
            logfile)
    except:
        raw_input(str(sys.exc_info()[1]))
    else:
        print("-=-=- debug mode done. -=-=-")
        
    
