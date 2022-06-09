

"""
SASCMS-1540

This script will update the accumulator accumulators.half_freeday_acc
This accumulator is supposed to return a odd number when crew have a half freeday to take out
and an even when crew have not.

The migration instructions however speciefed 1 and 0 instead of odd and even, which means that all migrated
data violates a fundamental assumption of this accumulator, that it is only increasing in value. Switches from
1 to 0 means that it decreased and "-1" will be interpreted in terms of "odd" and "even"

This script will detect such changes and switch the change from negative to positive. 
"""

import fixrunner


__version__ = '$Revision$'


class Crew(object):
    def __init__(self):
        self._entries = []

    def add(self, entry):
        self._entries.append(entry)

    def sort(self):
        entr_list = [(e.tim, e) for e in self._entries]
        entr_list.sort()
        self._entries = [e for (_,e) in entr_list]

    def fix_chain(self):
        self.sort()
        curr_val = -99
        for i,e in enumerate(self._entries):
#            print "i:", i, " curr_val:", curr_val, " e.val:", e.val, " acckey:", e.acckey
            if e.val < curr_val:
                # we jumped down, increase this and all remaining!
                self._increase_chain(self._entries[i:])
            curr_val = e.val

    def _increase_chain(self, entries):
        for e in entries:
            e.increase()

    def is_modified(self):
        return len(self.modified_records()) != 0

    def modified_records(self):
        return [e.to_rec() for e in self._entries if e.is_modified()]


class Entry(object):
    def __init__(self, db_entry):
        self.name = db_entry['name']
        self.acckey = db_entry['acckey']
        self.tim = db_entry['tim']
        self.val = db_entry['val']
        self._modified = False

    def is_modified(self):
        return self._modified

    def to_rec(self):
        return {'name':self.name,
                'acckey':self.acckey,
                'tim':self.tim,
                'val':self.val}

    def increase(self):
        self.val += 2
        self._modified = True


@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    crew_cache = {}
    for entry in fixrunner.dbsearch(dc, 'accumulator_int', "name='accumulators.half_freeday_acc'"):
        try:
            crew_cache[entry['acckey']].add(Entry(entry))
        except KeyError:
            crew = Crew()
            crew.add(Entry(entry))
            crew_cache[entry['acckey']] = crew

    for crew in crew_cache.values():
        crew.fix_chain()
        if crew.is_modified():
            for modified_rec in crew.modified_records():
                ops.append(fixrunner.createOp('accumulator_int', 'W', modified_rec))
##                 print "modified rec:", modified_rec
##         print "printing final status"
##         for rec in crew._entries:
##             print rec.to_rec()
##     print "Will perform %s operations" % (len(ops))
##     return []
    return ops



fixit.remark = 'SASCMS-1540 (%s)' % __version__


if __name__ == '__main__':
    fixit()
