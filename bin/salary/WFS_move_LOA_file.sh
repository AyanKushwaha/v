#!/bin/sh

# Sets CARMUSR if not set
if [ -z "$CARMUSR" ]; then
    a=`pwd`
    cd `dirname $0`/..
    CARMUSR=`pwd`
    export CARMUSR
    cd $a
fi


mv /opt/Carmen/CARMTMP/ftp/in/SALARY_SEIP/WFS_CMS_TOR* ${CARMUSR}/current_carmdata/REPORTS/SALARY_WFS

