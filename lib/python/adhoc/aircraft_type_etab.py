
import sys
import rave_etab

def printerr(tx):
    sys.stderr.write(tx+'\n')
            

if __name__ == '__main__':
    data = rave_etab.RaveEtab(None) #'aircraft_type')
    printerr("This script adds columns 'class1fc class2fc class3fc class1cc class2cc class3cc' to aircraft_type.etab and populates it with 'crewbunkfc and crewbunkcc' values.");

    printerr( "col 0: %s"% data.col_name(0))
    if not data.col_name(0).startswith('id'):
        printerr( "First column should be 'id'")
        exit(1)
    if data.col_count()==14:
        printerr ( "There are already 14 columns present")
        exit(1)
    data.add_col('I','class1fc','')
    data.add_col('I','class2fc','')
    data.add_col('I','class3fc','')
    data.add_col('I','class1cc','')
    data.add_col('I','class2cc','')
    data.add_col('I','class3cc','')
    for i in range(data.row_count()):
        r = data.row(i)
        if len(r)==8:
            r.append(r[4])
            r.append(0)
            r.append(0)
            r.append(0)
            r.append(0)
            r.append(r[5])
    data.save_as_etab(None) #'aircraft_type.out')

    printerr( "Done")
    exit(0)
