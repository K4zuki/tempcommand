# -*- coding: utf-8 -*-

import shlex
import pprint

tokens = shlex.shlex(
"""
chan(105,110);
base(90); ubase(0,1: 90);
reg(00 : ff);
ureg(0,1: 00 : ff);
TEMP(25);
base(D2); ubase(0,1: D2);
    reg(41:00); for(reg:42:02,B0,A9,8A,A7,A8,B1){}
    ureg(0,1:41:00); for(ureg:0,1:42:02,B0,A9,8A,A7,A8,B1){}
    # ureg(1:41:00); for(ureg:1:42:02,B0,A9,8A,A7,A8,B1){}
    reg(47:01);
    # ureg(0,1:47:01);

for(TEMP:  -40,0,100 )
{
    dely(1); sample();
    for(reg: 00: 00,02,04)
    {
        sample();
    }
    for(reg: 02: 0c,0e)
    {
        for(reg: 01,0A: 00,02,04)
        {
            sample();
            sample();
        }
    }
    suspend;
}
suspend;
EOF;
sample
""".upper()
)

def nop(arg):
    tok,idx,cmd,arg = arg
    print cmd,arg
    # return idx

def reg(arg):
    tok,idx,cmd,arg = arg
    arg = arg.strip(";")
    arg = arg.strip("{")
    arg = arg.strip("(")
    arg = arg.strip(")")
    arg = arg.split(":")
    print cmd,arg
    # return idx

def end(arg):
    tok,idx,cmd,arg = arg
    print "LOOP"
    # return idx

def suspend(arg):
    tok,idx,cmd,arg = arg
    print(" SUSPEND: press return to continue ".center(80, "#"))
    raw_input()
    # return idx

def found_for(arg):
    __tok,idx,cmd,arg = arg
    arg = arg.strip(";")
    arg = arg.strip("{")
    arg = arg.strip("(")
    arg = arg.strip(")")
    arg = arg.split(":")
    # print arg
    _cmd = arg[0]
    _arg = arg[1:]
    __arg = [[],]
    while(_arg):
        __arg.append(_arg.pop().split(','))
    __arg.reverse()
    __arg.pop()
    # print "__arg = ",__arg
    # print "len(__arg) = ",len(__arg)
    _stack = []
    inloop = []
    for i, command in enumerate(__tok, start = idx):
        cmd = command[0]
        arg = command[1]
        inloop.append([cmd,arg])
        # print "%03d"%i,cmd+arg
    # inloop = "".join(inloop)
    cmdtype = len(__arg)
    if(cmdtype == 3):
        for _,val in enumerate(__arg[2]):
            for _,_val in enumerate(__arg[1]):
                for _,__val in enumerate(__arg[0]):
                    _stack.append([_cmd, ":".join([__val,_val,val])])
                    _stack.extend(inloop)
                #     print "%s(%s:%s:%s);%s" %(
                #     _cmd,
                #     ",".join(str(__val)),
                #     _val,
                #     val,inloop
                #     ),
                # print
    elif(cmdtype == 2):
        for _,_val in enumerate(__arg[1]):
            for _,__val in enumerate(__arg[0]):
                _stack.append([_cmd, ":".join([__val,_val])])
                # print pprint.pprint(_stack)
                _stack.extend(inloop)
            #     print "%s(%s:%s);%s" %(
            #     _cmd,
            #     __val,
            #     _val,inloop
            #     ),
            # print
    elif(cmdtype == 1):
        for _,__val in enumerate(__arg[0]):
            _stack.append([_cmd, __val])
            _stack.extend(inloop)
            # print "%s(%s);%s" %(
            # _cmd,
            # __val,inloop
            # )
    # print "_stack = ",
    # print pprint.pprint(_stack)
    return _stack
    # callback[ cmd ]( (None, 0, _cmd, _arg ))

command = ["",""]
callback = {
"NOP":reg,
"REG":reg,
"UREG":reg,
"CHAN":reg,
"BASE":reg,
"UBASE":reg,
"TEMP":reg,
"FOR":found_for,
"}":end,
"DELY":reg,
"SAMPLE":reg,
"SUSPEND":reg,
}

_tok = []
__tok = []
_for = []
while(True):
    tok = tokens.get_token()
    if (not tok) or (tok=="EOF"):
        break
    else:
        # print tok
        _tok.append(tok)
        if(tok=="{" or tok==";"):
            __tok.append([_tok[0],"".join(_tok[1:])])
            _tok=[]
        if(tok=="}"):
            _f = []
            _for = []
            # _for.append([_tok[0],"".join(_tok[1:])])
            while not (__tok[-1][0] == "FOR"):
                # print __tok[-1]
                _for.append(__tok.pop())
            _f = __tok.pop()
            # print pprint.pprint(_for)
            # print _f
            _for.reverse()
            __tok.extend( found_for( (_for, 0, _f[0], _f[1]) ) )
            # print pprint.pprint(__tok)
            _tok = []
print pprint.pprint(__tok)
