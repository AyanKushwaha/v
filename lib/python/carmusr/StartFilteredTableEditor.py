

"""
"""

import os
import StartTableEditor

# launch()
def launch(args=[]):
    """
    """
    carmRole = os.getenv('CARMROLE')
    carmUsr = os.getenv('CARMUSR')
    params = args
    params += ['-f', '!/forms/tableeditor/dtable_studio_cms/MainApp.xml',
               '-P', 'tablereport=carmensystems.tableeditor.TableReport']

    if carmRole != 'Administrator' :
        params += ['-P', 'cmsRole=' + carmRole]

    StartTableEditor.StartTableEditor(params)

# main
if __name__ == "__main__":
    launch()

# eof
