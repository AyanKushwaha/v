Feature: Introduce training attribute ETOPS LIFUS LC

###############
## SKCMS-2545##
###############

Background:
    Given planning period from 01Sep2020 to 30Sep2020
    Given Rostering_FC


################################################################################################################
   @SCENARIO1
   Scenario: Check that trainee and instructor get correct attribute and duty code for LC instructor
   Given a crew member with
        | attribute | value | valid from | valid to |
        | base      | OSL   |            |          |
        | title rank| FP    |            |          |

   Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2020

   Given another crew member with
        | attribute | value | valid from | valid to |
        | base      | OSL   |            |          |
        | title rank| FC    |            |          |
   Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2020
   Given crew member 2 has qualification "POSITION+LCP" from 1JAN2020 to 31DEC2020
   Given crew member 2 has qualification "POSITION+A2NX" from 1JAN2020 to 31DEC2020

   Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | EWR     | 12SEP2020 | 08:00 | 12:00 | SK  | 321    |
        | leg | 0002 | EWR     | OSL     | 12SEP2020 | 13:00 | 20:00 | SK  | 321    |

   Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="ETOPS LIFUS/LC"
   Given trip 1 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="ETOPS LIFUS/LC"


   When I show "crew" in window 1

   Then rave "training.%leg_trainee_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      |  E    |
       | 1   | 1    | 2      |       |
   and rave "training.%leg_instructor_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | ""    |
       | 1   | 1    | 2      | E     |

   and rave "leg.%is_etops_lifus_lc%" values shall be
       | leg | trip | roster | value  |
       | 1   | 1    | 1      | "True" |
       | 1   | 1    | 2      | "False"|

################################################################################################################

   @SCENARIO2
   Scenario: Check that trainee and instructor get correct attribute and duty code for LIFUS instructor
   Given a crew member with
        | attribute | value | valid from | valid to |
        | base      | OSL   |            |          |
        | title rank| FP    |            |          |

   Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2020

   Given another crew member with
        | attribute | value | valid from | valid to |
        | base      | OSL   |            |          |
        | title rank| FC    |            |          |
   Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2020
   Given crew member 2 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 01JAN2020 to 31DEC2020
   Given crew member 2 has qualification "POSITION+A2NX" from 1JAN2020 to 31DEC2020

   Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | EWR     | 12SEP2020 | 08:00 | 12:00 | SK  | 321    |
        | leg | 0002 | EWR     | OSL     | 12SEP2020 | 13:00 | 20:00 | SK  | 321    |

   Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="ETOPS LIFUS/LC"
   Given trip 1 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="ETOPS LIFUS/LC"


   When I show "crew" in window 1


   Then rave "training.%leg_trainee_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      |  E    |
       | 1   | 1    | 2      |       |
   and rave "training.%leg_instructor_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | ""    |
       | 1   | 1    | 2      | E     |

   and rave "leg.%is_etops_lifus_lc%" values shall be
       | leg | trip | roster | value  |
       | 1   | 1    | 1      | "True" |
       | 1   | 1    | 2      | "False"|

##############################################################################################################
   @SCENARIO3
   Scenario: Check that trainee and instructor get correct attribute and duty code when trainee is FC

   Given a crew member with
        | attribute | value | valid from | valid to |
        | base      | OSL   |            |          |
        | title rank| FC    |            |          |

   Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2020

   Given another crew member with
        | attribute | value | valid from | valid to |
        | base      | OSL   |            |          |
        | title rank| FC    |            |          |
   Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2020
   Given crew member 2 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 01JAN2020 to 31DEC2020
   Given crew member 2 has qualification "POSITION+A2NX" from 1JAN2020 to 31DEC2020

   Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | EWR     | 12SEP2020 | 08:00 | 12:00 | SK  | 321    |
        | leg | 0002 | EWR     | OSL     | 12SEP2020 | 13:00 | 20:00 | SK  | 321    |

   Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="ETOPS LIFUS/LC"
   Given trip 1 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="ETOPS LIFUS/LC"

   When I show "crew" in window 1

   Then rave "training.%leg_trainee_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      |   EL  |
       | 1   | 1    | 2      |       |
   and rave "training.%leg_instructor_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | ""    |
       | 1   | 1    | 2      | E     |

   and rave "leg.%is_etops_lifus_lc%" values shall be
       | leg | trip | roster | value  |
       | 1   | 1    | 1      | "True" |
       | 1   | 1    | 2      | "False"|

   ###################
    # JIRA - SKCMS-2722
    ###################
   @SCENARIO4
   Scenario: Check that trainee in FP Position and instructor get correct attribute and duty code for LC instructor
   Given a crew member with
        | attribute | value | valid from | valid to |
        | base      | OSL   |            |          |
        | title rank| FP    |            |          |

   Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2020

   Given another crew member with
        | attribute | value | valid from | valid to |
        | base      | OSL   |            |          |
        | title rank| FC    |            |          |
   Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2020
   Given crew member 2 has qualification "POSITION+LCP" from 1JAN2020 to 31DEC2020
   Given crew member 2 has qualification "POSITION+A2NX" from 1JAN2020 to 31DEC2020

   Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | EWR     | 12SEP2020 | 08:00 | 12:00 | SK  | 321    |
        | leg | 0002 | EWR     | OSL     | 12SEP2020 | 13:00 | 20:00 | SK  | 321    |

   Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="ETOPS LIFUS/LC"
   Given trip 1 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="ETOPS LIFUS/LC"


   When I show "crew" in window 1

   Then rave "training.%leg_trainee_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      |  E   |
       | 1   | 1    | 2      |       |
   and rave "training.%leg_instructor_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | ""    |
       | 1   | 1    | 2      | E     |

   and rave "leg.%is_etops_lifus_lc%" values shall be
       | leg | trip | roster | value  |
       | 1   | 1    | 1      | "True" |
       | 1   | 1    | 2      | "False"|
Then the rule "rules_training_ccr.comp_max_nr_crew_performing_training_type_on_flight_ALL" shall pass on leg 1 on trip 1 on roster 1
Then the rule "rules_training_ccr.comp_trainee_assigned_in_correct_position_ALL" shall pass on leg 1 on trip 1 on roster 1

@SCENARIO5
   Scenario: Check that trainee in FP and instructor get correct attribute and duty code when trainee is FC

   Given a crew member with
        | attribute | value | valid from | valid to |
        | base      | OSL   |            |          |
        | title rank| FC    |            |          |

   Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2020

   Given another crew member with
        | attribute | value | valid from | valid to |
        | base      | OSL   |            |          |
        | title rank| FC    |            |          |
   Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2020
   Given crew member 2 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 01JAN2020 to 31DEC2020
   Given crew member 2 has qualification "POSITION+A2NX" from 1JAN2020 to 31DEC2020

   Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | EWR     | 12SEP2020 | 08:00 | 12:00 | SK  | 321    |
        | leg | 0002 | EWR     | OSL     | 12SEP2020 | 13:00 | 20:00 | SK  | 321    |

   Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="ETOPS LIFUS/LC"
   Given trip 1 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="ETOPS LIFUS/LC"

   When I show "crew" in window 1

   Then rave "training.%leg_trainee_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      |  EL   |
       | 1   | 1    | 2      |       |
   and rave "training.%leg_instructor_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | ""    |
       | 1   | 1    | 2      | E     |

   and rave "leg.%is_etops_lifus_lc%" values shall be
       | leg | trip | roster | value  |
       | 1   | 1    | 1      | "True" |
       | 1   | 1    | 2      | "False"|
Then the rule "rules_training_ccr.comp_max_nr_crew_performing_training_type_on_flight_ALL" shall pass on leg 1 on trip 1 on roster 1
Then the rule "rules_training_ccr.comp_trainee_assigned_in_correct_position_ALL" shall pass on leg 1 on trip 1 on roster 1

@SCENARIO6
   Scenario: Check that trainee in both FU and FP Position and instructor get correct attribute and duty code.

   Given a crew member with
        | attribute | value | valid from | valid to |
        | base      | OSL   |            |          |
        | title rank| FC    |            |          |

   Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2020

   Given another crew member with
        | attribute | value | valid from | valid to |
        | base      | OSL   |            |          |
        | title rank| FC    |            |          |
   Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2020
   Given crew member 2 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 01JAN2020 to 31DEC2020
   Given crew member 2 has qualification "POSITION+A2NX" from 1JAN2020 to 31DEC2020

   Given another crew member with
        | attribute | value | valid from | valid to |
        | base      | OSL   |            |          |
        | title rank| FC    |            |          |

   Given crew member 3 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2020

   Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | EWR     | 12SEP2020 | 08:00 | 12:00 | SK  | 321    |
        | leg | 0002 | EWR     | OSL     | 12SEP2020 | 13:00 | 20:00 | SK  | 321    |

   Given trip 1 is assigned to crew member 1 in position FU with attribute TRAINING="ETOPS LIFUS/LC"
   Given trip 1 is assigned to crew member 3 in position FP with attribute TRAINING="ETOPS LIFUS/LC"
   Given trip 1 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="ETOPS LIFUS/LC"

   When I show "crew" in window 1

   Then rave "training.%leg_trainee_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      |  ELL  |
       | 1   | 1    | 2      |       |
   and rave "training.%leg_instructor_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | ""    |
       | 1   | 1    | 2      | E     |

   and rave "leg.%is_etops_lifus_lc%" values shall be
       | leg | trip | roster | value  |
       | 1   | 1    | 1      | "True" |
       | 1   | 1    | 2      | "False"|
   
   Then the rule "rules_training_ccr.comp_max_nr_crew_performing_training_type_on_flight_ALL" shall pass on leg 1 on trip 1 on roster 1
   Then the rule "rules_training_ccr.comp_trainee_assigned_in_correct_position_ALL" shall pass on leg 1 on trip 1 on roster 1

@SCENARIO7
   Scenario: Check that trainee in both FU and FP Position and instructor get correct code.

   Given a crew member with
        | attribute | value | valid from | valid to |
        | base      | OSL   |            |          |
        | title rank| FP    |            |          |

   Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2020

   Given another crew member with
        | attribute | value | valid from | valid to |
        | base      | OSL   |            |          |
        | title rank| FC    |            |          |
   Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2020
   Given crew member 2 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 01JAN2020 to 31DEC2020
   Given crew member 2 has qualification "POSITION+A2NX" from 1JAN2020 to 31DEC2020

   Given another crew member with
        | attribute | value | valid from | valid to |
        | base      | OSL   |            |          |
        | title rank| FP    |            |          |

   Given crew member 3 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2020

   Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | EWR     | 12SEP2020 | 08:00 | 12:00 | SK  | 321    |
        | leg | 0002 | EWR     | OSL     | 12SEP2020 | 13:00 | 20:00 | SK  | 321    |

   Given trip 1 is assigned to crew member 1 in position FU with attribute TRAINING="ETOPS LIFUS/LC"
   Given trip 1 is assigned to crew member 3 in position FP with attribute TRAINING="ETOPS LIFUS/LC"
   Given trip 1 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="ETOPS LIFUS/LC"

   When I show "crew" in window 1

   Then rave "training.%leg_trainee_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      |  EL  |
       | 1   | 1    | 2      |       |
   and rave "training.%leg_instructor_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | ""    |
       | 1   | 1    | 2      | E     |

   and rave "leg.%is_etops_lifus_lc%" values shall be
       | leg | trip | roster | value  |
       | 1   | 1    | 1      | "True" |
       | 1   | 1    | 2      | "False"|
   
   Then the rule "rules_training_ccr.comp_max_nr_crew_performing_training_type_on_flight_ALL" shall pass on leg 1 on trip 1 on roster 1
   Then the rule "rules_training_ccr.comp_trainee_assigned_in_correct_position_ALL" shall pass on leg 1 on trip 1 on roster 1
   
               

