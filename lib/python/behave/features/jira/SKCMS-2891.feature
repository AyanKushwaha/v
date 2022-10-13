@TRACKING @JCRT @FD @FC @LC @A2A5 @ACQUAL @TRAINING
Feature: Tests that rules for recurrent training works based on leg end date at homebase

##############################################################################
    Background: Set up common data
        Given Tracking
        Given planning period from 1FEB2022 to 28FEB2022

        Given a crew member with
        | attribute  | value  |
        | base       | OSL    |
        | title rank | FP     |
        | region     | SKN    |
        Given crew member 1 has document "REC+CRM" from 02JAN1986 to 01JAN2035
        Given crew member 1 has document "REC+PGT" from 02JAN1986 to 20FEB2022
        Given crew member 1 has document "REC+LPCA5" from 02JAN1986 to 01JAN2035
        Given crew member 1 has document "REC+OPCA5" from 02JAN1986 to 01JAN2035
        Given crew member 1 has document "REC+LPC" from 02JAN1986 to 01JAN2035 and has qualification "A2"
        Given crew member 1 has document "REC+OPC" from 02JAN1986 to 01JAN2035 and has qualification "A2"
        Given crew member 1 has contract "V134-LH"

##############################################################################

        @SCENARIO1
        Scenario: Verify that the PGT document checks fail for crew if leg end date at homebase is greater than expiry time.

        Given crew member 1 has qualification "ACQUAL+A2" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 18MAY2017 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 19FEB2022 | 09:00 | 10:10 | SK  | 320    |
        | leg | 0002 | CPH     | SFO     | 19FEB2022 | 11:25 | 22:45 | SK  | 35A    |
        | leg | 0003 | SFO     | CPH     | 20FEB2022 | 01:30 | 12:20 | SK  | 35A    |
        | leg | 0004 | CPH     | OSL     | 21FEB2022 | 13:20 | 14:30 | SK  | 32W    |

        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2022 00:00"
        Then the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall fail on leg 4 on trip 1 on roster 1


##############################################################################


        @SCENARIO2
        Scenario: Verify that the PGT document checks pass for crew if leg end date at homebase is less than expiry time.

        Given crew member 1 has qualification "ACQUAL+A2" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 18MAY2017 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 17FEB2022 | 09:00 | 10:10 | SK  | 320    |
        | leg | 0002 | CPH     | SFO     | 17FEB2022 | 11:25 | 22:45 | SK  | 35A    |
        | leg | 0003 | SFO     | CPH     | 18FEB2022 | 01:30 | 12:20 | SK  | 35A    |
        | leg | 0004 | CPH     | OSL     | 19FEB2022 | 13:20 | 14:30 | SK  | 32W    |

        Given trip 1 is assigned to crew member 1 in position 1

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2022 00:00"
        Then the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 4 on trip 1 on roster 1

