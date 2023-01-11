WHENEVER SQLERROR EXIT 2 ROLLBACK
WHENEVER OSERROR EXIT 2 ROLLBACK
SET EXITCOMMIT OFF


------ dave_version_pre_check.sql ------
PROMPT Pre-checking version of dave
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 2 THEN NULL
            ELSE 'ERROR: Wrong Dave metadata version, expected dave >= 77 and dave_compat <= 77'
            END AS message
            FROM (SELECT * from dave_schemacfg
                WHERE c_cfg_type = 'dave'
                  AND c_cfg_group = 'module'
                  AND c_cfg_name = 'dave'
                  AND TO_NUMBER(SUBSTR(c_cfg_value, 1, INSTR(c_cfg_value, '.') - 1)) >= 77
            UNION ALL
            SELECT * from dave_schemacfg
                WHERE c_cfg_type = 'dave'
                  AND c_cfg_group = 'module'
                  AND c_cfg_name = 'dave_compat'
                  AND TO_NUMBER(SUBSTR(c_cfg_value, 1, INSTR(c_cfg_value, '.') - 1)) <= 77);

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20553, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_admin2_audit_pre_check.sql ------
PROMPT Pre-checking version of module admin2_audit
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module admin2_audit with version udm.admin2.07.04'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'admin2_audit'
              AND c_cfg_value = 'udm.admin2.07.04';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_admin2_datacontext_pre_check.sql ------
PROMPT Pre-checking version of module admin2_datacontext
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module admin2_datacontext with version udm.admin2.07.04'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'admin2_datacontext'
              AND c_cfg_value = 'udm.admin2.07.04';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_admin2_dig_pre_check.sql ------
PROMPT Pre-checking version of module admin2_dig
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module admin2_dig with version udm.admin2.07.04'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'admin2_dig'
              AND c_cfg_value = 'udm.admin2.07.04';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_admin2_rave_pre_check.sql ------
PROMPT Pre-checking version of module admin2_rave
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module admin2_rave with version udm.admin2.07.04'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'admin2_rave'
              AND c_cfg_value = 'udm.admin2.07.04';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air1_aircraft_pre_check.sql ------
PROMPT Pre-checking version of module air1_aircraft
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air1_aircraft with version udm.air1.11.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air1_aircraft'
              AND c_cfg_value = 'udm.air1.11.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air1_airport_pre_check.sql ------
PROMPT Pre-checking version of module air1_airport
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air1_airport with version udm.air1.11.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air1_airport'
              AND c_cfg_value = 'udm.air1.11.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air1_aoc_pre_check.sql ------
PROMPT Pre-checking version of module air1_aoc
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air1_aoc with version udm.air1.11.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air1_aoc'
              AND c_cfg_value = 'udm.air1.11.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air1_core_pre_check.sql ------
PROMPT Pre-checking version of module air1_core
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air1_core with version udm.air1.11.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air1_core'
              AND c_cfg_value = 'udm.air1.11.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air1_crew_pre_check.sql ------
PROMPT Pre-checking version of module air1_crew
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air1_crew with version udm.air1.11.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air1_crew'
              AND c_cfg_value = 'udm.air1.11.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air1_ctraining_pre_check.sql ------
PROMPT Pre-checking version of module air1_ctraining
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air1_ctraining with version udm.air1.11.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air1_ctraining'
              AND c_cfg_value = 'udm.air1.11.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air1_dutytype_pre_check.sql ------
PROMPT Pre-checking version of module air1_dutytype
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air1_dutytype with version udm.air1.11.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air1_dutytype'
              AND c_cfg_value = 'udm.air1.11.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air1_iocs_pre_check.sql ------
PROMPT Pre-checking version of module air1_iocs
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air1_iocs with version udm.air1.11.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air1_iocs'
              AND c_cfg_value = 'udm.air1.11.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air1_manpower_pre_check.sql ------
PROMPT Pre-checking version of module air1_manpower
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air1_manpower with version udm.air1.11.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air1_manpower'
              AND c_cfg_value = 'udm.air1.11.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air1_origsuffix_pre_check.sql ------
PROMPT Pre-checking version of module air1_origsuffix
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air1_origsuffix with version udm.air1.11.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air1_origsuffix'
              AND c_cfg_value = 'udm.air1.11.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air1_planning_pre_check.sql ------
PROMPT Pre-checking version of module air1_planning
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air1_planning with version udm.air1.11.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air1_planning'
              AND c_cfg_value = 'udm.air1.11.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air1_tracking_pre_check.sql ------
PROMPT Pre-checking version of module air1_tracking
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air1_tracking with version udm.air1.11.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air1_tracking'
              AND c_cfg_value = 'udm.air1.11.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air1_urm_pre_check.sql ------
PROMPT Pre-checking version of module air1_urm
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air1_urm with version udm.air1.11.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air1_urm'
              AND c_cfg_value = 'udm.air1.11.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air_jmp_3_2_pre_check.sql ------
PROMPT Pre-checking version of module air_jmp_3_2
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air_jmp_3_2 with version jmp.19.4.6'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_3_2'
              AND c_cfg_value = 'jmp.19.4.6';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air_jmp_access_pre_check.sql ------
PROMPT Pre-checking version of module air_jmp_access
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air_jmp_access with version jmp.19.4.6'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_access'
              AND c_cfg_value = 'jmp.19.4.6';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air_jmp_attributes_pre_check.sql ------
PROMPT Pre-checking version of module air_jmp_attributes
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air_jmp_attributes with version jmp.19.4.6'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_attributes'
              AND c_cfg_value = 'jmp.19.4.6';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air_jmp_bid_general_pre_check.sql ------
PROMPT Pre-checking version of module air_jmp_bid_general
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air_jmp_bid_general with version jmp.19.4.6'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_bid_general'
              AND c_cfg_value = 'jmp.19.4.6';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air_jmp_bid_transaction_pre_check.sql ------
PROMPT Pre-checking version of module air_jmp_bid_transaction
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air_jmp_bid_transaction with version jmp.19.4.6'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_bid_transaction'
              AND c_cfg_value = 'jmp.19.4.6';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air_jmp_common_establishment_pre_check.sql ------
PROMPT Pre-checking version of module air_jmp_common_establishment
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air_jmp_common_establishment with version jmp.19.4.6'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_common_establishment'
              AND c_cfg_value = 'jmp.19.4.6';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air_jmp_comparer_extension_pre_check.sql ------
PROMPT Pre-checking version of module air_jmp_comparer_extension
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air_jmp_comparer_extension with version jmp.19.4.6'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_comparer_extension'
              AND c_cfg_value = 'jmp.19.4.6';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air_jmp_core_pre_check.sql ------
PROMPT Pre-checking version of module air_jmp_core
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air_jmp_core with version jmp.19.4.6'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_core'
              AND c_cfg_value = 'jmp.19.4.6';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air_jmp_ctraining_pre_check.sql ------
PROMPT Pre-checking version of module air_jmp_ctraining
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air_jmp_ctraining with version jmp.19.4.6'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_ctraining'
              AND c_cfg_value = 'jmp.19.4.6';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air_jmp_patch_data_pre_check.sql ------
PROMPT Pre-checking version of module air_jmp_patch_data
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air_jmp_patch_data with version jmp.19.4.6'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_patch_data'
              AND c_cfg_value = 'jmp.19.4.6';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air_jmp_resource_consumption_pre_check.sql ------
PROMPT Pre-checking version of module air_jmp_resource_consumption
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air_jmp_resource_consumption with version jmp.19.4.6'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_resource_consumption'
              AND c_cfg_value = 'jmp.19.4.6';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air_jmp_separate_planned_tasks_pre_check.sql ------
PROMPT Pre-checking version of module air_jmp_separate_planned_tasks
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air_jmp_separate_planned_tasks with version jmp.19.4.6'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_separate_planned_tasks'
              AND c_cfg_value = 'jmp.19.4.6';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air_jmp_status_report_pre_check.sql ------
PROMPT Pre-checking version of module air_jmp_status_report
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air_jmp_status_report with version jmp.19.4.6'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_status_report'
              AND c_cfg_value = 'jmp.19.4.6';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air_new_manpower_pre_check.sql ------
PROMPT Pre-checking version of module air_new_manpower
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air_new_manpower with version jmp.19.4.6'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_new_manpower'
              AND c_cfg_value = 'jmp.19.4.6';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_air_opt_manpower_pre_check.sql ------
PROMPT Pre-checking version of module air_opt_manpower
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module air_opt_manpower with version jmp.19.4.6'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_opt_manpower'
              AND c_cfg_value = 'jmp.19.4.6';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_cmp_transition_pre_check.sql ------
PROMPT Pre-checking version of module cmp_transition
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module cmp_transition with version udm.01.02'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'cmp_transition'
              AND c_cfg_value = 'udm.01.02';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_custom_crew_attributes_pre_check.sql ------
PROMPT Pre-checking version of module custom_crew_attributes
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module custom_crew_attributes with version carmusr_jmp.01.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'custom_crew_attributes'
              AND c_cfg_value = 'carmusr_jmp.01.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_leave_rules_configuration_pre_check.sql ------
PROMPT Pre-checking version of module leave_rules_configuration
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module leave_rules_configuration with version carmusr_jmp.01.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'leave_rules_configuration'
              AND c_cfg_value = 'carmusr_jmp.01.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_recurrent_configuration_pre_check.sql ------
PROMPT Pre-checking version of module recurrent_configuration
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module recurrent_configuration with version carmusr_jmp.01.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'recurrent_configuration'
              AND c_cfg_value = 'carmusr_jmp.01.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_accounts_pre_check.sql ------
PROMPT Pre-checking version of module sas_accounts
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_accounts with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_accounts'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_admin_pre_check.sql ------
PROMPT Pre-checking version of module sas_admin
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_admin with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_admin'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_air_aircraft_pre_check.sql ------
PROMPT Pre-checking version of module sas_air_aircraft
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_air_aircraft with version udm.1.11'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_air_aircraft'
              AND c_cfg_value = 'udm.1.11';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_air_core_pre_check.sql ------
PROMPT Pre-checking version of module sas_air_core
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_air_core with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_air_core'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_air_crew_pre_check.sql ------
PROMPT Pre-checking version of module sas_air_crew
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_air_crew with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_air_crew'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_air_tracking_pre_check.sql ------
PROMPT Pre-checking version of module sas_air_tracking
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_air_tracking with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_air_tracking'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_annotations_pre_check.sql ------
PROMPT Pre-checking version of module sas_annotations
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_annotations with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_annotations'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_attributes_pre_check.sql ------
PROMPT Pre-checking version of module sas_attributes
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_attributes with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_attributes'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_base_breaks_pre_check.sql ------
PROMPT Pre-checking version of module sas_base_breaks
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_base_breaks with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_base_breaks'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_bought_days_pre_check.sql ------
PROMPT Pre-checking version of module sas_bought_days
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_bought_days with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_bought_days'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_calloutlist_pre_check.sql ------
PROMPT Pre-checking version of module sas_calloutlist
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_calloutlist with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_calloutlist'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_checkin_pre_check.sql ------
PROMPT Pre-checking version of module sas_checkin
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_checkin with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_checkin'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_cp_bid_pre_check.sql ------
PROMPT Pre-checking version of module sas_cp_bid
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_cp_bid with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_cp_bid'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_crew_meals_pre_check.sql ------
PROMPT Pre-checking version of module sas_crew_meals
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_crew_meals with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_crew_meals'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_crew_needs_pre_check.sql ------
PROMPT Pre-checking version of module sas_crew_needs
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_crew_needs with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_crew_needs'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_crew_user_filter_pre_check.sql ------
PROMPT Pre-checking version of module sas_crew_user_filter
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_crew_user_filter with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_crew_user_filter'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_dig_recipients_pre_check.sql ------
PROMPT Pre-checking version of module sas_dig_recipients
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_dig_recipients with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_dig_recipients'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_financial_pre_check.sql ------
PROMPT Pre-checking version of module sas_financial
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_financial with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_financial'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_handover_reports_pre_check.sql ------
PROMPT Pre-checking version of module sas_handover_reports
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_handover_reports with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_handover_reports'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_hotel_bookings_pre_check.sql ------
PROMPT Pre-checking version of module sas_hotel_bookings
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_hotel_bookings with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_hotel_bookings'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_indexes_pre_check.sql ------
PROMPT Pre-checking version of module sas_indexes
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_indexes with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_indexes'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_integration_pre_check.sql ------
PROMPT Pre-checking version of module sas_integration
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_integration with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_integration'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_leave_entitlement_pre_check.sql ------
PROMPT Pre-checking version of module sas_leave_entitlement
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_leave_entitlement with version carmusr_jmp.1.02'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_leave_entitlement'
              AND c_cfg_value = 'carmusr_jmp.1.02';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_leave_parameters_pre_check.sql ------
PROMPT Pre-checking version of module sas_leave_parameters
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_leave_parameters with version udm.1.02'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_leave_parameters'
              AND c_cfg_value = 'udm.1.02';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_leave_reduction_pre_check.sql ------
PROMPT Pre-checking version of module sas_leave_reduction
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_leave_reduction with version carmusr_jmp.1.02'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_leave_reduction'
              AND c_cfg_value = 'carmusr_jmp.1.02';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_legality_pre_check.sql ------
PROMPT Pre-checking version of module sas_legality
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_legality with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_legality'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_manpower_accumulators_pre_check.sql ------
PROMPT Pre-checking version of module sas_manpower_accumulators
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_manpower_accumulators with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_manpower_accumulators'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_nop_crew_pre_check.sql ------
PROMPT Pre-checking version of module sas_nop_crew
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_nop_crew with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_nop_crew'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_notification_pre_check.sql ------
PROMPT Pre-checking version of module sas_notification
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_notification with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_notification'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_passive_bookings_pre_check.sql ------
PROMPT Pre-checking version of module sas_passive_bookings
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_passive_bookings with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_passive_bookings'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_paxlst_pre_check.sql ------
PROMPT Pre-checking version of module sas_paxlst
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_paxlst with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_paxlst'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_planning_pre_check.sql ------
PROMPT Pre-checking version of module sas_planning
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_planning with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_planning'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_published_pre_check.sql ------
PROMPT Pre-checking version of module sas_published
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_published with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_published'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_rave_pre_check.sql ------
PROMPT Pre-checking version of module sas_rave
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_rave with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_rave'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_rule_violation_pre_check.sql ------
PROMPT Pre-checking version of module sas_rule_violation
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_rule_violation with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_rule_violation'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_special_local_transport_pre_check.sql ------
PROMPT Pre-checking version of module sas_special_local_transport
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_special_local_transport with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_special_local_transport'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_special_schedules_pre_check.sql ------
PROMPT Pre-checking version of module sas_special_schedules
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_special_schedules with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_special_schedules'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_standby_pre_check.sql ------
PROMPT Pre-checking version of module sas_standby
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_standby with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_standby'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_table_accumulators_pre_check.sql ------
PROMPT Pre-checking version of module sas_table_accumulators
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_table_accumulators with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_table_accumulators'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_training_pre_check.sql ------
PROMPT Pre-checking version of module sas_training
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_training with version sas.dm.1.01'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_training'
              AND c_cfg_value = 'sas.dm.1.01';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_training_cnx_time_pre_check.sql ------
PROMPT Pre-checking version of module sas_training_cnx_time
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_training_cnx_time with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_training_cnx_time'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT


------ module_version_sas_transport_bookings_pre_check.sql ------
PROMPT Pre-checking version of module sas_transport_bookings
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Expected module sas_transport_bookings with version sas.dm.1.00'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'sas_transport_bookings'
              AND c_cfg_value = 'sas.dm.1.00';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20503, error_check_output);
    END IF;
END;
/
PROMPT

PROMPT Start of migration. Set guard ...

INSERT INTO dave_metadata_status (state) VALUES ('Blocked: Schema migration');

COMMIT;


------ disable_all_triggers_pre_ddl.trg ------

-- Disable all triggers
DECLARE
    CURSOR trigger_cur IS
    SELECT trigger_name
      FROM USER_TRIGGERS;
    alter_stmt VARCHAR2(100);
BEGIN
    FOR rec IN trigger_cur LOOP
        alter_stmt := 'ALTER TRIGGER '||rec.trigger_name||' DISABLE';
        EXECUTE IMMEDIATE alter_stmt;
    END LOOP;
END;
/

COMMIT;


------ recompile_database_objects_post_ddl.trg ------

-- Recompile invalid database objects
DECLARE
    CURSOR package_cur IS
    SELECT object_name
      FROM USER_OBJECTS
      WHERE OBJECT_TYPE = 'PACKAGE'
        AND STATUS = 'INVALID';

    CURSOR package_body_cur IS
    SELECT object_name
      FROM USER_OBJECTS
      WHERE OBJECT_TYPE = 'PACKAGE BODY'
        AND STATUS = 'INVALID';

    CURSOR trigger_cur IS
    SELECT object_name
      FROM USER_OBJECTS
      WHERE OBJECT_TYPE = 'TRIGGER'
        AND STATUS = 'INVALID';
    alter_stmt VARCHAR2(100);
BEGIN
    FOR rec IN package_cur LOOP
        alter_stmt := 'ALTER PACKAGE '||rec.object_name||' COMPILE PACKAGE';
        EXECUTE IMMEDIATE alter_stmt;
    END LOOP;

    FOR rec IN package_body_cur LOOP
        alter_stmt := 'ALTER PACKAGE '||rec.object_name||' COMPILE BODY';
        EXECUTE IMMEDIATE alter_stmt;
    END LOOP;

    FOR rec IN trigger_cur LOOP
        alter_stmt := 'ALTER TRIGGER '||rec.object_name||' COMPILE';
        EXECUTE IMMEDIATE alter_stmt;
    END LOOP;
END;
/

COMMIT;


------ enable_all_triggers_post_ddl.trg ------

-- Enable all triggers
DECLARE
    CURSOR trigger_cur IS
    SELECT trigger_name
      FROM USER_TRIGGERS;
    alter_stmt VARCHAR2(100);
BEGIN
    FOR rec IN trigger_cur LOOP
        alter_stmt := 'ALTER TRIGGER '||rec.trigger_name||' ENABLE';
        EXECUTE IMMEDIATE alter_stmt;
    END LOOP;
END;
/

COMMIT;

PROMPT End of migration. Unset guard ...

DELETE FROM dave_metadata_status;

COMMIT;
