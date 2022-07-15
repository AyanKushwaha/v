@FC @ALL @JCRT @TRACKING @ROSTERING @A2NX
Feature: max days between LRP2 and first ETOPS LIFUS leg

##############################################################################
  Background: Setup common data
    
    Given a crew member with
    | attribute  | value |
    | crew rank  | FC    |
    | title rank | FC    |
    | region     | SKS   |
    | base       | STO   | 

##############################################################################
 @SCENARIO1
    Scenario: Days passed since LRP2 training is more than max so rule shall fail, no ETOPS LIFUS LC training in training log
      Given planning period from 1APR2020 to 30APR2020
      Given crew member 1 has qualification "ACQUAL+A2" from 01JAN2019 to 31DEC2020
      Given crew member 1 has qualification "POSITION+A2LR" from 01JAN2019 to 31DEC2020

      Given table crew_training_log additionally contains the following
      | crew          | typ            | code | tim             |
      | crew member 1 | COURSE         | LRP2 | 1FEB2020 08:00  |

      Given a trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | EWR     | 5APR2020 02:10 | 5APR2020 13:45 | 32Q    |
      | leg | SK  | 0002 | EWR     | ARN     | 7APR2020 09:10 | 7APR2020 20:45 | 32Q    |

      Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="ETOPS LIFUS"

     
      When I show "crew" in window 1
      and I load rule set "Tracking"

     Then the rule "rules_training_ccr.trng_max_days_between_lrp2_and_first_lh_a2nx_flight_FC" shall fail on leg 1 on trip 1 on roster 1
##############################################################################