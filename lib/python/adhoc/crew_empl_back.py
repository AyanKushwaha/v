
import sys
import rave_etab

def printerr(tx):
    sys.stderr.write(tx+'\n')

if __name__ == '__main__':
    data = rave_etab.RaveEtab(None) #'crew_employment')
    printerr("This script reverts column 'planning_group' from crew_employment.etab .");

    if data.col_name(0)!='crew':
        printerr( "First column should be 'crew'")
        exit(1)
    if data.col_count()!=15:
        printerr ( "There are not 15 columns present")
        exit(1)
    data.del_col(14)
    for i in range(data.row_count()):
        r = data.row(i)
        #print "row",i,len(r)
        if len(r)==15:
            del r[14]
    data.save_as_etab(None) #'crew_employment.out')

    printerr( "Done")
    exit(0)
            
