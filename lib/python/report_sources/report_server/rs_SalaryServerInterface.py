"""
This is the server interface for Salary stand alone application.

This is part of a client server solution for SAS salary calculations.
Client:     Wave form directly on mirador (table editor)
Middleware: DIG
Server:     Report server that calls this module.
"""

import salary.run as run
import salary.api as api
import logging

from report_sources.report_server.rs_if import argfix, add_reportprefix
from tm import TM

log = logging.getLogger('salary.SalaryServerInterface')


@argfix
@add_reportprefix
def generate(*a, **d):
    """
    Entry point for the report server
    Delegates processing according to param and returns result.
    
    The dictionary containing the inparameters must follow this:
     'commands':    A ;-separated string of commands, se details below.
     'runid':       Used as inparam for 'CreateForecasts' & 'CreateReports' Commands
    
    The commands should be one of: ('start_run', 'start_retro', 'start_export',
                                    'start_cancel', 'remove_run', 'release_run')
    """

    try:
        # For some strange reason table manager might be locked. 
        if TM.islocked():
            TM.unlock()
    
        # This flag tells DIG if model changes made by report should be saved to db.
        reports = []
        writeReportWorkerDeltaToDb = True
        
        log.debug("inparams = %s" % d)
    
        if 'commands' in d:
            # Clean leading and trailing spaces & semicolons
            commandsStr = d['commands'].strip(' ;')
            commands = commandsStr.split(';')
        else:
            raise api.SalaryException("Parameter 'commands' empty! Nothing to do!")
    
        if 'start_run' in commands:
            rd = run.RunData(**d)
            log.info("FIRSTDATE: %s" % rd.firstdate)
            log.info("LASTDATE: %s" % rd.lastdate)
            runid = run.run(rd)
            log.info("Run with runid '%d' created." % runid)
    
        elif 'start_export' in commands:
            writeReportWorkerDeltaToDb = False
            if 'runid' in d and 'format' in d:
                runid = d['runid']
                format = d['format']
            else:
                raise api.SalaryException("Command 'start_export' is missing parameters 'runid' and/or 'format'.")
            rd = run.RunData.fromRunId(runid)
            rd.exportformat = format
            filename = run.export(rd)
            log.info("File with name '%s' was exported." % filename)
            
        elif 'start_cancel' in commands:
            if 'runid' in d:
                runid = d['runid']
            else:
                raise api.SalaryException("Command start_cancel is missing parameter 'runid'.")
            new_runid = run.create_and_negate(run.RunData.fromRunId(runid))
            log.info("Cancellation run with id '%d' created." % new_runid)
    
        elif 'start_retro' in commands:
            if 'runid' in d:
                runid = d['runid']
            else:
                raise api.SalaryException("Command start_retro is missing parameter 'runid'.")
            new_runid = run.retro_run(run.RunData.fromRunId(runid))
            log.info("Retro run with id '%d' created." % new_runid)
            
        elif 'remove_run' in commands:
            if 'runid' in d:
                runid = d['runid']
            else:
                raise api.SalaryException("Command remove_run is missing parameter 'runid'.")
            rd = run.RunData.fromRunId(runid)
            api.zap(rd.runid)
            log.info("Run with id '%d' was removed." % rd.runid)
    
        elif 'release_run' in commands:
            if 'runid' in d:
                runid = d['runid']
            else:
                raise api.SalaryException("Command release_run is missing parameter 'runid'.")
            (reports, writeReportWorkerDeltaToDb) = run.release(run.RunData.fromRunId(runid))
            log.info("Run with id '%s' was released." % runid)
        
        elif 'send_balancing' in commands:
            writeReportWorkerDeltaToDb = False
            try:
                runid = d['runid']
            except:
                raise api.SalaryException("Command send_balancing is missing parameter 'runid'.")
            try:
                recipient = d['recipient']
            except:
                raise api.SalaryException("Command send_balancing is missing parameter 'recipient'.")
            reports = run.send_balancing(run.RunData.fromRunId(runid), recipient)
            log.info("A balancing report for runid '%s' was sent." % runid)
    
        else:
            raise api.SalaryException("Parameter 'commands' had an invalid value %s." % (commands,))
        
        return (reports, writeReportWorkerDeltaToDb)
    except:
        import traceback
        print "ERROR in rs_SalaryServerInterface"
        traceback.print_exc()
        print "END OF ERROR in rs_SalaryServerInterface"
        raise
