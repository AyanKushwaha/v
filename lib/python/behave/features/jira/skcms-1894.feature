@tracking
#These tests are intended to be tested in tracking studio, behaviour in planning has not been taken into account.
# "rules_indust_ccr.ind_max_fs_days_month" uses accumulators which is currently not supported, would be good to use in the future.

Feature: Evaluation of SKCMS-1894, three FS days for SKD CC Crew.

    Background: Set up for tracking

###################################################################################

    Scenario: Single FS in month
    Given planning period from 01JUL2018 to 31JUL2018


    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"


    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | FS   | CPH     | CPH     | 07JUL2018 | 00:00 | 23:59 |

    Given trip 1 is assigned to crew member 1 in position AP

    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1JUL2018 00:00"
    When I set parameter "fundamental.%end_para%" to "31JUL2018 00:00"
    Then the rule "rules_indust_ccr.ind_incorrect_separated_fs_days" shall pass on leg 1 on trip 1 on roster 1
    # and the rule "rules_indust_ccr.ind_max_fs_days_month" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_consecutive_fs_days" shall pass on leg 1 on trip 1 on roster 1

###################################################################################

    Scenario: Two (1 + 1) FS in month
    Given planning period from 01JUL2018 to 31JUL2018


    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | FS   | CPH     | CPH     | 07JUL2018 | 00:00 | 23:59 |

    Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | FS   | CPH     | CPH     | 24JUL2018 | 00:00 | 23:59 |

    Given trip 1 is assigned to crew member 1 in position AP
    Given trip 2 is assigned to crew member 1 in position AP

    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1JUL2018 00:00"
    When I set parameter "fundamental.%end_para%" to "31JUL2018 00:00"
    Then the rule "rules_indust_ccr.ind_incorrect_separated_fs_days" shall pass on leg 1 on trip 2 on roster 1
    # and the rule "rules_indust_ccr.ind_max_fs_days_month" shall pass on leg 1 on trip 2 on roster 1

###################################################################################

    Scenario: Three (2 + 1) FS in month
    Given planning period from 01JUL2018 to 31JUL2018


    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | FS   | CPH     | CPH     | 07JUL2018 | 00:00 | 23:59 |

    Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | FS   | CPH     | CPH     | 08JUL2018 | 00:00 | 23:59 |

    Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | FS   | CPH     | CPH     | 24JUL2018 | 00:00 | 23:59 |

    Given trip 1 is assigned to crew member 1 in position AP
    Given trip 2 is assigned to crew member 1 in position AP
    Given trip 3 is assigned to crew member 1 in position AP

    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1JUL2018 00:00"
    When I set parameter "fundamental.%end_para%" to "31JUL2018 00:00"
    Then the rule "rules_indust_ccr.ind_incorrect_separated_fs_days" shall pass on leg 1 on trip 1 on roster 1
    # and the rule "rules_indust_ccr.ind_max_fs_days_month" shall pass on leg 1 on trip 1 on roster 1

###################################################################################

    Scenario: Three (1 + 2) FS in month
    Given planning period from 01JUL2018 to 31JUL2018


    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | FS   | CPH     | CPH     | 07JUL2018 | 00:00 | 23:59 |

    Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | FS   | CPH     | CPH     | 23JUL2018 | 00:00 | 23:59 |

    Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | FS   | CPH     | CPH     | 24JUL2018 | 00:00 | 23:59 |

    Given trip 1 is assigned to crew member 1 in position AP
    Given trip 2 is assigned to crew member 1 in position AP
    Given trip 3 is assigned to crew member 1 in position AP

    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1JUL2018 00:00"
    When I set parameter "fundamental.%end_para%" to "31JUL2018 00:00"
    Then the rule "rules_indust_ccr.ind_incorrect_separated_fs_days" shall pass on leg 1 on trip 1 on roster 1
    # and the rule "rules_indust_ccr.ind_max_fs_days_month" shall pass on leg 1 on trip 1 on roster 1

###################################################################################

    Scenario: Three bundled FS in month
    Given planning period from 01JUL2018 to 31JUL2018


    Given a crew member with
    | attribute       | value     | valid from | valid to |s
    | base            | CPH       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | FS   | CPH     | CPH     | 07JUL2018 | 00:00 | 23:59 |

    Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | FS   | CPH     | CPH     | 08JUL2018 | 00:00 | 23:59 |

    Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | FS   | CPH     | CPH     | 09JUL2018 | 00:00 | 23:59 |

    Given trip 1 is assigned to crew member 1 in position AP
    Given trip 2 is assigned to crew member 1 in position AP
    Given trip 3 is assigned to crew member 1 in position AP

    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1JUL2018 00:00"
    When I set parameter "fundamental.%end_para%" to "31JUL2018 00:00"
    Then the rule "rules_indust_ccr.ind_incorrect_separated_fs_days" shall pass on leg 1 on trip 1 on roster 1
    # and the rule "rules_indust_ccr.ind_max_fs_days_month" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_consecutive_fs_days" shall fail on leg 1 on trip 1 on roster 1

###################################################################################

    Scenario: Three (1 + 1 + 1) FS in month
    Given planning period from 01JUL2018 to 31JUL2018


    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | FS   | CPH     | CPH     | 07JUL2018 | 00:00 | 23:59 |

    Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | FS   | CPH     | CPH     | 15JUL2018 | 00:00 | 23:59 |

    Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | FS   | CPH     | CPH     | 21JUL2018 | 00:00 | 23:59 |

    #Given a trip with the following activities
    #| act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    #| leg | 0001 | CPH     | LHR     | 10JUL2018 | 10:00 | 11:00 | SK  | 320    |

    #Given a trip with the following activities
    #| act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    #| leg | 0001 | CPH     | LHR     | 18JUL2018 | 10:00 | 11:00 | SK  | 320    |


    Given trip 1 is assigned to crew member 1 in position AP
    Given trip 2 is assigned to crew member 1 in position AP
    Given trip 3 is assigned to crew member 1 in position AP
    #Given trip 4 is assigned to crew member 1 in position AP
    #Given trip 5 is assigned to crew member 1 in position AP

    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1JUL2018 00:00"
    When I set parameter "fundamental.%end_para%" to "31JUL2018 00:00"
    Then the rule "rules_indust_ccr.ind_incorrect_separated_fs_days" shall fail on leg 1 on trip 1 on roster 1
    # and the rule "rules_indust_ccr.ind_max_fs_days_month" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_consecutive_fs_days" shall pass on leg 1 on trip 1 on roster 1


###################################################################################

    Scenario: Four bundled FS in month
    Given planning period from 01JUL2018 to 31JUL2018


    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | FS   | CPH     | CPH     | 07JUL2018 | 00:00 | 23:59 |

    Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | FS   | CPH     | CPH     | 08JUL2018 | 00:00 | 23:59 |

    Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | FS   | CPH     | CPH     | 09JUL2018 | 00:00 | 23:59 |

    Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | FS   | CPH     | CPH     | 10JUL2018 | 00:00 | 23:59 |

    Given trip 1 is assigned to crew member 1 in position AP
    Given trip 2 is assigned to crew member 1 in position AP
    Given trip 3 is assigned to crew member 1 in position AP
    Given trip 4 is assigned to crew member 1 in position AP

    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1JUL2018 00:00"
    When I set parameter "fundamental.%end_para%" to "31JUL2018 00:00"
    Then the rule "rules_indust_ccr.ind_incorrect_separated_fs_days" shall pass on leg 1 on trip 1 on roster 1
    # and the rule "rules_indust_ccr.ind_max_fs_days_month" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_consecutive_fs_days" shall fail on leg 1 on trip 1 on roster 1


###################################################################################

    Scenario: Four (2 + 2) bundled FS in month
    Given planning period from 01JUL2018 to 31JUL2018


    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | FS   | CPH     | CPH     | 07JUL2018 | 00:00 | 23:59 |

    Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | FS   | CPH     | CPH     | 08JUL2018 | 00:00 | 23:59 |

    Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | FS   | CPH     | CPH     | 14JUL2018 | 00:00 | 23:59 |

    Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | FS   | CPH     | CPH     | 15JUL2018 | 00:00 | 23:59 |

    Given trip 1 is assigned to crew member 1 in position AP
    Given trip 2 is assigned to crew member 1 in position AP
    Given trip 3 is assigned to crew member 1 in position AP
    Given trip 4 is assigned to crew member 1 in position AP

    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1JUL2018 00:00"
    When I set parameter "fundamental.%end_para%" to "31JUL2018 00:00"
    Then the rule "rules_indust_ccr.ind_incorrect_separated_fs_days" shall pass on leg 1 on trip 1 on roster 1
    # and the rule "rules_indust_ccr.ind_max_fs_days_month" shall fail on leg 1 on trip 1 on roster 1

###################################################################################



