#
#$Header: /opt/Carmen/CVS/sk_cms_user/bin/testing/perf_tools/runner.py,v 1.4 2010/01/19 10:10:25 adg349 Exp $
#
__version__ = "$Revision: 1.4 $"
"""
runner.py
Module for doing:
runner created parser strategies on givven set of logfiles
@date:17Sep2009
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""

import sys
import re
import os
import time

import traceback

from logfile import StdInLogFile
from parsers import ParserFactory

class ParseRunner(list):
    def __init__(self, strategy=ParserFactory.EMPTY, arg = None, parser=None, logfiles=None):

        # either one or the other
        self.arg = arg
        p = not (parser is None)
        l = not (logfiles is None)
        if not (p^l):
            raise Exception('Both parser and logfile are mutually exclusive')
        self._parser = parser
        self._logfiles = logfiles
        self._lines = []
        self._error_files = set()
        self._strategy = strategy
        self._factory = ParserFactory()

    @property
    def strategy(self):
        return self._factory.get_strategy(self._strategy, self.logfile, self.arg)

    @property
    def logfile(self):
        if self._logfiles:
            return self._logfiles.logfile
        else:
            return self._parser.logfile
        
    def __call__(self):
        for _ in self:
            pass
    def __iter__(self):
        if self._parser is not None:
            self._parser.__iter__()
        else:
            self._logfiles.__iter__()
        return self

    def next(self):
        if self._parser is not None:
            line = self._parser.next()
        else:
            line = self._logfiles.next()
        if self.logfile['file'] not in self._error_files:
            try:
                result = self.strategy.parse_line(line)
                if result:
                    str(result)
                    if isinstance(self.logfile, StdInLogFile):
                        print result
                    else:
                        self._lines.append(result)
            except Exception ,err:
                print 'Error parsing line:"%s" in file :%s Err: %s '%(line,
                                                                      self.logfile['file'] ,err)
                traceback.print_exc()
                self.add_error_file()
                
        return line
        
    def add_error_file(self):
        self._error_files.add(self.logfile['file'])
        
    
    def write_info(self, outdir):
        if not outdir or not os.path.isdir(outdir):
            raise IOError('No specified output directory')
        outfile = os.path.join(outdir, self._strategy+'.log')
        fsock = None
        try:
            fsock = open(outfile, 'w')
            self.show_info(where=fsock)
            fsock.close()
        except Exception, err:
            print err
            if fsock:
                fsock.close()
        if self._parser is not None:
            self._parser.write_info(outdir)
           

    
    def show_info(self, where=sys.stdout):
        self._lines.sort()
        print >> where, '################## %s ##################'%self._strategy
        if self._lines:
            print >> where, self._lines[0].str_header()
        for line in self._lines:
            print >> where, line
        print >> where, '---------------------- %s Error files -------------------------'%self.__class__.__name__
        for file in self._error_files:
            print >> where, file
        print >> where, '################# END ##################'
        if self._parser is not None and where==sys.stdout:
            self._parser.show_info()
            
