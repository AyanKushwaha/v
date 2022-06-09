#!/bin/sh
if [ $# -lt 4 ];then
    echo "Usage: get_db_changes_between_times.sh <schema> <db_connection> <start> <end>"
    echo "Time format is '20090415 12:00:00'"
    echo "Requires working sqlplus, given by etc/carmenv.sh"
    exit 1
fi

# Sets the CARMUSR variable, if it is not set
if [ -z "$CARMUSR" ]; then
    a=`pwd`
    cd `dirname $0`
    while [ `pwd` != '/' -a ! -d "crc" ]; do
        cd ..
    done
    CARMUSR=`pwd`
    export CARMUSR
    cd $a
fi

echo CARMUSR: $CARMUSR
# Sets CARMDATA, CARMSYS, CARMTMP and variables from CONFIG_extension.
. $CARMUSR/etc/carmenv.sh



_schema=$1
_dbconn=$2
_start=$3
_end=$4

echo "Following changes in db between "${_start}" and "${_end}" for schema:"${_schema}

sqlplus  -s  ${_schema}/${_schema}@${_dbconn} <<EOF| grep 'Entity'
SET SERVEROUTPUT ON 
set feedback off
set termout off
declare              
    text_nt VARCHAR2(256);
    count1 number;        
    start_ts number;
    end_ts number;
    max_revid number;
    min_revid number;
    max_commitid number;
    min_commitid number;
begin
 SELECT (to_date('${_start}','yyyymmdd hh24:mi:ss')-
         to_date('19860101','yyyymmdd'))*24*60*60 into start_ts from dual ;
 SELECT (to_date('${_end}','yyyymmdd hh24:mi:ss')-
         to_date('19860101','yyyymmdd'))*24*60*60 into end_ts from dual ;
 select revid, commitid into min_revid, min_commitid from dave_revision 
                              where commitid =
                             (select min(commitid) from DAVE_REVISION 
                              where committs >= start_ts );
 select revid, commitid into max_revid , max_commitid from dave_revision 
                              where commitid =
                              (select max(commitid) from DAVE_REVISION 
                               where committs <= end_ts and commitid < 999999999 );
  for cur1 in (SELECT DISTINCT(TABLENAME) FROM 
                   DAVE_UPDATED_TABLES U INNER JOIN 
            	 DAVE_REVISION R  ON R.REVID = U.REVID 
                 WHERE R.COMMITID > min_commitid AND 
		R.COMMITID <= max_commitid)	
  loop
	text_nt := 'select count(1) from ${_schema}.' || cur1.TABLENAME || 
		' where revid <='|| max_revid ||
		' and revid >= '||min_revid;

	execute immediate text_nt into count1;
	if count1 > 0 then
	  DBMS_OUTPUT.PUT_LINE('Entity ' || cur1.TABLENAME || ': ' || count1);
	end if ;
end loop;
END;
/
EOF
