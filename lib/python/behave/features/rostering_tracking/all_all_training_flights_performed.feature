Feature: Test that training flights are performed

    Background: Set up
      Given table ac_qual_map additionally contains the following
        | ac_type | aoc | ac_qual_fc | ac_qual_cc |
        | 35X     | SK  | A5         | AL         |

    @SCENARIO_1 @planning
    Scenario: FAM FLT activities are detected in roster and training log and they are considered performed if training need has completion date
       Given planning period from 1MAY2019 to 1JUN2019

       Given a crew member with
       | attribute  | value  | valid from | valid to  |
       | base       | STO    |            |           |
       | title rank | FC     |            |           |
       | region     | SKS    |            |           |

       Given crew member 1 has qualification "ACQUAL+A5" from 1FEB2019 to 31DEC2035

       Given a trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
         | leg | 0001 | OSL     | CPH     | 01MAY2019 | 10:00 | 11:00 | SK  | 35X    |
         | leg | 0002 | CPH     | OSL     | 01MAY2019 | 12:00 | 13:00 | SK  | 35X    |
       Given trip 1 is assigned to crew member 1 in position FC

       Given table crew_training_log additionally contains the following
         | crew          | typ     | code | tim            |
         | crew member 1 | FAM FLT | A5   | 4APR2019 12:22 |

       Given a trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
         | leg | 0001 | OSL     | CPH     | 02MAY2019 | 10:00 | 11:00 | SK  | 35X    |
         | leg | 0002 | CPH     | OSL     | 02MAY2019 | 12:00 | 13:00 | SK  | 35X    |
       Given trip 2 is assigned to crew member 1 in position FC with attribute TRAINING="FAM FLT"

       Given table crew_training_need additionally contains the following
         | crew          | part | validfrom | validto  | course   | attribute  | flights | maxdays | acqual | completion |
         | crew member 1 | 1    | 4FEB2019  | 8MAY2019 | CTR-A3A5 | FAM FLT    | 2       | 0       | A5     | 2MAY2019   |

       When I show "crew" in window 1
       and I load rule set "Rostering_FC"
       and I set parameter "fundamental.%start_para%" to "1MAY2019"
       and I set parameter "fundamental.%end_para%" to "1JUN2019"

       Then the rule "rules_qual_ccr.trng_all_training_flights_performed_all" shall pass on leg 1 on trip 1 on roster 1
       and rave "training.%nr_acts_of_type_and_code_in_ival%(\"FAM FLT\",\"A5\",4FEB2019,8MAY2019)" shall be "3"


    @SCENARIO_2 @tracking
    Scenario: No FAM FLT activities are detected in roster and training log and they are not considered performed if training need has no completion date
       Given planning period from 1MAY2019 to 1JUN2019

       Given a crew member with
       | attribute  | value  | valid from | valid to  |
       | base       | STO    |            |           |
       | title rank | FC     |            |           |
       | region     | SKS    |            |           |

       Given crew member 1 has qualification "ACQUAL+A5" from 1FEB2019 to 31DEC2035

       Given a trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
         | leg | 0001 | OSL     | CPH     | 01MAY2019 | 10:00 | 11:00 | SK  | 35X    |
         | leg | 0002 | CPH     | OSL     | 01MAY2019 | 12:00 | 13:00 | SK  | 35X    |
       Given trip 1 is assigned to crew member 1 in position FC

       Given table crew_training_need additionally contains the following
         | crew          | part | validfrom | validto  | course   | attribute  | flights | maxdays | acqual | completion |
         | crew member 1 | 1    | 4FEB2019  | 8MAY2019 | CTR-A3A5 | FAM FLT    | 2       | 0       | A5     |            |

       When I show "crew" in window 1
       and I load rule set "Tracking"

       Then the rule "rules_qual_ccr.trng_all_training_flights_performed_all" shall fail on leg 1 on trip 1 on roster 1
       and rave "training.%nr_acts_of_type_and_code_in_ival%(\"FAM FLT\",\"A5\",4FEB2019,8MAY2019)" shall be "0"


    @SCENARIO_3
    Scenario: No ETOPS LIFUS LC activities are detected in roster and training log, they are not considered performed, A2LR leg should fail
      Given planning period from 1MAY2020 to 1JUN2020

      Given a crew member with
      | attribute  | value  | valid from | valid to  |
      | base       | STO    |            |           |
      | title rank | FC     |            |           |
      | region     | SKS    |            |           |

   Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2020
   Given crew member 1 has qualification "POSITION+A2LR" from 1JAN2020 to 31DEC2020

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0001 | OSL     | EWR     | 01MAY2020 | 10:00 | 15:00 | SK  | 32Q    |
   | leg | 0002 | EWR     | OSL     | 01MAY2020 | 16:00 | 20:00 | SK  | 32Q    |
   Given trip 1 is assigned to crew member 1 in position FC

   Given table crew_training_need additionally contains the following
   | crew          | part | validfrom | validto  | course     | attribute      | flights | maxdays | acqual | completion |
   | crew member 1 | 1    | 4FEB2020  | 8MAY2020 | ETOPS A2LR | ETOPS LIFUS/LC | 2       | 0       | A2     |            |

   When I show "crew" in window 1
   and I load rule set "Tracking"

   Then the rule "rules_qual_ccr.trng_all_training_flights_performed_all" shall fail on leg 1 on trip 1 on roster 1


   @SCENARIO_4
   Scenario: Scenario should pass when crew has entries in training log and training need with completion date
    Given planning period from 1MAY2020 to 1JUN2020

    Given a crew member with
    | attribute  | value  | valid from | valid to  |
    | base       | STO    |            |           |
    | title rank | FC     |            |           |
    | region     | SKS    |            |           |

   Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2020
   Given crew member 1 has qualification "POSITION+A2LR" from 1JAN2020 to 31DEC2020

   Given table crew_training_log additionally contains the following
   | crew          | typ            | code | tim            |
   | crew member 1 | ETOPS LIFUS/LC | A2   | 4APR2020 12:22 |
   | crew member 1 | ETOPS LIFUS/LC | A2   | 5APR2020 12:22 |

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0001 | OSL     | EWR     | 01MAY2020 | 10:00 | 15:00 | SK  | 32Q    |
   | leg | 0002 | EWR     | OSL     | 01MAY2020 | 16:00 | 20:00 | SK  | 32Q    |
   Given trip 1 is assigned to crew member 1 in position FC

   Given table crew_training_need additionally contains the following
   | crew          | part | validfrom | validto  | course     | attribute      | flights | maxdays | acqual | completion |
   | crew member 1 | 1    | 4FEB2020  | 8MAY2020 | ETOPS A2LR | ETOPS LIFUS/LC | 2       | 0       | A2     | 30Apr2020  |

   When I show "crew" in window 1
   and I load rule set "Tracking"

   Then the rule "rules_qual_ccr.trng_all_training_flights_performed_all" shall pass on leg 1 on trip 1 on roster 1

  @SCENARIO_5
   Scenario: Scenario should pass when crew has entries in training log after 60 days of LRP2
    Given planning period from 1AUG2021 to 31AUG2021

    Given a crew member with
    | attribute  | value  | valid from | valid to  |
    | base       | STO    |            |           |
    | title rank | FC     |            |           |
    | region     | SKS    |            |           |

   Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2021 to 31DEC2021
   Given crew member 1 has qualification "POSITION+A2LR" from 1JAN2021 to 31DEC2021

   Given table crew_training_log additionally contains the following
   | crew          | typ            | code | tim             |
   | crew member 1 | COURSE         | LRP2 | 01MAY2021 08:00 |
   | crew member 1 | ETOPS LIFUS/LC | A2   | 05JUL2021 10:00 |
   | crew member 1 | ETOPS LIFUS/LC | A2   | 07JUL2021 10:00 |

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0001 | OSL     | EWR     | 05AUG2021 | 10:00 | 15:00 | SK  | 32Q    |
   | leg | 0002 | EWR     | OSL     | 07AUG2021 | 16:00 | 20:00 | SK  | 32Q    |
   
   Given trip 1 is assigned to crew member 1 in position FC 

   Given table crew_training_need additionally contains the following
   | crew          | part | validfrom | validto  | course     | attribute      | flights | maxdays | acqual | 
   | crew member 1 | 1    | 01MAY2021  | 05MAY2021 | ETOPS A2NX | ETOPS LIFUS/LC | 2       | 0       | A2     |  

   When I show "crew" in window 1
   and I load rule set "Tracking"

   Then the rule "rules_qual_ccr.trng_all_training_flights_performed_all" shall pass on leg 1 on trip 1 on roster 1

@SCENARIO_6
   Scenario: Scenario should pass when crew has non ETOPS flight not followed by A2NX flights with training attribute
    Given planning period from 1JUL2021 to 31AUG2021

    Given a crew member with
    | attribute  | value  | valid from | valid to  |
    | base       | STO    |            |           |
    | title rank | FC     |            |           |
    | region     | SKS    |            |           |

   Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2021 to 31DEC2021
   Given crew member 1 has qualification "POSITION+A2NX" from 1JAN2021 to 31DEC2021

   Given table crew_training_need additionally contains the following
   | crew          | part | validfrom | validto  | course     | attribute      | flights | maxdays | acqual |completion | 
   | crew member 1 | 1    | 05JUN2021 | 12JUN2021| ETOPS A2NX | ETOPS LIFUS/LC | 2       | 0       | A2     |           |

   Given table crew_training_log additionally contains the following
   | crew          | typ            | code | tim             |
   | crew member 1 | COURSE         | LRP2 | 05JUN2021 00:00 |

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 1427 | ARN     | CPH     | 02JUL2021 | 18:55 | 20:05 | SK  | 32N    |
   | leg | 1428 | CPH     | ARN     | 02JUL2021 | 20:55 | 22:10 | SK  | 32N    |
         
   Given trip 1 is assigned to crew member 1 in position FC 

   When I show "crew" in window 1
   and I load rule set "Tracking"

   Then the rule "rules_qual_ccr.trng_all_training_flights_performed_all" shall pass on leg 1 on trip 1 on roster 1


@SCENARIO_7
   Scenario: Scenario should pass when crew has non ETOPS flight followed by A2NX flights with training attribute
    Given planning period from 1JUL2021 to 31AUG2021

    Given a crew member with
    | attribute  | value  | valid from | valid to  |
    | base       | STO    |            |           |
    | title rank | FC     |            |           |
    | region     | SKS    |            |           |

   Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2021 to 31DEC2021
   Given crew member 1 has qualification "POSITION+A2NX" from 1JAN2021 to 31DEC2021

   Given table crew_training_need additionally contains the following
   | crew          | part | validfrom | validto  | course     | attribute      | flights | maxdays | acqual |completion | 
   | crew member 1 | 1    | 05JUN2021 | 12JUN2021| ETOPS A2NX | ETOPS LIFUS/LC | 2       | 0       | A2     |           |

   Given table crew_training_log additionally contains the following
   | crew          | typ            | code | tim             |
   | crew member 1 | COURSE         | LRP2 | 05JUN2021 00:00 |

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 1427 | ARN     | CPH     | 02JUL2021 | 18:55 | 20:05 | SK  | 32N    |
   | leg | 1428 | CPH     | ARN     | 02JUL2021 | 20:55 | 22:10 | SK  | 32N    |
   
   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0943 | CPH     | EWR     | 15JUL2021 | 10:00 | 15:00 | SK  | 32Q    |
   | leg | 0944 | EWR     | CPH     | 17JUL2021 | 16:00 | 20:00 | SK  | 32Q    |
   
   Given trip 1 is assigned to crew member 1 in position FC 
   Given trip 2 is assigned to crew member 1 in position FC with attribute TRAINING="ETOPS LIFUS/LC"

   When I show "crew" in window 1
   and I load rule set "Tracking"

   Then the rule "rules_qual_ccr.trng_all_training_flights_performed_all" shall pass on leg 1 on trip 1 on roster 1

@SCENARIO_8
   Scenario: Scenario should fail when crew has non ETOPS flight followed by A2NX flights without training attribute
    Given planning period from 1JUL2021 to 31AUG2021

    Given a crew member with
    | attribute  | value  | valid from | valid to  |
    | base       | STO    |            |           |
    | title rank | FC     |            |           |
    | region     | SKS    |            |           |

   Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2021 to 31DEC2021
   Given crew member 1 has qualification "POSITION+A2NX" from 1JAN2021 to 31DEC2021

   Given table crew_training_need additionally contains the following
   | crew          | part | validfrom | validto  | course     | attribute      | flights | maxdays | acqual |completion | 
   | crew member 1 | 1    | 05JUN2021 | 12JUN2021| ETOPS A2NX | ETOPS LIFUS/LC | 2       | 0       | A2     |           |

   Given table crew_training_log additionally contains the following
   | crew          | typ            | code | tim             |
   | crew member 1 | COURSE         | LRP2 | 05JUN2021 00:00 |

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 1427 | ARN     | CPH     | 02JUL2021 | 18:55 | 20:05 | SK  | 32N    |
   | leg | 1428 | CPH     | ARN     | 02JUL2021 | 20:55 | 22:10 | SK  | 32N    |
   
   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0943 | CPH     | EWR     | 15JUL2021 | 10:00 | 15:00 | SK  | 32Q    |
   | leg | 0944 | EWR     | CPH     | 17JUL2021 | 16:00 | 20:00 | SK  | 32Q    |
   
   Given trip 1 is assigned to crew member 1 in position FC 
   Given trip 2 is assigned to crew member 1 in position FC

   When I show "crew" in window 1
   and I load rule set "Tracking"

   Then the rule "rules_qual_ccr.trng_all_training_flights_performed_all" shall fail on leg 1 on trip 2 on roster 1
