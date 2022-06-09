#

#

"""
Copies the marked TOR table to the current subplan directory

Is invoked from the form CFM_TOR

The script takes the name of the marked TOR table and the path
of the current SpLocal directory as arguments
"""

#######################################################
#
# TOR_activate
#
# -----------------------------------------------------
#
#    This script is used from the form CFM_TOR to 
#    copy a TOR file to the current subplan.
#
#######################################################

import os
import os.path
import sys
import shutil

import Cui, Gui, Localization, Errlog
import carmstd.studio.area as area

# Source and destination files
#
# source
tor_file = sys.argv[1]
"""
Name of the marked TOR table
"""
tor_base = os.path.basename(tor_file)
"""
Name of the current sub-plan
"""
# destination
sp_file = sys.argv[2]
"""
Path for the sub-plan etable directory
"""
# Log
Errlog.log('TOR_activate.py: %s -> %s' % (tor_file, sp_file))

#
# Execute the copy command passed on command line
#
shutil.copy(tor_file,sp_file)

#
# Reload and redraw
#
Cui.CuiReloadTables()
Gui.GuiCallListener(Gui.RefreshListener, 'parametersChanged')

#
# Notify user with a message on the promptline in Studio
#
area.promptPush(Localization.MSGR("Selected TOR etable (%s) has been activated for the current subplan" % (tor_base)))

