# import npyscreen
import time
import sys
import traceback

## tempcommand: temperature chamber controller base class
class tempcommand():
    ## @var commandset
    #defines commands and callback functions
    commandset = {}

    ## @var commandList
    #contains whole command list read from script
    commandList = []

    ## @var argumentList
    #contains whole argument list read from script
    argumentList = []

    ## constructor
    def __init__(self):
        self.commandset = {}

    ## parse()
    # makes whole command list from script, cut off after first EOF,
    # destruct loops(break_loop()) and execute them all(parse_list())
    # @param script script (command list) file
    # @param logfile log output file
    def parse(self, script, logfile):
        count_eof = 0
        self.make_list(script)
        if(self.commandList.count("EOF")>1):
            count_eof = self.commandList.index("EOF")
            self.commandList = self.commandList[:count_eof]
            self.argumentList = self.argumentList[:count_eof]
        if(self.commandList.count("FOR")!=self.commandList.count("LOOP")):
            print "error",commandlist.count("FOR"),argumentlist.count("LOOP")
        else:
            self.break_loop(self.commandList,self.argumentList)
            self.parse_list(self.commandList,self.argumentList,logfile)
        return True

    ## make_list()
    # called from parse()
    # makes command list from read script
    # @param script script(command list) file
    def make_list(self, script):
        for line in script.split('\n'):
            for words in line.split('//')[0].split(','):
                word = ["".join(words.split())]
                for command in word:
                    command = command.upper()
                    if command.split()==[]:continue
                    for comd, func in self.commandset.iteritems():
                        read = command.split(comd)
                        if(read[0])=='':
                            try:
                                self.commandList.append(comd)
                                self.argumentList.append(read[1])

                            except:
                                print(
                                "".join(traceback.format_tb(sys.exc_info()[2]))+": "\
                                +str(sys.exc_info()[1]))

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

#0. list up index number(s) of both FOR and LOOP
#1. pop *biggest* FOR and get index number
#2. scan LOOP from smaller number
#3. find the best LOOP; the first LOOP which has bigger index number than FOR's one
#4. pop the LOOP
#5. destract the loop
#6. if FOR remains in the whole list, go to #1

    ## break_loop()
    # called from parse()
    # find FOR loop and cut then call _break_loop() to destruct
    # @param c_list command list
    # @param a_list argument list
    # @return destructed (c_list, a_list)
    def break_loop(self, c_list, a_list):
        c_temp = c_list[:]
        F_index = []
        L_index = []
        result = []
        c_result = []
        a_result = []
        """count FORs and LOOPs"""
        if(c_list.count("FOR") > 0): # if any FOR found
            for hoge in range(len(c_list)): # search in command list
                if c_list[hoge] == "FOR": # if FOR is found
                    F_index.append(hoge) # index added into FOR's list
                elif c_list[hoge] == "LOOP": # if LOOP is found
                    L_index.append(hoge) # index added into LOOP's list
            while(len(F_index) > 0): # while any FOR remains
                hoge = F_index.pop() # pop FOR's biggest index
                for foo in range(len(L_index)): # search over remaining LOOPs
                    if L_index[foo] > hoge: # if index(LOOP) > max_index(FOR)
                        break # break for loop

                foo = L_index.pop(foo) # pop hit LOOP index
                result.append([hoge,foo]) # result = [ [...], [...], [max_index(FOR), hit_index(LOOP)] ]
            result.reverse() # result = [ [smallest FOR], [2nd smallest], [...], ..., [largest FOR] ]
            result = result.pop() # result = [ largest FOR pair ]
            c_result,a_result = self._break_loop(   c_list[result[0]:result[1]],
                                                    a_list[result[0]:result[1]] )

            for hoge in range(len(c_list[result[0]:result[1]+1])):
                c_list.pop(result[0])
                a_list.pop(result[0])
            for hoge in range(len(c_result)):
                c_list.insert(result[0], c_result.pop())
                a_list.insert(result[0], a_result.pop())
            self.break_loop(c_list, a_list)

        return c_list, a_list
        pass

    ## _break_loop
    # called from break_loop()
    # destructs FOR loop into command and argument list
    # @param c_list command list
    # @param a_list argument list
    def _break_loop(self, c_list, a_list):
        c_result = []
        a_result = []
        var = a_list[0].split(";")
        a_lst = var[0].split("+")
        c_lst = var[1].split("|")
        for arg in a_lst:
            for cmd in c_lst:
                for comd, func in self.commandset.iteritems():
                    read = (str(cmd)+str(arg)).split(comd)
                    if(read[0])=='':
                        c_result.append(comd)
                        a_result.append(read[1])
            for hoge in c_list[1:]:
                c_result.append(hoge)
            for foo in a_list[1:]:
                a_result.append(foo)

        return (c_result,a_result)
        pass

    ## parse_list()
    # called from parse()
    # executes all listed commands
    # @param comlist command list
    # @param arglist argument list
    # @param logfile log output file
    def parse_list(self,comlist,arglist,logfile):
        execute = -1
        cnt = 0
        for command in comlist:
            try:
                execute = self.commandset[command][0](arglist[cnt])
            except:
                print("".join(traceback.format_tb(sys.exc_info()[2]))+": "
                    +str(sys.exc_info()[1]))

            logfile.write('\n')
            if execute==-1:break
            cnt+=1

        return True

    ## add_command
    # adds command and casllback functions as dictionary pair
    # @param command command; must be large character
    # @param func callback function; should be started with '_'
    def add_command(self,command,func):
        self.commandset[command] = [func]

    def _eof(self,dummy = -1):
        print 'EndOfFile'
        return -1

    commandset["EOF"] = [_eof]

    def _temp(self,temp = 30):
        print 'set temp: '+temp+' oC'
        return 0

    commandset["TEMP"] = [_temp]

    def _sample(self,dummy = -1):
        print 'Sample'
        return 0

    commandset["SAMPLE"] = [_sample]

    def _suspend(self,dummy = -1):
        print 'Suspend'
        return 0

    commandset["SUSPEND"] = [_suspend]

    def _volt(self,v = 3.0):
        print 'set voltage: '+v
        return 0

    commandset["VOLT"] = [_volt]

    def _delay(self,_wait = 1):
        print 'wait for: '+_wait+' minutes'
        return 0

    commandset["DELY"] = [_delay]

    def _kikusui(self,current = 0.001):
        print 'set current: '+current+' A'
        return 0

    commandset["KIKU"] = [_kikusui]

    def _base(self,baseaddr = 0x90):
        print 'set base address: 0x'+baseaddr
        return 0

    commandset["BASE"] = [_base]

    def _ulibase(self,argument):
        ulichan,ulibase= argument.split('=')
        print 'i2c slave address set: 0x%X of channel %d'%(int(ulibase,16),int(ulichan,16))
        return 0

    commandset["UBASE"] = [_ulibase]

    def _register(self,argument):
        i2creg,i2cdata = argument.split('=')
        print 'reg address = 0x%03X, data = 0x%02X' %( int(i2creg,16),int(i2cdata,16) )
        return 0

    commandset["REG"] = [_register]

    def _chanset(self,channels):
        print 'set channels @'+channels
        return 0

    commandset["CHAN"] = [_chanset]

    def _repeat(self,times = 1):
        print 'repeat '+times+' times'
        return 0

    commandset["REPEAT"] = [_repeat]

    def _loop(self,dummy = -1):
        print 'loop'
        return 0

    commandset["LOOP"] = [_loop]

if __name__ == '__main__':
    import tempcommand
    def _temp(temp = 30):
        print 'set temp: '+str(temp)+' oC'
        return 0

    def _for(argument = '1'):
        print argument
        var = argument.split(";")
        lst = var[0].split("+")
        for var[0] in lst:
            self.lpHeader.append(str(var[1])+str(var[0]))
        return 0

    def _loop(dummy = '-1'):
        if (self.isInLoop!=[]):#==True):
            self.isInLoop.pop()
            for head in self.lpHeader:
                self.parse(head,self._logfile)
                for commd in self.lpContain:
                    self.parse(commd,self._logfile)
        return 0

    def _sample(dummy = -1):
#        global parser
#        if (parser.isInLoop!=[]):
#            parser.lpContain.append("SAMPLE")
#            print 'Sample in loop'
#        else:
        print 'Sample'
        return 0

    def _register(argument):
        global parser
        i2creg,i2cdata = argument.split('=')
#        if (parser.isInLoop!=[]):
#            parser.lpContain.append("REG"+argument)
#            print 'reg address = 0x%03X, data = 0x%02X in inner loop' %( int(i2creg,16),int(i2cdata,16) )
#        else:
        print 'reg address = 0x%03X, data = 0x%02X' %( int(i2creg,16),int(i2cdata,16) )
        return 0

    def _chanset(channels):
        global parser
#        if (parser.isInLoop!=[]):
#            parser.lpContain.append("CHAN"+channels)
#            print 'set channels @'+channels
#        else:
        print 'set channels @'+channels
        return 0

    def _delay(_wait = 1):
        global parser
#        if (parser.isInLoop!=[]):
#            parser.lpContain.append("DELY"+_wait)
#            print 'wait for: '+_wait+' minutes'
#        else:
        print 'wait for: '+_wait+' minutes'
        return 0

    def _repeat(times = 1):
        print 'repeat '+times+' times'
        return 0

    try:
        parser = tempcommand.tempcommand()
        logfile = open("hoge.log",'a')
        parser.add_command("TEMP",parser._temp)
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
            chan105+110
            reg00=ff
            for -40+0+100; TEMP
                dely1
                sample
                for 00+02+04; reg00=
                    sample
                LOOP
                for 0c+0e; reg02=
                    for 00+02+04; reg01=|regAA=
                        sample
                    LOOP
                LOOP
                suspend
            LOOP
            suspend
            EOF
            sample
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
    finally:
        print("-=-=- debug mode done. -=-=-")
