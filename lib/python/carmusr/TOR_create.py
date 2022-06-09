#

#
"""
Creates a TOR-table based on the content of the window
"""

#######################################################
#
# TOR_create
#
# -----------------------------------------------------
#
#    This script is used from the CRR general menu to
#    generate a TOR etable. For the actual generation
#    the report hidden/TOR_etable.output is used
#
# File structure:
#######################################################

import os
import os.path
import tempfile

import Errlog
import Localization
import Cui
import Gui
import Cfh
import carmensystems.rave.api as r
import carmusr.HelperFunctions as HelperFunctions
import carmstd.cfhExtensions as cfhExtensions

from Variable import Variable
from __main__ import exception as CarmenException

import carmstd.area as area

def createTorFile():
   """
   Based on the current content of the window, the TOR table is created and saved
   within the CARMDATA/ETABLES/TOR directory

   Is invoked from the Trip General window

   The hidden/TOR_etable.output report is used in order to create the TOR table.

   A form will appear where the name of the table should be stated, the TOR table
   with that name is then saved within the CARMDATA/ETABLES/TOR directory
   """
   
   if HelperFunctions.isDBPlan():
       cfhExtensions.show("createTorFile: Should not run in Database!")
       Errlog.log("createTorFile: Should not run in Database!")
       return
   
   # Check that the need Rave variables are present.
   
   try: 
       r.eval("tor.tor_penalty_use") 
   except r.ParseError: 
       Gui.GuiMessage(Localization.MSGR('Needed Rave definitions are missing in the loaded ruleset'))
       return -1
   except r.UsageError: 
       Gui.GuiMessage(Localization.MSGR('No ruleset loaded'))
       return -1

   # Get the Window area for correct context!
   currentArea = Cui.CuiAreaIdConvert(Cui.gpc_info,Cui.CuiWhichArea)

   #
   # Get environment
   #
   user = os.environ['USER']
   carmdata = os.environ['CARMDATA']
   
   #
   # Get subplan name
   #
   subplan = Variable("")
   Cui.CuiGetSubPlanName(Cui.gpc_info, subplan)
   if subplan.value == '':
     Gui.GuiMessage(Localization.MSGR('No subplan. Action canceled'))
     return -1

   #
   # Check for trips
   #
   Cui.CuiCrgSetDefaultContext(Cui.gpc_info,currentArea,"window")
   if not r.eval("default_context","studio_tor.tor_plan_num_chains")[0]:
       Gui.GuiMessage(Localization.MSGR('No trips in window. Action canceled'))
       return -1

   #
   # Initial values
   #
   tordir = carmdata + '/ETABLES/TOR'
   torfile = '%s_%s' % (subplan.value, user)
   reportfile = tempfile.mktemp(suffix='_TOR')

   #
   # Create a TOR directory if it does not exist
   #

   if not os.path.isdir(tordir):
       try:
           os.mkdir(tordir)
       except OSError:
           Gui.GuiMessage(Localization.MSGR('Impossible to create a directory for TOR tables'))
           return -1

   # Form
   torForm = Cfh.Box("TOR_FORM")
   # Field
   torFileField = Cfh.FileName(torForm, "TOR_FILE", 0, torfile)
   torFileField.setMandatory()
   # Buttons
   ok = Cfh.Done(torForm, "OK")
   cancel = Cfh.Cancel(torForm, "CANCEL")
   # Layout
   layout = """
FORM;TOR_FORM;`Create a TOR table`
FIELD;TOR_FILE;`Save the new TOR table as:`
BUTTON;OK;`OK`;`_OK`
BUTTON;CANCEL;`Cancel`;`_Cancel`
"""
   # Create layout as a temporary CFH file
   cfhFilePath = tempfile.mktemp()
   cfhFile = open(cfhFilePath, "w")
   cfhFile.write(layout)
   cfhFile.close()

   # Load the temporary CFH file as a form and delete the file
   torForm.load(cfhFilePath)
   os.unlink(cfhFilePath)

   torForm.show(True)

   fullpath_torfile = tordir + '/' + torfile
   if torForm.loop() != Cfh.CfhOk:
      return 1
   
   #
   # Check if file already exist but not writable
   #
   torfile = torFileField.valof()
   fullpath_torfile = tordir + '/' + torfile
   if os.access(fullpath_torfile, os.F_OK) == 1 and os.access(fullpath_torfile, os.W_OK) == 0:
      Gui.GuiMessage(Localization.MSGR('Unable to write to file "%s"') % (fullpath_torfile))
      return -1
   if os.access(fullpath_torfile, os.F_OK) == 1:
      if not Gui.GuiYesNo("TOR_VERIFY",
                          Localization.MSGR("A TOR table with that name exists. Overwrite?")):
         return 1

   #
   # Create report in temporary file
   #
   try:
      Cui.CuiCrgCreatePlainReport(Cui.gpc_info, 
                                  currentArea, 
                                  'window',
                                  'TOR_etable.output', 
                                  reportfile,
                                  'ascii')
   except CarmenException:
      Gui.GuiMessage('Unable to generate the PDL report')
      os.unlink(reportfile)
      return -1

   #
   # Change and copy the file 
   #
   if (os.system('sed s/ETABLE_INIT_NAME/%s/ %s > %s' % 
                 (os.path.basename(fullpath_torfile), reportfile, fullpath_torfile))):
      Gui.GuiMessage('Unable to install the table in the TOR direcory')
      os.unlink(reportfile)
      return -1
   
   #
   # Clean up
   #
   os.unlink(reportfile)
   
   Errlog.log('TOR file (%s) created' % (fullpath_torfile))
   area.promptPush(Localization.MSGR("TOR file created"))
   return 0

if __name__ == '__main__':

   createTorFile()
