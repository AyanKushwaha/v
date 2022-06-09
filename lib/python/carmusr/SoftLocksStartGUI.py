
from Cui import *
import Cps, Errlog, String, Variable, Cfh, Localization
import os, tempfile

def show(message, form_name = "MESSAGE_BOX", title = "Message"):
    """
    Shows a box containing the specified message and with the specified title. 
    Stops the execution of the calling python program until the user 
    presses the Ok button.
    """

    box = Cfh.Box(form_name, title)

    p = Cfh.Label(box,"PICTURE","xm_information.pm")
    p.setLoc(Cfh.CfhLoc(1,1))

    l = Cfh.Label(box,"MESSAGE",message)
    l.setLoc(Cfh.CfhLoc(1,4))

    ok = Cfh.Done(box,"OK")
    ok.setText(Localization.MSGR("Ok"))
    ok.setMnemonic(Localization.MSGR("_Ok"))

    box.build()
    box.show(1)
    box.loop()

softlocksEtab = Variable.Variable('', 1024)
try:
    CuiCrcGetDictVarAsString(gpc_info, CuiNoArea, '', 'soft_locks.table_full_name', softlocksEtab)
except:
    show('Could not obtain rave variable soft_locks.%table_full_name%, will open a new SoftLocks etab.', title='SoftLocks warning')
    
pathReport = Variable.Variable(tempfile.mktemp())
try:
    CuiCrgCreatePlainReport(gpc_info, CuiWhichArea, 'window', 'hidden/SoftLocksValidation.output', pathReport, 'ascii')
except:
    show('Report "hidden/SoftLocksValidation.output" failed. Validation turned off.', title='SoftLocks warning')

pathCarmusr = os.getenv('CARMUSR')
pathSoftLocksGui = os.path.join(pathCarmusr, 'lib/python/carmusr', 'SoftLocksGUI.py')
pathEtab = os.path.join(pathCarmusr, 'crc', 'etable', softlocksEtab.value)
strCommand = 'python %s -etab %s -report %s' %(pathSoftLocksGui, pathEtab, pathReport.value)
Cps.Spawn(strCommand, 'SoftLocks GUI', 'k')
