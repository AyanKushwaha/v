@TRACKING @JCRT @FD @FC @LC @A2A3 @ACQUAL @TRAINING
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
        Given crew member 1 has document "REC+LPCA3" from 02JAN1986 to 01JAN2035
        Given crew member 1 has document "REC+OPCA3" from 02JAN1986 to 01JAN2035
        Given crew member 1 has document "REC+LPC" from 02JAN1986 to 01JAN2035 and has qualification "A2"
        Given crew member 1 has document "REC+OPC" from 02JAN1986 to 01JAN2035 and has qualification "A2"
        Given crew member 1 has contract "V134-LH"

##############################################################################

        @SCENARIO1
        Scenario: Verify that the LC document checks pass for A2A3 qualified crew.

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A2"
        Given crew member 1 has document "REC+LC" from 01JUN2015 to 01JUN2020 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A2" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A3" from 18MAY2017 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 320    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 33A    |
        | leg | 0003 | SFO     | CPH     | 20FEB2019 | 01:30 | 12:20 | SK  | 33A    |
        | leg | 0004 | CPH     | OSL     | 20FEB2019 | 13:20 | 14:30 | SK  | 32W    |

        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Jul19 (A2), May20 (A3)"


        @SCENARIO2
        Scenario: Verify that the LC document checks fail for A2A3 qualified crew with expired A2 LC document

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 01MAY2015 to 01FEB2019 and has qualification "A2"
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A2" from 15MAY2017 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 320    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 33A    |
        | leg | 0003 | SFO     | CPH     | 20FEB2019 | 01:30 | 12:20 | SK  | 33A    |
        | leg | 0004 | CPH     | OSL     | 20FEB2019 | 13:20 | 14:30 | SK  | 32W    |

        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall fail on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Jan19 (A2), Jul19 (A3)"


        @SCENARIO3
        Scenario: Verify that the LC document checks fail for A2A3 qualified crew with expired A3 LC document

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A2"
        Given crew member 1 has document "REC+LC" from 01MAY2015 to 01FEB2019 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A2" from 15MAY2017 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 320    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 33A    |
        | leg | 0003 | SFO     | CPH     | 20FEB2019 | 01:30 | 12:20 | SK  | 33A    |
        | leg | 0004 | CPH     | OSL     | 20FEB2019 | 13:20 | 14:30 | SK  | 32W    |

        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall fail on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Jul19 (A2), Jan19 (A3)"


        @SCENARIO4
        Scenario: Verify that the LC document checks fail for A2A3 qualified crew if LCA2 does not exist

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 01JAN2020 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A2" from 15MAY2017 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 320    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 33A    |
        | leg | 0003 | SFO     | CPH     | 20FEB2019 | 01:30 | 12:20 | SK  | 33A    |
        | leg | 0004 | CPH     | OSL     | 20FEB2019 | 13:20 | 14:30 | SK  | 32W    |

        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall fail on leg 1 on trip 1 on roster 1
        and rave "rules_qual_ccr.%qln_all_required_dates_registered_all_failtext%" shall be "OMA: Recurrent dates not registered LC (A2)"
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: - (A2), Dec19 (A3)"


        @SCENARIO5
        Scenario: Verify that the LC document checks fail for A2A3 qualified crew if LCA3 does not exist.

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 01JAN2020 and has qualification "A2"
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A2" from 15MAY2017 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 320    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 33A    |
        | leg | 0003 | SFO     | CPH     | 20FEB2019 | 01:30 | 12:20 | SK  | 33A    |
        | leg | 0004 | CPH     | OSL     | 20FEB2019 | 13:20 | 14:30 | SK  | 32W    |

        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall fail on leg 1 on trip 1 on roster 1
        and rave "rules_qual_ccr.%qln_all_required_dates_registered_all_failtext%" shall be "OMA: Recurrent dates not registered LC (A3)"
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Dec19 (A2), - (A3)"


        @SCENARIO6
        Scenario: Verify that the LC document checks fail for A2A3 qualified crew if LCA2 and LCA3 do not exist.

        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A2" from 15MAY2017 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 320    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 33A    |
        | leg | 0003 | SFO     | CPH     | 20FEB2019 | 01:30 | 12:20 | SK  | 33A    |
        | leg | 0004 | CPH     | OSL     | 20FEB2019 | 13:20 | 14:30 | SK  | 32W    |

        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall fail on leg 1 on trip 1 on roster 1
        and rave "rules_qual_ccr.%qln_all_required_dates_registered_all_failtext%" shall be "OMA: Recurrent dates not registered LC (A3), LC (A2)"
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: - (A2), - (A3)"


        @SCENARIO7
        Scenario: Verify that the LC document checks fail for A2A3 qualified crew if LCA2 and LCA3 have expired.

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JAN2019 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 01JUN2015 to 01JUN2017 and has qualification "A2"
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A2" from 15MAY2017 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 320    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 33A    |
        | leg | 0003 | SFO     | CPH     | 20FEB2019 | 01:30 | 12:20 | SK  | 33A    |
        | leg | 0004 | CPH     | OSL     | 20FEB2019 | 13:20 | 14:30 | SK  | 32W    |

        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall fail on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: May17 (A2), Jan19 (A3)"


        @SCENARIO8
        Scenario: Verify that the LC document checks pass when LC training for A3 is in roster

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 01JUL2019 and has qualification "A2"
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08FEB2018 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A2" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035

        Given another trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | SFO     | 03FEB2019 | 11:25 | 22:45 | SK  | 33B    |
        | leg | 0002 | SFO     | OSL     | 05FEB2019 | 01:30 | 12:20 | SK  | 33B    |
        Given trip 1 is assigned to crew member 1 in position 1 with attribute TRAINING="LC"

        Given another trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | SFO     | 10FEB2019 | 11:25 | 22:45 | SK  | 33B    |
        | leg | 0002 | SFO     | OSL     | 12FEB2019 | 01:30 | 12:20 | SK  | 33B    |
        Given trip 2 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 2 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 2 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Jun19 (A2), Feb18 (A3)"


        @SCENARIO9
        Scenario: Verify that the LC document checks pass when LC training for A2 is in roster

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08FEB2017 and has qualification "A2"
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08FEB2020 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A2" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035

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
        and rave "crg_info.%lc_str%" shall be " LC: Feb17 (A2), Feb20 (A3)"


        @SCENARIO10
        Scenario: Verify that the planned too early checks pass when LC training for A2 is in roster in correct time

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08FEB2019 and has qualification "A2"
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 01JUL2019 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A2" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035

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
        Scenario: Verify that the planned too early checks pass when LC training for A3 is in roster in correct time

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 01JUL2019 and has qualification "A2"
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08FEB2019 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A2" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035

        Given another trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CDG     | 03FEB2019 | 21:25 | 22:45 | SK  | 33B    |
        | leg | 0002 | CDG     | OSL     | 04FEB2019 | 07:30 | 08:50 | SK  | 33B    |
        Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="LC"

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"

        Then the rule "rules_qual_ccr.lc_must_not_be_planned_too_early_fc" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all" shall pass on leg 1 on trip 1 on roster 1
        and rave "training_log.%leg_type%" shall be "LC" on leg 1 on trip 1 on roster 1
        and rave "training_log.%leg_code%" shall be "A3" on leg 1 on trip 1 on roster 1


        @SCENARIO12
        Scenario: Verify that the planned too early checks fail when LC training for A2 is in roster too early

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08JUN2019 and has qualification "A2"
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 01JUL2019 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A2" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035

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
        Scenario: Verify that the LC document checks pass when LC training for A3 is in training log

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 01JUL2019 and has qualification "A2"
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08FEB2018 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A2" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035

        Given table crew_training_log additionally contains the following
        | crew          | typ | code | tim             | attr |
        | crew member 1 | LC  | A3   | 24JAN2019 10:00 |      |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | SFO     | 10FEB2019 | 11:25 | 22:45 | SK  | 33B    |
        | leg | 0002 | SFO     | OSL     | 12FEB2019 | 01:30 | 12:20 | SK  | 33B    |
        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "29JAN2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Jun19 (A2), Feb18 (A3)"


        @SCENARIO14
        Scenario: Verify that the LC document checks pass when LC training for A2 is in training log

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08FEB2018 and has qualification "A2"
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 01JUL2019 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A2" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035

        Given table crew_training_log additionally contains the following
        | crew          | typ | code | tim             | attr |
        | crew member 1 | LC  | A2   | 24JAN2019 10:00 |      |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | SFO     | 10FEB2019 | 11:25 | 22:45 | SK  | 33B    |
        | leg | 0002 | SFO     | OSL     | 12FEB2019 | 01:30 | 12:20 | SK  | 33B    |
        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "29JAN2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Feb18 (A2), Jun19 (A3)"


        @SCENARIO15
        Scenario: Verify that the LC document checks fail when LC training for A3 is in training log but A2 LC document is expired

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08FEB2018 and has qualification "A2"
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 01JUL2019 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A2" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035

        Given table crew_training_log additionally contains the following
        | crew          | typ | code | tim             | attr |
        | crew member 1 | LC  | A3   | 24JAN2019 10:00 |      |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | SFO     | 10FEB2019 | 11:25 | 22:45 | SK  | 32B    |
        | leg | 0002 | SFO     | OSL     | 12FEB2019 | 01:30 | 12:20 | SK  | 32B    |
        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "29JAN2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall fail on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Feb18 (A2), Jun19 (A3)"


        @SCENARIO16
        Scenario: Verify that the LC document checks fail when LC training for A2 is in training log but A3 LC document is expired

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 01JUL2019 and has qualification "A2"
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08FEB2018 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A2" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035

        Given table crew_training_log additionally contains the following
        | crew          | typ | code | tim             | attr |
        | crew member 1 | LC  | A2   | 24JAN2019 10:00 |      |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | SFO     | 10FEB2019 | 11:25 | 22:45 | SK  | 33B    |
        | leg | 0002 | SFO     | OSL     | 12FEB2019 | 01:30 | 12:20 | SK  | 33B    |
        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "29JAN2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall fail on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Jun19 (A2), Feb18 (A3)"
