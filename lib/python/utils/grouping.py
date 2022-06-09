

"""
Functions that split and shuffle data into manageable groups.
"""

# [acosta:10/106@15:13] NOTE: This function does not import anything, let's
# keep it that way! Core Python modules are perfectly alright, but not Cui,
# Cfh, rave, etc.

default_diff = lambda a, b: abs(cmp(a, b))


def split_groups(data, group_size, max_deviation=0, smartdiff=default_diff):
    """Split at list (of tuples, but not necessarily) into a list of lists
    where each group is 'group_size' big. The parameter 'max_deviation' tells
    how much the list is allowed to differ from 'group_size'. If the
    'smartdiff' function is made correctly, we should be able to create groups
    that have a better composition."""
    llo = group_size - max_deviation
    lhi = group_size + max_deviation
    if len(data) <= lhi:
        return [data]
    # Output data, list of lists
    odata = []
    # Current sublist
    sublist = []
    # Buffer used when number of elements is getting critical
    buffer = []
    i = 0
    for element in sorted(data):
        if llo <= i <= lhi:
            buffer.append(element)
        elif i > lhi:
            buffer.append(element)
            p1, p2 = split_buffer(buffer, smartdiff)
            sublist.extend(p1)
            odata.append(sublist)
            sublist = p2
            buffer = []
            i = 0
            continue
        else:
            sublist.append(element)
        i += 1
    if buffer:
        sublist.extend(buffer)
    if sublist:
        odata.append(sublist)
    return odata


def split_buffer(l, smartdiff=default_diff):
    """Split buffer into two parts using the 'smartdiff' function.
    This function should return a number, the greater this number
    is, the more "unequal" the two values.
    NOTE: The list 'l' has to be sorted!
    """
    diffs = []
    for i in xrange(len(l)):
        if i != 0:
            # Sort by (1) smartdiff, (2) distance from mid point
            diffs.append((smartdiff(l[i-1], l[i]), i))
    diffs.sort()
    bp = diffs[-1][-1]
    return l[:bp], l[bp:]


def n_level_diff(a, b):
    """Compare two n-tuples, return 0 if they are equal, otherwise
    return a number which is the order of the level that differs.
    Example:
    n_level_diff((1, 2, 3), (0, 1, 2)) => 3
    n_level_diff((1, 2, 3), (1, 3, 2)) => 2
    n_level_diff((1, 2, 3), (1, 2, 2)) => 1
    n_level_diff((1, 2, 3), (1, 2, 3)) => 0
    """
    if isinstance(a, (tuple, list)) and isinstance(b, (tuple, list)):
        z = zip(a, b)
        zlen = len(z)
        for i in xrange(zlen):
            if cmp(z[i][0], z[i][1]):
                return zlen - i
    return abs(cmp(a, b))


def seq2map(iterable):
    """Transform a sequence of tuples into a mapping: for instance:
    [(1, 2, 3), (1, 3, 1), (2, 1, 1), (2, 2, 1), (2, 2, 3)]
    ... becomes ..
    {1: {2: {3: {}}, 3: {1: {}}}, 2: {1: {1: {}}, 2: {1: {}, 3: {}}}}
    """
    def _seq2map(seq, mm):
        if len(seq) > 1:
            mm[seq[0]] = _seq2map(seq[1:], mm.get(seq[0], {}))
        else:
            mm[seq[0]] = {}
        return mm
    M = {}
    for t in iterable:
        if isinstance(t, (tuple, list)):
            M.update(_seq2map(t, M))
        else:
            M[t] = {}
    return M


def map2seq(mm, tuples=False):
    """Transform a mapping into a list of tuples or a list of lists.
    {1: {2: {3: {}}, 3: {1: {}}}, 2: {1: {1: {}}, 2: {1: {}, 3: {}}}}
    ... becomes ..
    [(1, 2, 3), (1, 3, 1), (2, 1, 1), (2, 2, 1), (2, 2, 3)]
    ... or (depending on argument 'tuples') ...
    [[1, 2, 3], [1, 3, 1], [2, 1, 1], [2, 2, 1], [2, 2, 3]]
    """
    if tuples:
        f = tuple
    else:
        f = list
    def _map2seq(m, p, l):
        for k in m:
            if m[k]:
                _map2seq(m[k], p + [k], l)
            else:
                l.append(f(p + [k]))
        return l
    return _map2seq(mm, [], [])


if __name__ == '__main__':
    # place for built-in tests
    pass


# example ================================================================{{{1
##     from utils.rave import RaveIterator
##     ri = RaveIterator('iterators.roster_set', 
##         {
##             'base': 'crew.%homebase%', 
##             'cat': 'crew.%main_func%',
##             'id': 'crew.%id%',
##             'sn': 'crew.%surname%',
##             'name': 'crew.%login_name%'
##         })
##     crewlist = []
##     for c in ri.eval('sp_crew'):
##         crewlist.append((c.cat, c.base, c.sn[:1], c.sn, c.name, c.id))
##     if len(crewlist) < 500:
##         print "--- ALL CREW IN ONE ---"
##         for cat, base, a, sn, name, id in sorted(crewlists):
##             print cat, base, id, name
##         print "--- ALL CREW IN ONE ---"
##     else:
##         print "--- SPLITTING INTO CAT/BASE ---"
##         crewmap = seq2map(crewlist)
##         for cat in sorted(crewmap):
##             for base in sorted(crewmap[cat]):
##                 stuff = map2seq(crewmap[cat][base])
##                 stuff.sort()
##                 if len(stuff) > 500:
##                     print "--- %s/%s too large splitting" % (cat, base)
##                     for group in split_groups(stuff, 400, 300, n_level_diff):
##                         print "--- GROUP START --- %s - %s" % (group[0][0], group[-1][0])
##                         for a, sn, name, id in group:
##                             print cat, base, id, name
##                         print "--- GROUP END ---"
##                 else:
##                     print "--- %s/%s in one piece" % (cat, base)
##                     for (a, sn, name, id) in stuff:
##                         print cat, base, id, name

# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
