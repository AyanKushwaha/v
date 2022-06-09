@TRACKING @JCRT @FD @FC @LC @A2A5 @ACQUAL @TRAINING
Feature: Tests that rules for recurrent training works with line checks for crew with multiple aircraft qualifications.

##############################################################################
    Background: Set up common data
        Given Tracking
        Given planning period from 1FEB2019 to 1JUL2019

        Given a crew member with
        | attribute  | value  |
        | base       | OSL    |
        | title rank | FP     |
        | region     | SKN    |
        Given crew member 1 has document "REC+CRM" from 02JAN1986 to 01JAN2035
        Given crew member 1 has document "REC+PGT" from 02JAN1986 to 01JAN2035
        Given crew member 1 has document "REC+PCA5" from 02JAN1986 to 01JAN2035
        Given crew member 1 has document "REC+OPCA5" from 02JAN1986 to 01JAN2035
        Given crew member 1 has document "REC+PC" from 02JAN1986 to 01JAN2035 and has qualification "A2"
        Given crew member 1 has document "REC+OPC" from 02JAN1986 to 01JAN2035 and has qualification "A2"
        Given crew member 1 has contract "V134-LH"

##############################################################################

        @SCENARIO1
        Scenario: Verify that the LC document checks pass for A2A5 qualified crew.

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A2"
        Given crew member 1 has document "REC+LC" from 01JUN2015 to 01JUN2020 and has qualification "A5"
        Given crew member 1 has qualification "ACQUAL+A2" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 18MAY2017 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 320    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 35A    |
        | leg | 0003 | SFO     | CPH     | 20FEB2019 | 01:30 | 12:20 | SK  | 35A    |
        | leg | 0004 | CPH     | OSL     | 20FEB2019 | 13:20 | 14:30 | SK  | 32W    |

        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Jul19 (A2), May20 (A5)"

    @SCENARIO2
        Scenario: Verify that the LC document checks fail for A2A5 qualified crew with expired A2 LC document

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 01MAY2015 to 01FEB2019 and has qualification "A2"
        Given crew member 1 has qualification "ACQUAL+A5" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A2" from 15MAY2017 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 320    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 35A    |
        | leg | 0003 | SFO     | CPH     | 20FEB2019 | 01:30 | 12:20 | SK  | 35A    |
        | leg | 0004 | CPH     | OSL     | 20FEB2019 | 13:20 | 14:30 | SK  | 32W    |

        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall fail on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Jan19 (A2), Jul19 (A5)"

        @SCENARIO3
        Scenario: Verify that the LC document checks fail for A2A5 qualified crew with expired A5 LC document

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A2"
        Given crew member 1 has document "REC+LC" from 01MAY2015 to 01FEB2019 and has qualification "A5"
        Given crew member 1 has qualification "ACQUAL+A5" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A2" from 15MAY2017 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 320    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 35A    |
        | leg | 0003 | SFO     | CPH     | 20FEB2019 | 01:30 | 12:20 | SK  | 35A    |
        | leg | 0004 | CPH     | OSL     | 20FEB2019 | 13:20 | 14:30 | SK  | 32W    |

        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall fail on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Jul19 (A2), Jan19 (A5)"

        @SCENARIO4
        Scenario: Verify that the LC document checks fail for A2A5 qualified crew if LCA2 does not exist

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 01JAN2020 and has qualification "A5"
        Given crew member 1 has qualification "ACQUAL+A5" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A2" from 15MAY2017 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 320    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 35A    |
        | leg | 0003 | SFO     | CPH     | 20FEB2019 | 01:30 | 12:20 | SK  | 35A    |
        | leg | 0004 | CPH     | OSL     | 20FEB2019 | 13:20 | 14:30 | SK  | 32W    |

        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall fail on leg 1 on trip 1 on roster 1
        and rave "rules_qual_ccr.%qln_all_required_dates_registered_all_failtext%" shall be "OMA: Recurrent dates not registered LC (A2)"
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: - (A2), Dec19 (A5)"


        @SCENARIO5
        Scenario: Verify that the LC document checks fail for A2A5 qualified crew if LCA5 does not exist.

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 01JAN2020 and has qualification "A2"
        Given crew member 1 has qualification "ACQUAL+A5" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A2" from 15MAY2017 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 320    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 35A    |
        | leg | 0003 | SFO     | CPH     | 20FEB2019 | 01:30 | 12:20 | SK  | 35A    |
        | leg | 0004 | CPH     | OSL     | 20FEB2019 | 13:20 | 14:30 | SK  | 32W    |

        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall fail on leg 1 on trip 1 on roster 1
        and rave "rules_qual_ccr.%qln_all_required_dates_registered_all_failtext%" shall be "OMA: Recurrent dates not registered LC (A5)"
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Dec19 (A2), - (A5)"

        @SCENARIO6
        Scenario: Verify that the LC document checks fail for A2A5 qualified crew if LCA2 and LCA5 do not exist.

        Given crew member 1 has qualification "ACQUAL+A5" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A2" from 15MAY2017 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 320    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 35A    |
        | leg | 0003 | SFO     | CPH     | 20FEB2019 | 01:30 | 12:20 | SK  | 35A    |
        | leg | 0004 | CPH     | OSL     | 20FEB2019 | 13:20 | 14:30 | SK  | 32W    |

        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall fail on leg 1 on trip 1 on roster 1
        and rave "rules_qual_ccr.%qln_all_required_dates_registered_all_failtext%" shall be "OMA: Recurrent dates not registered LC (A5), LC (A2)"
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: - (A2), - (A5)"


        @SCENARIO7
        Scenario: Verify that the LC document checks fail for A2A5 qualified crew if LCA2 and LCA5 have expired.

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JAN2019 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 01JUN2015 to 01JUN2017 and has qualification "A2"
        Given crew member 1 has qualification "ACQUAL+A5" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A2" from 15MAY2017 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 320    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 35A    |
        | leg | 0003 | SFO     | CPH     | 20FEB2019 | 01:30 | 12:20 | SK  | 35A    |
        | leg | 0004 | CPH     | OSL     | 20FEB2019 | 13:20 | 14:30 | SK  | 32W    |

        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall fail on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: May17 (A2), Jan19 (A5)"

        @SCENARIO8
        Scenario: Verify that the LC document checks pass when LC training for A5 is in roster

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 01JUL2019 and has qualification "A2"
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08FEB2018 and has qualification "A5"
        Given crew member 1 has qualification "ACQUAL+A2" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 26JUL2017 to 31DEC2035

        Given another trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | SFO     | 03FEB2019 | 11:25 | 22:45 | SK  | 35B    |
        | leg | 0002 | SFO     | OSL     | 05FEB2019 | 01:30 | 12:20 | SK  | 35B    |
        Given trip 1 is assigned to crew member 1 in position 1 with attribute TRAINING="LC"

        Given another trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | SFO     | 10FEB2019 | 11:25 | 22:45 | SK  | 35B    |
        | leg | 0002 | SFO     | OSL     | 12FEB2019 | 01:30 | 12:20 | SK  | 35B    |
        Given trip 2 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 2 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 2 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Jun19 (A2), Feb18 (A5)"


        @SCENARIO9
        Scenario: Verify that the LC document checks pass when LC training for A2 is in roster

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08FEB2017 and has qualification "A2"
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08FEB2020 and has qualification "A5"
        Given crew member 1 has qualification "ACQUAL+A2" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 26JUL2017 to 31DEC2035

        Given another trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | SFO     | 03FEB2019 | 11:25 | 22:45 | SK  | 320    |
        | leg | 0002 | SFO     | OSL     | 05FEB2019 | 01:30 | 12:20 | SK  | 320    |
        Given trip 1 is assigned to crew member 1 in position 1 with attribute TRAINING="LC"

        Given another trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0003 | OSL     | ARN     | 23FEB2019 | 11:25 | 15:45 | SK  | 320    |
        | leg | 0004 | ARN     | OSL     | 25FEB2019 | 01:30 | 06:20 | SK  | 320    |
        Given trip 2 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 2 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 2 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Feb17 (A2), Feb20 (A5)"

        @SCENARIO10
        Scenario: Verify that the planned too early checks pass when LC training for A2 is in roster in correct time

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08FEB2019 and has qualification "A2"
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 01JUL2019 and has qualification "A5"
        Given crew member 1 has qualification "ACQUAL+A2" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 26JUL2017 to 31DEC2035

        Given another trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CDG     | 03FEB2019 | 21:25 | 22:45 | SK  | 320    |
        | leg | 0002 | CDG     | OSL     | 04FEB2019 | 07:30 | 08:50 | SK  | 320    |
        Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="LC"

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.lc_must_not_be_planned_too_early_fc" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all" shall pass on leg 1 on trip 1 on roster 1
        and rave "training_log.%leg_type%" shall be "LC" on leg 1 on trip 1 on roster 1
        and rave "training_log.%leg_code%" shall be "A2" on leg 1 on trip 1 on roster 1


        @SCENARIO11
        Scenario: Verify that the planned too early checks pass when LC training for A5 is in roster in correct time

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 01JUL2019 and has qualification "A2"
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08FEB2019 and has qualification "A5"
        Given crew member 1 has qualification "ACQUAL+A2" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 26JUL2017 to 31DEC2035

        Given another trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CDG     | 03FEB2019 | 21:25 | 22:45 | SK  | 35A    |
        | leg | 0002 | CDG     | OSL     | 04FEB2019 | 07:30 | 08:50 | SK  | 35A    |
        Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="LC"

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"

        Then the rule "rules_qual_ccr.lc_must_not_be_planned_too_early_fc" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all" shall pass on leg 1 on trip 1 on roster 1
        and rave "training_log.%leg_type%" shall be "LC" on leg 1 on trip 1 on roster 1
        and rave "training_log.%leg_code%" shall be "A5" on leg 1 on trip 1 on roster 1


        @SCENARIO12
        Scenario: Verify that the planned too early checks fail when LC training for A2 is in roster too early

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08JUN2018 and has qualification "A2"
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 01JUL2019 and has qualification "A5"
        Given crew member 1 has qualification "ACQUAL+A2" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 26JUL2017 to 31DEC2035

        Given another trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CDG     | 03FEB2019 | 21:25 | 22:45 | SK  | 320    |
        | leg | 0002 | CDG     | OSL     | 04FEB2019 | 07:30 | 08:50 | SK  | 320    |
        Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="LC"

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.lc_must_not_be_planned_too_early_fc" shall fail on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all" shall pass on leg 1 on trip 1 on roster 1
        and rave "training_log.%leg_type%" shall be "LC" on leg 1 on trip 1 on roster 1
        and rave "training_log.%leg_code%" shall be "A2" on leg 1 on trip 1 on roster 1


        @SCENARIO13
        Scenario: Verify that the LC document checks pass when LC training for A5 is in training log

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 01JUL2019 and has qualification "A2"
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08FEB2018 and has qualification "A5"
        Given crew member 1 has qualification "ACQUAL+A2" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 26JUL2017 to 31DEC2035

        Given table crew_training_log additionally contains the following
        | crew          | typ | code | tim             | attr |
        | crew member 1 | LC  | A5   | 24JAN2019 10:00 |      |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | SFO     | 10FEB2019 | 11:25 | 22:45 | SK  | 35B    |
        | leg | 0002 | SFO     | OSL     | 12FEB2019 | 01:30 | 12:20 | SK  | 35B    |
        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "29JAN2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Jun19 (A2), Feb18 (A5)"

        @SCENARIO14
        Scenario: Verify that the LC document checks pass when LC training for A2 is in training log

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08FEB2018 and has qualification "A2"
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 01JUL2019 and has qualification "A5"
        Given crew member 1 has qualification "ACQUAL+A2" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 26JUL2017 to 31DEC2035

        Given table crew_training_log additionally contains the following
        | crew          | typ | code | tim             | attr |
        | crew member 1 | LC  | A2   | 24JAN2019 10:00 |      |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | SFO     | 10FEB2019 | 11:25 | 22:45 | SK  | 35B    |
        | leg | 0002 | SFO     | OSL     | 12FEB2019 | 01:30 | 12:20 | SK  | 35B    |
        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "29JAN2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Feb18 (A2), Jun19 (A5)"


        @SCENARIO15
        Scenario: Verify that the LC document checks fail when LC training for A5 is in training log but A2 LC document is expired

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08FEB2018 and has qualification "A2"
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 01JUL2019 and has qualification "A5"
        Given crew member 1 has qualification "ACQUAL+A2" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 26JUL2017 to 31DEC2035

        Given table crew_training_log additionally contains the following
        | crew          | typ | code | tim             | attr |
        | crew member 1 | LC  | A5   | 24JAN2019 10:00 |      |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | SFO     | 10FEB2019 | 11:25 | 22:45 | SK  | 320    |
        | leg | 0002 | SFO     | OSL     | 12FEB2019 | 01:30 | 12:20 | SK  | 320    |
        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "29JAN2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall fail on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Feb18 (A2), Jun19 (A5)"


        @SCENARIO16
        Scenario: Verify that the LC document checks fail when LC training for A2 is in training log but A5 LC document is expired

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 01JUL2019 and has qualification "A2"
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08FEB2018 and has qualification "A5"
        Given crew member 1 has qualification "ACQUAL+A2" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 26JUL2017 to 31DEC2035

        Given table crew_training_log additionally contains the following
        | crew          | typ | code | tim             | attr |
        | crew member 1 | LC  | A2   | 24JAN2019 10:00 |      |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | SFO     | 10FEB2019 | 11:25 | 22:45 | SK  | 35A    |
        | leg | 0002 | SFO     | OSL     | 12FEB2019 | 01:30 | 12:20 | SK  | 35A    |
        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "29JAN2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall fail on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Jun19 (A2), Feb18 (A5)"









