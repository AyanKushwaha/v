# Author: Kristoffer Thun
# Developed for JIRA: SKCMS-1959

@planning @FD
Feature: Add AST to rule min days between vacation and rec.
Background:
    Given planning period from 1mar2018 to 31mar2018


    @scenario1
    Scenario: Check that rule fails if AST activity is too soon after vacation.

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | title rank      | FC        |            |          |
    | region          | SKS       |            |          |

    Given crew member 1 has a personal activity "VA" at station "STO" that starts at 1MAR2018 23:00 and ends at 7MAR2018 23:00

    Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground |  K7  | ARN     | ARN     | 10MAR2018 | 14:00 | 18:00 |
    | ground |  K7  | ARN     | ARN     | 11MAR2018 | 14:00 | 18:00 |

    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="SKILL TEST"

    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1MAR2018 00:00"
    When I set parameter "fundamental.%end_para%" to "31MAR2018 00:00"
    Then the rule "rules_qual_ccr.min_days_btw_vacation_and_rec" shall fail on leg 1 on trip 2 on roster 1
    and the rule "rules_qual_ccr.min_days_btw_vacation_and_rec" shall fail on leg 2 on trip 2 on roster 1

      ###################################################################################
        @scenario2
    Scenario:  Check that rule passes when AST is enough days from vacation.

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | title rank      | FC        |            |          |
    | region          | SKS       |            |          |

    Given crew member 1 has a personal activity "VA" at station "STO" that starts at 1MAR2018 23:00 and ends at 7MAR2018 23:00

    Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground |  K7  | ARN     | ARN     | 14MAR2018 | 14:00 | 18:00 |
    | ground |  K7  | ARN     | ARN     | 15MAR2018 | 14:00 | 18:00 |

    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="SKILL TEST"

    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1MAR2018 00:00"
    When I set parameter "fundamental.%end_para%" to "31MAR2018 00:00"
    Then the rule "rules_qual_ccr.min_days_btw_vacation_and_rec" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_qual_ccr.min_days_btw_vacation_and_rec" shall pass on leg 2 on trip 2 on roster 1


