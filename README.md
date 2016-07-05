# tempcommand: yet another mini programming language
## example script
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

## example commandset
```{.python}
import tempcommand

def nop(arg):
    arg = arg.strip("{}();")
    arg = arg.split(":")
    print arg

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
# requirement
- **Python 2.7**
    - later python2 with `shlex` is needed; 2.6 and 2.7 has it
    - **Not tested with Python3**
    - [shlex](https://docs.python.org/2.7/library/shlex.html#module-shlex)

# backgrounds
`tempcommand` uses `shlex` library in python. The library splits the input script
  into minimum tokens - string, numbers, special characters, etc.
  Splitted tokens will be scanned until token reaches `EOF` token or end of file.
  The `EOF` token stops scanning script, even if more script remains.
  Other tokens will be concatenated until reaching:

- `;` as delimiter
- `{` as _**beginning**_ of loop structure

and stacked to queue. If read token is `}` then the compiler takes it as _**end**_ of
  loop and cuts queue from last `{` to this `}`, then throws cut queue to serializer
  function. The function, `serialize_loop()`, returns serialized(or loop-less)
  list of tokens, which will be stacked back to the queue again.

# basic rule
## tokens

- `[A-Z][a-z][0-9]*` as one word: `ABCabc` will not be separated
- `~!@#$%^&*()_+-={}|[]\:";'<>?,./` as one character: `ABC(def);` will be `ABC`,
  `(`, `def`, `)` and `;`
