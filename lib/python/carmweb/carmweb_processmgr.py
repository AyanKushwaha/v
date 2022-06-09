import utils
import sge
import os,sys
import re
import subprocess
JOB_PREFIX = "TwS_%x_" % (hash(os.path.expandvars("$HOST/$USER")) & 0xFFFFFFFF)
submitted_re = re.compile(r'Your job ([0-9]+) ')

__C = None
def _C():
    from carmensystems.common import ServiceConfig
    global __C
    if __C == None: __C = ServiceConfig.ServiceConfig()
    return __C
    
@utils.xmlrpc
def listRunningProcesses(processType=None, session=None):
    """
    Returns the currently running processes of a certain type.
    """
    pfx = JOB_PREFIX
    if processType:
        pfx += processType
    l = sge.list_jobs(pfx)
    for j in l:
        j.name = j.name[len(pfx):]
    if session != None:
        l = [x for x in l if x.context.get('tws_session','')==str(session)]
        
    return l

@utils.xmlrpc
def startProcess(name, **args):
    """
    Spawns a new process using the SGE.
    @param name: The process configuration name, as defined in the XML configuration.
    @param args: Command-line arguments. Substituted in the command-line as configured.  
    """
    proc,_ = _C().getProperty("carmweb_processes/%s" % name)
    _, cmdline = _C().getProperty("%s/start_cmd" % proc)
    _, reqs = _C().getProperty("%s/sge_requirements" % proc)
    reqs = reqs.split(" ")
    if "%" in cmdline:
        cmdline = _C().expandvars(cmdline)
    env = {'CARMUSR' : os.environ["CARMUSR"],
           'LOGDIR' : os.path.join(os.environ["LOGDIR"],"carmweb"),
           'CALLBACK_URI' : os.environ["CARMWEB_URI"],
           'CARMWEB' : os.environ.get("CARMWEB","CARMWEB"),
           'PROCESS_TYPE' : name,
           'COMMAND' : cmdline}
    print env
    startScript = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'sge_child.sh')
    print "will start",startScript
    program,_ = subprocess.Popen("which qsub", shell=True, stdout=subprocess.PIPE).communicate()
    if not program:
        raise Exception,"SGE qsub program not found"
    env = sum([['-v','%s=%s' % (x,env[x])] for x in env], [])
    args=[program.strip(),
          '-N', '%s%s' % (JOB_PREFIX, name),
          '-ac', 'tws_callback="%s"' % os.environ["CARMWEB_URI"]
          ]
    if args: args += reqs
    if env: args += env
    args += ['-notify','-b', 'y', startScript]
    print args
    p = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout,stderr = p.communicate()
    if p.returncode != 0:
        raise Exception,"SGE returned error: %s" % stderr
    m = submitted_re.search(stdout)
    if m:
        print "Job number: %d" % int(m.group(1))
        return int(m.group(1))
    return -1