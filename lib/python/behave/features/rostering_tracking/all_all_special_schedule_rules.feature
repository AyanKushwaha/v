@TRACKING @ROSTERING
Feature: Special schedule rules should apply if any of the duties is flight duties

########################
# JIRA - SKCMS-1552
########################

##############################################################################
  Background: Setup common data
    Given planning period from 1AUG2020 to 31AUG2020
    Given Tracking

    Given a crew member with
        | attribute  | value |
        | crew rank  | FC    |
        | title rank | FC    |
        | region     | SKS   |
        | base       | STO   |

    Given a crew member with
        | attribute  | value |
        | crew rank  | FC    |
        | title rank | FC    |
        | region     | SKS   |
        | base       | STO   |

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000351  | TRD     | OSL     | 15AUG2020 09:25 | 15AUG2020 10:20 | 73T     |         |
           | leg     | SK      | 004112  | OSL     | BOO     | 15AUG2020 11:50 | 15AUG2020 13:20 | 73B     |         |
           | leg     | SK      | 004113  | BOO     | OSL     | 15AUG2020 13:45 | 15AUG2020 18:15 | 73B     |         |
           | ground  |         |         | OSL     | OSL     | 16AUG2020 22:00 | 17AUG2020 02:00 |         | K3      |
           | dh      | SK      | 000332  | OSL     | TRD     | 17AUG2020 07:05 | 17AUG2020 12:05 | 738     |         |
    Given trip 1 is assigned to crew member 1 in position FP

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000351  | TRD     | OSL     | 15AUG2020 09:25 | 15AUG2020 10:20 | 73T     |         |
           | leg     | SK      | 004112  | OSL     | BOO     | 15AUG2020 11:50 | 15AUG2020 13:20 | 73B     |         |
           | leg     | SK      | 004113  | BOO     | OSL     | 15AUG2020 13:45 | 15AUG2020 18:15 | 73B     |         |
           | dh      | SK      | 000332  | OSL     | TRD     | 17AUG2020 07:05 | 17AUG2020 12:05 | 738     |         |
    Given trip 2 is assigned to crew member 2 in position FP

##############################################################################

    @SCENARIO1
    Scenario: Forbidden lower rank rule

    Given table special_schedules is overridden with the following
    | crewid  | typ            | validfrom        | str_val | validto          | int_from | int_to | time_val |
    | Crew001 | ForbiddenAct   | 01AUG2020 00:00  | LOWER   | 31AUG2020 00:00  |          |        |          |

    When I show "crew" in window 1
    Then rave "crew.%has_spec_sched_in_trip%("ForbiddenAct")" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "crew.%has_spec_sched_in_trip%("ForbiddenAct")" shall be "False" on leg 1 on trip 1 on roster 2
    and the rule "rules_soft_ccr_cct.sft_spec_sched_forbidden_lower_rank_FC" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_soft_ccr_cct.sft_spec_sched_forbidden_lower_rank_FC" shall pass on leg 1 on trip 1 on roster 2


    @SCENARIO2
    Scenario: Forbidden AC family rule

    Given table special_schedules is overridden with the following
    | crewid  | typ            | validfrom        | str_val | validto          | int_from | int_to | time_val |
    | Crew001 | ForbiddenAcFam | 01AUG2020 00:00  | B737    | 31AUG2020 00:00  |          |        |          |
    | Crew002 | ForbiddenAcFam | 01AUG2020 00:00  | AL      | 31AUG2020 00:00  |          |        |          |

    When I show "crew" in window 1
    Then rave "crew.%has_spec_sched_in_trip%("ForbiddenAcFam")" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "crew.%has_spec_sched_in_trip%("ForbiddenAcFam")" shall be "True" on leg 1 on trip 1 on roster 2
    and the rule "rules_soft_ccr_cct.sft_spec_sched_forbidden_ac_fam_ALL" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_soft_ccr_cct.sft_spec_sched_forbidden_ac_fam_ALL" shall pass on leg 1 on trip 1 on roster 2


    @SCENARIO3
    Scenario: Trip length rule

    Given table special_schedules is overridden with the following
    | crewid  | typ            | validfrom        | str_val | validto          | int_from | int_to | time_val |
    | Crew001 | TripLength     | 01AUG2020 00:00  | *       | 31AUG2020 00:00  | 1        | 2      |          |
    | Crew002 | TripLength     | 01AUG2020 00:00  | *       | 31AUG2020 00:00  | 1        | 3      |          |

    When I show "crew" in window 1
    Then rave "crew.%has_spec_sched_in_trip%("TripLength")" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "crew.%has_spec_sched_in_trip%("TripLength")" shall be "True" on leg 1 on trip 1 on roster 2
    and the rule "rules_soft_ccr_cct.sft_spec_sched_trip_length_ALL" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_soft_ccr_cct.sft_spec_sched_trip_length_ALL" shall pass on leg 1 on trip 1 on roster 2


    @SCENARIO4
    Scenario: Check in rule

    Given table special_schedules is overridden with the following
    | crewid  | typ            | validfrom        | str_val | validto          | int_from | int_to | time_val |
    | Crew001 | CheckIn        | 01AUG2020 00:00  | *       | 31AUG2020 00:00  | 1        | 7      | 11:00    |
    | Crew002 | CheckIn        | 01AUG2020 00:00  | *       | 31AUG2020 00:00  | 1        | 7      | 08:00    |


    When I show "crew" in window 1
    Then rave "crew.%has_spec_sched_in_trip%("CheckIn")" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "crew.%has_spec_sched_in_trip%("CheckIn")" shall be "True" on leg 1 on trip 1 on roster 2
    and the rule "rules_soft_ccr_cct.sft_spec_sched_ci_ALL" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_soft_ccr_cct.sft_spec_sched_ci_ALL" shall pass on leg 1 on trip 1 on roster 2


    @SCENARIO5
    Scenario: Check out rule

    Given table special_schedules is overridden with the following
    | crewid  | typ            | validfrom        | str_val | validto          | int_from | int_to | time_val |
    | Crew001 | CheckOut       | 01AUG2020 00:00  | *       | 31AUG2020 00:00  | 1        | 7      | 00:00    |
    | Crew002 | CheckOut       | 01AUG2020 00:00  | *       | 31AUG2020 00:00  | 1        | 7      | 15:00    |


    When I show "crew" in window 1
    Then rave "crew.%has_spec_sched_in_trip%("CheckOut")" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "crew.%has_spec_sched_in_trip%("CheckOut")" shall be "True" on leg 1 on trip 1 on roster 2
    and the rule "rules_soft_ccr_cct.sft_spec_sched_co_ALL" shall fail on leg 5 on trip 1 on roster 1
    and the rule "rules_soft_ccr_cct.sft_spec_sched_co_ALL" shall pass on leg 4 on trip 1 on roster 2


    @SCENARIO6
    Scenario: Max duty rule

    Given table special_schedules is overridden with the following
    | crewid  | typ            | validfrom        | str_val | validto          | int_from | int_to | time_val |
    | Crew001 | MaxDuty        | 01AUG2020 00:00  | *       | 31AUG2020 00:00  |          |        | 06:00    |
    | Crew002 | MaxDuty        | 01AUG2020 00:00  | *       | 31AUG2020 00:00  |          |        | 14:00    |


    When I show "crew" in window 1
    Then rave "crew.%has_spec_sched_in_trip%("MaxDuty")" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "crew.%has_spec_sched_in_trip%("MaxDuty")" shall be "True" on leg 1 on trip 1 on roster 2
    and the rule "rules_soft_ccr_cct.sft_spec_sched_duty_per_day_ALL" shall fail on leg 5 on trip 1 on roster 1
    and the rule "rules_soft_ccr_cct.sft_spec_sched_duty_per_day_ALL" shall pass on leg 4 on trip 1 on roster 2


    @SCENARIO7
    Scenario: Max legs rule

    Given table special_schedules is overridden with the following
    | crewid  | typ            | validfrom        | str_val | validto          | int_from | int_to | time_val |
    | Crew001 | MaxLegs        | 01AUG2020 00:00  | *       | 31AUG2020 00:00  | 1        | 2      |          |
    | Crew002 | MaxLegs        | 01AUG2020 00:00  | *       | 31AUG2020 00:00  | 1        | 3      |          |


    When I show "crew" in window 1
    Then rave "crew.%has_spec_sched_in_trip%("MaxLegs")" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "crew.%has_spec_sched_in_trip%("MaxLegs")" shall be "True" on leg 1 on trip 1 on roster 2
    and the rule "rules_soft_ccr_cct.sft_spec_sched_legs_in_duty_pass_ALL" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_soft_ccr_cct.sft_spec_sched_legs_in_duty_pass_ALL" shall pass on leg 1 on trip 1 on roster 2


    @SCENARIO8
    Scenario: Max block hours rule

    Given table special_schedules is overridden with the following
    | crewid  | typ            | validfrom        | str_val | validto          | int_from | int_to | time_val |
    | Crew001 | MaxBlh         | 01AUG2020 00:00  | *       | 31AUG2020 00:00  |          |        | 04:00    |
    | Crew002 | MaxBlh         | 01AUG2020 00:00  | *       | 31AUG2020 00:00  |          |        | 06:00    |


    When I show "crew" in window 1
    Then rave "crew.%has_spec_sched_in_trip%("MaxBlh")" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "crew.%has_spec_sched_in_trip%("MaxBlh")" shall be "True" on leg 1 on trip 1 on roster 2
    and the rule "rules_soft_ccr_cct.sft_spec_sched_blh_per_leg_ALL" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_soft_ccr_cct.sft_spec_sched_blh_per_leg_ALL" shall pass on leg 1 on trip 1 on roster 2


    @SCENARIO9
    Scenario: Forbidden destination rule

    Given table special_schedules is overridden with the following
    | crewid  | typ            | validfrom        | str_val | validto          | int_from | int_to | time_val |
    | Crew001 | ForbiddenDest  | 01AUG2020 00:00  | BOO     | 31AUG2020 00:00  |          |        |          |
    | Crew002 | ForbiddenDest  | 01AUG2020 00:00  | ARN     | 31AUG2020 00:00  |          |        |          |


    When I show "crew" in window 1
    Then rave "crew.%has_spec_sched_in_trip%("ForbiddenDest")" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "crew.%has_spec_sched_in_trip%("ForbiddenDest")" shall be "True" on leg 1 on trip 1 on roster 2
    and the rule "rules_soft_ccr_cct.sft_spec_sched_forbidden_dest_ALL" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_soft_ccr_cct.sft_spec_sched_forbidden_dest_ALL" shall pass on leg 1 on trip 1 on roster 2
