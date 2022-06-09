@CC
Feature:

    Background: Set up
        Given planning period from 1JUL2019 to 1AUG2019

        Given a crew member with
        | attribute  | value  | valid from | valid to  |
        | base       | CPH    |            |           |
        | title rank | AH     |            |           |
        | region     | SKD    |            |           |
        | contract   | V304   |            |           |

        Given table property_set is overridden with the following
        | id                       | si               |
        | ofdx_agmt_groups_TW99    | Safety training  |
        | ofdx_attend_goal_TW99    | Safety training  |
        | ofdx_attend_limit_TW99   | Safety training  |
        | ofdx_name_TW99           | Safety training  |
        | ofdx_period_start_TW99   | Safety training  |
        | ofdx_period_end_TW99     | Safety training  |
        | ofdx_qualifications_TW99 | Safety training  |

        Given table property is overridden with the following
        | id                       | validfrom | validto   | value_abs | value_int | value_str                               |
        | ofdx_agmt_groups_TW99    | 1JAN1986  | 31DEC2035 |           |           | SKD_CC_AG;SKS_CC_AG;NKF_CC_AG;SNK_CC_AG |
        | ofdx_attend_goal_TW99    | 01Jul2019 | 31Jan2020 |           | 1         |                                         |
        | ofdx_attend_limit_TW99   | 01Jul2019 | 31Jan2020 |           | 1         |                                         |
        | ofdx_name_TW99           | 01Jul2019 | 31Jan2020 |           |           | Safety training                         |
        | ofdx_period_end_TW99     | 01Jul2019 | 31Jan2020 | 31Jan2020 |           |                                         |
        | ofdx_period_start_TW99   | 01Jul2019 | 31Jan2020 | 01Jul2019 |           |                                         |
        | ofdx_qualifications_TW99 | 01Jul2019 | 31Jan2020 |           |           | ACQUAL+AL                               |

	Given table aircraft_type additionally contains the following
        | id  | maintype | crewbunkfc | crewbunkcc | maxfc | maxcc | class1fc | class1cc | class2cc | class3cc |
        | 35X | A350     | 2          | 4          | 4     | 10    | 2        | 1        | 0        | 0        |

        Given table ac_qual_map additionally contains the following
        | ac_type | aoc | ac_qual_fc | ac_qual_cc |
        | 35X     | SK  | A5         | AL         |

###############################################################################

    @SCENARIO1 @planning
    Scenario: Check that TW99 activity can be assigned to crew member with AL qualification

       Given crew member 1 has qualification "ACQUAL+AL" from 1APR2019 to 31DEC2035

       Given crew member 1 has a personal activity "TW99" at station "CPH" that starts at 3JUL2019 22:00 and ends at 4JUL2019 22:00

       When I show "crew" in window 1
       and I load rule set "Rostering_CC"
       and I set parameter "fundamental.%start_para%" to "1JUL2019 00:00"
       and I set parameter "fundamental.%end_para%" to "31JUL2019 00:00"

       Then the rule "rules_training_ccr.check_qual_al_for_tw99" shall pass on leg 1 on trip 1 on roster 1
       and the rule "rules_indust_common.ind_training_ofdx_activity_allowed" shall pass on leg 1 on trip 1 on roster 1


    @SCENARIO2 @tracking
    Scenario: Check that TW99 activity can be assigned to crew member with AL qualification in tracking

       Given crew member 1 has qualification "ACQUAL+AL" from 1APR2019 to 31DEC2035

       Given crew member 1 has a personal activity "TW99" at station "CPH" that starts at 3JUL2019 22:00 and ends at 4JUL2019 22:00

       When I show "crew" in window 1
       and I load rule set "Tracking"

       Then the rule "rules_training_ccr.check_qual_al_for_tw99" shall pass on leg 1 on trip 1 on roster 1
       and the rule "rules_soft_ccr_cct.sft_activity_not_allowed_on_day_all" shall pass on leg 1 on trip 1 on roster 1
       and the rule "rules_indust_common.ind_training_ofdx_activity_allowed" shall pass on leg 1 on trip 1 on roster 1


    @SCENARIO3 @planning
    Scenario: Check that TW99 activity can't be assigned to crew member without AL qualification

       Given crew member 1 has a personal activity "TW99" at station "CPH" that starts at 3JUL2019 22:00 and ends at 4JUL2019 22:00

       When I show "crew" in window 1
       and I load rule set "Rostering_CC"
       and I set parameter "fundamental.%start_para%" to "1JUL2019 00:00"
       and I set parameter "fundamental.%end_para%" to "31JUL2019 00:00"

       Then the rule "rules_training_ccr.check_qual_al_for_tw99" shall fail on leg 1 on trip 1 on roster 1
       and the rule "rules_indust_common.ind_training_ofdx_activity_allowed" shall fail on leg 1 on trip 1 on roster 1


    @SCENARIO4 @tracking
    Scenario: Check that TW99 activity can't be assigned to crew member without AL qualification in tracking

       Given crew member 1 has a personal activity "TW99" at station "CPH" that starts at 3JUL2019 22:00 and ends at 4JUL2019 22:00

       When I show "crew" in window 1
       and I load rule set "Tracking"

       Then the rule "rules_training_ccr.check_qual_al_for_tw99" shall fail on leg 1 on trip 1 on roster 1
       and the rule "rules_soft_ccr_cct.sft_activity_not_allowed_on_day_all" shall pass on leg 1 on trip 1 on roster 1
       and the rule "rules_indust_common.ind_training_ofdx_activity_allowed" shall fail on leg 1 on trip 1 on roster 1


    @SCENARIO5 @planning
    Scenario: Check that TW99 activity can be assigned to crew member with no current AL qual but that gets AL qual from course within 3 days

       Given table course_participant is overridden with the following
       | nr | c_name          | c_cat | startofcourse | endofcourse | pos                 | fromcrewgroup_name    | fromcrewgroup_cat | tocrewgroup_name | tocrewgroup_cat | crew    |
       | 2  | test skcms-2087 | C     | 02Jul2019     | 02Sep2019   | 0/0/0/0/0/0/1/0/0/0 | STO-AH-SH-EXKL RP/LIM | C                 | STO-AH-LH        | C               | Crew001 |

       Given table course is overridden with the following
       | name            | cat | status   | carrier | ctype | qualobt_typ | qualobt_subtype | createdate      | templname | startdate | enddate   | cc                    | airport |
       | test skcms-2087 | C   | RELEASED | SK      | CONV  | ACQUAL      | AL              | 20May2019 06:56 | test_2087 | 02Jul2019 | 02Sep2019 | 0/0/0/0//0/0/2/0//0/0 | ARN     |

       Given crew member 1 has qualification "ACQUAL+AL" from 6JUL2019 to 31DEC2035

       Given crew member 1 has a personal activity "TW99" at station "CPH" that starts at 3JUL2019 22:00 and ends at 4JUL2019 22:00

       When I show "crew" in window 1
       and I load rule set "Rostering_CC"
       and I set parameter "fundamental.%start_para%" to "1JUL2019 00:00"
       and I set parameter "fundamental.%end_para%" to "31JUL2019 00:00"

       Then the rule "rules_training_ccr.check_qual_al_for_tw99" shall pass on leg 1 on trip 1 on roster 1
       and the rule "rules_indust_common.ind_training_ofdx_activity_allowed" shall pass on leg 1 on trip 1 on roster 1


    @SCENARIO6 @tracking
    Scenario: Check that TW99 activity can be assigned to crew member with no current AL qual but that gets AL qual from course within 3 days in tracking

       Given table course_participant is overridden with the following
       | nr | c_name          | c_cat | startofcourse | endofcourse | pos                 | fromcrewgroup_name    | fromcrewgroup_cat | tocrewgroup_name | tocrewgroup_cat | crew    |
       | 2  | test skcms-2087 | C     | 02Jul2019     | 02Sep2019   | 0/0/0/0/0/0/1/0/0/0 | STO-AH-SH-EXKL RP/LIM | C                 | STO-AH-LH        | C               | Crew001 |

       Given table course is overridden with the following
       | name            | cat | status   | carrier | ctype | qualobt_typ | qualobt_subtype | createdate      | templname | startdate | enddate   | cc                    | airport |
       | test skcms-2087 | C   | RELEASED | SK      | CONV  | ACQUAL      | AL              | 20May2019 06:56 | test_2087 | 02Jul2019 | 02Sep2019 | 0/0/0/0//0/0/2/0//0/0 | ARN     |

       Given crew member 1 has qualification "ACQUAL+AL" from 6JUL2019 to 31DEC2035

       Given crew member 1 has a personal activity "TW99" at station "CPH" that starts at 3JUL2019 22:00 and ends at 4JUL2019 22:00

       When I show "crew" in window 1
       and I load rule set "Tracking"

       Then the rule "rules_training_ccr.check_qual_al_for_tw99" shall pass on leg 1 on trip 1 on roster 1
       and the rule "rules_indust_common.ind_training_ofdx_activity_allowed" shall pass on leg 1 on trip 1 on roster 1


    @SCENARIO7 @planning
    Scenario: Check that TW99 activity can not be assigned to crew member with no current AL qual but gains AL qual from course later than 3 days in the future

       Given table course_participant is overridden with the following
       | nr | c_name          | c_cat | startofcourse | endofcourse | pos                 | fromcrewgroup_name    | fromcrewgroup_cat | tocrewgroup_name | tocrewgroup_cat | crew    |
       | 2  | test skcms-2087 | C     | 02Jul2019     | 02Sep2019   | 0/0/0/0/0/0/1/0/0/0 | STO-AH-SH-EXKL RP/LIM | C                 | STO-AH-LH        | C               | Crew001 |

       Given table course is overridden with the following
       | name            | cat | status   | carrier | ctype | qualobt_typ | qualobt_subtype | createdate      | templname | startdate | enddate   | cc                    | airport |
       | test skcms-2087 | C   | RELEASED | SK      | CONV  | ACQUAL      | AL              | 20May2019 06:56 | test_2087 | 02Jul2019 | 02Sep2019 | 0/0/0/0//0/0/2/0//0/0 | ARN     |

       Given crew member 1 has qualification "ACQUAL+AL" from 6JUL2019 to 31DEC2035

       Given crew member 1 has a personal activity "TW99" at station "CPH" that starts at 1JUL2019 22:00 and ends at 2JUL2019 22:00

       When I show "crew" in window 1
       and I load rule set "Rostering_CC"
       and I set parameter "fundamental.%start_para%" to "1JUL2019 00:00"
       and I set parameter "fundamental.%end_para%" to "31JUL2019 00:00"

       Then the rule "rules_training_ccr.check_qual_al_for_tw99" shall fail on leg 1 on trip 1 on roster 1
       and the rule "rules_indust_common.ind_training_ofdx_activity_allowed" shall fail on leg 1 on trip 1 on roster 1


    @SCENARIO8 @planning
    Scenario: Check that TW99 activity can not be assigned to crew member with no current AL qual and that gets AL qual within 3 days, but not from course
       
       Given crew member 1 has qualification "ACQUAL+AL" from 6JUL2019 to 31DEC2035

       Given crew member 1 has a personal activity "TW99" at station "CPH" that starts at 3JUL2019 22:00 and ends at 4JUL2019 22:00

       When I show "crew" in window 1
       and I load rule set "Rostering_CC"
       and I set parameter "fundamental.%start_para%" to "1JUL2019 00:00"
       and I set parameter "fundamental.%end_para%" to "31JUL2019 00:00"

       #The rule in part 1 has hardcoded 3 day grace period, so no point checking it here, just check if ofdx is allowed
       Then the rule "rules_indust_common.ind_training_ofdx_activity_allowed" shall fail on leg 1 on trip 1 on roster 1


    @SCENARIO9 @tracking
    Scenario: Check that TW99 activity can not be assigned to crew member with no current AL qual and that gets AL qual within 3 days, but not from course in tracking

       Given crew member 1 has qualification "ACQUAL+AL" from 6JUL2019 to 31DEC2035

       Given crew member 1 has a personal activity "TW99" at station "CPH" that starts at 3JUL2019 22:00 and ends at 4JUL2019 22:00

       When I show "crew" in window 1
       and I load rule set "Tracking"

       #The rule in part 1 has hardcoded 3 day grace period, so no point checking it here, just check if ofdx is allowed
       Then the rule "rules_indust_common.ind_training_ofdx_activity_allowed" shall fail on leg 1 on trip 1 on roster 1


    @SCENARIO10 @planning
    Scenario: Check that A350 legs are illegal before TW99 activity in roster and legal after
       Given Rostering_CC

       Given crew member 1 has qualification "ACQUAL+AL" from 1APR2019 to 31DEC2035

       Given a trip with the following activities
       | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
       | leg | 0001 | CPH     | LHR     | 10JUL2019 | 10:00 | 11:00 | SK  | 35X    |
       | leg | 0002 | LHR     | CPH     | 10JUL2019 | 12:00 | 13:00 | SK  | 35X    |

       Given trip 1 is assigned to crew member 1 in position AH

       Given crew member 1 has a personal activity "TW99" at station "CPH" that starts at 13JUL2019 22:00 and ends at 14JUL2019 22:00

       Given a trip with the following activities
       | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
       | leg | 0001 | CPH     | LHR     | 20JUL2019 | 10:00 | 11:00 | SK  | 35X    |
       | leg | 0002 | LHR     | CPH     | 20JUL2019 | 12:00 | 13:00 | SK  | 35X    |

       Given trip 2 is assigned to crew member 1 in position AH

       When I show "crew" in window 1

       Then the rule "rules_qual_ccr.qln_ac_type_ok_all" shall fail on leg 1 on trip 1 on roster 1
       and the rule "rules_qual_ccr.qln_ac_type_ok_all" shall pass on leg 1 on trip 3 on roster 1


    @SCENARIO11 @planning
    Scenario: Check that A350 legs are legal after TW99 activity in training log
       Given Rostering_CC

       Given crew member 1 has qualification "ACQUAL+AL" from 1APR2019 to 31DEC2035

       Given table crew_training_log additionally contains the following
       | crew          | typ        | code | tim       |
       | crew member 1 | COURSE WEB | TW99 | 17APR2019 |

       Given a trip with the following activities
       | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
       | leg | 0001 | CPH     | LHR     | 10JUL2019 | 10:00 | 11:00 | SK  | 35X    |
       | leg | 0002 | LHR     | CPH     | 10JUL2019 | 12:00 | 13:00 | SK  | 35X    |

       Given trip 1 is assigned to crew member 1 in position AH

       Given a trip with the following activities
       | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
       | leg | 0001 | CPH     | LHR     | 20JUL2019 | 10:00 | 11:00 | SK  | 33A    |
       | leg | 0002 | LHR     | CPH     | 20JUL2019 | 12:00 | 13:00 | SK  | 33A    |

       Given trip 2 is assigned to crew member 1 in position AH

       When I show "crew" in window 1

       Then the rule "rules_qual_ccr.qln_ac_type_ok_all" shall pass on leg 1 on trip 1 on roster 1
       and the rule "rules_qual_ccr.qln_ac_type_ok_all" shall pass on leg 1 on trip 2 on roster 1


    @SCENARIO12 @planning
    Scenario: Check that A350 legs are illegal with no TW99 activity in training log or roster
       Given Rostering_CC

       Given crew member 1 has qualification "ACQUAL+AL" from 1APR2019 to 31DEC2035

       Given a trip with the following activities
       | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
       | leg | 0001 | CPH     | LHR     | 10JUL2019 | 10:00 | 11:00 | SK  | 35X    |
       | leg | 0002 | LHR     | CPH     | 10JUL2019 | 12:00 | 13:00 | SK  | 35X    |

       Given trip 1 is assigned to crew member 1 in position AH

       Given a trip with the following activities
       | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
       | leg | 0001 | CPH     | LHR     | 20JUL2019 | 10:00 | 11:00 | SK  | 33A    |
       | leg | 0002 | LHR     | CPH     | 20JUL2019 | 12:00 | 13:00 | SK  | 33A    |

       Given trip 2 is assigned to crew member 1 in position AH

       When I show "crew" in window 1

       Then the rule "rules_qual_ccr.qln_ac_type_ok_all" shall fail on leg 1 on trip 1 on roster 1
       and rave "rules_qual_ccr.%qln_ac_types_failtext_leg%" shall be "OMA: Qual. AC-type AL requires TW99 for A5 flight" on leg 1 on trip 1 on roster 1
       and the rule "rules_qual_ccr.qln_ac_type_ok_all" shall pass on leg 1 on trip 2 on roster 1


    @SCENARIO13 @planning
    Scenario: Check that A350 legs are illegal with no AL qualification
       Given Rostering_CC

       Given crew member 1 has qualification "ACQUAL+A2" from 1APR2019 to 31DEC2035

       Given a trip with the following activities
       | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
       | leg | 0001 | CPH     | LHR     | 10JUL2019 | 10:00 | 11:00 | SK  | 35X    |
       | leg | 0002 | LHR     | CPH     | 10JUL2019 | 12:00 | 13:00 | SK  | 35X    |

       Given trip 1 is assigned to crew member 1 in position AH

       Given a trip with the following activities
       | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
       | leg | 0001 | CPH     | LHR     | 20JUL2019 | 10:00 | 11:00 | SK  | 33A    |
       | leg | 0002 | LHR     | CPH     | 20JUL2019 | 12:00 | 13:00 | SK  | 33A    |

       Given trip 2 is assigned to crew member 1 in position AH

       When I show "crew" in window 1

       Then the rule "rules_qual_ccr.qln_ac_type_ok_all" shall fail on leg 1 on trip 1 on roster 1
       and rave "rules_qual_ccr.%qln_ac_types_failtext_leg%" shall be "OMA: Qual. AC-type: A2 [AL]" on leg 1 on trip 1 on roster 1
       and the rule "rules_qual_ccr.qln_ac_type_ok_all" shall fail on leg 1 on trip 2 on roster 1
       and rave "rules_qual_ccr.%qln_ac_types_failtext_leg%" shall be "OMA: Qual. AC-type: A2 [AL]" on leg 1 on trip 2 on roster 1


    @SCENARIO14 @planning
    Scenario: Check that A350 legs are illegal with expired AL qualification
       Given Rostering_CC

       Given crew member 1 has qualification "ACQUAL+AL" from 1APR2019 to 1JUL2019

       Given a trip with the following activities
       | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
       | leg | 0001 | CPH     | LHR     | 10JUL2019 | 10:00 | 11:00 | SK  | 35X    |
       | leg | 0002 | LHR     | CPH     | 10JUL2019 | 12:00 | 13:00 | SK  | 35X    |

       Given trip 1 is assigned to crew member 1 in position AH

       Given a trip with the following activities
       | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
       | leg | 0001 | CPH     | LHR     | 20JUL2019 | 10:00 | 11:00 | SK  | 33A    |
       | leg | 0002 | LHR     | CPH     | 20JUL2019 | 12:00 | 13:00 | SK  | 33A    |

       Given trip 2 is assigned to crew member 1 in position AH

       When I show "crew" in window 1

       Then the rule "rules_qual_ccr.qln_ac_type_ok_all" shall fail on leg 1 on trip 1 on roster 1
       and rave "rules_qual_ccr.%qln_ac_types_failtext_leg%" shall be "OMA: Qual: licence expired AL 01Jul2019" on leg 1 on trip 1 on roster 1
       and the rule "rules_qual_ccr.qln_ac_type_ok_all" shall fail on leg 1 on trip 2 on roster 1
       and rave "rules_qual_ccr.%qln_ac_types_failtext_leg%" shall be "OMA: Qual: licence expired AL 01Jul2019" on leg 1 on trip 2 on roster 1


    @SCENARIO15 @planning
    Scenario: Check that deadhead A350 legs are legal with no TW99 activity in training log or roster
       Given Rostering_CC

       Given crew member 1 has qualification "ACQUAL+AL" from 1APR2019 to 31DEC2035

       Given a trip with the following activities
       | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
       | dh  | 0001 | CPH     | LHR     | 10JUL2019 | 10:00 | 11:00 | SK  | 35X    |
       | leg | 0002 | LHR     | CPH     | 10JUL2019 | 12:00 | 13:00 | SK  | 35X    |

       Given trip 1 is assigned to crew member 1 in position AH

       When I show "crew" in window 1

       Then the rule "rules_qual_ccr.qln_ac_type_ok_all" shall pass on leg 1 on trip 1 on roster 1
       and the rule "rules_qual_ccr.qln_ac_type_ok_all" shall fail on leg 2 on trip 1 on roster 1
       and rave "rules_qual_ccr.%qln_ac_types_failtext_leg%" shall be "OMA: Qual. AC-type AL requires TW99 for A5 flight" on leg 2 on trip 1 on roster 1
