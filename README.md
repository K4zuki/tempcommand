tempcommand
===========

temperature chamber control command interpreter with ncurses based GUI

```{.python}
import tempcommand

parser = tempcommand.tempcommand()

logfile = open("hoge.log",'a')


# add_command("COMMAND", _callback)
#              ^^^^^^\   ^^^^^^^^^ - _callback() must be defined before this line
#                     `- always UPPERCASE

parser.add_command("TEMP",parser._temp)
parser.add_command("EOF",parser._eof)
parser.add_command("FOR",_for)
parser.add_command("SAMPLE",_sample)
parser.add_command("LOOP",_loop)
parser.add_command("REG",_register)
parser.add_command("CHAN",_chanset)
parser.add_command("DELY",_delay)

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

parser.break_loop(parser.commandList,parser.argumentList)
parser.parse_list(parser.commandList,parser.argumentList, logfile)

```
