#

#
import time
import os
import os.path
from tempfile import mkstemp

import Crs


"""This module holds general functionality for other Meal modules.
"""

""" Flag to indicate that application is running in test environment.
Uses env var CARMSYSTEM is set etc/local_template_XXXX in the user.
"""
isTestEnv = 'TEST' in os.getenv("CARMSYSTEMNAME", "")

def getExportDir():
    """Returns the directory where meal reports are written.
    
    The actual location of the directory is retrieved from Studio resource:
      meal / ExportDirectory
    If missing the dir is created with rwxrwxrwx access rights.
    """
    # Where to store export files
    exportDir = Crs.CrsGetModuleResource("meal", Crs.CrsSearchModuleDef, "ExportDirectory")
        
    # Create directory if it does not exist
    if not os.path.exists(exportDir):
        os.makedirs(exportDir)
    
    exportDir = os.path.realpath(exportDir)
    
    return exportDir

def newMealOutputFile(typeName, sequenceNr, suffix, isTest):
    """Returns (filehdl, fileName) to file in meal standard directory.
    
    The file name is set to :
      typeName + sequenceNr + [Test] + .suffix
    Access rights to the file is set to -rw-rw-r--
    The location of the output dir is retrieved from getExportDir().
    """
    dir = getExportDir()
    fileName1stPart = "%s%s%s" % (typeName, sequenceNr, ('', 'Test')[isTest])
    for duplExt in ('','_1','_2','_3','_A','_B','_C'):
        fileName = "%s%s.%s" % (fileName1stPart, duplExt, suffix)
        filePath = os.path.join(dir, fileName)
        if os.path.exists(filePath):
            continue
        else:
            break
    else:
        raise IOError, 'File %s.%s already exists.' % (fileName1stPart,suffix)
    fhdl = open(name=filePath, mode='w', buffering=0)
    os.chmod(filePath, 0664)

    return (fhdl, filePath)