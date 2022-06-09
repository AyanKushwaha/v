
#
# Purpose: Perform custom functions and save plan.
#
# User will get these options:
# 'Yes'     -> Save
# 'No'      -> Don't save, don't exit.
#
# [acosta:08/031@13:47] Changed to user 'referers', and to get
# empno only for the crew that is actually shown.
#

import Cui
import StartTableEditor
import carmensystems.rave.api as rave
import carmstd.cfhExtensions
import carmusr.modcrew
from utils.performance import log

from tm import TM


# Global variable that determines the message on the confirm save dialogue
save_db_to_file = False
skip_confirm_dialog = False

# Other global variables.
dialog_message = "Do you want to save?"
dialog_title = "Confirm Save"
dialog_max_crew = 34

def confirmSave():
    """Return 'True' if user wants to save, 'False' if not (= cancel)."""
    if skip_confirm_dialog:
        return True

    if save_db_to_file:
        return True
        
    import StartTableEditor

    open_forms = []
    try:
        for f in (StartTableEditor.getOpenForms() or []):
            if StartTableEditor.getFormState(f[0]) in ("visible","multiple","error"):
                open_forms.append(f[0])
    except:
        log("Failed to retrieve state of Wave forms. Assume none is open.")
        
    if open_forms:
        if len(open_forms) == 1:
            msg = "There is an open form.\n"
        else:
            msg = "There are %d open forms.\n" % len(open_forms)
        if carmstd.cfhExtensions.confirm(msg + "Unapplied changes in forms will be lost.\n\nDo You still want to save the plan?\n", title="Warning") == 0:
            return False

    mod_crew = carmusr.modcrew.get()
    if not mod_crew:
        dosave = carmstd.cfhExtensions.confirm(dialog_message, title=dialog_title)
        if dosave:
            if open_forms:
                log("===== START SAVE, NO MODIFIED ROSTERS, WITH OPEN FORM(S):")
                for f in open_forms:
                    log("===== %s" % f)
            else:
                log("===== START SAVE, NO MODIFIED ROSTERS")
        return dosave

    now, = rave.eval("fundamental.%now%")
    def _get_empno(crewid):
        for x in TM.crew[(crewid,)].referers('crew_employment', 'crew'):
            if x.validfrom <= now and x.validto > now:
                return x.extperkey
        return '?????'

    nr_crew = len(mod_crew)

    # Create list of sorted employee numbers, no more than dialog_max_crew
    E = sorted([_get_empno(mod_crew[i]) for i in xrange(0, min(nr_crew, dialog_max_crew))])

    # Split into rows
    r = 0
    rows = {r: []}
    for i in xrange(0, len(E)):
        # On first row, show 11 crew members, on the rest show 13
        if r == 0 and i > 12:
            r += 1
            rows[r] = []
        elif not (i - 12 + 1) % 13:
            r += 1
            rows[r] = []
        rows[r].append(E[i])
    if nr_crew > dialog_max_crew:
        rows[r].append('...')

    if nr_crew == 1:
        txt = "Crew member %s has been modified.\n%s"
    else:
        txt = "Crew members %s have been modified.\n%s"
    m = ',\n'.join([', '.join(y) for x, y in rows.iteritems()])
    dosave = carmstd.cfhExtensions.confirm(txt % (m, dialog_message), title=dialog_title)
    if dosave:
        if open_forms:
            log("===== START SAVE, %d MODIFIED ROSTERS, WITH OPEN FORM(S):" % nr_crew)
            for f in open_forms:
                log("===== %s" % f)
        else:
            log("===== START SAVE, %d MODIFIED ROSTERS" % nr_crew)
    return dosave


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
