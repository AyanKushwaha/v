#!/bin/bash
#
# Script for tracking local changes to a CARMUSR under version control with Mercurial.
#
# Prerequisites:
#   1. sqlite3, hg, bash, base64, gzip, tail and stat on path
#   2. Settings created in any of the following ways:
#       a) Beside the script, with the name local_carmusr_change_monitor.settings
#       b) In current users home folder, with the name 
#          .local_carmusr_change_monitor.settings
#       b) With arbitrary name and location, defined in the environment by 
#          the variable $CARMUSR_MONITOR_SETTINGS_LOCATION
#   3. The settings file is sourced and expected to contain definitions
#      of following three variables:
#        a) db_path (name and location of the sqlite db-file)
#        b) carmusr_path (location of the carmusr to monitor)
#        c) save_diffs (set to "enabled" or "disabled", depending on if you want
#           to save the full diff-contents or just the name of the changed file)
#
# Invokation:
#   * For updating no parameters should be given
#   * For listing full history, add the flag -history
#   * For showing the contents of a change, add the flag -extract followed
#     by the change ID shown in the history listing. (eg. -extract 123)
# 
# Behaviour:
#   * If changes are found, they are written on standard out
#   * If no changes are found, the script is completely silent
#
# Manually accessing local change history:
#   * By querying the database manually, you can see when current changes
#     were introduced and last confirmed.
#   * You can also see when old changes where introduced and last seen.
#   * If changes come and go many times, you have full history of every
#     time they appeared and disappeared.
#   * The diff contents are gziped and then encoded with base64. You must
#     decode and unzip before you can read their contents.
#
#
# Arvid Mullern-Aspegren, Jeppesen 2012


#### SQL templates ####

SCHEMA_DEF='CREATE TABLE modifications(changeid INTEGER PRIMARY KEY, modification varchar(1000), first_seen DATETIME DEFAULT CURRENT_TIMESTAMP, last_seen DATETIME, still_there boolean, gz_hgdiff_base64 clob);'

#### Function definitions ####

function read_settings {
    # The script settings are externalised, so that the core script can be easily
    # shared among multiple customers, sites and deployments.
    script_location="`dirname \"$0\"`"
    settings_file="$script_location/local_carmusr_change_monitor.settings"
    dev_settings_file="`cd;pwd`/.local_carmusr_change_monitor.settings"

    if [[ -f "$settings_file" ]]; then
        source "$settings_file"
    elif [[ -f $dev_settings_file ]]; then
        source $dev_settings_file
    elif [[ ! (-z $CARMUSR_MONITOR_SETTINGS_LOCATION) ]]; then
        source $CARMUSR_MONITOR_SETTINGS_LOCATION
    else
        echo Could not find settings file, exiting.
        exit 1
    fi

    if [[ -z "$db_path" ]]; then echo "db_path missing from settings" ;  exit 1;  fi
    if [[ -z "$carmusr_path" ]]; then echo "carmusr_path missing from settings" ;  exit 1;  fi
    if [[ -z "$save_diffs" ]]; then echo "save_diffs missing from settings";  exit 1;  fi
}

function help_text {
    echo " Invokation:"
    echo "  * To update the change db, use the flag -update "
    echo "  * To list full history, use the flag -history"
    echo "  * To show the contents of a specific change, use the flag"
    echo "    -extract followed by a change ID from the history listing"
    echo "    (eg. -extract 123)"
}

function check_db {
    type_of_check=$1

    if which /usr/bin/sqlite3 >>/dev/null 2>&1; then
        sqlt=/usr/bin/sqlite3
    else
        if which sqlite >>/dev/null 2>&1; then
            echo "Can't find sqlite"
            exit 1
        else
            sqlt=sqlite
        fi
    fi

    if [[ ! -f $db_path ]]; then
        echo -n "Can't find database '$db_path', "

        if [[ $type_of_check == "read_write" ]]; then
            echo "creating it now..."
            $sqlt $db_path "$SCHEMA_DEF"
        elif [[ $type_of_check == "read_only" ]]; then
            echo "exiting."
            false
        fi

        if [[ ! $? -eq 0 ]]; then
            exit 1
        fi
    fi

    if [[ $type_of_check == "read_write" ]]; then
        _db_owner=`stat -c %U "$db_path"`
        _me=`whoami`
        if [[ ! ($_db_owner == $_me) ]]; then
            echo "You ($_me) are not the owner ($_db_owner) of the change-database"
            exit 1
        fi
    fi
}

function get_mods_in_carmusr {
    cd $carmusr_path
    hg status -q
}

function get_mods_in_db {
    $sqlt $db_path "SELECT modification FROM modifications WHERE still_there='true';"
}

function insert_change_into_db {
    $sqlt $db_path "INSERT INTO modifications(modification, still_there, last_seen) VALUES('$@', 'true', CURRENT_TIMESTAMP);"
}

function remove_change_from_db {
    $sqlt $db_path "UPDATE modifications SET still_there='false' WHERE modification='$@';"
}

function confirm_change_in_db {
    $sqlt $db_path "UPDATE modifications SET last_seen=CURRENT_TIMESTAMP WHERE modification='$@' AND still_there='true';"
}

function list_full_history {
    $sqlt $db_path <<EOF
.mode column
.header on
.nullvalue NULL
.separator "|"
.width 8 50 19 19 11
SELECT changeid,modification,first_seen,last_seen,still_there FROM modifications ORDER BY last_seen ASC;
EOF
}

function store_diff_if_applicable {
    if [[ $save_diffs == "enabled" ]]; then

        cd $carmusr_path

        mod_description="$1"
        mod_file="`echo $1| head -n1 | cut -c3-`"

        diff_hg="`hg diff $mod_file | tail -n +4 | gzip -9 -n - | base64 -w 0`" 
        diff_db="`$sqlt $db_path \"SELECT gz_hgdiff_base64 FROM modifications WHERE modification='$mod_description' AND still_there='true'\"`"

        if [[ -z $diff_db ]]; then
            # There is no diff in the DB. Make one.
            $sqlt $db_path "UPDATE modifications SET gz_hgdiff_base64='$diff_hg' WHERE modification='$mod_description' AND still_there='true';"

        elif [[ ! ("$diff_hg" == "$diff_db") ]]; then
            # There is a diff in the DB, but it is not the same as the one in HG, 
            # "roll" the old mod-entry and set a diff on the new one.

            remove_change_from_db $mod_description
            insert_change_into_db $mod_description
            $sqlt $db_path "UPDATE modifications SET gz_hgdiff_base64='$diff_hg' WHERE modification='$mod_description' AND still_there='true';"

            echo "Content of already changed file changed again: $mod_file"
            number_of_changed_changes=$(($number_of_changed_changes + 1))

        else
            # There is a diff in the DB, and it is identical to the one in HG. Do nothing.
            true
        fi
    fi 
            
}

function extract_diff {
    if [[ $# -lt 1 ]]; then
        echo "Please provide a change ID"
    else
        raw_output="`$sqlt $db_path \"SELECT gz_hgdiff_base64 FROM modifications WHERE changeid=$1;\"`"
        if [[ -z "$raw_output" ]]; then
            echo "No diff found for change ID: $1 "
        else
            echo $raw_output | base64 -di | gzip -d -
        fi
    fi
}

function update_local_change_db {
    usr_tmp=/tmp/carmusr_mods.`date +%s`.$RANDOM
    db_tmp=/tmp/db_mods.`date +%s`.$RANDOM

    get_mods_in_carmusr > $usr_tmp
    get_mods_in_db > $db_tmp

    number_of_new_changes=0
    number_of_removed_changes=0
    number_of_changed_changes=0

    # Set newline as field separator (for iterating over change lists).
    IFS=$'\n'

    # Check for new things in the user.
    for usrmod in `cat $usr_tmp`; do
        change_is_new="true"
        for dbmod in `cat $db_tmp`; do
            if [[ $usrmod == $dbmod ]]; then
                change_is_new="false"
                break
            fi
        done

        if [[ $change_is_new == "true" ]]; then
            number_of_new_changes=$(($number_of_new_changes + 1))
            echo "New change: $usrmod"
            insert_change_into_db $usrmod
            store_diff_if_applicable $usrmod
        else
            store_diff_if_applicable $usrmod
            confirm_change_in_db $usrmod
        fi

    done

    # Mark any changes that are no longer present, as historic.
    for dbmod in `cat $db_tmp`; do
        change_is_no_longer_there="true"
        for usrmod in `cat $usr_tmp`; do
            if [[ $usrmod == $dbmod ]]; then
                change_is_no_longer_there="false"
                break
            fi
        done

        if [[ $change_is_no_longer_there == "true" ]]; then
            number_of_removed_changes=$(($number_of_removed_changes + 1))
            echo "Local change no longer present: $dbmod"
            remove_change_from_db $dbmod
        fi
    done

    # Clean-up temp files
    rm $usr_tmp $db_tmp

    if [[ $number_of_new_changes -gt 0 || $number_of_removed_changes -gt 0 || number_of_changed_changes -gt 0 ]]; then
        echo ""
        echo "$number_of_new_changes new local change(s)"
        echo "$number_of_removed_changes removed local change(s)"
        echo "$number_of_changed_changes re-changed local change(s)"
        echo ""
        echo "Found in $carmusr_path"
    fi

}

#### Script body ####

read_settings

if [[ $1 == "-history" ]]; then
    shift 1
    check_db read_only
    list_full_history $@
    exit $?
elif [[ $1 == "-extract" ]]; then
    shift 1
    check_db read_only
    extract_diff $@
    exit $?
elif [[ $1 == "-update" ]]; then
    check_db read_write
    update_local_change_db
    exit $?
elif [[ ! -z "$1" ]]; then
    echo "Unknown parameter/flag: $@"
    help_text
    exit 1
else
    help_text
    exit 1
fi    

