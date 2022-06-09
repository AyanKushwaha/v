# [acosta:08/092@17:09] Created.
# [acosta:08/095@12:04] Commented out parts that handle "Last Flown" (marked with XXX).

"""
Collect summary info for crew member.

See CR 101
"""

import time

import carmensystems.rave.api as rave

from tm import TM
import carmusr.TimeUtil as TimeUtil
from carmusr.VirtualQualification import virtual_to_real_quals
from utils.dave import EC
import utils.wave
utils.wave.register()

class Rec(dict):
    """Keep a record, with item or attribute access, in case a field contains
    no value - return 'None'."""
    def __init__(self, **k):
        dict.__init__(self, k)

    def __getitem__(self, k):
        try:
            return dict.__getitem__(self, k)
        except:
            return None

    def __getattr__(self, k):
        return self[k]

    def __setattr__(self, k, v):
        if k.startswith('_'):
            # Avoid infinite recursion
            object.__setattr__(self, k, v)
        else:
            self[k] = v

def keyLetterPriority(input):
    # Helper function for sort where letters will get priority over numerals
    # Input is supposed to be a list,
    # where the first element the string to be used for sorting    
    r = []
    for c in input[0]:
        if c.isdigit():
            r.append("z"+c)
        else:
            r.append(c.lower())
    return r

def profile(crewid, nowtime=None):
    """ Return list of profile entries (Rec objects). """
    
    c_ref = TM.crew[(crewid,)]

    if nowtime is None:
        nowtime = utils.wave.get_now_utc(True)

    # Get data
    cont = TM.tmp_cbi_crew_contract
    emp = TM.tmp_cbi_crew_employment    
    subtyp_and_qual = list()
    for q in TM.tmp_cbi_crew_qualification:
        if q.qual.typ == 'ACQUAL':
            subtyp_and_qual.append([q.qual.subtype,q])
    subtyp_and_qual.sort(key=keyLetterPriority)
    qual = [x[1] for x in subtyp_and_qual]
    rest = list()
    for r in TM.tmp_cbi_crew_restriction:
        if r.rest.typ == 'NEW' or r.rest.typ == 'TRAINING':
            rest.append(r)
    acqrest = TM.tmp_cbi_crew_restr_acqual
    acqqual = TM.tmp_cbi_crew_qual_acqual

    # Locate all "interesting dates"
    s = set()

    for x in cont:
        s.add(x.validfrom)
        s.add( TimeUtil.inclTimeToExclTime(x.validto))

    for x in emp:
        s.add(x.validfrom)
        s.add( TimeUtil.inclTimeToExclTime(x.validto))

    for x in qual:
        s.add(x.validfrom)
        s.add( TimeUtil.inclTimeToExclTime(x.validto))

    for x in rest:
        s.add(x.validfrom)
        s.add( TimeUtil.inclTimeToExclTime(x.validto))

    for x in acqrest:
        s.add(x.validfrom)
        s.add( TimeUtil.inclTimeToExclTime(x.validto))
        
    for x in acqqual:
        s.add(x.validfrom)
        s.add( TimeUtil.inclTimeToExclTime(x.validto))

    # Dict of dates in time order
    P = dict([(x, Rec(startdate=x)) for x in sorted(s)])

    # Fill in info from each source
    for x in cont:
        for d in P:
            if x.validfrom <= d and d <= x.validto:
                z = P[d]
                z.contract = "(%s) %s" % (x.contract.contract.descshort, x.contract.contract.id)
                #z.contract = x.contract.contract.descshort + " (%s)" % (x.contract.contract.id)
                z.grouptype = x.contract.contract.grouptype
                z.cyclestart = x.cyclestart
                z.agmtgroup = "%s (%s)" % ( x.contract.contract.agmtgroup.id , x.contract.contract.agmtgroup.si) 

    for x in emp:
        for d in P:
            if x.validfrom <= d and d <= x.validto:
                z = P[d]
                z.titlerank = x.titlerank.id
                z.crewrank = x.crewrank.id
                z.base = x.base.id
                z.station = x.station.id
                z.region = x.region.id
                z.planning_group = x.planning_group.id

    for x in qual:
        if [x.qual.subtype] != virtual_to_real_quals(x.qual.subtype):
            # Ignore virtual quals, e.g. AWB
            continue
        for d in P:
            if x.validfrom <= d and d <= x.validto:
                z = P[d]
                # qual is already sorted, so there is no sorting here.
                if z.qual_1 is None:
                    z.qual_1 = x.qual.subtype
                elif z.qual_2 is None:
                    z.qual_2 = x.qual.subtype
                elif z.qual_3 is None:
                    z.qual_3 = x.qual.subtype
                elif z.qual_4 is None:
                    z.qual_4 = x.qual.subtype
                else:
                    # Crew info supports 4 qualifications 
                    pass

    for x in rest:
        for d in P:
            if x.validfrom <= d and d <= x.validto:
                z = P[d]
                if z.rest_1 is None:
                    z.rest_1 = x.rest.subtype
                else:
                    if z.rest_1 > x.rest.subtype:
                        z.rest_2 = z.rest_1
                        z.rest_1 = x.rest.subtype
                    else:
                        z.rest_2 = x.rest.subtype

    for x in acqrest:
        name = '%s+%s' % (x.acqrestr.typ, x.qual.subtype)
        for d in P:
            if x.validfrom <= d and d <= x.validto:
                z = P[d]
                if z.rest_1 is None:
                    z.rest_1 = name
                else:
                    if z.rest_1 > name:
                        z.rest_2 = z.rest_1
                        z.rest_1 = name
                    else:
                        z.rest_2 = name

    for x in acqqual:
        # SKCMS-1942: Do not present AIRPORT qualificactions
        if x.acqqual.typ == "AIRPORT":
            continue

        for d in P:
            if x.validfrom <= d and d <= x.validto:
                z = P[d]
                for qual_subtype in virtual_to_real_quals(x.qual.subtype):
                    if z.qual_1 is not None and z.qual_1.startswith(qual_subtype):
                        z.qual_1 = '%s+%s' % (z.qual_1, x.acqqual.subtype)
                    elif z.qual_1 is None:
                        pass # z.qual_1 = '??+%s' % x.acqqual.subtype
                    elif z.qual_2 is not None and z.qual_2.startswith(qual_subtype):
                        z.qual_2 = '%s+%s' % (z.qual_2, x.acqqual.subtype)
                    elif z.qual_2 is None:
                        pass # z.qual_2 = '??+%s' % x.acqqual.subtype
                    elif z.qual_3 is not None and z.qual_3.startswith(qual_subtype):
                        z.qual_3 = '%s+%s' % (z.qual_3, x.acqqual.subtype)
                    elif z.qual_3 is None:
                        pass
                    elif z.qual_4 is not None and z.qual_4.startswith(qual_subtype):
                        z.qual_4 = '%s+%s' % (z.qual_4, x.acqqual.subtype)
                    elif z.qual_4 is None:
                        pass

    # This is the list that eventually will be returned
    L = [P[x] for x in sorted(P.keys(), reverse=True)]
    
    # Remove first entry (since it is an end date)
    L.pop(0)
    return L

def run_report(crewid=None):
    """Create PRT report and launch."""
    import Cui
    if crewid is None:
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea), 'OBJECT')
        crewid = rave.eval(rave.selected(rave.Level.atom()), 'crew.%id%')[0]
    Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, Cui.CuiNoArea, 'plan', 'CrewProfile.py', 0, 'CREWID=%s' % crewid)


if __name__ == '__main__':
    """Basic tests."""
    generate_report("10353")
    run_report()

