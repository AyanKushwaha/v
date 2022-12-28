@skip
Feature: Example, data setup tables

  Background: setup planning period
    Given planning period from 1feb2018 to 28feb2018
    Given Rostering_CC

  Scenario: Add values to tables

    Given a crew member

    Given table activity_set is overridden with the following
    | id  | grp  | si                   | recurrent_typ |
    | A41 | LPC  | Test of extra line 1 |               |

    Given table activity_set additionally contains the following
    | id  | grp  | si                   | recurrent_typ |
    | A42 | LPC  | Test of extra line 2 |               |

    Given table crew_employment additionally contains the following
    | crew          | validfrom | validto   | carrier | company | base | crewrank | titlerank | si | region | civicstation | station | country | extperkey | planning_group |
    | crew member 1 | 01NOV2018 | 01JAN2035 | SK      | SK      | STO  | FC       | FC        |    | SKS    | STO          | STO     | SE      | 42424     | SKS            |

    Given table preferred_hotel_exc additionally contains the following
    | airport | region | maincat | airport_hotel | validfrom | arr_flight_nr | dep_flight_nr | week_days | validto   | hotel | si |
    | GOT     | SKN    | C       | True          | 01JAN2018 | *             | *             | 1234567   | 01JAN2035 | GOT1  |    |

    Given table accumulator_int additionally contains the following
    | name                    | acckey | tim       | val |
    | accumulators.table_test | 12345  | 01NOV2018 | 42  |

    Given table accumulator_rel additionally contains the following
    | name                    | acckey | tim       | val    |
    | accumulators.table_test | 12345  | 01NOV2018 | 12:42  |

    When I show "crew" in window 1

    Then rave "true" shall be "True" on leg 1 on trip 1 on roster 1

