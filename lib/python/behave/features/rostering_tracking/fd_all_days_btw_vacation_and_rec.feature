# Author: Andreas Larsson
# Developed for JIRA: SKCMS-2058

@planning @FD
Feature: PC or OPC activity too soon after vacation.
Background:
    Given planning period from 1mar2018 to 31mar2018

    ###################################################################################
    @scenario1
    Scenario: Check that rule fails if PC is too soon after vacation.

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | title rank      | FC        |            |          |
    | region          | SKS       |            |          |

    Given crew member 1 has a personal activity "VA" at station "STO" that starts at 1MAR2018 23:00 and ends at 7MAR2018 23:00

    Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | S3   | ARN     | ARN     | 10MAR2018 | 14:00 | 18:00 |
    | ground | S3   | ARN     | ARN     | 11MAR2018 | 14:00 | 18:00 |

    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="SKILL TEST"

    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1MAR2018 00:00"
    When I set parameter "fundamental.%end_para%" to "31MAR2018 00:00"
    Then the rule "rules_qual_ccr.min_days_btw_vacation_and_rec" shall fail on leg 1 on trip 2 on roster 1
    and the rule "rules_qual_ccr.min_days_btw_vacation_and_rec" shall fail on leg 2 on trip 2 on roster 1

    ###################################################################################
    @scenario2
    Scenario: Check that rule passes when PC or OPC is enough days from vacation.

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | title rank      | FC        |            |          |
    | region          | SKS       |            |          |

    Given crew member 1 has a personal activity "VA" at station "STO" that starts at 1MAR2018 23:00 and ends at 7MAR2018 23:00

    Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | S3   | ARN     | ARN     | 14MAR2018 | 14:00 | 18:00 |
    | ground | S3   | ARN     | ARN     | 15MAR2018 | 14:00 | 18:00 |

    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="SKILL TEST"

    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1MAR2018 00:00"
    When I set parameter "fundamental.%end_para%" to "31MAR2018 00:00"
    Then the rule "rules_qual_ccr.min_days_btw_vacation_and_rec" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_qual_ccr.min_days_btw_vacation_and_rec" shall pass on leg 2 on trip 2 on roster 1

    ###################################################################################
    @scenario3
    Scenario: Check that rule fails when PC duty is too soon after vacation even when preceded with other duties in trip.

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | title rank      | FC        |            |          |
    | region          | SKS       |            |          |

    Given crew member 1 has a personal activity "VA" at station "STO" that starts at 1MAR2018 23:00 and ends at 7MAR2018 23:00

    Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | WTA1 | ARN     | ARN     | 10MAR2018 | 06:00 | 12:00 |
    | ground | S3   | ARN     | ARN     | 11MAR2018 | 16:00 | 18:00 |

    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="SKILL TEST"

    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1MAR2018 00:00"
    When I set parameter "fundamental.%end_para%" to "31MAR2018 00:00"
    Then the rule "rules_qual_ccr.min_days_btw_vacation_and_rec" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_qual_ccr.min_days_btw_vacation_and_rec" shall fail on leg 2 on trip 2 on roster 1

    ###################################################################################
    @scenario4
    Scenario: Check that rule passes when PC duty is enough days from vacation even when preceded with other duties in trip.

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | title rank      | FC        |            |          |
    | region          | SKS       |            |          |

    Given crew member 1 has a personal activity "VA" at station "STO" that starts at 1MAR2018 23:00 and ends at 7MAR2018 23:00

    Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | WTA1 | ARN     | ARN     | 15MAR2018 | 06:00 | 12:00 |
    | ground | S3   | ARN     | ARN     | 16MAR2018 | 16:00 | 20:00 |

    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="SKILL TEST"

    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1MAR2018 00:00"
    When I set parameter "fundamental.%end_para%" to "31MAR2018 00:00"
    Then the rule "rules_qual_ccr.min_days_btw_vacation_and_rec" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_qual_ccr.min_days_btw_vacation_and_rec" shall pass on leg 2 on trip 2 on roster 1

    ###################################################################################
    @scenario5
    Scenario: Check that rule is on duty level.

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | title rank      | FC        |            |          |
    | region          | SKS       |            |          |

    Given crew member 1 has a personal activity "VA" at station "STO" that starts at 1MAR2018 23:00 and ends at 7MAR2018 23:00

    Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | WTA1 | ARN     | ARN     | 11MAR2018 | 06:00 | 12:00 |
    | ground | S3   | ARN     | ARN     | 12MAR2018 | 16:00 | 20:00 |
    | ground | S3   | ARN     | ARN     | 16MAR2018 | 16:00 | 20:00 |

    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="SKILL TEST"

    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1MAR2018 00:00"
    When I set parameter "fundamental.%end_para%" to "31MAR2018 00:00"
    Then the rule "rules_qual_ccr.min_days_btw_vacation_and_rec" shall fail on leg 2 on trip 2 on roster 1
    and the rule "rules_qual_ccr.min_days_btw_vacation_and_rec" shall pass on leg 3 on trip 2 on roster 1
