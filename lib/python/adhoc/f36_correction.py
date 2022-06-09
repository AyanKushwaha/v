from tm import TM
import carmensystems.rave.api as R
import utils.Names
import Cui

def main():
    create_entitlement_corrections()
    create_reductions_corrections()

    TM.save()
    revid = TM.getSaveRevId()
    print "Saved changes with revid %s" % revid
    Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)


def create_entitlement_corrections():
    now, = R.eval('fundamental.%now%')
    date = now.day_floor()
    
    crewList, = R.eval('sp_crew', R.foreach(
        R.iter('iterators.roster_set',
               where=('crew.%is_cabin%')),
        'crew.%id%',
        'freedays.%%entitled_f36_days_corr%%(%s)'% now))

    for (ix, crew, amount) in crewList:
        if amount != 0:
            create_entry(crew, date, amount, now, "Entitled F36 days CORR")


def create_reductions_corrections():
    now, = R.eval('fundamental.%now%')
    nowdate = now.day_floor()
    pp_start, = R.eval('fundamental.%pp_start%')
    date = now.addyears(1).year_floor()

    intervals = [(now.year_floor(),now.year_floor().addmonths(3)),
                 (now.year_floor().addmonths(3),now.year_floor().addmonths(6)),
                 (now.year_floor().addmonths(6),now.year_floor().addmonths(9)),
                 (now.year_floor().addmonths(9),date)]

    for ivalstart, ivalend in intervals:
        if ivalstart < pp_start:
            continue
        
        src, = R.eval('freedays.%%reduction_source%%(%s)'% ivalstart)
        crewList, = R.eval('sp_crew', R.foreach(
            R.iter('iterators.roster_set',
                   where=('crew.%is_cabin%')),
            'crew.%id%',
            'freedays.%%f36_reduction_corr_diff%%(%s,%s)'% (ivalstart,ivalend)))
        
        for (ix, crew, amount) in crewList:
            if amount != 0:
                create_entry(crew, nowdate, amount, now, src)
    

def create_entry(crew, date, amount, now, src):
    entry = TM.account_entry.create((TM.createUUID(),))
    
    entry.crew = TM.crew[(crew)]
    entry.tim = date
    entry.account = TM.account_set[("F36")]
    entry.source = src
    entry.amount = amount
    entry.man = False
    entry.published = False
    entry.rate = (100, -100)[amount < 0]
    entry.reasoncode = ('IN Correction', 'OUT Correction')[amount < 0]
    entry.entrytime = now
    entry.username = utils.Names.username()


main()
