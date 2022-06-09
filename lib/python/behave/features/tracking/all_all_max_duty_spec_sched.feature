@JCT @TRACKING

Feature: fix max duty calculation in special schedule rule

########################
# JIRA - SKCMS-1418
########################

Background:
    Given Tracking
    Given planning period from 1AUG2020 to 31AUG2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | employee number | 11023      |            |           |
           | sex             | F          |            |           |
           | crew rank       | AP         | 02NOV2018  | 01JAN2036 |
           | region          | SKS        | 02NOV2018  | 01JAN2036 |
           | base            | STO        | 02NOV2018  | 01JAN2036 |
           | title rank      | AP         | 02NOV2018  | 01JAN2036 |
           | contract        | F00638     | 01JAN2020  | 02FEB2020 |
           | published       | 01AUG2020  | 01JAN1986  |           |

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000010  | ARN     | LLA     | 17AUG2020 13:00 | 17AUG2020 14:20 | 320     |         |
           | leg     | SK      | 000011  | LLA     | ARN     | 17AUG2020 14:55 | 17AUG2020 16:20 | 320     |         |
    Given trip 1 is assigned to crew member 1 in position AH



  @SCENARIO_1
  Scenario: Difference between previous variable and new one

  Given crew member 1 has a personal activity "RR" at station "ARN" that starts at 17AUG2020 08:20 and ends at 17AUG2020 12:10

  When I show "crew" in window 1
  Then rave "duty.%duty_time_spec_sched%(duty.union, True)" shall be "4:25" on leg 2 on trip 1 on roster 1
  and rave "duty.%duty_time%(duty.union, True)" shall be "5:22" on leg 2 on trip 1 on roster 1


  @SCENARIO_2
  Scenario: Standby does not affect the duty time calculation for the rule

  Given crew member 1 has a personal activity "RR" at station "ARN" that starts at 17AUG2020 06:20 and ends at 17AUG2020 11:10

  When I show "crew" in window 1
  Then rave "duty.%duty_time_spec_sched%(duty.union, True)" shall be "4:25" on leg 2 on trip 1 on roster 1


