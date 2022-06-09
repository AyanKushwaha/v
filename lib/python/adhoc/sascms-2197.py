

"""
SASCMS-2197 (CR) - F7S days to SKN FD.

This script was specially made to be able to run retroactively for SKN FD crew
only.
"""

import utils.mdor
utils.mdor.start(__name__)

import logging
import os
import salary.compconv

from AbsTime import AbsTime
from tm import TM, TMC


log = logging.getLogger('sascms-2197')
log.setLevel(logging.INFO)


class ZZF7SData(salary.compconv.F7SData):
    def get_class(self, cat, country):
        """Block all other F7S categories except for SKN FD."""
        if cat == "F" and country == "NO":
            return salary.compconv.F7SFD


def main(connect, schema, tim):
    commit = not bool(os.environ.get("CMS_SALARY_NOCOMMIT", False))
    global TM
    TM = TMC(connect, schema)
    # Notorious bug, tables must be loaded before newState()!
    TM('account_entry', 'crew_employment', 'crew_qualification',
            'crew_contract', 'account_baseline', 'activity_set')
    try:
        TM.newState()
        salary.compconv.Increment_F7S(tim, data_class=ZZF7SData).increment()
        if commit:
            TM.save()
            revid = TM.getSaveRevId()
            if revid > 0:
                log.info("...saved with revid = '%s'." % revid)
            else:
                log.info("...NOT saved - no changes were found!")
        else:
            log.info("...NOT saving (no-commit flag) was given.")
    except Exception, e:
        log.error(e)
        if commit:
            TM.undo()
        raise


if __name__ == '__main__':
    main(os.environ['DB_URL'], os.environ['DB_SCHEMA'], AbsTime(2010, 1, 1, 0, 0))


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
