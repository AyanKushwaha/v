@TRACKING @CC @CRMC @OCRC @CREWLIST

Feature: Test that it is possible to extract crewlist for CRMC and OCRC activities.

  @SCENARIO1
  Scenario: It should be possible to extract crewlist for CRMC and OCRC activities.
    Given Tracking
    Given planning period from 1MAR2020 to 1APR2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 15APR2019  | 01JAN2036 |
           | region          | SKS        | 15APR2019  | 01JAN2036 |
           | base            | STO        | 15APR2019  | 01JAN2036 |
           | title rank      | AH         | 15APR2019  | 01JAN2036 |
           | contract        | V00863     | 19APR2019  | 31DEC2035 |

    Given crew member 1 has qualification "ACQUAL+38" from 15APR2019 to 01JAN2036
    Given crew member 1 has qualification "ACQUAL+A2" from 23JUL2019 to 01JAN2036

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | ground  |         |         | ARN     | ARN     | 27MAR2020 08:00 | 27MAR2020 15:58 |         | CRMC    |
    Given trip 1 is assigned to crew member 1 in position TL


    Given table crew_training_log additionally contains the following
           | tim             | code | typ        | attr | crew          |
           | 27MAR2020 15:58 | TW20 | COURSE WEB |      | crew member 1 |
           | 27MAR2020 08:00 | CRMC | CRM        |      | crew member 1 |

    Given another crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AA         | 04MAR2020  | 18MAR2020 |
           | region          | SKD        | 04MAR2020  | 18MAR2020 |
           | base            | CPH        | 04MAR2020  | 18MAR2020 |
           | title rank      | AA         | 04MAR2020  | 18MAR2020 |
           | contract        | V345       | 04MAR2020  | 18MAR2020 |
     Given crew member 2 has qualification "ACQUAL+FF" from 04MAR2020 to 18MAR2020


    Given crew member 2 has a personal activity "OCRC" at station "CPH" that starts at 06MAR2020 07:30 and ends at 06MAR2020 15:30
    Given crew member 2 has a personal activity "F" at station "CPH" that starts at 06MAR2020 23:00 and ends at 07MAR2020 23:00

    Given table crew_training_log additionally contains the following
           | tim             | code | typ    | attr | crew          |
           | 06MAR2020 07:30 | OCRC | CRM    |      | crew member 1 |

    When I show "crew" in window 1
    Then rave "report_crewlists.%crewlist_allowed%" shall be "True" on leg 1 on trip 1 on roster 1
  and rave "report_crewlists.%crewlist_allowed%" shall be "True" on leg 1 on trip 1 on roster 2
