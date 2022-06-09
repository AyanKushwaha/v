# Author: Kristoffer Thun
# Developed for JIRA: SKWD-377

@PLANNING @ROSTERING @ALL @FD @TRACKING
Feature: Crew who has had a Skill Test for a Typerating course within the AST period, shall not be included.

Background:
  Given planning period from 1Dec2018 to 31Dec2018
  Given Rostering_FC

    Given table property is overridden with the following
      | id                    | validfrom | validto   | value_abs |
      | ast_period_start_A3A4 | 1JAN1986  | 31DEC2035 | 1OCT2018  |
      | ast_period_end_A3A4   | 1JAN1986  | 31DEC2035 | 1JUL2019  |


  ##############################################################################
  @scenario1
  Scenario: Case passes if FC is not assigned to AST or Skill Test during AST period.

  Given a trip with the following activities
  | act    | code | dep stn | arr stn | date      | dep   | arr   |
  | ground | s3   | ARN     | ARN     | 07DEC2018 | 10:00 | 11:00 |

  Given a crew member with
  | attribute       | value     | valid from | valid to |
  | base            | ARN       |            |          |
  | title rank      | FC        |            |          |
  | region          | SKS       |            |          |

  Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

  When I show "crew" in window 1
  Then rave "training.%needs_ast%" shall be "True" on leg 1 on trip 1 on roster 1

      ##############################################################################
  @scenario2
  Scenario: Case should return False if FC is assigned to SKILL TEST during AST period.

  Given a trip with the following activities
  | act    | code | dep stn | arr stn | date
  | ground | S6   | ARN     | ARN     | 12DEC2018

  Given table crew_training_need additionally contains the following
   | crew            | part | course          | validfrom | validto    |
   | crew member 1   | 1    |CONV TYPERATING | 1Jan1986  | 31Dec2035   |


   Given a crew member with
  | attribute       | value     | valid from | valid to |
  | base            | ARN       |            |          |
  | title rank      | FC        |            |          |
  | region          | SKS       |            |          |

  Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035
  
  Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="SKILL TEST"

  When I show "crew" in window 1
  Then rave "training.%needs_ast%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%has_skill_test_in_ast_period%" shall be "True"


      ##############################################################################
  @scenario3
  Scenario: Case should return False if FC is assigned to AST during AST period.

  Given a trip with the following activities
  | act    | code | dep stn | arr stn | date
  | ground | K6   | ARN     | ARN     | 02DEC2018


  Given a crew member with
  | attribute       | value     | valid from | valid to |
  | base            | ARN       |            |          |
  | title rank      | FC        |            |          |
  | region          | SKS       |            |          |

  Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

  Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="AST"

  When I show "crew" in window 1
  Then rave "training.%needs_ast%" shall be "False" on leg 1 on trip 1 on roster 1
