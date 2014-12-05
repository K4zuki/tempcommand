#-*- coding: utf-8 -*- 
#!/usr/bin/env python
import serial
import argparse
import struct
import os.path
import time

# Table 3. ASCII commands supported by SC18IM700
# ASCII command Hex value Command function
# [X] S 0x53 I2C-bus START
# [X] P 0x50 I2C-bus STOP
# [_] R 0x52 read SC18IM700 internal register
# [_] W 0x57 write to SC18IM700 internal register
# [_] I 0x49 read GPIO port
# [_] O 0x4F write to GPIO port
# [_] Z 0x5A power down
# [X] C 0x43 change channel

## serial2i2c: RS232C to I2C converter using mbed
class serial2i2c(object):
    _ser = 0
    _channel = 0
    _wait = 1e-2

    ## constructor
    # @param port COM port which device is conected
    # @param baud baudrate
    def __init__(self, port = 'com1', baud = '115200'):
        try:
            self._ser = serial.Serial(port,baudrate=baud,timeout=1)
        except:
            raise

    ## sets channel by sending "C" command packet
    # @param channel I2C bus channel
    # @return response from module
    def setChannel(self, channel = 0):
        self._channel = channel
        self._ser.write("C" + str(self._channel) + "P")
        time.sleep(self._wait)
        return (self._ser.readline().strip())

    ## reads multi byte data
    # @param address 8bit I2C slave address in HEX
    # @param length bytes to read
    # @return response string from device
    def read(self, address, length = 1):
        packet = ['S', 'P']
        address = self.convert_hex_to_ascii(address,0xa0)
        alength = len(address) / 2
        packet.insert(1, chr(ord(address[0]) | 1))
        packet.insert(1, address[1])
        for _l in self.convert_hex_to_ascii(length, 0xd0):
            packet.insert(3, _l)
#        print packet
        for _p in packet:
            self._ser.write(_p)
        time.sleep(self._wait * length * 2)
        return (self._ser.readline().strip())

    ## writes multi byte data
    # @param address 8bit I2C slave address in HEX
    # @param data data to send
    # @return sesponse string from device
    def write(self, address, data = 0):
        packet = ['S', 'P']
#        print address,self.convert_hex_to_ascii(address,0xa0)
        address = self.convert_hex_to_ascii(address, 0xa0)
        alength = len(address) / 2
        for _a in address:
            packet.insert(1, _a)
        
        data = self.convert_hex_to_ascii(data, 0xb0)
        length = len(data) / 2

        for _l in self.convert_hex_to_ascii(length,0xc0):
            packet.insert(3, _l)

        for _d in data:
            packet.insert(5, _d)
        
        for _p in packet:
            self._ser.write(_p)
        time.sleep(self._wait * length * 2)
        return (self._ser.readline().strip())

    ## writes data and then reads from same slave device
    # @param address I2C slave address in HEX
    # @param wdata data to send in HEX
    # @param rlength bytes to read
    # @return sesponse string from device
    def write_and_read(self, address, wdata = 0, rlength = 1):
        packet = ['S', 'S', 'P']

        address = self.convert_hex_to_ascii(address, 0xa0)
        alength = len(address) / 2
        for _a in address:
            packet.insert(1, _a)

        wdata = self.convert_hex_to_ascii(wdata, 0xb0)
        wlength = len(wdata) / 2

        for _wl in self.convert_hex_to_ascii(wlength, 0xc0):
            packet.insert(3, _wl)

        for _wd in wdata:
            packet.insert(5, _wd)

        packet.insert(6 + wlength * 2, chr(ord(address[0]) | 1))
        packet.insert(6 + wlength * 2, address[1])

        for _rl in self.convert_hex_to_ascii(rlength, 0xd0):
            packet.insert(8 + wlength * 2, _rl)

        for _p in packet:
            self._ser.write(_p)
            
        time.sleep(self._wait * rlength * 2)
        return (self._ser.readline().strip())

    def raw_write(self, data="DEADBEAF"):
        self._ser.write(data)

    ## sends 'S' command packet to make start condition
    def start(self):
        self._ser.write("S")
        
    ## sends 'P' command packet to make stop condition
    def stop(self):
        self._ser.write("P")
        time.sleep(self._wait)

    ## converts hex data to string
    # @param h data in HEX
    # @param mask mask data in HEX, LSB must be 0, MSB must not be 0 (0x?0, ?>0)
    # @return converted format in list
    def convert_hex_to_ascii(self, h, mask = 0xa0):
        chars_in_reverse = []
        chars_in_reverse.append(chr(mask | (h & 0x0F)))
        chars_in_reverse.append(chr(mask | ((h >> 4) & 0x0F)))
        h = h >> 8
        while h != 0x0:
            chars_in_reverse.append(chr(mask | (h & 0x0F)))
            chars_in_reverse.append(chr(mask | ((h >> 4) & 0x0F)))
            h = h >> 8

        return (chars_in_reverse)

class MyParser(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="hogeeee")
        self.parser.add_argument('--port','-p', help='number or name of serial port', default='com1')
#        self.parser.add_argument('--port','-p', help='number or name of serial port', default='/dev/ttyACM0')
#        self.parser.add_argument('--mon','-m', help='number or name of serial port', default='/dev/ttyACM0')
        self.parser.add_argument('--baud','-b', help='baudrate of serial port', default='115200')#460800
        self.args=self.parser.parse_args(namespace=self)        

if __name__=="__main__":
#    parser.print_help()
    parser=MyParser()
#    args=parser.parse_args()
#    print args
#    print args.port, args.baud
    
    port=parser.args.port # port number, different in OSes
    baud=parser.args.baud
    dev=serial2i2c(port,baud)
##    channel="C0P"
##    i2cw="S"+chr(0x80)+chr(0x04)+struct.pack(">4B",0xde,0xad,0xbe,0xaf)+"P"
##    i2crw="S"+chr(0x80)+chr(0x04)+struct.pack(">4B",0xde,0xad,0xbe,0xaf)+"S"+chr(0x81)+chr(0x04)+"P"
#    print channel,i2cw

#    raw_input("wait, press enter to set channel 0")
    raw_input("wait, press enter to transferring data")
    print dev.setChannel(0)
    print dev.write_and_read(0xD0,0xD0,16)
    raw_input("wait, press enter to transferring data")
    print dev.setChannel(1)
    print dev.write_and_read(0xD0,0xD0,16)
    raw_input("wait, press enter to transferring data")
    print dev.setChannel(2)
    print dev.write_and_read(0xD0,0xD0,16)
    raw_input("wait, press enter to transferring data")
    print dev.setChannel(3)
    print dev.write_and_read(0xD0,0xD0,16)
#    print dev.setChannel(0)
#    print dev.ser.write(channel)
#    print dev.ser.readline().strip()
#    raw_input("wait, press enter to set channel 1")
#    print dev.ser.write("C1P")
#    print dev.ser.readline().strip()

#    raw_input("wait, press enter to send write command")
##    print dev.write(0xD0,0xdeadbeaf)
##    ser.write(i2cw)
##    dev.start()
##    dev.raw_write(chr(0xd0))
##    dev.stop()
##    print dev.ser.readline().strip()
##    print dev.write_and_read(0xD0,0x50,16)
#    print dev.write_and_read(0xD0,0x50,16)
# 0x141,0x00
# 0x142,0xd2
# 0x142,0xb0
# 0x142,0xa9
# 0x142,0x8a
# 0x142,0xa7
# 0x142,0xa8
# 0x142,0xb1
##    print dev.write(0xD2,0x4100)
##    print dev.write(0xD2,0x42d2)
##    print dev.write(0xD2,0x42b0)
##    print dev.write(0xD2,0x42a9)
##    print dev.write(0xD2,0x428a)
##    print dev.write(0xD2,0x42a7)
##    print dev.write(0xD2,0x42a8)
##    print dev.write(0xD2,0x42b1)
##    time.sleep(0.1)
##    print dev.write(0xD2,0x4701)
##    time.sleep(0.1)
##    print dev.write_and_read(0xD0,0x50,16)
##    print dev.write_and_read(0xD0,0xD0,16)
#    print dev.write_and_read(0xD0,0x5D00,16)
##    print dev.write(0xD0,0x5D01)
##    time.sleep(0.1)
##    print dev.write(0xD0,0xD800)
##    print dev.write(0xD0,0xD846)
##    print dev.write(0xD0,0x5D00)
    
#    print dev.read(0xD0,1)
    while False:
        print dev.write(0xD0,0x5D00)
##        print dev.write(0xD0,0x5D01)
#        print dev.write_and_read(0xD0,0x50,16)
#        print dev.write_and_read(0xD0,0xD0,16)
        #print dev.write_and_read(0xD2,0x10,15)
#        print dev.write_and_read(0xD0,0x50,16)
#        print dev.write_and_read(0xD4,0x10,16)
##    print "%02X"%(int(dev.write_and_read(0x90,0xdeadbeaf,50).split(',')[0],16))
#    print dev.ser.readline().strip()

##    raw_input("wait, press enter to send repeated start command")
##    dev.ser.write(i2crw)
##    print dev.ser.readline()

##    raw_input("wait, press enter to send 'R' command")
##    dev.ser.write('RP')
##    print dev.ser.readline()
##    neroaddr=0xD0
##    nerodata=[
##        [0xD8,0x00],
##        [0xD8,0x46],
##        [0xD8,0x7F],
##    ]
##    nerodata2=""
##    for hoge in nerodata:
##        print dev.convert_hex_to_ascii(hoge),
##    
###    print dev.convert_hex_to_ascii(nerodata)
##    
##    print dev.write(neroaddr,nerodata)
    

##    raw_input("wait, press enter to send 'W' command")
##    ser.write('WP')
##    print dev.ser.readline()

##    raw_input("wait, press enter to send 'I' command")
##    ser.write('IP')
##    print dev.ser.readline()

##    raw_input("wait, press enter to send 'O' command")
##    ser.write('OP')
##    print dev.ser.readline()

##    raw_input("wait, press enter to send 'Z' command")
##    ser.write('ZP')
##    print dev.ser.readline()

##    raw_input("wait, press enter to send unknown command")
##    ser.write('XP')
##    print dev.ser.readline()

#    while(ser.inWaiting()>0):
#        print ser.readline()
#    dev.ser.close()
