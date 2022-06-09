@JCT @TRACKING

Feature: crew travelling to China must have a passport valid for at least 6 months

########################
# JIRA - SKCMS-2521
########################

Background:
    Given Tracking
    Given planning period from 1OCT2020 to 31OCT2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AP         | 02NOV2018  | 01JAN2036 |
           | region          | SKS        | 02NOV2018  | 01JAN2036 |
           | base            | STO        | 02NOV2018  | 01JAN2036 |
           | title rank      | AP         | 02NOV2018  | 01JAN2036 |

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000997  | CPH     | PVG     | 13OCT2020 16:40 | 14OCT2020 02:55 | 35A     |         |
    Given trip 1 is assigned to crew member 1 in position AP


  @SCENARIO_1
  Scenario: passport valid less than 6 months after trip

  Given table crew_document additionally contains the following
        |crew         | doc_typ    | doc_subtype | validfrom | validto    | docno | maindocno | issuer| si | ac_qual|
        |Crew001      | PASSPORT   | SE,1        | 01JAN2020 | 10APR2021  |       |           |       |    |        |

  When I show "crew" in window 1
  Then the rule "rules_doc_cct.has_valid_passport_China" shall fail on leg 1 on trip 1 on roster 1

  @SCENARIO_2
  Scenario: passport valid 6 months after trip

  Given table crew_document additionally contains the following
        |crew         | doc_typ    | doc_subtype | validfrom | validto    | docno | maindocno | issuer| si | ac_qual|
        |Crew001      | PASSPORT   | SE,1        | 01JAN2020 | 15APR2021  |       |           |       |    |        |

  When I show "crew" in window 1
  Then the rule "rules_doc_cct.has_valid_passport_China" shall pass on leg 1 on trip 1 on roster 1

  @SCENARIO_3
  Scenario: if several passports use the one with the longest validity

  Given table crew_document additionally contains the following
        |crew         | doc_typ    | doc_subtype | validfrom | validto    | docno | maindocno | issuer| si | ac_qual|
        |Crew001      | PASSPORT   | SE,1        | 01JAN2020 | 15APR2021  |       |           |       |    |        |
        |Crew001      | PASSPORT   | SE,2        | 01JAN2020 | 30DEC2020  |       |           |       |    |        |

  When I show "crew" in window 1
  Then rave "rules_doc_cct.%passport_valid_to_hb%" shall be "15APR2021 00:00" on leg 1 on trip 1 on roster 1