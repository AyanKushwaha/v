@FD @PC @OPC @TRAINING
Feature: Test PC and OPC

   Background:
     Given Tracking
     Given planning period from 1DEC2018 to 31JAN2019

   #################
   # JIRA - SKAM-822  
   #################
   @TRACKING @SCENARIO1
   Scenario: Check that PC is within training evaluation period spring starts in December


   Given a crew member with homebase "STO"

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0001 | ARN     | LHR     | 26DEC2018 | 10:00 | 11:00 | SK  | 320    |
   | leg | 0002 | LHR     | ARN     | 26DEC2018 | 12:00 | 13:00 | SK  | 320    |

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date     | dep   | arr   | car | ac_typ |
   | leg | 0001 | ARN     | LHR     | 3JAN2019 | 10:00 | 11:00 | SK  | 320    |
   | leg | 0002 | LHR     | ARN     | 3JAN2019 | 12:00 | 13:00 | SK  | 320    |

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0001 | ARN     | LHR     | 12JAN2019 | 10:00 | 11:00 | SK  | 320    |
   | leg | 0002 | LHR     | ARN     | 12JAN2019 | 12:00 | 13:00 | SK  | 320    |

   Given trip 1 is assigned to crew member 1
   Given trip 2 is assigned to crew member 1
   Given trip 3 is assigned to crew member 1

   When I show "crew" in window 1
   and I set parameter "training.%first_valid_time_for_spring_training%" to "29DEC2018"
   and I set parameter "training.%last_valid_time_for_spring_training%" to "11JAN2019"

   Then rave "rules_qual_ccr.%within_spring_training_eval_period%" shall be "False" on leg 1 on trip 1 on roster 1
   and rave "rules_qual_ccr.%within_spring_training_eval_period%" shall be "True" on leg 1 on trip 2 on roster 1
   and rave "rules_qual_ccr.%within_spring_training_eval_period%" shall be "False" on leg 1 on trip 3 on roster 1


   #################
   # JIRA - SKAM-822  
   #################
   @TRACKING @SCENARIO2
   Scenario: Check that PC is within training evaluation period spring starts in January


   Given a crew member with homebase "STO"

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0001 | ARN     | LHR     | 26DEC2018 | 10:00 | 11:00 | SK  | 320    |
   | leg | 0002 | LHR     | ARN     | 26DEC2018 | 12:00 | 13:00 | SK  | 320    |

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date     | dep   | arr   | car | ac_typ |
   | leg | 0001 | ARN     | LHR     | 3JAN2019 | 10:00 | 11:00 | SK  | 320    |
   | leg | 0002 | LHR     | ARN     | 3JAN2019 | 12:00 | 13:00 | SK  | 320    |

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0001 | ARN     | LHR     | 12JAN2019 | 10:00 | 11:00 | SK  | 320    |
   | leg | 0002 | LHR     | ARN     | 12JAN2019 | 12:00 | 13:00 | SK  | 320    |

   Given trip 1 is assigned to crew member 1
   Given trip 2 is assigned to crew member 1
   Given trip 3 is assigned to crew member 1

   When I show "crew" in window 1
   and I set parameter "training.%first_valid_time_for_spring_training%" to "1JAN2018"
   and I set parameter "training.%last_valid_time_for_spring_training%" to "11JAN2019"

   Then rave "rules_qual_ccr.%within_spring_training_eval_period%" shall be "False" on leg 1 on trip 1 on roster 1
   and rave "rules_qual_ccr.%within_spring_training_eval_period%" shall be "True" on leg 1 on trip 2 on roster 1
   and rave "rules_qual_ccr.%within_spring_training_eval_period%" shall be "False" on leg 1 on trip 3 on roster 1
