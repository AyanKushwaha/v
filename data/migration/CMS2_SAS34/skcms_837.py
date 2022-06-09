import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table
import AbsTime

__version__ = '2016_03_02'


def crt_prop(ops, prop_set_tbl, prop_tbl, p_id, p_from, p_to, p_str, p_time, p_int):
    d_from = int(AbsTime.AbsTime(p_from))
    d_to   = int(AbsTime.AbsTime(p_to))
    d_time = int(AbsTime.AbsTime(p_time)) if p_time else None 
    match_row = {'id':p_id}
    if len(prop_set_tbl.get_matching_rows(match_row))==0:
        row = prop_set_tbl.crt_row([p_id, p_id])
        prop_set_tbl.put_row(ops,row)
    else:
        print "property_set already exist for",p_id
    row = prop_tbl.crt_row([p_id, d_from, d_to, None, d_time, p_int, p_str, None, p_id])
    prop_tbl.put_row(ops,row)


def crt_code_standard(ops, prop_set_tbl, prop_tbl, acode, aname, afrom, ato, aag):
    crt_prop(ops, prop_set_tbl, prop_tbl, 'ofdx_name_'+acode,         afrom, ato, aname, None,  None)
    crt_prop(ops, prop_set_tbl, prop_tbl, 'ofdx_period_start_'+acode, afrom, ato, None,  afrom, None)
    crt_prop(ops, prop_set_tbl, prop_tbl, 'ofdx_period_end_'+acode,   afrom, ato, None,  ato,   None)
    crt_prop(ops, prop_set_tbl, prop_tbl, 'ofdx_attend_goal_'+acode,  afrom, ato, None,  None, 1)
    crt_prop(ops, prop_set_tbl, prop_tbl, 'ofdx_attend_limit_'+acode, afrom, ato, None,  None, 1)
    crt_prop(ops, prop_set_tbl, prop_tbl, 'ofdx_agmt_groups_'+acode,  afrom, ato, aag,   None, None)

    row = prop_set_tbl

@fixrunner.once
@fixrunner.run

def fixit(dc, *a, **k):
    ops = []

    prop_set_tbl = migrate_table.MigrateTable(dc, fixrunner, 'property_set', ['id', 'si'], 1)
    prop_set_tbl.load(None)

    prop_tbl = migrate_table.MigrateTable(dc, fixrunner, 'property', 
        ['id', 'validfrom', 'validto', 'value_rel', 'value_abs', 'value_int', 'value_str', 'value_bool','si'], 2)
    prop_tbl.load(None)

    print "MigrateTable created"
   
    crt_code_standard(ops, prop_set_tbl, prop_tbl, 'OA92','Pilot Meeting STO', '01Jan2016', '01Jan2017', 'SKS_FD_AG;SKN_FD_AG;SKD_FD_OTH_ACQ;SKIS_FD_AG;SKIN_FD_AG;SKID_FD_AG')

    prop_set_tbl.write_orig()
    prop_tbl.write_orig()
    print "Done, updates= ",len(ops)
    return ops 
   

fixit.program = 'skcms_837.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
