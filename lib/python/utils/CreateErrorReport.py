#
# A python script which creates an error report template
#
# Copied from Stefan Hammar's NTH-packages. Some function
# has been copied from separate modules into this file
#

text_template = """
----------------------------------------------------------
Summary:

<SP: Please supply a brief summary of the problem>

----------------------------------------------------------
Step-by-Step:

<SP: Please specify step by step how to reproduce the defect>

----------------------------------------------------------
Expected behaviour:

<SP: Please specify how you believe the system should have
behaved in the above situation.>

----------------------------------------------------------
Broken behaviour?

Was the behaviour correct in any previous release? <Yes, No, Don't Know>

----------------------------------------------------------
"""
def nth_xddts_do():

    import sys
    import os

    from Variable import Variable
    import Cui
    import Crs
    import Csl
    import tempfile
    from __main__ import exception as CarmenError

    def call(cmd, input=""):
        def _call_new(cmd, input=""):
            """
            >= 2.4 version
            """
            import subprocess
            p = subprocess.Popen(cmd,shell=True,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            ret = p.communicate(input)
            return (ret[0], ret[1], p.returncode)

        def _call_old(cmd, input=""):
            """
            <= 2.2 version.
            WARNING - Something is wrong here. Only a limited number
            of calls could be executed. ?!?
            """
            import popen2
            p = popen2.Popen3(cmd, 1, 0)
            if input:
                p.tochild.write(input)
                p.tochild.close()
            ret = p.wait()
            return (p.fromchild.read(), p.childerr.read(), ret)

        """ 
        'call(cmd)' will execute 'cmd' using /bin/sh. 
        The result is a tuple with the result
        (stdout), the error messages (stderr) and the return 
        value.
        'input' may be used as (stdin).
        """
        try:
            import subprocess #@UnusedImport
            return _call_new(cmd, input="")
        except ImportError:
            return _call_old(cmd, input="")
        
    
    def get_ss_client_info():
        cp = os.getenv("_CARMCLIENTINFO") or os.getenv("CLIENTINFO")
        spl = cp.split(";")
        if len(spl) < 6:
            return "Client:\n  no info available"
        
        if ("=" in spl[0]): # new style
            return "\n".join(["  Client:"] +
                             ["    %s: %s" % ((a + "." * 10)[:13], b) for a,b in
                             [s.split("=") for s in spl]])       

        # old style
        
        return """  Client:
    package......: %s
    os...........: %s 
    os version...: %s
    os arch......: %s
    java version.: %s""" % tuple(spl[:5])


    def get_ss_url():
        ssu = os.getenv("_CARMSESSIONSERVERURL")
        if ssu:
            return ssu
        if not ssu:
            cp = os.getenv("CLIENT_PATH")  # Old Session Server 
            if cp: 
                return "https://%s:8443" % cp.split("@")[1].split(".")[0].split(":")[0]
            else:
                return None  # No Session Server

            
    def get_ss_info():
        """
        Get info from the release_info file on the session server.
        A tuple is returned: (SS-Version, auth method, ARCH)
        """
        import subprocess  # not in 2.2
 
        ssu = get_ss_url()

        if not ssu: 
            return "No Session Server"
                
        cmd = "wget --no-check-certificate --proxy=off -O - -q %s/carmfileservlet/SessionServer/data/config/release_info" % (ssu,)
        p = subprocess.Popen(cmd, shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        so, _ = p.communicate()
        if not so: 
            return ("Unknown version", None, None)
        
        res = [s.split(":") for s in so.split("\n")]

        # Version
        v = "%s.%s" % (res[1][1].strip(), res[2][1].strip())
        if res[2][1].strip() == "current":
            v += ", built %s" % (":".join(res[3][1:]).strip()) 

        if len(res) > 5:  # Since 20/5 2009
            # Arch
            ar = res[9][1].strip()
            # Auth
            au = res[10][1].strip()
        else:
            ar = au = None

        return (v, ar, au)    


    def get_ref_plans():

        if nth_get_major_release_number() < 14:    
            return None, None

        import carmensystems.rave.api as r

        rp1 = None
        rp2 = None
    
        try:
            c_bag = r.context("plan_1_sp_crrs").bag()
            for chain_bag in c_bag.chain_set():
                rp1 = "/".join(chain_bag.reference_plan_name().split("/")[-5:-1])
                break
            c_bag = r.context("plan_2_sp_crrs").bag()
            for chain_bag in c_bag.chain_set():
                rp2 = "/".join(chain_bag.reference_plan_name().split("/")[-5:-1])
                break
        except r.UsageError: 
            return None, None # No rule set

        return rp1, rp2
    def show_file(title, filepath):
        """
        Displays a file in a nice Studio popup window.
        @param title : Text to show in the window frame
        @type  title : str
        @param text  : Text to display in the window.
        @type  text  : str
        """
        csl = Csl.Csl()
        csl.evalExpr('csl_show_file("%s","%s")' % (title, filepath))

    def show_text(title, text):
        """
        Displays a text in a nice Studio popup window.
        @param title : Text to show in the window frame
        @type  title : str
        @param text  : Text to display in the window.
        @type  text  : str
        """

        fn = tempfile.mktemp()
        f = open(fn, "w")
        f.write(text)
        f.close()
        show_file(title, fn)
        os.unlink(fn)
    def nth_get_major_release_number(release_as_string=None):
        """
        Get a release number given a release string.
        Get current release if None given as argument.

        @param : release_as_string (seldom specified.)
        @type s: Any data type. Converted to string id needed.
        @return: The major release number.
                 Master       : 99
                 TRACKING_1*  : 13
                 Other        : Use the UtilVersion number.

        @rtype: int
        """
        if release_as_string != None:
            v = str(release_as_string)
        else:
            v = os.path.expandvars("$CarmReleaseMajor")

        if v == "master":
            i = 99
        elif v[:10] == "TRACKING_1":
            i = 13
        elif v.isdigit():
            i = int(v)
        elif release_as_string == None:
            rinfo = dict([row[:-1].split("=")
                          for row
                          in open(os.path.expandvars("$CARMSYS/data/config/release_info")).readlines()
                          if "=" in row])
            rs = rinfo.get("UtilVersion", 0)
            if rs == "master":
             i = 99
            elif rs == "CMS2" or v[:4] == "CMS2":
             i = 17.5
	    elif rs == "20d":
 	     i = 20
            else:
             i = int(rs)
        else:
            i = 0

        return i


    sep = "---------------------------------------------------------"

    content = [sep, "Defect Submission", sep, "",]

    # System definition

    cs,_,_ = call('cd $CARMSYS;echo `/bin/pwd`')
    content.append("CARMSYS=%s" % (cs[:-1]))

    content.append("CARMUSR=%s" % os.getenv("CARMUSR"))
    content.append("CARMTMP=%s" % os.getenv("CARMTMP"))

    consider_also=["CCROLE"]
    skip=["CARMSYS","CARMUSR","CARMTMP","CARMSITE",
          "CARMARCH","CARMSGE","CARMSTD","CARM_EDITOR",
          "CARMCCSITE","CARMCCSUBSITE"]
    l = [k for k in os.environ.keys() if  k in consider_also or
         (k[:4] == "CARM" and k not in skip and k[:9] != "CARMUTIL_")]
    l.sort()
    for item in l:
        content.append("%s=%s" % (item, os.environ[item]))
    content.append("")

    # Plan names

    buf = Variable("")
    Cui.CuiGetSubPlanPath(Cui.gpc_info, buf)
    plan = buf.value
    if plan:
        if nth_get_major_release_number() > 13: # rave bags used
            import carmensystems.rave.api as r
            try:
                for c_bag in r.context("lp_activity").bag().chain_set():
                    sol = c_bag.solution_name()
                    plan += "/%s" % sol
                    break
            except r.UsageError:
                pass # Probably no loaded rule set
    else:    
        Cui.CuiGetLocalPlanPath(Cui.gpc_info, buf)
        plan = buf.value  
    if not plan:
        plan = "<No plan loaded>"
    content.append("PLAN...: %s" % plan)

    env = Cui.CuiGetEnvPlanNames(Cui.gpc_info)
    if env and env[0]:
        content.append("ENV_PL.: %s" % (env[0],))

    rp1, rp2 = get_ref_plans()

    if rp1:
        content.append("REF PL1: %s" % rp1)
        if rp2:
            content.append("REF PL2: %s" % rp2)

    # Database info
    
    bba = Variable("")
    bbb = Variable("")
    bbc = Variable(0)
    try:
        Cui.CuiGetLocalPlanDBPath(Cui.gpc_info, bba, bbb, bbc)
        content.append("DB\n Conn..: %s\n Schema: %s\n Branch: %s" % (bba.value,
                                                                      bbb.value,
                                                                      bbc.value))
        content.append("CRS (config.legSetAcceleration): %s" % 
                       Crs.CrsGetModuleResource("config",
                                                Crs.CrsSearchModuleDef,
                                                "legSetAcceleration"))
    except (AttributeError, CarmenError):  # Old version or no DB.
        pass
    
    content.append("")
    
    # Misc environments
    content.append("LOGFILE: %s" % os.getenv("LOG_FILE"))
    content.append("HOST...: %s" % os.getenv("HOST"))
    a = os.getenv("ARCH")
    content.append("ARCH...: %s" % a)
    rh = os.path.exists("/etc/redhat-release")
    su = os.path.exists("/etc/SuSE-release")
    
    if rh:
       content.append("OS.....: %s" % call("cat /etc/redhat-release")[0][:-1])

    if su:
       res = call("cat /etc/SuSE-release")[0].split()     
       content.append("OS.....: SuSE %s.%s" % (res[-4], res[-1]))

    if su or rh:
       rinfo = dict([row[:-1].split("=")
                     for row
                     in open(os.path.expandvars("$CARMSYS/data/config/release_info")).readlines()
                     if "=" in row])

       util_version = rinfo.get("UtilVersion", rinfo["Major"])
       if (not util_version.isdigit()) or int(util_version) > 12: 
          content.append("UTILrpm: %s" % call("rpm -q carmutil%s" % util_version)[0].split("\n")[0]) 

    user = os.getenv("LOGNAME")
    content.append("USER...: %s" % user)
    content.append("")

    if os.getenv("MACRO_SCRIPT"):
        content.append("")   
        content.append("MACRO_SCRIPT=%s" % os.getenv("MACRO_SCRIPT"))

    # PYBATCH stuff

    pyb = os.getenv("PYBATCHSYS")
    if pyb:
        content.append("")   
        content.append("PYBATCHSYS=%s" % pyb)
        content.append("PYBATCHTMP=%s" % (os.getenv("PYBATCHTMP") or "n.a",))
        content.append("PYBATCHLIB=%s" % (os.getenv("PYBATCHLIB") or "n.a",))

    # Mercurial Tag
    # Replaced with Git Tag
    #tag,_,_ = call('hg -R $CARMUSR id -b -t -n')
     tag,_ = call("git log -1 HEAD^  --pretty=format:\"%h $ad %s\"  | grep -oP   '^[^:]+'")
    if tag:
        content.append("")   
        content.append("TAG:\n    %s" %tag )
 
    # Get the rest from the specified file
    
    # for row in text_template:
    content.append(text_template)

    # Show the result

    show_text("Defect Submission", "\n".join(content)) 

if __name__ == '__main__':
    nth_xddts_do()
# end of file
