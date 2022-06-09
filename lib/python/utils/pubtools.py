

"""
Utilities for roster publication - to be used in those cases
Cui.CuiPublishRosters(...) can't do the job, for instance when publishing based
on already published data in the Report Server.
"""

# imports ================================================================{{{1
from tm import TM
import utils.time_util as time_util
from modelserver import EntityNotFoundError


# classes ================================================================{{{1

# OverlapGroup -----------------------------------------------------------{{{2
class OverlapGroup(list):
    """Group of activities that mutually overlap each other."""
    def __init__(self, interval):
        list.__init__(self)
        self.interval = interval


# Handler ----------------------------------------------------------------{{{2
class Handler:
    """Methods that are not dependent on implementation."""

    # The lower the better
    winner, loser = (0, 1)

    def superimpose(self, higher, lower):
        L = [self.NonAdjustable(x) for x in higher]
        L.extend([self.Adjustable(x) for x in lower])
        return self.resolve_overlaps(L)

    def resolve_overlaps(self, iterable):
        ops = []
        iset = time_util.IntervalSet()
        for obj in iterable:
            iset.add(time_util.TimeInterval(obj.interval.first, obj.interval.last))
        # Merge adjacent intervals
        iset.merge()
        # Populate list of overlap group objects.
        ogs = []
        for interval in iset:
            ogs.append(OverlapGroup(interval))

        for obj in iterable:
            for og in ogs:
                if obj.interval.overlaps(og.interval):
                    og.append(obj)
        # Resolve each overlap group individually.
        for og in ogs:
            self.resolve_group(og)
            for obj in og:
                ops.extend(obj.finalize())
        return ops

    def resolve_group(self, og):
        """Resolve overlaps within an overlap group containing overlapping
        trips/legs."""
        # sort group ordered by dignity
        og.sort()

        # Compare items within group
        for i in xrange(len(og)):
            if og[i].is_discarded():
                continue
            for j in xrange(i + 1, len(og)):
                if og[j].is_discarded():
                    continue
                if og[i].interval.overlaps(og[j].interval):
                    try:
                        og[j].adjust(og[i].interval)
                    except AttributeError:
                        # Not adjustable, the method adjust() is not there, so discard.
                        og[j].discard()


# HandlerTM --------------------------------------------------------------{{{2
class HandlerTM(Handler):
    """TableManager implementation of Handler."""
    def copy_tags(self, crew, start, end, from_pubtype, to_pubtypes=()):
        """Copy records published with 'old_tag' to records with tag
        'new_tag'."""
        f_recs = []
        t_recs = {}
        min_start = max_end = None
        all_records = list(self.records(crew))
        for rec in all_records:
            if rec.pubtype.id == from_pubtype and rec.pubstart < end and start < rec.pubend:
                if min_start is None:
                    min_start = rec.pubstart
                else:
                    min_start = min(min_start, rec.pubstart)
                if max_end is None:
                    max_end = rec.pubend
                else:
                    max_end = max(max_end, rec.pubend)
                f_recs.append(rec)

        if min_start is None or max_end is None:
            return

        for rec in all_records:
            if min_start < rec.pubend and rec.pubstart < max_end:
                if rec.pubtype.id in to_pubtypes:
                    if rec.pubtype.id in t_recs:
                        t_recs[rec.pubtype.id].append(rec)
                    else:
                        t_recs[rec.pubtype.id] = [rec]

        for to_pubtype in to_pubtypes:
            new_recs = [self.DummyRecord(rec, to_pubtype) for rec in f_recs]
            if to_pubtype in t_recs:
                self.superimpose(new_recs, t_recs[to_pubtype])
            # Delay creation of objects to avoid index clashes.
            for rec in new_recs:
                rec.do_create()

    def records(self, crew):
        return TM.crew[(crew,)].referers('published_roster', 'crew')

    # DummyRecord --------------------------------------------------------{{{3
    class DummyRecord:
        """We cannot create any new records until everything is cleaned up.
        (Because of risk that TM.published_roster.create() will fail.)"""
        def __init__(self, rec, to_pubtype):
            self.crew = rec.crew
            self.pubstart = rec.pubstart
            self.pubtype = TM.publication_type_set[(to_pubtype,)]
            self.pubend = rec.pubend
            self.pubcid = rec.pubcid
            self.si = "pubtools.py"
            self.rec = rec

        def __str__(self):
            return str(self.rec)

        def do_create(self):
            try:
                new_rec = TM.published_roster[(self.pubstart, self.crew,
                    self.pubtype)]
                print "pubtools.DummyRecord: ERROR: multiple entries!", self, self.pubtype.id
            except EntityNotFoundError:
                new_rec = TM.published_roster.create((self.pubstart, self.crew,
                    self.pubtype))
            new_rec.pubcid = self.pubcid
            new_rec.pubend = self.pubend
            new_rec.si = self.si
            return new_rec

    # NonAdjustable ------------------------------------------------------{{{3
    class NonAdjustable(tuple):
        def __new__(cls, rec):
            return tuple.__new__(cls, (Handler.winner, -rec.pubcid,
                rec.pubstart))

        def __init__(self, rec):
            self.rec = rec
            self.interval = time_util.TimeInterval(rec.pubstart, rec.pubend)

        def is_discarded(self):
            return False

        def finalize(self):
            return []

    # Adjustable ---------------------------------------------------------{{{3
    class Adjustable(tuple):
        def __new__(cls, rec):
            return tuple.__new__(cls, (Handler.loser, -rec.pubcid,
                rec.pubstart))

        def __init__(self, rec):
            self.rec = rec
            self.interval = time_util.TimeInterval(rec.pubstart, rec.pubend)
            self._discarded = False
            self.cut_off_set = time_util.IntervalSet()
            self.keep = False

        def discard(self):
            self._discarded = True

        def is_discarded(self):
            return self._discarded

        def finalize(self):
            ops = []
            if self.is_discarded():
                self.rec.remove()
                return []
            if self.cut_off_set:
                self.cut_off_set.complement(self.interval)
                for portion in self.cut_off_set:
                    ops.extend(self.create(portion))
                if not self.keep:
                    self.rec.remove()
            return ops

        def adjust(self, other):
            """other is "better", so we adjust ourselves."""
            self.cut_off_set.add(other)

        def create(self, interval):
            if interval.first == self.interval.first:
                self.rec.pubend = interval.last
                self.keep = True
                return [self]
            else:
                try:
                    newrec = TM.published_roster[(interval.first,
                                                  self.rec.crew, self.rec.pubtype)]
                    print "pubtools.Adjustable: ERROR: multiple entries!", self, self.rec.pubtype.id
                except EntityNotFoundError:
                    newrec = TM.published_roster.create((interval.first,
                                                         self.rec.crew, self.rec.pubtype))
                newrec.pubend = interval.last
                newrec.pubcid = self.rec.pubcid
                newrec.si = self.rec.si
            return [self.__class__(newrec)]


# HandlerDIG -------------------------------------------------------------{{{2
class HandlerDIG(Handler):
    """Improvement? - could be nice to have (in the future)"""
    pass


# entity_handler ========================================================={{{1
entity_handler = HandlerTM()


# copy_tags =============================================================={{{1
copy_tags = entity_handler.copy_tags
    

# __main__ ==============================================================={{{1
if __name__ == '__main__':
    # Basic tests have been moved to ../tests/utils/test_pubtools.py
    pass


# Example ================================================================{{{1
# copy_tags('87970', AbsTime(2005, 6, 21, 22, 0), AbsTime(2005, 6, 30, 22, 0), 
#            'PUBLISHED', ('INFORMED', 'DELIVERED'))

# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
