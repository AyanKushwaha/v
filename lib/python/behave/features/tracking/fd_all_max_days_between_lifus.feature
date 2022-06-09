Feature: Test max days between lifus legs

  Background: set up for tracking
    Given Tracking
    Given planning period from 1JUN2019 to 30JUN2019

    Given table ac_qual_map additionally contains the following
      | ac_type | aoc | ac_qual_fc | ac_qual_cc |
      | 35X     | SK  | A5         | AL         |

  @SCENARIO1
  Scenario: Check that rule fails when max days between LIFUS legs is exceeded

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    Given crew member 1 has qualification "ACQUAL+A5" from 1JUN2019 to 30JUN2019
    Given crew member 1 has acqual qualification "ACQUAL+A5+INSTRUCTOR+LIFUS" from 1JUN2019 to 30JUN2019 

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 2 has qualification "ACQUAL+A5" from 1JUN2019 to 30JUN2019 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 01JUN2019 | 10:00 | 11:00 | SK  | 35X    |
    | leg | 0002 | LHR     | OSL     | 01JUN2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="LIFUS"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="LIFUS"

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim            |
      | crew member 2 | LIFUS   | A5   | 17MAY2019 12:22 |

    Given table crew_training_need additionally contains the following
      | crew          | part | validfrom | validto   | course   | attribute  | flights | maxdays | acqual | completion |
      | crew member 2 | 1    | 1JUN2019  | 31AUG2019 | REFRESH  | LIFUS      | 2       | 0       | A5     |            |

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_max_days_between_lifus_legs_fc" shall fail on leg 1 on trip 1 on roster 2


  @SCENARIO2
  Scenario: Check that rule passes when max days between LIFUS legs is on max limit

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    Given crew member 1 has qualification "ACQUAL+A5" from 1JUN2019 to 30JUN2019
    Given crew member 1 has acqual qualification "ACQUAL+A5+INSTRUCTOR+LIFUS" from 1JUN2019 to 30JUN2019 

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 2 has qualification "ACQUAL+A5" from 1JUN2019 to 30JUN2019 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 01JUN2019 | 10:00 | 11:00 | SK  | 35X    |
    | leg | 0002 | LHR     | OSL     | 01JUN2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="LIFUS"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="LIFUS"

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 2 | LIFUS   | A5   | 18MAY2019 12:22 |

    Given table crew_training_need additionally contains the following
      | crew          | part | validfrom | validto   | course   | attribute  | flights | maxdays | acqual | completion |
      | crew member 2 | 1    | 1JUN2019  | 31AUG2019 | REFRESH  | LIFUS      | 2       | 0       | A5     |            |

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_max_days_between_lifus_legs_fc" shall pass on leg 1 on trip 1 on roster 2
