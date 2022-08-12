@tracking @vacation @fs1 @skn @cc
Feature: Testing rule that evaluates if FS1 days are valid to place immediately after VA or VA1. (SKCMS-1910)
Only applies to CC SKN, which is divided into SNK and NKF.

    Background: Setup for tracking
      Given Tracking
      Given planning period from 1oct2018 to 31oct2018

##########################################################################################
# Scenarios that shall pass
##########################################################################################

    @scenario1 @VA1 @SNK
    Scenario: 1. FS1 is placed on single-day weekend directly after VA1 longer than 6 days. Crew shall be in agreement SNK
    Covers VA1 + agreement SNK + Saturday

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | AH     |
    | region     | SKN    |
    Given crew member 1 has contract "V00210"
    and crew member 1 has a personal activity "VA1" at station "OSL" that starts at 12oct2018 22:00 and ends at 19oct2018 22:00
    and crew member 1 has a personal activity "FS1" at station "OSL" that starts at 19oct2018 22:00 and ends at 20oct2018 22:00

    When I show "crew" in window 1
    Then rave "crew.%has_agmt_group_snk_cc_at_date%(21Oct2018)" shall be "True" on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall pass on leg 1 on trip 2 on roster 1

##########################################################################################

    @scenario1.1 @VA @NKF
    Scenario: 1.1. FS1 is placed on single-day weekend directly after VA longer than 6 days. Crew shall be in agreement NKF
    Covers VA + agreement NKF + Sunday

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | AH     |
    | region     | SKN    |
    Given crew member 1 has contract "V00207"
    and crew member 1 has a personal activity "VA" at station "OSL" that starts at 12oct2018 22:00 and ends at 20oct2018 22:00
    and crew member 1 has a personal activity "FS1" at station "OSL" that starts at 20oct2018 22:00 and ends at 21oct2018 22:00

    When I show "crew" in window 1
    Then rave "crew.%has_agmt_group_nkf_cc_at_date%(21Oct2018)" shall be "True" on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall pass on leg 1 on trip 2 on roster 1

##########################################################################################

    @scenario2 @VA1 @NKF
    Scenario: 2. FS1 is placed on full weekend directly after VA longer than 6 days. Crew shall be in agreement NKF
    Covers VA + agreement NKF + full weekend

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | AH     |
    | region     | SKN    |
    Given crew member 1 has contract "V00207"
    and crew member 1 has a personal activity "VA1" at station "OSL" that starts at 12oct2018 22:00 and ends at 19oct2018 22:00
    and crew member 1 has a personal activity "FS1" at station "OSL" that starts at 19oct2018 22:00 and ends at 21oct2018 22:00

    When I show "crew" in window 1
    Then rave "crew.%has_agmt_group_nkf_cc_at_date%(21Oct2018)" shall be "True" on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall pass on leg 1 on trip 2 on roster 1

##########################################################################################
# Scenarios that shall fail
##########################################################################################

    @scenario3 @VA1 @NKF
    Scenario: 3. FS1 is placed on single-day weekend with a break after VA longer than 6 days. Crew shall be in agreement NKF

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | AH     |
    | region     | SKN    |
    Given crew member 1 has contract "V00207"
    and crew member 1 has a personal activity "VA1" at station "OSL" that starts at 12oct2018 22:00 and ends at 19oct2018 22:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 20oct2018 22:00 and ends at 21oct2018 22:00

    When I show "crew" in window 1
    Then rave "crew.%has_agmt_group_nkf_cc_at_date%(21Oct2018)" shall be "True" on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 2 on roster 1

##########################################################################################

    @scenario4 @LA @SNK
    Scenario: 4. FS is placed on weekend one day after LA longer than 6 days. Crew shall be in SNK.
    Rule shall not be valid for other activities than in activity set VAC

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | AH     |
    | region     | SKN    |
    Given crew member 1 has contract "V00210"
    and crew member 1 has a personal activity "LA" at station "OSL" that starts at 12oct2018 22:00 and ends at 19oct2018 22:00
    and crew member 1 has a personal activity "FS1" at station "OSL" that starts at 19oct2018 22:00 and ends at 20oct2018 22:00

    When I show "crew" in window 1
    Then rave "crew.%has_agmt_group_snk_cc_at_date%(20Oct2018)" shall be "True" on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 2 on roster 1

##########################################################################################

    @scenario5 @VA1 @SNK
    Scenario: 5. FS is placed on weekend one day after VA less than 6 days. Crew shall be in SNK.
    Rule shall not be valid unless VA is more than 6 days

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | AH     |
    | region     | SKN    |
    Given crew member 1 has contract "V00210"
    and crew member 1 has a personal activity "VA1" at station "OSL" that starts at 13oct2018 22:00 and ends at 19oct2018 22:00
    and crew member 1 has a personal activity "FS1" at station "OSL" that starts at 19oct2018 22:00 and ends at 20oct2018 22:00

    When I show "crew" in window 1
    Then rave "crew.%has_agmt_group_snk_cc_at_date%(20Oct2018)" shall be "True" on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 2 on roster 1

