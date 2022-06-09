#
#$Header: /opt/Carmen/CVS/sk_cms_user/bin/testing/perf_tools/parsers.py,v 1.7 2010/01/28 15:32:08 adg349 Exp $
#
__version__ = "$Revision: 1.7 $"
"""
parsers.py
Module for doing:
Implemented parser strategies for various attributes and logfiles. Includes strategy factory
@date:17Sep2009
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""
import sys
import re
import os
import time
import logfile as L

class LogLine(dict):
    """
    Hold parsed info and help with sorting
    """
    def __init__(self, header):
        self._header = header
        
    def __cmp__(self, other):
       
        return cmp(self['sortval'], other['sortval'])
      
    def __str__(self):

        val = ''
        for e in self._header:
            val += str(self.get(e,'N/A')) +", "
        return val
                
    def str_header(self):
        return ', '.join(self._header)
            
class EmptyStrategy(object):
    """
    To implement parses, simply make a class that takes a wrappedlogfile and returns
    a logline object when interesting propertiy has been found
    """
    def __init__(self, logfile):
        self.logfile = logfile
        
    def parse_line(self, line):
        """
        Do nothing, but really we should use line
        """
        return None
    
class BaseStrategy(EmptyStrategy):
    def __init__(self, logfile):
        EmptyStrategy.__init__(self, logfile)
        self._HEADER = ['file', 'date', 'time']
        self._PROPERTIES = []
        
    def set_line_mtime(self, logline):
        if isinstance(self.logfile,L.StdInLogFile):
            ftime = time.gmtime()
        else:
            mtime = os.path.getmtime(self.logfile['file'])
            ftime = time.gmtime(mtime)
        _date = time.strftime("%Y%m%d",ftime)
        _time = time.strftime("%H:%M:%S",ftime)
        date_time = time.strptime("%s %s"%(_date, _time),'%Y%m%d %H:%M:%S')
        logline['date'] =  _date
        logline['time'] = _time
        logline['sortval'] = date_time
        
    def header(self):
        header = []
        for line in self._HEADER:
            header.append(line)
        for prop in self._PROPERTIES:
            header.append(prop)
        return header   
    
class StudioStrategy(BaseStrategy):

    def __init__(self,logfile):
        BaseStrategy.__init__(self,logfile)
        self._PROPERTIES = []
        self._MODES = []
        self.flag_1 = False
        self.flag_2 = False
        self.current_lines = []
        self.time_re = re.compile(r'.*(?<=^time\: ).*',re.IGNORECASE)
        self.next_line_is_time = False
        
    def parse_properties(self, logline):
        for item in self._PROPERTIES:
            for _line in [_line for _line in self.current_lines  if item in _line]:
                tmp_line = ''.join([e for e in _line if e in ('.',':') or e.isdigit()])
                real, cpu = tmp_line.split(':')[1:]
                break
            else:
                real, cpu = ("0","0")
            logline[item+'_real'] = real
            logline[item+'_cpu'] = cpu
            
    def set_line_time(self, logline):
        _date, _time = "None", "None"
        for line in self.current_lines:
            if self.time_re.match(line):
                _, _date, _time = line.split(' ')
                date_time = time.strptime("%s %s"%(_date, _time),'%Y%m%d %H:%M:%S')
                logline['date'] =  _date
                logline['time'] = _time
                logline['sortval'] = date_time
                return
            
            
    def header(self):
        header = []
        for line in self._HEADER:
                header.append(line)
        for prop in self._PROPERTIES:
            if self._MODES:
                for mode in self._MODES:
                    header.append(prop+'_'+mode)
            else:
                header.append(prop)
        return header
        
class StudioOpenPlanStrategy(StudioStrategy):
    """Parse open plan time"""
    
    def __init__(self, logfile):

        StudioStrategy.__init__(self,logfile)
        # Studio Specific regexps and properties
        self._PROPERTIES = ['Total', 'CARMSYS', 'model', 'rave']
        self._ACCUMULATORS = ['int', 'rel', 'time']
        self._MODES = ['real', 'cpu']
        self._FULL_HEADER = []
        self._STR_HEADER = []

        
        self._DAVE_FILTERS={'period.start':re.compile(r'(?!.*acc.*).*(?<=period.start = ).*',re.IGNORECASE),
                            'period.end':re.compile(r'(?!.*acc.*).*(?<=period.end = ).*',re.IGNORECASE),
                            'crew_filter_start':re.compile(r'.*(?<=crew_user_filter_cct.start = ).*',re.IGNORECASE),
                            'crew_filter_quals':re.compile(r'.*(?<=crew_user_filter_cct.quals = ).*',re.IGNORECASE),
                            'crew_rankregion1':re.compile(r'.*(?<=crew_user_filter_cct.rankregion1 = ).*',
                                                          re.IGNORECASE),
                            'crew_rankregion2':re.compile(r'.*(?<=crew_user_filter_cct.rankregion2  = ).*',
                                                          re.IGNORECASE)}


        self.dave_filter_re = re.compile(r'.*davefiltertool.*',re.IGNORECASE)
        self.open_plan_start_re = re.compile(r'.*dispatching.*openplan\.loadplan.*',re.IGNORECASE)
        self.summary_re = re.compile(r'.*\-\-\-\-\-.*',re.IGNORECASE)

        # Accumulators
        self.acc_start_re = re.compile(r'.*load etable _builtin.accumulator.*',re.IGNORECASE)
        self.acc_end_re = re.compile(r'.*finished load.*',re.IGNORECASE)
        self.acc_int_re = re.compile(r'.*accumulator_int.*',re.IGNORECASE)
        self.acc_rel_re = re.compile(r'.*accumulator_rel.*',re.IGNORECASE)
        self.acc_time_re = re.compile(r'.*accumulator_time.*',re.IGNORECASE)
        

        self.current_acc = -1
        self.acc_lines = {'int':'','rel':'','time':''}



    
    def header(self):
        if not self._FULL_HEADER:
            header = StudioStrategy.header(self)

            for acc in self._ACCUMULATORS:
                for mode in self._MODES:
                    header.append('acc_'+acc+'_'+mode)
                header.append('acc_'+acc+'_rows')
            for prop,item in self._DAVE_FILTERS.items():
                header.append(prop)
                
            self._FULL_HEADER = header
        
        return self._FULL_HEADER

    
    def parse_line(self, line):
        # Open plan times
        # Ok, we are opening a plan, next log line is timestamp, catch that
        if not self.flag_1 and \
               self.open_plan_start_re.match(line):
            self.next_line_is_time = True
            self.flag_1 = True
            
            
        elif self.next_line_is_time:
            # get timestamp
            
            
            self.current_lines.append(line)
            self.next_line_is_time = False
        # Ok, now we are setting filters, i.e we are loading plan
        elif self.flag_1 and self.dave_filter_re.match(line):
            for item, regexp in self._DAVE_FILTERS.items():
                if  regexp.match(line):
                    self.current_lines.append(line)
                    break
        
        elif self.flag_1 and not self.flag_2 and \
                 self.summary_re.match(line):
            # In open plan times summary we
            # collect rows
            
            
            self.flag_2 = True
        elif self.summary_re.match(line) and \
                 self.flag_1 and self.flag_2:
            # Ok at en of summary, parse collected rows and reset
            
            
            self.flag_1 = False
            self.flag_2 = False
            result = self.parse_current_lines()
            self.current_lines = []
            return result
            
        elif self.flag_2:
            # In summary, collect all lines
            self.current_lines.append(line)

        # load accumulators
        # Two lines, first is name of acc, second is statistics
        if self.flag_1 and \
               self.acc_start_re.match(line)  and \
               self.current_acc == '':
            if self.acc_int_re.match(line):
                self.current_acc = 'int'
            elif self.acc_rel_re.match(line):
                self.current_acc = 'rel'
            elif self.acc_time_re.match(line):
                self.current_acc = 'time'
        elif  self.current_acc != '' and \
                 self.acc_end_re.match(line) and \
                 self.flag_1:
            
            
            self.acc_lines[self.current_acc] = line
            self.current_acc = ''
            
        return None

  
    def parse_acc_load(self, acc, line):
        if line:
            tmp_line = line.replace('.',',')
            tmp_line = ''.join([e for e in tmp_line if e.isdigit() or e == ','])
            (rows, select_real, select_cpu,
             read_real, read_cpu) = [int(e) for e in tmp_line.split(',') if e]
            real =  str(round(((select_real+read_real)/1000.0),2))
            cpu = str(round(((select_cpu+read_cpu)/1000.0),2))
        else:
            cpu = real = rows = "0"

        return rows, real , cpu
        
    def parse_current_lines(self):
        logline = LogLine(self.header())
        logline['file'] = self.logfile['file']
        self.set_line_time(logline)
        
        for item, regexp in self._DAVE_FILTERS.items():
            for line in  self.current_lines:
                val = regexp.match(line)
                if val:
                    _, val = str(val.group(0)).replace(' ','').split('=')
                    break
            else:
                val = "N/A"
            logline[item] = val  

        # main parse
        self.parse_properties(logline)
        
        for acc in self._ACCUMULATORS:
            rows, real, cpu = self.parse_acc_load(acc, self.acc_lines.get(acc,''))
            logline['acc_'+acc+'_rows'] = rows
            logline['acc_'+acc+'_real'] = real
            logline['acc_'+acc+'_cpu'] = cpu
        self.acc_lines = {'int':'','rel':'','time':''}
        return logline

class CctOpenPlanStrategy(StudioOpenPlanStrategy):
    pass

class ExtPubServerOpenPlanStrategy(CctOpenPlanStrategy):
    def __init__(self, logfile):
        CctOpenPlanStrategy.__init__(self, logfile)
        
        self.open_plan_start_re = re.compile(r'.*about to open subplan.*',re.IGNORECASE)
    
   
        
    def set_line_time(self, logline):
        # use files mtime, since ext pub server only opens once
        self.set_line_mtime(logline)
        
class CasOpenPlanStrategy(StudioOpenPlanStrategy):
    def __init__(self, logfile):
        StudioOpenPlanStrategy.__init__(self, logfile)
        self.open_plan_start_re = re.compile(r'.*dispatching.*cuiplanmanager.*',re.IGNORECASE)
        self._DAVE_FILTERS={'period.start':re.compile(r'(?!.*acc.*).*(?<=period.start = ).*',re.IGNORECASE),
                            'period.end':re.compile(r'(?!.*acc.*).*(?<=period.end = ).*',re.IGNORECASE),
                            'crew_filter_start':re.compile(r'.*(?<=crew_user_filter_quals.start = ).*',re.IGNORECASE),
                            'emp_rankregion':re.compile(r'.*(?<=crew_user_filter_employment.rankregion = ).*',
                                                          re.IGNORECASE),
                            'crew_qual':re.compile(r'.*(?<=crew_user_filter_quals.quals = ).*',
                                                          re.IGNORECASE)}
        self._HEADER.append('storage')
        self.storage = 'file'
        
        
    def parse_acc_load(self, acc, line):
        if line:
            tmp_line = line.replace('.',',')
            tmp_line = ''.join([e for e in tmp_line if e.isdigit() or e == ','])
            (rows, real, cpu) = [int(e) for e in tmp_line.split(',') if e]
            real =  str(round(((real)/1000.0),2))
            cpu = str(round(((cpu)/1000.0),2))
        else:
            cpu = real = rows = "0"

        return rows, real , cpu
    
    def parse_line(self, line):
        if self.flag_1 and  self.dave_filter_re.match(line):
            self.storage = 'db'
        return StudioOpenPlanStrategy.parse_line(self, line)

    def parse_current_lines(self):
        logline = StudioOpenPlanStrategy.parse_current_lines(self)
        logline['storage'] = self.storage
        self.storage = 'file'
        return logline

class AlertOpenPlanStrategy(CctOpenPlanStrategy):
    """
    Parse open plan times
    """
    def __init__(self, logfile):
        CctOpenPlanStrategy.__init__(self, logfile)
        # AM will always open plan
        self.open_plan_start_re = re.compile(r'.*dispatching.*initwebserver.*',re.IGNORECASE)


class TI3OpenPlanStrategy(CctOpenPlanStrategy):
    """
    Parse open plan times
    """
    
    def __init__(self, logfile):
        CctOpenPlanStrategy.__init__(self, logfile)
        # AM will always open plan
        self.open_plan_start_re = re.compile(r'.*dispatching.*ti3batchsave.*',re.IGNORECASE)

    def set_line_time(self, logline):
        self.set_line_mtime(logline)

class CctSavePlanStrategy(StudioStrategy):
     
    def __init__(self,logfile):
        StudioStrategy.__init__(self, logfile)
        self._HEADER = ['file', 'date', 'time']
        self._PROPERTIES = ['Total',
                            'Accounthandler',
                            'attributes',
                            'pre-processing',
                            'meals', '(sys) save',
                            'post-processing']
        
        self._MODES = ['real', 'cpu']
        self._FULL_HEADER = None
        self._STR_HEADER = None

        self.summary_re = re.compile(r'.*\-\-\-\-\-.*',re.IGNORECASE)
        self.save_start_re = re.compile(r'.*dispatching.*openplan\.saveplan.*',re.IGNORECASE)
        
    def parse_line(self, line):
        
        if not self.flag_1 and \
               self.save_start_re.match(line):
            self.flag_1 = True
            self.next_line_is_time = True
        elif self.next_line_is_time:
            self.current_lines.append(line)
            self.next_line_is_time = False
        elif self.flag_1 and \
                 not self.flag_2 and \
                 self.summary_re.match(line):
            self.flag_2 = True
        elif self.flag_2 and self.summary_re.match(line):
            result = self.parse_current_lines()
            self.flag_1 = self.flag_2 = False
            self.current_lines = []
            return result
        elif self.flag_1 and self.flag_2:
            self.current_lines.append(line)
        return []
    
    def parse_current_lines(self):
        logline = LogLine(self.header())
        logline['file'] = self.logfile['file']
        self.set_line_time(logline)
        self.parse_properties(logline)

        return logline



class CctTI3SavePlanStrategy(CctSavePlanStrategy):

    def set_line_time(self, logline):
        self.set_line_mtime(logline)
        
        
class CctExtPubSavePlanStrategy(CctSavePlanStrategy):
    def __init__(self,logfile):
        CctSavePlanStrategy.__init__(self, logfile)
        self.save_start_re = re.compile(r'.*external publish saving plan.*',re.IGNORECASE)
        self.time_re = self.save_start_re
        
    def parse_line(self, line):
        if not self.flag_1 and \
               self.save_start_re.match(line):
            self.flag_1 = True
            self.current_lines.append(line)
        elif self.flag_1 and \
                 not self.flag_2 and \
                 self.summary_re.match(line):
            self.flag_2 = True
        elif self.flag_2 and self.summary_re.match(line):
            result = self.parse_current_lines()
            self.flag_1 = self.flag_2 = False
            self.current_lines = []
            return result
        elif self.flag_1 and self.flag_2:
            self.current_lines.append(line)
        return []

    def set_line_time(self, logline):
        for line in self.current_lines:
            if self.time_re.match(line):
                line = line.replace(' INFO External publish saving plan...','')
                
                date_time = time.strptime(line,'%a, %d %b %Y %H:%M:%S')
                logline['date'] = "%s%s%s"%tuple(date_time)[0:3]
                logline['time'] = "%.2d:%.2d:%.2d"%(tuple(date_time)[3:6])
                logline['sortval'] = date_time
                return
            
class CctCslDispatcherSavePlanStrategy(StudioStrategy):

    def __init__(self,logfile):
        StudioStrategy.__init__(self, logfile)
        self._HEADER = ['file', 'date', 'time']
        self._PROPERTIES = ['csl_cpu']
        
        self._FULL_HEADER = None
        self._STR_HEADER = None

        self.save_start_re = re.compile(r'.*dispatching.*openplan\.saveplan.*',re.IGNORECASE)
        self.save_end_re = re.compile(r'.*guidispatchexeccb.*pythonevalexpr.*carmensystems.studio.tracking.openPlan.saveplan.*',re.IGNORECASE)
        

    def parse_line(self, line):
        
        if self.save_start_re.match(line):
            self.next_line_is_time = True
        elif self.next_line_is_time:
            self.current_lines.append(line)
            self.next_line_is_time = False
        elif self.save_end_re.match(line):
            self.current_lines.append(line)
            result = self.parse_current_lines()
            self.flag_1 = self.flag_2 = False
            self.current_lines = []
            return result
        return []

    def parse_current_lines(self):
        logline = LogLine(self.header())
        logline['file'] = self.logfile['file']
        self.set_line_time(logline)
        for line in self.current_lines:
            if self.save_end_re.match(line):
                logline['csl_cpu'] = str(float(re.compile(r'(?<=cpu time )(.*) ms').search(line).group(1))/1000.0)
        return logline

class CoreDumpStrategy(StudioStrategy):

    def __init__(self, logfile):
        StudioStrategy.__init__(self, logfile)
        self.core_re = re.compile('.*testing for core.*',re.IGNORECASE)
        
    def parse_line(self, line):
        if self.core_re.match(line):
            logline = LogLine(self.header())
            logline['file'] = self.logfile['file']
            self.set_line_time(logline)
            return logline
        
    def set_line_time(self, logline):
        self.set_line_mtime(logline)

class CrewServiceMsgStrategy(BaseStrategy):
    def __init__(self,logfile):
        BaseStrategy.__init__(self,logfile)
        self.start_re = re.compile(r'.*created process proc\d{1,5}.*',re.IGNORECASE)
        self.end_re = re.compile(r'.*exit proc\d{1,5}.*',re.IGNORECASE)
        self.current_line = []
        self.start_proc_re = re.compile(r'(?<=process proc).*',re.IGNORECASE)
        
        self.end_proc_re = re.compile(r'(?<=exit proc).*',re.IGNORECASE)
        self.current_proc = ''
        self.in_parse = False
        self.gmtimes = {}
        self.report_re = re.compile(r'.*using report script source.*',re.IGNORECASE)
        self.get_report_re = re.compile('(?<=report\_sources\.report\_server\.).*',re.IGNORECASE)
        self._HEADER = ['file','timestamp','proc','time','report','report_int','crew', 'data']
        self.data_re = re.compile(r'reportrequesthandler for request\: (.*)', re.IGNORECASE)
        
    def parse_line(self, line):
        if self.start_re.match(line):
            try:
                proc = self.start_proc_re.search(line).group(0)
                start = time.mktime(time.strptime(line[3:22],'%Y-%m-%d %H:%M:%S'))
                start = start+float("0."+line[23:26])
                self.gmtimes[proc] = [start,'','','']
            
                self.current_proc = proc
            except:
                #print 'Vorkert parse %s'%line
                self.current_proc = ''
        elif self.report_re.match(line) and self.current_proc != '':
            try:
                self.gmtimes[self.current_proc][1] = self.get_report_re.search(line).group(0)
                self.current_proc == ''
            except:
                #print 'Vorkert parse %s'%line
                pass
        elif self.data_re.search(line):
            try:
                data_line = self.data_re.search(line).group(1)
                data_line = '"%s"'%(data_line.replace(',','|'))
                self.gmtimes[self.current_proc][2] = data_line
                self.gmtimes[self.current_proc][3] = data_line.split('|')[1]
            except:
                if self.current_proc != '':
                    self.gmtimes[self.current_proc][2] = 'N/A'
                    self.gmtimes[self.current_proc][2] = '00000'
        elif self.end_re.match(line):
            
            try:
                end = time.mktime(time.strptime(line[3:22],'%Y-%m-%d %H:%M:%S'))
                end = end+float("0."+line[23:26])
                proc = self.end_proc_re.search(line).group(0)
                start = self.gmtimes[proc][0]
                report =  self.gmtimes[proc][1]
                logline = LogLine(self.header())
                logline['file'] = self.logfile['file']
                logline['timestamp'] = line[3:22]
                logline['sortval'] = end
                logline['proc'] = proc
                logline['time'] = str(round((end -start),3))
                logline['report'] = report
                logline['report_int'] = len(report)
                logline['data'] = self.gmtimes[proc][2]
                logline['crew'] = self.gmtimes[proc][3]
                del self.gmtimes[proc]
                return logline
            except:
                #print 'Vorkert parse %s'%line
                return None
        return None
            #del self.gmtimes[proc]

class ScatterCrewServiceMsgStrategy(CrewServiceMsgStrategy):
    def parse_line(self, line):
        result = CrewServiceMsgStrategy.parse_line(self, line)
        if result:
            logline=LogLine(['epoch','report_int'])
            logline['epoch'] = result['sortval']
            logline['report_int'] = len(result['report'])
            return logline
        
class AggCrewServiceMsgStrategy(CrewServiceMsgStrategy):

    def __init__(self, logfile, cutoff=1.0):
        CrewServiceMsgStrategy.__init__(self, logfile)
        self.current_time = -1.0
        self.agg_lines= []
	try:
            self._cutoff = 60.0*float(cutoff)
        except:
            self._cutoff = 60.0
        self._reports = []
    
    def parse_line(self, line):
        logline = CrewServiceMsgStrategy.parse_line(self, line)
        #print logline
	if logline:
            try:
                line_time = logline['sortval']
                #print abs(line_time-self.current_time)
		#print self._cutoff
		if self.current_time < 0:
                    self.current_time = line_time
                elif abs(line_time - self.current_time) <= self._cutoff:
                    self.agg_lines.append(logline)
                elif abs(line_time - self.current_time) > self._cutoff:
                    result = self.__parse_agg_lines()
                    self.agg_lines = []
                    self.current_time = line_time
                    return result
                
            except  Exception, err:
                print 'errr', err
                self.agg_lines = []
                self.current_time = line_time
    
    def __parse_agg_lines(self):
        if not self.agg_lines:
            return None #short cuircuit
        agg_count = {}
        self.agg_lines.sort()
        for logline in self.agg_lines:
            report = logline['report']
            f_time = float(logline['time'])
            if agg_count.has_key(report):
                agg_count[report][0] += 1
                agg_count[report][1] += f_time
                #max/min
                if agg_count[report][2] < f_time:
                    agg_count[report][2] = f_time
                if agg_count[report][3] > f_time:
                    agg_count[report][3] = f_time
            else:
                agg_count[report] = [1, f_time, f_time, f_time]
                if report not in set(self._reports):
                    self._reports.append(report)
        header = [e for e in self.header() if e not in ('report','proc','time',
                                                        'data', 'report_int', 'crew')]
        header += self._reports
        logline = LogLine(header)
        #use last agg as marker
        logline['file'] = self.agg_lines[-1]['file']
        logline['timestamp'] = self.agg_lines[-1]['timestamp']
        logline['sortval'] = self.agg_lines[-1]['sortval']
        for report in self._reports:
            if agg_count.has_key(report):
                count = agg_count[report][0]
                mu = str(round(agg_count[report][1]/count,2))
                max_ =  str(round(agg_count[report][2],2))
                min_ = str(round(agg_count[report][3],2))
            else:
                count = 0
                mu = 0
                max_ = 0
                min_ = 0
            logline[report] = '%s : %s/%s/%s/%s'%(report, count, mu, min_, max_)
        
        return logline

class CctAMRefreshStrategy(StudioStrategy):
    """
    Command service openTask YnEWZLgKEd6EvQAfKc9/vA==
    ...
    StudioEditor::refresh starting at Tue Oct 13 15:09:22 2009
    StudioEditor memory usage: 1745190912.0  resident :1561980928.0 stack: 1241088.0 
    StudioEditor::refresh::Plan data took 2 second(s)
    StudioEditor memory usage: 1745190912.0  resident :1562050560.0 stack: 1241088.0
    ...
    cslDispatcher: returnvalue was 0, real time 6620 ms, cpu time 4260 ms
    """
    def __init__(self, logfile):
        StudioStrategy.__init__(self, logfile)
        self.dispatch_start_re = re.compile(r'.*csldispatcher\: dispatching.*',re.IGNORECASE)
        self.dispatch_end_re = re.compile(r'.*csldispatcher\: returnvalue was.*',re.IGNORECASE)
        self.refresh_start_re = re.compile(r'.*command service opentask.*',re.IGNORECASE)
        self._PROPERTIES = ['refresh_real', 'refresh_cpu']
        
        self.current_time_line = ''
        self.current_dispatch_lvl = 0
        self.refresh_dispatch_lvl = 0
    def parse_line(self, line):
        if self.flag_1 and self.dispatch_start_re.match(line):
            self.current_dispatch_lvl += 1
        if self.flag_1 and self.dispatch_end_re.match(line):
            self.current_dispatch_lvl -= 1
        if self.refresh_start_re.match(line):
            self.current_lines.append(self.current_time_line)
            self.flag_1 = True   
        elif self.time_re.match(line):
            self.current_time_line = line
        elif self.dispatch_end_re.match(line) and self.flag_1 and \
                 self.current_dispatch_lvl == -1:
            logline = LogLine(self.header())
            logline['file'] = self.logfile['file']
            self.set_line_time(logline)
            _, real, cpu = ''.join([e for e in line if e.isdigit() or e == ","]).split(',')
            logline['refresh_real'] = str(round(float(real)/1000.0,2))
            logline['refresh_cpu'] = str(round(float(cpu)/1000.0,2))
            
            self.current_dispatch_lvl = 0
            self.current_lines = []
            self.flag_1 = False
            return logline
        return None
    
class CctGuiRefreshStrategy(StudioStrategy):
    """
    guiDispatchExecCB: PythonEvalExpr(\"carmensystems.studio.Tracking.OpenPlan.refres
    hGui()\") real time 12470 ms, cpu time 11350 ms
    """
    def __init__(self, logfile):
        StudioStrategy.__init__(self, logfile)
        self.refresh_end_re = re.compile(r'.*guidispatchexeccb.*\.openplan\.refreshgui.*',re.IGNORECASE)
        self.refresh_start_re = re.compile(r'.*dispatching.*openplan\.refreshgui.*',re.IGNORECASE)
        self._PROPERTIES = ['refresh_real', 'refresh_cpu']
 
        
    def parse_line(self, line):
        if self.refresh_start_re.match(line):
            self.next_line_is_time = True
        elif self.next_line_is_time:
            self.current_lines.append(line)
            self.next_line_is_time = False
        elif self.refresh_end_re.match(line):
            logline = LogLine(self.header())
            logline['file'] = self.logfile['file']
            self.set_line_time(logline)
            real, cpu = ''.join([e for e in line if e.isdigit() or e == ","]).split(',')
            logline['refresh_real'] = str(round(float(real)/1000.0,2))
            logline['refresh_cpu'] = str(round(float(cpu)/1000.0,2))
            self.current_lines = []
            return logline
        return None
    
class CctRefreshStrategy(StudioStrategy):


    def __init__(self, logfile):
        StudioStrategy.__init__(self, logfile)
        self.gui_refresh = CctGuiRefreshStrategy(logfile)
        self.am_refresh = CctAMRefreshStrategy(logfile)
     #   self._PROPERTIES = ['refresh_real', 'refresh_cpu']
        
    def parse_line(self, line):
        try:
            logline = self.gui_refresh.parse_line(line)
            if logline:
                return logline
            logline = self.am_refresh.parse_line(line)
            if logline:
                return logline
        except:
            return None
        return None
            
            
            
        
class CmpAccStrategy(BaseStrategy):
    
    def __init__(self, logfile):
        BaseStrategy.__init__(self, logfile)

        self.flag_1 = False
        self._PROPERTIES = []
        self.__set_current_lines()

        self.end_re = re.compile(r'.*accumulation status.*',re.IGNORECASE)
        self.range = range(0,len(self.current_lines))

        
        for item_ix in self.range:
            name = self.current_lines[item_ix]['name']
            self._PROPERTIES.append(name)
            if not self.__name_is_attr(name) and '_end' in name:
                self._PROPERTIES.append(name.replace('_end','_length'))
                
                
                
    def __name_is_attr(self, name):
        return name in ('category', 'acc_from', 'acc_to')
    
    def __set_current_lines(self):
        self.current_lines = [{'name':'category','re':re.compile(r'.*\<category\>.*', re.IGNORECASE),
                               'val':''},
                              {'name':'acc_from','re':re.compile(r'.*\<acc_from\>.*', re.IGNORECASE),
                               'val':''},
                              {'name':'acc_to','re':re.compile(r'.*\<acc_to\>.*', re.IGNORECASE),
                               'val':''},
                              {'name':'load_start','re':re.compile(r'.*initiating load.*', re.IGNORECASE),
                               'val':''},
                              {'name':'load_end','re':re.compile(r'.*loaded tables(?! \"\[\'accumulator_int_run.*)',
                                                                 re.IGNORECASE),
                               'val':''},
                              {'name':'roster_start','re':re.compile(r'.*building the rosters.*', re.IGNORECASE),
                               'val':''},
                              {'name':'roster_end','re':re.compile(r'.*completed load.*', re.IGNORECASE),
                               'val':''},
                              {'name':'assignment_start','re':re.compile(r'.*started.*assignments.*', re.IGNORECASE),
                               'val':''},
                              {'name':'assignment_end','re':re.compile(r'.*finished.*assignments.*', re.IGNORECASE),
                               'val':''},
                              {'name':'vac_start','re':re.compile(r'.*started.*vacations.*', re.IGNORECASE),
                               'val':''},
                              {'name':'vac_end','re':re.compile(r'.*finished.*vacations.*', re.IGNORECASE),
                               'val':''},
                              {'name':'save_start','re':re.compile(r'.*finished.*user.*scripts', re.IGNORECASE),
                               'val':''},
                              {'name':'save_end','re':re.compile(r'.*accumulation status.*', re.IGNORECASE),
                               'val':''}
                              ]
        
        
    def parse_line(self, line):

        for item_ix in self.range:
            regexp = self.current_lines[item_ix]['re']
            if regexp.match(line):
                self.current_lines[item_ix]['val']= line[0:200]

        if self.end_re.match(line):
            logline = LogLine(self.header())
            logline['file'] = self.logfile['file']
            self.set_line_mtime(logline)
            result = self.__parse_current_lines(logline)
            self.__set_current_lines()
            self.flag_1 = False
            return result
        
        return []

    def __get_na(self, name):
        if '_start' in name or '_end' in name:
            return 'N A'
        else:
            return 'N/A'
    def __parse_current_lines(self, logline):


        for item_ix in self.range:
            name = self.current_lines[item_ix]['name']
            try:
                val = self.current_lines[item_ix]['val']
                if self.__name_is_attr(name):
                    regexp_str='(?<=%s\>\=)\w+'%name
                    logline[name] = re.compile(regexp_str).search(val).group()
                else:
                    try:
                        time_stamp = time.strptime(val[0:19],'%Y-%m-%d %H:%M:%S')
                        self.current_lines[item_ix]['val'] = time_stamp
                    except:
                        self.current_lines[item_ix]['val'] = time.strptime('0000-01-01 00:00:00','%Y-%m-%d %H:%M:%S')
            except:
                logline[name] = self.__get_na(name)
                
        for item_ix in self.range:
            name = self.current_lines[item_ix]['name']
            if self.__name_is_attr(name) or item_ix < 2:
                continue
            try:
                logline[name] = time.strftime('%Y-%m-%d %H:%M:%S', self.current_lines[item_ix]['val'])
                if '_end' in name:
                    try:
                        prev_time = time.mktime(self.current_lines[item_ix-1]['val'])
                        this_time = time.mktime(self.current_lines[item_ix]['val'])
                        logline[name.replace('_end','_length')] = str(this_time-prev_time)
                    except:
                        logline[name.replace('_end','_length')] = "N/A"

            except:
                logline[name] = self.__get_na(name)
                if '_end' in name:
                    logline[name.replace('_end','_length')] = "N/A"
        return logline


class ParserFactory(object):
    EMPTY = 'EMPTY'
    OPEN  = 'OPEN_TIMES'
    SAVE  = 'SAVE_TIMES'
    SAVE_CSL = 'SAVE_TIME_CSL'
    CORE = 'CORE_DUMPS'
    CMP_ACC = 'CMP_ACC'
    REFRESH = 'REFRESH'
    REQ_REPLY_TIME = 'REQ_REPLY_TIME'
    AGG_REQ_REPLY_TIME = 'AGG_REQ_REPLY_TIME'
    SCATTER_REQ_REPLY_TIME = 'SCATTER_REQ_REPLY_TIME'
    
    def __init__(self):

        self._current = None
        self._current_key = None

            
    def get_strategy(self, strategy, logfile, arg=None):
        """
        Only create new parser strategy when we have a new logfile
        """
        if self._current is None or \
               id(logfile) != self._current_key:
            
            if strategy == self.__class__.OPEN:
                if  isinstance(logfile,L.CctAlertLogFile):
                    self._current = AlertOpenPlanStrategy(logfile)
                    
                elif isinstance(logfile,L.CctTI3LogFile):
                    self._current = TI3OpenPlanStrategy(logfile)
            
                elif isinstance(logfile,L.CctLogFile):
                    self._current = CctOpenPlanStrategy(logfile)
                elif isinstance(logfile,L.CasLogFile):
                    self._current = CasOpenPlanStrategy(logfile)    
                elif isinstance(logfile,L.StdInLogFile):
                    self._current = CctOpenPlanStrategy(logfile)
                elif isinstance(logfile,L.ExtPublicationServerLogFile):
                    self._current = ExtPubServerOpenPlanStrategy(logfile)

            elif  strategy == self.__class__.SAVE_CSL:
                if  isinstance(logfile,L.CctLogFile):
                    self._current = CctCslDispatcherSavePlanStrategy(logfile)            
            elif  strategy == self.__class__.SAVE:
                if  isinstance(logfile,L.CctLogFile):
                    self._current = CctSavePlanStrategy(logfile)
                

                elif isinstance(logfile,L.CctTI3LogFile):
                    self._current = CctTI3SavePlanStrategy(logfile)
                elif isinstance(logfile,L.StdInLogFile):
                    self._current = CctSavePlanStrategy(logfile)
                elif isinstance(logfile,L.ExtPublicationServerLogFile):
                    self._current = CctExtPubSavePlanStrategy(logfile)

            elif  strategy == self.__class__.CORE:
                self._current = CoreDumpStrategy(logfile)

            elif strategy == self.__class__.CMP_ACC:
                self._current = CmpAccStrategy(logfile)

            elif strategy == self.__class__.REFRESH:
                self._current = CctRefreshStrategy(logfile)

            elif strategy == self.__class__.REQ_REPLY_TIME:
                if isinstance(logfile,L.DIGServiceLogFile) or \
                       isinstance(logfile,L.StdInLogFile):  
                    self._current = CrewServiceMsgStrategy(logfile)
            elif strategy == self.__class__.AGG_REQ_REPLY_TIME:
                if isinstance(logfile,L.DIGServiceLogFile) or \
                       isinstance(logfile,L.StdInLogFile):  
                    self._current = AggCrewServiceMsgStrategy(logfile, arg)       
            elif strategy == self.__class__.SCATTER_REQ_REPLY_TIME:
                if isinstance(logfile,L.DIGServiceLogFile) or \
                       isinstance(logfile,L.StdInLogFile):  
                    self._current = ScatterCrewServiceMsgStrategy(logfile)           

            if self._current is None:
                    self._current = EmptyStrategy(logfile)

            self._current_key = id(logfile)

        return self._current
