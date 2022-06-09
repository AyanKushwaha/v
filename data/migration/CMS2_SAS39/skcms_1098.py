import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table
import AbsTime
import RelTime

__version__ = '2016_08_16'


def crt_prop(ops, prop_set_tbl, prop_tbl, p_id, p_descr,  p_from, p_to, p_rel, p_abs, p_int, p_str):
    d_from = int(AbsTime.AbsTime(p_from))
    d_to   = int(AbsTime.AbsTime(p_to))
    d_rel = int(RelTime.RelTime(p_rel)) if p_rel else None
    d_abs = int(AbsTime.AbsTime(p_abs)) if p_abs else None
    if p_descr is None:
        p_desr = p_id
    match_row = {'id':p_id}
    if len(prop_set_tbl.get_matching_rows(match_row))==0:
        row = prop_set_tbl.crt_row([p_id, p_descr])
        prop_set_tbl.put_row(ops,row)
    else:
        print "property_set already exist for",p_id
    row = prop_tbl.crt_row([p_id, d_from, d_to, d_rel, d_abs, p_int, p_str, None, p_descr])
    prop_tbl.put_row(ops,row)

@fixrunner.once
@fixrunner.run

def fixit(dc, *a, **k):
    ops = []

    prop_set_tbl = migrate_table.MigrateTable(dc, fixrunner, 'property_set', ['id', 'si'], 1)
    prop_set_tbl.load(None)

    prop_tbl = migrate_table.MigrateTable(dc, fixrunner, 'property',
        ['id', 'validfrom', 'validto', 'value_rel', 'value_abs', 'value_int', 'value_str', 'value_bool','si'], 2)
    prop_tbl.load(None)

    #print "MigrateTable created"

    crt_prop(ops, prop_set_tbl, prop_tbl, 'meal_skn_time_to_frst_brk','Max time until a meal is required for SKN','1oct2016','31dec2035',
        '5:45', None, None, None)
    crt_prop(ops, prop_set_tbl, prop_tbl, 'meal_sks_time_to_frst_brk','Max time until a meal is required for SKS','1oct2016','31dec2035',
        '6:00', None, None, None)
    crt_prop(ops, prop_set_tbl, prop_tbl, 'meal_skd_time_to_frst_brk','Max time until a meal is required for SKD','1oct2016','31dec2035',
        '6:00', None, None, None)

    prop_set_tbl.write_orig()
    prop_tbl.write_orig()
    print "Done, updates= ",len(ops)
    return ops


fixit.program = 'skcms_1098.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
