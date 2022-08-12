@CC @FC @ALL @JCRT @TRACKING @ROSTERING @A2LR
Feature: Trips containing LR version should be visible on the information box on the right

##############################################################################
  Background: Setup common data
    Given planning period from 1AUG2020 to 1SEP2020

##############################################################################
@TEST_1
Scenario: A2LR first and then 38

  Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 004430  | OSL     | TOS     | 28AUG2020 15:45 | 28AUG2020 17:35 | 32Q     |         |
           | leg     | SK      | 004433  | TOS     | OSL     | 28AUG2020 18:05 | 28AUG2020 19:55 | 73H     |         |

  When I show "trips" in window 1
  and I load rule set "Tracking"
  Then rave "studio_config.%ac_qual_string%" shall be "A2LR 38" on leg 1

@TEST_2
Scenario: A2LR and then AL

  Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 004430  | OSL     | TOS     | 28AUG2020 15:45 | 28AUG2020 17:35 | 32Q     |         |
           | leg     | SK      | 004433  | TOS     | OSL     | 28AUG2020 18:05 | 28AUG2020 19:55 | 33B     |         |

  When I show "trips" in window 1
  and I load rule set "Tracking"
  Then rave "studio_config.%ac_qual_string%" shall be "AL A2LR" on leg 1

@TEST_3
Scenario: 38 and then A2LR
# Using trip 2 as 2 trips are created because of the 73H aircraft type needing more crew than 32Q

  Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 004430  | OSL     | TOS     | 28AUG2020 15:45 | 28AUG2020 17:35 | 73H     |         |
           | leg     | SK      | 004433  | TOS     | OSL     | 28AUG2020 18:05 | 28AUG2020 19:55 | 32Q     |         |

  When I show "trips" in window 1
  and I load rule set "Tracking"
  Then rave "studio_config.%ac_qual_string%" shall be "A2LR 38" on leg 1 on trip 2

@TEST_4
Scenario: AL and then A2LR
# Using trip 2 as 2 trips are created because of the 33B aircraft type needing more crew than 32Q

  Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 004430  | OSL     | TOS     | 28AUG2020 15:45 | 28AUG2020 17:35 | 33B     |         |
           | leg     | SK      | 004433  | TOS     | OSL     | 28AUG2020 18:05 | 28AUG2020 19:55 | 32Q     |         |

  When I show "trips" in window 1
  and I load rule set "Tracking"
  Then rave "studio_config.%ac_qual_string%" shall be "AL A2LR" on leg 1 on trip 2
