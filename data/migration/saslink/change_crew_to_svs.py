"""
SKCMS-2778: Change some existing crew to Link crew for testing
Note you need to update crew_user_filter for these crew to show up
"""
import datetime
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime


__version__ = '2022-01-21'


filepath = os.path.expandvars('$CARMUSR')
directory = filepath+'/data/migration/saslink/'

def val_date(date_str):
    return int(AbsTime(date_str))/24/60

birthday = val_date("23Feb1985")
employment = int(AbsTime("01Dec2021"))
valid_to = int(AbsTime("31Dec2035"))
today = int(AbsTime(str(datetime.datetime.now().strftime("%d%b%Y"))))


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()

    ranks = {'FC': 5, 'FP': 5, 'AP': 5, 'AH': 15}

    for rank, amount in ranks.items():
        print("Looking for %s crew to modify" % rank)
        for ce_entry in fixrunner.dbsearch(dc, 'crew_employment', "crewrank='%s' AND validto>%i" % (rank, today))[:amount]:
            crew = ce_entry['crew']
            print("Processing crew %s", crew)
            ce_entry['carrier'] = 'SVS'
            ce_entry['company'] = 'SVS'
            ce_entry['base'] = 'CPH'
            ce_entry['region'] = 'SVS'
            ce_entry['station'] = 'CPH'
            ce_entry['civicstation'] = 'CPH'
            ce_entry['country'] = 'DK'
            ce_entry['planning_group'] = 'SVS'
            ops.append(fixrunner.createop('crew_employment', 'U', ce_entry))

            for cc_entry in fixrunner.dbsearch(dc, 'crew_contract', "crew='%s' and validto>%i" % (crew, today)):
                print("Processing crew contract for %s", crew)
                cc_entry['contract'] = 'V0001'
                ops.append(fixrunner.createop('crew_contract', 'U', cc_entry))
            
            for cq_entry in fixrunner.dbsearch(dc, 'crew_qualification', "crew='%s' and qual_typ='ACQUAL' and validto>%i" % (crew, today)):
                print("Processing crew qualification for %s", crew)
                #Create the new row to be inserted
                new = {'crew' : crew,
                   'qual_typ' : 'ACQUAL',
                   'qual_subtype' : 'EJ',
                   'validfrom' : cq_entry['validfrom'],
                   'validto' : cq_entry['validto']}
                
                try:
                    #remove new row if already exists
                    ops.append(fixrunner.createop('crew_qualification', 'D', new))
                
                except RuntimeError:
                    print ("record not existing")

                
                ops.append(fixrunner.createop('crew_qualification', 'N', new ))
            #break
    return ops



fixit.program = 'change_crew_to_sl.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
