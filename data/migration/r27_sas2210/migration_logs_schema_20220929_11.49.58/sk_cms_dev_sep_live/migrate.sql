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
            WHEN 0 THEN 'Expected module air_jmp_3_2 with version jmp.19.16.4300'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_3_2'
              AND c_cfg_value = 'jmp.19.16.4300';

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
            WHEN 0 THEN 'Expected module air_jmp_access with version jmp.19.16.4300'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_access'
              AND c_cfg_value = 'jmp.19.16.4300';

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
            WHEN 0 THEN 'Expected module air_jmp_attributes with version jmp.19.16.4300'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_attributes'
              AND c_cfg_value = 'jmp.19.16.4300';

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
            WHEN 0 THEN 'Expected module air_jmp_bid_general with version jmp.19.16.4300'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_bid_general'
              AND c_cfg_value = 'jmp.19.16.4300';

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
            WHEN 0 THEN 'Expected module air_jmp_bid_transaction with version jmp.19.16.4300'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_bid_transaction'
              AND c_cfg_value = 'jmp.19.16.4300';

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
            WHEN 0 THEN 'Expected module air_jmp_common_establishment with version jmp.19.16.4300'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_common_establishment'
              AND c_cfg_value = 'jmp.19.16.4300';

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
            WHEN 0 THEN 'Expected module air_jmp_comparer_extension with version jmp.19.16.4300'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_comparer_extension'
              AND c_cfg_value = 'jmp.19.16.4300';

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
            WHEN 0 THEN 'Expected module air_jmp_core with version jmp.19.16.4300'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_core'
              AND c_cfg_value = 'jmp.19.16.4300';

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
            WHEN 0 THEN 'Expected module air_jmp_ctraining with version jmp.19.16.4300'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_ctraining'
              AND c_cfg_value = 'jmp.19.16.4300';

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
            WHEN 0 THEN 'Expected module air_jmp_patch_data with version jmp.19.16.4300'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_patch_data'
              AND c_cfg_value = 'jmp.19.16.4300';

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
            WHEN 0 THEN 'Expected module air_jmp_resource_consumption with version jmp.19.16.4300'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_resource_consumption'
              AND c_cfg_value = 'jmp.19.16.4300';

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
            WHEN 0 THEN 'Expected module air_jmp_separate_planned_tasks with version jmp.19.16.4300'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_separate_planned_tasks'
              AND c_cfg_value = 'jmp.19.16.4300';

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
            WHEN 0 THEN 'Expected module air_jmp_status_report with version jmp.19.16.4300'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_jmp_status_report'
              AND c_cfg_value = 'jmp.19.16.4300';

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
            WHEN 0 THEN 'Expected module air_new_manpower with version jmp.19.16.4300'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_new_manpower'
              AND c_cfg_value = 'jmp.19.16.4300';

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
            WHEN 0 THEN 'Expected module air_opt_manpower with version jmp.19.16.4300'
            ELSE NULL
            END AS message
            FROM dave_schemacfg
            WHERE c_cfg_type = 'dave'
              AND c_cfg_group = 'module'
              AND c_cfg_name = 'air_opt_manpower'
              AND c_cfg_value = 'jmp.19.16.4300';

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


------ drop_entity_crew_filter_group_tag_pre_check.sql ------
PROMPT Pre-checking entity crew_filter_group_tag before dropping for broken references
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN NULL
            ELSE 'Entity "crew_filter_group_tag" is referenced from unknown entities ' || LISTAGG(c_ent_name, ', ')
                WITHIN GROUP (ORDER BY c_ent_name)
            END AS message
            FROM dave_entity_fks
            WHERE c_fk_tgtname = 'crew_filter_group_tag';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20507, error_check_output);
    END IF;
END;
/
PROMPT


------ drop_entity_estr_calc_node_node_tag_pre_check.sql ------
PROMPT Pre-checking entity estr_calc_node_node_tag before dropping for broken references
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN NULL
            ELSE 'Entity "estr_calc_node_node_tag" is referenced from unknown entities ' || LISTAGG(c_ent_name, ', ')
                WITHIN GROUP (ORDER BY c_ent_name)
            END AS message
            FROM dave_entity_fks
            WHERE c_fk_tgtname = 'estr_calc_node_node_tag';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20507, error_check_output);
    END IF;
END;
/
PROMPT


------ drop_entity_estr_calc_node_tag_pre_check.sql ------
PROMPT Pre-checking entity estr_calc_node_tag before dropping for broken references
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN NULL
            ELSE 'Entity "estr_calc_node_tag" is referenced from unknown entities ' || LISTAGG(c_ent_name, ', ')
                WITHIN GROUP (ORDER BY c_ent_name)
            END AS message
            FROM dave_entity_fks
            WHERE c_fk_tgtname = 'estr_calc_node_tag'
              AND c_ent_name NOT IN ('estr_calc_node_node_tag');

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20507, error_check_output);
    END IF;
END;
/
PROMPT


------ drop_entity_resource_group_tag_pre_check.sql ------
PROMPT Pre-checking entity resource_group_tag before dropping for broken references
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN NULL
            ELSE 'Entity "resource_group_tag" is referenced from unknown entities ' || LISTAGG(c_ent_name, ', ')
                WITHIN GROUP (ORDER BY c_ent_name)
            END AS message
            FROM dave_entity_fks
            WHERE c_fk_tgtname = 'resource_group_tag'
              AND c_ent_name NOT IN ('crew_filter_group_tag');

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20507, error_check_output);
    END IF;
END;
/
PROMPT


------ table_name_uniqueness_bought_days_svs_pre_check.sql ------
PROMPT Pre-checking table bought_days_svs for table name uniqueness
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS

        SELECT CASE COUNT(*)
          WHEN 0 THEN NULL
          ELSE 'Object with name "bought_days_svs" already exists'
          END AS message
          FROM USER_OBJECTS
          WHERE OBJECT_NAME = 'BOUGHT_DAYS_SVS'
          AND OBJECT_TYPE IN(
            'TABLE',
            'VIEW',
            'SEQUENCE',
            'SYNONYM',
            'PROCEDURE',
            'FUNCTION',
            'PACKAGE',
            'VIEW',
            'TYPE',
            'OPERATOR');

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20504, error_check_output);
    END IF;
END;
/
PROMPT


------ index_name_uniqueness_bought_days_svs_pre_check.sql ------
PROMPT Pre-checking table bought_days_svs for index name uniqueness
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN NULL
            ELSE 'Table "bought_days_svs" tries to create already existing indexes: ' || LISTAGG(index_name, ', ')
                WITHIN GROUP (ORDER BY index_name)
            END AS message
            FROM user_indexes
            WHERE index_name IN ('BOUGHT_DAYS_SVS_IB', 'BOUGHT_DAYS_SVS_IN', 'BOUGHT_DAYS_SVS_IP');

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20512, error_check_output);
    END IF;
END;
/
PROMPT


------ table_name_uniqueness_bought_days_svs_tmp_pre_check.sql ------
PROMPT Pre-checking table bought_days_svs_tmp for table name uniqueness
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS

        SELECT CASE COUNT(*)
          WHEN 0 THEN NULL
          ELSE 'Object with name "bought_days_svs_tmp" already exists'
          END AS message
          FROM USER_OBJECTS
          WHERE OBJECT_NAME = 'BOUGHT_DAYS_SVS_TMP'
          AND OBJECT_TYPE IN(
            'TABLE',
            'VIEW',
            'SEQUENCE',
            'SYNONYM',
            'PROCEDURE',
            'FUNCTION',
            'PACKAGE',
            'VIEW',
            'TYPE',
            'OPERATOR');

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20504, error_check_output);
    END IF;
END;
/
PROMPT


------ alter_table_published_roster_pre_check.sql ------
PROMPT Pre-checking table published_roster for index name uniqueness
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN NULL
            ELSE 'Table "published_roster" tries to create already existing indexes: ' || LISTAGG(index_name, ', ')
                WITHIN GROUP (ORDER BY index_name)
            END AS message
            FROM user_indexes
            WHERE index_name IN ('PUBLISHED_ROSTER_IX1');

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20512, error_check_output);
    END IF;
END;
/
PROMPT

PROMPT Pre-checking table published_roster before altering for existence of removed or modified indexes
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS
        SELECT CASE COUNT(*)
            WHEN 0 THEN 'Table "published_roster" is missing expected index "idx$$_d65b0001"'
            ELSE NULL
            END AS message
            FROM user_indexes
            WHERE index_name = 'IDX$$_D65B0001';

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20513, error_check_output);
    END IF;
END;
/
PROMPT


------ drop_table_crew_filter_group_tag_pre_check.sql ------
PROMPT Pre-checking table crew_filter_group_tag before dropping for unknown columns
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS

        SELECT CASE COUNT(*)
          WHEN 0 THEN NULL
          ELSE 'Table "crew_filter_group_tag" has unknown columns ' || LISTAGG(column_name, ', ')
            WITHIN GROUP (ORDER BY column_name)
          END AS message
          FROM USER_TAB_COLUMNS
          WHERE table_name = 'CREW_FILTER_GROUP_TAG'
          AND column_name NOT IN ('REVID', 'DELETED', 'PREV_REVID', 'NEXT_REVID', 'BRANCHID', 'CREWFILTER_NAME', 'CREWFILTER_CAT', 'GROUPTAG');

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20506, error_check_output);
    END IF;
END;
/
PROMPT


------ drop_table_crew_filter_group_tag_tmp_pre_check.sql ------
PROMPT Pre-checking table crew_filter_group_tag_tmp before dropping for unknown columns
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS

        SELECT CASE COUNT(*)
          WHEN 0 THEN NULL
          ELSE 'Table "crew_filter_group_tag_tmp" has unknown columns ' || LISTAGG(column_name, ', ')
            WITHIN GROUP (ORDER BY column_name)
          END AS message
          FROM USER_TAB_COLUMNS
          WHERE table_name = 'CREW_FILTER_GROUP_TAG_TMP'
          AND column_name NOT IN ('REVID', 'DELETED', 'PREV_REVID', 'NEXT_REVID', 'BRANCHID', 'CREWFILTER_NAME', 'CREWFILTER_CAT', 'GROUPTAG');

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20506, error_check_output);
    END IF;
END;
/
PROMPT


------ drop_table_estr_calc_node_node_tag_pre_check.sql ------
PROMPT Pre-checking table estr_calc_node_node_tag before dropping for unknown columns
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS

        SELECT CASE COUNT(*)
          WHEN 0 THEN NULL
          ELSE 'Table "estr_calc_node_node_tag" has unknown columns ' || LISTAGG(column_name, ', ')
            WITHIN GROUP (ORDER BY column_name)
          END AS message
          FROM USER_TAB_COLUMNS
          WHERE table_name = 'ESTR_CALC_NODE_NODE_TAG'
          AND column_name NOT IN ('REVID', 'DELETED', 'PREV_REVID', 'NEXT_REVID', 'BRANCHID', 'CALCNODE_SETUP_NAME', 'CALCNODE_SETUP_CAT', 'CALCNODE_NAME', 'NODETAG');

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20506, error_check_output);
    END IF;
END;
/
PROMPT


------ drop_table_estr_calc_node_node_tag_tmp_pre_check.sql ------
PROMPT Pre-checking table estr_calc_node_node_tag_tmp before dropping for unknown columns
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS

        SELECT CASE COUNT(*)
          WHEN 0 THEN NULL
          ELSE 'Table "estr_calc_node_node_tag_tmp" has unknown columns ' || LISTAGG(column_name, ', ')
            WITHIN GROUP (ORDER BY column_name)
          END AS message
          FROM USER_TAB_COLUMNS
          WHERE table_name = 'ESTR_CALC_NODE_NODE_TAG_TMP'
          AND column_name NOT IN ('REVID', 'DELETED', 'PREV_REVID', 'NEXT_REVID', 'BRANCHID', 'CALCNODE_SETUP_NAME', 'CALCNODE_SETUP_CAT', 'CALCNODE_NAME', 'NODETAG');

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20506, error_check_output);
    END IF;
END;
/
PROMPT


------ drop_table_estr_calc_node_tag_pre_check.sql ------
PROMPT Pre-checking table estr_calc_node_tag before dropping for unknown columns
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS

        SELECT CASE COUNT(*)
          WHEN 0 THEN NULL
          ELSE 'Table "estr_calc_node_tag" has unknown columns ' || LISTAGG(column_name, ', ')
            WITHIN GROUP (ORDER BY column_name)
          END AS message
          FROM USER_TAB_COLUMNS
          WHERE table_name = 'ESTR_CALC_NODE_TAG'
          AND column_name NOT IN ('REVID', 'DELETED', 'PREV_REVID', 'NEXT_REVID', 'BRANCHID', 'ID', 'CAPTION', 'CAT');

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20506, error_check_output);
    END IF;
END;
/
PROMPT


------ drop_table_estr_calc_node_tag_tmp_pre_check.sql ------
PROMPT Pre-checking table estr_calc_node_tag_tmp before dropping for unknown columns
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS

        SELECT CASE COUNT(*)
          WHEN 0 THEN NULL
          ELSE 'Table "estr_calc_node_tag_tmp" has unknown columns ' || LISTAGG(column_name, ', ')
            WITHIN GROUP (ORDER BY column_name)
          END AS message
          FROM USER_TAB_COLUMNS
          WHERE table_name = 'ESTR_CALC_NODE_TAG_TMP'
          AND column_name NOT IN ('REVID', 'DELETED', 'PREV_REVID', 'NEXT_REVID', 'BRANCHID', 'ID', 'CAPTION', 'CAT');

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20506, error_check_output);
    END IF;
END;
/
PROMPT


------ drop_table_resource_group_tag_pre_check.sql ------
PROMPT Pre-checking table resource_group_tag before dropping for unknown columns
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS

        SELECT CASE COUNT(*)
          WHEN 0 THEN NULL
          ELSE 'Table "resource_group_tag" has unknown columns ' || LISTAGG(column_name, ', ')
            WITHIN GROUP (ORDER BY column_name)
          END AS message
          FROM USER_TAB_COLUMNS
          WHERE table_name = 'RESOURCE_GROUP_TAG'
          AND column_name NOT IN ('REVID', 'DELETED', 'PREV_REVID', 'NEXT_REVID', 'BRANCHID', 'ID', 'CAPTION', 'CAT');

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20506, error_check_output);
    END IF;
END;
/
PROMPT


------ drop_table_resource_group_tag_tmp_pre_check.sql ------
PROMPT Pre-checking table resource_group_tag_tmp before dropping for unknown columns
PROMPT ================================================================================

DECLARE
    error_check_output VARCHAR2(32767) := '';

    CURSOR check_cur IS

        SELECT CASE COUNT(*)
          WHEN 0 THEN NULL
          ELSE 'Table "resource_group_tag_tmp" has unknown columns ' || LISTAGG(column_name, ', ')
            WITHIN GROUP (ORDER BY column_name)
          END AS message
          FROM USER_TAB_COLUMNS
          WHERE table_name = 'RESOURCE_GROUP_TAG_TMP'
          AND column_name NOT IN ('REVID', 'DELETED', 'PREV_REVID', 'NEXT_REVID', 'BRANCHID', 'ID', 'CAPTION', 'CAT');

BEGIN
    OPEN check_cur;
    FETCH check_cur INTO error_check_output;
    CLOSE check_cur;

    IF length(error_check_output) > 0 THEN
        RAISE_APPLICATION_ERROR(-20506, error_check_output);
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


------ create_table_bought_days_svs_pre_ddl.sql ------
PROMPT Create table bought_days_svs

CREATE TABLE bought_days_svs (
    revid NUMBER(10) NOT NULL,
    deleted CHAR(1 CHAR) NOT NULL,
    prev_revid NUMBER(10) NOT NULL,
    next_revid NUMBER(10) NOT NULL,
    branchid NUMBER(10) DEFAULT 1 NOT NULL,
    crew VARCHAR2(14 CHAR) NOT NULL,
    start_time NUMBER(10) NOT NULL,
    end_time NUMBER(10),
    day_type VARCHAR2(10 CHAR),
    hours NUMBER(10),
    minutes NUMBER(10),
    uname VARCHAR2(10 CHAR),
    si VARCHAR2(40 CHAR),
    account_name VARCHAR2(20 CHAR),
    CONSTRAINT bought_days_svs_pk PRIMARY KEY ( revid, branchid, crew, start_time ) USING INDEX TABLESPACE FLM_BIG_IDX);

CREATE INDEX bought_days_svs_ib ON bought_days_svs ( branchid ) TABLESPACE FLM_BIG_IDX;
CREATE INDEX bought_days_svs_in ON bought_days_svs ( next_revid ) TABLESPACE FLM_BIG_IDX;
CREATE UNIQUE INDEX bought_days_svs_ip ON bought_days_svs ( crew, start_time, branchid, prev_revid ) TABLESPACE FLM_BIG_IDX;

COMMIT;


------ create_table_bought_days_svs_tmp_pre_ddl.sql ------
PROMPT Create table bought_days_svs_tmp

CREATE GLOBAL TEMPORARY TABLE bought_days_svs_tmp (
    revid NUMBER(10) NOT NULL,
    deleted CHAR(1 CHAR),
    prev_revid NUMBER(10),
    next_revid NUMBER(10),
    branchid NUMBER(10) DEFAULT 1 NOT NULL,
    crew VARCHAR2(14 CHAR) NOT NULL,
    start_time NUMBER(10) NOT NULL,
    end_time NUMBER(10),
    day_type VARCHAR2(10 CHAR),
    hours NUMBER(10),
    minutes NUMBER(10),
    uname VARCHAR2(10 CHAR),
    si VARCHAR2(40 CHAR),
    account_name VARCHAR2(20 CHAR),
    CONSTRAINT bought_days_svs_tmp_pk PRIMARY KEY ( revid, branchid, crew, start_time ))
    ON COMMIT PRESERVE ROWS;

COMMIT;


------ alter_table_published_roster_pre_ddl.sql ------
PROMPT Pre alter table for published_roster

DROP INDEX idx$$_d65b0001;

COMMIT;


------ drop_table_crew_filter_group_tag_post_ddl.sql ------
PROMPT Drop table crew_filter_group_tag

DROP TABLE crew_filter_group_tag;

COMMIT;


------ drop_table_crew_filter_group_tag_tmp_post_ddl.sql ------
PROMPT Drop table crew_filter_group_tag_tmp

DROP TABLE crew_filter_group_tag_tmp;

COMMIT;


------ drop_table_estr_calc_node_node_tag_post_ddl.sql ------
PROMPT Drop table estr_calc_node_node_tag

DROP TABLE estr_calc_node_node_tag;

COMMIT;


------ drop_table_estr_calc_node_node_tag_tmp_post_ddl.sql ------
PROMPT Drop table estr_calc_node_node_tag_tmp

DROP TABLE estr_calc_node_node_tag_tmp;

COMMIT;


------ drop_table_estr_calc_node_tag_post_ddl.sql ------
PROMPT Drop table estr_calc_node_tag

DROP TABLE estr_calc_node_tag;

COMMIT;


------ drop_table_estr_calc_node_tag_tmp_post_ddl.sql ------
PROMPT Drop table estr_calc_node_tag_tmp

DROP TABLE estr_calc_node_tag_tmp;

COMMIT;


------ drop_table_resource_group_tag_post_ddl.sql ------
PROMPT Drop table resource_group_tag

DROP TABLE resource_group_tag;

COMMIT;


------ drop_table_resource_group_tag_tmp_post_ddl.sql ------
PROMPT Drop table resource_group_tag_tmp

DROP TABLE resource_group_tag_tmp;

COMMIT;


------ alter_table_published_roster_post_ddl.sql ------
PROMPT Post alter table for published_roster


CREATE INDEX published_roster_ix1 ON published_roster ( crew, branchid, pubtype, next_revid, deleted, pubend ) TABLESPACE FLM_BIG_IDX;

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


------ alter_module_air_jmp_3_2_metadata.sql ------
-- Update module information metadata in dave_schemacfg
DELETE FROM dave_schemacfg
WHERE (c_cfg_type = 'dave' AND c_cfg_group = 'module' AND c_cfg_name = 'air_jmp_3_2')
   OR (c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_3_2' AND c_cfg_name = 'version');
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'dave', 'module', 'air_jmp_3_2', 'jmp.19.4.6' );
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_3_2', 'version', 'jmp.19.4.6' );
DELETE FROM dave_schemacfg WHERE c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_3_2' AND c_cfg_name = 'compatible';
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_3_2', 'compatible', 'jmp.19.4.6' );

-- Update module dependency metadata in dave_schemacfg

COMMIT;


------ alter_module_air_jmp_access_metadata.sql ------
-- Update module information metadata in dave_schemacfg
DELETE FROM dave_schemacfg
WHERE (c_cfg_type = 'dave' AND c_cfg_group = 'module' AND c_cfg_name = 'air_jmp_access')
   OR (c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_access' AND c_cfg_name = 'version');
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'dave', 'module', 'air_jmp_access', 'jmp.19.4.6' );
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_access', 'version', 'jmp.19.4.6' );
DELETE FROM dave_schemacfg WHERE c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_access' AND c_cfg_name = 'compatible';
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_access', 'compatible', 'jmp.19.4.6' );

-- Update module dependency metadata in dave_schemacfg

COMMIT;


------ alter_module_air_jmp_attributes_metadata.sql ------
-- Update module information metadata in dave_schemacfg
DELETE FROM dave_schemacfg
WHERE (c_cfg_type = 'dave' AND c_cfg_group = 'module' AND c_cfg_name = 'air_jmp_attributes')
   OR (c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_attributes' AND c_cfg_name = 'version');
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'dave', 'module', 'air_jmp_attributes', 'jmp.19.4.6' );
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_attributes', 'version', 'jmp.19.4.6' );
DELETE FROM dave_schemacfg WHERE c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_attributes' AND c_cfg_name = 'compatible';
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_attributes', 'compatible', 'jmp.19.4.6' );

-- Update module dependency metadata in dave_schemacfg

COMMIT;


------ alter_module_air_jmp_bid_general_metadata.sql ------
-- Update module information metadata in dave_schemacfg
DELETE FROM dave_schemacfg
WHERE (c_cfg_type = 'dave' AND c_cfg_group = 'module' AND c_cfg_name = 'air_jmp_bid_general')
   OR (c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_bid_general' AND c_cfg_name = 'version');
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'dave', 'module', 'air_jmp_bid_general', 'jmp.19.4.6' );
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_bid_general', 'version', 'jmp.19.4.6' );
DELETE FROM dave_schemacfg WHERE c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_bid_general' AND c_cfg_name = 'compatible';
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_bid_general', 'compatible', 'jmp.19.4.6' );

-- Update module dependency metadata in dave_schemacfg

COMMIT;


------ alter_module_air_jmp_bid_transaction_metadata.sql ------
-- Update module information metadata in dave_schemacfg
DELETE FROM dave_schemacfg
WHERE (c_cfg_type = 'dave' AND c_cfg_group = 'module' AND c_cfg_name = 'air_jmp_bid_transaction')
   OR (c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_bid_transaction' AND c_cfg_name = 'version');
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'dave', 'module', 'air_jmp_bid_transaction', 'jmp.19.4.6' );
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_bid_transaction', 'version', 'jmp.19.4.6' );
DELETE FROM dave_schemacfg WHERE c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_bid_transaction' AND c_cfg_name = 'compatible';
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_bid_transaction', 'compatible', 'jmp.19.4.6' );

-- Update module dependency metadata in dave_schemacfg

COMMIT;


------ alter_module_air_jmp_common_establishment_metadata.sql ------
-- Update module information metadata in dave_schemacfg
DELETE FROM dave_schemacfg
WHERE (c_cfg_type = 'dave' AND c_cfg_group = 'module' AND c_cfg_name = 'air_jmp_common_establishment')
   OR (c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_common_establishment' AND c_cfg_name = 'version');
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'dave', 'module', 'air_jmp_common_establishment', 'jmp.19.4.6' );
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_common_establishment', 'version', 'jmp.19.4.6' );
DELETE FROM dave_schemacfg WHERE c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_common_establishment' AND c_cfg_name = 'compatible';
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_common_establishment', 'compatible', 'jmp.19.4.6' );

-- Update module dependency metadata in dave_schemacfg

COMMIT;


------ alter_module_air_jmp_comparer_extension_metadata.sql ------
-- Update module information metadata in dave_schemacfg
DELETE FROM dave_schemacfg
WHERE (c_cfg_type = 'dave' AND c_cfg_group = 'module' AND c_cfg_name = 'air_jmp_comparer_extension')
   OR (c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_comparer_extension' AND c_cfg_name = 'version');
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'dave', 'module', 'air_jmp_comparer_extension', 'jmp.19.4.6' );
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_comparer_extension', 'version', 'jmp.19.4.6' );
DELETE FROM dave_schemacfg WHERE c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_comparer_extension' AND c_cfg_name = 'compatible';
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_comparer_extension', 'compatible', 'jmp.19.4.6' );

-- Update module dependency metadata in dave_schemacfg

COMMIT;


------ alter_module_air_jmp_core_metadata.sql ------
-- Update module information metadata in dave_schemacfg
DELETE FROM dave_schemacfg
WHERE (c_cfg_type = 'dave' AND c_cfg_group = 'module' AND c_cfg_name = 'air_jmp_core')
   OR (c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_core' AND c_cfg_name = 'version');
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'dave', 'module', 'air_jmp_core', 'jmp.19.4.6' );
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_core', 'version', 'jmp.19.4.6' );
DELETE FROM dave_schemacfg WHERE c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_core' AND c_cfg_name = 'compatible';
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_core', 'compatible', 'jmp.19.4.6' );

-- Update module dependency metadata in dave_schemacfg

COMMIT;


------ alter_module_air_jmp_ctraining_metadata.sql ------
-- Update module information metadata in dave_schemacfg
DELETE FROM dave_schemacfg
WHERE (c_cfg_type = 'dave' AND c_cfg_group = 'module' AND c_cfg_name = 'air_jmp_ctraining')
   OR (c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_ctraining' AND c_cfg_name = 'version');
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'dave', 'module', 'air_jmp_ctraining', 'jmp.19.4.6' );
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_ctraining', 'version', 'jmp.19.4.6' );
DELETE FROM dave_schemacfg WHERE c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_ctraining' AND c_cfg_name = 'compatible';
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_ctraining', 'compatible', 'jmp.19.4.6' );

-- Update module dependency metadata in dave_schemacfg

COMMIT;


------ alter_module_air_jmp_patch_data_metadata.sql ------
-- Update module information metadata in dave_schemacfg
DELETE FROM dave_schemacfg
WHERE (c_cfg_type = 'dave' AND c_cfg_group = 'module' AND c_cfg_name = 'air_jmp_patch_data')
   OR (c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_patch_data' AND c_cfg_name = 'version');
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'dave', 'module', 'air_jmp_patch_data', 'jmp.19.4.6' );
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_patch_data', 'version', 'jmp.19.4.6' );
DELETE FROM dave_schemacfg WHERE c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_patch_data' AND c_cfg_name = 'compatible';
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_patch_data', 'compatible', 'jmp.19.4.6' );

-- Update module dependency metadata in dave_schemacfg

COMMIT;


------ alter_module_air_jmp_resource_consumption_metadata.sql ------
-- Update module information metadata in dave_schemacfg
DELETE FROM dave_schemacfg
WHERE (c_cfg_type = 'dave' AND c_cfg_group = 'module' AND c_cfg_name = 'air_jmp_resource_consumption')
   OR (c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_resource_consumption' AND c_cfg_name = 'version');
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'dave', 'module', 'air_jmp_resource_consumption', 'jmp.19.4.6' );
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_resource_consumption', 'version', 'jmp.19.4.6' );
DELETE FROM dave_schemacfg WHERE c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_resource_consumption' AND c_cfg_name = 'compatible';
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_resource_consumption', 'compatible', 'jmp.19.4.6' );

-- Update module dependency metadata in dave_schemacfg

COMMIT;


------ alter_module_air_jmp_separate_planned_tasks_metadata.sql ------
-- Update module information metadata in dave_schemacfg
DELETE FROM dave_schemacfg
WHERE (c_cfg_type = 'dave' AND c_cfg_group = 'module' AND c_cfg_name = 'air_jmp_separate_planned_tasks')
   OR (c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_separate_planned_tasks' AND c_cfg_name = 'version');
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'dave', 'module', 'air_jmp_separate_planned_tasks', 'jmp.19.4.6' );
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_separate_planned_tasks', 'version', 'jmp.19.4.6' );
DELETE FROM dave_schemacfg WHERE c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_separate_planned_tasks' AND c_cfg_name = 'compatible';
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_separate_planned_tasks', 'compatible', 'jmp.19.4.6' );

-- Update module dependency metadata in dave_schemacfg

COMMIT;


------ alter_module_air_jmp_status_report_metadata.sql ------
-- Update module information metadata in dave_schemacfg
DELETE FROM dave_schemacfg
WHERE (c_cfg_type = 'dave' AND c_cfg_group = 'module' AND c_cfg_name = 'air_jmp_status_report')
   OR (c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_status_report' AND c_cfg_name = 'version');
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'dave', 'module', 'air_jmp_status_report', 'jmp.19.4.6' );
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_status_report', 'version', 'jmp.19.4.6' );
DELETE FROM dave_schemacfg WHERE c_cfg_type = 'default' AND c_cfg_group = 'air_jmp_status_report' AND c_cfg_name = 'compatible';
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_jmp_status_report', 'compatible', 'jmp.19.4.6' );

-- Update module dependency metadata in dave_schemacfg

COMMIT;


------ alter_module_air_new_manpower_metadata.sql ------
-- Update module information metadata in dave_schemacfg
DELETE FROM dave_schemacfg
WHERE (c_cfg_type = 'dave' AND c_cfg_group = 'module' AND c_cfg_name = 'air_new_manpower')
   OR (c_cfg_type = 'default' AND c_cfg_group = 'air_new_manpower' AND c_cfg_name = 'version');
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'dave', 'module', 'air_new_manpower', 'jmp.19.4.6' );
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_new_manpower', 'version', 'jmp.19.4.6' );
DELETE FROM dave_schemacfg WHERE c_cfg_type = 'default' AND c_cfg_group = 'air_new_manpower' AND c_cfg_name = 'compatible';
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_new_manpower', 'compatible', 'jmp.19.4.6' );

-- Update module dependency metadata in dave_schemacfg

COMMIT;


------ alter_module_air_opt_manpower_metadata.sql ------
-- Update module information metadata in dave_schemacfg
DELETE FROM dave_schemacfg
WHERE (c_cfg_type = 'dave' AND c_cfg_group = 'module' AND c_cfg_name = 'air_opt_manpower')
   OR (c_cfg_type = 'default' AND c_cfg_group = 'air_opt_manpower' AND c_cfg_name = 'version');
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'dave', 'module', 'air_opt_manpower', 'jmp.19.4.6' );
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_opt_manpower', 'version', 'jmp.19.4.6' );
DELETE FROM dave_schemacfg WHERE c_cfg_type = 'default' AND c_cfg_group = 'air_opt_manpower' AND c_cfg_name = 'compatible';
INSERT INTO dave_schemacfg ( c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'default', 'air_opt_manpower', 'compatible', 'jmp.19.4.6' );

-- Update module dependency metadata in dave_schemacfg

COMMIT;


------ create_entity_bought_days_svs_metadata.sql ------
-- Insert attribute metadata into dave_attribcfg
INSERT INTO dave_attribcfg ( c_ent_name, c_attrib_name, c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'bought_days_svs', 'crew', 'default', 'default', 'desc', 'Crew Identifier' );
INSERT INTO dave_attribcfg ( c_ent_name, c_attrib_name, c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'bought_days_svs', 'start_time', 'default', 'default', 'desc', 'Start time for bought day' );
INSERT INTO dave_attribcfg ( c_ent_name, c_attrib_name, c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'bought_days_svs', 'end_time', 'default', 'default', 'desc', 'End time for bought day' );
INSERT INTO dave_attribcfg ( c_ent_name, c_attrib_name, c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'bought_days_svs', 'day_type', 'default', 'default', 'desc', 'Type for bought day' );
INSERT INTO dave_attribcfg ( c_ent_name, c_attrib_name, c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'bought_days_svs', 'hours', 'default', 'default', 'desc', 'Total bought Hours' );
INSERT INTO dave_attribcfg ( c_ent_name, c_attrib_name, c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'bought_days_svs', 'minutes', 'default', 'default', 'desc', ' Total Bought minutes' );
INSERT INTO dave_attribcfg ( c_ent_name, c_attrib_name, c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'bought_days_svs', 'uname', 'default', 'default', 'desc', 'Record commiter' );
INSERT INTO dave_attribcfg ( c_ent_name, c_attrib_name, c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'bought_days_svs', 'si', 'default', 'default', 'desc', 'Suplementary information' );
INSERT INTO dave_attribcfg ( c_ent_name, c_attrib_name, c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'bought_days_svs', 'account_name', 'default', 'default', 'desc', 'Name of account for bought day' );

-- Insert metadata into dave_entity_attribs
INSERT INTO dave_entity_attribs ( c_ent_name, c_attrib_name, c_attrib_colix, c_attrib_keyix, c_attrib_apitype, c_attrib_role, c_table_alias, c_col_name ) VALUES (
    'bought_days_svs', 'revid', 0, -1, 'I', 'R', 'bought_days_svs', 'revid' );
INSERT INTO dave_entity_attribs ( c_ent_name, c_attrib_name, c_attrib_colix, c_attrib_keyix, c_attrib_apitype, c_attrib_role, c_table_alias, c_col_name ) VALUES (
    'bought_days_svs', 'deleted', 1, -1, 'C', 'D', 'bought_days_svs', 'deleted' );
INSERT INTO dave_entity_attribs ( c_ent_name, c_attrib_name, c_attrib_colix, c_attrib_keyix, c_attrib_apitype, c_attrib_role, c_table_alias, c_col_name ) VALUES (
    'bought_days_svs', 'branchid', 2, -1, 'I', 'B', 'bought_days_svs', 'branchid' );
INSERT INTO dave_entity_attribs ( c_ent_name, c_attrib_name, c_attrib_colix, c_attrib_keyix, c_attrib_apitype, c_attrib_role, c_table_alias, c_col_name ) VALUES (
    'bought_days_svs', 'crew', 3, 0, 'S', 'K', 'bought_days_svs', 'crew' );
INSERT INTO dave_entity_attribs ( c_ent_name, c_attrib_name, c_attrib_colix, c_attrib_keyix, c_attrib_apitype, c_attrib_role, c_table_alias, c_col_name ) VALUES (
    'bought_days_svs', 'start_time', 4, 1, 'A', 'K', 'bought_days_svs', 'start_time' );
INSERT INTO dave_entity_attribs ( c_ent_name, c_attrib_name, c_attrib_colix, c_attrib_keyix, c_attrib_apitype, c_attrib_role, c_table_alias, c_col_name ) VALUES (
    'bought_days_svs', 'end_time', 5, -1, 'A', 'N', 'bought_days_svs', 'end_time' );
INSERT INTO dave_entity_attribs ( c_ent_name, c_attrib_name, c_attrib_colix, c_attrib_keyix, c_attrib_apitype, c_attrib_role, c_table_alias, c_col_name ) VALUES (
    'bought_days_svs', 'day_type', 6, -1, 'S', 'N', 'bought_days_svs', 'day_type' );
INSERT INTO dave_entity_attribs ( c_ent_name, c_attrib_name, c_attrib_colix, c_attrib_keyix, c_attrib_apitype, c_attrib_role, c_table_alias, c_col_name ) VALUES (
    'bought_days_svs', 'hours', 7, -1, 'R', 'N', 'bought_days_svs', 'hours' );
INSERT INTO dave_entity_attribs ( c_ent_name, c_attrib_name, c_attrib_colix, c_attrib_keyix, c_attrib_apitype, c_attrib_role, c_table_alias, c_col_name ) VALUES (
    'bought_days_svs', 'minutes', 8, -1, 'R', 'N', 'bought_days_svs', 'minutes' );
INSERT INTO dave_entity_attribs ( c_ent_name, c_attrib_name, c_attrib_colix, c_attrib_keyix, c_attrib_apitype, c_attrib_role, c_table_alias, c_col_name ) VALUES (
    'bought_days_svs', 'uname', 9, -1, 'S', 'N', 'bought_days_svs', 'uname' );
INSERT INTO dave_entity_attribs ( c_ent_name, c_attrib_name, c_attrib_colix, c_attrib_keyix, c_attrib_apitype, c_attrib_role, c_table_alias, c_col_name ) VALUES (
    'bought_days_svs', 'si', 10, -1, 'S', 'N', 'bought_days_svs', 'si' );
INSERT INTO dave_entity_attribs ( c_ent_name, c_attrib_name, c_attrib_colix, c_attrib_keyix, c_attrib_apitype, c_attrib_role, c_table_alias, c_col_name ) VALUES (
    'bought_days_svs', 'account_name', 11, -1, 'S', 'N', 'bought_days_svs', 'account_name' );

-- Insert metadata into dave_entity_tables
INSERT INTO dave_entity_tables ( c_ent_name, c_table_alias, c_table_role, c_attrib_keyix, c_table_name ) VALUES (
    'bought_days_svs', 'bought_days_svs', 'M', -1, 'bought_days_svs' );
INSERT INTO dave_entity_tables ( c_ent_name, c_table_alias, c_table_role, c_attrib_keyix, c_table_name ) VALUES (
    'bought_days_svs', 'TMP', 't', -1, 'bought_days_svs_tmp' );

-- Insert metadata into dave_entitycfg
INSERT INTO dave_entitycfg ( c_ent_name, c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'bought_days_svs', 'config', 'datagroup', 'cfg', 'default' );
INSERT INTO dave_entitycfg ( c_ent_name, c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'bought_days_svs', 'config', 'merge.strategy', 'cfg', 'properties' );
INSERT INTO dave_entitycfg ( c_ent_name, c_cfg_type, c_cfg_group, c_cfg_name, c_cfg_value ) VALUES (
    'bought_days_svs', 'default', 'default', 'desc', 'Bought freedays, compensation and vacation days' );

-- Insert metadata into dave_entity_fks
INSERT INTO dave_entity_fks ( c_ent_name, c_fk_name, c_fk_tgtname, c_fk_keycols, c_fk_tgtcols, c_fk_reffield ) VALUES (
    'bought_days_svs', 'crew', 'crew', 'crew', 'id', 'N' );


COMMIT;


------ drop_entity_crew_filter_group_tag_metadata_late.sql ------
-- Delete metadata from dave_attribcfg
DELETE FROM dave_attribcfg WHERE c_ent_name='crew_filter_group_tag';

-- Delete metadata from dave_entity_attribs
DELETE FROM dave_entity_attribs WHERE c_ent_name='crew_filter_group_tag';

-- Delete metadata from dave_entity_tables
DELETE FROM dave_entity_tables WHERE c_ent_name='crew_filter_group_tag';

-- Delete metadata from dave_entitycfg
DELETE FROM dave_entitycfg WHERE c_ent_name='crew_filter_group_tag';

-- Delete metadata from dave_entity_fks
DELETE FROM dave_entity_fks WHERE c_ent_name='crew_filter_group_tag';
DELETE FROM dave_entity_fks WHERE c_fk_tgtname='crew_filter_group_tag';

-- Delete records from dave_updated_tables
DELETE FROM dave_updated_tables WHERE tablename = 'crew_filter_group_tag';

-- Clear filter definitions: Delete records from dave_filter_ref
DELETE FROM dave_filter_ref
WHERE source_filter IN
    (SELECT id FROM dave_entity_filter WHERE entity = 'crew_filter_group_tag')
OR target_filter IN
    (SELECT id FROM dave_entity_filter WHERE entity = 'crew_filter_group_tag');

-- Clear filter definitions: Delete records from dave_entity_filter
DELETE FROM dave_entity_filter WHERE entity = 'crew_filter_group_tag';


COMMIT;


------ drop_entity_estr_calc_node_node_tag_metadata_late.sql ------
-- Delete metadata from dave_attribcfg
DELETE FROM dave_attribcfg WHERE c_ent_name='estr_calc_node_node_tag';

-- Delete metadata from dave_entity_attribs
DELETE FROM dave_entity_attribs WHERE c_ent_name='estr_calc_node_node_tag';

-- Delete metadata from dave_entity_tables
DELETE FROM dave_entity_tables WHERE c_ent_name='estr_calc_node_node_tag';

-- Delete metadata from dave_entitycfg
DELETE FROM dave_entitycfg WHERE c_ent_name='estr_calc_node_node_tag';

-- Delete metadata from dave_entity_fks
DELETE FROM dave_entity_fks WHERE c_ent_name='estr_calc_node_node_tag';
DELETE FROM dave_entity_fks WHERE c_fk_tgtname='estr_calc_node_node_tag';

-- Delete records from dave_updated_tables
DELETE FROM dave_updated_tables WHERE tablename = 'estr_calc_node_node_tag';

-- Clear filter definitions: Delete records from dave_filter_ref
DELETE FROM dave_filter_ref
WHERE source_filter IN
    (SELECT id FROM dave_entity_filter WHERE entity = 'estr_calc_node_node_tag')
OR target_filter IN
    (SELECT id FROM dave_entity_filter WHERE entity = 'estr_calc_node_node_tag');

-- Clear filter definitions: Delete records from dave_entity_filter
DELETE FROM dave_entity_filter WHERE entity = 'estr_calc_node_node_tag';


COMMIT;


------ drop_entity_estr_calc_node_tag_metadata_late.sql ------
-- Delete metadata from dave_attribcfg
DELETE FROM dave_attribcfg WHERE c_ent_name='estr_calc_node_tag';

-- Delete metadata from dave_entity_attribs
DELETE FROM dave_entity_attribs WHERE c_ent_name='estr_calc_node_tag';

-- Delete metadata from dave_entity_tables
DELETE FROM dave_entity_tables WHERE c_ent_name='estr_calc_node_tag';

-- Delete metadata from dave_entitycfg
DELETE FROM dave_entitycfg WHERE c_ent_name='estr_calc_node_tag';

-- Delete metadata from dave_entity_fks
DELETE FROM dave_entity_fks WHERE c_ent_name='estr_calc_node_tag';
DELETE FROM dave_entity_fks WHERE c_fk_tgtname='estr_calc_node_tag';

-- Delete records from dave_updated_tables
DELETE FROM dave_updated_tables WHERE tablename = 'estr_calc_node_tag';

-- Clear filter definitions: Delete records from dave_filter_ref
DELETE FROM dave_filter_ref
WHERE source_filter IN
    (SELECT id FROM dave_entity_filter WHERE entity = 'estr_calc_node_tag')
OR target_filter IN
    (SELECT id FROM dave_entity_filter WHERE entity = 'estr_calc_node_tag');

-- Clear filter definitions: Delete records from dave_entity_filter
DELETE FROM dave_entity_filter WHERE entity = 'estr_calc_node_tag';


COMMIT;


------ drop_entity_resource_group_tag_metadata_late.sql ------
-- Delete metadata from dave_attribcfg
DELETE FROM dave_attribcfg WHERE c_ent_name='resource_group_tag';

-- Delete metadata from dave_entity_attribs
DELETE FROM dave_entity_attribs WHERE c_ent_name='resource_group_tag';

-- Delete metadata from dave_entity_tables
DELETE FROM dave_entity_tables WHERE c_ent_name='resource_group_tag';

-- Delete metadata from dave_entitycfg
DELETE FROM dave_entitycfg WHERE c_ent_name='resource_group_tag';

-- Delete metadata from dave_entity_fks
DELETE FROM dave_entity_fks WHERE c_ent_name='resource_group_tag';
DELETE FROM dave_entity_fks WHERE c_fk_tgtname='resource_group_tag';

-- Delete records from dave_updated_tables
DELETE FROM dave_updated_tables WHERE tablename = 'resource_group_tag';

-- Clear filter definitions: Delete records from dave_filter_ref
DELETE FROM dave_filter_ref
WHERE source_filter IN
    (SELECT id FROM dave_entity_filter WHERE entity = 'resource_group_tag')
OR target_filter IN
    (SELECT id FROM dave_entity_filter WHERE entity = 'resource_group_tag');

-- Clear filter definitions: Delete records from dave_entity_filter
DELETE FROM dave_entity_filter WHERE entity = 'resource_group_tag';


COMMIT;

PROMPT End of migration. Unset guard ...

DELETE FROM dave_metadata_status;

COMMIT;
