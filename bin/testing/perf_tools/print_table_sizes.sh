#!/bin/sh
if [[ $# -lt 1 ]]; then
    echo "Usage print_table_sizes.sh <schema_name> <db_conn> <table_name>"
    echo "If tablename = all, all tables are counted"
    exit 1
fi
if [[ -z $3 ]]; then
    tbl='all'
else
    tbl=$3
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

. $CARMUSR/etc/carmenv.sh

#| grep 'Entity' | sort -rn -k3 | awk '{printf "%10s, %10s\n", $2,$3}'
##| grep 'TABLE' | sort -rn -k3 | awk '{printf "%25s, %10s\n", $2,$3, $4}'
printf "%25s, %10s, %10s\n" "table" "total" "current"
sqlplus $1/$1@$2 <<EOF | grep 'TABLE' | sort -rn -k3 | awk '{printf "%25s, %10s, %10s\n", $2,$3, $4}'
SET SERVEROUTPUT ON 
set feedback off
set termout off
declare              
    text_1 VARCHAR2(256);
    text_2 VARCHAR2(256);
    count1 number;    
    count2 number;
begin
    DBMS_OUTPUT.PUT_LINE('LINEDANCE');
 for cur1 in (SELECT DISTINCT c_ent_name FROM 
                 DAVE_entity_tables where c_table_role='M' and 
		 ('$tbl'='all' or c_ent_name like '$tbl'))	

 loop
	text_1 := 'select count(1) from '||cur1.c_ent_name;
	execute immediate text_1 into count1;
        text_2 := 'select count(1) from '||cur1.c_ent_name ||' where next_revid=0 and deleted = ''N''';
        execute immediate text_2 into count2; 
	DBMS_OUTPUT.PUT_LINE('TABLE ' || cur1.C_ENT_NAME || ' ' || count1 || ' ' || count2);
end loop;

if  '$tbl' = 'all' then
	text_1 := 'select count(1) from dave_revision';
	execute immediate text_1 into count1;
	DBMS_OUTPUT.PUT_LINE('TABLE dave_revision ' || count1 ||' 0');
	text_1 := 'select count(1) from dave_updated_tables';
	execute immediate text_1 into count1;
	DBMS_OUTPUT.PUT_LINE('TABLE dave_updated_tables ' || count1 ||' 0');
end if;
END;
/
EOF

