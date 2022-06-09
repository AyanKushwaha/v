import sys
import os
if len(sys.argv) < 2:
    print >>sys.stderr, "Do not call this script directly"
    sys.exit(1)
if len(sys.argv) < 3:
    sys.argv.append("help")
sys.argv = sys.argv[1:]

def do_help(mod,brief=False):
    if not brief: print >>sys.stderr, "%s subcommands:" % sys.argv[0]
    for m in dir(mod):
        v = m
        if m == '_list_':
            v = 'list'
        if v[:1] != '_':
            dg = getattr(mod, m)
            if type(dg) is type(do_help):
                if brief:
                    print v
                else:
                    print >>sys.stderr, "  %s:" % v
                    if dg.__doc__:
                        print >>sys.stderr,"    %s" %dg.__doc__.replace('\n','\n    ')
                    else:
                        print >>sys.stderr,"    No help provided"

try:
    mod = __import__(sys.argv[0])
    if sys.argv[1] in ('-h', '--help'): sys.argv[1] = 'help'
    if sys.argv[1] == 'list': sys.argv[1] = '_list_'
    if not hasattr(mod, sys.argv[1]):
        if sys.argv[1].lower() == 'help':
            do_help(mod)
        elif sys.argv[1].lower() == '--briefhelp':
            do_help(mod,True)
        else:
            print >>sys.stderr, "Unrecognized subcommand \'%s\'" % (sys.argv[1])
            sys.exit(1)
    else:
        func = getattr(mod, sys.argv[1])
        posargs = []
        kwargs = {}
        for arg in sys.argv[2:]:
            if arg[:2] == '--':
                kv = arg[2:].split("=",1)
                if len(kv) != 2:
                    print >>sys.stderr, "'=' must follow '--'-option"
                    sys.exit(1)
                k,v = kv
                if v in ("True","true"): v = True
                elif v in ("False","false"): v = False
                elif v.isdigit(): v = int(v)
                kwargs[k] = v
            else:
                posargs.append(arg)
        ret = func(*posargs, **kwargs)
        if ret: sys.exit(ret)
except ImportError,e:
    if str(e) == "No module named %s" % sys.argv[0]:
        print >>sys.stderr, "Unrecognized command '%s'" % sys.argv[0]
    else:
        import traceback
        traceback.print_exc()
    sys.exit(1)
