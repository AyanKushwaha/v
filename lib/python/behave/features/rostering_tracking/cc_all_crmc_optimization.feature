@CC @TRAINING @CRMC
Feature: Check optimization related expressions and rules around CRMC

  @SCENARIO1 @planning
  Scenario: CC has CRMC document ending 31DEC2020 and employment after 1JAN2020 1 month until CRMC requirement CRMC planned
    Given Rostering_CC
    Given planning period from 1DEC2020 to 1JAN2021
    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01JAN2020  |          |
      | contract   | V00863 | 01JAN2020  |          |
      | employment |        | 01JAN2020  |          |

    Given crew member 1 has document "REC+REC" from 01JAN2020 to 31DEC2035
    Given crew member 1 has document "REC+CRMC" from 01JAN2020 to 1JAN2021

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            | ac_typ | car | num | date |
      | ground | CRMC | ARN     | ARN     | 1DEC2020 10:00 | 1DEC2020 17:00 |        | SK  |     |      |

    Given trip 1 is assigned to crew member 1 in position TL

    When I show "crew" in window 1

    Then rave "roster_cost_training.%missing_assignment_cost%" shall be "0" on leg 1 on trip 1 on roster 1
    and rave "crew_pos.%matador_assign%" shall be "8"


  @SCENARIO2 @planning
  Scenario: CC has no CRMC document and employment before 1JAN2020 1 month until CRMC requirement CRMC planned
    Given Rostering_CC
    Given planning period from 1DEC2022 to 1JAN2023
    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01FEB2018  |          |
      | contract   | V00863 | 01FEB2018  |          |
      | employment |        | 01FEB2018  |          |

    Given crew member 1 has document "REC+REC" from 01JAN2021 to 31DEC2035

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            | ac_typ | car | num | date |
      | ground | CRMC | ARN     | ARN     | 1DEC2022 10:00 | 1DEC2022 17:00 |        | SK  |     |      |

    Given trip 1 is assigned to crew member 1 in position TL

    When I show "crew" in window 1

    Then rave "roster_cost_training.%missing_assignment_cost%" shall be "0" on leg 1 on trip 1 on roster 1
    and rave "crew_pos.%matador_assign%" shall be "8"


  @SCENARIO3 @planning
  Scenario: CC has CRMC document ending 31DEC2020 and employment after 1JAN2020 1 month until CRMC requirement no CRMC planned
    Given Rostering_CC
    Given planning period from 1DEC2020 to 1JAN2021
    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01JAN2020  |          |
      | contract   | V00863 | 01JAN2020  |          |
      | employment |        | 01JAN2020  |          |

    Given crew member 1 has document "REC+REC" from 01JAN2020 to 31DEC2035
    Given crew member 1 has document "REC+CRMC" from 01JAN2020 to 1JAN2021

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr             | ac_typ | car | code | date |
      | leg | SK  | 001 | ARN     | HEL     | 05Dec2020 10:00 | 05DEC2020 12:00 | 319     | SK  |      |      |
      | leg | SK  | 002 | HEL     | ARN     | 05Dec2020 13:00 | 05DEC2020 15:00 | 319     | SK  |      |      |

    Given trip 1 is assigned to crew member 1 in position TL

    When I show "crew" in window 1

    Then rave "roster_cost_training.%missing_assignment_cost%" shall be "40000" on leg 1 on trip 1 on roster 1
    # FIXME: CRMC is counted twice because two different activities give the CRMC document, same as for CRM


  @SCENARIO4 @planning
  Scenario: CC has no CRMC document and employment before 1JAN2020 1 month until CRMC requirement no CRMC planned
    Given Rostering_CC
    Given planning period from 1DEC2022 to 1JAN2023
    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01FEB2018  |          |
      | contract   | V00863 | 01FEB2018  |          |
      | employment |        | 01FEB2018  |          |

    Given crew member 1 has document "REC+REC" from 01JAN2021 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr             | ac_typ | car | code | date |
      | leg | SK  | 001 | ARN     | HEL     | 05Dec2022 10:00 | 05DEC2022 12:00 | 319     | SK  |      |      |
      | leg | SK  | 002 | HEL     | ARN     | 05Dec2022 13:00 | 05DEC2022 15:00 | 319     | SK  |      |      |

    Given trip 1 is assigned to crew member 1 in position TL

    When I show "crew" in window 1

    Then rave "roster_cost_training.%missing_assignment_cost%" shall be "40000" on leg 1 on trip 1 on roster 1
    # FIXME: CRMC is counted twice because two different activities give the CRMC document, same as for CRM


  @SCENARIO5 @planning
  Scenario: CC has CRMC document ending 31DEC2020 and employment after 1JAN2020 2 months until CRMC requirement CRMC planned
    Given Rostering_CC
    Given planning period from 1NOV2020 to 1DEC2020
    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01JAN2020  |          |
      | contract   | V00863 | 01JAN2020  |          |
      | employment |        | 01JAN2020  |          |

    Given crew member 1 has document "REC+REC" from 01JAN2020 to 31DEC2035
    Given crew member 1 has document "REC+CRMC" from 01JAN2020 to 1JAN2021

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            | ac_typ | car | num | date |
      | ground | CRMC | ARN     | ARN     | 1NOV2020 10:00 | 1NOV2020 17:00 |        | SK  |     |      |

    Given trip 1 is assigned to crew member 1 in position TL

    When I show "crew" in window 1

    Then rave "roster_cost_training.%missing_assignment_cost%" shall be "0" on leg 1 on trip 1 on roster 1
    and rave "crew_pos.%matador_assign%" shall be "8"


  @SCENARIO6 @planning
  Scenario: CC has no CRMC document and employment before 1JAN2020 2 months until CRMC requirement CRMC planned
    Given Rostering_CC
    Given planning period from 1NOV2022 to 1DEC2022
    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01FEB2018  |          |
      | contract   | V00863 | 01FEB2018  |          |
      | employment |        | 01FEB2018  |          |

    Given crew member 1 has document "REC+REC" from 01JAN2021 to 31DEC2035

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            | ac_typ | car | num | date |
      | ground | CRMC | ARN     | ARN     | 1NOV2022 10:00 | 1NOV2022 17:00 |        | SK  |     |      |

    Given trip 1 is assigned to crew member 1 in position TL

    When I show "crew" in window 1

    Then rave "roster_cost_training.%missing_assignment_cost%" shall be "0" on leg 1 on trip 1 on roster 1
    and rave "crew_pos.%matador_assign%" shall be "8"


  @SCENARIO7 @planning
  Scenario: CC has CRMC document ending 31DEC2020 and employment after 1JAN2020 3 months until CRMC requirement no CRMC planned
    Given Rostering_CC
    Given planning period from 1NOV2020 to 1DEC2020
    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01JAN2020  |          |
      | contract   | V00863 | 01JAN2020  |          |
      | employment |        | 01JAN2020  |          |

    Given crew member 1 has document "REC+REC" from 01JAN2020 to 31DEC2035
    Given crew member 1 has document "REC+CRMC" from 01JAN2020 to 1JAN2021

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr             | ac_typ | car | code | date |
      | leg | SK  | 001 | ARN     | HEL     | 05NOV2020 10:00 | 05NOV2020 12:00 | 319     | SK  |      |      |
      | leg | SK  | 002 | HEL     | ARN     | 05NOV2020 13:00 | 05NOV2020 15:00 | 319     | SK  |      |      |

    Given trip 1 is assigned to crew member 1 in position TL

    When I show "crew" in window 1

    Then rave "roster_cost_training.%missing_assignment_cost%" shall be "20000" on leg 1 on trip 1 on roster 1
    # FIXME: CRMC is counted twice because two different activities give the CRMC document, same as for CRM


  @SCENARIO8 @planning
  Scenario: CC has no CRMC document and employment before 1JAN2020 2 months until CRMC requirement no CRMC planned
    Given Rostering_CC
    Given planning period from 1NOV2022 to 1DEC2022
    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01FEB2018  |          |
      | contract   | V00863 | 01FEB2018  |          |
      | employment |        | 01FEB2018  |          |

    Given crew member 1 has document "REC+REC" from 01JAN2021 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr             | ac_typ | car | code | date |
      | leg | SK  | 001 | ARN     | HEL     | 05NOV2022 10:00 | 05NOV2022 12:00 | 319     | SK  |      |      |
      | leg | SK  | 002 | HEL     | ARN     | 05NOV2022 13:00 | 05NOV2022 15:00 | 319     | SK  |      |      |

    Given trip 1 is assigned to crew member 1 in position TL

    When I show "crew" in window 1

    Then rave "roster_cost_training.%missing_assignment_cost%" shall be "20000" on leg 1 on trip 1 on roster 1
    # FIXME: CRMC is counted twice because two different activities give the CRMC document, same as for CRM


  @SCENARIO9 @planning
  Scenario: CC has CRMC document ending 31DEC2020 and employment after 1JAN2020 3 months until CRMC requirement CRMC planned
    Given Rostering_CC
    Given planning period from 1OCT2020 to 1NOV2020
    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01JAN2020  |          |
      | contract   | V00863 | 01JAN2020  |          |
      | employment |        | 01JAN2020  |          |

    Given crew member 1 has document "REC+REC" from 01JAN2020 to 31DEC2035
    Given crew member 1 has document "REC+CRMC" from 01JAN2020 to 1JAN2021

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            | ac_typ | car | num | date |
      | ground | CRMC | ARN     | ARN     | 1OCT2020 10:00 | 1OCT2020 17:00 |        | SK  |     |      |

    Given trip 1 is assigned to crew member 1 in position TL

    When I show "crew" in window 1

    Then rave "roster_cost_training.%missing_assignment_cost%" shall be "0" on leg 1 on trip 1 on roster 1
    and rave "crew_pos.%matador_assign%" shall be "8"


  @SCENARIO10 @planning
  Scenario: CC has no CRMC document and employment before 1JAN2020 3 months until CRMC requirement CRMC planned
    Given Rostering_CC
    Given planning period from 1OCT2022 to 1NOV2022
    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01FEB2018  |          |
      | contract   | V00863 | 01FEB2018  |          |
      | employment |        | 01FEB2018  |          |

    Given crew member 1 has document "REC+REC" from 01JAN2021 to 31DEC2035

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            | ac_typ | car | num | date |
      | ground | CRMC | ARN     | ARN     | 1OCT2022 10:00 | 1OCT2022 17:00 |        | SK  |     |      |

    Given trip 1 is assigned to crew member 1 in position TL

    When I show "crew" in window 1

    Then rave "roster_cost_training.%missing_assignment_cost%" shall be "0" on leg 1 on trip 1 on roster 1
    and rave "crew_pos.%matador_assign%" shall be "8"


  @SCENARIO11 @planning
  Scenario: CC has CRMC document ending 31DEC2020 and employment after 1JAN2020 3 months until CRMC requirement no CRMC planned
    Given Rostering_CC
    Given planning period from 1OCT2020 to 1NOV2020
    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01JAN2020  |          |
      | contract   | V00863 | 01JAN2020  |          |
      | employment |        | 01JAN2020  |          |

    Given crew member 1 has document "REC+REC" from 01JAN2020 to 31DEC2035
    Given crew member 1 has document "REC+CRMC" from 01JAN2020 to 1JAN2021

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr             | ac_typ | car | code | date |
      | leg | SK  | 001 | ARN     | HEL     | 05OCT2020 10:00 | 05OCT2020 12:00 | 319     | SK  |      |      |
      | leg | SK  | 002 | HEL     | ARN     | 05OCT2020 13:00 | 05OCT2020 15:00 | 319     | SK  |      |      |

    Given trip 1 is assigned to crew member 1 in position TL

    When I show "crew" in window 1

    Then rave "roster_cost_training.%missing_assignment_cost%" shall be "20000" on leg 1 on trip 1 on roster 1
    # FIXME: CRMC is counted twice because two different activities give the CRMC document, same as for CRM


  @SCENARIO12 @planning
  Scenario: CC has no CRMC document and employment before 1JAN2020 3 months until CRMC requirement no CRMC planned
    Given Rostering_CC
    Given planning period from 1OCT2022 to 1NOV2022
    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01FEB2018  |          |
      | contract   | V00863 | 01FEB2018  |          |
      | employment |        | 01FEB2018  |          |

    Given crew member 1 has document "REC+REC" from 01JAN2021 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr             | ac_typ | car | code | date |
      | leg | SK  | 001 | ARN     | HEL     | 05OCT2022 10:00 | 05OCT2022 12:00 | 319     | SK  |      |      |
      | leg | SK  | 002 | HEL     | ARN     | 05OCT2022 13:00 | 05OCT2022 15:00 | 319     | SK  |      |      |

    Given trip 1 is assigned to crew member 1 in position TL

    When I show "crew" in window 1

    Then rave "roster_cost_training.%missing_assignment_cost%" shall be "20000" on leg 1 on trip 1 on roster 1
    # FIXME: CRMC is counted twice because two different activities give the CRMC document, same as for CRM


  @SCENARIO13 @planning
  Scenario: CC has CRMC document ending 31DEC2020 and employment after 1JAN2020 4 months until CRMC requirement no CRMC planned
    Given Rostering_CC
    Given planning period from 1SEP2020 to 1OCT2020
    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01JAN2020  |          |
      | contract   | V00863 | 01JAN2020  |          |
      | employment |        | 01JAN2020  |          |

    Given crew member 1 has document "REC+REC" from 01JAN2020 to 31DEC2035
    Given crew member 1 has document "REC+CRMC" from 01JAN2020 to 1JAN2021

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr             | ac_typ | car | code | date |
      | leg | SK  | 001 | ARN     | HEL     | 05SEP2020 10:00 | 05SEP2020 12:00 | 319     | SK  |      |      |
      | leg | SK  | 002 | HEL     | ARN     | 05SEP2020 13:00 | 05SEP2020 15:00 | 319     | SK  |      |      |

    Given trip 1 is assigned to crew member 1 in position TL

    When I show "crew" in window 1

    Then rave "roster_cost_training.%missing_assignment_cost%" shall be "0" on leg 1 on trip 1 on roster 1
    # FIXME: CRMC is counted twice because two different activities give the CRMC document, same as for CRM


  @SCENARIO14 @planning
  Scenario: CC has no CRMC document and employment before 1JAN2020 4 months until CRMC requirement no CRMC planned
    Given Rostering_CC
    Given planning period from 1SEP2022 to 1OCT2022
    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01FEB2018  |          |
      | contract   | V00863 | 01FEB2018  |          |
      | employment |        | 01FEB2018  |          |

    Given crew member 1 has document "REC+REC" from 01JAN2021 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr             | ac_typ | car | code | date |
      | leg | SK  | 001 | ARN     | HEL     | 05SEP2022 10:00 | 05SEP2022 12:00 | 319     | SK  |      |      |
      | leg | SK  | 002 | HEL     | ARN     | 05SEP2022 13:00 | 05SEP2022 15:00 | 319     | SK  |      |      |

    Given trip 1 is assigned to crew member 1 in position TL

    When I show "crew" in window 1

    Then rave "roster_cost_training.%missing_assignment_cost%" shall be "0" on leg 1 on trip 1 on roster 1
    # FIXME: CRMC is counted twice because two different activities give the CRMC document, same as for CRM
