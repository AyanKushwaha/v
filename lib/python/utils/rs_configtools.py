

"""
Module with help functions to get configured data for DIG channels,
report servers etc.
If the config API had been better, then this module would not have been
needed... The config API sucks!
The idea is to package all configuration attributes (hostnames, port numbers,
service names, start commands) etc. together with the channel/report server.
"""

import os
import warnings
from carmensystems.common.Config import Config

warnings.simplefilter('ignore', UserWarning)


class CMDIF:
    """Common interface for channels and report servers (in this module)."""
    def start(self, callback):
        """Call callback with a list of command and arguments
        needed to start."""
        return callback(*self.get_cmd('start'))

    def stop(self, callback):
        """Call callback with a list of command and arguments
        needed to stop."""
        return callback(*self.get_cmd('stop'))

    def get_cmd(self, cmd):
        """Template method."""
        raise NotImplementedError('get_cmd() not implemented')


class DIGChannel(CMDIF):
    """Represents a DIG Channel."""
    def __init__(self, channel):
        self.channel = channel

    def get_cmd(self, cmd):
        """Template method for starting DIG channel."""
        if cmd == 'start':
            return [os.path.expandvars('$CARMSYS/bin/digmain'),
                    '-c', self.channel,
                    os.path.expandvars('$CARMUSR/etc/config.xml')]
        else:
            raise NotImplementedError("Command '%s' not supported.")

    def __str__(self):
        return '\n'.join((
            "---",
            "channel name : %s" % self.channel,
        ))


class RSBase(CMDIF):
    """Common functionality for workers and portal."""
    rstype = 'unknown'
    def __init__(self, procname):
        self.procname = procname
        self.hostname = None
        self.nodename = None
    

class Portal(RSBase):
    """Represents a Report Server Portal."""
    rstype = 'portal'
    def __init__(self, procname):
        RSBase.__init__(self, procname)
        self.port = None

    def __str__(self):
        return " - %-20.20s: %s@%s (%s)" % (self.rstype, self.procname,
                self.nodename, self.url)

    @property
    def url(self):
        return "http://%s:%s/RPC2" % (self.hostname, self.port)

    def set_node(self, nodename, hostname, port):
        self.nodename = nodename
        self.hostname = hostname
        self.port = port

    def get_cmd(self, cmd):
        """Template method for starting a portal."""
        return [os.path.expandvars('$CARMSYS/etc/scripts/portal'), cmd,
                self.nodename, self.procname]


class ReportWorker(RSBase):
    """Represents a Report Server Report Worker."""
    rstype = 'reportworker'
    def __str__(self):
        return " - %-20.20s: %s@%s (%s)" % (self.rstype, self.procname,
                self.nodename, self.hostname)

    def set_node(self, nodename, hostname, *a):
        self.nodename = nodename
        self.hostname = hostname

    def get_cmd(self, cmd):
        return [os.path.expandvars('$CARMSYS/etc/scripts/reportworkerStudio'), cmd,
                self.nodename, self.procname]


class ReportService(dict):
    """Portal and worker(s) for a Report Server."""
    def __init__(self, servicename):
        dict.__init__(self)
        # The portal service name will identify the service
        self.servicename = servicename
        self.portal = None
        self.workers = []

    def __str__(self):
        return '---\nReport Server:\n' + '\n'.join(
                [str(x) for x in [self.portal] + self.workers])
    
    def set_portal(self, procname):
        """Set the portal object."""
        if self.portal is not None:
            warnings.warn("%s already has a portal (%s)." % (
                self.servicename, self.portal.procname))
        self.portal = Portal(procname)
        self[procname] = self.portal

    def add_worker(self, procname):
        """Add report worker."""
        worker = ReportWorker(procname)
        self.workers.append(worker)
        self[procname] = worker

    def get_workers(self, worker=None):
        """Get process names of all workers."""
        return [x for x in self.workers 
                if (worker is None or x.procname == worker)]

    def start_worker(self, callback, worker=None):
        """Start named worker (or all workers)."""
        for w in self.get_workers(worker):
            w.start(callback)

    def stop_worker(self, callback, worker=None):
        """Stop named worker (or all workers)."""
        for w in self.get_workers(worker):
            w.stop(callback)

    def start_portal(self, callback):
        """Start the portal."""
        self.portal.start(callback)

    def stop_portal(self, callback):
        """Stop the portal."""
        self.portal.start(callback)

    def processes(self):
        """Return processnames for all sub objects (portal and workers)."""
        return [self[x].procname for x in self]


class ConfigHandler(object):
    """Handle the CMS XML configuration, which is a mess."""
    def __init__(self, baseconfig=None):
        self.set_config(baseconfig)

    def channel(self, channel_name):
        """Return DIGChannel() object for 'channel_name'."""
        return self.channels[channel_name]

    @property
    def channels(self):
        """Dictionary of DIGChannel objects, indexed on process name."""
        if self.__channels is None:
            self.__channels = self.get_channel_mapping()
        return self.__channels

    @property
    def config(self):
        """Get current Config() object (cached)."""
        return self.configparser.config

    @property
    def configparser(self):
        if self.__config is None:
            if self.baseconfig is None:
                a = ()
            else:
                a = (self.baseconfig,)
            self.__config = Config(*a)
        return self.__config

    @property
    def reportservers(self):
        if self.__reportservers is None:
            self.__reportservers = self.get_rs_mapping()
        return self.__reportservers

    def reportserver(self, rsname):
        """Return ReportService() object for 'channel_name'."""
        return self.reportservers[rsname]

    def reset(self):
        """Reset and force re-read of configuration."""
        self.__config = None
        self.__channels = None
        self.__reportservers = None

    def set_config(self, config):
        """Reset and use configuration file given as argument."""
        self.reset()
        self.baseconfig = config

    def get_channel_mapping(self):
        """Return dictionary of DIGChannel objects, indexed on process name"""
        digchannels = {}
        for system in self.config.getElementsByTagName('system'):
            for dig in system.getElementsByTagName('dig'):
                for channel in dig.getElementsByTagName('channel'):
                    channel_name = channel.getAttribute('name')
                    digchannels[channel_name] = DIGChannel(channel_name)
        if not digchannels:
            warnings.warn("No DIG channels found.")
        return digchannels

    def get_rs_mapping(self):
        """Return dictionary of ReportService objects, indexed on process
        name"""
        reportservers = {}
        dignodes = {}
        portals = set()
        process_group_map = {}
        for system in self.config.getElementsByTagName('system'):
            for program in system.getElementsByTagName('program'):
                program_name = program.getAttribute('name')
                for process_groups in program.getElementsByTagName('process_groups'):
                    for process_group in process_groups.getElementsByTagName('process_group'):
                        process_group_name = process_group.getAttribute('name')
                        for start in process_group.getElementsByTagName('start'):
                            process_group_map.setdefault(process_group_name, []).append(nodval(start))
                for process in program.getElementsByTagName('process'):
                    process_name = process.getAttribute('name')
                    rs = None
                    if program_name == 'reportserver':
                        for service in process.getElementsByTagName('service'):
                            service_name = service.getAttribute('name')
                            if service_name in reportservers:
                                rs = reportservers[service_name]
                            else:
                                rs = ReportService(service_name)
                                reportservers[service_name] = rs
                            rs.set_portal(process_name)
                            portals.add(process_name)
                        for portal_service in process.getElementsByTagName('portal_service'):
                            service_name = nodval(portal_service)
                            if service_name in reportservers:
                                rs = reportservers[service_name]
                            else:
                                rs = ReportService(service_name)
                                reportservers[service_name] = rs
                            rs.add_worker(process_name)
            for hosts in system.getElementsByTagName('hosts'):
                for host in hosts.getElementsByTagName('host'):
                    host_name = host.getAttribute('name')
                    # Apply some magic (expandvars). 
                    # - WHY can't the XML representation of the Config() object
                    #   contain expanded attributes/values???? 
                    # - WHY can't Config API support XPath (which is a
                    #   standard)???
                    host_hostname = self.configparser.expandvars(host.getAttribute('hostname'))
                    host_portbase = self.configparser.expandvars(host.getAttribute('portbase'))
                    # Desmond will run on portbase, the order of a *portal*
                    # will decide portnumber, only *services* will step portno.
                    # This logic comes from studying ServiceConfig.
                    portno = int(host_portbase)
                    for start in host.getElementsByTagName('start'):
                        procname = nodval(start)
                        if procname in portals:
                            portno += 1
                            port = portno
                        else:
                            port = None
                        if procname in process_group_map:
                            for p in process_group_map[procname]:
                                dignodes[p] = host_name, host_hostname, port
                        else:
                            dignodes[procname] = host_name, host_hostname, port
            for rs in reportservers.itervalues():
                for proc in rs:
                    try:
                        node, hostname, port = dignodes[proc]
                        rs[proc].set_node(node, hostname, port)
                    except:
                        warnings.warn("No host info for process (%s)." % proc)
        if not reportservers:
            warnings.warn("No report servers found.")
        return reportservers


config_handler = ConfigHandler()


# private functions ======================================================{{{1
def bit():
    """Built-in Test."""
    def print_cmd(*a):
        print a
    print channels()
    print channel('salary_manual')
    print reportservers()
    print reportserver('portal_publish')
    reportserver('portal_publish').start_worker(print_cmd, 'SAS_RS_WORKER_PUBLISH1')


def nodval(n):
    """Utility - return text value of node."""
    return ''.join([x.nodeValue for x in n.childNodes])


# public functions ======================================================={{{1
def channel(channel_name):
    """Return DIGChannel() object for 'channel_name'."""
    return config_handler.channel(channel_name)


def channels():
    """Return list of DIG channel names."""
    return sorted(config_handler.channels)


def reportserver(report_server_name):
    """Return ReportService() object for 'channel_name'."""
    return config_handler.reportserver(report_server_name)


def reportservers():
    """Return list of Portal service names."""
    return sorted(config_handler.reportservers)


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    bit()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
