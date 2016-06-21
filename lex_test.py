
# -*- coding: utf-8 -*-

# Copyright (c) 2016 Kazuki Yamamoto
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation the rights to use, copy,
# modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the
# following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import shlex
import pprint

tokens = shlex.shlex(
"""
chan(105,110);
base(90); ubase(0,1: 90);
reg(00 : ff);
ureg(0,1: 00 : ff);
# TEMP(25);
base(D2); ubase(0,1: D2);
    reg(41:00); for(reg:42:02,B0,A9,8A,A7,A8,B1){}
    ureg(0,1:41:00); for(ureg:0,1:42:02,B0,A9,8A,A7,A8,B1){}
    # ureg(1:41:00); for(ureg:1:42:02,B0,A9,8A,A7,A8,B1){}
    reg(47:01);
    ureg(0,1:47:01);
for(TEMP:  -40,0,100 )
{
    dely(1);
    # sample();
    for(reg: 00: 00,02,04)
    {
        # sample();
    }
    for(reg: 02: 0c,0e)
    {
        for(reg: 01,0A: 00,02,04)
        {

            # sample();
            # sample();
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
    arg = arg.strip("{}();")
    arg = arg.split(":")
    print arg
    # return idx

def reg(arg):
    arg = arg.strip("{}();")
    arg = arg.split(":")
    print arg

def suspend(arg):
    arg = arg.strip("{}();")
    arg = arg.split(":")
    print(" SUSPEND: press return to continue ".center(80, "#"))
    raw_input()

def serialize_loop(arg):
    __tok,idx,cmd,arg = arg
    arg = arg.strip("{}();")
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

# callback = {
#     "NOP":nop,
#     "REG":reg,
#     "UREG":reg,
#     "CHAN":reg,
#     "BASE":reg,
#     "UBASE":reg,
#     "TEMP":reg,
#     "DELY":reg,
#     "SAMPLE":reg,
#     "SUSPEND":suspend,
# }

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
            _tok = []
        if(tok == "}"):
            # _f = []
            _for = []
            # _for.append([_tok[0],"".join(_tok[1:])])
            while not (__tok[-1][0] == "FOR"):
                # print __tok[-1]
                _for.append(__tok.pop())
            _f = __tok.pop()
            # print pprint.pprint(_for)
            # print _f
            _for.reverse()
            __tok.extend( serialize_loop( (_for, 0, _f[0], _f[1]) ) )
            # print pprint.pprint(__tok)
            _tok = []
print pprint.pprint(__tok)

# for i, command in enumerate(__tok):
#     cmd = command[0]
#     arg = command[1]
#     callback[ cmd ]( arg )
