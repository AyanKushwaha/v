
# [acosta:07/005@11:50] First version

"""
This module takes care of the directory structure for the spool files.

       +--  in         Files that are going to be imported.
       |
       +--  out        Files that are going to be exported.
       |
       +--  imported   Files that have been imported.
     --+
       +--  exported   Files that have been exported.
       |
       +--  in.error   Files that failed to be imported.
       |
       +--  out.error  Files that failed to be exported.
"""

# imports ================================================================{{{1
import os, sys


# globals ================================================================{{{1
FTP_ROOT = os.path.expandvars("$CARMTMP/ftp")
mode = 0775

in_dir = "%s/in" % (FTP_ROOT)
out_dir = "%s/out" % (FTP_ROOT)
exported_dir = "%s/exported" % (FTP_ROOT)
imported_dir = "%s/imported" % (FTP_ROOT)
in_error_dir = "%s/in.error" % (FTP_ROOT)
out_error_dir = "%s/out.error" % (FTP_ROOT)


# functions =============================================================={{{1

# makedirs ---------------------------------------------------------------{{{2
def makedirs():
    """ Create spool directories if not already existing. """
    for d in [in_dir, imported_dir, in_error_dir, out_dir, exported_dir, out_error_dir]:
        if not os.path.exists(d):
            try:
                os.makedirs(d, mode)
            except Exception, e:
                print >>sys.stderr, "spool: ERROR: Failed to create directory '%s'. (%s)" % (d, e)


# outputFile -------------------------------------------------------------{{{2
def outputFile(fn, mode="r"):
    """ Returns handle to output file in spool directory 'out' 
        Optionally another path may be used
    """
    if os.path.basename(fn) != fn:
        return open(fn, mode)
    return open("%s/%s" % (out_dir, fn), mode)


# inputFile --------------------------------------------------------------{{{2
def inputFile(fn):
    """ Returns handle to input file in spool directory 'in' """
    return open("%s/%s" % (in_dir, fn), "r")


# exportDone -------------------------------------------------------------{{{2
def exportDone(fn):
    """ Move file from out-box to exported-box """
    moveFile(fn, out_dir, exported_dir)


# exportFailed -----------------------------------------------------------{{{2
def exportFailed(fn):
    """ Move file from out-box to error directory """
    moveFile(fn, out_dir, out_error_dir)


# importDone -------------------------------------------------------------{{{2
def importDone(fn):
    """ Move file from in-box to imported-box """
    moveFile(fn, in_dir, imported_dir)


# importFailed -----------------------------------------------------------{{{2
def importFailed(fn):
    """ Move file from in-box to error directory """
    moveFile(fn, in_dir, in_error_dir)


# moveFile ---------------------------------------------------------------{{{2
def moveFile(fn, fromdir, todir):
    """ Move file 'fn' from directory 'fromdir' to directory 'todir' """
    if os.path.basename(fn) != fn:
        os.rename(fn, "%s/%s" % (todir, os.path.basename(fn)))
    else:
        os.rename("%s/%s" % (fromdir, fn), "%s/%s" % (todir, fn))


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
