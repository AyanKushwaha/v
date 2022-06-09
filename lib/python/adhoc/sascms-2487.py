

"""
SASCMS-2487

Restore removals from earlier 'account_entry' revision, accumulation job went
ape.
"""

import adhoc.fixrunner as fixrunner
import utils.dt as dt


revid = 23337690


#def print_out_changes(dc, revid):
#    fmt = '%(crew)-5.5s %(account)-9.9s %(tim_)16.16s %(amount)7.7s %(username)-5.5s %(entrytime_)16.16s'
#    change_set = {}
#    for entry in fixrunner.dbsearch(dc, 'account_entry', 'revid > %d' % revid):
#        change_set[(entry['crew'], entry['entrytime'], entry['id'])] = entry
#
#    if change_set:
#        s =  "These crew and accounts have been changed since accumulation"
#        print '=' * len(s)
#        print s
#        print '=' * len(s)
#        print
#        print fmt % dict(crew='crew', account='account', tim_='tim',
#                amount='amount', username='username', entrytime_='entrytime')
#        print fmt % dict(crew=5 * '=', account=9 * '=', tim_=5 * '=', amount=7 * '=', 
#                username=5 * '=', entrytime_=16 * '=') 
#        for key in sorted(change_set):
#            entry = change_set[key]
#            entry['tim_'] = dt.m2dt(entry['tim']).strftime('%Y-%d-%m %H:%M')
#            entry['entrytime_'] = dt.m2dt(entry['entrytime']).strftime('%Y-%d-%m %H:%M')
#            print fmt % entry


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    #print_out_changes(dc, revid)
    return fixrunner.backout(dc, revid)


if __name__ == '__main__':
    fixit()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
