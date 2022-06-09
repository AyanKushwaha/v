
# [acosta:07/169@10:05] First version.
# [acosta:07/345@01:27] Removed raising of exception, faults lead to no change.

"""
Conversion to and from SAS duty codes.

These codes are handled:
    'P', 'PP', 'DD', 'D' (passive/deadhead)
    'L', 'LL', 'H', 'HH' (anywhere in dutycode)
    'U' (anywhere in dutycode)
"""

# Improvement?: This module needs to be revised now when we know more about duty codes. [acosta:09/113@15:08] 


import re

fc_pos = ['FR', 'FP', 'FC']
cc_pos = ['AH', 'AS', 'AP']

# NOTE: Don't just change the lists above without checking that all tests in 
# ../tests/utils/test_dutycd.py still work!

above_below = ['LL', 'L', '', 'H', 'HH']


def dutycd2pos(rank, dutycd):
    """ Convert from SAS duty code to 'pos' in 'crew_flight_duty'. """
    # No change
    if dutycd == '':
        return rank2pos(rank)
    
    # Passive/dead head
    elif dutycd in ('P', 'PP', 'D', 'DD'):
        return 'DH'

    # Supernumerary, 'U' can be anywhere in the duty code.
    elif 'U' in dutycd:
        if rank.startswith('F'):
            return 'FU'
        else:
            return 'AU'

    # Above or below rank (training codes are discarded)
    hilo = re.compile(r'[^L]*(L[L]?)[^L]*|[^H]*(^H[H]?)[^H]*')
    m = hilo.match(dutycd)
    if not m is None:
        if m.group(1) is None:
            dc = m.group(2)
        else:
            dc = m.group(1)
        if rank in fc_pos:
            pos = fc_pos
        elif rank in cc_pos:
            pos = cc_pos
        else:
            return rank2pos(rank)

        ix = pos.index(rank)
        change = above_below.index(dc) - above_below.index('')

        # Special case, AH with dutycode H becomes AP
        if pos[ix] == 'AH' and change > 0:
            return 'AP'
        # AP flying lower will become AH not AS
        if pos[ix] == 'AP' and change < 0:
            return 'AH'

        ix += change
        ix = min(ix, len(pos) - 1)
        ix = max(ix, 0)
        return pos[ix]

    return rank2pos(rank)


def pos2dutycd(rank, pos):
    """ Convert from 'pos' in 'crew_flight_duty' to SAS duty code. """
    if rank == pos:
        return ''

    elif pos == 'DH':
        return 'P'  # or 'D' ??

    elif pos in ('AU', 'FU'):
        return 'U'

    elif pos in fc_pos or pos in cc_pos:
        if rank == 'AH' and pos == 'AP':
            # special case
            return 'H'
        #if rank == 'AP' and pos == 'AH':
        #    # special case
        #    return 'L'
        if pos in fc_pos:
            p = fc_pos
        else:
            p = cc_pos
        d = p.index(pos) - p.index(rank) + above_below.index('')
        d = min(d, len(above_below) - 1)
        d = max(d, 0)
        return above_below[d]

    else:
        pass

    return ''


def rank2pos(rank):
    """Make sure that only valid positions will be returned. 'FO' is not a
    position."""
    if rank == 'FA':
        # New flight deck crew
        return 'FP'
    if rank == 'AA':
        # New cabin crew
        return 'AH'
    if rank.startswith('F') and rank not in ('FC', 'FP', 'FR'):
        # takes care of FE, FS, FO
        return 'FU'
    if rank.startswith('A') and rank not in ('AP', 'AS', 'AH'):
        # takes care of possible new ranks
        return 'AU'
    return rank


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
