@tracking @SKJ @CC @OVERTIME
Feature: Check that AST recurrents work.
  Background: Set up common data

    Given Tracking

    Given planning period from 1JAN2020 to 31JAN2020
    Given a crew member with
      | attribute  | value |
      | crew rank  | AH    |
      | title rank | AH    |
      | region     | SKJ   |
      | base       | NRT   |

    Given crew member 1 has qualification "ACQUAL+AL" from 1APR2017 to 31DEC2035


  @SCENARIO1
  Scenario: Check overtime limits for SK983 and SK984

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 984 | NRT     | CPH     | 5JAN2020 02:10 | 5JAN2020 13:45 | 33A    |
      | leg | SK  | 983 | CPH     | NRT     | 6JAN2020 13:45 | 7JAN2020 00:45 | 33A    |
    Given trip 1 is assigned to crew member 1 in position AH


    When I show "crew" in window 1

    Then rave "report_jp_overtime.%overtime_limit%" shall be "13:15" on leg 1 on trip 1 on roster 1
    and rave "report_jp_overtime.%overtime_limit%" shall be "12:50" on leg 2 on trip 1 on roster 1

  @SCENARIO2
  Scenario: Check overtime calculation for trip without training

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 984 | NRT     | CPH     | 5JAN2020 02:10 | 5JAN2020 13:45 | 33A    |
      | leg | SK  | 983 | CPH     | NRT     | 6JAN2020 13:45 | 7JAN2020 00:52 | 33A    |
    Given trip 1 is assigned to crew member 1 in position AH


    When I show "crew" in window 1

    Then rave "report_jp_overtime.%leg_ot_normal%" shall be "0:05" on leg 1 on trip 1 on roster 1
    and rave "report_jp_overtime.%leg_ot_normal%" shall be "0:07" on leg 2 on trip 1 on roster 1


  @SCENARIO3
  Scenario: Check overtime calculation for trip with only deadheads and training

    Given a trip with the following activities
      | act    | num | code | dep stn | arr stn | dep             | arr             | ac_typ |
      | dh     | 984 |      | NRT     | CPH     | 8JAN2020 02:10  | 8JAN2020 13:45  | 34A    |
      | ground |     | NP54 | CPH     | CPH     | 9JAN2020 11:00  | 9JAN2020 14:00  |        |
      | ground |     | CX7  | CPH     | CPH     | 10JAN2020 06:15 | 10JAN2020 14:00 |        |
      | dh     | 983 |      | CPH     | NRT     | 11JAN2020 13:45 | 12JAN2020 00:52 | 34A    |
    Given trip 1 is assigned to crew member 1 in position AH


    When I show "crew" in window 1

    Then rave "report_jp_overtime.%leg_ot_normal%" shall be "0:00" on leg 1 on trip 1 on roster 1
    and rave "report_jp_overtime.%leg_ot_normal%" shall be "0:00" on leg 4 on trip 1 on roster 1


  @SCENARIO4
  Scenario: Check overtime calculation for trip with no training and one deadhead

    Given a trip with the following activities
      | act    | num | code | dep stn | arr stn | dep             | arr             | ac_typ |
      | leg    | 984 |      | NRT     | CPH     | 8JAN2020 02:10  | 8JAN2020 13:45  | 34A    |
      | dh     | 983 |      | CPH     | NRT     | 9JAN2020 13:45  | 10JAN2020 00:52 | 34A    |

    Given trip 1 is assigned to crew member 1 in position AH with
      | type      | leg | name        | value |
      | attribute | 2   | JP_OVERTIME |       |


    When I show "crew" in window 1

    Then rave "report_jp_overtime.%leg_ot_normal%" shall be "0:05" on leg 1 on trip 1 on roster 1
    and rave "report_jp_overtime.%leg_ot_normal%" shall be "0:07" on leg 2 on trip 1 on roster 1


  @SCENARIO5
  Scenario: Check overtime calculation for trip called out from standby

    Given crew member 1 has the following personal activities
      | code | stn | start_date | start_time | end_date | end_time |
      | R2   | NRT | 7JAN2020   | 19:00      | 7JAN2020 | 21:11    |
 
    Given a trip with the following activities
      | act    | num | code | dep stn | arr stn | dep             | arr             | ac_typ |
      | leg    | 984 |      | NRT     | CPH     | 8JAN2020 02:10  | 8JAN2020 13:45  | 34A    |
      | leg    | 983 |      | CPH     | NRT     | 9JAN2020 13:45  | 10JAN2020 00:52 | 34A    |
    Given trip 1 is assigned to crew member 1 in position AH


    When I show "crew" in window 1

    Then rave "report_jp_overtime.%leg_ot_normal%" shall be "2:16" on leg 2 on trip 1 on roster 1
    and rave "report_jp_overtime.%leg_ot_normal%" shall be "0:07" on leg 3 on trip 1 on roster 1


  @SCENARIO6
  Scenario: Check overtime limits with over 16 hours for SK983 and SK984

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 984 | NRT     | CPH     | 5JAN2020 02:10 | 5JAN2020 18:45 | 33A    |
      | leg | SK  | 983 | CPH     | NRT     | 6JAN2020 13:45 | 7JAN2020 06:45 | 33A    |
    Given trip 1 is assigned to crew member 1 in position AH


    When I show "crew" in window 1

    Then rave "report_jp_overtime.%leg_ot_over_16_hours%" shall be "2:20" on leg 1 on trip 1 on roster 1
    and rave "report_jp_overtime.%leg_ot_over_16_hours%" shall be "2:50" on leg 2 on trip 1 on roster 1


  @SCENARIO7
  Scenario: Check overtime with over 16 hours calculation for trip without training

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 984 | NRT     | CPH     | 5JAN2020 02:10 | 5JAN2020 18:45 | 33A    |
      | leg | SK  | 983 | CPH     | NRT     | 6JAN2020 13:45 | 7JAN2020 06:52 | 33A    |
    Given trip 1 is assigned to crew member 1 in position AH


    When I show "crew" in window 1

    Then rave "report_jp_overtime.%leg_ot_over_16_hours%" shall be "2:20" on leg 1 on trip 1 on roster 1
    and rave "report_jp_overtime.%leg_ot_over_16_hours%" shall be "2:57" on leg 2 on trip 1 on roster 1


  @SCENARIO8
  Scenario: Check overtime with over 16 hours calculation for trip with only deadheads and training

    Given a trip with the following activities
      | act    | num | code | dep stn | arr stn | dep             | arr             | ac_typ |
      | dh     | 984 |      | NRT     | CPH     | 8JAN2020 02:10  | 8JAN2020 18:45  | 34A    |
      | ground |     | NP54 | CPH     | CPH     | 9JAN2020 11:00  | 9JAN2020 14:00  |        |
      | ground |     | CX7  | CPH     | CPH     | 10JAN2020 06:15 | 10JAN2020 14:00 |        |
      | dh     | 983 |      | CPH     | NRT     | 11JAN2020 13:45 | 12JAN2020 06:52 | 34A    |
    Given trip 1 is assigned to crew member 1 in position AH


    When I show "crew" in window 1

    Then rave "report_jp_overtime.%leg_ot_over_16_hours%" shall be "0:00" on leg 1 on trip 1 on roster 1
    and rave "report_jp_overtime.%leg_ot_over_16_hours%" shall be "0:00" on leg 4 on trip 1 on roster 1

  @SCENARIO9
  Scenario: Check overtime with over 16 hours calculation for trip with no training and one deadhead

    Given a trip with the following activities
      | act    | num | code | dep stn | arr stn | dep             | arr             | ac_typ |
      | leg    | 984 |      | NRT     | CPH     | 8JAN2020 02:10  | 8JAN2020 18:45  | 34A    |
      | dh     | 983 |      | CPH     | NRT     | 9JAN2020 13:45  | 10JAN2020 06:52 | 34A    |

    Given trip 1 is assigned to crew member 1 in position AH with
      | type      | leg | name        | value |
      | attribute | 2   | JP_OVERTIME |       |


    When I show "crew" in window 1

    Then rave "report_jp_overtime.%leg_ot_over_16_hours%" shall be "2:20" on leg 1 on trip 1 on roster 1
    and rave "report_jp_overtime.%leg_ot_over_16_hours%" shall be "2:57" on leg 2 on trip 1 on roster 1


  @SCENARIO10
  Scenario: Check overtime with over 16 hours calculation for trip called out from standby

    Given crew member 1 has the following personal activities
      | code | stn | start_date | start_time | end_date | end_time |
      | R2   | NRT | 7JAN2020   | 19:00      | 7JAN2020 | 21:11    |

    Given a trip with the following activities
      | act    | num | code | dep stn | arr stn | dep             | arr             | ac_typ |
      | leg    | 984 |      | NRT     | CPH     | 8JAN2020 02:10  | 8JAN2020 18:45  | 34A    |
      | leg    | 983 |      | CPH     | NRT     | 9JAN2020 13:45  | 10JAN2020 06:52 | 34A    |
    Given trip 1 is assigned to crew member 1 in position AH


    When I show "crew" in window 1

    Then rave "report_jp_overtime.%leg_ot_over_16_hours%" shall be "2:20" on leg 2 on trip 1 on roster 1
    and rave "report_jp_overtime.%leg_ot_over_16_hours%" shall be "2:57" on leg 3 on trip 1 on roster 1