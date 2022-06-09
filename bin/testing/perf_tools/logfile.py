#
#$Header: /opt/Carmen/CVS/sk_cms_user/bin/testing/perf_tools/logfile.py,v 1.3 2010/01/19 10:10:25 adg349 Exp $
#
__version__ = "$Revision: 1.3 $"
"""
logfile.py
Module for doing:
Wrapper for each logfile, selects file vid class staic variable REGEXP
@date:17Sep2009
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""
import sys
import re
import os
import time

class LogFile(dict):

    REGEXP = re.compile(r'.*')
    
    def __init__(self, file_name):
        self['file'] = file_name
        self._file_info = {}
        self.__check_file()
        self.rev_re = re.compile(r'.*\.\d{1,2}')
        try:
            if self.rev_re.match(self['file']):
                nr = ''.join([e for e in self['file'][-2:] if e.isdigit()])
                self['suffix'] = int(nr)
            else:
                raise 'default'
        except:
            self['suffix'] = 0
        
        
    def __check_file(self):
        if not os.path.exists(self['file']):
            raise IOError('File %s not found'%self['file'])

    def __cmp__(self, other):
        try:
            cmp_val = -cmp(self['suffix'],other['suffix'])
            if cmp_val != 0:
                return cmp_val
        except:
            pass
        return cmp(self['file'],other['file'])
    
    def __iter__(self):
        self._fd = None
        try:
            self._fd = open(self['file'],'r')
        except:
            self.close()
        return self
                
    def next(self):
        try:
            if self._fd:
                line = self._fd.next().replace('\n','')
                return line
            else:
                raise StopIteration
        except StopIteration:
            if self._fd:
                self.close()
            raise StopIteration
        
    def close(self):
        if self._fd:
            self._fd.close()
            self._fd = None



            
class StudioLogFile(LogFile):

    REGEXP = re.compile(r'^studio\..*')
         

class CasLogFile(StudioLogFile):
    
    REGEXP = re.compile(r'^studio\.Planning\..*')

    
class CctLogFile(StudioLogFile):
    
    REGEXP = re.compile(r'^studio\.(Tracking||AlertMonitor||.*TI3\_BATCH.*)\.')
  
    
        
class CctTrackingLogFile(CctLogFile):
    REGEXP = re.compile(r'^studio\.Tracking\.')
        

class CctAlertLogFile(CctLogFile):
    REGEXP = re.compile(r'^studio\.AlertMonitor\.')


class CctTI3LogFile(CctLogFile):
    REGEXP = re.compile(r'^studio\..*TI3_BATCH.*\.')
    

class AccumulateLogFile(LogFile):
    REGEXP = re.compile(r'^accumulate\..*\.')
    
class MiradorLogFile(LogFile):
    REGEXP = re.compile(r'^mirador\..*\.')

class DIGServiceLogFile(LogFile):
    REGEXP = re.compile(r'^services\.log($|\.[0-9])')


class StdInLogFile(dict):
    def __init__(self):
        self.in_stream = sys.stdin
        self['file'] = 'sys.stdin'
    
    def __iter__(self):
        return self
                
    def next(self):
        if self.in_stream:
            line = self.in_stream.next().replace('\n','')
            return line
        else:
            raise StopIteration
        
class ExtPublicationServerLogFile(LogFile):
    REGEXP = re.compile(r'^extpublishserver.*')
