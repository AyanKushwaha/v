@CC @FC @ALL @JCRT @TRACKING @ROSTERING @A2NX
Feature: Crew flying A2NX legs should have qualification POSITION+A2NX.

##############################################################################
  Background: Setup common data
    Given planning period from 1MAR2020 to 1APR2020

    Given table aircraft_type is overridden with the following
    | id  | maintype | crewbunkfc | crewbunkcc | maxfc | maxcc | class1fc | class1cc | class2cc | class3cc | version |
    | 32N | A320     | 0          | 0          | 4     | 5     | 0        | 0        | 0        | 0        | LR      |
    | 32X | A320     | 0          | 0          | 4     | 5     | 0        | 0        | 0        | 0        |         |

    Given table ac_qual_map additionally contains the following
    | ac_type | aoc | ac_qual_fc | ac_qual_cc |
    | 32N     | SK  | A2         | A2         |
    | 32X     | SK  | A2         | A2         |

    Given table activity_set additionally contains the following
    | id   | grp | si                      | recurrent_typ |
    | Q2LR | COD | A2 Long Range course CC |               |
    | LRP2 | COD | A2 Long Range course FD |               |

    Given table activity_set_period additionally contains the following
    | id   | validfrom        | validto         |
    | Q2LR | 01Jan1986 00:00  | 31Dec2035 00:00 |
    | LRP2 | 01Jan1986 00:00  | 31Dec2035 00:00 |

    Given a crew member with
    | attribute  | value |
    | crew rank  | AP    |
    | title rank | AP    |
    | region     | SKS   |
    | base       | STO   |

    Given a crew member with
    | attribute  | value |
    | crew rank  | FC    |
    | title rank | FC    |
    | region     | SKS   |
    | base       | STO   |

##############################################################################

    @SCENARIO1
    Scenario: Crew without ACQUAL+A2 and POSITION+A2NX assigned to A2NX leg is illegal because missing ACQUAL+A2.
      Given Tracking
      Given crew member 1 has qualification "ACQUAL+A2" from 1APR2019 to 31DEC2019
      Given crew member 2 has qualification "ACQUAL+A2" from 1APR2019 to 31DEC2019

      Given a trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | EWR     | 5MAR2020 02:10 | 5MAR2020 13:45 | 32N    |

      Given trip 1 is assigned to crew member 1
      Given trip 1 is assigned to crew member 2 in position FC

      When I show "crew" in window 1

      Then the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall fail on leg 1 on trip 1 on roster 1
      and rave "rules_qual_ccr.%qln_ac_types_failtext_leg%" shall be "OMA: Qual: licence expired A2 31Dec2019" on leg 1 on trip 1 on roster 1
      and the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall fail on leg 1 on trip 1 on roster 2
      and rave "rules_qual_ccr.%qln_ac_types_failtext_leg%" shall be "OMA: Qual: licence expired A2 31Dec2019" on leg 1 on trip 1 on roster 2

##############################################################################

    @SCENARIO2
    Scenario: Crew with ACQUAL+A2 and without POSITION+A2NX assigned to A2NX leg is not legal.
      Given Tracking
      Given crew member 1 has qualification "ACQUAL+A2" from 01JAN2019 to 31DEC2020
      Given crew member 2 has qualification "ACQUAL+A2" from 01JAN2019 to 31DEC2020

      Given a trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | EWR     | 5MAR2020 02:10 | 5MAR2020 13:45 | 32N    |

      Given another trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | GOT     | 6MAR2020 08:00 | 6MAR2020 09:00 | 32N    |

      Given trip 1 is assigned to crew member 1
      Given trip 1 is assigned to crew member 2 in position FC
      Given trip 2 is assigned to crew member 1
      Given trip 2 is assigned to crew member 2 in position FC

      When I show "crew" in window 1

      Then the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall fail on leg 1 on trip 1 on roster 1
      and rave "rules_qual_ccr.%qln_ac_types_failtext_leg%" shall be "OMA: Qual. AC-type A2NX requires Position A2NX" on leg 1 on trip 1 on roster 1
      and the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall fail on leg 1 on trip 1 on roster 2
      and rave "rules_qual_ccr.%qln_ac_types_failtext_leg%" shall be "OMA: Qual. AC-type A2 requires Position A2NX for LH flights" on leg 1 on trip 1 on roster 2
      and the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall fail on leg 1 on trip 2 on roster 1
      and rave "rules_qual_ccr.%qln_ac_types_failtext_leg%" shall be "OMA: Qual. AC-type A2NX requires Position A2NX" on leg 1 on trip 2 on roster 1
      and the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall fail on leg 1 on trip 2 on roster 2
      and rave "rules_qual_ccr.%qln_ac_types_failtext_leg%" shall be "OMA: Qual. AC-type A2 requires Position A2NX or A2_OW for SH flights" on leg 1 on trip 2 on roster 2

##############################################################################

    @SCENARIO3
    Scenario: Crew with ACQUAL+A2 and POSITION+A2NX assigned to A2NX leg is legal.
      Given Tracking
      Given crew member 1 has qualification "ACQUAL+A2" from 01JAN2019 to 31DEC2020
      Given crew member 1 has qualification "POSITION+A2NX" from 01JAN2019 to 31DEC2020
      Given crew member 2 has qualification "ACQUAL+A2" from 01JAN2019 to 31DEC2020
      Given crew member 2 has qualification "POSITION+A2NX" from 01JAN2019 to 31DEC2020


      Given a trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | EWR     | 5MAR2020 02:10 | 5MAR2020 13:45 | 32N    |

      Given another trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | GOT     | 6MAR2020 08:00 | 6MAR2020 09:00 | 32N    |

      Given trip 1 is assigned to crew member 1
      Given trip 1 is assigned to crew member 2 in position FC
      Given trip 2 is assigned to crew member 1
      Given trip 2 is assigned to crew member 2 in position FC

      When I show "crew" in window 1

      Then the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall pass on leg 1 on trip 1 on roster 1
      and the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall pass on leg 1 on trip 1 on roster 2
      and the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall pass on leg 1 on trip 2 on roster 1
      and the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall pass on leg 1 on trip 2 on roster 2

##############################################################################

    @SCENARIO4
    Scenario: Regular (not long range aircraft) A2 leg should not consider POSITION+A2NX qualification for any crew.
      Given Tracking
      Given crew member 1 has qualification "ACQUAL+A2" from 01JAN2019 to 31DEC2020
      Given crew member 1 has qualification "POSITION+A2NX" from 01JAN2019 to 31DEC2020
      Given crew member 2 has qualification "ACQUAL+A2" from 01JAN2019 to 31DEC2020
      Given crew member 2 has qualification "POSITION+A2NX" from 01JAN2019 to 31DEC2020

      Given another crew member with
      | attribute  | value |
      | crew rank  | AH    |
      | title rank | AH    |
      | region     | SKS   |
      | base       | STO   |

      Given crew member 3 has qualification "ACQUAL+A2" from 01JAN2019 to 31DEC2020

      Given another crew member with
      | attribute  | value |
      | crew rank  | FP    |
      | title rank | FP    |
      | region     | SKD   |
      | base       | CPH   |

      Given crew member 4 has qualification "ACQUAL+A2" from 01JAN2019 to 31DEC2020

      Given a trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | GOT     | 5MAR2020 08:00 | 5MAR2020 09:00 | 32X    |

      Given trip 1 is assigned to crew member 1
      Given trip 1 is assigned to crew member 2 in position FC
      Given trip 1 is assigned to crew member 3
      Given trip 1 is assigned to crew member 4 in position FP

      When I show "crew" in window 1

      Then the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall pass on leg 1 on trip 1 on roster 1
      and the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall pass on leg 1 on trip 1 on roster 2
      and the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall pass on leg 1 on trip 1 on roster 3
      and the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall pass on leg 1 on trip 1 on roster 4

##############################################################################

    @SCENARIO5
    Scenario: Illegal to assign A2NX leg to crew with A2NX course planned after leg start.
      Given Tracking
      Given crew member 1 has qualification "ACQUAL+A2" from 01JAN2019 to 31DEC2020
      Given crew member 1 has a personal activity "Q2LR" at station "ARN" that starts at 7MAR202020 08:00 and ends at 7MAR2020 17:00
      Given crew member 2 has qualification "ACQUAL+A2" from 01JAN2019 to 31DEC2020
      Given crew member 2 has a personal activity "LRP2" at station "ARN" that starts at 7MAR202020 08:00 and ends at 7MAR2020 17:00

      Given a trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | EWR     | 5MAR2020 02:10 | 5MAR2020 13:45 | 32N    |

      Given another trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | GOT     | 6MAR2020 08:00 | 6MAR2020 09:00 | 32N    |

      Given trip 1 is assigned to crew member 1
      Given trip 1 is assigned to crew member 2
      Given trip 2 is assigned to crew member 1
      Given trip 2 is assigned to crew member 2

      When I show "crew" in window 1

      Then the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall fail on leg 1 on trip 1 on roster 1
      and rave "rules_qual_ccr.%qln_ac_types_failtext_leg%" shall be "OMA: Qual. AC-type A2NX requires Position A2NX" on leg 1 on trip 1 on roster 1
      and the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall fail on leg 1 on trip 1 on roster 2
      and rave "rules_qual_ccr.%qln_ac_types_failtext_leg%" shall be "OMA: Qual. AC-type A2 requires Position A2NX for LH flights" on leg 1 on trip 1 on roster 2
      and the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall fail on leg 1 on trip 2 on roster 1
      and rave "rules_qual_ccr.%qln_ac_types_failtext_leg%" shall be "OMA: Qual. AC-type A2NX requires Position A2NX" on leg 1 on trip 2 on roster 1
      and the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall fail on leg 1 on trip 2 on roster 2
      and rave "rules_qual_ccr.%qln_ac_types_failtext_leg%" shall be "OMA: Qual. AC-type A2 requires Position A2NX or A2_OW for SH flights" on leg 1 on trip 2 on roster 2

##############################################################################

    @SCENARIO6
    Scenario: Legal to assign A2NX leg to crew without POSITION+A2NX if A2NX course is planned before leg start.
      Given Tracking
      Given crew member 1 has qualification "ACQUAL+A2" from 01JAN2019 to 31DEC2020
      Given crew member 1 has a personal activity "Q2LR" at station "ARN" that starts at 3MAR202020 08:00 and ends at 3MAR2020 17:00
      Given crew member 2 has qualification "ACQUAL+A2" from 01JAN2019 to 31DEC2020
      Given crew member 2 has a personal activity "LRP2" at station "ARN" that starts at 3MAR202020 08:00 and ends at 3MAR2020 17:00

      Given a trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | EWR     | 5MAR2020 02:10 | 5MAR2020 13:45 | 32N    |

      Given another trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | GOT     | 6MAR2020 08:00 | 6MAR2020 09:00 | 32N    |

      Given trip 1 is assigned to crew member 1
      Given trip 1 is assigned to crew member 2
      Given trip 2 is assigned to crew member 1
      Given trip 2 is assigned to crew member 2

      When I show "crew" in window 1

      Then the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall pass on leg 1 on trip 1 on roster 1
      and the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall pass on leg 1 on trip 1 on roster 2
      and the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall pass on leg 1 on trip 2 on roster 1
      and the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall pass on leg 1 on trip 2 on roster 2

##############################################################################

    @SCENARIO7
    Scenario: Legal to assign A2NX leg to crew with A2NX course in training log before leg start.
      Given Tracking
      Given crew member 1 has qualification "ACQUAL+A2" from 01JAN2019 to 31DEC2020
      Given crew member 2 has qualification "ACQUAL+A2" from 01JAN2019 to 31DEC2020

      Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | COURSE  | Q2LR | 3FEB2020 08:00  |
      | crew member 2 | COURSE  | LRP2 | 3FEB2020 08:00  |

      Given a trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | EWR     | 5MAR2020 02:10 | 5MAR2020 13:45 | 32N    |

      Given another trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | GOT     | 6MAR2020 08:00 | 6MAR2020 09:00 | 32N    |

      Given trip 1 is assigned to crew member 1
      Given trip 1 is assigned to crew member 2
      Given trip 2 is assigned to crew member 1
      Given trip 2 is assigned to crew member 2

      When I show "crew" in window 1

      Then the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall pass on leg 1 on trip 1 on roster 1
      and the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall pass on leg 1 on trip 1 on roster 2
      and the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall pass on leg 1 on trip 2 on roster 1
      and the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall pass on leg 1 on trip 2 on roster 2

##############################################################################

    @SCENARIO8
    Scenario: Crew with ACQUAL+A2 and POSITION+A2NX assigned to A2_OW leg is legal for FD on SH otherwise illegal
      Given Tracking
      Given crew member 1 has qualification "ACQUAL+A2" from 01JAN2019 to 31DEC2020
      Given crew member 1 has qualification "POSITION+A2_OW" from 01JAN2019 to 31DEC2020
      Given crew member 2 has qualification "ACQUAL+A2" from 01JAN2019 to 31DEC2020
      Given crew member 2 has qualification "POSITION+A2_OW" from 01JAN2019 to 31DEC2020


      Given a trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | EWR     | 5MAR2020 02:10 | 5MAR2020 13:45 | 32N    |

      Given another trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | GOT     | 6MAR2020 08:00 | 6MAR2020 09:00 | 32N    |

      Given trip 1 is assigned to crew member 1
      Given trip 1 is assigned to crew member 2 in position FC
      Given trip 2 is assigned to crew member 1
      Given trip 2 is assigned to crew member 2 in position FC

      When I show "crew" in window 1

      Then the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall fail on leg 1 on trip 1 on roster 1
      and rave "rules_qual_ccr.%qln_ac_types_failtext_leg%" shall be "OMA: Qual. AC-type A2NX requires Position A2NX" on leg 1 on trip 1 on roster 1
      and the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall fail on leg 1 on trip 1 on roster 2
      and rave "rules_qual_ccr.%qln_ac_types_failtext_leg%" shall be "OMA: Qual. AC-type A2 requires Position A2NX for LH flights" on leg 1 on trip 1 on roster 2
      and the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall fail on leg 1 on trip 2 on roster 1
      and rave "rules_qual_ccr.%qln_ac_types_failtext_leg%" shall be "OMA: Qual. AC-type A2NX requires Position A2NX" on leg 1 on trip 2 on roster 1
      and the rule "rules_qual_ccr.qln_ac_type_ok_ALL" shall pass on leg 1 on trip 2 on roster 2

##############################################################################
