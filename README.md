
tempcommand
===========

`tempcommand` is yet another mini programming language

```{.txt}
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
```
* * *
```{.python}
import tempcommand

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

callback = {
   "NOP":nop,
   "REG":reg,
   "UREG":reg,
   "CHAN":reg,
   "BASE":reg,
   "UBASE":reg,
   "TEMP":reg,
   "DELY":reg,
   "SAMPLE":reg,
   "SUSPEND":suspend,
}

parser = tempcommand.tempcommand()

with open("script.txt", "rb") as file:
    script = file.read()

parser.parse(script.upper())

```
