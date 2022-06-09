'''
Created on Mar 22, 2010

@author: rickard
'''

import os
import Cui
import subprocess

_FILES_TO_PURGE = None
_FILE_COUNT = 0

def displayHtml(html, title="Report"):
    displayHtmlFile(_getTempFile(html), title)
    
def displayHtmlFile(htmlFile, title="Report"):
    # The embedded browser seems kind a shaky and only works sometimes, lets
    # use the external instead.
    #Cui.CuiStartEmbeddedBrowser(htmlFile, "ABS", "", title)    
    Cui.CuiStartExternalBrowser(htmlFile, "ABS")
    
def displayXml(xml, transform, title="XML"):
    displayXmlFile(_getTempFile(xml), transform, title)
    
def displayXmlFile(xml, transform, title="XML"):
    (stdout, stderr) = subprocess.Popen("xsltproc --nowrite '%s' '%s'" % (transform, xml), stdout=subprocess.PIPE, shell=True).communicate()
    displayHtml(stdout, title)

def _getTempFile(contents):
    global _FILES_TO_PURGE
    global _FILE_COUNT
    if _FILES_TO_PURGE == None:
        _FILES_TO_PURGE = []
        import atexit
        atexit.register(_purge_files)
    _FILE_COUNT = _FILE_COUNT + 1
    fileName = os.path.expandvars("/tmp/htmlreport.$USER.%d.html" % _FILE_COUNT)
    _FILES_TO_PURGE.append(fileName)
    f = file(fileName, "w")
    print >>f, contents
    f.close()
    return fileName
    
def _purge_files():
    global _FILES_TO_PURGE
    if not _FILES_TO_PURGE: return
    for f in _FILES_TO_PURGE:
        try:
            os.unlink(f)
            print "Deleted file",f
        except:
            pass