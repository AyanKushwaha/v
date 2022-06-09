import os
import os.path
import sys
import re
import subprocess
from utils.ServiceConfig import ServiceConfig
from carmensystems.common.Config import Config

def build(clean=True):
    """
    Rebuild the Crew Portal WAR and configuration files to $CARMTMP/crewportal.
    """
    if not isinstance(clean, bool):
        raise Exception("Illegal argument")

    _mk_deploy_env(clean)
    config = Config()
    path = os.environ['PATH']
    os.environ['JAVA_HOME'] = config.getProperty("bids/java_home")[1]
    os.environ['MAVEN_HOME'] = config.getProperty("bids/maven_home")[1] + "/bin"
    os.environ['PATH'] += os.pathsep + os.environ['MAVEN_HOME']
    _maven()
    os.environ['PATH'] = path
    os.unsetenv("MAVEN_HOME")
    os.unsetenv("JAVA_HOME")

def deploy():
    """
    Deploy $CARMTMP/crewportal in the JBoss nodes.
    """

    config = Config()
    app_home = config.getProperty("bids/app_home")[1]

    main_nodes = []
    app_nodes = []
    cp_main_nodes = config.getProperties("cluster_hosts/cp_main_node")
    for main_node in cp_main_nodes:
        main_nodes.append(main_node[1])
    cp_app_nodes = config.getProperties("cluster_hosts/cp_app_node")
    for app_node in cp_app_nodes:
        app_nodes.append(app_node[1])

    print "Deploy on main nodes: {%s}, app nodes: {%s}"%(",".join(main_nodes), ",".join(app_nodes))
    print "app_home is: ", app_home

    for node in main_nodes:
        if os.getenv("CARMSYSTEMNAME") == "CMSDEV":
            os.system("ssh -t %s sudo rm -rf /usr/java/jboss-eap/standalone/deployments /usr/java/jboss-eap/standalone/crewportal" % (str(node)))
        _remote_cp(node,
            os.path.join(app_home, "deploy", "*"),
            config.getProperty("bids/jboss_home_deploy")[1])
        _remote_cp(node,
                   os.path.join(app_home, "conf", "*"),
                   config.getProperty("bids/jboss_home_conf")[1])
    for node in app_nodes:
        _remote_cp(node,
                   os.path.join(app_home, "deploy", "*"),
                   config.getProperty("bids/jboss_home_deploy")[1])
        _remote_cp(node,
                   os.path.join(app_home, "conf.app", "*"),
                   config.getProperty("bids/jboss_home_conf")[1])


def buildsystem():
    """
    Alias for build
    """
    return build()

def deploysystem():
    """
    Alias for deploy
    """
    return deploy()

def _mk_deploy_env(clean=True):
    """
    Generate deploy_env.properties which is used by build.xml to generate links to the correct report servers etc.
    Constructed to merging:
      * The shell environment
      * <service name>=<service url> for each sysmond service
      * <element key>=<value> for each xmlconfig value where <element key> has '/' replaced with '.'
    """
    file = os.path.expandvars("$CARMTMP/compile/deploy_env.properties")
    if not clean and os.path.isfile(file):
        # TODO: Check time stamp
        return

    print "Generating %s..."%file
    if not os.path.isdir(os.path.dirname(file)):
        os.makedirs(os.path.dirname(file))

    fd = open(file, "w")
    for (x, y) in sorted(_get_build_env().items()):
        fd.write("%s=%s\n"%(x,y))
    fd.close()

def _get_build_env():
    environment = {}

    try:
        environment["CARMUSR_VERSION"] = _check_output(["/bin/sh",
                                                         "-c" ,
                                                        "git log -1 HEAD^ --pretty=format:\"%h $ad %s\" | grep -oP   '^[^:]+'"])
    except Exception, e:
        print >>sys.stderr, "WARNING: Could not identify CARMUSR version: %s"%e

    # Include only a limited set of environment variables to avoid unexpected '@' characters in variables like $PS1
    environment.update({x:y for x,y in os.environ.items() if x.startswith("CARM")})

    config = ServiceConfig()
    for (service, process, host, url) in config.getServices():
        environment[service] = url
        environment["%s.base"%service] = url.replace("/RPC2", "")

    for (path, value) in config.getProperties("*"):
        key = re.sub(r"\[\d*\]", "", path).replace("/carmen", "carmen").replace("/", ".")
        if not environment.has_key(key):
            environment[key] = value

    return environment

def _maven():
    config = Config()
    bids_home = config.getProperty("bids/bids_user")[1]
    print "### this the bid_home ", bids_home
    print "### The subprocess call is:  ", " ".join(["mvn", "clean", "install", "-P", "cmsshell", "-f", bids_home + "/pom.xml" #, "-X"
                                                      ])
    ret = subprocess.check_call(["mvn", "clean", "install", "-P", "cmsshell", "-f", bids_home + "/pom.xml" #, "-X"
                                 ])

def _remote_cp(host, source, dest):
    cmd = ["ssh", host, "/bin/mkdir" , "-p", dest]
    print " ".join(cmd)
    subprocess.check_call(cmd)
    cmd = ["ssh", host, "/bin/cp", "-a", source, dest]
    print " ".join(cmd)
    subprocess.check_call(cmd)

### check_output copied from subprocess.py in Python-2.7.3
def _check_output(*popenargs, **kwargs):
    r"""Run command with arguments and return its output as a byte string.

    If the exit code was non-zero it raises a CalledProcessError.  The
    CalledProcessError object will have the return code in the returncode
    attribute and output in the output attribute.

    The arguments are the same as for the Popen constructor.  Example:

    >>> check_output(["ls", "-l", "/dev/null"])
    'crw-rw-rw- 1 root root 1, 3 Oct 18  2007 /dev/null\n'

    The stdout argument is not allowed as it is used internally.
    To capture standard error in the result, use stderr=STDOUT.

    >>> check_output(["/bin/sh", "-c",
    ...               "ls -l non_existent_file ; exit 0"],
    ...              stderr=STDOUT)
    'ls: non_existent_file: No such file or directory\n'
    """
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        raise subprocess.CalledProcessError(retcode, cmd)
    return output
