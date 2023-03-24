@JCRT @CC @SKD
Feature: new monthly parttime group in SKD

Background:
    Given Tracking
    Given planning period from 01OCT2020 to 31OCT2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 05NOV1998  | 31DEC2035 |
           | region          | SKD        | 05NOV1998  | 31DEC2035 |
           | base            | CPH        | 05NOV1998  | 31DEC2035 |
           | title rank      | AH         | 05NOV1998  | 31DEC2035 |
           | contract        | F00660     | 05OCT2019  | 31DEC2035 |

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 05NOV1998  | 31DEC2035 |
           | region          | SKD        | 05NOV1998  | 31DEC2035 |
           | base            | CPH        | 05NOV1998  | 31DEC2035 |
           | title rank      | AH         | 05NOV1998  | 31DEC2035 |
           | contract        | F00111     | 05OCT2019  | 31DEC2035 |

    Given table crew_contract_set is overridden with the following
    |  id    | dutypercent  | desclong           |
    | F00660 | 50           | MonthlyParttime    |


    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 002587  | CPH     | PMI     | 05OCT2020 14:10 | 05OCT2020 17:25 | 32N     |         |
           | leg     | SK      | 002588  | PMI     | CPH     | 05OCT2020 18:15 | 05OCT2020 21:20 | 32N     |         |
    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 1 is assigned to crew member 2 in position AH

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000458  | CPH     | OSL     | 06OCT2020 12:30 | 06OCT2020 13:40 | 32J     |         |
           | leg     | SK      | 000459  | OSL     | CPH     | 06OCT2020 14:30 | 06OCT2020 15:40 | 32J     |         |
           | leg     | SK      | 001470  | CPH     | OSL     | 06OCT2020 17:00 | 06OCT2020 18:05 | 32J     |         |
           | leg     | SK      | 000463  | OSL     | CPH     | 06OCT2020 19:00 | 06OCT2020 20:10 | 32J     |         |
    Given trip 2 is assigned to crew member 1 in position AH
    Given trip 2 is assigned to crew member 2 in position AH

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000793  | CPH     | NCE     | 08OCT2020 07:40 | 08OCT2020 10:05 | 32N     |         |
           | leg     | SK      | 000794  | NCE     | CPH     | 08OCT2020 10:55 | 08OCT2020 13:15 | 32N     |         |
    Given trip 3 is assigned to crew member 1 in position AH
    Given trip 3 is assigned to crew member 2 in position AH

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000943  | CPH     | ORD     | 14OCT2020 08:15 | 14OCT2020 17:20 | 33A     |         |
           | leg     | SK      | 000944  | ORD     | CPH     | 16OCT2020 21:00 | 17OCT2020 05:15 | 33A     |         |
    Given trip 4 is assigned to crew member 1 in position AH
    Given trip 4 is assigned to crew member 2 in position AH

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 002823  | CPH     | FAO     | 19OCT2020 04:05 | 19OCT2020 07:55 | 32N     |         |
           | leg     | SK      | 002824  | FAO     | CPH     | 19OCT2020 08:45 | 19OCT2020 12:25 | 32N     |         |
    Given trip 5 is assigned to crew member 1 in position AH
    Given trip 5 is assigned to crew member 2 in position AH

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000943  | CPH     | ORD     | 20OCT2020 08:15 | 20OCT2020 17:20 | 33A     |         |
           | leg     | SK      | 000944  | ORD     | CPH     | 21OCT2020 21:00 | 22OCT2020 05:15 | 33A     |         |
    Given trip 6 is assigned to crew member 1 in position AH
    Given trip 6 is assigned to crew member 2 in position AH

  @SCENARIO_1
  Scenario: test rule ind_max_duty_time_in_calendar_month_FC_SKN_SKL_SKS


  When I show "crew" in window 1
  and I set parameter "duty_time.%max_in_month_cc_4exng%" to "60:00"

  Then rave "crew.%is_crew_monthly_parttime_at_date%(wop.%start_utc%)" shall be "True" on leg 1 on trip 1 on roster 1
  and rave "crew.%is_crew_monthly_parttime_at_date%(wop.%start_utc%)" shall be "False" on leg 1 on trip 1 on roster 2
  and rave "rules_indust_ccr.%duty_time_calendar_month%" shall be "74:25" on leg 1 on trip 1 on roster 2
  and the rule "rules_indust_ccr.ind_max_duty_time_in_calendar_month_FC_SKN_SKL_SKS" shall fail on leg 1 on trip 1 on roster 1
  and the rule "rules_indust_ccr.ind_max_duty_time_in_calendar_month_FC_SKN_SKL_SKS" shall pass on leg 1 on trip 1 on roster 2


  @SCENARIO_2 @To_Be_Checked
  Scenario: test rule ind_max_duty_time_in_cal_month_pt_cc_pt_SKS_monthly_pt_SKD

  Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000716  | ARN     | HEL     | 01OCT2020 12:50 | 01OCT2020 13:45 | 32N     |         |
           | leg     | SK      | 000721  | HEL     | ARN     | 01OCT2020 14:20 | 01OCT2020 15:25 | 32N     |         |
           | leg     | SK      | 000002  | ARN     | LLA     | 01OCT2020 19:10 | 01OCT2020 20:25 | 32N     |         |
           | leg     | SK      | 000011  | LLA     | ARN     | 02OCT2020 13:50 | 02OCT2020 15:10 | 31W     |         |
           | leg     | SK      | 000070  | ARN     | OSD     | 02OCT2020 15:55 | 02OCT2020 16:55 | 31W     |         |
           | leg     | SK      | 000071  | OSD     | ARN     | 02OCT2020 17:25 | 02OCT2020 18:20 | 31W     |         |
  Given trip 7 is assigned to crew member 1 in position AH
  Given trip 7 is assigned to crew member 2 in position AH


  When I show "crew" in window 1

  Then rave "rules_indust_ccr.%planned_duty_time_calendar_month%" shall be "88:50" on leg 1 on trip 1 on roster 2
  and rave "duty_time.%max_duty_in_calendar_month_pt_cc%(rules_indust_ccr.%_specific_date%)" shall be "83:00" on leg 1 on trip 1 on roster 1
  and the rule "rules_indust_ccr.ind_max_duty_time_in_calendar_month_pt_cc_parttime_SKS_monthly_parttime_SKD" shall pass on leg 1 on trip 1 on roster 1
  and the rule "rules_indust_ccr.ind_max_duty_time_in_calendar_month_pt_cc_parttime_SKS_monthly_parttime_SKD" shall pass on leg 1 on trip 1 on roster 2
