@PLANNING @ROSTERING @ALL @FD
Feature: Rule checks that FP are in normal composition during Skill test training activity.
This feature considers planning system

Background:
  Given planning period from 1Dec2018 to 31Dec2018 
  
  ##############################################################################
  @FD_PASS_1
  Scenario: Case passes if FP is assigned FP at captain upgrade during skill test
  
  Given a crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | STO     |             |           |
  | title rank | FP      |             |           |
  | region     | SKS     |             |           |
  Given crew member 1 has restriction "TRAINING+CAPT" from 1DEC2018 to 31DEC2018
  
  Given a trip with the following activities
  | act    | code | dep stn | arr stn | date      | dep   | arr   |
  | ground | S2   | OSL     | OSL     | 9Dec2018  | 00:00 | 23:59 |


  Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="SKILL TEST"
  
  When I show "crew" in window 1
  When I load ruleset "rule_set_jcr_fc"
  When I set parameter "fundamental.%start_para%" to "1DEC2018 00:00"
  When I set parameter "fundamental.%end_para%" to "31DEC2018 00:00"
  Then the rule "rules_training_ccr.trng_normal_crew_comp_at_skilltest_cdr_upgrade" shall pass on leg 1 on trip 1 on roster 1
  and rave "crew.%has_restr_training_capt%(9DEC2018)" shall be "True"
  and rave "training.%crew_on_skill_test%" shall be "True"
  
  ##############################################################################
  @FD_PASS_2
  Scenario: Case passes if FP is assigned FP at captain upgrade during skill test. Crew shall be SKD
  
  Given a crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | CPH     |             |           |
  | title rank | FP      |             |           |
  | region     | SKD     |             |           |
  Given crew member 1 has restriction "TRAINING+CAPT" from 1DEC2018 to 31DEC2018
  
  Given a trip with the following activities
  | act    | code | dep stn | arr stn | date      | dep   | arr   |
  | ground | S2   | CPH     | CPH     | 9Dec2018  | 00:00 | 23:59 |


  Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="SKILL TEST"
  
  When I show "crew" in window 1
  When I load ruleset "rule_set_jcr_fc"
  When I set parameter "fundamental.%start_para%" to "1DEC2018 00:00"
  When I set parameter "fundamental.%end_para%" to "31DEC2018 00:00"
  Then the rule "rules_training_ccr.trng_normal_crew_comp_at_skilltest_cdr_upgrade" shall pass on leg 1 on trip 1 on roster 1
  and rave "crew.%has_restr_training_capt%(9DEC2018)" shall be "True"
  and rave "training.%crew_on_skill_test%" shall be "True"
  
  ##############################################################################
  @FD_PASS_3
  Scenario: Case passes if FP is assigned FP at captain upgrade during skill test. Crew shall be SKN
  
  Given a crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | OSL     |             |           |
  | title rank | FP      |             |           |
  | region     | SKN     |             |           |
  Given crew member 1 has restriction "TRAINING+CAPT" from 1DEC2018 to 31DEC2018
  
  Given a trip with the following activities
  | act    | code | dep stn | arr stn | date      | dep   | arr   |
  | ground | S2   | OSL     | OSL     | 9Dec2018  | 00:00 | 23:59 |


  Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="SKILL TEST"
  
  When I show "crew" in window 1
  When I load ruleset "rule_set_jcr_fc"
  When I set parameter "fundamental.%start_para%" to "1DEC2018 00:00"
  When I set parameter "fundamental.%end_para%" to "31DEC2018 00:00"
  Then the rule "rules_training_ccr.trng_normal_crew_comp_at_skilltest_cdr_upgrade" shall pass on leg 1 on trip 1 on roster 1
  and rave "crew.%has_restr_training_capt%(9DEC2018)" shall be "True"
  and rave "training.%crew_on_skill_test%" shall be "True"
  
  ##############################################################################
  @FD_PASS_4
  Scenario: Case passes if FC is assigned FP without captain upgrade during skill test. Crew shall be SKN
  
  Given a crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | OSL     |             |           |
  | title rank | FC      |             |           |
  | region     | SKN     |             |           |
  
  
  Given a trip with the following activities
  | act    | code | dep stn | arr stn | date      | dep   | arr   |
  | ground | S2   | OSL     | OSL     | 9Dec2018  | 00:00 | 23:59 |


  Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="SKILL TEST"
  
  When I show "crew" in window 1
  When I load ruleset "rule_set_jcr_fc"
  When I set parameter "fundamental.%start_para%" to "1DEC2018 00:00"
  When I set parameter "fundamental.%end_para%" to "31DEC2018 00:00"
  Then the rule "rules_training_ccr.trng_normal_crew_comp_at_skilltest_cdr_upgrade" shall pass on leg 1 on trip 1 on roster 1
  and rave "crew.%has_restr_training_capt%(9DEC2018)" shall be "False"
  and rave "training.%crew_on_skill_test%" shall be "True"
  
  ##############################################################################
  @FD_PASS_5
  Scenario: Case passes if FC is assigned FP at captain upgrade not uring skill test. Crew shall be SKN
  
  Given a crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | OSL     |             |           |
  | title rank | FC      |             |           |
  | region     | SKN     |             |           |
  Given crew member 1 has restriction "TRAINING+CAPT" from 1DEC2018 to 31DEC2018
  
  Given a trip with the following activities
  | act    | code | dep stn | arr stn | date      | dep   | arr   |
  | ground | S2   | OSL     | OSL     | 9Dec2018  | 00:00 | 23:59 |

  
  When I show "crew" in window 1
  When I load ruleset "rule_set_jcr_fc"
  When I set parameter "fundamental.%start_para%" to "1DEC2018 00:00"
  When I set parameter "fundamental.%end_para%" to "31DEC2018 00:00"
  Then the rule "rules_training_ccr.trng_normal_crew_comp_at_skilltest_cdr_upgrade" shall pass on leg 1 on trip 1 on roster 1
  and rave "crew.%has_restr_training_capt%(9DEC2018)" shall be "True"
  and rave "training.%crew_on_skill_test%" shall be "False"
  
  ##############################################################################
  @FD_FAIL_1
  Scenario: Case fails if FC is assigned FP at captain upgrade during skill test. 
  
  Given a crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | STO     |             |           |
  | title rank | FC      |             |           |
  | region     | SKS     |             |           |
  Given crew member 1 has restriction "TRAINING+CAPT" from 1DEC2018 to 31DEC2018
  
  Given a trip with the following activities
  | act    | code | dep stn | arr stn | date      | dep   | arr   |
  | ground | S2   | ARN     | ARN     | 9Dec2018  | 00:00 | 23:59 |

  Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="SKILL TEST"
  
  When I show "crew" in window 1
  When I load ruleset "rule_set_jcr_fc"
  When I set parameter "fundamental.%start_para%" to "1DEC2018 00:00"
  When I set parameter "fundamental.%end_para%" to "31DEC2018 00:00"
  Then the rule "rules_training_ccr.trng_normal_crew_comp_at_skilltest_cdr_upgrade" shall fail on leg 1 on trip 1 on roster 1
  and rave "crew.%has_restr_training_capt%(9DEC2018)" shall be "True"
  and rave "training.%crew_on_skill_test%" shall be "True"
  
  ##############################################################################
  @FD_FAIL_2
  Scenario: Case fails if FC is assigned FP at captain upgrade during skill test. Crew shall be SKD
  
  Given a crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | CPH     |             |           |
  | title rank | FC      |             |           |
  | region     | SKD     |             |           |
  Given crew member 1 has restriction "TRAINING+CAPT" from 1DEC2018 to 31DEC2018
  
  Given a trip with the following activities
  | act    | code | dep stn | arr stn | date      | dep   | arr   |
  | ground | S2   | CPH     | CPH     | 9Dec2018  | 00:00 | 23:59 |

  Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="SKILL TEST"
  
  When I show "crew" in window 1
  When I load ruleset "rule_set_jcr_fc"
  When I set parameter "fundamental.%start_para%" to "1DEC2018 00:00"
  When I set parameter "fundamental.%end_para%" to "31DEC2018 00:00"
  Then the rule "rules_training_ccr.trng_normal_crew_comp_at_skilltest_cdr_upgrade" shall fail on leg 1 on trip 1 on roster 1
  and rave "crew.%has_restr_training_capt%(9DEC2018)" shall be "True"
  and rave "training.%crew_on_skill_test%" shall be "True"
  
  ##############################################################################
  @FD_FAIL_1
  Scenario: Case fails if FC is assigned FP at captain upgrade during skill test. Crew shall be SKN
  
  Given a crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | OSL     |             |           |
  | title rank | FC      |             |           |
  | region     | SKN     |             |           |
  Given crew member 1 has restriction "TRAINING+CAPT" from 1DEC2018 to 31DEC2018
  
  Given a trip with the following activities
  | act    | code | dep stn | arr stn | date      | dep   | arr   |
  | ground | S2   | OSL     | OSL     | 9Dec2018  | 00:00 | 23:59 |

  Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="SKILL TEST"
  
  When I show "crew" in window 1
  When I load ruleset "rule_set_jcr_fc"
  When I set parameter "fundamental.%start_para%" to "1DEC2018 00:00"
  When I set parameter "fundamental.%end_para%" to "31DEC2018 00:00"
  Then the rule "rules_training_ccr.trng_normal_crew_comp_at_skilltest_cdr_upgrade" shall fail on leg 1 on trip 1 on roster 1
  and rave "crew.%has_restr_training_capt%(9DEC2018)" shall be "True"
  and rave "training.%crew_on_skill_test%" shall be "True"