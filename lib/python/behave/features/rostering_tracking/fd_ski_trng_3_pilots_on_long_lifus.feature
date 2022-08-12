@jcrt @fd @fc @tracking @rostering @lifus @training
Feature: FD SKI 3 pilots needed on long lifus to MIA

Background:
  Given planning period from 1MAR2019 to 30MAR2019
  Given Tracking

   ###########################################################################################
   # Tracking cases
   ###########################################################################################

   Scenario: rule passes if leg is going to mia with number of fd on long lifus is 3 training attribute ZFTT LIFUS

   Given planning period from 1MAR2019 to 30MAR2019


    Given a crew member with
    | attribute       | value     | valid from  | valid to |
    | employee number | 38003     |             |          |
    | base            | OSL       |             |          |
    | crew rank       | FP        |             |          |

    Given a crew member with
    | attribute       | value     | valid from  | valid to |
    | employee number | 25755     |             |          |
    | base            | CPH       |             |          |
    | title rank      | FC        |             |          |

     Given a crew member with
    | attribute       | value     | valid from  | valid to |
    | employee number | 28840     |             |          |
    | base            | CPH       |             |          |
    | title rank      | FP        |             |          |

    Given a trip with the following activities
    | act | num   | dep stn | arr stn | dep      | arr |
    | leg | 0001  | CPH     | MIA     | 24MAR2019 05:00 | 24MAR2019 17:00 |
    | leg | 0002  | MIA     | CPH     | 26MAR2019 05:00 | 26MAR2019 17:00 |

   Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="ZFTT LIFUS"
   Given trip 1 is assigned to crew member 2 in position FC
   Given trip 1 is assigned to crew member 3 in position FP

   When I show "crew" in window 1
   Then rave "rules_training_ccr.trng_3_pilots_on_long_lifus" shall be "True" on leg 1 on trip 1 on roster 1
   and rave "rules_training_ccr.%trng_3_pilots_on_long_lifus_valid%" shall be "True" on leg 1 on trip 1 on roster 1

##############################################################################################

   Scenario: rule passes if leg is going to mia with number of fd on long lifus is 3 training attribute LIFUS

   Given planning period from 1MAR2019 to 30MAR2019


    Given a crew member with
    | attribute       | value     | valid from  | valid to |
    | employee number | 38003     |             |          |
    | base            | OSL       |             |          |
    | crew rank       | FP        |             |          |

    Given a crew member with
    | attribute       | value     | valid from  | valid to |
    | employee number | 25755     |             |          |
    | base            | CPH       |             |          |
    | title rank      | FC        |             |          |

     Given a crew member with
    | attribute       | value     | valid from  | valid to |
    | employee number | 28840     |             |          |
    | base            | CPH       |             |          |
    | title rank      | FP        |             |          |

    Given a trip with the following activities
    | act | num   | dep stn | arr stn | dep      | arr |
    | leg | 0001  | CPH     | MIA     | 24MAR2019 05:00 | 24MAR2019 17:00 |
    | leg | 0002  | MIA     | CPH     | 26MAR2019 05:00 | 26MAR2019 17:00 |

   Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="LIFUS"
   Given trip 1 is assigned to crew member 2 in position FC
   Given trip 1 is assigned to crew member 3 in position FP

   When I show "crew" in window 1
   Then rave "rules_training_ccr.trng_3_pilots_on_long_lifus" shall be "True" on leg 1 on trip 1 on roster 1
   and rave "rules_training_ccr.%trng_3_pilots_on_long_lifus_valid%" shall be "True" on leg 1 on trip 1 on roster 1

##############################################################################################

   Scenario: rule passes if leg is going to mia with number of fd on long lifus is 3 training attribute X LIFUS

   Given planning period from 1MAR2019 to 30MAR2019


    Given a crew member with
    | attribute       | value     | valid from  | valid to |
    | employee number | 38003     |             |          |
    | base            | OSL       |             |          |
    | crew rank       | FP        |             |          |

    Given a crew member with
    | attribute       | value     | valid from  | valid to |
    | employee number | 25755     |             |          |
    | base            | CPH       |             |          |
    | title rank      | FC        |             |          |

     Given a crew member with
    | attribute       | value     | valid from  | valid to |
    | employee number | 28840     |             |          |
    | base            | CPH       |             |          |
    | title rank      | FP        |             |          |

    Given a trip with the following activities
    | act | num   | dep stn | arr stn | dep      | arr |
    | leg | 0001  | CPH     | MIA     | 24MAR2019 05:00 | 24MAR2019 17:00 |
    | leg | 0002  | MIA     | CPH     | 26MAR2019 05:00 | 26MAR2019 17:00 |

   Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="X LIFUS"
   Given trip 1 is assigned to crew member 2 in position FC
   Given trip 1 is assigned to crew member 3 in position FP

   When I show "crew" in window 1
   Then rave "rules_training_ccr.trng_3_pilots_on_long_lifus" shall be "True" on leg 1 on trip 1 on roster 1
   and rave "rules_training_ccr.%trng_3_pilots_on_long_lifus_valid%" shall be "True" on leg 1 on trip 1 on roster 1

##############################################################################################

   Scenario: rule passes if leg is going to mia with number of fd on long lifus is 3 training attribute ZFTT X

   Given planning period from 1MAR2019 to 30MAR2019


    Given a crew member with
    | attribute       | value     | valid from  | valid to |
    | employee number | 38003     |             |          |
    | base            | OSL       |             |          |
    | crew rank       | FP        |             |          |

    Given a crew member with
    | attribute       | value     | valid from  | valid to |
    | employee number | 25755     |             |          |
    | base            | CPH       |             |          |
    | title rank      | FC        |             |          |

     Given a crew member with
    | attribute       | value     | valid from  | valid to |
    | employee number | 28840     |             |          |
    | base            | CPH       |             |          |
    | title rank      | FP        |             |          |

    Given a trip with the following activities
    | act | num   | dep stn | arr stn | dep      | arr |
    | leg | 0001  | CPH     | MIA     | 24MAR2019 05:00 | 24MAR2019 17:00 |
    | leg | 0002  | MIA     | CPH     | 26MAR2019 05:00 | 26MAR2019 17:00 |

   Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="ZFTT X"
   Given trip 1 is assigned to crew member 2 in position FC
   Given trip 1 is assigned to crew member 3 in position FP

   When I show "crew" in window 1
   Then rave "rules_training_ccr.trng_3_pilots_on_long_lifus" shall be "True" on leg 1 on trip 1 on roster 1
   and rave "rules_training_ccr.%trng_3_pilots_on_long_lifus_valid%" shall be "True" on leg 1 on trip 1 on roster 1

##############################################################################################

   Scenario: rule passes  as validity failes due to training attribute NONE

   Given planning period from 1MAR2019 to 30MAR2019


    Given a crew member with
    | attribute       | value     | valid from  | valid to |
    | employee number | 38003     |             |          |
    | base            | OSL       |             |          |
    | crew rank       | FP        |             |          |

    Given a crew member with
    | attribute       | value     | valid from  | valid to |
    | employee number | 25755     |             |          |
    | base            | CPH       |             |          |
    | title rank      | FC        |             |          |

     Given a crew member with
    | attribute       | value     | valid from  | valid to |
    | employee number | 28840     |             |          |
    | base            | CPH       |             |          |
    | title rank      | FP        |             |          |

    Given a trip with the following activities
    | act | num   | dep stn | arr stn | dep      | arr |
    | leg | 0001  | CPH     | MIA     | 24MAR2019 05:00 | 24MAR2019 17:00 |
    | leg | 0002  | MIA     | CPH     | 26MAR2019 05:00 | 26MAR2019 17:00 |

   Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="NONE"
   Given trip 1 is assigned to crew member 2 in position FC
   Given trip 1 is assigned to crew member 3 in position FP

   When I show "crew" in window 1
   Then rave "rules_training_ccr.trng_3_pilots_on_long_lifus" shall be "True" on leg 1 on trip 1 on roster 1
   and rave "rules_training_ccr.%trng_3_pilots_on_long_lifus_valid%" shall be "False" on leg 1 on trip 1 on roster 1

##############################################################################################

   Scenario: rule passes  as validity failes due to non SKI crew

   Given planning period from 1MAR2019 to 30MAR2019


    Given a crew member with
    | attribute       | value     | valid from  | valid to |
    | employee number | 10123     |             |          |
    | base            | STO       |             |          |
    | region          | SKS       |             |          |
    | crew rank       | FP        |             |          |

    Given a crew member with
    | attribute       | value     | valid from  | valid to |
    | employee number | 10373     |             |          |
    | base            | STO       |             |          |
    | region          | SKS       |             |          |
    | title rank      | FC        |             |          |

     Given a crew member with
    | attribute       | value     | valid from  | valid to |
    | employee number | 10194     |             |          |
    | base            | STO       |             |          |
    | region          | SKS       |             |          |
    | title rank      | FP        |             |          |

    Given a trip with the following activities
    | act | num   | dep stn | arr stn | dep      | arr |
    | leg | 0001  | CPH     | MIA     | 24MAR2019 05:00 | 24MAR2019 17:00 |
    | leg | 0002  | MIA     | CPH     | 26MAR2019 05:00 | 26MAR2019 17:00 |

   Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="LIFUS"
   Given trip 1 is assigned to crew member 2 in position FC
   Given trip 1 is assigned to crew member 3 in position FP

   When I show "crew" in window 1
   Then rave "rules_training_ccr.trng_3_pilots_on_long_lifus" shall be "True" on leg 1 on trip 1 on roster 1
   and rave "rules_training_ccr.%trng_3_pilots_on_long_lifus_valid%" shall be "False" on leg 1 on trip 1 on roster 1

##############################################################################################

   Scenario: rule fails if leg is not going to mia with number of fd on long lifus is not 3

   Given planning period from 1MAR2019 to 30MAR2019


    Given a crew member with
    | attribute       | value     | valid from  | valid to |
    | employee number | 38003     |             |          |
    | base            | OSL       |             |          |
    | crew rank       | FP        |             |          |

    Given a crew member with
    | attribute       | value     | valid from  | valid to |
    | employee number | 25755     |             |          |
    | base            | CPH       |             |          |
    | title rank      | FC        |             |          |

    Given a trip with the following activities
    | act | num   | dep stn | arr stn | dep      | arr |
    | leg | 0001  | CPH     | MIA     | 24MAR2019 05:00 | 24MAR2019 17:00 |
    | leg | 0002  | MIA     | CPH     | 26MAR2019 05:00 | 26MAR2019 17:00 |

   Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="ZFTT LIFUS"
   Given trip 1 is assigned to crew member 2 in position FC

   When I show "crew" in window 1
   Then rave "rules_training_ccr.trng_3_pilots_on_long_lifus" shall be "False" on leg 1 on trip 1 on roster 1
   and rave "rules_training_ccr.%trng_3_pilots_on_long_lifus_valid%" shall be "True" on leg 1 on trip 1 on roster 1

##############################################################################################

    Scenario: rule passes due to validity if leg is not going to LAX with number of fd on long lifus is 3

    Given planning period from 1MAR2019 to 30MAR2019

           Given a crew member with
  | attribute       | value     | valid from | valid to  |
  | employee number | 38003     |            |           |
  | base            | OSL       |            |           |
  | crew rank       | FP        |            |           |

     Given a crew member with
  | attribute       | value     | valid from  | valid to |
  | employee number | 25755     |             |          |
  | base            | CPH       |             |          |
  | title rank      | FC        |             |          |

     Given a crew member with
  | attribute       | value     | valid from  | valid to |
  | employee number | 28840     |             |          |
  | base            | CPH       |             |          |
  | title rank      | FP        |             |          |

    Given a trip with the following activities
    | act | num   | dep stn | arr stn | dep      | arr |
    | leg | 0001  | CPH     | LAX     | 24MAR2019 05:00 | 24MAR2019 17:00 |
    | leg | 0002  | LAX     | CPH     | 26MAR2019 05:00 | 26MAR2019 17:00 |


   Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="LIFUS"
   Given trip 1 is assigned to crew member 2 in position FC
   Given trip 1 is assigned to crew member 3 in position FP

    When I show "trips" in window 1
    Then rave "rules_training_ccr.trng_3_pilots_on_long_lifus" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "rules_training_ccr.%trng_3_pilots_on_long_lifus_valid%" shall be "False" on leg 1 on trip 1 on roster 1

##############################################################################################

    Scenario: rule passes due to validity if leg is not going to LAX with number of fd on long lifus is 2

    Given planning period from 1MAR2019 to 30MAR2019

           Given a crew member with
  | attribute       | value     | valid from | valid to  |
  | employee number | 38003     |            |           |
  | base            | OSL       |            |           |
  | crew rank       | FP        |            |           |

     Given a crew member with
  | attribute       | value     | valid from  | valid to |
  | employee number | 25755     |             |          |
  | base            | CPH       |             |          |
  | title rank      | FC        |             |          |



    Given a trip with the following activities
    | act | num   | dep stn | arr stn | dep      | arr |
    | leg | 0001  | CPH     | LAX     | 24MAR2019 05:00 | 24MAR2019 17:00 |
    | leg | 0002  | LAX     | CPH     | 26MAR2019 05:00 | 26MAR2019 17:00 |


   Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="LIFUS"
   Given trip 1 is assigned to crew member 2 in position FC


    When I show "trips" in window 1
    Then rave "rules_training_ccr.trng_3_pilots_on_long_lifus" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "rules_training_ccr.%trng_3_pilots_on_long_lifus_valid%" shall be "False" on leg 1 on trip 1 on roster 1

 ##########################################################################################

    Scenario: rule fails if leg is going to mia with number of fd on long lifus is not 3

   Given planning period from 1MAR2019 to 30MAR2019

    Given a crew member with
    | attribute       | value     | valid from  | valid to |
    | employee number | 38003     |             |          |
    | base            | OSL       |             |          |
    | crew rank       | FP        |             |          |

    Given a crew member with
    | attribute       | value     | valid from  | valid to |
    | employee number | 25755     |             |          |
    | base            | CPH       |             |          |
    | title rank      | FC        |             |          |

    Given a trip with the following activities
    | act | num   | dep stn | arr stn | dep      | arr |
    | leg | 0001  | CPH     | MIA     | 24MAR2019 05:00 | 24MAR2019 17:00 |
    | leg | 0002  | MIA     | CPH     | 26MAR2019 05:00 | 26MAR2019 17:00 |

   Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="ZFTT LIFUS"
   Given trip 1 is assigned to crew member 2 in position FC

   When I show "crew" in window 1
   Then rave "rules_training_ccr.trng_3_pilots_on_long_lifus" shall be "False" on leg 1 on trip 1 on roster 1
   and rave "rules_training_ccr.%trng_3_pilots_on_long_lifus_valid%" shall be "True" on leg 1 on trip 1 on roster 1

##############################################################################################


