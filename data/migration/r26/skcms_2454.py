"""
SKCMS-2454 R26: Add datagroups to every entity in the data model.
Release: r26
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2020-09-02a'

filepath = os.path.expandvars('$CARMUSR')
directory = filepath+'/data/migration/r26/'
#directory = filepath+'/data/config/models/'



@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    
    filecounter = 0
    entcounter = 0
    dgcounter = 0
    search_entity = "<entity name=\""
    search_datagroup = "<config name=\"datagroup\""
    insert_string = "<config name=\"datagroup\" cfg=\"default\" />"
    
    for filename in os.listdir(directory):
        
        if filename.endswith(".xml"):
            
            filecounter+=1
            print "Filename: " + directory + filename
            fopen = open(directory+filename,mode='r+')        
            fread = fopen.readlines()            
            insert_datagroup = False
            write_file = False
            
            for index, line in enumerate(fread):
                if search_entity in fread[index-1] and (search_datagroup not in line):
                    print "Inserting datagroup"
                    fread.insert(index, (" "*(entity_start_index+2)) + insert_string + "\n")
                    dgcounter+=1
                    write_file = True
                if search_entity in line:
                    entity_start_index = line.find(search_entity)
                    entcounter+=1
                    print "Found entity line: ", line
                if search_datagroup in line:
                    print "Found existing datagroup line"
            if write_file:
                print "Writing to file: ", filename
                fopen.seek(0)               
                fopen.writelines(fread)
                
    print "********************************************"
    print "Found ", entcounter, " entity definitions in ", filecounter, " files"
    print "Inserted ", dgcounter, " datagroup lines"
    
fixit.program = 'skcms_2454.py (%s)' % __version__
if __name__ == '__main__':
    fixit()