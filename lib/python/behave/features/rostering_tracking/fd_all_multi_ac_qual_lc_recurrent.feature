@TRACKING @JCRT @FD @FC @LC @A3A4 @ACQUAL @TRAINING
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
        Given crew member 1 has document "REC+LPCA3A5" from 02JAN1986 to 01JAN2035
        Given crew member 1 has document "REC+OPCA3A5" from 02JAN1986 to 01JAN2035
        Given crew member 1 has document "REC+LPCA4" from 02JAN1986 to 01JAN2035
        Given crew member 1 has document "REC+OPCA4" from 02JAN1986 to 01JAN2035
        Given crew member 1 has contract "V134-LH"

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 320    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 35B    |
        | leg | 0003 | SFO     | CPH     | 20FEB2019 | 01:30 | 12:20 | SK  | 35B    |
        | leg | 0004 | CPH     | OSL     | 20FEB2019 | 13:20 | 14:30 | SK  | 32W    |
##############################################################################

        @FD_LC_DOC_1
        Scenario: Verify that the LC document checks pass for A3A4A5 qualified crew.

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 01JUN2015 to 01JUN2018 and has qualification "A4"
        Given crew member 1 has document "REC+LC" from 01MAY2015 to 01MAY2020 and has qualification "A5"
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 18MAY2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 15MAY2017 to 31DEC2035
        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Apr20 A3 or A4"


        @FD_LC_DOC_2
        Scenario: Verify that the LC document checks pass for A3A5 qualified crew.

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 01MAY2015 to 01MAY2020 and has qualification "A5"
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 15MAY2017 to 31DEC2035
        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Apr20 A3"


        @FD_LC_DOC_3
        Scenario: Verify that the LC document checks pass for A3A4A5 qualified crew that lost their A4 qual.

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 01JUN2015 to 01JUN2018 and has qualification "A4"
        Given crew member 1 has document "REC+LC" from 01MAY2015 to 01MAY2020 and has qualification "A5"
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 15MAY2017 to 31DEC2035
        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Apr20 A3"


        @FD_LC_DOC_4
        Scenario: Verify that the LC document checks pass for A3A4A5 qualified crew before A5 ILC

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 01JUN2015 to 01JUN2018 and has qualification "A4"
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 15MAY2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 15MAY2017 to 31DEC2035
        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Jul19 A4"


        @FD_LC_DOC_5
        Scenario: Verify that the LC document checks pass for A3A5 qualified crew before A5 ILC

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 15MAY2017 to 31DEC2035
        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Jul19 A3"


        @FD_LC_DOC_6
        Scenario: Verify that the LC document checks fail for A3A5 qualified crew before A5 ILC if LCA3 has expired.

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 01JAN2019 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 15MAY2017 to 31DEC2035
        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall fail on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Dec18 A3"


        @FD_LC_DOC_7
        Scenario: Verify that the LC document checks fail for A3A4A5 qualified crew before A5 ILC if LCA3 and LCA4 has expired.

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JAN2019 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 01JUN2015 to 01JUN2017 and has qualification "A4"
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 15MAY2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 15MAY2017 to 31DEC2035
        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall fail on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Jan19 A4"


        @FD_LC_DOC_8
        Scenario: Verify that the LC document checks pass for multi qualified crew if alternating LC (A3 or A4) has A3 in roster.

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 28FEB2019 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08FEB2017 and has qualification "A4"
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08FEB2018 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 15MAY2017 to 31DEC2035

        Given another trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | CPH     | SFO     | 03FEB2019 | 11:25 | 22:45 | SK  | 33B    |
        | leg | 0002 | SFO     | CPH     | 05FEB2019 | 01:30 | 12:20 | SK  | 35B    |
        | leg | 0003 | CPH     | ARN     | 23FEB2019 | 11:25 | 15:45 | SK  | 35B    |
        | leg | 0004 | ARN     | CPH     | 25FEB2019 | 01:30 | 06:20 | SK  | 33B    |
        Given trip 2 is assigned to crew member 1 in position 1 with attribute TRAINING="LC"

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 3 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 3 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Feb19 A3 or A4"


        @FD_LC_DOC_9
        Scenario: Verify that the LC document checks pass for multi qualified crew if alternating LC (A3 or A4) has A4 in roster.

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 28FEB2019 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08FEB2017 and has qualification "A4"
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 08FEB2018 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 15MAY2017 to 31DEC2035

        Given another trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | CPH     | SFO     | 03FEB2019 | 11:25 | 22:45 | SK  | 34B    |
        | leg | 0002 | SFO     | CPH     | 05FEB2019 | 01:30 | 12:20 | SK  | 35B    |
        | leg | 0003 | CPH     | ARN     | 23FEB2019 | 11:25 | 15:45 | SK  | 35B    |
        | leg | 0004 | ARN     | CPH     | 25FEB2019 | 01:30 | 06:20 | SK  | 34B    |
        Given trip 2 is assigned to crew member 1 in position 1 with attribute TRAINING="LC"

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 3 on trip 1 on roster 1
        and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 3 on trip 1 on roster 1
        and rave "crg_info.%lc_str%" shall be " LC: Feb19 A3 or A4"
