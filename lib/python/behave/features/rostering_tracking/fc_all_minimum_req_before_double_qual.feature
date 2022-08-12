@TRACKING @PLANNING @FC

Feature: test activation of the rule rules_caa_ccr.trng_min_blk_or_legs_before_double_qual

Background: common background
  Given Tracking
  Given planning period from 01AUG2020 to 31AUG2020
  Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 03JUN2020  | 01JAN2036 |
           | region          | SKS        | 03JUN2020  | 01JAN2036 |
           | base            | STO        | 03JUN2020  | 01JAN2036 |
           | title rank      | FC         | 03JUN2020  | 01JAN2036 |
           | contract        | V133-CV60  | 01JUN2020  | 01SEP2020 |

  Given crew member 1 has qualification "ACQUAL+A2" from 21MAY2020 to 01JAN2036

  Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000689  | ARN     | LIN     | 16AUG2020 09:05 | 16AUG2020 11:45 | 32N     |         |
           | leg     | SK      | 000690  | LIN     | ARN     | 16AUG2020 12:35 | 16AUG2020 15:15 | 32N     |         |
           | leg     | SK      | 000165  | ARN     | GOT     | 16AUG2020 16:15 | 16AUG2020 17:10 | 31W     |         |
           | leg     | SK      | 000166  | GOT     | ARN     | 16AUG2020 17:40 | 16AUG2020 18:35 | 31W     |         |
  Given trip 1 is assigned to crew member 1 in position FC

  Given table crew_training_need additionally contains the following
      | crew     | part | validfrom     | validto    | course       | attribute  | acqual |
      | Crew001  | 1    | 13NOV2019     | 13FEB2020  | CCQ from SH  | ILC        | A3     |


  @SCENARIO_1
  Scenario: if course not taken then the rule is inactive

  When I show "crew" in window 1
  Then rave "rules_caa_ccr.%course_CCQ_A2A3_A3A2_A2A5_A5A2_ILC_last_year%" shall be "False" on leg 1 on trip 1 on roster 1
  and rave "rules_caa_ccr.%valid_trng_min_blk_or_legs_before_double_qual%" shall be "False" on leg 1 on trip 1 on roster 1


  @SCENARIO_2
  Scenario: course taken but only one qualification is active, then the rule is inactive

  Given table crew_training_log additionally contains the following
      | crew     | typ  | code   | tim        |
      | Crew001  | ILC  | A3     | 01FEB2020  |

  When I show "crew" in window 1
  Then rave "rules_caa_ccr.%course_CCQ_A2A3_A3A2_A2A5_A5A2_ILC_last_year%" shall be "True" on leg 1 on trip 1 on roster 1
  and rave "rules_caa_ccr.%valid_trng_min_blk_or_legs_before_double_qual%" shall be "False" on leg 1 on trip 1 on roster 1


  @SCENARIO_3
  Scenario: course taken and both qualifications are active, rule is active

  Given crew member 1 has qualification "ACQUAL+A3" from 21MAY2020 to 01JAN2036

  Given table crew_training_log additionally contains the following
      | crew     | typ  | code   | tim        |
      | Crew001  | ILC  | A3     | 01FEB2020  |

  When I show "crew" in window 1
  Then rave "rules_caa_ccr.%course_CCQ_A2A3_A3A2_A2A5_A5A2_ILC_last_year%" shall be "True" on leg 1 on trip 1 on roster 1
  and rave "rules_caa_ccr.%valid_trng_min_blk_or_legs_before_double_qual%" shall be "True" on leg 1 on trip 1 on roster 1
  and the rule "rules_caa_ccr.trng_min_blk_or_legs_before_double_qual" shall fail on leg 1 on trip 1 on roster 1