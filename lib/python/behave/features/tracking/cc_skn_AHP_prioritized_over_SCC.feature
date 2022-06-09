@JCT @TRACKING

Feature: Norwegian AH/AS with qual POSITION+AHP gets priority over crew with POSITION+SCC to get AP position assigned

########################
# JIRA - SKCMS-2513
########################

Background:
    Given Tracking
    Given planning period from 1SEP2020 to 30SEP2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | sex             | F          |            |           |
           | crew rank       | AH         | 13MAY2013  | 31DEC2035 |
           | region          | SKN        | 13MAY2013  | 31DEC2035 |
           | base            | OSL        | 13MAY2013  | 31DEC2035 |
           | title rank      | AH         | 13MAY2013  | 31DEC2035 |
           | contract        | V851       | 01DEC2015  | 31DEC2035 |

    Given crew member 1 has qualification "POSITION+SCC" from 08FEB2017 to 31DEC2035

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | sex             | F          |            |           |
           | crew rank       | AH         | 01JAN2018  | 01OCT2021 |
           | region          | SKN        | 01JAN2018  | 01OCT2021 |
           | base            | OSL        | 01JAN2018  | 01OCT2021 |
           | title rank      | AH         | 01JAN2018  | 01OCT2021 |
           | contract        | V1030      | 01JAN2020  | 01OCT2021 |
    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | sex             | F          |            |           |
           | crew rank       | AH         | 01JAN2018  | 01OCT2021 |
           | region          | SKN        | 01JAN2018  | 01OCT2021 |
           | base            | OSL        | 01JAN2018  | 01OCT2021 |
           | title rank      | AH         | 01JAN2018  | 01OCT2021 |
           | contract        | V1030      | 01JAN2020  | 01OCT2021 |

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | sex             | F          |            |           |
           | crew rank       | AH         | 01JAN2018  | 01OCT2021 |
           | region          | SKN        | 01JAN2018  | 01OCT2021 |
           | base            | OSL        | 01JAN2018  | 01OCT2021 |
           | title rank      | AH         | 01JAN2018  | 01OCT2021 |
           | contract        | V1030      | 01JAN2020  | 01OCT2021 |

    Given table crew_seniority is overridden with the following
            | crew     | grp   | validfrom  | validto    | seniority | si   |
            | Crew001  | SAS   | 01AUG2020  | 31DEC2020  | 220       |      |
            | Crew002  | SAS   | 01AUG2020  | 31DEC2020  | 527       |      |

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000844  | OSL     | ARN     | 10SEP2020 05:00 | 10SEP2020 06:05 | 32J     |         |
           | leg     | SK      | 000847  | ARN     | OSL     | 10SEP2020 07:00 | 10SEP2020 08:00 | 32J     |         |

    Given trip 1 is assigned to crew member 3 in position AH
    Given trip 1 is assigned to crew member 4 in position AH


    @SCENARIO_1
    Scenario: Crew1 assigned to AP and Crew2 assigned to AH, without AHP qualification

    Given trip 1 is assigned to crew member 1 in position AP
    Given trip 1 is assigned to crew member 2 in position AH

    When I show "crew" in window 1
    Then rave "crew.%is_ahp%(leg.%start_hb%)" shall be "False" on leg 1 on trip 1 on roster 2
    and rave "rules_indust_cct.%most_senior_AHP%" shall be "?????" on leg 1 on trip 1 on roster 2
    and the rule "rules_indust_cct.comp_assigned_in_ap_must_be_most_senior_AHP" shall pass on trip 1 on roster 2


    @SCENARIO_2
    Scenario: Crew1 assigned to AP and Crew2 assigned to AH, with AHP qualification

    Given crew member 2 has qualification "POSITION+AHP" from 01JAN1980 to 31DEC2035
    Given trip 1 is assigned to crew member 1 in position AP
    Given trip 1 is assigned to crew member 2 in position AH

    When I show "crew" in window 1
    Then rave "crew.%is_ahp%(leg.%start_hb%)" shall be "True" on leg 1 on trip 1 on roster 2
    and rave "rules_indust_cct.%most_senior_AHP%" shall be "Crew002" on leg 1 on trip 1 on roster 2
    and the rule "rules_indust_cct.comp_assigned_in_ap_must_be_most_senior_AHP" shall fail on trip 1 on roster 1


    @SCENARIO_3
    Scenario: Crew1 assigned to AH and Crew2 assigned to AP, without AHP qualification

    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 1 is assigned to crew member 2 in position AP

    When I show "crew" in window 1
    Then rave "crew.%is_ahp%(leg.%start_hb%)" shall be "False" on leg 1 on trip 1 on roster 2
    and rave "rules_indust_cct.%most_senior_AHP%" shall be "?????" on leg 1 on trip 1 on roster 2
    and the rule "rules_indust_cct.comp_assigned_in_ap_must_be_most_senior_AHP" shall pass on trip 1 on roster 2


    @SCENARIO_4
    Scenario: Crew1 assigned to AH and Crew2 assigned to AP, with AHP qualification

    Given crew member 2 has qualification "POSITION+AHP" from 01JAN1980 to 31DEC2035
    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 1 is assigned to crew member 2 in position AP

    When I show "crew" in window 1
    Then rave "crew.%is_ahp%(leg.%start_hb%)" shall be "True" on leg 1 on trip 1 on roster 2
    and rave "rules_indust_cct.%most_senior_AHP%" shall be "Crew002" on leg 1 on trip 1 on roster 2
    and the rule "rules_indust_cct.comp_assigned_in_ap_must_be_most_senior_AHP" shall pass on trip 1 on roster 2
