Feature: Test airport qualifications

  Background: set up for tracking
    Given Tracking
    Given planning period from 1feb2018 to 28feb2018


  @SCENARIO1
  Scenario: Check that airport is allowed when qualification is active

    Given a crew member with homebase "OSL"
    Given crew member 1 has qualification "ACQUAL+A2" from 1FEB2018 to 28FEB2018 
    Given crew member 1 has acqual qualification "ACQUAL+A2+AIRPORT+GZP" from 1FEB2018 to 28FEB2018 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | GZP     | 01FEB2018 | 10:00 | 11:00 | SK  | 319    |
    | leg | 0002 | GZP     | OSL     | 01FEB2018 | 12:00 | 13:00 | SK  | 319    |
    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_arr_airport_ok_fc" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO2
  Scenario: Check that airport is not allowed when airport qualification is not active

    Given a crew member with homebase "OSL"
    Given crew member 1 has qualification "ACQUAL+A2" from 1FEB2018 to 28FEB2018 
    Given crew member 1 has acqual qualification "ACQUAL+A2+AIRPORT+GZP" from 2FEB2018 to 28FEB2018 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | GZP     | 01FEB2018 | 10:00 | 11:00 | SK  | 319    |
    | leg | 0002 | GZP     | OSL     | 01FEB2018 | 12:00 | 13:00 | SK  | 319    |
    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_arr_airport_ok_fc" shall fail on leg 1 on trip 1 on roster 1


  @SCENARIO3
  Scenario: Check that airport is not allowed when crew has NEW restriction for ACTYPE

    Given a crew member with homebase "OSL"
    Given crew member 1 has qualification "ACQUAL+A2" from 1FEB2018 to 28FEB2018 
    Given crew member 1 has acqual qualification "ACQUAL+A2+AIRPORT+GZP" from 1FEB2018 to 28FEB2018 
    Given crew member 1 has acqual restriction "ACQUAL+A2+NEW+ACTYPE" from 1FEB2018 to 28FEB2018 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | GZP     | 01FEB2018 | 10:00 | 11:00 | SK  | 319    |
    | leg | 0002 | GZP     | OSL     | 01FEB2018 | 12:00 | 13:00 | SK  | 319    |
    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_actype_airport_ok_fc" shall fail on leg 1 on trip 1 on roster 1


  @SCENARIO4
  Scenario: Check that airport is allowed when qualification is active for AWB and flying A3

    Given a crew member with homebase "OSL"
    Given crew member 1 has qualification "ACQUAL+A3" from 1FEB2018 to 28FEB2018 
    Given crew member 1 has acqual qualification "ACQUAL+AWB+AIRPORT+US" from 1FEB2018 to 28FEB2018 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | SFO     | 01FEB2018 | 10:00 | 11:00 | SK  | 33A    |
    | leg | 0002 | SFO     | OSL     | 01FEB2018 | 12:00 | 13:00 | SK  | 33A    |
    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_arr_airport_ok_fc" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO5
  Scenario: Check that airport is allowed when qualification is active for AWB and flying A4

    Given a crew member with homebase "OSL"
    Given crew member 1 has qualification "ACQUAL+A4" from 1FEB2018 to 28FEB2018 
    Given crew member 1 has acqual qualification "ACQUAL+AWB+AIRPORT+US" from 1FEB2018 to 28FEB2018 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | SFO     | 01FEB2018 | 10:00 | 11:00 | SK  | 34A    |
    | leg | 0002 | SFO     | OSL     | 01FEB2018 | 12:00 | 13:00 | SK  | 34A    |
    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_arr_airport_ok_fc" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO6
  Scenario: Check that airport is not allowed when qualification is not active for AWB and flying A4

    Given a crew member with homebase "OSL"
    Given crew member 1 has qualification "ACQUAL+A4" from 1FEB2018 to 28FEB2018 
    Given crew member 1 has acqual qualification "ACQUAL+AWB+AIRPORT+US" from 2FEB2018 to 28FEB2018 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | SFO     | 01FEB2018 | 10:00 | 11:00 | SK  | 34A    |
    | leg | 0002 | SFO     | OSL     | 01FEB2018 | 12:00 | 13:00 | SK  | 34A    |
    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_arr_airport_ok_fc" shall fail on leg 1 on trip 1 on roster 1


  @SCENARIO7
  Scenario: Check that airport qualifications in planning period are detected correctly

    Given a crew member with homebase "OSL"
    Given crew member 1 has qualification "ACQUAL+A2" from 1FEB2018 to 15FEB2018 
    Given crew member 1 has qualification "ACQUAL+A4" from 15FEB2018 to 1MAR2018 
#    Given crew member 1 has qualification "AIRPORT+GZP" from 1FEB2018 to 15FEB2018 
#    Given crew member 1 has qualification "AIRPORT+US" from 15FEB2018 to 1MAR2018 
    Given crew member 1 has acqual qualification "ACQUAL+A2+AIRPORT+GZP" from 1FEB2018 to 1MAR2018 
    Given crew member 1 has acqual qualification "ACQUAL+AWB+AIRPORT+US" from 15FEB2018 to 1MAR2018 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | SFO     | 01FEB2018 | 10:00 | 11:00 | SK  | 34A    |
    | leg | 0002 | SFO     | OSL     | 01FEB2018 | 12:00 | 13:00 | SK  | 34A    |
    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    Then rave "crew.%has_aptqln_in_pp%(\"GZP\")" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "crew.%has_aptqln_in_pp%(\"US\")" shall be "True" on leg 1 on trip 1 on roster 1


  @SCENARIO8
  Scenario: Check that airport qualification in planning period is detected correctly when no airport qualification in beginning of period

    Given a crew member with homebase "OSL"
    Given crew member 1 has qualification "ACQUAL+A4" from 15FEB2018 to 1MAR2018 
    Given crew member 1 has acqual qualification "ACQUAL+A2+AIRPORT+GZP" from 1FEB2018 to 1MAR2018 
    Given crew member 1 has acqual qualification "ACQUAL+AWB+AIRPORT+US" from 15FEB2018 to 1MAR2018 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | SFO     | 01FEB2018 | 10:00 | 11:00 | SK  | 34A    |
    | leg | 0002 | SFO     | OSL     | 01FEB2018 | 12:00 | 13:00 | SK  | 34A    |
    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    Then rave "crew.%has_aptqln_in_pp%(\"GZP\")" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "crew.%has_aptqln_in_pp%(\"US\")" shall be "True" on leg 1 on trip 1 on roster 1


  @SCENARIO9
  Scenario: Check that airport qualification in planning period is detected correctly when no airport qualification at end of period

    Given a crew member with homebase "OSL"
    Given crew member 1 has qualification "ACQUAL+A2" from 1FEB2018 to 15FEB2018 
    Given crew member 1 has acqual qualification "ACQUAL+A2+AIRPORT+GZP" from 1FEB2018 to 1MAR2018 
    Given crew member 1 has acqual qualification "ACQUAL+AWB+AIRPORT+US" from 15FEB2018 to 1MAR2018 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | SFO     | 01FEB2018 | 10:00 | 11:00 | SK  | 34A    |
    | leg | 0002 | SFO     | OSL     | 01FEB2018 | 12:00 | 13:00 | SK  | 34A    |
    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    Then rave "crew.%has_aptqln_in_pp%(\"GZP\")" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "crew.%has_aptqln_in_pp%(\"US\")" shall be "False" on leg 1 on trip 1 on roster 1
