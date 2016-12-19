#-*- coding: utf-8 -*-
#!/usr/bin/env python

import time
import datetime
import os
import sys
import stat
import json

from library import templexer
import argparse
import ConfigParser
configread = ConfigParser.ConfigParser()

# sys.path.append("./library")


def hoge(arg):
    arg = arg.strip("{}();")
    arg = arg.split(":")
    print arg

templexer.add_command("HOGE", hoge)

if __name__ == "__main__":
    class MyParser(object):

        def __init__(self):
            self._parser = argparse.ArgumentParser(description="""
            templexer test script
            """)
            self._parser.add_argument('--device', '-D', help='device number',
                                      default=1)
            self._parser.add_argument('--config', '-C', help='config file',
                                      default="default.conf")
            self._parser.add_argument('--script', '-S', help='script file',
                                      default="script.txt")
            self.args = self._parser.parse_args(namespace=self)

    parser = MyParser()
    _device = parser.args.device
    _config = parser.args.config
    _script = parser.args.script

    configread.read(_config)
    # print configread.items("script")

    scr = configread.get("script", "source")

    templexer.parse(scr)
    # with open(_script, "rb") as _file:
    #     script = _file.read()
    #     script = script.upper()
    #     # configread.read(script)
    # # print script
    # # print templexer.callback
    #     # print isinstance(script, basestring)
