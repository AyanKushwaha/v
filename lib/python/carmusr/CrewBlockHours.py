

"""
Display crew statistics:
    Block Hours
    Loggable Block Hours (a.k.a. Reduced Block Hours)
    Simulator Block Hours
    Landings

and allow for manual modifications of these values.
"""

# imports ================================================================{{{1
import getpass

import utils.crewlog as crewlog
import utils.wave
if not utils.wave.STANDALONE:
    import Cui
    import carmstd.cfhExtensions as cfhExtensions
    import StartTableEditor
    import MenuState

from AbsTime import AbsTime
from RelTime import RelTime
from modelserver import IntColumn, StringColumn, RefColumn, BoolColumn, RelTimeColumn, TimeColumn
from modelserver import EntityNotFoundError

from tm import TM, TempTable
from utils.time_util import Interval


# help classes ==========================================================={{{1

# CBHError ---------------------------------------------------------------{{{2
class CBHError(Exception):
    """Anticipated faults in the application."""
    msg = ''
    def __init__(self, msg=''):
        self.msg = msg

    def __str__(self):
        return str(self.msg)


# conf -------------------------------------------------------------------{{{2
class conf:
    """Some configuration variables."""
    appname = "Crew Block Hours"
    formpath = "$CARMUSR/data/form/crew_block_hours.xml"
    cbh_acc = 'tmp_cbh_acc_table'
    cbh_actypes = 'tmp_cbh_ac_types'
    cbh_crew_details = 'tmp_cbh_crew_details'
    cbh_form_info = 'tmp_cbh_form_info'
    cbh_stat = 'tmp_cbh_stat'
    acfam_others = 'OTHER'


# SequentialInfo ---------------------------------------------------------{{{2
class SequentialInfo:
    """Base class, provides a sequence number counter."""
    def __init__(self):
        self.__seqno = 0

    def get_seqno(self):
        """Return sequence number and increase."""
        s = self.__seqno
        self.__seqno += 1
        return s


# classes for handling temporary tables =================================={{{1

# TmpAcc -----------------------------------------------------------------{{{2
class TmpAcc(SequentialInfo):
    """Handle temporary table with manual corrections."""

    class TmpAcTypes:
        """Temporary table with list of A/C families. This table is used by the
        Wave GUI to get a drop-down list."""
        def __init__(self):
            """Create table if not already there and populate with information
            from 'aircraft_type'."""
            self.table = TempTable(conf.cbh_actypes, [StringColumn('id')])
            self.table.removeAll()
            self.default_acfamily = None
            for acfamily in sorted(set([x.maintype for x in TM.aircraft_type])):
                rec = self.table.create((acfamily,))
                if self.default_acfamily is None:
                    self.default_acfamily = rec
            self.table.create((conf.acfam_others,))

    def __init__(self, parent):
        """Create temporary table (if not already there)."""
        SequentialInfo.__init__(self)
        self.th_actypes = self.TmpAcTypes()
        self.table = TempTable(conf.cbh_acc, [ 
                IntColumn('seqno', 'Sequence Number'),
            ], [
                RefColumn('typ', 'crew_log_acc_set', 'Accumulator Type'),
                RefColumn('crew', 'crew', 'Crew ID'),
                RefColumn('acfamily', conf.cbh_actypes, 'AC Family'),
                TimeColumn('tim', 'Time'),
                IntColumn('accvalue_i', 'Value'),
                RelTimeColumn('accvalue_r', 'Value'),
            ])
        self.table.removeAll()
        self.crewid = None
        self.typ = None
        self.parent = parent

    def clear(self):
        """Empty temporary table."""
        self.table.removeAll()

    def populate(self, typ, crewid):
        """Fill table with information from 'crew_log_acc_mod'."""
        self.crewid = crewid
        self.typ = typ
        self.table.removeAll()
        for x in TM.crew[(crewid,)].referers('crew_log_acc_mod', 'crew'):
            if x.typ.acc_type == typ:
                rec = self.table.create((self.get_seqno(),))
                rec.typ = x.typ
                rec.crew = x.crew
                rec.acfamily = getattr(TM, conf.cbh_actypes)[(x.acfamily,)]
                rec.tim = x.tim
                rec.accvalue_i = x.accvalue
                rec.accvalue_r = RelTime(x.accvalue)
	            #Errlog.log( "rec.accvalue_r: %s" % rec.accvalue_r)

    def delete_row(self, seqno):
        """Remove row from temporary table."""
        self.table[(int(seqno),)].remove()

    def create_new_row(self):
        """Add new row to temporary table."""
        now = utils.wave.get_now_utc()
        rec = self.table.create((self.get_seqno(),))
        rec.typ = TM.crew_log_acc_set[(self.typ,)]
        rec.crew = TM.crew[(self.crewid,)]
        rec.acfamily = self.th_actypes.default_acfamily
        rec.tim = now

    def int_value(self, rec):
        """Convert user-entered value to integer."""
        if rec.typ.is_reltime:
            value = rec.accvalue_r
        else:
            value = rec.accvalue_i
        try:
            return int(value)
        except:
            return 0

    def save_changes(self):
        """Commit changes in temporary table to 'crew_log_acc_mod'."""

        # Sync the temporary table with crew_log_acc_mod, this will be in
        # several steps: 
        # (i)   transform temptable data to dictionary 'tempdata'.
        # (ii)  transform data from crew_log_acc_mod to dictionary 'moddata'.
        # (iii) compare 'tempdata' and 'moddata' and group records into three
        #       groups: added, changed, and, removed.
        # (iv)  commit changes to crew_log_acc_mod and update statistics
        # (v)   remove all rows and refresh from crew_log_acc_mod

        crew_ref = TM.crew[(self.crewid,)]
        acc_ref = TM.crew_log_acc_set[(self.typ,)]

        # (i) put entries from this temptable into 'tempdata'
        tempdata = {}

        for row in self.table:
            try:
                acfam = row.acfamily.id
            except:
                raise CBHError("Incomplete record, A/C family missing. Edit or remove the record.")
            if row.tim is None:
                raise CBHError("Incomplete record, Time-point missing. Edit or remove the record.")
            value = self.int_value(row)
            if value == 0:
                # No need to save empty rows.
                row.remove()
                continue
            key = (acfam, row.tim)
            tempdata[key] = value + tempdata.get(key, 0)

        # (ii) put entries from crew_log_acc_mod into 'moddata'
        moddata = {}

        for rec in crew_ref.referers('crew_log_acc_mod', 'crew'):
            if rec.typ.acc_type == self.typ:
                key = (rec.acfamily, rec.tim)
                moddata[key] = (rec.accvalue or 0) + moddata.get(key, 0)

        # (iii) compare newly entered data with persistent data
        added, changed, deleted = set(), set(), set()
        for key in tempdata:
            if key in moddata:
                if tempdata[key] != moddata[key]:
                    changed.add(key)
            else:
                added.add(key)
        for key in moddata:
            if key not in tempdata:
                deleted.add(key)

        # (iv) let 'crew_log_acc_mod' reflect changes in temptable and update
        # statistics
        for key in added:
            # Add new entries
            dbkey = (crew_ref, acc_ref) + key
            dbrow = TM.crew_log_acc_mod.create(dbkey)
            dbrow.accvalue = tempdata[key]
            self.parent.update_statistics(dbkey, tempdata[key])

        for key in changed:
            # Modify database entries
            dbkey = (crew_ref, acc_ref) + key
            dbrow = TM.crew_log_acc_mod[dbkey]
            oldvalue = dbrow.accvalue
            dbrow.accvalue = tempdata[key]
            self.parent.update_statistics(dbkey, tempdata[key] - oldvalue)

        for key in deleted:
            # Remove database entries
            dbkey = (crew_ref, acc_ref) + key
            dbrow = TM.crew_log_acc_mod[dbkey]
            oldvalue = dbrow.accvalue
            dbrow.remove()
            self.parent.update_statistics(dbkey, -oldvalue)

        # (v) Remove all rows and refresh from crew_log_acc_mod
        self.populate(self.typ, self.crewid)

        if utils.wave.STANDALONE:
            # Save to DB without using studio
            TM.save()


# TmpDetails -------------------------------------------------------------{{{2
class TmpDetails:
    """Temporary table that contains information about the crew member and
    makes it possible for the end-user to change type (blockhrs, logblkhrs,
    etc.)"""
    def __init__(self, parent):
        self.table = TempTable(conf.cbh_crew_details, [
                IntColumn('seqno', 'Sequence Number'),
            ], [
                StringColumn('empno', 'Employee Number'),
                StringColumn('name', 'Name'),
                StringColumn('rank', 'Rank'),
                RefColumn('typ', 'crew_log_acc_set', 'Acc. Type'),
            ])
        self.clear()
        self.parent = parent

    def populate(self, crewid, now):
        """Populate table with information about the crew member."""
        self.clear()
        rec = self.table.create((0,))
        rec.typ = TM.crew_log_acc_set[(self.parent.typ,)]
        crewref = TM.crew[(crewid,)]
        for cemp in crewref.referers('crew_employment', 'crew'):
            if cemp.validfrom <= now < cemp.validto:
                rec.empno = "%s (%s)" % (cemp.extperkey, crewid)
                for info in crewref.referers('crew_extra_info', 'id'):
                    if info.validfrom <= now < info.validto:
                        rec.name = info.logname
                        break
                else:
                    rec.name = cemp.crew.logname
                rec.rank = cemp.crewrank.id
                break

    def clear(self):
        """Empty temporary table."""
        self.table.removeAll()


# TmpFormInfo ------------------------------------------------------------{{{2
class TmpFormInfo:
    """Temporary table that is used to communicate with the GUI."""
    def __init__(self, parent):
        """Create temporary table if not existent."""
        self.parent = parent
        self.table = TempTable(conf.cbh_form_info, [
                IntColumn('seqno', 'Sequence Number'),
            ], [
                StringColumn('status_message', 'Status bar message'),
                StringColumn('status_colour', 'Status bar colour'),
                BoolColumn('unsaved_changes', 'Unsaved changes?'),
            ])
        self.table.removeAll()
        self.table.create((0,))

    def set_status_message(self, message, is_error=False):
        """Submit message to Wave GUI."""
        row = self.table[(0,)]
        row.status_message = message
        if is_error:
            row.status_colour = "red"
        else:
            row.status_colour = "transparent"


# TmpStat ----------------------------------------------------------------{{{2
class TmpStat(SequentialInfo):
    """Handle temporary table with statistics for crew member."""
    def __init__(self, parent):
        """Create temporary table if not existent."""
        SequentialInfo.__init__(self)
        self.table = TempTable(conf.cbh_stat, [
                IntColumn('seqno', 'Sequence Number'),
            ], [
                TimeColumn('validfrom', 'Valid from'),
                TimeColumn('validto', 'Valid to'),
                StringColumn('itext', 'Interval'),
                StringColumn('acfamily', 'A/C Family'),
                IntColumn('accvalue_i', 'Value (int)'),
                RelTimeColumn('accvalue_r', 'Value (reltime)'),
            ])
        self.clear()
        self.intervals = []
        self.parent = parent

    def clear(self):
        """Remove all entries from temporary table."""
        self.table.removeAll()

    def populate(self, typ, crew, now):
        """Clear table and fill with statistics from database."""
        self.clear()
        try:
            the_cstat = crewlog.stat_1_90_6_12_life(crew, typ=typ, hi=now)
            the_intervals = the_cstat.intervals
            cstat = the_cstat[typ][crew]
        except KeyError:
            return

        all = {}
        for a in cstat:
            for i in cstat[a]:
                all[i] = all.get(i, 0) + cstat[a][i]

        self.intervals = zip(('This month', 'Last month', 'Last 90 days', 
            'Last 6 months', 'Last 12 months', 'Lifetime'), the_intervals)

        for acfamily in sorted(cstat):
            for (caption, interval) in self.intervals:
                self.add(acfamily, caption, interval, cstat[acfamily].get(interval, 0))
        for (caption, interval) in self.intervals:
            self.add('ALL', caption, interval, all.get(interval, 0))

    def add(self, acfamily, caption, interval, value):
        """Add one row to the temporary table."""
        rec = self.table.create((self.get_seqno(),))
        validfrom, validto = interval
        rec.validfrom = AbsTime(validfrom)
        rec.validto = AbsTime(validto)
        rec.itext = caption
        rec.acfamily = acfamily
        rec.accvalue_i = value
        try:
            rec.accvalue_r = RelTime(value)
        except:
            pass
        return rec

    def update_statistics(self, key, value):
        """Update temporary table directly after manual changes in order to
        avoid costly database searches."""
        crewref, acctyperef, acfamily, tim = key
        U = {}
        for rec in self.table:
            if rec.acfamily != 'ALL':
                if acctyperef.is_reltime:
                    if rec.accvalue_r is None:
                        v = 0
                    else:
                        v = int(rec.accvalue_r)
                else:
                    if rec.accvalue_i is None:
                        v = 0
                    else:
                        v = rec.accvalue_i
                U[(rec.acfamily, Interval(int(rec.validfrom), int(rec.validto)))] = (rec.itext, v)
        for (c, i) in self.intervals:
            if i.first <= int(tim) <= i.last:
                if (acfamily, i) in U:
                    itext, v = U[(acfamily, i)]
                    U[(acfamily, i)] = (itext, v + value)
                else:
                    U[(acfamily, i)] = (c, value)
        self.clear()
        all = {}
        for (a, i) in sorted(U):
            c, v = U[(a, i)]
            self.add(a, c, i, v)
            all[i] = all.get(i, 0) + v
        for (c, i) in self.intervals:
            self.add('ALL', c, i, all.get(i, 0))


# CBH ===================================================================={{{1
class CBH:
    """Crew Block Hours handler, dispatch messages to the different
    components."""
    def __init__(self):
        """Set some default values. Don't create any temporary tables at this
        stage, since the module is imported at a very early stage."""
        self.crewid = None
        self.typ = 'blockhrs'
        self.now = None

    def initiate_tables(self):
        """XMLRPC: Create tables if not already there. This method is called
        from Wave GUI upon load."""

        # Set the menu state OpenWaveForms to hide Undo buttons in Studio
        # on opening wave forms (Crew Info, Crew Accounts, Crew Training,
        # Crew Block Hours). SASCMS-4562
        if not utils.wave.STANDALONE:
            MenuState.setMenuState('OpenWaveForms', 1, forceMenuUpdate = True)

        utils.wave.refresh_wave_values()
        now_utc = utils.wave.get_now_utc()
        TM('crew_employment','crew_log_acc_mod')
        self.th_details = TmpDetails(self)
        self.th_acc = TmpAcc(self)
        self.th_forminfo = TmpFormInfo(self)
        self.th_stat = TmpStat(self)
        if self.crewid is not None:
            empno = None
            for row in TM.crew_employment.search("(&(crew=%s)(validfrom<%s)(validto>%s))" % (self.crewid, now_utc, now_utc)):
                empno = row.extperkey
                break
            if empno is None:
                self.error_message("Crew with crewid %s not found in crew employment." % self.crewid)
            else:
                self.get_new_crew(empno)
        return {'actions': 'refreshClient();'}

    def set_crewid_from_studio(self):
        """Pick current crew when launched from within Studio."""
        self.crewid = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object",
                "crr_crew_id")

    def change_type(self, typ):
        """XMLRPC: Change accumulator type."""
        self.typ = typ
        self.th_acc.populate(typ, self.crewid)
        self.th_stat.populate(typ, self.crewid, self.now)
        typref = TM.crew_log_acc_set[(typ,)]
        self.message("Changed type to '%s'." % typref.si)

    def create_new_row(self):
        """XMLRPC: Create new row in temporary table."""
        try:
            self.th_acc.create_new_row()
            self.message("Row created.")
        except CBHError, cbhe:
            self.error_message(cbhe)

    def delete_row(self, seqno):
        """XMLRPC: Delete current row."""
        try:
            self.th_acc.delete_row(seqno)
            self.message("Row deleted.")
        except CBHError, cbhe:
            self.error_message(cbhe)

    def get_new_crew(self, empno):
        """XMLRPC: Collect info for crew member with employee number 'empno'."""
        utils.wave.refresh_wave_values()
        now = utils.wave.get_now_utc()
        TM.refresh()
        try:
            crewid = None
            for x in TM.crew_employment.search("(&(extperkey=%s)(validfrom<=%s)(validto>%s))" % (empno, now, now)):
                crewid = x.crew.id
                break
            if crewid is None:
                raise CBHError("Crew %s not found/valid. Please enter a valid employment number." % empno)
            self.populate(crewid, self.typ, now)
            self.message("Fetched crew %s." % empno)
        except CBHError, cbhe:
            self.error_message(cbhe)

    def save_changes(self, message):
        """XMLRPC: Commit changes."""
        try:
            if int(message) not in (0, 1):
                raise CBHError("Formatting error found. Entries with wrong format are outlined in red.")
            self.th_acc.save_changes()
            self.message("Changes saved.")
        except CBHError, cbhe:
            self.error_message(cbhe)

    def message(self, msg, is_error=False):
        """Set message for status row in Wave GUI."""
        self.th_forminfo.set_status_message(str(msg), is_error)

    def error_message(self, msg):
        """Set error message for status row in Wave GUI. The error message has a
        different background color."""
        self.message(msg, True)

    def clear(self):
        """Clear temporary tables."""
        self.th_details.clear()
        self.th_acc.clear()
        self.th_stat.clear()

    def populate(self, crewid, typ, now):
        """Populate temporary tables with crew info."""
        self.typ = typ
        self.crewid = crewid
        self.now = now
        self.th_details.populate(crewid, now)
        self.th_acc.populate(typ, crewid)
        self.th_stat.populate(typ, crewid, now)

    def update_statistics(self, key, value):
        """Recalculate statistics so that recent changes will be shown in the
        statistics pane. Avoid looping thru the database again."""
        self.th_stat.update_statistics(key, value)


# cbh ===================================================================={{{1
# Singleton instance of CBH
cbh = CBH()


# XML-RPC functions ======================================================{{{1
# Register CSD (XML-RPC) functions accessible from the XML form.

# cbh_change_type --------------------------------------------------------{{{2
class cbh_change_type(utils.wave.LocalService):
    """Add new row to crew_log_acc_mod."""
    def func(token, typ):
        return cbh.change_type(typ)


# cbh_create_new_row -----------------------------------------------------{{{2
class cbh_create_new_row(utils.wave.LocalService):
    """Add new row to crew_log_acc_mod."""
    def func(token):
        return cbh.create_new_row()


# cbh_delete_row ---------------------------------------------------------{{{2
class cbh_delete_row(utils.wave.LocalService):
    """Delete row from crew_log_acc_mod."""
    def func(token, seqno):
        return cbh.delete_row(seqno)


# cbh_get_new_crew -------------------------------------------------------{{{2
class cbh_get_new_crew(utils.wave.LocalService):
    """Refresh GUI and tables with new crew."""
    def func(token, empno):
        return cbh.get_new_crew(empno)


# cbh_initiate_tables ----------------------------------------------------{{{2
class cbh_initiate_tables(utils.wave.LocalService):
    """Called from form at start-up."""
    def func(token):
        return cbh.initiate_tables()
    

# cbh_save_changes -------------------------------------------------------{{{2
class cbh_save_changes(utils.wave.ModelChangeService):
    """Commit changes."""
    def func(token, message):
        return cbh.save_changes(message)


# start =================================================================={{{1
def start():
    """Called from Studio menu to start Crew Block Hours."""
    cbh.set_crewid_from_studio()
    if str(StartTableEditor.getFormState(conf.formpath)).lower() not in ('none', 'error'):
        #Form already open!
        cfhExtensions.show("%s form is open,\nplease use the already opened form!" % conf.appname)
        return 
    StartTableEditor.StartTableEditor(['-f', conf.formpath], conf.appname)


# run_on_import =========================================================={{{1
def run_on_import():
    """This function will be run the first time this module is imported."""
    utils.wave.register()


# Register XML-RPC methods
run_on_import()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
