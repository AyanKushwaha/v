Feature: Rule for enabling longhaul after shorthaul (SFO/LAX) for SKD CC in FG

    ############################################################################
    # Scenarios that shall pass
    ############################################################################

        @SCENARIO_1
        Scenario: Shorthaul duty prior to longhaul duty CPH to SFO eligible for Swedish crew in fixed groups
        Given planning period from 1Oct2018 to 31Oct2018

        Given a crew member with
        | attribute  | value  | valid from | valid to
        | base       | ARN    |            |
        | title rank | AS     |            |
        | region     | SKS    |            |
        Given crew member 1 has contract "F00102"

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ  |
        | leg | 0001 | ARN     | OSL     | 12Oct2018 | 15:55 | 16:55 | SK  | 320     |
        | leg | 0002 | OSL     | ARN     | 12Oct2018 | 17:55 | 18:55 | SK  | 320     |
        | dh  | 0003 | ARN     | CPH     | 12Oct2018 | 20:25 | 21:25 | SK  | 320     |
        | leg | 0004 | CPH     | SFO     | 13Oct2018 | 11:05 | 23:30 | SK  | 33A     |
        | leg | 0005 | SFO     | CPH     | 15Oct2018 | 10:00 | 21:45 | SK  | 33A     |
        | dh  | 0006 | CPH     | ARN     | 15Oct2018 | 22:45 | 23:45 | SK  | 320     |

        Given trip 1 is assigned to crew member 1

        When I show "crew" in window 1
        When I load rule set "rule_set_jct"
        Then the rule "rules_indust_ccr.ind_union_production_before_far_timeszones_not_allowed" shall pass on leg 2 on trip 1 on roster 1
        and rave "crew.%in_fixed_group_at_date%(15Oct2018)" shall be "True" on leg 2 on trip 1 on roster 1

        @SCENARIO_2
        Scenario: Two shorthaul dutys prior to longhaul duty CPH to SFO eligible for Swedish crew in fixed groups
        Given planning period from 1Oct2018 to 31Oct2018

        Given a crew member with
        | attribute  | value  | valid from | valid to
        | base       | ARN    |            |
        | title rank | AS     |            |
        | region     | SKS    |            |
        Given crew member 1 has contract "F00102"

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ  |
        | leg | 0001 | ARN     | OSL     | 11Oct2018 | 14:55 | 15:55 | SK  | 320     |
        | leg | 0002 | OSL     | ARN     | 11Oct2018 | 16:55 | 17:55 | SK  | 320     |
        | leg | 0001 | ARN     | OSL     | 12Oct2018 | 15:55 | 16:55 | SK  | 320     |
        | leg | 0002 | OSL     | ARN     | 12Oct2018 | 17:55 | 18:55 | SK  | 320     |
        | dh  | 0003 | ARN     | CPH     | 12Oct2018 | 20:25 | 21:25 | SK  | 320     |
        | leg | 0004 | CPH     | SFO     | 13Oct2018 | 11:05 | 23:30 | SK  | 33A     |
        | leg | 0005 | SFO     | CPH     | 15Oct2018 | 10:00 | 21:45 | SK  | 33A     |
        | dh  | 0006 | CPH     | ARN     | 15Oct2018 | 22:45 | 23:45 | SK  | 320     |

        Given trip 1 is assigned to crew member 1

        When I show "crew" in window 1
        When I load rule set "rule_set_jct"
        Then the rule "rules_indust_ccr.ind_union_production_before_far_timeszones_not_allowed" shall pass on leg 2 on trip 1 on roster 1
        and rave "crew.%in_fixed_group_at_date%(15Oct2018)" shall be "True" on leg 2 on trip 1 on roster 1

        @SCENARIO_3
        Scenario: Longhaul without shorthaul duty CPH to SFO eligible for Swedish crew in fixed groups
        Given planning period from 1Oct2018 to 31Oct2018

        Given a crew member with
        | attribute  | value  | valid from | valid to
        | base       | ARN    |            |
        | title rank | AS     |            |
        | region     | SKS    |            |
        Given crew member 1 has contract "F00102"

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ  |
        | leg | 0004 | CPH     | SFO     | 13Oct2018 | 11:05 | 23:30 | SK  | 33A     |
        | leg | 0005 | SFO     | CPH     | 15Oct2018 | 10:00 | 21:45 | SK  | 33A     |
        | dh  | 0006 | CPH     | ARN     | 15Oct2018 | 22:45 | 23:45 | SK  | 320     |

        Given trip 1 is assigned to crew member 1

        When I show "crew" in window 1
        When I load rule set "rule_set_jct"
        Then the rule "rules_indust_ccr.ind_union_production_before_far_timeszones_not_allowed" shall pass on leg 2 on trip 1 on roster 1
        and rave "crew.%in_fixed_group_at_date%(15Oct2018)" shall be "True" on leg 2 on trip 1 on roster 1

        @SCENARIO_4
        Scenario: Shorthaul duty not ending at homebase without deadhead prior to longhaul duty CPH to SFO eligible for Swedish crew in fixed groups
        Given planning period from 1Oct2018 to 31Oct2018

        Given a crew member with
        | attribute  | value  | valid from | valid to
        | base       | ARN    |            |
        | title rank | AS     |            |
        | region     | SKS    |            |
        Given crew member 1 has contract "F00102"

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ  |
        | leg | 0001 | ARN     | OSL     | 12Oct2018 | 15:55 | 16:55 | SK  | 320     |
        | leg | 0002 | OSL     | CPH     | 12Oct2018 | 17:55 | 18:55 | SK  | 320     |
        | leg | 0004 | CPH     | SFO     | 13Oct2018 | 11:05 | 23:30 | SK  | 33A     |
        | leg | 0005 | SFO     | CPH     | 15Oct2018 | 10:00 | 21:45 | SK  | 33A     |
        | dh  | 0006 | CPH     | ARN     | 15Oct2018 | 22:45 | 23:45 | SK  | 320     |

        Given trip 1 is assigned to crew member 1

        When I show "crew" in window 1
        When I load rule set "rule_set_jct"
        Then the rule "rules_indust_ccr.ind_union_production_before_far_timeszones_not_allowed" shall pass on leg 2 on trip 1 on roster 1
        and rave "crew.%in_fixed_group_at_date%(15Oct2018)" shall be "True" on leg 2 on trip 1 on roster 1
