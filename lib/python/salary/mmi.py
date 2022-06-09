
# [acosta:06/242@12:57] Adjusted for newer version of CARMSYS.
# [acosta:07/092@15:43] Trying to give more meaningful messages to operator in case of error.

"""
This is the Man-Machine-Interface to the salary system.

This is part of a client server solution for SAS salary calculations.
Client: wave form directly on mirador (table editor)
Middleware: dig
Server: report server calls a interface module.
"""

# NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE!  
#
# TM.newState(), TM.save(), and, TM.undo(), will probably disappear in a near
# future.
# 
# Rows with calls to these methods are marked with XXX.
#
# NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE!  


# imports ================================================================{{{1
import logging
import os

import carmensystems.services.dispatcher as csd
from utils.Names import username

from dig.DigJobQueue import DigJobQueue
from modelserver import DateColumn, IntColumn, RefColumn, StringColumn, TimeColumn, BoolColumn
from tm import TM, TempTable

import salary.api as api
import salary.conf as conf
import salary.run as run
import utils.exception
import utils.mailtools as mailtools
import utils.wave


# Init on module creation ================================================{{{1
log = logging.getLogger('salary.mmi')


# [acosta:07/065@17:01] added these variables to be able to use the new concept
_messageHandler = None
_runIdHandler = None
_formatHandler = None


# Handlers for temporary tables used by the form ========================={{{1

# MessageHandler ---------------------------------------------------------{{{2
class MessageHandler:
    """
    Show status message in status bar.
    """
    MAXLENGTH = 200
    def __init__(self):
        self.defaultmsg = " "
        self.lastmsg = self.defaultmsg
        self.messagesTempTable = self.MessagesTempTable()
        self.messagesTempTable.removeAll()
        self.record = self.messagesTempTable.create((0,))

    def setmsg(self, msg):
        log.debug("MessageHandler().setmsg(%s)'." % (msg))
        msg = msg[:self.MAXLENGTH]
        self.record.message = msg
        self.lastmsg = msg

    def enable(self, m=None):
        log.debug("MessageHandler().enable(%s)" % (m))
        if m is None:
            self.setmsg(self.defaultmsg)
        else:
            if not m == self.lastmsg:
                self.setmsg(m)

    def disable(self):
        log.debug("MessageHandler().disable()")
        self.setmsg(self.defaultmsg)

    # Inner classes ------------------------------------------------------{{{3
    # MessagesTempTable --------------------------------------------------{{{4
    class MessagesTempTable(TempTable):
        def __init__(self):
            TempTable.__init__(self,
                conf.tmp_salary_messages, 
                [IntColumn("dummy", "Dummy column")],
                [StringColumn("message", "Message")]
            )

class MailingMenuItemHandler:
    """
    Enable/disable menu item (mailing to crew).
    """
    def __init__(self, runid):
        self.runid = runid
        self.tmpMenuToggleTable = self.TmpMenuToggleTbl()
        self.tmpMenuToggleTable.removeAll()
        self.tmpMenuToggleTable.create((0,))
        self.tmpMenuToggleRow = self.tmpMenuToggleTable[(0,)]

        if self.runid <> "NULL":
            self.doit()

    def doit(self):
        enable = True
        ldap = "(&(paramname=runid)(paramvalue=%s))" % (self.runid)

        for param in TM.job_parameter.search(ldap):
            ldap2 = "(&(id=%s)(channel=crewmailer))" % (param.job.id)

            for job in TM.job.search(ldap2):
                if job.channel == "crewmailer":
                    enable = False

        self.tmpMenuToggleRow.enable = enable

    class TmpMenuToggleTbl(TempTable):
        def __init__(self):                
            TempTable.__init__(self,
                               "tmp_menu_toggle",
                               [IntColumn("id", "Id")],
                               [BoolColumn("enable", "Enable")]
                               )

# FormatHandler ----------------------------------------------------------{{{2
class FormatHandler:
    def __init__(self):
        self.formatTempTable = self.FormatTempTable()
        # Has to be created last! contains reference to formats
        self.pickFormatTempTable = self.PickFormatTempTable()
        # Refresh their values, this need only to be done once, since all
        # contain static data
        self.formatTempTable.refresh()

    def refresh(self):
        self.pickFormatTempTable.removeAll()
        r_format = self.pickFormatTempTable.create((-1,))
        r_format.format = self.formatTempTable.reference()

    # Inner classes ------------------------------------------------------{{{3
    # FormatTempTable ----------------------------------------------------{{{4
    class FormatTempTable(TempTable):
        """ Static, keeps the names of available export formats.  """
        def __init__(self):
            TempTable.__init__(self,
                name=conf.tmp_salary_format,
                keys=[StringColumn("format", "Export format")]
            )

        def refresh(self):
            log.debug("FormatTempTable().refresh()")
            self.removeAll()
            for f in conf.allowedExportFormats:
                try:
                    self.create((f,))
                except:
                    raise

        def reference(self):
            return self.getOrCreateRef((conf.allowedExportFormats[0],))

    # PickFormatTempTable ------------------------------------------------{{{4
    class PickFormatTempTable(TempTable):
        """ Static, keeps the names of available export formats.  """
        def __init__(self):
            TempTable.__init__(self,
                name=conf.tmp_salary_pick_format,
                keys=[IntColumn("key", "Export format")],
                cols=[RefColumn("format", conf.tmp_salary_format, "Export format")]
            )


# RunIdHandler -----------------------------------------------------------{{{2
class RunIdHandler:
    """
    This class contains definitions of a lot of tables used by the MMI.
    There is one inner class for each temporary table used.
    """
    def __init__(self):
        # Create some temptables!
        self.admCodeTempTable = self.AdmCodeTempTable()
        self.extSysTempTable = self.ExtSysTempTable()
        self.runTypeTempTable = self.RunTypeTempTable()
        # Has to be created last!
        self.runIdTempTable = self.RunIdTempTable()
        # Refresh their values, this need only to be done once, since all
        # contain static data
        self.admCodeTempTable.refresh()
        self.extSysTempTable.refresh()
        self.runTypeTempTable.refresh()

        # First time, fill in with some resonable values
        self.times = api.Times()
        #selector = api.getSelector()
        selector =  ''
        self.runIdTempTable.removeAll()
        self.r_runid = self.runIdTempTable.create((0,))
        self.r_runid.starttime = self.times.now
        self.r_runid.runtype_expl = self.runTypeTempTable.reference()
        self.r_runid.admcode_expl = self.admCodeTempTable.reference()
        self.r_runid.selector = selector[:40]
        self.r_runid.extsys = self.extSysTempTable.reference()
        self.r_runid.firstdate = self.times.month_start
        self.r_runid.lastdate = self.times.month_end

    def refresh(self):
        """ Refresh RunIdTempTable, with next run id """
        self.times.refresh()
        self.r_runid.starttime = self.times.now

    # Inner classes ------------------------------------------------------{{{3
    # AdmCodeTempTable ---------------------------------------------------{{{4
    class AdmCodeTempTable(TempTable):
        """ Static, keeps the admin codes and their descriptions.  """
        def __init__(self):
            TempTable.__init__(self,
                name=conf.tmp_salary_admin_code,
                keys=[StringColumn("description", "Description")],
                cols=[StringColumn("admcode", "Admin Code")]
            )

        def refresh(self):
            self.removeAll()
            # Normal run should be default, set to (N) in case the description changed.
            self.default_keyfield = "(N)"
            for rec in TM.salary_admin_code:
                try:
                    keyfield = "(%s) %s" % (rec.admcode, rec.description)
                    if rec.admcode == "N":
                        self.default_keyfield = keyfield
                    if rec.admcode in ("R", "C"):
                        # [acosta:08/109@09:11] Don't allow "R" or "C" to appear here.
                        # Retros and Cancels will be started by "Cancel Run" or "Retro Run"
                        continue
                    r_admcode = self.create((keyfield,))
                    r_admcode.admcode = rec.admcode
                except:
                    raise

        def reference(self):
            return self.getOrCreateRef((self.default_keyfield,))

    # ExtSysTempTable ----------------------------------------------------{{{4
    class ExtSysTempTable(TempTable):
        """ Static, keeps the names of the salary systems.  """
        def __init__(self):
            TempTable.__init__(self,
                name=conf.tmp_salary_region,
                keys=[StringColumn("extsys", "Salary System")]
            )

        def refresh(self):
            self.removeAll()
            for sys in conf.allowedSalarySystems:
                try:
                    self.create((sys,))
                except:
                    raise

        def reference(self):
            return self.getOrCreateRef((conf.allowedSalarySystems[0],))

    # RunIdTempTable -----------------------------------------------------{{{4
    class RunIdTempTable(TempTable):
        """ This is the main table for the MMI.  """
        def __init__(self):
            TempTable.__init__(self,
                name=conf.tmp_salary_run_id,
                keys=[IntColumn("dummy", "Dummy column")],
                cols=[
                    TimeColumn("starttime", "Run time"),
                    RefColumn("runtype_expl", conf.tmp_salary_run_type, "Run type"),
                    RefColumn("admcode_expl", conf.tmp_salary_admin_code, "Admin code explained"),
                    StringColumn("selector", "Selector"),
                    RefColumn("extsys", conf.tmp_salary_region, "Salary system"),
                    DateColumn("firstdate", "Start of period"),
                    DateColumn("lastdate", "End of period"),
                    StringColumn("note", "Comment"),
                ]
            )

    # RunTypeTempTable ---------------------------------------------------{{{4
    class RunTypeTempTable(TempTable):
        """ Static, stores run types (Per Diem/Overtime) """
        def __init__(self):
            TempTable.__init__(self,
                name=conf.tmp_salary_run_type,
                keys=[StringColumn("dummy", "Dummy column")],
                cols=[
                    StringColumn("description", "Description"),
                    StringColumn("runtype", "Run Type")
                ]
            )

        def refresh(self):
            self.removeAll()
            self.default_keyvalue = conf.runTypeDescription[conf.allowedRunTypes[0]]
            for r in conf.allowedRunTypes:
                try:
                    # This funny work-around is because the XML GUI gives key
                    # fields a different color, so the description is both in a
                    # key field and in an ordinary column.
                    r_runtype = self.create((conf.runTypeDescription[r],))
                    r_runtype.description = conf.runTypeDescription[r]
                    r_runtype.runtype = r
                except:
                    raise

        def reference(self):
            return self.getOrCreateRef((self.default_keyvalue,))


# Handler for the form ==================================================={{{1

# SalaryFormHandler ------------------------------------------------------{{{2
class SalaryFormHandler:
    """Main Form handler

    Initiates form, methods and temporary tables
    """

    def __init__(self):
        """ Create temporary tables, if not already existing.  Also clear and
        refill with data """
        global _messageHandler
        global _runIdHandler
        global _formatHandler

        _messageHandler = MessageHandler()
        _runIdHandler = RunIdHandler()
        _formatHandler = FormatHandler()
        _formatHandler.refresh()
        _runIdHandler.refresh()
        _messageHandler.disable()
        csd.registerService(
            self.doCommand,
            "carmensystems.mirador.tablemanager.doCommand")
        self.DJQ = DigJobQueue(channel=conf.channel, submitter=conf.submitter,
                reportName='report_sources.report_server.rs_SalaryServerInterface')


    def doCommand(self, token, func, runid=None, format=None):
        log.debug("Salary().service(%s, %s, %s, %s)" % (token, func, runid, format))
        """ This function is registered service called from GUI.

        First argument is a handle (not used), func tells us which button the
        user pressed.
        """
        try:
            try:

                if func == 'start_run':
                    # Start a new salary run.
                    TM.refresh()        # XXX
                    for rec in _runIdHandler.runIdTempTable:
                        log.debug("... tmprec = '%s'" % (rec))
                        rd = run.RunData.fromTempRec(rec)
                        # Only the first record should be there
                        break

                    try:
                        # Try to dynamically create module that will be used in the server
                        log.debug("... loading class '%s' from module '%s.%s'" % (rd.extsys, conf.runTypePackage, rd.runtype))
                        module = __import__("%s.%s" % (conf.runTypePackage, rd.runtype), (), (), rd.extsys)
                        c = getattr(module, rd.extsys)
                        del module
                    except:
                        # Inform user that this is not implemented 
                        message("Run type '%s' is not defined for salary system '%s'." % (rd.runtype, rd.extsys))
                        return

                    rd['commands'] = func
                    jobid = self.DJQ.submitJob(rd)
                    message("Job '%d' created - '%s' run for salary system '%s'." % (jobid, rec.runtype_expl.description, rd.extsys))

                elif func == 'start_retro':
                    # Start a retro run (with diffs from a previous run)
                    TM.refresh()        # XXX
                    if runid is None:
                        raise api.SalaryException("Not enough arguments to function '%s'." % (func))

                    jobid = self.DJQ.submitJob({
                        'commands': 'start_retro',
                        'runid': runid
                    })
                    message("Job '%d' created - retro of run with runid '%s'." % (jobid, runid))

                elif func == 'start_export':
                    # Create export file.
                    if runid is None or format is None:
                        raise api.SalaryException("Not enough arguments to function '%s'." % (func,))
                    jobid = self.DJQ.submitJob({
                        'commands': 'start_export',
                        'runid': runid,
                        'format': format,
                    }, reloadModel="1")
                    message("Job '%d' created - export file with format '%s' for runid '%s'." % (jobid, format, runid) )

                elif func == 'start_cancel':
                    # Create new run with all values negated.
                    TM.refresh()        # XXX
                    if runid is None:
                        raise api.SalaryException("Not enough arguments to function '%s'." % (func))
                    jobid = self.DJQ.submitJob({
                        'commands': 'start_cancel',
                        'runid': runid
                    }, reloadModel="1")
                    message("Job '%d' created - cancellation of run with runid '%s'." % (jobid, runid))

                elif func == 'remove_run':
                    # Remove run in all tables
                    TM.refresh()        # XXX
                    if runid is None:
                        raise api.SalaryException("Not enough arguments to function '%s'." % (func))
                    jobid = self.DJQ.submitJob({
                        'commands': 'remove_run',
                        'runid': runid
                    }, reloadModel="1")
                    message("Job '%d' created - Remove run with runid '%s'." % (jobid, runid))

                elif func == 'release_run':
                    # "Release run" -> export the file, and copy it to a "RELEASE" subfolder
                    TM.refresh()        # XXX
                    if runid is None:
                        raise api.SalaryException("Not enough arguments to function '%s'." % (func))
                    rundata = api.getRunIdData(int(runid))

                    jobid = self.DJQ.submitJob({
                        'commands': 'release_run',
                        'runid': runid
                    }, reloadModel="1")
                    message("Job '%d' created - Release run with runid '%s'." % (jobid, runid))

                elif func == 'email_run':
                    TM.refresh()        # XXX
                    if runid is None:
                        raise api.SalaryException("Not enough arguments to function '%s'." % (func))
                    rundata = api.getRunIdData(int(runid))

                    DJQ = DigJobQueue(channel=conf.emailchannel, submitter=conf.submitter, reportName=None)
                    jobid = DJQ.submitJob({
                        'runid': runid,
                        'runtype': rundata.runtype,
                        'extsys': rundata.extsys,
                        'firstdate': rundata.firstdate,
                        'lastdate': rundata.lastdate,
                    }, reloadModel="1")
                    message("Job '%d' created - Email run with runid '%s'." % (jobid, runid))
                    
                elif func == 'get_report':
                    # Create new run with all values negated.
                    if runid is None or format is None:
                        raise api.SalaryException("Not enough arguments to function '%s'." % (func))
                    irunid = int(runid)
                    message("Requesting report for run with runid '%s'." % runid)
                    rundata = api.getRunIdData(irunid)
                    if rundata.runtype == 'PERDIEM' or (rundata.runtype == 'OVERTIME' and rundata.extsys == 'DK') or (rundata.runtype == 'TEMP_CREW' and rundata.extsys == 'SE'):
                        # If it's Per Diem then the report is divided into several PDFs
                        # Link the PDF files, so they will be in the same temporary directory
                        # as the HTML index file.
                        # Overtime also has it's index file pointing to Overtime Statement and
                        # Convertible Crew report (for DK crew only).
                        # Temp Crew for SE crew has an index file pointing to the Temp Crew report and Resource Pool Illness Report. 
                        for file in os.listdir(api.reportDirectory()):
                            if api.reportPrefix(irunid) in file:
                                message("Linking to %s" % file)
                                # files that belong to this run.
                                utils.wave.make_link(os.path.join(api.reportDirectory(), file))
                        return utils.wave.show_document(token, format, api.reportFileName(irunid, ext=".html"))
                    else:
                        # Just show the PDF
                        return utils.wave.show_document(token, format, api.reportFileName(irunid))

                elif func == 'send_balancing':
                    if runid is None:
                        raise api.SalaryException("Not enough arguments to function '%s'." % (func))
                    rundata = api.getRunIdData(int(runid))
                    try:
                        recipient = username()
                    except:
                        message("Cannot extract recipient email address for the balancing report.")
                        return
                    # PROD or PROD_TEST
                    if 'PROD' in os.environ.get('CARMSYSTEMNAME'):
                        recipient += '@sas.dk'
                    jobid = self.DJQ.submitJob({
                        'commands': 'send_balancing',
                        'recipient': recipient,
                        'runid': runid
                    }, reloadModel="1")
                    message("Job '%d' created - Send balancing report for runid '%s' to '%s'." % (jobid, runid, recipient))

                elif func == 'validity_check':
                    if runid is None or format is None:
                        raise api.SalaryException("Not enough arguments to function '%s'." % (func))
                    message("Requesting validity check for run with runid '%s'." % runid)
                    return utils.wave.show_document(token, format, api.reportFileName(int(runid), ext='.pdf',
                                subtype=conf.validity_check_subtype))

                else:
                    raise api.SalaryException("Do not know how to handle the function named '%s'." % (func))

            except api.SalaryException, e:
                message(str(e))
                # Have to re-raise, or the data will be saved...
                raise

            except:
                message(utils.exception.getCause())
                # Have to re-raise, or the data will be saved...
                raise
        finally:
            _runIdHandler.refresh()


# functions =============================================================={{{1

# message ----------------------------------------------------------------{{{2
def message(msg):
    """ For status messages
    """
    _messageHandler.enable(msg)


# initFormTableManager ---------------------------------------------------{{{2
def initFormTableManager(*args):
    """Helps delaying instantiation, of form & tmp tables, until needed.
    """
    global SH
    SH = SalaryFormHandler()


# __main__ ==============================================================={{{1
csd.registerService(
    initFormTableManager,
    "carmensystems.mirador.tablemanager.salary_initiate_tables")

def toggleMailingMenuItem(dummy, runid):
    """ Used to enable or disable the mailing menu entry in the Salary form.
    """
    global MMIH
    MMIH = MailingMenuItemHandler(runid)

csd.registerService(
    toggleMailingMenuItem,
    "carmensystems.mirador.tablemanager.toggleMailingMenuItem")

# setup ------------------------------------------------------------------{{{2
def setup():
    """ Create temporary tables, if not already existing.  Also clear and
    refill with data """
    global _messageHandler
    global _runIdHandler
    global _formatHandler
    _messageHandler = MessageHandler()
    _runIdHandler = RunIdHandler()
    _formatHandler = FormatHandler()
    _formatHandler.refresh()
    _runIdHandler.refresh()
    _messageHandler.disable()


# form -------------------------------------------------------------------{{{2
def form():
    """ This is the 'main' function. """
    import StartTableEditor
    log.debug("form()")
    setup()
    StartTableEditor.StartTableEditor(['-f', '$CARMUSR/data/form/salary.xml'])


# main ==================================================================={{{1
if __name__ == '__main__':
    """ Start form """
    form()


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=2:
# eof
