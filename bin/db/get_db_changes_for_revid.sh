#!/bin/sh
# $Header: /opt/Carmen/CVS/sk_cms_user/bin/get_db_changes_for_revid.sh,v 1.1 2009/05/05 11:34:32 janca Exp $
# Author: Janne Carlsson, 2009-05-05
#
if [ $# -lt 2 ];then
    echo "Usage: get_db_changes_for_revid.sh <schema> <start>"
    echo "Must be executed in CARMUSR root dir"
    echo "The script extracts all column data from all tables that was affected by the"
    echo "supplied revid (normally the reported revid from a save operation)."
    echo ""
    echo "As for now only changes made by the user that executes the script are considered."
    echo "(Needs to be tested more!)"
    exit 1
fi

CARMUSR=$PWD
export CARMUSR

. ./bin/carmenv.sh

XMLCONFIG=$CARMSYS/bin/xmlconfig
DBHOST_CFG=`$XMLCONFIG db/host 2>/dev/null | awk '{ print $3 }'`
DBHOST1=`$XMLCONFIG db/host1 2>/dev/null | awk '{ print $3 }'`
DBHOST2=`$XMLCONFIG db/host2 2>/dev/null | awk '{ print $3 }'`
SERVICE_NAME=`$XMLCONFIG db/service_name 2>/dev/null | awk '{ print $3 }'`

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

_schema=$1
_start=$2
echo "Changes in db for revid: "${_start}" in schema: "${_schema}" by user: "${USER}
sqlplus -s ${_schema}/${_schema}@${DBHOST}:1521/${SERVICE_NAME} <<EOF 
SET SERVEROUTPUT ON 
set feedback off
set lines 500
set pages 80
set termout off

create or replace package dynamic_cursor is
  type t_crs is ref cursor;
  procedure dyn_sel (
       tab_name   in varchar2,
       col_name   in varchar2,
       where_col  in varchar2,
       val        in varchar2,
       crs        in out t_crs);
  procedure openCursor (
       tab_name   in varchar2,
       col_name   in varchar2,
       where_col  in varchar2,
       rev        in number);
end dynamic_cursor;             
/

create or replace package body dynamic_cursor as
   procedure dyn_sel (
          tab_name   in varchar2,
          col_name   in varchar2,
          where_col  in varchar2,
          val        in varchar2,
          crs        in out t_crs)
   is
     stmt varchar2(100);
   begin
   stmt := 'select '||col_name||' from ${_schema}.'||tab_name||' where '||where_col||'= :1 ';
   open crs for stmt using val;
   end dyn_sel;

   procedure openCursor (
          tab_name   in varchar2,
          col_name   in varchar2,
          where_col  in varchar2,
          rev        in number)
   is
     tc t_crs;
     f1 varchar2(50);
   begin
     dyn_sel(tab_name,col_name,where_col,rev,tc);
     loop
       fetch tc into f1;
       exit when tc%notfound;
       dbms_output.put(f1||', ');
     end loop;
   end openCursor;
     
end dynamic_cursor;     
/

declare              
    max_revid number;
    min_revid number;
    revid number;
    max_commitid number;
    min_commitid number;
    tbl_name varchar2(256);
    col_name varchar2(256);
    cursor cur2(tbl IN VARCHAR2) is
      select distinct column_name from all_tab_columns where table_name=upper(tbl);
      
begin
    select revid, commitid into min_revid, min_commitid from dave_revision where revid = ${_start};
    select revid, commitid into max_revid , max_commitid from dave_revision where commitid = (select max(commitid) from DAVE_REVISION where commitid < 999999999);
    revid := min_revid;
    for cur1 in (SELECT DISTINCT TABLENAME FROM DAVE_UPDATED_TABLES U INNER JOIN DAVE_REVISION R  ON R.REVID = U.REVID WHERE R.COMMITID >= min_commitid AND R.COMMITID <= max_commitid AND R.CLIUSER='${USER}')
    loop
      tbl_name := upper(cur1.TABLENAME);
      DBMS_OUTPUT.PUT_LINE('-----------------------------------------------------');
      DBMS_OUTPUT.PUT_LINE('---- '||tbl_name||' ----');
      DBMS_OUTPUT.PUT_LINE('---- next_revid:'||revid);
      open cur2(tbl_name);
      loop
        fetch cur2 into col_name;
        exit when cur2%NOTFOUND;
        DBMS_OUTPUT.PUT(rpad(col_name,30,' ')||',');
        dynamic_cursor.openCursor(tbl_name, col_name, 'NEXT_REVID', revid);
        DBMS_OUTPUT.NEW_LINE;
      end loop;
      close cur2;
      DBMS_OUTPUT.NEW_LINE;
      DBMS_OUTPUT.PUT_LINE('---- revid:'||max_revid);
      open cur2(tbl_name);
      loop
        fetch cur2 into col_name;
        exit when cur2%NOTFOUND;
        DBMS_OUTPUT.PUT(rpad(col_name,30,' ')||',');
        dynamic_cursor.openCursor(tbl_name, col_name, 'REVID', revid);
        DBMS_OUTPUT.NEW_LINE;
      end loop;
      close cur2;
      DBMS_OUTPUT.NEW_LINE;
      DBMS_OUTPUT.NEW_LINE;
      
    end loop;
    exception
      when others then
        DBMS_OUTPUT.PUT_LINE(SQLERRM);
    
    
END;
/
drop package dynamic_cursor;
EOF

