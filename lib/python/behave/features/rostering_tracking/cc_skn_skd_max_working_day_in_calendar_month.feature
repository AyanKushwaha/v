@JCR @CC @SKD @SKN
Feature: Rule checks that working days are max 19

  Background:
    Given Rostering_CC
    Given planning period from 1SEP2020 to 30SEP2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AP         | 04FEB2020  | 01JAN2036 |
           | region          | SKD        | 04FEB2020  | 01JAN2036 |
           | base            | CPH        | 04FEB2020  | 01JAN2036 |
           | title rank      | AP         | 04FEB2020  | 01JAN2036 |
           | contract        | V300       | 01OCT2006  | 01OCT2021 |

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AP         | 04FEB2020  | 01JAN2036 |
           | region          | SKD        | 04FEB2020  | 01JAN2036 |
           | base            | CPH        | 04FEB2020  | 01JAN2036 |
           | title rank      | AP         | 04FEB2020  | 01JAN2036 |
           | contract        | V3012      | 01OCT2006  | 01OCT2021 |

    Given table crew_contract_set additionally contains the following
       | id     | dutypercent  | desclong           |
       | V3012  | 50           | MonthlyParttime    |

    @SCENARIO_1
    Scenario: 19 working days, rule not applicable for monthly parttime

    Given crew member 1 with homebase "CPH" has duty time that exceeds 152 hours in month SEP in 2020
    Given crew member 2 with homebase "CPH" has duty time that exceeds 152 hours in month SEP in 2020

    When I show "crew" in window 1

    Then rave "rules_indust_ccr.%_nr_prod_days_in_month_skn_skd_vg_cc%" shall be "19" on leg 1 on trip 19 on roster 1
    and the rule "rules_indust_ccr.ind_max_prod_days_in_calendar_month_skn_skd_vg_cc" shall pass on leg 1 on trip 19 on roster 1
    and rave "rules_indust_ccr.%_max_prod_days_in_calendar_month_skn_skd_vg_cc_valid%" shall be "False" on leg 1 on trip 19 on roster 2


    @SCENARIO_2
    Scenario: 20 working days, rule not applicable for monthly parttime

    Given crew member 1 with homebase "CPH" has duty time that exceeds 160 hours in month SEP in 2020
    Given crew member 2 with homebase "CPH" has duty time that exceeds 160 hours in month SEP in 2020

    When I show "crew" in window 1

    Then rave "rules_indust_ccr.%_nr_prod_days_in_month_skn_skd_vg_cc%" shall be "20" on leg 1 on trip 20 on roster 1
    and the rule "rules_indust_ccr.ind_max_prod_days_in_calendar_month_skn_skd_vg_cc" shall fail on leg 1 on trip 20 on roster 1
    and rave "rules_indust_ccr.%_max_prod_days_in_calendar_month_skn_skd_vg_cc_valid%" shall be "False" on leg 1 on trip 19 on roster 2