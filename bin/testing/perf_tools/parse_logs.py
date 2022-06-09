#!/usr/bin/env python
#
#$Header: /opt/Carmen/CVS/sk_cms_user/bin/testing/perf_tools/parse_logs.py,v 1.4 2010/01/19 11:13:54 adg349 Exp $
#
__version__ = "$Revision: 1.4 $"
"""
parser_logs.py
Module for doing:
Command line parser start, takes argument syntax and creates logfile list and parsers
@date:17Sep2009
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""
import sys
import re
import os
import time

from runner import ParseRunner
from parsers import ParserFactory

import logfiles as L
logfiles = {'log':L.LogFiles,
            'cct':L.CctLogFiles,
            'cas':L.CasLogFiles,
            'time':L.TimeLogFiles,
            'acc':L.CmpAccLogFiles,
            'digservlog':L.DIGServiceLogFiles,
            'stdin':L.StdInLogFiles,
            'extpub':L.ExtPublicationServerLogFiles}
    
parsers  = {'studioopenplan':ParserFactory.OPEN,
            'studiosaveplan':ParserFactory.SAVE,
            'studiocslsaveplan':ParserFactory.SAVE_CSL,
            'studiocoredump':ParserFactory.CORE,
            'cmpacc':ParserFactory.CMP_ACC,
            'studiorefresh':ParserFactory.REFRESH,
            'reqreply':ParserFactory.REQ_REPLY_TIME,
            'aggreqreply':ParserFactory.AGG_REQ_REPLY_TIME,
            'scatterreqreply':ParserFactory.SCATTER_REQ_REPLY_TIME,
            'empty':ParserFactory.EMPTY}

def print_usage():
    print 'Usage is parse_logs.py syntax [dir], if no dir then reads from stdin'
    print "Syntax is 'file:<logfilefilter>:<arg>|parse:<desired parser>:[arg]|mode:<option>:[arg]'"
    print 'Current implemented tools:'
    for item in logfiles:
        print "'file:%s:'    - %s"%(item,logfiles[item].__doc__)
    for item in parsers:
        print "'parse:%s:'    - %s"%(item,parsers[item])

def get_logfiles(syntax):
    current_log = logfiles['log']()

    # Create log file selection
    if syntax:
        for item in [item.lower() for item in syntax.split('|') if 'file:' in item]:
            try:
                _, log, arg = item.split(':')
                print 'Adding logfilter %s, %s'%(log, arg)
                current_log = logfiles[log](arg, current_log)
            except Exception, err:
                print err
                print 'Unknown logfile selection or arg: %s, %s'%(log, arg)
                return 1
  
    return current_log

def get_parsers(syntax, current_log):
    # Add parsers
    current_parser = None
    if syntax:
        for item in [item.lower() for item in syntax.split('|') if 'parse:' in item]:
            try:
                _, log, arg = item.split(':')
                
                print 'Adding parser %s, %s'%(log, arg)
                if current_parser is not None:
                    current_parser = ParseRunner(strategy=parsers[log],
                                                 arg=arg,
                                                 parser=current_parser,
                                                 logfiles=None)
                else:
                    current_parser = ParseRunner(strategy=parsers[log],
                                                 arg=arg,
                                                 parser=None,
                                                 logfiles=current_log)
            except Exception, err:
                print err
                print 'Unknown parser selection or arg: %s, %s'%(log, arg)
                return 1
            
    if current_parser is None:
        print 'Unable to parse syntax "%s", defaulting parser to empty'%syntax
        current_parser = ParseRunner(arg=0,
                                     strategy=ParserFactory.EMPTY,
                                     parser=None,
                                     logfiles=current_log)
    return current_parser

def parse_stdin(syntax):
    logfiles = L.StdInLogFiles()
    parser = get_parsers(syntax,logfiles)
    parser()
    

def parse_dir(dir, syntax = ""):

    dir = os.path.abspath(dir)
    
    current_log = get_logfiles(syntax)
    current_parser = get_parsers(syntax, current_log)
    # Add files
    for file in [os.path.join(dir,file) for file in os.listdir(dir)]:
        if not os.path.isfile(file):
            continue
        try:
            current_log.append(file)
        except Exception, err:
            print err,'h'
            pass
 

    # run the whole shebang
    print '-------------  Parsing %s files -----------------'% current_log.__len__()
    current_parser()
    if syntax:
        for item in [item for item in syntax.split('|') if 'mode' in item]:
            try: 
                _, mode, arg = item.split(':')
                if mode.lower() == 'write':
                    current_parser.write_info(arg)
                elif mode.lower() == 'show':
                    current_parser.show_info() 
            except Exception, err:
                print err
                print 'Unknown mode: %s, %s'%(log, arg)
                return 1
    else:
        current_parser.show_info()


        
if __name__=="__main__":
    if len(sys.argv) == 1:
        print_usage()
        sys.exit(1)
    if len(sys.argv) == 2:
        parse_stdin(sys.argv[1])
    elif len(sys.argv) == 3:

        try:
            syntax = sys.argv[1]
        except:
            syntax = ""
        try:
            DIR = sys.argv[2]
        except:
            print "Error, no supplied log dir"
            sys.exit(1)
        parse_dir(DIR,syntax)
