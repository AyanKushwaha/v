#

#
__version__ = "$Revision$"
"""
PerformaceMonitor
Module for doing:
Logging performance to standard log file and custom logfile
@date:23Feb2009
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""


import os
import Errlog
import time
import resource


# Object for logging used by module
_LOGGER = None

# Get log level

_LOG_SIZE_TO_FILE = 2
_LOG_TIMES_TO_FILE = 1
_NO_LOG = 0 

try:
    _MODE = int(os.environ.get('CARM_LOG_PERF_LEVEL',_NO_LOG))
except:
    _MODE = _NO_LOG
    
_PERFORMANCE_LOG_DIR = 'performance'
_LOG_DIRS = {_NO_LOG:'',
             _LOG_TIMES_TO_FILE:'time',
             _LOG_SIZE_TO_FILE:'table_size'}

class ITimeLogger(list):
    """
    Abstract class for TimeLogger
    """
    def __init__(self, title=""):
        raise NotImplementedError
    
    def tic(self,message=""):
        raise NotImplementedError

    def dialog_reset(self):
        raise NotImplementedError
    
    def reset(self,title=""):
        raise NotImplementedError

    def log(self,message=""):
        raise NotImplementedError
    
class Tic:
    """
    Wrapper for time tic
    """
    _STR_TEMPLATE = "%s: %.2f s (cpu: %.2f s)" 
    _XML_TEMPLATE = '<tic message="%s">\n<real>%f</real>\n<cpu>%f</cpu>\n</tic>\n'
    def __init__(self,message,
                 time,
                 elapsed_time,
                 elapsed_cpu_time):
        self._message = message
        self._time = time
        self._elapsed_time = elapsed_time
        self._elapsed_cpu_time = elapsed_cpu_time
        
    @property
    def timestamp(self):
        return self._time
    @property
    def t(self):
        return self._elapsed_time
    @property
    def cpu_t(self):
        return self._elapsed_cpu_time
    def __cmp__(self, other):
        return cmp(self.timestamp, other.timestamp)
    def __str__(self):
        return Tic._STR_TEMPLATE%(self._message,
                                  self.t,
                                  self.cpu_t)
    def xml(self):
        return Tic._XML_TEMPLATE%(self._message,
                                  self.t,
                                  self.cpu_t)

class TimeLogger(ITimeLogger):
    """
    Logs time stamps to standard studio log channel
    """
    
    def __init__(self, title=""):
        self.reset(title)
        
    def reset(self, title=""):
        self[:] = []
        self._title = title
        self._t = self.__get_time()
        self._cpu_t = self.__get_cpu_time()

    def dialog_reset(self):
        self._t = self.__get_time()
        self._cpu_t = self.__get_cpu_time()
        
    def tic(self, message=""):
        time = self.__get_time()
        cpu_time = self.__get_cpu_time()
        elapsed_time = time - self._t
        elapsed_cpu_time =  cpu_time - self._cpu_t
        # Create Tic
        self.append(Tic(message, time, elapsed_time, elapsed_cpu_time))
        self._t = time
        self._cpu_t = cpu_time
    
    def log(self):
        self.sort()
        message = ['-'*45]
        message.append('  %s:\n    Total: %.2f s (cpu: %.2f s)'%(self._title,
                                                                 self.sum_t(),
                                                                 self.sum_cpu_t()))
        
        for tic in self:
            message.append('    '+str(tic))
        message.append('-'*45)            
        Errlog.log('\n'.join(message))
        ##################################################################################################
        # Start of InfluxDB output code
        # The code below appends the performance stats to a special logfile in InfluxDB line format
        # This logfile can then be tailed by a Telegraf agent and the lines pushed to an InfluxDB instance
        ##################################################################################################
        stat_influxdb_formated = ''
        try:                
            clean_message_header = '%s: %.2f s (cpu: %.2f s),'%(self._title,self.sum_t(),self.sum_cpu_t())
            clean_message =  [':'.join([x.split(':', 1)[0][4:].replace(' ', '_').replace('-','').replace('(','').replace(')',''),x.split(':', 1)[1]]) for x in message[2:-1]]
            clean_message.append('Total: %.2f s (cpu: %.2f s)' %(self.sum_t(),self.sum_cpu_t()))
            clean_message_line = clean_message_header + ','.join(clean_message)
            stat_logger_path = '/var/carmtmp/performance_stats/cms_stats.log'
            stat_logger_user = os.getenv('USER', 'UNKNOWN')
            stat_logger_app = os.getenv('SK_APP', 'SK_APP')
            stat_logger_host = os.getenv('HOSTNAME', os.uname()[1]).split('.')[0].lower()
            ts = "%.9f" % time.time()
            sl_ts = ts.replace('.', '')
            sl_me = 'cms_studio_performance_' + stat_logger_app.lower() + '_' + self._title.split()[0].lower() + ',host=' + stat_logger_host + ',user=' + stat_logger_user
            sl_tags = []
            for piece in clean_message:
                item = piece.split(':')
                sl_tags.append(item[0].lower() + '_s=' + item[1].split(' ')[1] + ',' + item[0].lower() + '_cpu_s=' + item[2].split(' ')[1])
            sl_tags_str = ','.join(sl_tags)
            stat_influxdb_formated = sl_me + " " + sl_tags_str + " " + sl_ts 
            with open(stat_logger_path, 'a+') as stat_file:
                stat_file.write( stat_influxdb_formated + os.linesep)
        except Exception, err:
            Errlog.log('PerformanceMonitor.cms_stats.log::%s'%err)
            Errlog.log(stat_influxdb_formated)            
        ########################
        # End of InfluxDB output
        ########################
        
    def sum_t(self):
        return sum([tic.t for tic in self])

    def sum_cpu_t(self):
        return sum([tic.cpu_t for tic in self])
    
    def __get_time(self):
        return time.time()
    
    def __get_cpu_time(self):
        cpu_tic = resource.getrusage(resource.RUSAGE_SELF)
        return cpu_tic.ru_utime+cpu_tic.ru_stime

class FileTimeLogger(TimeLogger):
    """
    Writes to normal studio log as well as
    $CARMTMP/logfiles/performance/$LOG_FILE.xml
    """
    def __init__(self,title=""):
        self._log_file_path = None
        self.__set_or_create_tmp_file()
        TimeLogger.__init__(self, title)

    def log(self):
        try:
            if self._log_file_path:
                old_str = ['<?xml version="1.0" encoding="ISO-8859-1" ?>\n']
                old_str.append('<entries>\n') #start tag
                old_str.extend([item for item in self.__read_string() if not
                                item.find('entries')>-1])
                old_str.extend(self.__get_tag())
                old_str.append('</entries>\n') # end tag
                self.__write_string(''.join(old_str))
        except Exception, err:
            Errlog.log('PerformanceMontior.FileTimeLogger.log::%s'%err)
        # Base class logging (studio log file)
        TimeLogger.log(self)

    def __get_tag(self):
        time_str = time.strftime('%Y-%m-%d %H:%M',time.gmtime())
        tag = ['<logentry title="%s" time="%s">\n'%(self._title,time_str)]
        tag.append(self.__get_total_tag())
        for tic in self:
            tag.append(tic.xml())
        tag.append('</logentry>\n')
        return tag

    def __get_total_tag(self):
        return '<total>\n<real>%f</real>\n<cpu>%f</cpu>\n</total>\n'%(self.sum_t(),
                                                                      self.sum_cpu_t())
    
    def __set_or_create_tmp_file(self):
        """
        Get log file name and create directory if needed
        """
        logfile = os.environ.get('LOG_FILE',None)
        if logfile is None:
            # No extra logging, act as normal time logger
            return
        log_dir = os.path.dirname(logfile)
        log_name = os.path.basename(logfile)
        new_log_dir = os.path.join(log_dir,_PERFORMANCE_LOG_DIR,
                                   _LOG_DIRS[_LOG_TIMES_TO_FILE])
        if not os.path.exists(new_log_dir):
            os.makedirs(new_log_dir)
        self._log_file_path = os.path.join(new_log_dir, log_name+'.xml')
        
    def __read_string(self):
        fd = None
        try:
            fd = open(self._log_file_path,'r')
            lines = fd.readlines() 
            fd.close()
            return lines
        except:
            if fd:
                fd.close()
        return []

    def __write_string(self, line):    
        fd = None
        try:
            fd = open(self._log_file_path,'w')
            fd.write(line)
        finally:
            if fd:
                fd.close() 

# Public access methods
def time_reset(message):
    #  message += " (%s)" % time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime())
    message += " (%s)" % time.strftime('%Y-%m-%d %H:%M',time.gmtime())

    _LOGGER.reset(message)

def time_dialog_reset():
    _LOGGER.dialog_reset()
    
def time_tic(message):
    _LOGGER.tic(message)

def time_log():
    _LOGGER.log()   

if _MODE == _LOG_TIMES_TO_FILE: 
    _LOGGER = FileTimeLogger()
else:
    _LOGGER = TimeLogger()
    

