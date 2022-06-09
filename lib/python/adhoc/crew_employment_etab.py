
import sys
import rave_etab

def printerr(tx):
    sys.stderr.write(tx+'\n')

if __name__ == '__main__':
    data = rave_etab.RaveEtab(None) #'crew_employment')
    printerr("This script adds column 'planning_group' to crew_employment.etab and populates it with 'region' values.");

    if data.col_name(0)!='crew':
        printerr( "First column should be 'crew'")
        exit(1)
    if data.col_count()==15:
        printerr ( "There are already 15 columns present")
        exit(1)
    data.add_col('S','planning_group','')
    for i in range(data.row_count()):
        r = data.row(i)
        #print "row",i,len(r)
        if len(r)==14:
            r.append(r[9])
    data.save_as_etab(None) #'crew_employment.out')

    printerr( "Done")
    exit(0)
            
