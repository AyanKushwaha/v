#!/bin/sh
# @(#) $Header: /opt/Carmen/CVS/sk_cms_user/bin/gather_statistics.sh,v 1.5 2010/04/09 13:27:41 adg239 Exp $
#########################################
# Copyright Jeppesen Systems AB
# Robert Tropp Larsen
# 
# Script to start Oracle statistics on one DB node
# It fetches the schema name from configuration and 
# runs daily and weekly statistics.
# It runs both weekly and daily statistics or CMP statistics
# When the weekly statistics is run, can be configured in etc/demond_task.xml, 
# process CMD_GATHER_STATS
#
# The script uses $CARMUSR/etc/analyzetables and $CARMUSR/etc/analyzetables_no_histogram
# to control which table to run statistics for with or wihtout histograms.

# Sets the CARMUSR variable, if it is not set
if [ -z "$CARMUSR" ]; then
    a=`pwd`
    cd `dirname $0`
    while [ `pwd` != '/' -a ! -d "crc" ]; do
      cd ..
    done
    # Get the physical directory with '-P'
    CARMUSR=`pwd -P`
    export CARMUSR
    cd $a
fi
 
# Sets CARMDATA, CARMSYS, CARMTMP and variables from CONFIG_extension.
SK_INTEGRATION=True
export SK_INTEGRATION
. $CARMUSR/bin/carmenv.sh
 
# CMP or normal statistics
CMP="false"
if [ $# -eq 1 ];then
    if [ "$1" == "cmp" ];then
       CMP="true"
    fi
fi

XMLCONFIG=$CARMSYS/bin/xmlconfig 
SCHEMA=`$XMLCONFIG data_model/schema 2>/dev/null | awk '{ print $3 }'`
DBHOST_CFG=`$XMLCONFIG db/host 2>/dev/null | awk '{ print $3 }'`
DBHOST1=`$XMLCONFIG db/host1 2>/dev/null | awk '{ print $3 }'`
DBHOST2=`$XMLCONFIG db/host2 2>/dev/null | awk '{ print $3 }'`
SERVICE_NAME=`$XMLCONFIG db/service_name 2>/dev/null | awk '{ print $3 }'`
D=`date +%H%M%d%m`
                                                                                                                  
if [ -z $DBHOST_CFG  ];then
    ping -c 1 $DBHOST1 > /dev/null 2>&1 
    if [ $? -eq 0 ] ; then 
           DBHOST=$DBHOST1
    else 
           DBHOST=$DBHOST2
    fi 
else
    DBHOST=$DBHOST_CFG
fi

CONNECT="carmdba/hemligt@${DBHOST}:1521/$SERVICE_NAME"
weekly_statistics()
{
    echo `date` "Running weekly statistics"
    sqlplus -s $CONNECT << EOF
    exec dbms_stats.gather_schema_stats(ownname => '$SCHEMA',estimate_percent => 50,cascade =>TRUE, degree=>6 );
EOF
}

cmp_daily_statistics()
{
    echo `date` "Running CMP daily statistics"
    rm -rf /tmp/gather_stats_cmp.sql
    for T in `cat $CARMUSR/etc/analyzetables_cmp`
    do

        echo "exec dbms_stats.gather_table_stats(ownname => '$SCHEMA',tabname => '$T',estimate_percent => 50, cascade => TRUE, degree=>6); " >> /tmp/gather_stats_cmp.sql
    done
    sqlplus -s $CONNECT << EOF
    spool /tmp/gather_stats_$D.log
    @/tmp/gather_stats_cmp.sql
    spool off
    exit
EOF

}

daily_statistics()
{
    echo `date` "Running daily statistics"
    rm -rf /tmp/gather_stats.sql
    for T in `cat $CARMUSR/etc/analyzetables`
    do

        echo "exec dbms_stats.gather_table_stats(ownname => '$SCHEMA',tabname => '$T',estimate_percent => dbms_stats.auto_sample_size, cascade => TRUE, degree => 6); " >> /tmp/gather_stats.sql
    done
    sqlplus -s $CONNECT << EOF
    spool /tmp/gather_stats_$D.log
    @/tmp/gather_stats.sql
    spool off
    exit
EOF

}

daily_statistics_no_histogram()
{
    echo `date` "Running daily statistics with no histogram"
    rm -rf /tmp/gather_stats_no_histogram.sql
    for T in `cat $CARMUSR/etc/analyzetables_no_histogram`
    do

        echo "exec dbms_stats.gather_table_stats(ownname => '$SCHEMA',tabname => '$T',estimate_percent => dbms_stats.auto_sample_size,method_opt=> 'FOR ALL COLUMNS SIZE 1',NO_INVALIDATE  => false ,cascade => true, degree => 6);" >> /tmp/gather_stats_no_histogram.sql
    done
    sqlplus -s $CONNECT << EOF
    spool /tmp/gather_stats_1_$D.log
    @/tmp/gather_stats_no_histogram.sql
    spool off
    exit
EOF
}

flush_shared_pool()
{
    echo `date` "Flushing shared pool"
    if [ -z $DBHOST_CFG ]; then
        CONNECT="flm_dba/jeppesen@${DBHOST1}:1521/$SERVICE_NAME"
        sqlplus -s $CONNECT << EOF
        alter system flush shared_pool
        /
        exit
EOF
        CONNECT="flm_dba/jeppesen@${DBHOST2}:1521/$SERVICE_NAME"
        sqlplus -s $CONNECT  << EOF
        alter system flush shared_pool
        /
        exit
EOF
    else
        CONNECT="system/hemligt@${DBHOST}:1521/$SERVICE_NAME"
        sqlplus -s $CONNECT  << EOF
        alter system flush shared_pool
        /
        exit
EOF
    fi
}                                                                                                                   

now=`date`
echo $now
echo "Starting Oracle statistics on $DBHOST for $SCHEMA"
day=`date +'%w'`
date=`date +'%d'`
WEEKDAYS=`$XMLCONFIG CMD_GATHER_STATS/weekly_days 2>/dev/null | awk '{ print $3 }'`
WEEKDATES=`$XMLCONFIG CMD_GATHER_STATS/weekly_dates 2>/dev/null | awk '{ print $3 }'`
if [ "$CMP" == "true" ]; then
    cmp_daily_statistics
else
    if [ -z $WEEKDAYS -a -z $WEEKDATES ]; then
        echo "Weekly statistics not configured"
        daily_statistics
    else
        echo $WEEKDAYS | grep $day > /dev/null 2>&1
        weekday=$?
        echo $WEEKDATES | grep $date > /dev/null 2>&1
        weekdate=$?
        if [ "$weekday" -eq "0" -o "$weekdate" -eq "0" ]; then
            weekly_statistics
        else
            daily_statistics
        fi
    fi
    daily_statistics_no_histogram
fi
flush_shared_pool
echo `date`
echo "Finished Oracle statistics on $DBHOST for $SCHEMA"

