import Cui
import os
import crewlists.services_archiver as archiver


print "------------ Executing archive_crewlists ----------------"

# Example:
# reports =[("crewlists", "crewlists.crewroster"),
#          ("crewlists", "crewlists.crewlist"),
#          ("crewlists", "crewlists.crewbasic"),
#          ("crewlists", "crewlists.subreports.DUTYCALC"),
#          ("crewlists", "crewlists.subreports.DUTYOVERTIME")]

reports =[("crewlists", "crewlists.subreports.PILOTLOGCREW"),
          ("crewlists", "crewlists.subreports.PILOTLOGFLIGHT")]

first_date = os.environ.get('PERIOD_START','ERROR')

if first_date != "ERROR":
    for (servicetype, servicename) in reports:
        archiver.report(servicetype, servicename, first_date)
else:
    print "Failed to the planning period date"

Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)






