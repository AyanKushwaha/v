import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table
import AbsTime
import sys

__version__ = '2015_10_22'


timestart = int(AbsTime.AbsTime('01JAN1986'))/24/60
timeend =   int(AbsTime.AbsTime('31DEC2035'))/24/60

DIC_AGS = { 'STO': 'SKIS_FD_AG', 'CPH' : 'SKID_FD_AG', 'OSL': 'SKIN_FD_AG'}

def base_ags_dic(dc):
   ret = {}

   vcols = ['contract','validfrom','validto', 'si','maincat','base','company']
   cev = migrate_table.MigrateTable(dc, fixrunner, 'crew_contract_valid',vcols, 2)
   #sys.stderr.write("cev created\n")
   cev.load(None)
   #sys.stderr.write("cev loaded\n")
   for row in cev.get_rows():
     #sys.stderr.write(str(row)+'\n')
     b = row['base']
     if b in DIC_AGS:
         ret[row['contract']] = DIC_AGS[b]
   return ret

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    #sys.stderr.write("Start migration\n")
    base_ags = base_ags_dic(dc)
    #sys.stderr.write("base ags created"+str( len(base_ags))+'\n')
    ag = migrate_table.MigrateTable(dc, fixrunner, 'agmt_group_set' ,['id','validfrom','validto','si'],1)
    #sys.stderr.write("MigrateTable created\n")
    ag.load(None)

    row = ag.crt_row(['SKID_FD_AG',timestart,timeend,'Flight Deck SKI DK'])
    ag.put_row(ops,row)
    row = ag.crt_row(['SKIS_FD_AG',timestart,timeend,'Flight Deck SKI SE'])
    ag.put_row(ops,row)
    row = ag.crt_row(['SKIN_FD_AG',timestart,timeend,'Flight Deck SKI NO'])
    ag.put_row(ops,row)

    row = ag.crt_row(['SKI_FD_AG'])
    ag.del_row(ops,row)
    #sys.stderr.write( "ags created\n") 

    ag.write_orig()
    #sys.stderr.write( "ags written\n")

    cols = ['id','si','dutypercent','grouptype','pattern','nooffreedays','noofparttime','parttimecode','descshort',
        'desclong','noofvadays','bxmodule','laborunion','congrouptype','conpattern','agmtgroup']
    ce = migrate_table.MigrateTable(dc,fixrunner,'crew_contract_set',cols,1)
    #sys.stderr.write( "contr_set created\n")
    ce.load("agmtgroup='SKI_FD_AG'")
    #sys.stderr.write( "loaded\n")
    for row in ce.get_rows():
        if row['agmtgroup'] != 'SKI_FD_AG':
            break
        row['agmtgroup'] = base_ags[row['id']]
        ce.put_row(ops,row)
    #sys.stderr.write( "c created\n")
    ce.write_orig() 
    
    #sys.stderr.write( "done,updates="+str(len(ops))+'\n')
    #for op in ops:
    #    print str(op)
    return ops


fixit.program = 'skcms_761.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


