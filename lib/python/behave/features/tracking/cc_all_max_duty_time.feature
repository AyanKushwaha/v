#######################################
# This feature intends to include all max duty time rules for cabin
#
########################################
@TRACKING @SBY @SKD @SKN @CC
Feature: Testing max duty time rules for cabin

    Background: Setup for tracking
        Given Tracking
        Given planning period from 1FEB2020 to 1APR2020

        @SCENARIO1
        Scenario: Max duty time when standby callout NKF CC should not exceed 17 hours.
            Given a crew member with
                   | attribute       | value      | valid from | valid to  |
                   | crew rank       | AH         | 26NOV2018  | 01JAN2036 |
                   | region          | SKN        | 26NOV2018  | 01JAN2036 |
                   | base            | OSL        | 26NOV2018  | 01JAN2036 |
                   | title rank      | AH         | 26NOV2018  | 01JAN2036 |
                   | contract        | V301       | 01FEB2020  | 01JAN2036 |
            Given crew member 1 has qualification "ACQUAL+38" from 26NOV2018 to 01JAN2036

            Given crew member 1 has a personal activity "R" at station "OSL" that starts at 24FEB2020 05:00 and ends at 24FEB2020 10:40
            Given a trip with the following activities
                   | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
                   | leg     | SK      | 000809  | OSL     | LHR     | 24FEB2020 14:00 | 24FEB2020 16:25 | 73H     |         |
                   | leg     | SK      | 000810  | LHR     | OSL     | 24FEB2020 19:50 | 24FEB2020 21:53 | 73H     |         |
            Given trip 1 is assigned to crew member 1 in position AH

            When I show "crew" in window 1
            Then the rule "rules_indust_cct.ind_max_duty_time_when_sb_callout" shall fail on leg 2 on trip 1 on roster 1

        # SKCMS-2462
        @SCENARIO2
        Scenario: Max duty time when standby callout SKD CC should not exceed 17 hours.
            Given a crew member with
                   | attribute       | value      | valid from | valid to  |
                   | crew rank       | AH         | 03APR2001  | 31DEC2035 |
                   | region          | SKD        | 03APR2001  | 31DEC2035 |
                   | base            | CPH        | 03APR2001  | 31DEC2035 |
                   | title rank      | AH         | 03APR2001  | 31DEC2035 |
                   | contract        | F00661     | 12APR2019  | 31DEC2035 |
            Given crew member 1 has qualification "ACQUAL+A2" from 25AUG2014 to 01JAN2036
            Given crew member 1 has qualification "ACQUAL+AL" from 13MAR2019 to 01JAN2036
            Given crew member 1 has qualification "POSITION+SCC" from 24OCT2008 to 31DEC2035

            Given crew member 1 has a personal activity "RS" at station "CPH" that starts at 26FEB2020 09:00 and ends at 26FEB2020 10:05
            Given a trip with the following activities
                   | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
                   | dh      | SK      | 009241  | CPH     | LPA     | 26FEB2020 12:15 | 26FEB2020 17:20 | 34B     |         |
                   | leg     | SK      | 006274  | LPA     | CPH     | 26FEB2020 20:43 | 27FEB2020 01:47 | 34B     |         |
            Given trip 1 is assigned to crew member 1 in position AH

            When I show "crew" in window 1
            Then the rule "rules_indust_cct.ind_max_duty_time_when_sb_callout" shall fail on leg 2 on trip 1 on roster 1
