import carmensystems.rave.api as R
from tm import TM
import utils.Names
import Cui

def main():
    now, = R.eval('fundamental.%now%')
    date = now.addyears(1).year_floor()
    
    crewList, = R.eval('sp_crew', R.foreach(
        R.iter('iterators.roster_set',
               where=('crew.%is_cabin%')),
        'crew.%id%',
        'freedays.%%entitled_f36_days_of_lookup_year_2013_mod%%(%s)'% date))

    for (ix, crew, amount) in crewList:
        if amount != 0:
            create_entry(crew, date, amount, now)

    TM.save()
    revid = TM.getSaveRevId()
    print "Saved changes with revid %s" % revid
    Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)


def create_entry(crew, date, amount, now):
    entry = TM.account_entry.create((TM.createUUID(),))
    
    entry.crew = TM.crew[(crew)]
    entry.tim = date
    entry.account = TM.account_set[("F36")]
    entry.source = "Entitled F36 days"
    entry.amount = amount
    entry.man = False
    entry.published = False
    entry.rate = 100
    entry.reasoncode = "IN Entitlement"
    entry.entrytime = now
    entry.username = utils.Names.username()


main()
