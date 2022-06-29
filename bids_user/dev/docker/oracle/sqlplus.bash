#!/usr/bin/env bash

# script should pickup $ORACLE_HOME and $ORACLE_PWD variables from docker
# env, please, consider to add them if your environment doesn't has it...

export ORA_HOST='127.0.0.1'
export PATH="${ORACLE_HOME}/bin:${PATH}"
export SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd ${SCRIPT_DIR}/

# DBA
SQLPLUS_CONNECTION_STRING="sys/${ORACLE_PWD}@//${ORA_HOST}/orcl"
echo '@dba/01-create-tablespaces-and-application-user.sql'     | sqlplus -s ${SQLPLUS_CONNECTION_STRING} as SYSDBA >/tmp/migration.log && echo 'DBA complete.'

# DDL
SQLPLUS_CONNECTION_STRING="cp_sas/cp_sas@//${ORA_HOST}/orcl"
echo '@ddl/01-create-sequences.sql'                            | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo '@ddl/02-create-tables-constraints-and-indexes.sql'       | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "
DDL complete."

# DML
echo "@dml/CP_SAS_USERS.sql"                                  | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_GROUPS.sql"                                 | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_USERGROUPS.sql"                             | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_QUALIFICATIONS.sql"                         | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_USERQUALIFICATIONS.sql"                     | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_PERIODS.sql"                                | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_NOTIFICATIONS.sql"                          | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_NOTIFICATIONMESSAGEPARAMETERS.sql"          | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_KEYLOCK.sql"                                | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_USERROLES.sql"                              | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_USERATTRIBUTES.sql"                         | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_BIDGROUPS.sql"                              | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_BIDGROUPORDER.sql"                          | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_BIDS.sql"                                   | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_BIDORDER.sql"                               | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_BIDPROPERTIES.sql"                          | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_BIDPROPERTYENTRIES.sql"                     | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_TRIPSEARCHES.sql"                           | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_SEARCHPROPERTIES.sql"                       | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_SEARCHPROPERTYENTRIES.sql"                  | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_USERSETTINGS.sql"                           | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_BATCHJOBS.sql"                              | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_QRTZ_JOB_LISTENERS.sql"                     | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_QRTZ_SIMPLE_TRIGGERS.sql"                   | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_QRTZ_CRON_TRIGGERS.sql"                     | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_QRTZ_TRIGGER_LISTENERS.sql"                 | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_QRTZ_PAUSED_TRIGGER_GRPS.sql"               | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_QRTZ_FIRED_TRIGGERS.sql"                    | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_QRTZ_SCHEDULER_STATE.sql"                   | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_QRTZ_LOCKS.sql"                             | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_REQUESTLOGS.sql"                            | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_REQUESTLOGDETAILS.sql"                      | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_REQUESTLOGERRORS.sql"                       | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_AUDITTRAILS.sql"                            | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_USERMESSAGES.sql"                           | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_BACKENDREQUESTS.sql"                        | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_QRTZ_JOB_DETAILS.sql"                       | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_QRTZ_TRIGGERS.sql"                          | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_QRTZ_BLOB_TRIGGERS.sql"                     | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_QRTZ_CALENDARS.sql"                         | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_USERDIRROLES.sql"                           | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "@dml/CP_SAS_USERDIRECTORY.sql"                          | sqlplus -s ${SQLPLUS_CONNECTION_STRING} >>/tmp/migration.log && echo -ne '.'
echo "
DML complete."
