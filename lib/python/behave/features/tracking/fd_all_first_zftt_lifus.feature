@TRACKING @ZFTT @LIFUS @FD @LH
Feature: First ZFTT LIFUS, i.e. first 2 legs on FD LH shall be planned with 3 pilots

  Background: Set up

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FP         | 04DEC2019  | 06MAY2020 |
           | region          | SKI        | 04DEC2019  | 06MAY2020 |
           | base            | STO        | 04DEC2019  | 06MAY2020 |
           | title rank      | FC         | 04DEC2019  | 06MAY2020 |
           | contract        | V133-LH    | 23SEP2019  | 01APR2020 |
    Given crew member 1 has qualification "ACQUAL+A3" from 23SEP2019 to 01JAN2036
    Given crew member 1 has acqual qualification "ACQUAL+A3+AIRPORT+US" from 28FEB2020 to 28FEB2021
    Given crew member 1 has acqual qualification "ACQUAL+AWB+AIRPORT+US" from 28FEB2020 to 28FEB2021
    Given crew member 1 has acqual qualification "ACQUAL+AWB+AIRPORT+US" from 12MAR2020 to 31MAR2021

    Given crew member 1 has the following training need
    | part | course          | attribute  | valid from | valid to   | flights | max days | acqual |
    | 1    | CONV TYPERATING | ZFTT LIFUS | 23SEP2019  | 10MAY2020  | 4       | 0        | A3     |

    Given another crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 02JUN2009  | 31DEC2035 |
           | region          | SKI        | 02JUN2009  | 31DEC2035 |
           | base            | STO        | 02JUN2009  | 31DEC2035 |
           | title rank      | FC         | 02JUN2009  | 31DEC2035 |
           | contract        | V00146-LH  | 01JUN2018  | 01APR2020 |
    Given crew member 2 has qualification "ACQUAL+A3" from 02JUN2009 to 31DEC2035
    Given crew member 2 has qualification "ACQUAL+A4" from 02JUN2009 to 31DEC2035
    Given crew member 2 has qualification "ACQUAL+A5" from 04NOV2019 to 01JAN2036
    Given crew member 2 has acqual qualification "ACQUAL+A3+INSTRUCTOR+SFE" from 24SEP2013 to 01OCT2022
    Given crew member 2 has acqual qualification "ACQUAL+A3+INSTRUCTOR+TRI" from 22JAN2013 to 01OCT2021
    Given crew member 2 has acqual qualification "ACQUAL+A4+INSTRUCTOR+SFE" from 24SEP2013 to 01OCT2022
    Given crew member 2 has acqual qualification "ACQUAL+A4+INSTRUCTOR+TRI" from 22JAN2013 to 01OCT2021
    Given crew member 2 has acqual qualification "ACQUAL+A5+INSTRUCTOR+SFE" from 09JAN2020 to 01OCT2022
    Given crew member 2 has acqual qualification "ACQUAL+A5+INSTRUCTOR+TRI" from 09JAN2020 to 01OCT2021
    Given crew member 2 has acqual qualification "ACQUAL+AWB+AIRPORT+US" from 03APR2009 to 31OCT2022
    Given crew member 2 has acqual qualification "ACQUAL+AWB+INSTRUCTOR+LIFUS" from 01MAR2016 to 31DEC2035

    Given another crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FP         | 05SEP2016  | 01JAN2036 |
           | region          | SKI        | 05SEP2016  | 01JAN2036 |
           | base            | STO        | 05SEP2016  | 01JAN2036 |
           | title rank      | FP         | 05SEP2016  | 01JAN2036 |
           | contract        | V133-LH    | 05DEC2019  | 01APR2020 |
    Given crew member 3 has qualification "ACQUAL+A3" from 10DEC2017 to 01JAN2036
    Given crew member 3 has qualification "ACQUAL+A4" from 16OCT2017 to 01JAN2036
    Given crew member 3 has acqual qualification "ACQUAL+AWB+AIRPORT+US" from 04DEC2018 to 31DEC2035

    Given another crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 07NOV2019  | 01JAN2036 |
           | region          | SKI        | 07NOV2019  | 01JAN2036 |
           | base            | STO        | 07NOV2019  | 01JAN2036 |
           | title rank      | FC         | 07NOV2019  | 01JAN2036 |
           | contract        | V133-LH    | 24SEP2018  | 01APR2020 |
    Given crew member 4 has qualification "ACQUAL+A3" from 04DEC2019 to 01JAN2036
    Given crew member 4 has qualification "ACQUAL+A4" from 09OCT2019 to 01JAN2036
    Given crew member 4 has acqual qualification "ACQUAL+A3+INSTRUCTOR+TRI" from 04DEC2019 to 01OCT2022
    Given crew member 4 has acqual qualification "ACQUAL+A4+INSTRUCTOR+TRI" from 24NOV2019 to 01OCT2022
    Given crew member 4 has acqual qualification "ACQUAL+AWB+AIRPORT+US" from 30NOV2018 to 31DEC2035
    Given crew member 4 has acqual qualification "ACQUAL+AWB+INSTRUCTOR+LIFUS" from 13AUG2019 to 31DEC2035


    Given table crew_training_log additionally contains the following
           | tim             | code  | typ                | attr   | crew          |
           | 28FEB2020 09:24 | A3    | ZFTT LIFUS         | US     | crew member 1 |
           | 01MAR2020 21:55 | A3    | ZFTT LIFUS         |        | crew member 1 |
           | 12MAR2020 09:32 | A3    | ZFTT LIFUS         | US     | crew member 1 |

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000945  | ARN     | ORD     | 28FEB2020 09:20 | 28FEB2020 18:35 | 33A     |         |
           | leg     | SK      | 000946  | ORD     | ARN     | 01MAR2020 22:00 | 02MAR2020 06:25 | 33A     |         |

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000945  | ARN     | ORD     | 12MAR2020 09:20 | 12MAR2020 18:35 | 33A     |         |
           | leg     | SK      | 000946  | ORD     | ARN     | 13MAR2020 22:00 | 14MAR2020 06:25 | 33A     |         |

  @SCENARIO1
  Scenario: Check that first ZFTT LIFUS trip requires three pilots in both month planning period, 3rd FD not assigned
    Given Tracking
    Given planning period from 1FEB2020 to 31Mar2020

    Given trip 1 is assigned to crew member 1 in position FP with
           | type      | leg             | name            | value           |
           | attribute | 1,2             | TRAINING        | ZFTT LIFUS      |
    Given trip 1 is assigned to crew member 2 in position FC with
           | type      | leg             | name            | value           |
           | attribute | 1,2             | INSTRUCTOR      | LIFUS           |

    Given trip 2 is assigned to crew member 1 in position FP with
           | type      | leg             | name            | value           |
           | attribute | 1               | TRAINING        | ZFTT LIFUS      |

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_3_pilots_on_first_zftt" shall fail on leg 1 on trip 1 on roster 1


  @SCENARIO2
  Scenario: Check that first ZFTT LIFUS trip requires three pilots in both month planning period, 3rd FD assigned
    Given Tracking
    Given planning period from 1FEB2020 to 31Mar2020

    Given trip 1 is assigned to crew member 1 in position FP with
           | type      | leg             | name            | value           |
           | attribute | 1,2             | TRAINING        | ZFTT LIFUS      |
    Given trip 1 is assigned to crew member 2 in position FC with
           | type      | leg             | name            | value           |
           | attribute | 1,2             | INSTRUCTOR      | LIFUS           |
    Given trip 1 is assigned to crew member 3 in position FR

    Given trip 2 is assigned to crew member 1 in position FP with
           | type      | leg             | name            | value           |
           | attribute | 1               | TRAINING        | ZFTT LIFUS      |

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_3_pilots_on_first_zftt" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO3
  Scenario: Check that second ZFTT LIFUS trip do not require three pilots in both month planning period
    Given Tracking
    Given planning period from 1FEB2020 to 31Mar2020

    Given trip 1 is assigned to crew member 1 in position FP with
           | type      | leg             | name            | value           |
           | attribute | 1,2             | TRAINING        | ZFTT LIFUS      |
    Given trip 1 is assigned to crew member 2 in position FC with
           | type      | leg             | name            | value           |
           | attribute | 1,2             | INSTRUCTOR      | LIFUS           |
    Given trip 1 is assigned to crew member 3 in position FR

    Given trip 2 is assigned to crew member 1 in position FP with
           | type      | leg             | name            | value           |
           | attribute | 1               | TRAINING        | ZFTT LIFUS      |
    Given trip 2 is assigned to crew member 4 in position FC with
           | type      | leg             | name            | value           |
           | attribute | 1               | INSTRUCTOR      | ZFTT LIFUS      |


    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_3_pilots_on_first_zftt" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.trng_3_pilots_on_first_zftt" shall pass on leg 1 on trip 2 on roster 1


  @SCENARIO4
  Scenario: Check that second ZFTT LIFUS trip do not require three pilots in full March planning period
    Given Tracking
    Given planning period from 1MAR2020 to 31Mar2020

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000946  | ORD     | ARN     | 01MAR2020 22:00 | 02MAR2020 06:25 | 33A     |         |

    Given trip 3 is assigned to crew member 1 in position FP with
           | type      | leg             | name            | value           |
           | attribute | 1               | TRAINING        | ZFTT LIFUS      |

    Given trip 2 is assigned to crew member 1 in position FP with
           | type      | leg             | name            | value           |
           | attribute | 1               | TRAINING        | ZFTT LIFUS      |
    Given trip 2 is assigned to crew member 4 in position FC with
           | type      | leg             | name            | value           |
           | attribute | 1               | INSTRUCTOR      | ZFTT LIFUS      |

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_3_pilots_on_first_zftt" shall pass on leg 1 on trip 2 on roster 1


  @SCENARIO5
  Scenario: Check that second ZFTT LIFUS trip do not require three pilots in split March planning period
  # SKCMS-2390
    Given Tracking
    Given planning period from 8MAR2020 to 31Mar2020

    Given trip 2 is assigned to crew member 1 in position FP with
           | type      | leg             | name            | value           |
           | attribute | 1               | TRAINING        | ZFTT LIFUS      |
    Given trip 2 is assigned to crew member 4 in position FC with
           | type      | leg             | name            | value           |
           | attribute | 1               | INSTRUCTOR      | ZFTT LIFUS      |

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_3_pilots_on_first_zftt" shall pass on leg 1 on trip 1 on roster 1


