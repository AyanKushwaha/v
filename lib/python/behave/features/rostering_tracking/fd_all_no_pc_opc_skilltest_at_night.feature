@JCRT @TRAINING @ALL @FD @SKCMS-798
Feature: Rule checks that PC/OPC and Skill test activitites are not performed during night (0000-0515)

  ##############################################################################
  # Notes:
  #  By default checkin/briefing time is 2h before the leg,
  #  checkout/debriefing is 1h after the leg.
  ##############################################################################
  Background:
    Given planning period from 1JAN2019 to 3JAN2019


  ##############################################################################
  @PASS_1
  Scenario: Rule passes on OPC starting after night

    Given a crew member with homebase "STO"

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | S2   | ARN     | ARN     | 2jan2019  | 06:15 | 10:00 |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
    When I set parameter "fundamental.%end_para%" to "3JAN2019 00:00"

    Then rave "rules_indust_ccr.%trng_no_pc_opc_skilltest_at_night_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    Then the rule "rules_indust_ccr.trng_no_pc_opc_skilltest_at_night_FC" shall pass on leg 1 on trip 1 on roster 1

  ##############################################################################
  @PASS_2
  Scenario: Rule passes on PC ending before night
    Given a crew member with homebase "STO"

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | Y2   | ARN     | ARN     | 1jan2019  | 17:00 | 22:00 |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
    When I set parameter "fundamental.%end_para%" to "3JAN2019 00:00"

    Then rave "rules_indust_ccr.%trng_no_pc_opc_skilltest_at_night_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    Then the rule "rules_indust_ccr.trng_no_pc_opc_skilltest_at_night_FC" shall pass on leg 1 on trip 1 on roster 1

  ##############################################################################
  @PASS_3
  Scenario: Rule passes on skill test at day
    Given a crew member with homebase "STO"

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | S3   | ARN     | ARN     | 1jan2019  | 12:00 | 16:00 |

    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="SKILL TEST"

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
    When I set parameter "fundamental.%end_para%" to "3JAN2019 00:00"

    Then rave "rules_indust_ccr.%trng_no_pc_opc_skilltest_at_night_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    Then the rule "rules_indust_ccr.trng_no_pc_opc_skilltest_at_night_FC" shall pass on leg 1 on trip 1 on roster 1


  ##############################################################################
  
  @PASS_4
  Scenario: Rule passes on skill test ending exactly 00:00 local time
    Given a crew member with homebase "STO"

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | Y2   | HEL     | HEL     | 1jan2019  | 12:00 | 21:00 |

    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="SKILL TEST"

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
    When I set parameter "fundamental.%end_para%" to "3JAN2019 00:00"

    Then rave "rules_indust_ccr.%trng_no_pc_opc_skilltest_at_night_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    Then the rule "rules_indust_ccr.trng_no_pc_opc_skilltest_at_night_FC" shall pass on leg 1 on trip 1 on roster 1
    and rave "rules_indust_ccr.%activity_end_time%" shall be "02JAN2019 00:00" on leg 1 on trip 1 on roster 1


  ##############################################################################
  
  @PASS_5
  Scenario: Rule passes on skill test starting exactly 05:15 local time 
    Given a crew member with homebase "STO"

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | Y2   | HEL     | HEL     | 1jan2019  | 05:15 | 13:00 |

    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="SKILL TEST"

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
    When I set parameter "fundamental.%end_para%" to "3JAN2019 00:00"

    Then rave "rules_indust_ccr.%trng_no_pc_opc_skilltest_at_night_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    Then the rule "rules_indust_ccr.trng_no_pc_opc_skilltest_at_night_FC" shall pass on leg 1 on trip 1 on roster 1
    and rave "rules_indust_ccr.%activity_start_time%" shall be "01JAN2019 05:15" on leg 1 on trip 1 on roster 1


  ##############################################################################
  @FAIL_1
  Scenario: Rule fails on OPC starting at night
    Given a crew member with homebase "STO"

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | S2   | ARN     | ARN     | 2jan2019  | 04:14 | 09:00 |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
    When I set parameter "fundamental.%end_para%" to "3JAN2019 00:00"

    Then rave "rules_indust_ccr.%trng_no_pc_opc_skilltest_at_night_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    Then the rule "rules_indust_ccr.trng_no_pc_opc_skilltest_at_night_FC" shall fail on leg 1 on trip 1 on roster 1

  ##############################################################################
  @FAIL_2
  Scenario: Rule fails on PC ending at night
    Given a crew member with homebase "STO"

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | Y2   | ARN     | ARN     | 1jan2019  | 18:00 | 23:01 |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
    When I set parameter "fundamental.%end_para%" to "3JAN2019 00:00"

    Then rave "rules_indust_ccr.%trng_no_pc_opc_skilltest_at_night_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    Then the rule "rules_indust_ccr.trng_no_pc_opc_skilltest_at_night_FC" shall fail on leg 1 on trip 1 on roster 1

  ##############################################################################
  @FAIL_3
  Scenario: Rule fails on skill test on night time
    Given a crew member with homebase "STO"

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | Y3   | ARN     | ARN     | 2jan2019  | 01:00 | 03:00 |

    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="SKILL TEST"

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
    When I set parameter "fundamental.%end_para%" to "3JAN2019 00:00"

    Then rave "rules_indust_ccr.%trng_no_pc_opc_skilltest_at_night_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    Then the rule "rules_indust_ccr.trng_no_pc_opc_skilltest_at_night_FC" shall fail on leg 1 on trip 1 on roster 1

  ##############################################################################
  @FAIL_4
  Scenario: Rule fails on OPC with check-in at night
    Given a crew member with homebase "STO"

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | S9   | ARN     | ARN     | 2jan2019  | 06:14 | 10:00 |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
    When I set parameter "fundamental.%end_para%" to "3JAN2019 00:00"

    Then rave "rules_indust_ccr.%trng_no_pc_opc_skilltest_at_night_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    Then the rule "rules_indust_ccr.trng_no_pc_opc_skilltest_at_night_FC" shall fail on leg 1 on trip 1 on roster 1

  ##############################################################################
  @FAIL_5
  Scenario: Rule fails on PC with check-out at night
    Given a crew member with homebase "STO"

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | Z9   | ARN     | ARN     | 1jan2019  | 17:00 | 22:01 |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
    When I set parameter "fundamental.%end_para%" to "3JAN2019 00:00"

    Then rave "rules_indust_ccr.%trng_no_pc_opc_skilltest_at_night_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    Then the rule "rules_indust_ccr.trng_no_pc_opc_skilltest_at_night_FC" shall fail on leg 1 on trip 1 on roster 1
    
    ##############################################################################
    @FAIL_6
    Scenario: Rule fails on PC with check-out at night local time
      Given a crew member with homebase "STO"
  
      Given a trip with the following activities
      | act    | code | dep stn | arr stn | date      | dep   | arr   |
      | ground | Z9   | HEL     | HEL     | 1jan2019  | 17:00 | 22:01 |
  
      Given trip 1 is assigned to crew member 1
  
      When I show "crew" in window 1
      When I load ruleset "Rostering_FC"
      When I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
      When I set parameter "fundamental.%end_para%" to "3JAN2019 00:00"
  
      Then rave "rules_indust_ccr.%trng_no_pc_opc_skilltest_at_night_valid%" shall be "True" on leg 1 on trip 1 on roster 1
      Then the rule "rules_indust_ccr.trng_no_pc_opc_skilltest_at_night_FC" shall fail on leg 1 on trip 1 on roster 1
      
      ##############################################################################
      @FAIL_7
      Scenario: Rule fails on PC with check-in at night local time
        Given a crew member with homebase "STO"
    
        Given a trip with the following activities
        | act    | code | dep stn | arr stn | date      | dep   | arr   |
        | ground | Z9   | HEL     | HEL     | 1jan2019  | 05:14 | 13:00 |
    
        Given trip 1 is assigned to crew member 1
    
        When I show "crew" in window 1
        When I load ruleset "Rostering_FC"
        When I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
        When I set parameter "fundamental.%end_para%" to "3JAN2019 00:00"
    
        Then rave "rules_indust_ccr.%trng_no_pc_opc_skilltest_at_night_valid%" shall be "True" on leg 1 on trip 1 on roster 1
        Then the rule "rules_indust_ccr.trng_no_pc_opc_skilltest_at_night_FC" shall fail on leg 1 on trip 1 on roster 1
        
        ##############################################################################
        @FAIL_8
        Scenario: Rule fails on skill test with check-out at night local time
          Given a crew member with homebase "STO"
      
          Given a trip with the following activities
          | act    | code | dep stn | arr stn | date      | dep   | arr   |
          | ground | S2   | HEL     | HEL     | 1jan2019  | 17:00 | 22:01 |
      
          Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="SKILL TEST"
      
          When I show "crew" in window 1
          When I load ruleset "Rostering_FC"
          When I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
          When I set parameter "fundamental.%end_para%" to "3JAN2019 00:00"
      
          Then rave "rules_indust_ccr.%trng_no_pc_opc_skilltest_at_night_valid%" shall be "True" on leg 1 on trip 1 on roster 1
          Then the rule "rules_indust_ccr.trng_no_pc_opc_skilltest_at_night_FC" shall fail on leg 1 on trip 1 on roster 1
          
        ##############################################################################
        @FAIL_9
        Scenario: Rule fails on skill test with check-in at night local time
          Given a crew member with homebase "STO"
      
          Given a trip with the following activities
          | act    | code | dep stn | arr stn | date      | dep   | arr   |
          | ground | S2   | HEL     | HEL     | 1jan2019  | 05:14 | 13:00 |
      
          Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="SKILL TEST"
      
          When I show "crew" in window 1
          When I load ruleset "Rostering_FC"
          When I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
          When I set parameter "fundamental.%end_para%" to "3JAN2019 00:00"
      
          Then rave "rules_indust_ccr.%trng_no_pc_opc_skilltest_at_night_valid%" shall be "True" on leg 1 on trip 1 on roster 1
          Then the rule "rules_indust_ccr.trng_no_pc_opc_skilltest_at_night_FC" shall fail on leg 1 on trip 1 on roster 1


