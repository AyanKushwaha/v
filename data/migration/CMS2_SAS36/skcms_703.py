import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table

__version__ = '2016_04_01'

def convert_ac_qual_map(dc, ops):
    print "convert ac_qual_map_tbl ",len(ops)
    #print "initiating ac_qual_map"
    ac_qual_map_tbl = prop_set_tbl = migrate_table.MigrateTable(dc, fixrunner, 'ac_qual_map', ['ac_type', 'aoc', 'ac_qual_fc', 'ac_qual_cc'], 2)
    ac_qual_map_tbl.load(None)
    #print "inititated"
    for row in ac_qual_map_tbl.get_rows():
        #print "found row ", row
        chg = False
        if row['ac_qual_fc'] == '36':
            row['ac_qual_fc'] = '38'
            chg = True 
        if row['ac_qual_cc'] == '36':
            row['ac_qual_cc'] = '38'
            chg = True 
        #print "changed row", row
        if chg:
            ac_qual_map_tbl.put_row(ops, row)
        #print "put"
    #print "fixing cc"
    ac_qual_map_tbl.write_orig()
        
def convert_crew_qualification(dc, ops):
    print "convert crew_qualification_tbl ",len(ops)
    crew_qualification_tbl = migrate_table.MigrateTable(dc, fixrunner, 'crew_qualification', ['crew', 'qual_typ', 'qual_subtype', 'validfrom', 'validto', 'lvl', 'si', 'acstring'], 4)
    crew_qualification_tbl.load(None)
    for row in crew_qualification_tbl.get_matching_rows({'qual_typ':'ACQUAL', 'qual_subtype': '36'}):
        newrow = crew_qualification_tbl.crt_row([row['crew'], 'ACQUAL', '38', row['validfrom'], row['validto'], row['lvl'], row['si'], row['acstring']])
        if crew_qualification_tbl.has_row(newrow):
            print "Row already exists crew_qual: ",newrow
        else:
            crew_qualification_tbl.put_row(ops, newrow)
        crew_qualification_tbl.del_row(ops, row)
    crew_qualification_tbl.write_orig()

def convert_crew_restr_acqual(dc, ops):
    print "convert crew_restr_acqual_tbl ",len(ops)
    crew_restr_acqual_tbl = migrate_table.MigrateTable(dc, fixrunner, 'crew_restr_acqual', ['crew', 'qual_typ', 'qual_subtype', 'acqrestr_typ', 'acqrestr_subtype', 'validfrom', 'validto', 'lvl', 'si'], 6)
    crew_restr_acqual_tbl.load(None)
    for row in crew_restr_acqual_tbl.get_matching_rows({'qual_typ':'ACQUAL', 'qual_subtype': '36'}):
        newrow = crew_restr_acqual_tbl.crt_row([row['crew'], 'ACQUAL', '38', row['acqrestr_typ'], row['acqrestr_subtype'], row['validfrom'], row['validto'], row['lvl'], row['si']])
        if crew_restr_acqual_tbl.has_row(newrow):
            print "Row already exists crew_restr_acq: ",newrow
        else:
            crew_restr_acqual_tbl.put_row(ops, newrow)
        crew_restr_acqual_tbl.del_row(ops, row)
    crew_restr_acqual_tbl.write_orig()
        
def convert_crew_qual_acqual(dc, ops):
    print "convert crew_qual_acqual_tbl ",len(ops)
    crew_qual_acqual_tbl = migrate_table.MigrateTable(dc, fixrunner, 'crew_qual_acqual', ['crew', 'qual_typ', 'qual_subtype', 'acqqual_typ', 'acqqual_subtype', 'validfrom', 'validto', 'lvl', 'si'], 6)
    crew_qual_acqual_tbl.load(None)
    for row in crew_qual_acqual_tbl.get_matching_rows({'qual_typ':'ACQUAL', 'qual_subtype': '36'}):
        newrow = crew_qual_acqual_tbl.crt_row([row['crew'], 'ACQUAL', '38', row['acqqual_typ'], row['acqqual_subtype'], row['validfrom'], row['validto'], row['lvl'], row['si']])
        if crew_qual_acqual_tbl.has_row(newrow):
            print "Row already exists crew_qual_acq: ",newrow
        else:
            crew_qual_acqual_tbl.put_row(ops, newrow)
        crew_qual_acqual_tbl.del_row(ops, row)
    crew_qual_acqual_tbl.write_orig()
        
def convert_crew_qualification_set(dc, ops):
    print "convert crew_qualification_set_blr ",len(ops)
    crew_qualification_set_tbl = migrate_table.MigrateTable(dc, fixrunner, 'crew_qualification_set', ['typ', 'subtype', 'si', 'descshort', 'desclong'], 2)
    crew_qualification_set_tbl.load(None)
    for row in crew_qualification_set_tbl.get_matching_rows({'typ':'ACQUAL', 'subtype':'36'}):
        crew_qualification_set_tbl.del_row(ops,row)
    crew_qualification_set_tbl.write_orig()

def convert_crew_document(dc, ops):
    print "convert crew_document_tbl ",len(ops)
    crew_document_tbl = migrate_table.MigrateTable(dc, fixrunner, 'crew_document', ['crew', 'doc_typ', 'doc_subtype', 'validfrom', 'validto', 'docno', 'maindocno', 'issuer', 'si', 'ac_qual'], 4)
    crew_document_tbl.load(None)
    for row in crew_document_tbl.get_matching_rows({'ac_qual': '36'}):
        row['ac_qual'] ='38'
        crew_document_tbl.put_row(ops, row)
    crew_document_tbl.write_orig()

def convert_crew_training_log(dc, ops):
    print "convert crew_training_log_tbl ",len(ops)
    crew_training_log_tbl = migrate_table.MigrateTable(dc, fixrunner, 'crew_training_log', ['crew', 'typ', 'code', 'tim', 'attr'], 4)
    crew_training_log_tbl.load(None)
    for row in crew_training_log_tbl.get_matching_rows({'attr': '36'}):
        row['attr'] = '38'
        crew_training_log_tbl.put_row(ops, row)
    for row in crew_training_log_tbl.get_matching_rows({'code': '36'}):
        newrow = crew_training_log_tbl.crt_row([row['crew'], row['typ'], '38', row['tim'], row['attr']])
        if crew_training_log_tbl.has_row(newrow):
            print "Row already exists crew_training_log: ",newrow
        else:
            crew_training_log_tbl.put_row(ops, newrow)
        crew_training_log_tbl.del_row(ops, row)
    crew_training_log_tbl.write_orig()

def convert_crew_training_need(dc, ops):
    print "convert crew_training_need_tbl ",len(ops)
    crew_training_need_tbl = migrate_table.MigrateTable(dc, fixrunner, 'crew_training_need', 
                                                        ['crew', 'part', 'validfrom', 'validto', 'course', 'attribute', 'flights', 'maxdays', 'acqual', 'completion', 'si', 'course_subtype'], 3)
    crew_training_need_tbl.load(None)
    for row in crew_training_need_tbl.get_matching_rows({'acqual': '36'}):
        row['acqual'] = '38'
        crew_training_need_tbl.put_row(ops, row)
    crew_training_need_tbl.write_orig()

def convert_crew_user_filter(dc, ops):
    print "convert crew_user_filter_tbl ",len(ops)
    crew_user_filter_tbl = migrate_table.MigrateTable(dc, fixrunner, 'crew_user_filter', ['crew', 'filt', 'val', 'validfrom', 'validto', 'si'], 4)
    crew_user_filter_tbl.load(None)
    for row in crew_user_filter_tbl.get_matching_rows({'filt': 'ACQUAL', 'val': '36'}):
        newrow = crew_user_filter_tbl.crt_row([row['crew'], row['filt'], '38', row['validfrom'], row['validto'], row['si']])
        if crew_user_filter_tbl.has_row(newrow):
            print "Row already exists crew_user_filter: ",newrow
        else:
            crew_user_filter_tbl.put_row(ops, newrow)
        crew_user_filter_tbl.del_row(ops, row)
    crew_user_filter_tbl.write_orig()
      
def convert_apt_restrictions(dc, ops):
    print "convert apt_restrictions_tbl ",len(ops)
    apt_restrictions_tbl = migrate_table.MigrateTable(dc, fixrunner, 'apt_restrictions', ['station', 'restr_typ', 'restr_subtype', 'ac_qual', 'lifus_all', 'lifus_first', 'lifus_four', 'lifus_num'], 4)
    apt_restrictions_tbl.load(None)
    for row in apt_restrictions_tbl.get_matching_rows({'ac_qual': '36'}):
        newrow = apt_restrictions_tbl.crt_row([row['station'], row['restr_typ'], row['restr_subtype'], '38', row['lifus_all'], row['lifus_first'], row['lifus_four'], row['lifus_num']])
        if apt_restrictions_tbl.has_row(newrow):
            print "Row already exists apt_restr: ",newrow
        else:
            apt_restrictions_tbl.put_row(ops, newrow)
        apt_restrictions_tbl.del_row(ops, row)
    apt_restrictions_tbl.write_orig()

def convert_course_content(dc, ops):
    print "convert course_content_tbl ",len(ops)
    course_content_tbl = migrate_table.MigrateTable(dc, fixrunner, 'course_content', ['course', 'course_subtype','ac_qual','rank','activity','activity_order','quantity','min_hrs','si'], 5)
    course_content_tbl.load(None)
    for row in course_content_tbl.get_matching_rows({'ac_qual': '36'}):
        newrow = course_content_tbl.crt_row([row['course'], row['course_subtype'], '38', row['rank'], row['activity'], row['activity_order'], row['quantity'], row['min_hrs'], row['si']])
        if course_content_tbl.has_row(newrow):
            print "Row already exists course_content: ",newrow
        else:
            course_content_tbl.put_row(ops, newrow)
        course_content_tbl.del_row(ops, row)
    course_content_tbl.write_orig()

def convert_course_ac_qual_set(dc, ops):
    print "convert course_ac_qual_set_tbl ",len(ops)
    course_ac_qual_set_tbl = migrate_table.MigrateTable(dc, fixrunner, 'course_ac_qual_set', ['id', 'si'], 1)
    course_ac_qual_set_tbl.load(None)
    for row in course_ac_qual_set_tbl.get_matching_rows({'id': '36'}):
        course_ac_qual_set_tbl.del_row(ops, row)
    course_ac_qual_set_tbl.write_orig()

ACQUALS_DIC = { 'AL3690':'AL3890', 'AL36':'AL38', '3690':'3890', '36': '38', 'A236':'A238', 'ALA236': 'ALA238'}
#        try:
#            if ac_quals == 'AL3690':
##                ac_quals = 'AL3890'
#                change = True
#            elif ac_quals == 'AL36':
#                ac_quals = 'AL38'
#                change = True
#            elif ac_quals == '3690':
#                ac_quals = '3890'
#                change = True
#            elif ac_quals == '36':
#                ac_quals = '38'
#                change = True

def convert_cabin_recurrent(dc, ops):
    print "convert cabin_recurrent_tbl ",len(ops)
    cabin_recurrent_tbl = migrate_table.MigrateTable(dc, fixrunner, 'cabin_recurrent', ['base', 'acquals', 'validfrom', 'validto', 'reccode'], 3)
    cabin_recurrent_tbl.load(None)
    for row in cabin_recurrent_tbl.get_rows():
        if row['acquals'] in ACQUALS_DIC:
            newrow = cabin_recurrent_tbl.crt_row([row['base'], ACQUALS_DIC[row['acquals']], row['validfrom'], row['validto'], row['reccode']])
            if cabin_recurrent_tbl.has_row(newrow):
                print "Row already exists cabin_recurrent: ",newrow
            else:
                cabin_recurrent_tbl.put_row(ops, newrow)
            cabin_recurrent_tbl.del_row(ops, row)
    cabin_recurrent_tbl.write_orig()

def convert_cabin_training(dc, ops):
    print "convert cabin_training_tbl ",len(ops)
    cabin_training_tbl = migrate_table.MigrateTable(dc, fixrunner, 'cabin_training', ['taskcode', 'validfrom', 'validto', 'base', 'qualgroup', 'typ'], 2)
    cabin_training_tbl.load(None)
    for row in cabin_training_tbl.get_matching_rows({'qualgroup' : '36'}):
        row['qualgroup'] = '38'
        cabin_training_tbl.put_row(ops, row)
    cabin_training_tbl.write_orig()

def convert_pc_opc_composition(dc, ops):
    print "convert pc_opc_composition_tbl ",len(ops)
    pc_opc_composition_tbl = migrate_table.MigrateTable(dc, fixrunner, 'pc_opc_composition', ['simtype_grp', 'simtype_legtime', 'qual', 'validfrom', 'validto', 'twofcsim', 'pclimit', 'allowedlower'], 4)
    pc_opc_composition_tbl.load(None)
    for row in pc_opc_composition_tbl.get_matching_rows({'qual': '36'}):
        newrow = pc_opc_composition_tbl.crt_row([row['simtype_grp'], row['simtype_legtime'], '38', row['validfrom'], row['validto'], row['twofcsim'], row['pclimit'], row['allowedlower']])
        if pc_opc_composition_tbl.has_row(newrow):
            print "Row already exists oc_opc_composition: ",newrow
        else:
            pc_opc_composition_tbl.put_row(ops, newrow)
        pc_opc_composition_tbl.del_row(ops, row)
    pc_opc_composition_tbl.write_orig()

# there is no valid data for 36 in db
#def convert_pgt_need(dc, ops):
#    pgt_need_tbl = migrate_table.MigrateTable(dc, fixrunner, 'pgt_need', ['base', 'qual','validfrom', 'validto', 'minval', 'maxval'], 4)
#    pgt_need_tbl.load(None)
##    for row in pgt_need_tbl.get_matching_rows({'filt': 'ACQUAL', 'val': '36'}):
#        newrow = pgt_need_tbl.crt_row([row.crew, row.filt, '38', row.validfrom, row.validto, row.si])
#        if pgt_need_tbl.has_row(newrow):
#            print "Row already exists pgt_need_tbl: ",newrow
#        else:
#            pgt_need_tbl.put_row(ops, newrow)
#            pgt_need_tbl.del_row(ops, row)
    
@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    convert_ac_qual_map(dc, ops)
    convert_crew_qualification(dc, ops)
    convert_crew_restr_acqual(dc, ops)
    convert_crew_qual_acqual(dc, ops)
    convert_crew_qualification_set(dc, ops)
    convert_crew_document(dc, ops)
    convert_crew_training_log(dc, ops)
    convert_crew_training_need(dc, ops)
    convert_crew_user_filter(dc, ops)
    convert_apt_restrictions(dc, ops)
    convert_course_content(dc, ops)
    #_convert_course_content_exc(dc, ops)  no 36 data in db
    convert_course_ac_qual_set(dc, ops)
    convert_cabin_recurrent(dc, ops)
    convert_cabin_training(dc, ops)
    convert_pc_opc_composition(dc, ops)
    #convert_pgt_need(dc, ops) mo valid 36 data in db 
    print "Done, ops= ",len(ops)
    return ops 

fixit.program = 'skcms_703.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
