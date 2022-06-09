#!/bin/bash
#
# Wrapper script to start a mirador process and  launching the Table Editor.
# Using current_carmsys -> /carm/release/Tracking/Tracking-TRACKING_1.57.1.2_CARMSYS
#
# Org: Björn Svensson, Jeppesen, 20081118
#

#
# Assume that the start script is located in the carmusr get abolute path
# by assuming that a crc directory exist at the top level
#
if [ -z "$CARMUSR" ]; then
    a=`pwd`
    cd `dirname $0`
    while [ `pwd` != '/' -a ! -d "bin" ]; do
        cd ..
    done
    CARMUSR=`pwd`
    export CARMUSR
    cd $a
fi


#
# Source the carmenv configuration file. Will set
# all other CARMXXX variables
#
. $CARMUSR/bin/carmenv.sh

#
# Schema can be specified on command line
#
schema=$SCHEMA
connect=$DATABASE

table_editor() {
    #
    # Start mirador
    #
    linkfile=`mktemp`    
    $CARMSYS/bin/mirador --watchdog --linkfile $linkfile &
    pid=$!

    #
    # Wait for mirador to start, but also check if it died
    #
    while [ ! -s $linkfile ] ; do
	ps -p $pid > /dev/null || { rm $linkfile; exit 1; }
	sleep 1
    done
    
    url=`cat $linkfile`
    rm $linkfile
    
    #
    # Start Table Editor
    #
    echo java -Xmx512m -Xms512m -jar $CARMSYS/lib/classes/tableeditor-all.jar -f '!/forms/tableeditor/dtable_standalone_cms/MainApp.xml' -c $connect -s $schema -d $url
    java -Xmx512m -Xms512m -jar $CARMSYS/lib/classes/tableeditor-all.jar  -f '!/forms/tableeditor/dtable_standalone_cms/MainApp.xml' -c $connect -s $schema -d $url
    kill $pid
}

table_editor 2>&1 
#| /usr/bin/tee -a $LOGFILE
