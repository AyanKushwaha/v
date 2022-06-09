#!/bin/env python

import cx_Oracle as oc	
import modelserver



table_sizes = []
missing_tables = []
tables_to_check = []

def getTableNames ():
	global tables_to_check
	con = oc.connect('sk_feb_r22/sk_feb_r22@devdb01:1521/CMSDEV')
	cur = con.cursor()
	cur.execute('SELECT table_name FROM all_tables')
	for (result,) in cur:
		tables_to_check.append(result)			
	cur.close()
	con.close()


def loadTable(table_name) :

    tm = modelserver.TableManager.instance()
    
    try :
        tm.loadTable(table_name)
        
        return tm.table(table_name)

    except modelserver.TableNotFoundError :
       
        print "{0} - Table not found.".format(table_name)
        
        return None

    except BaseException as error:
        print "{0} - type = {1}".format(table_name,type(error))
        print "{0} - Name = {1}".format(table_name, error)
        print "{0} - Got Exception: {1}".format(table_name, error)  

        return None


def getTableSize(table_name) :

    global table_sizes
    global missing_tables
 
    table = loadTable(table_name.lower())

    if table :
        print "{0} - Size: {1}".format(table_name,table.size())
        table_sizes.append((table_name, table.size()))
    else :
#        print "Error get size of the table: ", table_name
        missing_tables.append(table_name)


   
def listTableSizes() :
    
    global table_sizes
    global missing_tables

    table_sizes = []
    missing_tables = []

    for t in tables_to_check :
        if len(table_sizes) < 2:
		getTableSize(t)

    print "----------------------------------------------"
    print "Table sizes:" 
    for table_name, size in table_sizes :
        print "{0};{1}".format(table_name,size) 

    print "----------------------------------------------" 
    print "Missing tables : " 
    for table_name in missing_tables :
        print "{0}".format(table_name) 



if __name__ == "__main__":
	getTableNames() 
	listTableSizes()


