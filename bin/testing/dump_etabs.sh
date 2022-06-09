#!/bin/bash
# $Header$

_DB_LOC="`echo $DB_URL |sed -e 's/oracle:\(.\+\)%.\+\//\1\//' | sed -e 's/oracle://'`";

tables=`
sqlplus -S $_DB_LOC <<EOF ;
set heading off
set feedback off

SELECT c_ent_name
FROM dave_entity_tables
WHERE c_table_role = 'M'
ORDER BY c_ent_name;

EOF
`

config_file=$(mktemp)
cat > ${config_file} <<EOF
<?xml version="1.0" ?>
<etabdump version="0.7" defmode="ignore">
EOF

cmdline=" $@ "
for table in ${tables}
do
    m=`expr match "$cmdline" " .*$table "`
    if [ $m -eq 0 ]
    then
       cat >> ${config_file} <<EOF
<filter entity="${table}">
  <field dname="revid">&lt; 0</field>
</filter>
EOF
    else
	echo Dumping full table $table

    fi
    cat >> ${config_file} <<EOF
<map entity="${table}" etab="${table}"></map>
EOF
done

cat >> ${config_file} <<EOF
</etabdump>
EOF

echo "Export data from schema ${DB_SCHEMA} in ${DB_URL}"
# echo "$(cat ${config_file})"
$CARMSYS/bin/carmrunner etabdump -c ${DB_URL} -s ${DB_SCHEMA} -f ${config_file} .

