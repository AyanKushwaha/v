import adhoc.fixrunner as fixrunner
import os
import json
from pprint import pprint
from AbsTime import AbsTime
from AbsDate import AbsDate

#  __version__ = '$Revision$'
__version__ = 'SKSD-7153_01'


def convertDates(table_name, row):
    for key in row:
        if key in ["validto", "validfrom"]:
            #  print "row[%s]: %s" % (key, row[key])
            if table_name in ["crew_extra_info"]:
                row[key] = int(AbsTime(str(row[key]))) / 24 / 60
            else:
                row[key] = int(AbsTime(str(row[key])))
        elif key in ["birthday", "employmentdate"]:
            #  print "row[%s]: %s" % (key, row[key])
            row[key] = int(AbsTime(str(row[key]))) / 24 / 60
    return row

def addRow(ops, table_name, row):
    row = convertDates(table_name, row)
    ops.append(fixrunner.createOp(table_name, 'W', row))

crew_tables = [
"crew",
"crew_employment",
"crew_contract",
"crew_qualification",
"crew_contact",
"crew_extra_info",
"crew_relatives",
"crew_address"
]

#  @fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    carmusr_path = os.getenv("CARMUSR")
    print "carmusr path is: ", carmusr_path
    crewlists = json.loads(open(carmusr_path + "/data/migration/add_crew_ccd/crewlist.json").read())
    pprint(crewlists)


    #print "starting"
    dic = {}
    ops = []

    count=0
    #print "Birthday: ",crewlists["crewlist"][0]["crew"]["birthday"]
    for crew in crewlists["crewlist"]:
        for table in crew_tables:
	    #  pprint(crew[table])
	    for row in crew[table]:
		#  print table
		#  pprint(row)
		#  print "########################################"
		addRow(ops, table, row)
	    #  pprint(crew[table])
	    #  print "########################################"
            #  addRow(ops, table, crew[table])

    print "done,updates=",len(ops)
    return ops


fixit.program = 'add_crew.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


