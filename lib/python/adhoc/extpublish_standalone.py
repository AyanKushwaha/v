import Cui
import os
import dig.extpublishserver as extpublish 

print "------------ Processing crew_ext_publication ----------------"

program = "extpublish"
process = "standalone"

logpath = "${CARMTMP}/logfiles/%s.%s.${USER}.${HOSTNAME}" % (program, process)
logpath = os.path.expandvars(logpath)

print logpath

extpublish.ExtPublishServer(program, process, logpath, False)

Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)






