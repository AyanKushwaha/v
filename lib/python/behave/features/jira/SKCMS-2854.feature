@TRACKING @JCRT @FD @FC @LC @A2A5 @ACQUAL @TRAINING
Feature: Tests that rules for recurrent training works with line checks for crew with multiple aircraft qualifications.

##############################################################################
    Background: Set up common data
        Given Tracking
        Given planning period from 1JAN2022 to 28FEB2022

        Given a crew member with
        | attribute  | value  |
        | base       | OSL    |
        | title rank | FP     |
        | region     | SKN    |
        
        
##############################################################################
    @SCENARIO1
    Scenario: Verify that the PGT document is check passed for given crew.
    
    Given crew member 1 has document "REC+CRM" from 02JAN1986 to 01JAN2035
    Given crew member 1 has document "REC+LC" from 02JAN1986 to 01JAN2035 and has qualification "A2"
    Given crew member 1 has document "REC+PGT" from 02JAN2020 to 30NOV2021
    Given crew member 1 has document "REC+PCA5" from 02JAN1986 to 01JAN2035
    Given crew member 1 has document "REC+OPCA5" from 02JAN1986 to 01JAN2035
    Given crew member 1 has document "REC+PC" from 02JAN1986 to 01JAN2035 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 02JAN1986 to 01JAN2035 and has qualification "A2"
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has contract "V134-LH"

    Given a trip with the following activities
            | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
            | leg | 0001 | OSL     | CPH     | 10FEB2022 | 09:00 | 10:10 | SK  | 320    |
            | leg | 0002 | CPH     | SFO     | 10FEB2022 | 11:25 | 22:45 | SK  | 35A    |
            | leg | 0003 | SFO     | CPH     | 12FEB2022 | 01:30 | 12:20 | SK  | 35A    |
            | leg | 0004 | CPH     | OSL     | 12FEB2022 | 13:20 | 14:30 | SK  | 32W    |
    Given trip 1 is assigned to crew member 1 in position 1

    When I show "crew" in window 1  
    Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall fail on leg 1 on trip 1 on roster 1

    @SCENARIO2
    Scenario: Verify that Rule fail when crew have  REC+LC document  and PGT both expired.
    
    Given crew member 1 has document "REC+CRM" from 02JAN1986 to 01JAN2035
    Given crew member 1 has document "REC+LC" from 02JAN1986 to 30NOV2021 and has qualification "A2"
    Given crew member 1 has document "REC+PGT" from 02JAN2020 to 30NOV2021
    Given crew member 1 has document "REC+PCA5" from 02JAN1986 to 01JAN2035
    Given crew member 1 has document "REC+OPCA5" from 02JAN1986 to 01JAN2035
    Given crew member 1 has document "REC+PC" from 02JAN1986 to 01JAN2035 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 02JAN1986 to 01JAN2035 and has qualification "A2"
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has contract "V134-LH"

    Given a trip with the following activities
            | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
            | leg | 0001 | OSL     | CPH     | 10FEB2022 | 09:00 | 10:10 | SK  | 320    |
            | leg | 0002 | CPH     | SFO     | 10FEB2022 | 11:25 | 22:45 | SK  | 35A    |
            | leg | 0003 | SFO     | CPH     | 12FEB2022 | 01:30 | 12:20 | SK  | 35A    |
            | leg | 0004 | CPH     | OSL     | 12FEB2022 | 13:20 | 14:30 | SK  | 32W    |
    Given trip 1 is assigned to crew member 1 in position 1

    When I show "crew" in window 1  
    Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall fail on leg 1 on trip 1 on roster 1

    @SCENARIO3
    Scenario: Verify that Rule fail when crew have  REC+LC document  and CRM both expired.
    
    Given crew member 1 has document "REC+CRM" from 02JAN1986 to 30NOV2021
    Given crew member 1 has document "REC+LC" from 02JAN1986 to 30NOV2021 and has qualification "A2"
    Given crew member 1 has document "REC+PGT" from 02JAN2020 to 01JAN2035
    Given crew member 1 has document "REC+PCA5" from 02JAN1986 to 01JAN2035
    Given crew member 1 has document "REC+OPCA5" from 02JAN1986 to 01JAN2035
    Given crew member 1 has document "REC+PC" from 02JAN1986 to 01JAN2035 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 02JAN1986 to 01JAN2035 and has qualification "A2"
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has contract "V134-LH"

    Given a trip with the following activities
            | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
            | leg | 0001 | OSL     | CPH     | 10FEB2022 | 09:00 | 10:10 | SK  | 320    |
            | leg | 0002 | CPH     | SFO     | 10FEB2022 | 11:25 | 22:45 | SK  | 35A    |
            | leg | 0003 | SFO     | CPH     | 12FEB2022 | 01:30 | 12:20 | SK  | 35A    |
            | leg | 0004 | CPH     | OSL     | 12FEB2022 | 13:20 | 14:30 | SK  | 32W    |
    Given trip 1 is assigned to crew member 1 in position 1

    When I show "crew" in window 1  
    Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall fail on leg 1 on trip 1 on roster 1
    

    
