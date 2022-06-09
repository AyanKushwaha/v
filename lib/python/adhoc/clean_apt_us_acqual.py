import re
import sys
from AbsTime import AbsTime
import datetime

def to_dict(s):
    d = {}
    for pair in s.split(', '):
        k, v = pair.split(': ')
        try:
            d[eval(k)] = eval(v)
        except:
            d[eval(k)] = AbsTime(v)

    return d

def main():
    if len(sys.argv) != 2:
        print "Specify the name of the db sanity log file to parse"
    else:
        nowdt = datetime.datetime.now()
        now = AbsTime(nowdt.year, nowdt.month, nowdt.day, nowdt.hour, nowdt.minute)
        regexp1 = re.compile('^Overlap in crew_qual_acqual: {(.*)} with other period: {(.*)}$')
        keys = set()
        with open(sys.argv[1]) as fp:
            for line in fp:
                match = regexp1.match(line)
                if match != None:
                    o1 = to_dict(match.group(1))
                    o2 = to_dict(match.group(2))
                    if o1['acqqual_typ'] == 'AIRPORT' and o1['acqqual_subtype'] == 'US':
                        if o1['validto'] > now and o2['validto'] > now:
                            if o1['validto'] > o2['validto']:
                                validfrom = o1['validfrom']
                            elif o2['validto'] > o1['validto']:
                                validfrom = o2['validfrom']
                            elif o2['validfrom'] > o1['validfrom']:
                                validfrom = o2['validfrom']
                            else:
                                validfrom = o1['validfrom']
                            keys.add((o1['crew'], o1['qual_subtype'], o1['acqqual_subtype'], validfrom))
        rows = []
        for crew, q_subtype, acq_subtype, validfrom in keys:
            rows.append("(&(crew=%s)(qual.subtype=%s)(acqqual.subtype=%s)(validfrom=%s))" % (crew, q_subtype, acq_subtype, validfrom))
        print "(|%s)" % ''.join(rows)
                    

if __name__ == '__main__':
    main()
