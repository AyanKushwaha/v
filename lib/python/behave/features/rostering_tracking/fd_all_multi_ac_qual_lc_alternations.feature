@TRACKING @JCRT @FD @FC @LC @A3A4 @ACQUAL @TRAINING
Feature: Tests that line checks for crew with multiple aircraft qualifications alternate as needed.

##############################################################################
    Background: Set up for Tracking with common data
        Given Tracking
        Given planning period from 1FEB2019 to 1JUL2019

        Given a crew member with
        | attribute  | value  |
        | base       | OSL    |
        | title rank | FP     |
        | region     | SKN    |
        Given crew member 1 has contract "V134-LH"
##############################################################################

        @FD_LC_ALT_1
        Scenario: Double qualified LH pilot (A3A4) LC should alternate to A4 after A3

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 01JUN2015 to 01JUN2018 and has qualification "A4"
        Given crew member 1 has qualification "ACQUAL+A3" from 13APR2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 01FEB2011 to 31DEC2035

        When I show "crew" in window 1
        Then rave "crew.%expiry_doc_alternating_ac_qual%("REC","LC",crew.%any_ac_qual%,01FEB2019)" shall be "A4" on leg 1 on trip 1 on roster 1


        @FD_LC_ALT_2
        Scenario: Double qualified LH pilot (A3A4) LC should alternate to A3 after A4

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A4"
        Given crew member 1 has document "REC+LC" from 01JUN2015 to 01JUN2018 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A3" from 01FEB2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 13APR2011 to 31DEC2035

        When I show "crew" in window 1
        Then rave "crew.%expiry_doc_alternating_ac_qual%("REC","LC",crew.%any_ac_qual%,01FEB2019)" shall be "A3" on leg 1 on trip 1 on roster 1


        @FD_LC_ALT_3
        Scenario: Double qualified LH pilot (A3A5) LC should alternate to A3 after A5

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 01JUN2015 to 01JUN2018 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A3" from 01FEB2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 13APR2011 to 31DEC2035

        When I show "crew" in window 1
        Then rave "crew.%expiry_doc_alternating_ac_qual%("REC","LC",crew.%any_ac_qual%,01FEB2019)" shall be "A3" on leg 1 on trip 1 on roster 1


        @FD_LC_ALT_4
        Scenario: Double qualified LH pilot (A3A5) LC should alternate to A5 after A3

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 01JUN2015 to 01JUN2018 and has qualification "A5"
        Given crew member 1 has qualification "ACQUAL+A3" from 01FEB2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 13APR2011 to 31DEC2035

        When I show "crew" in window 1
        Then rave "crew.%expiry_doc_alternating_ac_qual%("REC","LC",crew.%any_ac_qual%,01FEB2019)" shall be "A5" on leg 1 on trip 1 on roster 1


        @FD_LC_ALT_5
        Scenario: Triple qualified LH pilot (A3A4A5) LC should alternate to A5 after A3

        Given crew member 1 has document "REC+LC" from 30JUL2018 to 31JUL2019 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 30JAN2018 to 31JAN2018 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 30JUL2017 to 31JUL2017 and has qualification "A4"
        Given crew member 1 has qualification "ACQUAL+A3" from 01FEB2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 13APR2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 13APR2011 to 31DEC2035

        When I show "crew" in window 1
        Then rave "crew.%expiry_doc_alternating_ac_qual%("REC","LC",crew.%any_ac_qual%,01FEB2019)" shall be "A5" on leg 1 on trip 1 on roster 1


        @FD_LC_ALT_6
        Scenario: Triple qualified LH pilot (A3A4A5) LC should alternate to A5 after A4

        Given crew member 1 has document "REC+LC" from 30JUL2018 to 31JUL2019 and has qualification "A4"
        Given crew member 1 has document "REC+LC" from 30JAN2018 to 31JAN2018 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 30JUL2017 to 31JUL2017 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A3" from 01FEB2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 13APR2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 13APR2011 to 31DEC2035

        When I show "crew" in window 1
        Then rave "crew.%expiry_doc_alternating_ac_qual%("REC","LC",crew.%any_ac_qual%,01FEB2019)" shall be "A5" on leg 1 on trip 1 on roster 1


        @FD_LC_ALT_7
        Scenario: Triple qualified LH pilot (A3A4A5) LC should alternate to A3 or A4 after A5 with previous A4

        Given crew member 1 has document "REC+LC" from 30JUL2018 to 31JUL2019 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 30JAN2018 to 31JAN2018 and has qualification "A4"
        Given crew member 1 has document "REC+LC" from 30JUL2017 to 31JUL2017 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A3" from 01FEB2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 13APR2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 13APR2011 to 31DEC2035

        When I show "crew" in window 1
        Then rave "crew.%expiry_doc_alternating_ac_qual%("REC","LC",crew.%any_ac_qual%,01FEB2019)" shall be "A3 or A4" on leg 1 on trip 1 on roster 1


        @FD_LC_ALT_8
        Scenario: Triple qualified LH pilot (A3A4A5) LC should alternate to A3 or A4 after A5 with previous A3

        Given crew member 1 has document "REC+LC" from 30JUL2018 to 31JUL2019 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 30JAN2018 to 31JAN2018 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 30JUL2017 to 31JUL2017 and has qualification "A4"
        Given crew member 1 has qualification "ACQUAL+A3" from 01FEB2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 13APR2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 13APR2011 to 31DEC2035

        When I show "crew" in window 1
        Then rave "crew.%expiry_doc_alternating_ac_qual%("REC","LC",crew.%any_ac_qual%,01FEB2019)" shall be "A3 or A4" on leg 1 on trip 1 on roster 1


        @FD_LC_ALT_9
        Scenario: Double qualified LH pilot (A3A4) LC should alternate to fall back to A3 if losing A4 qual

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 01JUN2015 to 01JUN2018 and has qualification "A4"
        Given crew member 1 has qualification "ACQUAL+A3" from 13APR2011 to 31DEC2035

        When I show "crew" in window 1
        Then rave "crew.%expiry_doc_alternating_ac_qual%("REC","LC",crew.%any_ac_qual%,01FEB2019)" shall be "A3" on leg 1 on trip 1 on roster 1

        @FD_LC_ALT_10
        Scenario: Double qualified LH pilot (A3A4) LC should alternate to fall back to A4 if losing A3 qual

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A4"
        Given crew member 1 has document "REC+LC" from 01JUN2015 to 01JUN2018 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A4" from 13APR2011 to 31DEC2035

        When I show "crew" in window 1
        Then rave "crew.%expiry_doc_alternating_ac_qual%("REC","LC",crew.%any_ac_qual%,01FEB2019)" shall be "A4" on leg 1 on trip 1 on roster 1


        @FD_LC_ALT_11
        Scenario: Double qualified LH pilot (A3A5) LC should alternate to fall back to A3 if losing A5 qual

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 01JUN2015 to 01JUN2018 and has qualification "A5"
        Given crew member 1 has qualification "ACQUAL+A3" from 13APR2011 to 31DEC2035

        When I show "crew" in window 1
        Then rave "crew.%expiry_doc_alternating_ac_qual%("REC","LC",crew.%any_ac_qual%,01FEB2019)" shall be "A3" on leg 1 on trip 1 on roster 1

        @FD_LC_ALT_12
        Scenario: Double qualified LH pilot (A3A5) LC should alternate to fall back to A5 if losing A3 qual

        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 01JUN2015 to 01JUN2018 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A5" from 13APR2011 to 31DEC2035

        When I show "crew" in window 1
        Then rave "crew.%expiry_doc_alternating_ac_qual%("REC","LC",crew.%any_ac_qual%,01FEB2019)" shall be "A5" on leg 1 on trip 1 on roster 1


        @FD_LC_ALT_13
        Scenario: Triple qualified LH pilot (A3A4A5) LC should alternate to A3 after A5 if losing A4 qual

        Given crew member 1 has document "REC+LC" from 30JUL2018 to 31JUL2019 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 30JAN2018 to 31JAN2018 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 30JUL2017 to 31JUL2017 and has qualification "A4"
        Given crew member 1 has qualification "ACQUAL+A3" from 01FEB2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 13APR2011 to 31DEC2035

        When I show "crew" in window 1
        Then rave "crew.%expiry_doc_alternating_ac_qual%("REC","LC",crew.%any_ac_qual%,01FEB2019)" shall be "A3" on leg 1 on trip 1 on roster 1


        @FD_LC_ALT_14
        Scenario: Triple qualified LH pilot (A3A4A5) LC should alternate to A3 after A4 if losing A5 qual

        Given crew member 1 has document "REC+LC" from 30JUL2018 to 31JUL2019 and has qualification "A4"
        Given crew member 1 has document "REC+LC" from 30JAN2018 to 31JAN2018 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 30JUL2017 to 31JUL2017 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A3" from 01FEB2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 13APR2011 to 31DEC2035

        When I show "crew" in window 1
        Then rave "crew.%expiry_doc_alternating_ac_qual%("REC","LC",crew.%any_ac_qual%,01FEB2019)" shall be "A3" on leg 1 on trip 1 on roster 1


        @FD_LC_ALT_15
        Scenario: Triple qualified LH pilot (A3A4A5) LC should alternate to A4 after A3 if losing A5 qual

        Given crew member 1 has document "REC+LC" from 30JUL2018 to 31JUL2019 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 30JAN2018 to 31JAN2018 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 30JUL2017 to 31JUL2017 and has qualification "A4"
        Given crew member 1 has qualification "ACQUAL+A3" from 01FEB2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 13APR2011 to 31DEC2035

        When I show "crew" in window 1
        Then rave "crew.%expiry_doc_alternating_ac_qual%("REC","LC",crew.%any_ac_qual%,01FEB2019)" shall be "A4" on leg 1 on trip 1 on roster 1

        # A4A5 should not exist, so no tests or rave support for that, add here if needed in the future.


####### Additional tests to verify change regarding A3 or A4 for triple qual across the system #######

        @FD_LC_ALT_A3A4_1
        Scenario: Triple qualified LH pilot (A3A4A5) should report A3 or A4 after A5 in various places and handle operations based on that value properly

        Given crew member 1 has document "REC+LC" from 30JUL2018 to 31JUL2019 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 30JAN2018 to 31JAN2018 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 30JUL2017 to 31JUL2017 and has qualification "A4"
        Given crew member 1 has qualification "ACQUAL+A3" from 01FEB2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 13APR2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 13APR2011 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 33B    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 34B    |
        | leg | 0003 | SFO     | OSL     | 20FEB2019 | 01:30 | 12:20 | SK  | 35B    |
        Given trip 1 is assigned to crew member 1 in position 1 with attribute TRAINING="LC"

        When I show "crew" in window 1
        Then rave "crg_info.%lc_str%" shall be " LC: Jul19 A3 or A4" on leg 1 on trip 1 on roster 1
        and rave "training.%expiry_month_lc%" shall be "Jul19" on leg 1 on trip 1 on roster 1
        and rave "training.%recurrent_type_expiry_date%("LC",training.%any_ac_qual%,01FEB2019)" shall be "31JUL2019 00:00" on leg 1 on trip 1 on roster 1
        and rave "training.%_recurrent_type_registered%("LC",training.%any_ac_qual%,01FEB2019)" shall be "True" on leg 1 on trip 1 on roster 1
        and rave "rules_qual_ccr.%next_expiring_multi_qual_is_not_leg_qual%" shall be "False" on leg 1 on trip 1 on roster 1
        and rave "rules_qual_ccr.%next_expiring_multi_qual_is_not_leg_qual%" shall be "False" on leg 2 on trip 1 on roster 1
        and rave "rules_qual_ccr.%next_expiring_multi_qual_is_not_leg_qual%" shall be "True" on leg 3 on trip 1 on roster 1


        @FD_LC_ALT_A3A4_2
        Scenario: Triple qualified LH pilot (A3A4A5) has LC document that expires in planning period inside warning window, should warn

        Given crew member 1 has document "REC+LC" from 30JUL2018 to 28FEB2019 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 30JAN2018 to 31JAN2018 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 30JUL2017 to 31JUL2017 and has qualification "A4"
        Given crew member 1 has qualification "ACQUAL+A3" from 01FEB2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 13APR2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 13APR2011 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 33B    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 34B    |
        | leg | 0003 | SFO     | OSL     | 20FEB2019 | 01:30 | 12:20 | SK  | 35B    |
        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        Then rave "crew_warnings.%crew_lc_expires_in_pp%" shall be "True" on leg 1 on trip 1 on roster 1


        @FD_LC_ALT_A3A4_3
        Scenario: Triple qualified LH pilot (A3A4A5) has LC document that expires in planning period outside warning window, should not warn

        Given crew member 1 has document "REC+LC" from 30JUL2018 to 30APR2019 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 30JAN2018 to 31JAN2018 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 30JUL2017 to 31JUL2017 and has qualification "A4"
        Given crew member 1 has qualification "ACQUAL+A3" from 01FEB2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 13APR2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 13APR2011 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 33B    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 34B    |
        | leg | 0003 | SFO     | OSL     | 20FEB2019 | 01:30 | 12:20 | SK  | 35B    |
        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        Then rave "crew_warnings.%crew_lc_expires_in_pp%" shall be "False" on leg 1 on trip 1 on roster 1


        @FD_LC_ALT_A3A4_4
        Scenario: Triple qualified LH pilot (A3A4A5) has LC document that does not expire in planning period, should not warn

        Given crew member 1 has document "REC+LC" from 30JUL2018 to 31JUL2019 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 30JAN2018 to 31JAN2018 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 30JUL2017 to 31JUL2017 and has qualification "A4"
        Given crew member 1 has qualification "ACQUAL+A3" from 01FEB2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 13APR2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 13APR2011 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 33B    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 34B    |
        | leg | 0003 | SFO     | OSL     | 20FEB2019 | 01:30 | 12:20 | SK  | 35B    |
        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        Then rave "crew_warnings.%crew_lc_expires_in_pp%" shall be "False" on leg 1 on trip 1 on roster 1


        @FD_LC_ALT_A3A4_5
        Scenario: Triple qualified LH pilot (A3A4A5) has upcoming LC A3 or A4, performs LC A3 in planning period, should report properly before and after

        Given crew member 1 has document "REC+LC" from 30JUL2018 to 31JUL2019 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 30JAN2018 to 31JAN2018 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 30JUL2017 to 31JUL2017 and has qualification "A4"
        Given crew member 1 has qualification "ACQUAL+A3" from 01FEB2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 13APR2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 13APR2011 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 33B    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 33B    |
        | leg | 0003 | SFO     | OSL     | 20FEB2019 | 01:30 | 12:20 | SK  | 35B    |
        Given trip 1 is assigned to crew member 1 in position 1 with attribute TRAINING="LC"

        When I show "crew" in window 1
        Then rave "training.%recurrent_flight_training_performed%("LC", training.%any_ac_qual%, 01FEB2019)" shall be "False" on leg 1 on trip 1 on roster 1
        and rave "training.%recurrent_flight_training_performed%("LC", training.%any_ac_qual%, 28FEB2019)" shall be "True" on leg 1 on trip 1 on roster 1


        @FD_LC_ALT_A3A4_6
        Scenario: Triple qualified LH pilot (A3A4A5) has upcoming LC A3 or A4, performs LC A4 in planning period, should report properly before and after

        Given crew member 1 has document "REC+LC" from 30JUL2018 to 31JUL2019 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 30JAN2018 to 31JAN2018 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 30JUL2017 to 31JUL2017 and has qualification "A4"
        Given crew member 1 has qualification "ACQUAL+A3" from 01FEB2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 13APR2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 13APR2011 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 34B    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 34B    |
        | leg | 0003 | SFO     | OSL     | 20FEB2019 | 01:30 | 12:20 | SK  | 35B    |
        Given trip 1 is assigned to crew member 1 in position 1 with attribute TRAINING="LC"

        When I show "crew" in window 1
        Then rave "training.%recurrent_flight_training_performed%("LC", training.%any_ac_qual%, 01FEB2019)" shall be "False" on leg 1 on trip 1 on roster 1
        and rave "training.%recurrent_flight_training_performed%("LC", training.%any_ac_qual%, 28FEB2019)" shall be "True" on leg 1 on trip 1 on roster 1


        @FD_LC_ALT_A3A4_7
        Scenario: Single qualified LH pilot (A3) has upcoming LC A3, performs LC A3 in planning period, should work as it did before multi qual changes

        Given crew member 1 has document "REC+LC" from 30JUL2018 to 31JUL2019 and has qualification "A3"
        Given crew member 1 has qualification "ACQUAL+A3" from 01FEB2011 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 33B    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 33B    |
        Given trip 1 is assigned to crew member 1 in position 1 with attribute TRAINING="LC"

        When I show "crew" in window 1
        Then rave "training.%recurrent_flight_training_performed%("LC", training.%any_ac_qual%, 01FEB2019)" shall be "False" on leg 1 on trip 1 on roster 1
        and rave "training.%recurrent_flight_training_performed%("LC", training.%any_ac_qual%, 28FEB2019)" shall be "True" on leg 1 on trip 1 on roster 1


        @FD_LC_ALT_A3A4_8
        Scenario: Triple qualified LH pilot (A3A4A5) has LC document that expires in planning period with planned LC, must and may have filters should work as expected with upcoming A3 or A4 LC

        Given crew member 1 has document "REC+LC" from 30JUL2018 to 30APR2019 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 30JAN2018 to 31JAN2018 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 30JUL2017 to 31JUL2017 and has qualification "A4"
        Given crew member 1 has qualification "ACQUAL+A3" from 01FEB2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 13APR2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 13APR2011 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 34B    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 34B    |
        | leg | 0003 | SFO     | OSL     | 20FEB2019 | 01:30 | 12:20 | SK  | 35B    |
        Given trip 1 is assigned to crew member 1 in position 1 with attribute TRAINING="LC"

        When I show "crew" in window 1
        Then rave "training.%must_have_in_period%("LC", "A3", 01FEB2019, 15FEB2019)" shall be "False" on leg 1 on trip 1 on roster 1
        and rave "training.%must_have_in_period%("LC", "A4", 01FEB2019, 15FEB2019)" shall be "False" on leg 1 on trip 1 on roster 1
        and rave "training.%must_have_in_period%("LC", "A3", 01MAR2019, 01MAY2019)" shall be "False" on leg 1 on trip 1 on roster 1
        and rave "training.%must_have_in_period%("LC", "A4", 01MAR2019, 01MAY2019)" shall be "False" on leg 1 on trip 1 on roster 1


        @FD_LC_ALT_A3A4_9
        Scenario: Triple qualified LH pilot (A3A4A5) has LC document that expires in planning period without planned LC, must and may have filters should work as expected with upcoming A3 or A4 LC

        Given crew member 1 has document "REC+LC" from 30JUL2018 to 30APR2019 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 30JAN2018 to 31JAN2018 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 30JUL2017 to 31JUL2017 and has qualification "A4"
        Given crew member 1 has qualification "ACQUAL+A3" from 01FEB2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 13APR2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 13APR2011 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 34B    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 34B    |
        | leg | 0003 | SFO     | OSL     | 20FEB2019 | 01:30 | 12:20 | SK  | 35B    |
        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        Then rave "training.%must_have_in_period%("LC", "A3", 01FEB2019, 15FEB2019)" shall be "False" on leg 1 on trip 1 on roster 1
        and rave "training.%must_have_in_period%("LC", "A4", 01FEB2019, 15FEB2019)" shall be "False" on leg 1 on trip 1 on roster 1
        and rave "training.%must_have_in_period%("LC", "A3", 01MAR2019, 01MAY2019)" shall be "True" on leg 1 on trip 1 on roster 1
        and rave "training.%must_have_in_period%("LC", "A4", 01MAR2019, 01MAY2019)" shall be "True" on leg 1 on trip 1 on roster 1


        @FD_LC_ALT_A3A4_10
        Scenario: Single qualified LH pilot (A2) has LC document that expires in planning period, must and may have filters should work as before

        Given crew member 1 has document "REC+LC" from 30JUL2018 to 30APR2019 and has qualification "A2"
        Given crew member 1 has qualification "ACQUAL+A2" from 01FEB2011 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 32W    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 32W    |
        | leg | 0003 | SFO     | OSL     | 20FEB2019 | 01:30 | 12:20 | SK  | 32W    |
        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        Then rave "training.%must_have_in_period%("LC", "A2", 01FEB2019, 15FEB2019)" shall be "False" on leg 1 on trip 1 on roster 1
        and rave "training.%must_have_in_period%("LC", "A2", 01MAR2019, 01MAY2019)" shall be "True" on leg 1 on trip 1 on roster 1


        @FD_LC_ALT_A3A4_11
        Scenario: Qualification check overrides should handle A3 or A4 properly as well as other normal qualifications

        Given crew member 1 has document "REC+LC" from 30JUL2018 to 31JUL2019 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 30JAN2018 to 31JAN2018 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 30JUL2017 to 31JUL2017 and has qualification "A4"
        Given crew member 1 has qualification "ACQUAL+A3" from 01FEB2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 13APR2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 13APR2011 to 31DEC2035

        When I show "crew" in window 1
        Then rave "crew.%has_ac_qual_override_a3a4%("A3 or A4", 01FEB2019)" shall be "True" on leg 1 on trip 1 on roster 1
        and rave "crew.%has_ac_qual_override_a3a4%("A5", 01FEB2019)" shall be "True" on leg 1 on trip 1 on roster 1


        @FD_LC_ALT_A3A4_12
        Scenario: Qualification check overrides should handle A3 or A4 properly as well as other normal qualifications, with other results if one qual is missing

        Given crew member 1 has document "REC+LC" from 30JUL2018 to 31JUL2019 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 30JAN2018 to 31JAN2018 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 30JUL2017 to 31JUL2017 and has qualification "A4"
        Given crew member 1 has qualification "ACQUAL+A3" from 01FEB2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 13APR2011 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 32W    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 32W    |
        | leg | 0003 | SFO     | OSL     | 20FEB2019 | 01:30 | 12:20 | SK  | 32W    |
        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        Then rave "crew.%has_ac_qual_override_a3a4%("A3 or A4", 01FEB2019)" shall be "False" on leg 1 on trip 1 on roster 1
        and rave "crew.%has_ac_qual_override_a3a4%("A5", 01FEB2019)" shall be "True" on leg 1 on trip 1 on roster 1

