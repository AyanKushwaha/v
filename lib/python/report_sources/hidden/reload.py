
# [acosta:06/324@13:56] For test purposes, reload the named module(s)

"""
This 'report' is for test purposes, it reloads each module in the
argument list.
"""

# imports ================================================================{{{1
import os
from tempfile import mkstemp


# functions =============================================================={{{1

# save -------------------------------------------------------------------{{{2
def save(*args, **kwds):
    (fd, fileName) = mkstemp(suffix='.tmp',
                                  prefix='reload_',
                                  dir=os.path.expandvars('$CARMTMP'),
                                  text=True)
    outFile = os.fdopen(fd, 'w')
    outFile.write(report(args[0]))
    outFile.close()

    return fileName


# report -----------------------------------------------------------------{{{2
def report(list, re_raise=False):
    """ 
    Returns status list
    """
    reloaded_ok = []
    reloaded_nok = []
   
    for module in list:
        try:
            do_reload(module)
            reloaded_ok.append(module)
        except Exception, e:
            if re_raise:
                raise e
            reloaded_nok.append(module)

    s = ""
    if reloaded_ok:
        s += "These modules where reloaded:\n\t" + "\n\t".join(reloaded_ok) + "\n"
       
    if reloaded_nok:
        s += "These modules where not reloaded:\n\t" + "\n\t".join(reloaded_nok) + "\n"

    return s


# do_reload --------------------------------------------------------------{{{2
def do_reload(module):
    # Investigate: This code is copied, why import/reload twice??
    exec("import %s" % module)
    exec("reload(%s)" % module)
    reload(__import__(module))


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
