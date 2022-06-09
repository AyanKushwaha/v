@tracking @VA @FS @SKN @CC
Feature: Testing rule that evaluates if FS days are valid to place immediately after VA or VA1. (SKCMS-1910)
Only applies to SNK and NKF CC on full weekends.


    Background: Setup for tracking
      Given Tracking
      Given planning period from 1oct2018 to 31oct2018

##########################################################################################
# Scenarios that shall pass
##########################################################################################

    @scenario1 @SNK @V00210
    Scenario: 1. FS is placed on full weekend directly after VA1 longer than 6 days. Crew shall be in agreement SNK
    Covers VA1 + agreement SNK

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | AH     |
    | region     | SKN    |
    Given crew member 1 has contract "V00210"
    and crew member 1 has a personal activity "VA1" at station "OSL" that starts at 12oct2018 22:00 and ends at 19oct2018 22:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 19oct2018 22:00 and ends at 21oct2018 22:00

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall pass on leg 1 on trip 2 on roster 1
    and rave "crew.%has_agmt_group_snk_cc_at_date%(21Oct2018)" shall be "True" on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 2 on roster 1

##########################################################################################
    @scenario1.1 @SNK @V00210
    Scenario: 1.1 1 FS is placed on weekday directly after VA1 longer than 6 days.

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | AH     |
    | region     | SKN    |
    Given crew member 1 has contract "V00210"
    and crew member 1 has a personal activity "VA1" at station "OSL" that starts at 14oct2018 22:00 and ends at 21oct2018 22:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 21oct2018 22:00 and ends at 22oct2018 22:00

    When I show "crew" in window 1

    Then rave "crew.%has_agmt_group_snk_cc_at_date%(21Oct2018)" shall be "True" on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 2 on roster 1

##########################################################################################
    @scenario1.2 @SNK @V00210
    Scenario: 1.2 2 FS is placed on weekday directly after VA1 longer than 6 days.

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | AH     |
    | region     | SKN    |
    Given crew member 1 has contract "V00210"
    and crew member 1 has a personal activity "VA1" at station "OSL" that starts at 14oct2018 22:00 and ends at 21oct2018 22:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 21oct2018 22:00 and ends at 23oct2018 22:00

    When I show "crew" in window 1

    Then rave "crew.%has_agmt_group_snk_cc_at_date%(21Oct2018)" shall be "True" on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 2 on roster 1

##########################################################################################
    @scenario1.3 @SNK @V00210
    Scenario: 1.3 1 FS is placed on weekday one day after VA1 longer than 6 days.

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | AH     |
    | region     | SKN    |
    Given crew member 1 has contract "V00210"
    and crew member 1 has a personal activity "VA1" at station "OSL" that starts at 14oct2018 22:00 and ends at 21oct2018 22:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 22oct2018 22:00 and ends at 23oct2018 22:00

    When I show "crew" in window 1

    Then rave "crew.%has_agmt_group_snk_cc_at_date%(21Oct2018)" shall be "True" on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 2 on roster 1

##########################################################################################

    @scenario2 @V00207 @NKF
    Scenario: 2. FS is placed on full weekend directly after VA longer than 6 days. Crew shall be in agreement NKF
    Covers VA + agreement NKF

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | AH     |
    | region     | SKN    |
    Given crew member 1 has contract "V00207"
    and crew member 1 has a personal activity "VA1" at station "OSL" that starts at 12oct2018 22:00 and ends at 19oct2018 22:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 19oct2018 22:00 and ends at 21oct2018 22:00

    When I show "crew" in window 1

    Then rave "crew.%has_agmt_group_nkf_cc_at_date%(21Oct2018)" shall be "True" on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 2 on roster 1

##########################################################################################

    @scenario2.1 @SNK @V00210
    Scenario: 2.1 FS is placed partially on weekend or week day

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | AH     |
    | region     | SKN    |
    Given crew member 1 has contract "V00210"
    and crew member 1 has a personal activity "VA1" at station "OSL" that starts at 6oct2018 22:00 and ends at 13oct2018 22:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 19oct2018 22:00 and ends at 21oct2018 22:00

    When I show "crew" in window 1

    Then rave "crew.%has_agmt_group_snk_cc_at_date%(20Oct2018)" shall be "True" on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall pass on leg 1 on trip 2 on roster 1


##########################################################################################
# Scenarios that shall fail
##########################################################################################

    @scenario3 @V00207 @NKF
    Scenario: 3. FS is placed on weekend (Saturday) directly after VA1 longer than 6 days. Crew shall be in agreement NKF
    Covers Saturday + agreement NKF + VA1

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | AH     |
    | region     | SKN    |
    Given crew member 1 has contract "V00207"
    and crew member 1 has a personal activity "VA1" at station "OSL" that starts at 11oct2018 22:00 and ends at 19oct2018 22:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 19oct2018 22:00 and ends at 20oct2018 22:00

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_fs_days_in_weekend_covers_both_saturday_and_sunday" shall fail on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 2 on roster 1

################################################################################################

    @scenario4 @SNK @V00210
    Scenario: 4. FS is placed on weekend (Sunday) directly after VA longer than 6 days. Crew shall be in agreement SNK
    Covers Sunday + agreement SNK + VA1

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | AH     |
    | region     | SKN    |
    Given crew member 1 has contract "V00210"
    and crew member 1 has a personal activity "VA1" at station "OSL" that starts at 12oct2018 22:00 and ends at 20oct2018 22:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 20oct2018 22:00 and ends at 21oct2018 22:00

    When I show "crew" in window 1

    Then rave "crew.%has_agmt_group_snk_cc_at_date%(21Oct2018)" shall be "True" on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_days_in_weekend_covers_both_saturday_and_sunday" shall fail on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 2 on roster 1

################################################################################################

    @scenario5
    Scenario: 5. FS is placed on weekend directly after VA longer than 6 days. Crew is not in SNK or NKF
    Covers crew not in accepted agreement group

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | AH     |
    | region     | SKN    |
    Given crew member 1 has contract "V00199"
    and crew member 1 has a personal activity "VA1" at station "OSL" that starts at 12oct2018 22:00 and ends at 19oct2018 22:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 19oct2018 22:00 and ends at 21oct2018 22:00

    When I show "crew" in window 1

    Then rave "crew.%has_agmt_group_snk_cc_at_date%(20Oct2018)" shall be "False" on leg 1 on trip 2 on roster 1
    and rave "crew.%has_agmt_group_nkf_cc_at_date%(20Oct2018)" shall be "False" on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 2 on roster 1

##########################################################################################

    @scenario6 @SNK @V00210
    Scenario: 6. FS is placed on weekend one day after VA longer than 6 days. Crew shall be in SNK.

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | AH     |
    | region     | SKN    |
    Given crew member 1 has contract "V00210"
    and crew member 1 has a personal activity "VA1" at station "OSL" that starts at 12oct2018 22:00 and ends at 19oct2018 22:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 20oct2018 22:00 and ends at 22oct2018 22:00

    When I show "crew" in window 1

    Then rave "crew.%has_agmt_group_snk_cc_at_date%(20Oct2018)" shall be "True" on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 2 on roster 1

##########################################################################################

    @scenario7 @SNK @V00210
    Scenario: 7. FS is placed on full weekend directly after VA = 6 days. Crew shall be in agreement SNK
    Covers edge-case VA = 6 days

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | AH     |
    | region     | SKN    |
    Given crew member 1 has contract "V00210"
    and crew member 1 has a personal activity "VA1" at station "OSL" that starts at 13oct2018 22:00 and ends at 19oct2018 22:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 19oct2018 22:00 and ends at 21oct2018 22:00

    When I show "crew" in window 1

    Then rave "crew.%has_agmt_group_snk_cc_at_date%(20Oct2018)" shall be "True" on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 2 on roster 1

##########################################################################################

    @scenario8 @SNK @V00210
    Scenario: 8. FS is placed on weekend one day after LA longer than 6 days. Crew shall be in SNK.
    Rule shall not be valid for other activities than in activity set VAC

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | AH     |
    | region     | SKN    |
    Given crew member 1 has contract "V00210"
    and crew member 1 has a personal activity "LA" at station "OSL" that starts at 12oct2018 22:00 and ends at 19oct2018 22:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 19oct2018 22:00 and ends at 21oct2018 22:00

    When I show "crew" in window 1

    Then rave "crew.%has_agmt_group_snk_cc_at_date%(20Oct2018)" shall be "True" on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 2 on roster 1

##########################################################################################

    @scenario9 @SNK @V00210
    Scenario: 9. FS is placed partially on weekend or week day.

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | AH     |
    | region     | SKN    |
    Given crew member 1 has contract "V00210"
    and crew member 1 has a personal activity "VA1" at station "OSL" that starts at 12oct2018 22:00 and ends at 20oct2018 22:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 20oct2018 22:00 and ends at 22oct2018 22:00

    When I show "crew" in window 1

    Then rave "crew.%has_agmt_group_snk_cc_at_date%(20Oct2018)" shall be "True" on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_days_in_weekend_covers_both_saturday_and_sunday" shall fail on leg 1 on trip 2 on roster 1


##########################################################################################

    @scenario10 @SNK @V00210
    Scenario: 10. FS is placed partially on weekend or week day

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | AH     |
    | region     | SKN    |
    Given crew member 1 has contract "V00210"
    and crew member 1 has a personal activity "VA1" at station "OSL" that starts at 5oct2018 22:00 and ends at 12oct2018 22:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 19oct2018 22:00 and ends at 21oct2018 22:00

    When I show "crew" in window 1

    Then rave "crew.%has_agmt_group_snk_cc_at_date%(20Oct2018)" shall be "True" on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall fail on leg 1 on trip 2 on roster 1
