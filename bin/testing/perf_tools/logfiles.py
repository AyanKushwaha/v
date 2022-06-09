#
#$Header: /opt/Carmen/CVS/sk_cms_user/bin/testing/perf_tools/logfiles.py,v 1.3 2010/01/19 10:10:25 adg349 Exp $
#
__version__ = "$Revision: 1.3 $"
"""
logfiles.py
Module for doing:
List opf logfiles to parse, includes various filters to lists
@date:17Sep2009
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""
import sys
import re
import os
import time

from common import WrapObject

import logfile as L

class WrappedLogFile(WrapObject):


    _CLASSES = [L.__getattribute__(c) for c in dir(L) if 'LogFile' in c]
    def __init__(self, file_name):
        self._child = None
        for _class in WrappedLogFile._CLASSES:
            if _class.REGEXP.match(os.path.basename(file_name)):
                self._child = _class(file_name)
                break
            
        if self._child is None:
            raise  NotImplementedError('No support yet')
    def __cmp__(self, other):
        return self._child.__cmp__(other)
    
class LogFiles(list):
    """ Simple collection of logfiles"""
    def __init__(self):
        list.__init__(self)
        self.logfile_ix = 0

    @property
    def logfile(self):
        return self[self.logfile_ix]
        
    def __iter__(self):
        self.logfile_ix = 0
        if len(self)>0:
            self.logfile.__iter__()
        return self

    def next(self):
        try:
            try:
                line = self[self.logfile_ix].next()
                return line
            except StopIteration:
                self.logfile_ix += 1
                self.logfile.__iter__()
                return self.next()
        except IndexError:
            raise StopIteration

    def append(self, file):
        if type(file) == type('str'):
            file = WrappedLogFile(file)
        list.append(self, file)
        
            

class CctLogFiles(WrapObject):
    """ Tracking logfiles """
    def __init__(self, arg, logfiles):
        WrapObject.__init__(self)
        self._child = logfiles
        #arg not yet used
        
    def append(self, file):
        if  L.CctLogFile.REGEXP.match(os.path.basename(file)):
            object.__getattribute__(self, "_child").append(file)
            
    def __getattribute__(self, name):
        if name == 'append':
            return object.__getattribute__(self, "append")
        return getattr(object.__getattribute__(self, "_child"), name)
    
class CasLogFiles(WrapObject):
    """Planning logfiles """
    def __init__(self, arg, logfiles):
        WrapObject.__init__(self)
        self._child = logfiles
        #arg not yet used
        
    def append(self, file):
        if  L.CasLogFile.REGEXP.match(os.path.basename(file)):
            object.__getattribute__(self, "_child").append(file)
            
    def __getattribute__(self, name):
        if name == 'append':
            return object.__getattribute__(self, "append")
        return getattr(object.__getattribute__(self, "_child"), name)

class PreLogFiles(WrapObject):
    """Planning logfiles """
    def __init__(self, arg, logfiles):
        WrapObject.__init__(self)
        self._child = logfiles
        #arg not yet used
        
    def append(self, file):
        if  L.CasLogFile.REGEXP.match(os.path.basename(file)):
            object.__getattribute__(self, "_child").append(file)
            
    def __getattribute__(self, name):
        if name == 'append':
            return object.__getattribute__(self, "append")
        return getattr(object.__getattribute__(self, "_child"), name)
    
    
class TimeLogFiles(WrapObject):
    """ Timefiltered logfiles, mtime >= float(arg) days """
    def __init__(self, arg, logfiles):
        WrapObject.__init__(self)
        self._child = logfiles
        # Only add files newer than <arg> days
        self._cutoff = time.mktime(time.gmtime())-(float(arg)*24.0*60.0*60.0)
        
    def append(self, file):
        mtime = os.path.getmtime(file)
        if mtime >= object.__getattribute__(self, "_cutoff"):
            object.__getattribute__(self, "_child").append(file)
            
    def __getattribute__(self, name):
        if name == 'append':
            return object.__getattribute__(self, "append")
        return getattr(object.__getattribute__(self, "_child"), name)


class CmpAccLogFiles(WrapObject):
    """CmpAcc logfiles"""   
    def __init__(self, arg, logfiles):
        WrapObject.__init__(self)
        self._child = logfiles
        
    def append(self, file):
        if L.AccumulateLogFile.REGEXP.match(os.path.basename(file)):
            object.__getattribute__(self, "_child").append(file)
            
    def __getattribute__(self, name):
        if name == 'append':
            return object.__getattribute__(self, "append")
        return getattr(object.__getattribute__(self, "_child"), name)


class DIGServiceLogFiles(WrapObject):
    """ DIG Services logfiles"""
    def __init__(self, arg, logfiles):
        WrapObject.__init__(self)
        self._child = logfiles
        self._append_re = L.DIGServiceLogFile.REGEXP
        
    def append(self, file):
        if object.__getattribute__(self,'_append_re').match(os.path.basename(file)):
            object.__getattribute__(self, "_child").append(file)
            self.sort()
            
    def __getattribute__(self, name):
        if name == 'append':
            return object.__getattribute__(self, "append")
        return getattr(object.__getattribute__(self, "_child"), name)



class StdInLogFiles(object):
    """Reads from stdin instead of files"""
    def __init__(self):
        self.logfile = L.StdInLogFile()
        
    def __iter__(self):
        return self.logfile.__iter__()
                
    def next(self):
        if self.logfile:
            return self.logfile.next()
        else:
            raise StopIteration

class ExtPublicationServerLogFiles(CctLogFiles):
    def append(self, file):
        if  L.ExtPublicationServerLogFile.REGEXP.match(os.path.basename(file)):
            object.__getattribute__(self, "_child").append(file)
            
#class ChannelInLogFiles(object):
    
