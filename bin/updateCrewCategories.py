#!/usr/bin/env python
# $Header: /opt/Carmen/CVS/sk_cms_user/bin/updateCrewCategories.py,v 1.4 2008/07/16 12:14:32 markus Exp $

import os,sys,getopt,shutil

##Old > New
##A FC > A
##B FP > B
##C FS > -
##D AP > E
##E AS > F
##F AH > G
##G FR > C
##H FI > D
##I AI > H
##J TR > J
##K TL > I
old2newKeys = {
    'A': 'A',
    'B': 'B',
    'C': '-',
    'D': 'E',
    'E': 'F',
    'F': 'G',
    'G': 'C',
    'H': 'D',
    'I': 'H',
    'J': 'J',
    'K': 'I'}

##New > Old
##A FC > A
##B FP > B
##C FR > G
##D FI > H
##E AP > D
##F AS > E
##G AH > F
##H AI > I
##I TL > K
##J TR > J
new2oldKeys = {
    'A': 'A',
    'B': 'B',
    'C': 'G',
    'D': 'H',
    'E': 'D',
    'F': 'E',
    'G': 'F',
    'H': 'I',
    'I': 'K',
    'J': 'J'}

def upCats(crewCats):
    newCrewCats = ""
    for char in crewCats:
        try:
            newChar = keys[char]
        except:
            newChar = char
        newCrewCats += newChar
    return newCrewCats

help=False
old2new=False
new2old=False
planfile='subplan'
headerfile='subplanHeader'
backup=True
dirpath=""

try:
    short='honxP:H:d:'
    long=['help','old2new','new2old','nobackup','planfile=','headerfile=',"directory="]
    for opt,val in getopt.getopt(sys.argv[1:],short,long)[0]:
        if opt in ('-h','--help'):
	    help=True
        elif opt in ('-o','--old2new'):
            old2new=True
            keys=old2newKeys
        elif opt in ('-n','--new2old'):
            new2old=True
            keys=new2oldKeys
        elif opt in ('-x','--nobackup'):
            backup=False
      	elif opt in ('-P','--planfile'):
            planfile=val
        elif opt in ('-H','--headerfile'):
            headerfile=val
        elif opt in ('-d','--directory'):
            dirpath=val
except Exception,e:
    print e,'(Use -h for help)'
    sys.exit(-1)

if help:
    print """Usage: updateCrewCategories [required-option] [optional-options]
    where required-options is one of -o or -n
    
Takes a planfile and a headerfile and converts it from old (SAS) format to new (Jeppesen) format or vice versa.
The planfile should be in compressed format, without .Z-suffix.
If no files are specified it is assumed that the files 'subplan' and 'subplanHeader' in the current directory should be modified.

Options: -h --help
         -o --old2new
         -n --new2old
         -x --nobackup    Don't save backup copies of files
         -d --directory   Path to a directory where the files are located
         -P --planfile    filename for planfile
                          ('subplan' is used if not specified)
         -H --headerfile  filename for headerfile'
                          ('subplanHeader' is used if not specified)"""
    sys.exit(0)

if (old2new and new2old) or not (old2new or new2old):
    print 'You must specify (one) direction of conversion (Use -h for help)'
    sys.exit(-1)
else:
    # Add paths to directory, if specified
    planfile=os.path.join(dirpath, planfile)
    headerfile=os.path.join(dirpath, headerfile)
    if backup:
        print 'backups the affected files: %s' % planfile
        planfileBAK = os.path.splitext(planfile)[0] + ".bak"
        headerfileBAK = os.path.splitext(headerfile)[0] + ".bak"
        try:
            shutil.copy2(planfile,planfileBAK)
            shutil.copy2(headerfile,headerfileBAK)
        except:
            print 'Couldn\'t backup files'
            sys.exit(-1)

    print 'modifies the headerfile ('+headerfile+')'
    try:
        hf = open(headerfile)
    except:
        print 'No such file: '+headerfile
        sys.exit(-1)
    headerfileNEW = os.path.splitext(headerfile)[0] + ".new"
    hfo = open(headerfileNEW, "w")
    lines = hf.readlines()
    line = lines[2]
    fields = line.split(";")
    if fields[0] == "554":
        fields[9] = upCats(fields[9])
    else:
        print 'error'
    newLine = ";".join(fields)
    lines[2] = newLine
    hfo.writelines(lines)
    hf.close()
    hfo.close()
    os.rename(headerfileNEW,headerfile)

    print 'modifies the planfile ('+planfile+')'

    #uncompresses the planfile
    planfileZ = os.path.splitext(planfile)[0] + ".Z"
    try:
        os.rename(planfile,planfileZ)
    except:
        print 'No such file: '+planfile
        sys.exit(-1)
    os.system('uncompress '+planfileZ)
    #'planfile' is now the uncompressed file

    pf = open(planfile)
    planfileNEW = os.path.splitext(planfile)[0] + ".new"
    pfo = open(planfileNEW, "w")
   
    for line in pf:
        fields = line.split(";")
        if fields[0] == "58":
            fields[2] = upCats(fields[2])
            newLine = ";".join(fields)
        else:
            newLine = line
        pfo.write(newLine)

    pf.close()
    pfo.close()

    os.system('compress '+planfileNEW)
    os.rename(planfileNEW+".Z",planfile)

