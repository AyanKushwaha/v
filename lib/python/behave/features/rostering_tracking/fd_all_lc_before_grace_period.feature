@TRACKING @JCRT @FD @FC @LC @OMA @A3A4 @ACQUAL @TRAINING
Feature: Tests that rules regarding line check timings work properly for crew with multiple aircraft qualifications, and that they trigger as they should before the grace period for all relevant crew.

##############################################################################
    Background: Set up for Tracking
        Given Tracking
        Given planning period from 1FEB2019 to 1JUL2019
##############################################################################

        @LC_FD_F1
        Scenario: SH pilot has LC more than 3 months in the future.
        Should get warning LC too early and be possible to rule except
        Warning: LC too early.

        Given a crew member with
        | attribute  | value  |
        | base       | CPH    |
        | title rank | FP     |
        | region     | SKD    |
        Given crew member 1 has document "REC+LC" from 30JUN2017 to 30JUN2019 and has qualification "A2"
        Given crew member 1 has contract "F00469"
        Given crew member 1 has qualification "ACQUAL+A2" from 30JUN2017 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | CPH     | ARN     | 17FEB2019 | 13:25 | 14:35 | SK  | 320    |
        | leg | 0002 | ARN     | MMX     | 17FEB2019 | 16:35 | 17:45 | SK  | 32G    |
        | leg | 0003 | MMX     | ARN     | 17FEB2019 | 18:10 | 19:15 | SK  | 32G    |
        | leg | 0004 | ARN     | OSD     | 17FEB2019 | 19:55 | 20:55 | SK  | 32G    |
        | leg | 0005 | OSD     | ARN     | 18FEB2019 | 11:45 | 12:45 | SK  | 32G    |
        | leg | 0006 | ARN     | FRA     | 18FEB2019 | 13:40 | 15:50 | SK  | 32G    |
        | leg | 0007 | FRA     | ARN     | 18FEB2019 | 16:30 | 18:40 | SK  | 32G    |
        | leg | 0008 | ARN     | OSD     | 18FEB2019 | 19:55 | 20:55 | SK  | 32G    |
        | leg | 0009 | OSD     | ARN     | 19FEB2019 | 11:45 | 12:45 | SK  | 32G    |
        | leg | 0010 | ARN     | OSL     | 19FEB2019 | 14:40 | 15:40 | SK  | 32G    |
        | leg | 0011 | OSL     | ARN     | 19FEB2019 | 16:15 | 17:15 | SK  | 32G    |
        | leg | 0012 | ARN     | CPH     | 19FEB2019 | 19:00 | 20:10 | SK  | 32W    |
        Given trip 1 is assigned to crew member 1 in position 1 with attribute TRAINING="LC"

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.lc_must_not_be_planned_too_early_fc" shall fail on leg 1 on trip 1 on roster 1


        @LC_FD_F2
        Scenario: Double qualified LH pilot (A3A4) has LC more than 3 months in the future.
        Crew Document shows A4 = time for A3. Training attribtue set on A3 trip.
        Should get warning LC too early and be possible to rule except
        Warning: LC too early.

        Given a crew member with
        | attribute  | value  |
        | base       | OSL    |
        | title rank | FP     |
        | region     | SKN    |
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A4"
        Given crew member 1 has contract "V134-LH"
        Given crew member 1 has qualification "ACQUAL+A3" from 13APR2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 01FEB2011 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | EWR     | 01FEB2019 | 10:00 | 18:25 | SK  | 33B    |
        | leg | 0002 | EWR     | OSL     | 03FEB2019 | 00:05 | 07:25 | SK  | 33B    |
        Given trip 1 is assigned to crew member 1 in position 1 with attribute TRAINING="LC"

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.lc_must_not_be_planned_too_early_fc" shall fail on leg 1 on trip 1 on roster 1


        @LC_FD_F3
        Scenario: Double qualified LH pilot (A3A4) has LC more than 3 months in the future.
        Crew Document says A4 = time for A3. Training attribute set on A4 trip.
        Should get warning LC too early but not be possible to rule except.
        Warning: No LC training need for A4.

        Given a crew member with
        | attribute  | value  |
        | base       | OSL    |
        | title rank | FP     |
        | region     | SKN    |
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A4"
        Given crew member 1 has contract "V134-LH"
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 15MAY2017 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 34B    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 34B    |
        | leg | 0003 | SFO     | CPH     | 20FEB2019 | 01:30 | 12:20 | SK  | 34B    |
        | leg | 0004 | CPH     | OSL     | 20FEB2019 | 13:20 | 14:30 | SK  | 320    |
        Given trip 1 is assigned to crew member 1 in position 1 with attribute TRAINING="LC"

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_ALL" shall fail on leg 1 on trip 1 on roster 1


        @LC_FD_F4
        Scenario: Double qualified LH pilot (A3A5) has LC more than 3 months in the future.
        Crew Document shows A5 = time for A3. Training attribtue set on A3 trip.
        Should get warning LC too early and be possible to rule except
        Warning: LC too early.

        Given a crew member with
        | attribute  | value  |
        | base       | OSL    |
        | title rank | FP     |
        | region     | SKN    |
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A5"
        Given crew member 1 has contract "V134-LH"
        Given crew member 1 has qualification "ACQUAL+A3" from 13APR2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 01FEB2011 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | EWR     | 01FEB2019 | 10:00 | 18:25 | SK  | 33B    |
        | leg | 0002 | EWR     | OSL     | 03FEB2019 | 00:05 | 07:25 | SK  | 33B    |
        Given trip 1 is assigned to crew member 1 in position 1 with attribute TRAINING="LC"

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.lc_must_not_be_planned_too_early_fc" shall fail on leg 1 on trip 1 on roster 1


        @LC_FD_F5
        Scenario: Double qualified LH pilot (A3A5) has LC more than 3 months in the future.
        Crew Document says A5 = time for A3. Training attribute set on A5 trip.
        Should get warning LC too early but not be possible to rule except.
        Warning: No LC training need for A5.

        Given a crew member with
        | attribute  | value  |
        | base       | OSL    |
        | title rank | FP     |
        | region     | SKN    |
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A5"
        Given crew member 1 has contract "V134-LH"
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 15MAY2017 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 35B    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 35B    |
        | leg | 0003 | SFO     | CPH     | 20FEB2019 | 01:30 | 12:20 | SK  | 35B    |
        | leg | 0004 | CPH     | OSL     | 20FEB2019 | 13:20 | 14:30 | SK  | 320    |
        Given trip 1 is assigned to crew member 1 in position 1 with attribute TRAINING="LC"

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_ALL" shall fail on leg 1 on trip 1 on roster 1


        @LC_FD_F6
        Scenario: Triple qualified LH pilot (A3A4A5) has LC more than 3 months in the future.
        Crew Document says A3 = time for A5. Training attribute set on A3 trip.
        Should get warning LC too early but not be possible to rule except.
        Warning: No LC training need for A3.

        Given a crew member with
        | attribute  | value  |
        | base       | OSL    |
        | title rank | FP     |
        | region     | SKN    |
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A3"
        Given crew member 1 has document "REC+LC" from 01JUN2015 to 01JUN2018 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 01MAY2015 to 01MAY2017 and has qualification "A4"
        Given crew member 1 has contract "V134-LH"
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 15MAY2017 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 18MAY2017 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH     | 18FEB2019 | 09:00 | 10:10 | SK  | 35B    |
        | leg | 0002 | CPH     | SFO     | 18FEB2019 | 11:25 | 22:45 | SK  | 35B    |
        | leg | 0003 | SFO     | CPH     | 20FEB2019 | 01:30 | 12:20 | SK  | 35B    |
        | leg | 0004 | CPH     | OSL     | 20FEB2019 | 13:20 | 14:30 | SK  | 320    |
        Given trip 1 is assigned to crew member 1 in position 1 with attribute TRAINING="LC"

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_ALL" shall fail on leg 1 on trip 1 on roster 1


        @LC_FD_F7
        Scenario: Triple qualified LH pilot (A3A4A5) has LC more than 3 months in the future.
        Crew Document shows A5, previous LC before that was A4 = time for A3. Training attribtue set on A3 trip.
        Should get warning LC too early and be possible to rule except
        Warning: LC too early.

        Given a crew member with
        | attribute  | value  |
        | base       | OSL    |
        | title rank | FP     |
        | region     | SKN    |
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A5"
        Given crew member 1 has document "REC+LC" from 01JUN2015 to 01JUN2018 and has qualification "A4"
        Given crew member 1 has document "REC+LC" from 01MAY2015 to 01MAY2017 and has qualification "A3"
        Given crew member 1 has contract "V134-LH"
        Given crew member 1 has qualification "ACQUAL+A3" from 13APR2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A4" from 01FEB2011 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A5" from 01FEB2011 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | EWR     | 01FEB2019 | 10:00 | 18:25 | SK  | 33B    |
        | leg | 0002 | EWR     | OSL     | 03FEB2019 | 00:05 | 07:25 | SK  | 33B    |
        Given trip 1 is assigned to crew member 1 in position 1 with attribute TRAINING="LC"

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.lc_must_not_be_planned_too_early_fc" shall fail on leg 1 on trip 1 on roster 1


        @LC_FD_F8
        Scenario: Single qualified LH pilot (A3) has LC more than 3 months in the future.
        Should get warning LC too early and be possible to rule except
        Warning: LC too early.

        Given a crew member with
        | attribute  | value  |
        | base       | OSL    |
        | title rank | FP     |
        | region     | SKN    |
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A3"
        Given crew member 1 has contract "V133-LH"
        Given crew member 1 has qualification "ACQUAL+A3" from 26JUL2017 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | EWR     | 10FEB2019 | 10:00 | 18:25 | SK  | 33B    |
        | leg | 0002 | EWR     | OSL     | 11FEB2019 | 00:05 | 07:25 | SK  | 33B    |
        Given trip 1 is assigned to crew member 1 in position 1 with attribute TRAINING="LC"

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.lc_must_not_be_planned_too_early_fc" shall fail on leg 1 on trip 1 on roster 1


        @LC_FD_F9
        Scenario: Single qualified LH pilot (A5) has LC more than 3 months in the future.
        Should get warning LC too early and be possible to rule except
        Warning: LC too early.

        Given a crew member with
        | attribute  | value  |
        | base       | OSL    |
        | title rank | FP     |
        | region     | SKN    |
        Given crew member 1 has document "REC+LC" from 30JUL2015 to 31JUL2019 and has qualification "A5"
        Given crew member 1 has contract "V133-LH"
        Given crew member 1 has qualification "ACQUAL+A5" from 26JUL2017 to 31DEC2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | EWR     | 10FEB2019 | 10:00 | 18:25 | SK  | 35B    |
        | leg | 0002 | EWR     | OSL     | 11FEB2019 | 00:05 | 07:25 | SK  | 35B    |
        Given trip 1 is assigned to crew member 1 in position 1 with attribute TRAINING="LC"

        When I show "crew" in window 1
        When I set parameter "fundamental.%use_now_debug%" to "TRUE"
        When I set parameter "fundamental.%now_debug%" to "10FEB2019 00:00"
        Then the rule "rules_qual_ccr.lc_must_not_be_planned_too_early_fc" shall fail on leg 1 on trip 1 on roster 1
