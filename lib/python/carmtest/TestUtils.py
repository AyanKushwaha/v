#

#
__version__ = "$Revision: 1.1 $"
"""
<module name>
Module for doing:
<xyz>
@date:02Dec2009
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""
import os
import tempfile
import Errlog

class TmpMacro(object):

    XML = """<?xml version="1.0" encoding="UTF-8"?>"""
    def __init__(self):

        self.tmp_files = []
                   
    def generate_tmp(self, values={}):

        (fd_out, file )= tempfile.mkstemp()
        try:
            for line in self.__class__.XML.split("\n"):
                for val in values:
                    line = line.replace(val,values[val])
                os.write(fd_out, line)
        finally:
            os.close(fd_out)     
        self.log('Created file, %s'%file)
        self.tmp_files.append(file)
        return file
    
    def __del__(self):
        for file in self.tmp_files:
            os.system('rm -rf %s'%file)
            self.log('Removed file %s'%file)

    def log(self, msg):
        Errlog.log("%s ::%s"%(self.__class__.__name__, msg))


