SET SERVEROUTPUT ON SIZE UNLIMITED
SET HEADING OFF
SET FEEDBACK OFF

------ dave_version_pre_manual_check.sql ------
PROMPT Pre-checking version of dave
PROMPT ================================================================================
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
PROMPT


------ module_version_admin2_audit_pre_manual_check.sql ------
PROMPT Pre-checking version of module admin2_audit
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module admin2_audit with version udm.admin2.07.04'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'admin2_audit'
      AND c_cfg_value = 'udm.admin2.07.04';
PROMPT


------ module_version_admin2_datacontext_pre_manual_check.sql ------
PROMPT Pre-checking version of module admin2_datacontext
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module admin2_datacontext with version udm.admin2.07.04'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'admin2_datacontext'
      AND c_cfg_value = 'udm.admin2.07.04';
PROMPT


------ module_version_admin2_dig_pre_manual_check.sql ------
PROMPT Pre-checking version of module admin2_dig
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module admin2_dig with version udm.admin2.07.04'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'admin2_dig'
      AND c_cfg_value = 'udm.admin2.07.04';
PROMPT


------ module_version_admin2_rave_pre_manual_check.sql ------
PROMPT Pre-checking version of module admin2_rave
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module admin2_rave with version udm.admin2.07.04'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'admin2_rave'
      AND c_cfg_value = 'udm.admin2.07.04';
PROMPT


------ module_version_air1_aircraft_pre_manual_check.sql ------
PROMPT Pre-checking version of module air1_aircraft
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air1_aircraft with version udm.air1.11.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air1_aircraft'
      AND c_cfg_value = 'udm.air1.11.00';
PROMPT


------ module_version_air1_airport_pre_manual_check.sql ------
PROMPT Pre-checking version of module air1_airport
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air1_airport with version udm.air1.11.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air1_airport'
      AND c_cfg_value = 'udm.air1.11.00';
PROMPT


------ module_version_air1_aoc_pre_manual_check.sql ------
PROMPT Pre-checking version of module air1_aoc
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air1_aoc with version udm.air1.11.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air1_aoc'
      AND c_cfg_value = 'udm.air1.11.00';
PROMPT


------ module_version_air1_core_pre_manual_check.sql ------
PROMPT Pre-checking version of module air1_core
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air1_core with version udm.air1.11.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air1_core'
      AND c_cfg_value = 'udm.air1.11.00';
PROMPT


------ module_version_air1_crew_pre_manual_check.sql ------
PROMPT Pre-checking version of module air1_crew
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air1_crew with version udm.air1.11.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air1_crew'
      AND c_cfg_value = 'udm.air1.11.00';
PROMPT


------ module_version_air1_ctraining_pre_manual_check.sql ------
PROMPT Pre-checking version of module air1_ctraining
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air1_ctraining with version udm.air1.11.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air1_ctraining'
      AND c_cfg_value = 'udm.air1.11.00';
PROMPT


------ module_version_air1_dutytype_pre_manual_check.sql ------
PROMPT Pre-checking version of module air1_dutytype
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air1_dutytype with version udm.air1.11.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air1_dutytype'
      AND c_cfg_value = 'udm.air1.11.00';
PROMPT


------ module_version_air1_iocs_pre_manual_check.sql ------
PROMPT Pre-checking version of module air1_iocs
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air1_iocs with version udm.air1.11.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air1_iocs'
      AND c_cfg_value = 'udm.air1.11.00';
PROMPT


------ module_version_air1_manpower_pre_manual_check.sql ------
PROMPT Pre-checking version of module air1_manpower
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air1_manpower with version udm.air1.11.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air1_manpower'
      AND c_cfg_value = 'udm.air1.11.00';
PROMPT


------ module_version_air1_origsuffix_pre_manual_check.sql ------
PROMPT Pre-checking version of module air1_origsuffix
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air1_origsuffix with version udm.air1.11.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air1_origsuffix'
      AND c_cfg_value = 'udm.air1.11.00';
PROMPT


------ module_version_air1_planning_pre_manual_check.sql ------
PROMPT Pre-checking version of module air1_planning
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air1_planning with version udm.air1.11.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air1_planning'
      AND c_cfg_value = 'udm.air1.11.00';
PROMPT


------ module_version_air1_tracking_pre_manual_check.sql ------
PROMPT Pre-checking version of module air1_tracking
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air1_tracking with version udm.air1.11.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air1_tracking'
      AND c_cfg_value = 'udm.air1.11.00';
PROMPT


------ module_version_air1_urm_pre_manual_check.sql ------
PROMPT Pre-checking version of module air1_urm
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air1_urm with version udm.air1.11.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air1_urm'
      AND c_cfg_value = 'udm.air1.11.00';
PROMPT


------ module_version_air_jmp_3_2_pre_manual_check.sql ------
PROMPT Pre-checking version of module air_jmp_3_2
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air_jmp_3_2 with version jmp.19.16.4300'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air_jmp_3_2'
      AND c_cfg_value = 'jmp.19.16.4300';
PROMPT


------ module_version_air_jmp_access_pre_manual_check.sql ------
PROMPT Pre-checking version of module air_jmp_access
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air_jmp_access with version jmp.19.16.4300'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air_jmp_access'
      AND c_cfg_value = 'jmp.19.16.4300';
PROMPT


------ module_version_air_jmp_attributes_pre_manual_check.sql ------
PROMPT Pre-checking version of module air_jmp_attributes
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air_jmp_attributes with version jmp.19.16.4300'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air_jmp_attributes'
      AND c_cfg_value = 'jmp.19.16.4300';
PROMPT


------ module_version_air_jmp_bid_general_pre_manual_check.sql ------
PROMPT Pre-checking version of module air_jmp_bid_general
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air_jmp_bid_general with version jmp.19.16.4300'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air_jmp_bid_general'
      AND c_cfg_value = 'jmp.19.16.4300';
PROMPT


------ module_version_air_jmp_bid_transaction_pre_manual_check.sql ------
PROMPT Pre-checking version of module air_jmp_bid_transaction
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air_jmp_bid_transaction with version jmp.19.16.4300'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air_jmp_bid_transaction'
      AND c_cfg_value = 'jmp.19.16.4300';
PROMPT


------ module_version_air_jmp_common_establishment_pre_manual_check.sql ------
PROMPT Pre-checking version of module air_jmp_common_establishment
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air_jmp_common_establishment with version jmp.19.16.4300'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air_jmp_common_establishment'
      AND c_cfg_value = 'jmp.19.16.4300';
PROMPT


------ module_version_air_jmp_comparer_extension_pre_manual_check.sql ------
PROMPT Pre-checking version of module air_jmp_comparer_extension
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air_jmp_comparer_extension with version jmp.19.16.4300'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air_jmp_comparer_extension'
      AND c_cfg_value = 'jmp.19.16.4300';
PROMPT


------ module_version_air_jmp_core_pre_manual_check.sql ------
PROMPT Pre-checking version of module air_jmp_core
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air_jmp_core with version jmp.19.16.4300'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air_jmp_core'
      AND c_cfg_value = 'jmp.19.16.4300';
PROMPT


------ module_version_air_jmp_ctraining_pre_manual_check.sql ------
PROMPT Pre-checking version of module air_jmp_ctraining
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air_jmp_ctraining with version jmp.19.16.4300'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air_jmp_ctraining'
      AND c_cfg_value = 'jmp.19.16.4300';
PROMPT


------ module_version_air_jmp_patch_data_pre_manual_check.sql ------
PROMPT Pre-checking version of module air_jmp_patch_data
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air_jmp_patch_data with version jmp.19.16.4300'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air_jmp_patch_data'
      AND c_cfg_value = 'jmp.19.16.4300';
PROMPT


------ module_version_air_jmp_resource_consumption_pre_manual_check.sql ------
PROMPT Pre-checking version of module air_jmp_resource_consumption
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air_jmp_resource_consumption with version jmp.19.16.4300'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air_jmp_resource_consumption'
      AND c_cfg_value = 'jmp.19.16.4300';
PROMPT


------ module_version_air_jmp_separate_planned_tasks_pre_manual_check.sql ------
PROMPT Pre-checking version of module air_jmp_separate_planned_tasks
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air_jmp_separate_planned_tasks with version jmp.19.16.4300'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air_jmp_separate_planned_tasks'
      AND c_cfg_value = 'jmp.19.16.4300';
PROMPT


------ module_version_air_jmp_status_report_pre_manual_check.sql ------
PROMPT Pre-checking version of module air_jmp_status_report
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air_jmp_status_report with version jmp.19.16.4300'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air_jmp_status_report'
      AND c_cfg_value = 'jmp.19.16.4300';
PROMPT


------ module_version_air_new_manpower_pre_manual_check.sql ------
PROMPT Pre-checking version of module air_new_manpower
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air_new_manpower with version jmp.19.16.4300'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air_new_manpower'
      AND c_cfg_value = 'jmp.19.16.4300';
PROMPT


------ module_version_air_opt_manpower_pre_manual_check.sql ------
PROMPT Pre-checking version of module air_opt_manpower
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module air_opt_manpower with version jmp.19.16.4300'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'air_opt_manpower'
      AND c_cfg_value = 'jmp.19.16.4300';
PROMPT


------ module_version_cmp_transition_pre_manual_check.sql ------
PROMPT Pre-checking version of module cmp_transition
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module cmp_transition with version udm.01.02'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'cmp_transition'
      AND c_cfg_value = 'udm.01.02';
PROMPT


------ module_version_custom_crew_attributes_pre_manual_check.sql ------
PROMPT Pre-checking version of module custom_crew_attributes
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module custom_crew_attributes with version carmusr_jmp.01.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'custom_crew_attributes'
      AND c_cfg_value = 'carmusr_jmp.01.00';
PROMPT


------ module_version_leave_rules_configuration_pre_manual_check.sql ------
PROMPT Pre-checking version of module leave_rules_configuration
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module leave_rules_configuration with version carmusr_jmp.01.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'leave_rules_configuration'
      AND c_cfg_value = 'carmusr_jmp.01.00';
PROMPT


------ module_version_recurrent_configuration_pre_manual_check.sql ------
PROMPT Pre-checking version of module recurrent_configuration
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module recurrent_configuration with version carmusr_jmp.01.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'recurrent_configuration'
      AND c_cfg_value = 'carmusr_jmp.01.00';
PROMPT


------ module_version_sas_accounts_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_accounts
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_accounts with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_accounts'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_admin_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_admin
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_admin with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_admin'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_air_aircraft_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_air_aircraft
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_air_aircraft with version udm.1.11'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_air_aircraft'
      AND c_cfg_value = 'udm.1.11';
PROMPT


------ module_version_sas_air_core_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_air_core
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_air_core with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_air_core'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_air_crew_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_air_crew
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_air_crew with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_air_crew'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_air_tracking_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_air_tracking
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_air_tracking with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_air_tracking'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_annotations_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_annotations
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_annotations with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_annotations'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_attributes_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_attributes
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_attributes with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_attributes'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_base_breaks_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_base_breaks
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_base_breaks with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_base_breaks'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_bought_days_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_bought_days
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_bought_days with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_bought_days'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_calloutlist_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_calloutlist
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_calloutlist with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_calloutlist'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_checkin_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_checkin
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_checkin with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_checkin'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_cp_bid_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_cp_bid
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_cp_bid with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_cp_bid'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_crew_meals_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_crew_meals
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_crew_meals with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_crew_meals'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_crew_needs_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_crew_needs
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_crew_needs with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_crew_needs'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_crew_user_filter_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_crew_user_filter
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_crew_user_filter with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_crew_user_filter'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_dig_recipients_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_dig_recipients
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_dig_recipients with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_dig_recipients'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_financial_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_financial
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_financial with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_financial'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_handover_reports_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_handover_reports
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_handover_reports with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_handover_reports'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_hotel_bookings_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_hotel_bookings
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_hotel_bookings with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_hotel_bookings'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_indexes_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_indexes
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_indexes with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_indexes'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_integration_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_integration
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_integration with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_integration'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_leave_entitlement_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_leave_entitlement
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_leave_entitlement with version carmusr_jmp.1.02'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_leave_entitlement'
      AND c_cfg_value = 'carmusr_jmp.1.02';
PROMPT


------ module_version_sas_leave_parameters_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_leave_parameters
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_leave_parameters with version udm.1.02'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_leave_parameters'
      AND c_cfg_value = 'udm.1.02';
PROMPT


------ module_version_sas_leave_reduction_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_leave_reduction
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_leave_reduction with version carmusr_jmp.1.02'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_leave_reduction'
      AND c_cfg_value = 'carmusr_jmp.1.02';
PROMPT


------ module_version_sas_legality_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_legality
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_legality with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_legality'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_manpower_accumulators_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_manpower_accumulators
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_manpower_accumulators with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_manpower_accumulators'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_nop_crew_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_nop_crew
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_nop_crew with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_nop_crew'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_notification_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_notification
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_notification with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_notification'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_passive_bookings_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_passive_bookings
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_passive_bookings with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_passive_bookings'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_paxlst_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_paxlst
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_paxlst with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_paxlst'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_planning_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_planning
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_planning with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_planning'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_published_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_published
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_published with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_published'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_rave_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_rave
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_rave with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_rave'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_rule_violation_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_rule_violation
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_rule_violation with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_rule_violation'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_special_local_transport_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_special_local_transport
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_special_local_transport with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_special_local_transport'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_special_schedules_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_special_schedules
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_special_schedules with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_special_schedules'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_standby_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_standby
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_standby with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_standby'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_table_accumulators_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_table_accumulators
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_table_accumulators with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_table_accumulators'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_training_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_training
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_training with version sas.dm.1.01'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_training'
      AND c_cfg_value = 'sas.dm.1.01';
PROMPT


------ module_version_sas_training_cnx_time_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_training_cnx_time
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_training_cnx_time with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_training_cnx_time'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ module_version_sas_transport_bookings_pre_manual_check.sql ------
PROMPT Pre-checking version of module sas_transport_bookings
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Expected module sas_transport_bookings with version sas.dm.1.00'
    ELSE NULL
    END AS message
    FROM dave_schemacfg
    WHERE c_cfg_type = 'dave'
      AND c_cfg_group = 'module'
      AND c_cfg_name = 'sas_transport_bookings'
      AND c_cfg_value = 'sas.dm.1.00';
PROMPT


------ drop_entity_crew_filter_group_tag_pre_manual_check.sql ------
PROMPT Pre-checking entity crew_filter_group_tag before dropping for broken references
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN NULL
    ELSE 'Entity "crew_filter_group_tag" is referenced from unknown entities ' || LISTAGG(c_ent_name, ', ')
        WITHIN GROUP (ORDER BY c_ent_name)
    END AS message
    FROM dave_entity_fks
    WHERE c_fk_tgtname = 'crew_filter_group_tag';
PROMPT


------ drop_entity_estr_calc_node_node_tag_pre_manual_check.sql ------
PROMPT Pre-checking entity estr_calc_node_node_tag before dropping for broken references
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN NULL
    ELSE 'Entity "estr_calc_node_node_tag" is referenced from unknown entities ' || LISTAGG(c_ent_name, ', ')
        WITHIN GROUP (ORDER BY c_ent_name)
    END AS message
    FROM dave_entity_fks
    WHERE c_fk_tgtname = 'estr_calc_node_node_tag';
PROMPT


------ drop_entity_estr_calc_node_tag_pre_manual_check.sql ------
PROMPT Pre-checking entity estr_calc_node_tag before dropping for broken references
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN NULL
    ELSE 'Entity "estr_calc_node_tag" is referenced from unknown entities ' || LISTAGG(c_ent_name, ', ')
        WITHIN GROUP (ORDER BY c_ent_name)
    END AS message
    FROM dave_entity_fks
    WHERE c_fk_tgtname = 'estr_calc_node_tag'
      AND c_ent_name NOT IN ('estr_calc_node_node_tag');
PROMPT


------ drop_entity_resource_group_tag_pre_manual_check.sql ------
PROMPT Pre-checking entity resource_group_tag before dropping for broken references
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN NULL
    ELSE 'Entity "resource_group_tag" is referenced from unknown entities ' || LISTAGG(c_ent_name, ', ')
        WITHIN GROUP (ORDER BY c_ent_name)
    END AS message
    FROM dave_entity_fks
    WHERE c_fk_tgtname = 'resource_group_tag'
      AND c_ent_name NOT IN ('crew_filter_group_tag');
PROMPT


------ table_name_uniqueness_bought_days_svs_pre_manual_check.sql ------
PROMPT Pre-checking table bought_days_svs for table name uniqueness
PROMPT ================================================================================

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
PROMPT


------ index_name_uniqueness_bought_days_svs_pre_manual_check.sql ------
PROMPT Pre-checking table bought_days_svs for index name uniqueness
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN NULL
    ELSE 'Table "bought_days_svs" tries to create already existing indexes: ' || LISTAGG(index_name, ', ')
        WITHIN GROUP (ORDER BY index_name)
    END AS message
    FROM user_indexes
    WHERE index_name IN ('BOUGHT_DAYS_SVS_IB', 'BOUGHT_DAYS_SVS_IN', 'BOUGHT_DAYS_SVS_IP');
PROMPT


------ table_name_uniqueness_bought_days_svs_tmp_pre_manual_check.sql ------
PROMPT Pre-checking table bought_days_svs_tmp for table name uniqueness
PROMPT ================================================================================

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
PROMPT


------ alter_table_published_roster_pre_manual_check.sql ------
PROMPT Pre-checking table published_roster for index name uniqueness
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN NULL
    ELSE 'Table "published_roster" tries to create already existing indexes: ' || LISTAGG(index_name, ', ')
        WITHIN GROUP (ORDER BY index_name)
    END AS message
    FROM user_indexes
    WHERE index_name IN ('PUBLISHED_ROSTER_IX1');
PROMPT

PROMPT Pre-checking table published_roster before altering for existence of removed or modified indexes
PROMPT ================================================================================
SELECT CASE COUNT(*)
    WHEN 0 THEN 'Table "published_roster" is missing expected index "idx$$_d65b0001"'
    ELSE NULL
    END AS message
    FROM user_indexes
    WHERE index_name = 'IDX$$_D65B0001';
PROMPT


------ drop_table_crew_filter_group_tag_pre_manual_check.sql ------
PROMPT Pre-checking table crew_filter_group_tag before dropping for unknown columns
PROMPT ================================================================================

SELECT CASE COUNT(*)
  WHEN 0 THEN NULL
  ELSE 'Table "crew_filter_group_tag" has unknown columns ' || LISTAGG(column_name, ', ')
    WITHIN GROUP (ORDER BY column_name)
  END AS message
  FROM USER_TAB_COLUMNS
  WHERE table_name = 'CREW_FILTER_GROUP_TAG'
  AND column_name NOT IN ('REVID', 'DELETED', 'PREV_REVID', 'NEXT_REVID', 'BRANCHID', 'CREWFILTER_NAME', 'CREWFILTER_CAT', 'GROUPTAG');
PROMPT


------ drop_table_crew_filter_group_tag_tmp_pre_manual_check.sql ------
PROMPT Pre-checking table crew_filter_group_tag_tmp before dropping for unknown columns
PROMPT ================================================================================

SELECT CASE COUNT(*)
  WHEN 0 THEN NULL
  ELSE 'Table "crew_filter_group_tag_tmp" has unknown columns ' || LISTAGG(column_name, ', ')
    WITHIN GROUP (ORDER BY column_name)
  END AS message
  FROM USER_TAB_COLUMNS
  WHERE table_name = 'CREW_FILTER_GROUP_TAG_TMP'
  AND column_name NOT IN ('REVID', 'DELETED', 'PREV_REVID', 'NEXT_REVID', 'BRANCHID', 'CREWFILTER_NAME', 'CREWFILTER_CAT', 'GROUPTAG');
PROMPT


------ drop_table_estr_calc_node_node_tag_pre_manual_check.sql ------
PROMPT Pre-checking table estr_calc_node_node_tag before dropping for unknown columns
PROMPT ================================================================================

SELECT CASE COUNT(*)
  WHEN 0 THEN NULL
  ELSE 'Table "estr_calc_node_node_tag" has unknown columns ' || LISTAGG(column_name, ', ')
    WITHIN GROUP (ORDER BY column_name)
  END AS message
  FROM USER_TAB_COLUMNS
  WHERE table_name = 'ESTR_CALC_NODE_NODE_TAG'
  AND column_name NOT IN ('REVID', 'DELETED', 'PREV_REVID', 'NEXT_REVID', 'BRANCHID', 'CALCNODE_SETUP_NAME', 'CALCNODE_SETUP_CAT', 'CALCNODE_NAME', 'NODETAG');
PROMPT


------ drop_table_estr_calc_node_node_tag_tmp_pre_manual_check.sql ------
PROMPT Pre-checking table estr_calc_node_node_tag_tmp before dropping for unknown columns
PROMPT ================================================================================

SELECT CASE COUNT(*)
  WHEN 0 THEN NULL
  ELSE 'Table "estr_calc_node_node_tag_tmp" has unknown columns ' || LISTAGG(column_name, ', ')
    WITHIN GROUP (ORDER BY column_name)
  END AS message
  FROM USER_TAB_COLUMNS
  WHERE table_name = 'ESTR_CALC_NODE_NODE_TAG_TMP'
  AND column_name NOT IN ('REVID', 'DELETED', 'PREV_REVID', 'NEXT_REVID', 'BRANCHID', 'CALCNODE_SETUP_NAME', 'CALCNODE_SETUP_CAT', 'CALCNODE_NAME', 'NODETAG');
PROMPT


------ drop_table_estr_calc_node_tag_pre_manual_check.sql ------
PROMPT Pre-checking table estr_calc_node_tag before dropping for unknown columns
PROMPT ================================================================================

SELECT CASE COUNT(*)
  WHEN 0 THEN NULL
  ELSE 'Table "estr_calc_node_tag" has unknown columns ' || LISTAGG(column_name, ', ')
    WITHIN GROUP (ORDER BY column_name)
  END AS message
  FROM USER_TAB_COLUMNS
  WHERE table_name = 'ESTR_CALC_NODE_TAG'
  AND column_name NOT IN ('REVID', 'DELETED', 'PREV_REVID', 'NEXT_REVID', 'BRANCHID', 'ID', 'CAPTION', 'CAT');
PROMPT


------ drop_table_estr_calc_node_tag_tmp_pre_manual_check.sql ------
PROMPT Pre-checking table estr_calc_node_tag_tmp before dropping for unknown columns
PROMPT ================================================================================

SELECT CASE COUNT(*)
  WHEN 0 THEN NULL
  ELSE 'Table "estr_calc_node_tag_tmp" has unknown columns ' || LISTAGG(column_name, ', ')
    WITHIN GROUP (ORDER BY column_name)
  END AS message
  FROM USER_TAB_COLUMNS
  WHERE table_name = 'ESTR_CALC_NODE_TAG_TMP'
  AND column_name NOT IN ('REVID', 'DELETED', 'PREV_REVID', 'NEXT_REVID', 'BRANCHID', 'ID', 'CAPTION', 'CAT');
PROMPT


------ drop_table_resource_group_tag_pre_manual_check.sql ------
PROMPT Pre-checking table resource_group_tag before dropping for unknown columns
PROMPT ================================================================================

SELECT CASE COUNT(*)
  WHEN 0 THEN NULL
  ELSE 'Table "resource_group_tag" has unknown columns ' || LISTAGG(column_name, ', ')
    WITHIN GROUP (ORDER BY column_name)
  END AS message
  FROM USER_TAB_COLUMNS
  WHERE table_name = 'RESOURCE_GROUP_TAG'
  AND column_name NOT IN ('REVID', 'DELETED', 'PREV_REVID', 'NEXT_REVID', 'BRANCHID', 'ID', 'CAPTION', 'CAT');
PROMPT


------ drop_table_resource_group_tag_tmp_pre_manual_check.sql ------
PROMPT Pre-checking table resource_group_tag_tmp before dropping for unknown columns
PROMPT ================================================================================

SELECT CASE COUNT(*)
  WHEN 0 THEN NULL
  ELSE 'Table "resource_group_tag_tmp" has unknown columns ' || LISTAGG(column_name, ', ')
    WITHIN GROUP (ORDER BY column_name)
  END AS message
  FROM USER_TAB_COLUMNS
  WHERE table_name = 'RESOURCE_GROUP_TAG_TMP'
  AND column_name NOT IN ('REVID', 'DELETED', 'PREV_REVID', 'NEXT_REVID', 'BRANCHID', 'ID', 'CAPTION', 'CAT');
PROMPT

