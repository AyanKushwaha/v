

"""
Small script that locates crew with birth countries that are not legal and
tries to correct this.

NB! The script does not take care of empty BCOUNTRY in table crew.

See SKU-3864.
"""

import fixrunner


# Some cases where we now the remedy.
country_map = {
    'BEL': 'BE',
    'DEU': 'DE',
    'N0': 'NO',
    'no': 'NO',
    'RA': 'AR',  # Argentina
    'se': 'SE',
    'UK': 'GB',
    'USA': 'US',
    'YV': 'VE',  # Venezuela
}


def level_1_query(dc, query, columns):
    """Generator - return dictionary per iteration. 'columns' is a list of
    column names."""
    l1conn = dc.getL1Connection()
    l1conn.rquery(query, None)
    R = l1conn.readRow()
    while R:
        # Create dictionary, colname=value
        d = dict(zip(columns, R.valuesAsList()))
        # Remove 'branchid' (why ??, DIG does this, but is it necessary??)
        d.pop('branchid', None)
        yield d
        R = l1conn.readRow()
    l1conn.endQuery()


@fixrunner.once
@fixrunner.run
def fixit(dc, debug=False, *a, **k):
    ops = []
    for crew in list(level_1_query(dc, " ".join((
            "SELECT id, bcountry",
            "FROM crew",
            "WHERE next_revid = 0",
            "AND deleted = 'N'",
            "AND bcountry NOT IN"
            "(SELECT id FROM country WHERE next_revid = 0 and deleted = 'N')"
        )), ('id', 'bcountry'))):
        print "crew %(id)s, bcountry %(bcountry)s " % crew,
        if debug:
            fixrunner.log.debug("Trying crew '%s' with country '%s'..." % (crew['id'], crew['bcountry']))
        for entry in fixrunner.dbsearch(dc, 'crew', " ".join((
                "id = '%s'" % crew['id'], 
                "AND deleted = 'N'",
                "AND next_revid = 0",
            ))):
            try:
                new_bcountry = country_map[entry['bcountry']]
                entry['bcountry'] = new_bcountry
                if debug:
                    fixrunner.log.debug("...setting country to '%s'." % new_bcountry)
                ops.append(fixrunner.createop('crew', 'U', entry))
                print new_bcountry
            except Exception, e:
                fixrunner.log.error("Could not update crew '%s' (bcountry=%s). [%s]" % (crew, entry.get('bcountry', None), e))
                break
    return ops


fixit.program = 'sku-3864.py (2009-11-17)'


if __name__ == '__main__':
    fixit()
