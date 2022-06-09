
# [acosta:08/218@17:29] First version.
# [acosta:08/224@17:03] Improved: unique names and removal on exit.

"""
Dump 'activity_set' into an Etable format, so the CFH form for creating
activities - '$CARMUSR/data/form/pact' - can use this temporary Etable for
validating that the activity code is part of 'activity_set' (>2000 activity
codes).

The Etable that was used previously for this purpose,
'$CARMUSR/crc/etable/tasks_studio.etab', is still used, but now only to create
the list of activities the user can pick from (~20-30 activity codes).

Files involved:
    $CARMUSR/data/form/pact
    $CARMUSR/data/config/CarmResources/Implementation.etab
        default.default.TASK_ETAB_NAME, TASK_ETAB_CODE, TASK_ETAB_DESC, ...
    $CARMSYS/data/config/CarmResources/General.etab 
        (default values for TASK_ETAB_START, TASK_ETAB_END, TASK_ETAB_DAYOFF
        and TASK_ETAB_SHIFT unchanged)

NOTE:
    * This module is imported (indirectly from StudioCustom).
    * Upon import, an empty Etable will be created (name is specified in
      'Implementation.etab').
    * This etable will be removed on exit (using 'atexit' handler).
"""

# imports ================================================================{{{1
import atexit
import datetime
import os
import time
import traceback

import Crs
import Cui

from Etab import Etable
from tm import TM
from Variable import Variable
from AbsTime import AbsTime


# exports ================================================================{{{1
__all__ = ['run', 'main', 'Main']


# classes ================================================================{{{1

# IterWrapperActivityGroupPeriod -----------------------------------------{{{2
class IterWrapperActivityGroupPeriod:
    """Help class, iterates over the ETable."""

    def __init__(self):
        """Create object used for iterating the Etable."""
        l_path = Variable("", 200)
        Cui.CuiGetLocalPlanPath(Cui.gpc_info, l_path)
        table_path = os.path.join(os.environ['CARMDATA'], "LOCAL_PLAN",
                                  str(l_path), "etable", "LpLocal", "activity_group_period")
        if not os.path.exists(table_path):
            if os.path.exists(table_path+'.etab'):
                table_path += '.etab'
            else:
                raise Exception('activity_set:: Could not find table %s'%table_path)
            
        self.etable = Etable(table_path)

    def __iter__(self):
        """Reset row index, note row numbers start with 1."""
        self.rowidx = 0
        return self

    def next(self):
        """Called for each iteration."""
        # Index starts with 'one' (1).
        self.rowidx += 1
        try:
            row = self.etable[self.rowidx]
            values = dict()
            values["id"] = row[0]
            values["validfrom"] = AbsTime(row[1])
            values["validto"] = AbsTime(row[2])
            values["onduty"] = row[10]
            values["dayoff"] = row[12]
            return values
        except:
            raise StopIteration()

# IterWrapperActivitySet -------------------------------------------------{{{2
class IterWrapperActivitySet:
    """Help class, iterates over the ETable."""

    def __init__(self, group_data):
        """Create object used for iterating the Etable."""
        l_path = Variable("", 200)
        Cui.CuiGetLocalPlanPath(Cui.gpc_info, l_path)
        self.etable = Etable(os.path.join(os.environ['CARMDATA'], "LOCAL_PLAN",
            str(l_path), "etable", "LpLocal", "activity_set"))
        self.group_data = group_data

    def __iter__(self):
        """Reset row index, note row numbers start with 1."""
        self.rowidx = 0
        return self

    def next(self):
        """Called for each iteration."""
        # Index starts with 'one' (1).
        self.rowidx += 1
        try:
            row = self.etable[self.rowidx]
            values = dict()
            values["id"], values["grp"], values["si"] = row[:3]
            values["dayoff"] = "N"
            values["onduty"] = "N"
            if self.group_data.has_key(values['grp']):
                if self.group_data[values['grp']].has_key("dayoff"):
                    values["dayoff"] = self.group_data[values['grp']]["dayoff"]
                if self.group_data[values['grp']].has_key("onduty"):
                    values["onduty"] = self.group_data[values['grp']]["onduty"]
            
            return values
        except:
            raise StopIteration()

# IterWrapperDb --------------------------------------------------------{{{2
class IterWrapperDb:
    """Help class, iterates over the database table."""

    def __init__(self, period_start):
        """Create object used for iterating the Etable."""
        self.group_data = dict()

        for gp in TM.activity_group_period:
            # Period filter..
            # Always store first version as a default backup.
            # Then only override with versions which include period_start.
            # Last period start including record will win.
            if gp.validfrom > period_start or ((not gp.validto is None) and gp.validto < period_start):
                if self.group_data.has_key(gp.id.id):
                    continue
            self.group_data[gp.id.id] = dict()
            if gp.dayoff == 0:
                self.group_data[gp.id.id]["dayoff"] = 'N'
            else:
                self.group_data[gp.id.id]["dayoff"] = 'Y'
            if gp.onduty == 0:    
                self.group_data[gp.id.id]["onduty"] = 'N'
            else:
                self.group_data[gp.id.id]["onduty"] = 'Y'
        
    def __iter__(self):
        """Reset row index, note row numbers start with 1."""
        self.activity_set_iter = iter(TM.activity_set)
        return self

    def next(self):
        """Called for each iteration."""
        rec = self.activity_set_iter.next()
        values = dict()
        values["id"] = rec.id
        values["si"] = rec.si
        values["grp"] = rec.grp.id
        # Default values for onduty and dayoff in case
        # they don't exist or columns are null in activity_group_period
        values["dayoff"] = 'N'
        values["onduty"] = 'N'
        if self.group_data.has_key(rec.grp.id):
            if self.group_data[rec.grp.id].has_key("dayoff"):
                values["dayoff"] = self.group_data[rec.grp.id]["dayoff"]
            if self.group_data[rec.grp.id].has_key("onduty"):
                values["onduty"] = self.group_data[rec.grp.id]["onduty"]

        return values

    
# Main -------------------------------------------------------------------{{{2
class Main:
    """Iterate database entity or Etable and create temporary Etable with extra
    columns that can be used by the CFH form for validation of input."""
    def __init__(self, etab=None):
        """The parameter 'etab' can be a file name (for testing)."""

        if etab is None:
            # Fetch name from CRS
            self.etab = Crs.CrsGetAppModuleResource(
                    "default", Crs.CrsSearchAppExact, 
                    "default", Crs.CrsSearchModuleExact,
                    "TASK_ETAB_NAME")
        else:
            self.etab = etab
        now = time.gmtime()
        self.period_start = AbsTime(now[0], now[1], now[2], 0, 0)

    def __call__(self):
        """Create and copy to Etable."""
        f = open(self.etab, "w")
        self.write_header(f)
        for e in self:
            self.write_record(e, f)
        f.close()
        return self

    def __iter__(self):
        """Return iterator depending on context."""
        if self.is_db():
            return iter(IterWrapperDb(self.period_start))
        else:
            group_data = dict()
            for gp in iter(IterWrapperActivityGroupPeriod()):
                if gp['validfrom'] > self.period_start or ((not gp['validto'] is None) and gp['validto'] < self.period_start):
                    if group_data.has_key(gp['id']):
                        continue
                group_data[gp['id']] = dict()
                if gp['dayoff'].upper() == 'FALSE':
                    group_data[gp['id']]["dayoff"] = 'N'
                else:
                    group_data[gp['id']]["dayoff"] = 'Y'
                if gp['onduty'].upper() == 'FALSE':    
                    group_data[gp['id']]["onduty"] = 'N'
                else:
                    group_data[gp['id']]["onduty"] = 'Y'
            return iter(IterWrapperActivitySet(group_data))

    def init(self):
        """Create an empty Etable and register 'atexit' function to remove the
        table when the application is closed."""
        f = open(self.etab, "w")
        self.write_header(f)
        f.close()
        atexit.register(self.remove_etable)

    def is_db(self):
        """Return bool: True if database plan, False if file based."""
        db = Variable(0)
        Cui.CuiSubPlanIsDBPlan(Cui.gpc_info, db)
        return bool(db.value)

    def main(self):
        return self

    def remove_etable(self):
        """Try to remove the temporary Etable."""
        try:
            os.unlink(self.etab)
        except:
            pass

    def write_header(self, file):
        """Write the Etable header with column information."""
        print >>file, '\n'.join((
            '/*',
            ' * Created by %s.%s at %sZ.' % (self.__module__,
                self.__class__.__name__,
                datetime.datetime.today().isoformat()),
            ' */',
            '',
            '8',
            'Sid "Task code",',
            'Sgrp "Task group",',
            'Ssi "Task description",',
            'RStartTime "Time of day when the task starts",',
            'REndTime "Time of day when the task ends",',
            'SShift "Task shift",',
            'SDayOff "Is the task day off? Y/N",',
            'SOnDuty "Duty Y/N",',
            '',
        ))

    def write_record(self, rec, file):
        """Print one record to the Etable."""
        print >>file, '"%s", "%s", "%s", 0:00, 0:00, "0", "%s", "%s",' % (rec["id"], rec["grp"], rec["si"], rec["dayoff"], rec["onduty"])
        

# run ===================================================================={{{1
run = Main()


# main ==================================================================={{{1
main = run.main


# initialization code ===================================================={{{1
# This code is run every time this module is imported.
run.init()


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    main()
    

# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
