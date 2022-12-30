@TRACKING @JCRT @TRAINING @ALL @FD @SKS-532
Feature: Rule for minimum 30 days (one month) spacing required between each sim session

  Background: 
    Given Tracking
    Given planning period from 1MAR2020 to 30APR2020

  @SCENARIO1
  Scenario: Check that rule fails when sim session is less than 30 days spacing and passes when sim session is >= 30 days spacing
    Given a crew member with
      | attribute       | value |
      | employee number | 1     |
      | crew rank       | FC    |
      | title rank      | FC    |
      | region          | SKI   |
      | base            | STO   |
    Given a crew member with
      | attribute       | value |
      | employee number | 2     |
      | crew rank       | FC    |
      | title rank      | FC    |
      | region          | SKI   |
      | base            | STO   |
    Given a crew member with
      | attribute       | value |
      | employee number | 3     |
      | crew rank       | FC    |
      | title rank      | FC    |
      | region          | SKI   |
      | base            | STO   |
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+LPC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1MAY2018 to 30SEP2020 and has qualification "A2"
    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 31MAY2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 30NOV2020

    Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 2 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 2 has document "REC+OPC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 2 has document "REC+LPC" from 1MAY2018 to 30SEP2020 and has qualification "A2"
    Given crew member 2 has document "REC+OPCA3" from 1APR2018 to 31MAY2020
    Given crew member 2 has document "REC+LPCA3" from 1MAY2018 to 30NOV2020

    Given crew member 3 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 3 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 3 has document "REC+OPC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 3 has document "REC+LPC" from 1MAY2018 to 30SEP2020 and has qualification "A2"
    Given crew member 3 has document "REC+OPCA3" from 1APR2018 to 31MAY2020
    Given crew member 3 has document "REC+LPCA3" from 1MAY2018 to 30NOV2020

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr             |
      | ground | S6   | ARN     | ARN     | 14MAR2020 8:00 | 14MAR2020 12:00 |
      And a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr             |
      | ground | S6   | ARN     | ARN     | 13APR2020 8:00 | 13APR2020 12:00 |

    Given trip 1 is assigned to crew member 1 in position FC
      And trip 2 is assigned to crew member 1 in position FC

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr             |
      | ground | S6   | ARN     | ARN     | 14MAR2020 8:00 | 14MAR2020 12:00 |
      And a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr             |
      | ground | S6   | ARN     | ARN     | 14APR2020 8:00 | 14APR2020 12:00 |

    Given trip 3 is assigned to crew member 2 in position FC
      And trip 4 is assigned to crew member 2 in position FC

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr             |
      | ground | S6   | ARN     | ARN     | 14MAR2020 8:00 | 14MAR2020 12:00 |
      And a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr             |
      | ground | S6   | ARN     | ARN     | 15APR2020 8:00 | 15APR2020 12:00 |

    Given trip 5 is assigned to crew member 3 in position FC
      And trip 6 is assigned to crew member 3 in position FC

     When I show "crew" in window 1

    #Rule fails as there is only 29 days of space between two sim session
     Then the rule "rules_training_ccr.min_30_days_required_between_each_sim_session" shall fail on leg 1 on trip 2 on roster 1
      And rave "rules_training_ccr.%num_days_since_last_sim_event%" shall be "29" on leg 1 on trip 2 on roster 1
    #Rule passes as there is 30 days of space between two sim session
      And the rule "rules_training_ccr.min_30_days_required_between_each_sim_session" shall pass on leg 1 on trip 2 on roster 2
      And rave "rules_training_ccr.%num_days_since_last_sim_event%" shall be "30" on leg 1 on trip 2 on roster 2
    #Rule passes as there is 31 days of space between two sim session
      And the rule "rules_training_ccr.min_30_days_required_between_each_sim_session" shall pass on leg 1 on trip 2 on roster 3
      And rave "rules_training_ccr.%num_days_since_last_sim_event%" shall be "31" on leg 1 on trip 2 on roster 3

  @SCENARIO2
  Scenario: Check that rule passes in case of SIM ASSIST or SIM INSTR assignment
    Given a crew member with
      | attribute       | value |
      | employee number | 1     |
      | crew rank       | FC    |
      | title rank      | FC    |
      | region          | SKI   |
      | base            | STO   |
    Given a crew member with
      | attribute       | value |
      | employee number | 2     |
      | crew rank       | FC    |
      | title rank      | FC    |
      | region          | SKI   |
      | base            | STO   |
    Given a crew member with
      | attribute       | value |
      | employee number | 3     |
      | crew rank       | FC    |
      | title rank      | FC    |
      | region          | SKI   |
      | base            | STO   |
    Given a crew member with
      | attribute       | value |
      | employee number | 4     |
      | crew rank       | FC    |
      | title rank      | FC    |
      | region          | SKI   |
      | base            | STO   |

    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+SFI" from 1JAN2018 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+SFE" from 1FEB2018 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+TRI" from 1FEB2018 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+TRE" from 1FEB2018 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035
    Given crew member 1 has document "REC+LPC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1MAY2018 to 30SEP2020 and has qualification "A2"
    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 31MAY2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 30NOV2020

    Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 2 has acqual qualification "ACQUAL+A2+INSTRUCTOR+SFI" from 1JAN2018 to 31DEC2035
    Given crew member 2 has acqual qualification "ACQUAL+A2+INSTRUCTOR+SFE" from 1FEB2018 to 31DEC2035
    Given crew member 2 has acqual qualification "ACQUAL+A2+INSTRUCTOR+TRI" from 1FEB2018 to 31DEC2035
    Given crew member 2 has acqual qualification "ACQUAL+A2+INSTRUCTOR+TRE" from 1FEB2018 to 31DEC2035
    Given crew member 2 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035
    Given crew member 2 has document "REC+OPC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 2 has document "REC+LPC" from 1MAY2018 to 30SEP2020 and has qualification "A2"
    Given crew member 2 has document "REC+OPCA3" from 1APR2018 to 31MAY2020
    Given crew member 2 has document "REC+LPCA3" from 1MAY2018 to 30NOV2020

    Given crew member 3 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 3 has acqual qualification "ACQUAL+A2+INSTRUCTOR+SFI" from 1JAN2018 to 31DEC2035
    Given crew member 3 has acqual qualification "ACQUAL+A2+INSTRUCTOR+SFE" from 1FEB2018 to 31DEC2035
    Given crew member 3 has acqual qualification "ACQUAL+A2+INSTRUCTOR+TRI" from 1FEB2018 to 31DEC2035
    Given crew member 3 has acqual qualification "ACQUAL+A2+INSTRUCTOR+TRE" from 1FEB2018 to 31DEC2035
    Given crew member 3 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035
    Given crew member 3 has document "REC+LPC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 3 has document "REC+OPC" from 1MAY2018 to 30SEP2020 and has qualification "A2"
    Given crew member 3 has document "REC+LPCA3" from 1APR2018 to 31MAY2020
    Given crew member 3 has document "REC+OPCA3" from 1MAY2018 to 30NOV2020

    Given crew member 4 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 4 has acqual qualification "ACQUAL+A2+INSTRUCTOR+SFI" from 1JAN2018 to 31DEC2035
    Given crew member 4 has acqual qualification "ACQUAL+A2+INSTRUCTOR+SFE" from 1FEB2018 to 31DEC2035
    Given crew member 4 has acqual qualification "ACQUAL+A2+INSTRUCTOR+TRI" from 1FEB2018 to 31DEC2035
    Given crew member 4 has acqual qualification "ACQUAL+A2+INSTRUCTOR+TRE" from 1FEB2018 to 31DEC2035
    Given crew member 4 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035
    Given crew member 4 has document "REC+OPC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 4 has document "REC+LPC" from 1MAY2018 to 30SEP2020 and has qualification "A2"
    Given crew member 4 has document "REC+OPCA3" from 1APR2018 to 31MAY2020
    Given crew member 4 has document "REC+LPCA3" from 1MAY2018 to 30NOV2020

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr             |
      | ground | S6   | ARN     | ARN     | 14MAR2020 8:00 | 14MAR2020 12:00 |
      And a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr             |
      | ground | S6   | ARN     | ARN     | 13APR2020 8:00 | 13APR2020 12:00 |

    Given trip 1 is assigned to crew member 1 in position FC
      And trip 2 is assigned to crew member 1 in position FC with attribute TRAINING="SIM ASSIST"

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr             |
      | ground | S6   | ARN     | ARN     | 14MAR2020 8:00 | 14MAR2020 12:00 |
      And a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr             |
      | ground | S6   | ARN     | ARN     | 13APR2020 8:00 | 13APR2020 12:00 |

    Given trip 3 is assigned to crew member 2 in position FC
      And trip 4 is assigned to crew member 2 in position TR with attribute TRAINING="SIM INSTR"

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr             |
      | ground | S6   | ARN     | ARN     | 14MAR2020 8:00 | 14MAR2020 12:00 |
      And a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr             |
      | ground | S6   | ARN     | ARN     | 13APR2020 8:00 | 13APR2020 12:00 |

    Given trip 5 is assigned to crew member 3 in position FC with attribute TRAINING="SIM ASSIST"
      And trip 6 is assigned to crew member 3 in position FC

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr             |
      | ground | Y6   | ARN     | ARN     | 14MAR2020 8:00 | 14MAR2020 12:00 |
      And a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr             |
      | ground | Y6   | ARN     | ARN     | 13APR2020 8:00 | 13APR2020 12:00 |

    Given trip 7 is assigned to crew member 4 in position TR with attribute TRAINING="SIM INSTR"
      And trip 8 is assigned to crew member 4 in position FC

     When I show "crew" in window 1

    #Rule passes for all the cases below as SIM INSTR and SIM ASSIST are not considered as valid sim session for the rule
     Then the rule "rules_training_ccr.min_30_days_required_between_each_sim_session" shall pass on leg 1 on trip 2 on roster 1
      And the rule "rules_training_ccr.min_30_days_required_between_each_sim_session" shall pass on leg 1 on trip 2 on roster 2
      And the rule "rules_training_ccr.min_30_days_required_between_each_sim_session" shall pass on leg 1 on trip 2 on roster 3
      And rave "rules_training_ccr.%num_days_since_last_sim_event%" shall be "12520" on leg 1 on trip 2 on roster 3
      And the rule "rules_training_ccr.min_30_days_required_between_each_sim_session" shall pass on leg 1 on trip 2 on roster 4
      And rave "rules_training_ccr.%num_days_since_last_sim_event%" shall be "12520" on leg 1 on trip 2 on roster 4
