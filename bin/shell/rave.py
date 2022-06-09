import os,shutil,sys

def check(ruleset="all"):
    """ Checks syntax for all rulesets """
    compile(ruleset,skipcompilation=True)

def cleanall():
    """ Removes all compiled rulesets """

    carmusr_path = os.environ['CARMUSR']

    carmtmps = ['current_carmtmp_cct']

    dirs_to_clean = [os.path.join(os.path.join(carmusr_path, x), "compile") for x in carmtmps]
    dirs_to_clean += [os.path.join(os.path.join(carmusr_path, x), "crc") for x in carmtmps]

    clean = True
    for dir in dirs_to_clean:
        if os.path.isdir(dir):
            clean = False
            print "Cleaning %s ..." % dir
            shutil.rmtree(dir)

    if clean:
        print "Nothing to clean"

def compile(ruleset="all", explorer=False, delivery=False, skipcompilation=False, optimize=None, profiler=False, local=False, suffix=""):
    """ Compiles a number of rulesets
        @param explorer - set to true in to activate debug possibilities in Rave Explorer and Eclipse
        @param delivery -
        @param skipcompilation -
        @param optimize -
        @param profiler -
        @param local -
    
    """

    if delivery:
        compile(ruleset, True, False, None, False, local, "explorer")
        compile(ruleset, False, False, None, False, local)
        return

    if optimize is None:
        optimize = not explorer
    if ruleset == "all":
        ruleset = "cct"
    rulesets = set()
    errors = []
    for rs in ruleset.split(","):
        rs = rs.lower()
        if rs in ("cct","tracking"):
            rulesets.add("Tracking")
        else:
            print >>sys.stderr, "Warning: Unknown ruleset '%s'" % rs
    for rs in rulesets:
        ret_val = _submitCompilation(rs,explorer,skipcompilation,optimize,profiler,local,suffix)

        if ret_val != 0:
            errors.append(rs)

    if errors:
        print 40 * "*"
        print " Rave compilation failed!"
        print " Could not compile rulesets:"
        for e in errors:
            print "  - %s" % (e)
        print 40 * "*"
    else:
        print "Rave compilation completed successfully"

    return len(errors)
        
def _submitCompilation(ruleset,explorer,skipcompilation,optimize,profiler,local,suffix):
    sk_app="Tracking"
     
    rave_dialect="gpc"

    if local:
        os.environ['COMPILE_SERVER_x86_64_linux'] = os.environ['HOSTNAME']
        os.environ['COMPILE_SERVER_i386_linux'] = os.environ['HOSTNAME']
        os.environ['_AUTOTEST__LOCAL_COMPILE_'] = '1'
        
    print "Building the %s ruleset for product %s" % (ruleset,sk_app)
    # The global option "-enable group_redefine" enables proper redefinition of groups.
    # This will be the default way in a future release, at which point the option can
    # be removed from this call. The option is only available in R26, so exclude it from
    # Manpower until we have R26 for Manpower. More info in Jeppesen's R26 release notes.
    enable = '' if ruleset == "Manpower" else '-enable group_redefine'
    commands = ". $CARMUSR/etc/scripts/shellfunctions.sh && setCarmvars '%(skapp)s' && echo \"Carmsys is $CARMSYS\" && $CARMSYS/bin/crc_compile %(enable)s %(skipcompilation)s %(optimize)s %(suffix)s %(explorer)s %(profiler)s %(dialect)s $CARMUSR/crc/source/%(ruleset)s"% {
      'enable':enable,
      'optimize':optimize and '-optimize' or '',
      'suffix':suffix and '-suffix %s' % suffix or '',
      'explorer':explorer and '-explorer' or '',
      'profiler':profiler and '-profiler' or '',
      'skipcompilation':skipcompilation and '-skipcompilation' or '',
      'dialect':rave_dialect,
      'ruleset':ruleset,
      'skapp':sk_app,
    }
    return os.system("sh -c '%s'" % commands)
    
