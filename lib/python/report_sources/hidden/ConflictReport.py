
#
# Wrapper script to avoid link to the carmsys script
# (Refer to:
#  http://honolulu.carmen.se/wiki/index.php/Studio/Customization#Conflict_Handling)
# acosta: 2008-02-01
#
try:
    from carmensystems.studio.plans.ConflictReport import *
except:
    from carmensystems.studio.plans.private.ConflictReport import *

#ConflictReport = C.ConflictReport
#createReport = C.createReport
