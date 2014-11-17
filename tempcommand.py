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
    
    def parse(self,script,logfile):
        count_eof=0
        self.make_list(script)
        if(self.commandList.count("EOF")>1):
            count_eof=self.commandList.index("EOF")
            self.commandList=self.commandList[:count_eof]
            self.argumentList=self.argumentList[:count_eof]
        if(self.commandList.count("FOR")!=self.commandList.count("LOOP")):
            print "error",commandlist.count("FOR"),argumentlist.count("LOOP")
        else:
            self.break_loop(self.commandList,self.argumentList)
            self.parse_list(self.commandList,self.argumentList,logfile)
        return True

    def make_list(self,script):
        for line in script.split('\n'):
            for words in line.split('//')[0].split(','):
                word=["".join(words.split())]
                for command in word:
                    command=command.upper()
                    if command.split()==[]:continue
                    for comd, func in self.commandset.iteritems():
                        read=command.split(comd)
                        if(read[0])=='':
                            try:
                                self.commandList.append(comd)
                                self.argumentList.append(read[1])
                            except:
                                npyscreen.notify_confirm("".join(traceback.format_tb(sys.exc_info()[2]))+": "
                                    +str(sys.exc_info()[1]),title="ERROR REPORT",editw=1)

                    else: continue
                    break
                    
                else:
                    continue
                break
            else:
                continue
            break
            
        if(self.commandList.count("FOR")!=self.commandList.count("LOOP")):
            print "error",commandlist.count("FOR"),argumentlist.count("LOOP")

        return True
        
#1. pop biggest FOR
#2. scan LOOP from bigger number
#3. (LOOP>FOR) && minimum(abs(LOOP-FOR)) is the best LOOP
#4. pop the LOOP
#5. break the loop

    def break_loop(self,c_list,a_list):
        c_temp=c_list[:]
        F_index = []
        L_index = []
        result=[]
        c_result=[]
        a_result=[]
        
        if(c_list.count("FOR")>0):
            for hoge in range(len(c_list)):
                if c_list[hoge] == "FOR":
                    F_index.append(hoge)
                elif c_list[hoge] == "LOOP":
                    L_index.append(hoge)
            i=0
            while(len(F_index)>0):
                hoge=F_index.pop()
                i=0
                for foo in range(len(L_index)):
                    if L_index[foo]>hoge:
                        break
                        
                foo=L_index.pop(foo)
                result.append([hoge,foo])
            result.reverse()
            result=result.pop()
            c_result,a_result = self._break_loop( c_list[result[0]:result[1]],
                                    a_list[result[0]:result[1]])
            for hoge in range(len(c_list[result[0]:result[1]+1])):
                c_list.pop(result[0])
                a_list.pop(result[0])
            for hoge in range(len(c_result)):
                c_list.insert(result[0],c_result.pop())
                a_list.insert(result[0],a_result.pop())
            self.break_loop(c_list,a_list)

        return c_list,a_list
        pass
        
    def _break_loop(self, c_list, a_list):
        c_result=[]
        a_result=[]
        var=a_list[0].split(";")
        lst=var[0].split("+")
        for var[0] in lst:
            for comd, func in self.commandset.iteritems():
                read=(str(var[1])+str(var[0])).split(comd)
                if(read[0])=='':
                    c_result.append(comd)
                    a_result.append(read[1])
                    for hoge in c_list[1:]:
                        c_result.append(hoge)
                    for foo in a_list[1:]:
                        a_result.append(foo)

        return (c_result,a_result)
        pass
        
    def parse_list(self,comlist,arglist,logfile):
        execute=-1
        cnt=0
        for command in comlist:
            try:
                execute=self.commandset[command][0](arglist[cnt])
            except:
                npyscreen.notify_confirm("".join(traceback.format_tb(sys.exc_info()[2]))+": "
                    +str(sys.exc_info()[1]),title="ERROR REPORT",editw=1)

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
    
if __name__ == '__main__':
    import tempcommand
    def _temp(temp=30):
        print 'set temp: '+str(temp)+' oC'
        return 0

    def _for(times=1):
        global parser,logfile
        parser.isInLoop.append(True)
        var=times.split(";")
        lst=var[0].split("+")
        for var[0] in lst:
            print str(var[1])+str(var[0])
            parser.lpHeader.append(str(var[1])+str(var[0]))
        return 0

    def _loop(dummy=-1):
        global parser,logfile
        print parser.lpHeader
        print parser.lpContain
        if (parser.isInLoop[0]==True):
            parser.isInLoop.pop(0)
            for head in parser.lpHeader:
                parser.parse(head,logfile)
                for commd in parser.lpContain:
                    parser.parse(commd,logfile)
                
            print 'end of loop'
        return 0

    def _sample(dummy=-1):
        global parser
        if (parser.isInLoop!=[]):
            parser.lpContain.append("SAMPLE")
            print 'Sample in loop'
        else:
            print 'Sample'
        return 0

    def _register(argument):
        global parser
        i2creg,i2cdata=argument.split('=')
        if (parser.isInLoop!=[]):
            parser.lpContain.append("REG"+argument)
            print 'reg address = 0x%03X, data = 0x%02X in inner loop' %( int(i2creg,16),int(i2cdata,16) )
        else:
            print 'reg address = 0x%03X, data = 0x%02X' %( int(i2creg,16),int(i2cdata,16) )
        return 0
        
    def _chanset(channels):
        global parser
        if (parser.isInLoop!=[]):
            parser.lpContain.append("CHAN"+channels)
            print 'set channels @'+channels
        else:
            print 'set channels @'+channels
        return 0
        
    def _delay(_wait=1):
        global parser
        if (parser.isInLoop!=[]):
            parser.lpContain.append("DELY"+_wait)
            print 'wait for: '+_wait+' minutes'
        else:
            print 'wait for: '+_wait+' minutes'
        return 0

    def _repeat(times=1):
        print 'repeat '+times+' times'
        return 0

    try:
        parser=tempcommand.tempcommand()
        logfile=open("hoge.log",'a')
        parser.add_command("TEMP",_temp)
        parser.add_command("EOF",parser._eof)
        parser.add_command("FOR",_for)
        parser.add_command("SAMPLE",_sample)
        parser.add_command("LOOP",_loop)
        parser.add_command("REG",_register)
        parser.add_command("CHAN",_chanset)
        parser.add_command("DELY",_delay)
#        print "_command_",parser.commandList
#        print "_argument_",parser.argumentList
        parser.make_list(
            """
            chan105
            reg00=ff
            for -40+0+100; TEMP
                dely1
                sample
                for 00+02+04; reg00=
                    sample
                LOOP
                for 0c+0e; reg00=
                    for 00+02+04; reg00=
                        sample
                    LOOP
                LOOP
                suspend
            LOOP
            suspend
            sample
            EOF
            """
        )
#        print parser.commandList
        parser.break_loop(parser.commandList,parser.argumentList)
        parser.parse_list(parser.commandList,parser.argumentList,logfile)
#        raw_input("hoge")
#        reverse=parser.commandList[:]
#        reverse.reverse()
#        print reverse
#        hitp=parser.commandList.index('FOR')
#        hitn=reverse.index('LOOP')
#        parser.parse(
#            """
#            for -40+-20+0+20+30+40+60+80+100+120+140; TEMP
#                dely1
#                chan105,reg00=ff,SAMPLE
#                chan106,regff=00,SAMPLE
#            loop
#            EOF
#            """,
#            logfile)
    except:
        raw_input(str(sys.exc_info()[1]))
    else:
        print("-=-=- debug mode done. -=-=-")
        
    
