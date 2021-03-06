#-*- coding: utf-8 -*-
#!/usr/bin/env python
import instr_local
import monthname
import tempcommand

import npyscreen
import pkg_resources
pkg_resources.require("pyVisa>=1.5")
import visa
import time
import datetime
import os
import sys
import stat
import socket
import traceback

try:
    import uli
except:
    import dummyULI as uli

try:
    import usbio.usbio as usbio
except:
    import dummyUSB as usbio

# TempCtrl
# only calls MainForm


class TempCtrl(npyscreen.NPSAppManaged):

    def onStart(self):
        self.mainform = self.addForm("MAIN", MainForm, name="\tTemerature Control and measurement\t",
            color="GOOD")  # , minimum_lines = 35, minimum_columns = 100)

# MainForm
# main class


class MainForm(npyscreen.ActionForm, tempcommand.tempcommand):
    _outfile = None
    _logfile = None
    _i2c = False
    _uli2c = [False, False]
    _cypress = -99
    _script_fullname = ""
    _script_basename = ""

    # UI creation
    def create(self):
        self.commandset = {}

        self.add_command("NOP",     self._nop)
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
        self.add_command("UREG",    self._uliregister)
        self.add_command("CHAN",    self._chanset)
        self.add_command("FOR",     self._for)
        self.add_command("LOOP",    self._loop)

        self.add_command("SBASE",   self._serialbase)
        self.add_command("SREG",    self._serialregister)
        self.add_command("SCHAN",   self._serialchannel)

        self.add_command("CALL",    self._call)
        self.add_command("UCALL",    self._ulicall)
#        self.add_command("SCALL",    self._serialcall)

        self.add_command("EMAIL",   self._email)

        self._scrfilename = self.add(npyscreen.TitleFilename, name="Filename:",
            value="W:\\Tokyo\\Home\\kyamamot\\common\\GitHub\\tempcommand\\")
#            value = "W:\\Tokyo\\Data\\Design Center\\")
#            value = "W:\\Tokyo\\Data\\Design Center\\Nori2\\Evaluation\\OL1_02.txt")
        self._psu = self.add(npyscreen.TitleText, name="PSU:", value="24", width=35)

        self._chamber = self.add(npyscreen.TitleText, name="Chamber:", value="16", width=35)
        self.nextrely -= 1
        self._isctrl_chamber = self.add(npyscreen.CheckBox, value=True,
            name="Control Temp", relx=40, width=35)

        self._dmm1 = self.add(npyscreen.TitleText, name="Multimeter1:", value="2", width=35)
        self.nextrely -= 1
        self._isUSB_dmm1 = self.add(npyscreen.CheckBox, value=False,
                                    name="34461A", relx=40, width=35)

# self._isuse_dmm2 = self.add(npyscreen.CheckBox, value = True, name =
# "Use DMM2", width = 35)
        self._isuse_dmm2 = self.add(npyscreen.CheckBox, value=False, name="Use DMM2", width=35)
        self._isuse_dmm2.whenToggled = self._dmm2_toggled
        self.nextrely -= 1
        self._dmm2 = self.add(npyscreen.TitleText, name="Multimeter2:", value="10", relx=40, width=35,
            editable=False, hidden=True,)

        self._isuse_smu = self.add(npyscreen.CheckBox, value=False, name="Use KEITHLEY", width=35)
        self._isuse_smu.whenToggled = self._smu_toggled
        self.nextrely -= 1
        self._smu = self.add(npyscreen.TitleText, name="KEITHLEY:", value="10", relx=40, width=35,
            editable=False, hidden=True,)

        self._isuse_kikusui = self.add(npyscreen.CheckBox, value=False,
                                       name="Use Kikusui", width=35)
        self._isuse_kikusui.whenToggled = self._kikusui_toggled
        self.nextrely -= 1
        self._isUSB_kikusui = self.add(npyscreen.CheckBox, value=True, name="Use USB", relx=40, width=35,
            editable=False, hidden=True,)
        self._kikusui = self.add(npyscreen.TitleText, name="Kikusui:", value="10", relx=40, width=35,
            editable=False, hidden=True,)

# self._isuse_serial = self.add(npyscreen.CheckBox, value = False, name =
# "Use Ser-I2C", width = 35)
        self._isuse_serial = self.add(npyscreen.CheckBox, value=False, name="Use Ser-I2C", width=35)
        self._isuse_serial.whenToggled = self._serial_toggled
        self.nextrely -= 1
        self._serial = self.add(npyscreen.TitleText, name="Serial-I2C:", value="com8", relx=40, width=35,
            editable=False, hidden=True,)

        self._isuse_email = self.add(npyscreen.CheckBox, value=False, name="Use email", width=35)
        self._isuse_email.whenToggled = self._email_toggled
        self.nextrely -= 1
        self._sendto = self.add(npyscreen.TitleFilename, name="User:", width=50, relx=40,
            editable=False, hidden=True, value="user@example.com")
        self._sendsrv = self.add(npyscreen.TitleFilename, name="SMTP:", width=50, relx=40,
            editable=False, hidden=True, value="smtp.example.com")

        self._Tcurrent = self.add(npyscreen.TitleFixedText,  name="current temp:",
            value="    27.0 oC    >>>", max_width=40, editable=False)
        self.nextrely -= 1
        self._Ttarget = self.add(npyscreen.TitleFixedText, name="target temp:",
            value="27.0 oC", editable=False, relx=40)
        self._processing = self.add(npyscreen.TitleFixedText, name="In process:",
            value="---", editable=False)

        self._shell = self.add(npyscreen.MultiLineEdit,
            scroll_end=True, value=">>>\n", name="log:",
            multiline=True, editable=False)

        self._dmm2_toggled()
        self._smu_toggled()
        self._kikusui_toggled()
        self._serial_toggled()
        self._email_toggled()

    # event callback when DMM2 flag changed
    def _dmm2_toggled(self):
        self._dmm2.editable = self._isuse_dmm2.value
        self._dmm2.hidden = not self._isuse_dmm2.value
        self._dmm2.update()
#        self.shellResponse( "toggled, "+str(self._isuse_dmm2.value))

    # event callback when SMU flag changed
    def _smu_toggled(self):
        self._smu.editable = self._isuse_smu.value
        self._smu.hidden = not self._isuse_smu.value
        self._smu.update()
#        self.shellResponse( "toggled, "+str(self._isuse_smu.value))

    # event callback when Kikusui flag changed
    def _kikusui_toggled(self):
        self._kikusui.editable = self._isuse_kikusui.value
        self._kikusui.hidden = not self._isuse_kikusui.value
        self._isUSB_kikusui.editable = self._isuse_kikusui.value
        self._isUSB_kikusui.hidden = not self._isuse_kikusui.value
        self._kikusui.update()
        self._isUSB_kikusui.update()
#        self.shellResponse( "toggled, "+str(self._isuse_kikusui.value))

    # event callback when Ser-I2C flag changed
    def _serial_toggled(self):
        self._serial.editable = self._isuse_serial.value
        self._serial.hidden = not self._isuse_serial.value
        self._serial.update()
        # self.shellResponse( "toggled, "+str(self._isuse_serial.value))

    # event callback when EMAIL flag changed
    def _email_toggled(self):
        self._sendto.editable = self._isuse_email.value
        self._sendto.hidden = not self._isuse_email.value
        self._sendsrv.editable = self._isuse_email.value
        self._sendsrv.hidden = not self._isuse_email.value
        self._sendto.update()
        self._sendsrv.update()
        # self.shellResponse( "toggled, "+str(self._isuse_email.value))

    # shell-look output
    def shellResponse(self, string):
        self._shell.value = ">>> " + str(string) + "\n" + self._shell.value
        self.display()

    # event callback if cancelled
    def on_cancel(self):
        # if self.TCrun:
        #     self.shellResponse( " ### cancel while TCrun: make SAFE closing! ### ")
        #     self.display()
        #     time.sleep(1)
        #     self.exit_application()
        # else:
        self.shellResponse(" ### cancel before TCrun: just close ### ")
        self.display()
        time.sleep(1)
        self.exit_application()

    # event callback if ok
    # just calls main loop
    def on_ok(self):
        # if self.TCrun:
        #     self.shellResponse( "ok while TCrun: do nothing")
        # else:
        #     # vvv debug code vvv
        # self.shellResponse( " ### ok before TCrun: start run ###")
        # self.shellResponse(self._psu.get_value())
        # self.shellResponse(self._chamber.get_value())
        # self.shellResponse(self.dmm1.get_value())
        # self.shellResponse(self.dmm2.get_value())
        # self.shellResponse(str(self._isuse_dmm2.value))
        # self.shellResponse(str(self.isctrl_chamber.value))
        #     #^^^ debug code ^^^
        # self.TCrun = True
        self.tc_run()

    # exit application
    def exit_application(self):
        self.parentApp.NEXT_ACTIVE_FORM = None
        self.editing = False

    # main loop
    def tc_run(self):
        lib = rm = False
        todaydetail = datetime.datetime.today()
        todaydir = "C:\\Users\\Public\\Documents\\" + monthname.monthname()
        if os.path.exists(todaydir) != 1:
            os.mkdir(todaydir)
        csvname = todaydetail.strftime("%H.%M.%S") + ".chamber.csv"
        filename = todaydir + "\\" + csvname

        self._outfile = open(filename, 'a')
        # self._outfile.write( os.environ['COMPUTERNAME']+"\n" )
        self._outfile.write(socket.gethostname() + "\n")
        self._outfile.write(monthname.monthname() + "\\" +
                            todaydetail.strftime("%H.%M.%S") + ".chamber.csv" + "\n")

        self._logfile = open(filename + ".log", 'a')

        try:
        #    self._cypress = usbio.usbio.autodetect()
            usbio.setup()
            self._cypress = usbio.autodetect()
        except:
        #    npyscreen.notify_confirm(str(self._cypress),title = "REPORT",editw = 1)
            npyscreen.notify_confirm("".join(traceback.format_tb(sys.exc_info()[2])) + ": "
                + str(sys.exc_info()[1]), title="ERROR REPORT", editw=1)
            self._i2c = False
            self._cypress = -99
            self.shellResponse("no Cypress I2C connected")

        else:
        #    self._i2c  = usbio.usbio.I2C(self._cypress, 0x90)#0x48/7bit = 0x90/8bit
            self._i2c = usbio.I2C(self._cypress, 0x90)  # 0x48/7bit = 0x90/8bit

        self._uli2c[0] = uli.I2C(0, 0x90, 0)  # 0x48/7bit = 0x90/8bit
        self._uli2c[1] = uli.I2C(0, 0x90, 1)  # 0x48/7bit = 0x90/8bit
        chan0 = self._uli2c[0].searchI2CDev(0x90, 0xFF)
        chan1 = self._uli2c[1].searchI2CDev(0x90, 0xFF)
        self.shellResponse(str(chan0))
        self.shellResponse(str(chan1))
        time.sleep(0.5)
        if(chan0 == []): self._uli2c[0] = False
        if(chan1 == []): self._uli2c[1] = False
        if(chan0 == [] and chan1 == []):
            self.shellResponse("no SAM3U I2C connected")

        self.shellResponse(self._uli2c)
        self.shellResponse(self._cypress)

        try:
            lib = visa.VisaLibrary()
            rm = visa.ResourceManager()
        except:
            lib = rm = False
            self.shellResponse("no VISA connected")

        self.display()
        currentvolt = 3.7

        self.Chamber = instr_local.dummy()
        try:
            self.Chamber = instr_local.chamber(
                rm, self._chamber.get_value(), self._isctrl_chamber.value)
        except:
            npyscreen.notify_confirm("".join(traceback.format_tb(sys.exc_info()[2])) + ": "
                + str(sys.exc_info()[1]), title="ERROR REPORT", editw=1)

        self.A34401A = instr_local.dummy()
        try:
            self.A34401A = instr_local.multimeter(
                rm, self._dmm1.get_value(), self._isUSB_dmm1.value)
        except:
            npyscreen.notify_confirm("".join(traceback.format_tb(sys.exc_info()[2])) + ": "
                + str(sys.exc_info()[1]), title="ERROR REPORT", editw=1)

        self.E3640A = instr_local.dummy()
        try:
            self.E3640A = instr_local.powersupply(rm, self._psu.get_value())
        except:
            npyscreen.notify_confirm("".join(traceback.format_tb(sys.exc_info()[2])) + ": "
                + str(sys.exc_info()[1]), title="ERROR REPORT", editw=1)

        else:
            self.E3640A.output(True)

        self.A34970A = instr_local.dummy()
        if self._isuse_dmm2.value:
            try:
                self.A34970A = instr_local.multimeter2(
                    rm, self._dmm2.get_value(), self._isuse_dmm2.value)
            except:
                npyscreen.notify_confirm("".join(traceback.format_tb(sys.exc_info()[2])) + ": "
                    + str(sys.exc_info()[1]), title="ERROR REPORT", editw=1)

        self.K2400 = instr_local.dummy()
        if self._isuse_smu.value:
            try:
                self.K2400 = instr_local.sourcemeter(
                    rm, self._smu.get_value(), self._isuse_smu.value)
            except:
                npyscreen.notify_confirm("".join(traceback.format_tb(sys.exc_info()[2])),
                    title="ERROR REPORT", editw=1)

        self.PLZ164 = instr_local.dummy()
        if self._isuse_kikusui.value:
            try:
                self.PLZ164 = instr_local.kikusui(rm, self._kikusui.get_value(),
                    self._isUSB_kikusui.value, self._isuse_kikusui.value)
            except:
                npyscreen.notify_confirm("".join(traceback.format_tb(sys.exc_info()[2])),
                    title="ERROR REPORT", editw=1)

        self.mbedI2C = instr_local.dummy()
        if self._isuse_serial.value:
            try:
                self.mbedI2C = instr_local.serial_i2c(
                    self._serial.get_value(), isuse=self._isuse_serial.value)
            except:
                npyscreen.notify_confirm("".join(traceback.format_tb(sys.exc_info()[2])) + ": "
                    + str(sys.exc_info()[1]), title="ERROR REPORT", editw=1)

        # else:
        # self.mbedI2C = instr_local.dummy()

        self._script_fullname = self._scrfilename.get_value()
        self._script_basename = "\\".join(self._script_fullname.split("\\")[
                                          :-1])  # path\to\scriptfile(windows only)

        scr = open(os.path.join(self._script_fullname), 'r')
        script = scr.read()
        scr.close()

        self.parse(script, self._logfile)

        time_finished = todaydetail.strftime("%H.%M.%S")
        self._outfile.write(time_finished + " finished\n")
        self._outfile.close()
        self._logfile.close()
        os.chmod(filename, stat.S_IREAD)
        os.chmod(filename + ".log", stat.S_IREAD)
        self.E3640A.disconnect(lib)
        self.Chamber.disconnect(lib)
        self.A34401A.disconnect(lib)
        if self._isuse_dmm2.value:
            self.A34970A.disconnect(lib)
        if self._isuse_smu.value:
            self.K2400.disconnect(lib)
        if self._isuse_kikusui.value:
            self.PLZ164.disconnect(lib)
        if self._isuse_serial.value:
            self.mbedI2C.disconnect()
        info = (socket.gethostname(), todaydir, csvname, time_finished)
        try:
            self.sendmail(self._sendto.get_value(), self._sendsrv.get_value(),
                          info, self._isuse_email.value)
        except:
            npyscreen.notify_confirm("".join(traceback.format_tb(sys.exc_info()[2])) + ": "
                + str(sys.exc_info()[1]), title="ERROR REPORT(sendmail)", editw=1)

        self.exit_application()

    # command callback EMAIL
    # EMAIL(user@example.com;smtp.example.com)
    # @param user@example.com user email address
    # @param smtp.example.com SMTP server address
    def _email(self, argument):
        dummy, mailto = argument.split("(")
        mailto, dummy = mailto.split(")")
        user, smtp = mailto.split(";")
        self._processing.value = "EMAIL( " + user + " )"
        self._sendto.set_value(user)
        self._sendsrv.set_value(smtp)
        self._isuse_email.value = True
        self._email_toggled()
        return 0

    # sends email as set
    def sendmail(self, address, server, info, isuse=False):
        import smtplib
#        from email.mime.text import MIMEText
#        from email.mime.multipart import MIMEMultipart
        from email import Encoders
        from email.Utils import formatdate
        from email.MIMEBase import MIMEBase
        from email.MIMEMultipart import MIMEMultipart
        from email.MIMEText import MIMEText
        if isuse:
            msg = MIMEMultipart()
            machinename, path, outfile, finished = info
            logfile = outfile + ".log"
            sender = address
            subject = "[ LAB ] tempctrl finished"
            body = "Temerature Control and measurement finished on " + machinename + " at " + finished + ".\n"\
                    + "outputs are " + outfile + " and " + logfile + ""

            msg['From'] = sender
            msg['To'] = sender
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            attachment = MIMEBase('text', 'comma-separated-values')
            file = open(path + '\\' + outfile)
            attachment.set_payload(file.read())
            file.close()
            Encoders.encode_base64(attachment)
            msg.attach(attachment)
            attachment.add_header("Content-Disposition", "attachment", filename=outfile)

            text = msg.as_string()
            # print text
            # Send the message via our SMTP server
            s = smtplib.SMTP(server)  # will be changed
            s.sendmail(sender, sender, text)
            s.quit()

    # command callback EOF
    # no parameters
    def _eof(self, dummy='-1'):
        self.shellResponse('EndOfFile triggered')
        return -1

    # no operation NOP
    # no parameters
    def _nop(self, dummy='-1'):
        self.shellResponse('--=-=-=-=-=-=-=--')
        self._outfile.write(
            "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n")
        return 0

    # command callback TEMP
    # TEMP x.x
    # @param x.x target temperature
    def _temp(self, temp='30'):
        self._processing.value = "TEMP" + str(temp)
        self._Ttarget.value = str(temp) + " oC"

        self.shellResponse('temperature set: ' + temp + ' oC')
        self.shellResponse(self.Chamber.setTemp(temp))
        time.sleep(10)
        i = 0
        while 1:  # release code
            i += 1  # release code
            current, target, absolute, hoge = self.Chamber.getTemp()
            self._Tcurrent.value = "    " + str(current) + " oC    >>>"
            diff = abs(float(current) - float(target))

            self.shellResponse(str(i) + ",\t current = " + current +
                                ",\t target = " + target + ",\t limit = " + absolute + "," + hoge + ",\t " + str(diff))
            if diff < 0.2:
                break
            time.sleep(10)  # release code

        self.shellResponse('reached target')
        self._outfile.write(temp + "oC\n")
        return 0

    def _sample(self, dummy='-1'):
        self._processing.value = "SAMPLE"

        self.shellResponse('sample triggered')
        current, target, absolute, hoge = self.Chamber.getTemp()
        read = ",,," + current + "," + str(self.E3640A.read()) + "," + str(self.A34401A.sample())
        if self._isuse_dmm2.value:
            read += "," + str(self.A34970A.sample())
        if self._isuse_smu.value:
            read += "," + str(self.K2400.sample())
        self._outfile.write(read + "\n")
        return 0

    def _suspend(self, dummy='-1'):  # SUSPEND

        self.shellResponse('suspend triggered')

        npyscreen.notify_confirm("\n\t\t-=-=-=-SUSPEND-=-=-=-\n" +
            "I would like more flexible popup which runs temp check in buckground \
            but for now this is the solution as this works anyway...", title="SUSPEND", editw=1)

        self.shellResponse('return from popup')
        return 0

    def _volt(self, volt='3.0'):  # VOLT x.x : sets supply voltage to be x.xV
        self._processing.value = "VOLT" + str(volt)

        self.shellResponse('voltage set: ' + volt + ' V')
        self._outfile.write(volt + 'V\n')
        self.E3640A.SetVoltage(volt)
        return 0

    def _delay(self, delay=1):  # DELY x : wait for x minutes
        self._processing.value = "DELY" + str(delay)
        self.shellResponse('wait for: ' + delay + ' minutes')
        for i in range(6 * int(delay)):
            current, target, absolute, hoge = self.Chamber.getTemp()
            self.shellResponse(str(i) + "," + current + "," + target + "," + absolute + "," + hoge)
            time.sleep(10)
        return 0

    def _kikusui(self, current='1e-3'):

        self.shellResponse('current set: ' + current + ' A')
        return 0

    def _base(self, baseaddr='90'):  # BASE xx : set 8bit base address to be xx (HEX)
        baseaddr = int(baseaddr, 16)
        self._processing.value = "BASE" + str(baseaddr)

        self.shellResponse('i2c slave address set: %02X' % (baseaddr))
        self._i2c = usbio.I2C(self._cypress, baseaddr)
#        self._i2c = usbio.usbio.I2C(self._cypress, baseaddr)
        self._outfile.write("SLAVE = %02X,(8it)\n" % (baseaddr))
        return 0

    def _register(self, argument):
        self._processing.value = "REG" + str(argument)
        i2creg, i2cdata = argument.split('=')
        i2creg = int(i2creg, 16)
        i2cdata = int(i2cdata, 16)

        self.shellResponse('reg address = 0x%02X, data = 0x%02X' % (i2creg, i2cdata))
        if self._cypress == -99: pass
        else:
            self._i2c.write_register(i2creg, i2cdata)
        self._outfile.write(',reg%02Xh =, 0x%02X\n' % (i2creg, i2cdata))

        return 0

    def _call(self, conf):  # CALL(filename) : load i2c setting file "filename" and write them all into device under usbio module
        self._processing.value = "CALL " + conf
        dummy, file = conf.split("(")
        conf, dummy = file.split(")")
        conf = self._script_basename + "\\" + conf
        scr = open(os.path.join(conf), 'r')
        script = scr.read()
        scr.close()

        self.shellResponse('reading i2c config file: ' + conf)
        self._outfile.write(',reading:,' + conf + '\n')
        for line in script.split('\n'):
            words = line.split('//')[0]
            if words.split() == []: continue

            base, reg, data = words.split()  # still string
            base = int(base, 16)
            reg = int(reg, 16)
            data = int(data, 16)

            self._outfile.write("base = %02X, reg = %02X, data = %02X\n" % (base, reg, data))
            self.shellResponse("base = %02X, reg = %02X, data = %02X" % (base, reg, data))
            i2c = usbio.I2C(self._cypress, base)
            if self._cypress == -99: pass
            else:
                i2c.write_register(i2creg, i2cdata)
        return 0

    def _ulibase(self, argument):  # UBASEx[+y] = zz -> channel = x[and y], baseaddress = zz
        self._processing.value = "UBASE" + str(argument)
        ulichan, ulibase = argument.split('=')
        channels = ulichan.split('+')
        if len(channels) > 1:
            ulichan = [channels[0], channels[1]]
        else:
            ulichan = [channels[0]]
        ulibase = int(ulibase, 16)
        for f in ulichan:
            if self._uli2c[int(f)] == False:
                pass
            else:
                self._uli2c[int(f)] = uli.I2C(0, ulibase, int(f))  # 0x48/7bit = 0x90/8bit
            self._outfile.write("SLAVE= 0x%02X,CH= u%d (8bit)\n" % (ulibase, int(f)))
            self.shellResponse('i2c slave address set: 0x%02X of channel u%d' % (ulibase, int(f)))

        return 0

    def _uliregister(self, argument):  # UREGx[+y]:aa = bb -> channel = x[and y],reg = aa,data = bb
        self._processing.value = "UREG" + str(argument)
        ulichan, i2cdata = argument.split(':')
        ulireg, ulidata = i2cdata.split('=')
        channels = ulichan.split('+')

        if len(channels) > 1:
            ulichan = [channels[0], channels[1]]
        else:
            ulichan = [channels[0]]
        ulireg = int(ulireg, 16)
        ulidata = int(ulidata, 16)
        for f in ulichan:
            if self._uli2c[int(f)] == False:
                pass
            else:
                self._uli2c[int(f)].write_register(ulireg, ulidata)
            self._outfile.write('channel u%d,reg%02Xh =, 0x%02X\n' % (int(f), ulireg, ulidata))
            self.shellResponse('channel = u%d, reg address = 0x%02X, data = 0x%02X'
                % (int(f), ulireg, ulidata))

                %(int(f), ulireg, ulidata))
        return 0

    def _ulicall(self, conf):  # UCALL(x = filename) load i2c setting file "filename" and write them all into device under uli module, channel = x
        self._processing.value="UCALL( " + conf + " )"
        dummy, conf=conf.split("(")
        conf, dummy=conf.split(")")
        channel, conf=conf.split("=")
        conf=self._script_basename + "\\" + conf
        scr=open(os.path.join(conf), 'r')
        script=scr.read()
        scr.close()

        self.shellResponse('ch u' + channel + ': reading i2c config file: ' + conf)
        self._outfile.write('ch u' + channel + ':,reading:,' + conf + '\n')
        channel=int(channel)
        for line in script.split('\n'):
            words=line.split('//')[0]
            if words.split() == []: continue

            base, reg, data=words.split()  # still string
            base=int(base, 16)
            reg=int(reg, 16)
            data=int(data, 16)

            self._outfile.write("base = %02X, reg = %02X, data = %02X\n" % (base, reg, data))
            self.shellResponse("base = %02X, reg = %02X, data = %02X" % (base, reg, data))
            i2c=uli.I2C(0, base, channel)  # 0x48/7bit = 0x90/8bit
            if self._uli2c[channel] == False:
                pass
            else:
                i2c.write_register(ulireg, ulidata)
        return 0
        pass

    def _serialbase(self, baseaddr = '90'):
#        baseaddr = int(baseaddr,16)
        self._processing.value="SBASE" + str(baseaddr)
        ch=self.mbedI2C.getChannel()
        self.mbedI2C.setBase(ch, int(baseaddr, 16))

        self.shellResponse('i2c slave address set: 0x' + str(baseaddr))

            % (ch))
        return 0

    def _serialregister(self, argument):
        self._processing.value="SREG" + str(argument)
        i2creg, i2cdata=argument.split('=')
        i2creg=int(i2creg, 16)
        i2cdata=int(i2cdata, 16)
        ch=self.mbedI2C.getChannel()
        base=self.mbedI2C.getBase(ch)
        packet=self.mbedI2C.regWrite(base, i2creg, i2cdata)

        self.shellResponse('reg address = 0x%02X, data = 0x%02X' % (i2creg, i2cdata))
        self._outfile.write('channel s%d,reg%02Xh =, 0x%02X\n' % (base, i2creg, i2cdata))

        return 0

    def _serialchannel(self, channel):
        self._processing.value="SCHAN" + (channel)
        if(channel == '0'): ch=0
        elif(channel == '1'): ch=1
        elif(channel == '2'): ch=2
        elif(channel == '3'): ch=3
        else: ch=0
        dummy=self.mbedI2C.setChannel(ch)
        ch=self.mbedI2C.getChannel()

        self.shellResponse('set channel to s' + str(channel))
        self._outfile.write('I2C channel ,s%d\n' % (ch))
        return 0

    def _serialcall(self, conf):
        pass

    def _chanset(self, channels):
        self._processing.value="CHAN" + str(channels)

        self.shellResponse('set channels(@' + channels.replace('+', ',') + ')')
        self.A34970A.setChannel('(@' + channels.replace('+', ',') + ')')
        return 0

    def _for(self, argument='1'):
#        self.isInLoop.append(True)

        var=argument.split(";")
        lst=var[0].split("+")
        for var[0] in lst:
            self.lpHeader.append(str(var[1]) + str(var[0]))
        return 0

    def _loop(self, dummy='-1'):
        if (self.isInLoop != []):  # ==True):
            self.isInLoop.pop()
            for head in self.lpHeader:
                self.parse(head, self._logfile)
                for commd in self.lpContain:
                    self.parse(commd, self._logfile)


        return 0

if __name__ == '__main__':
    TC=TempCtrl()
    try:
        TC.run()
    except:
        npyscreen.notify_confirm("".join(traceback.format_tb(sys.exc_info()[2]))
                + str(sys.exc_info()[1]), title="ERROR REPORT", editw=1)
    else:
        sys.stdout=sys.__stdout__
        raw_input("\t -------- measurement finished (Press RETURN key to exit) --------\
                \n\n\n\n\n\n\n\n\n\n\n")
