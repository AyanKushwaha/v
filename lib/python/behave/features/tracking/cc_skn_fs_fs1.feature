Feature: Test FS1 rules

  Background: Setup for tracking
    Given Tracking
    Given planning period from 1dec2018 to 31dec2018

  @tracking @FS
  Scenario: Test that two FS days can be placed together

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "V00204"

    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 2dec2018 23:00 and ends at 3dec2018 23:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 3dec2018 23:00 and ends at 4dec2018 23:00

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_min_days_between_fs" shall pass on leg 1 on trip 2 on roster 1


  @tracking @FS
  Scenario: Test that two FS days can't be placed with 1 - 2 days separation

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "V00204"

    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 2dec2018 23:00 and ends at 3dec2018 23:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 4dec2018 23:00 and ends at 5dec2018 23:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 7dec2018 23:00 and ends at 8dec2018 23:00

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_min_days_between_fs" shall fail on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_min_days_between_fs" shall fail on leg 1 on trip 3 on roster 1


  @tracking @FS
  Scenario: Test that two FS days can be placed with 3 days separation

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "V00204"

    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 2dec2018 23:00 and ends at 3dec2018 23:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 6dec2018 23:00 and ends at 7dec2018 23:00

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_min_days_between_fs" shall pass on leg 1 on trip 2 on roster 1


  @tracking @FS1
  Scenario: Test that two FS1 days can be placed together

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "V00204"

    and crew member 1 has a personal activity "FS1" at station "OSL" that starts at 7dec2018 23:00 and ends at 8dec2018 23:00
    and crew member 1 has a personal activity "FS1" at station "OSL" that starts at 8dec2018 23:00 and ends at 9dec2018 23:00

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_min_days_between_fs" shall pass on leg 1 on trip 2 on roster 1


  @tracking @FS @FS1
  Scenario: Test that FS-FS1 days can't be placed with 1 - 2 days separation

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "V00204"

    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 6dec2018 23:00 and ends at 7dec2018 23:00
    and crew member 1 has a personal activity "FS1" at station "OSL" that starts at 8dec2018 23:00 and ends at 9dec2018 23:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 10dec2018 23:00 and ends at 11dec2018 23:00

    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 19dec2018 23:00 and ends at 20dec2018 23:00
    and crew member 1 has a personal activity "FS1" at station "OSL" that starts at 22dec2018 23:00 and ends at 23dec2018 23:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 25dec2018 23:00 and ends at 26dec2018 23:00

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_min_days_between_fs" shall fail on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_min_days_between_fs" shall fail on leg 1 on trip 3 on roster 1
    and the rule "rules_indust_ccr.ind_min_days_between_fs" shall fail on leg 1 on trip 5 on roster 1
    and the rule "rules_indust_ccr.ind_min_days_between_fs" shall fail on leg 1 on trip 6 on roster 1


  @tracking @FS @FS1
  Scenario: Test that FS-FS1 days can be placed with 3 days separation

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "V00204"

    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 4dec2018 23:00 and ends at 5dec2018 23:00
    and crew member 1 has a personal activity "FS1" at station "OSL" that starts at 8dec2018 23:00 and ends at 9dec2018 23:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 12dec2018 23:00 and ends at 13dec2018 23:00

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_min_days_between_fs" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_min_days_between_fs" shall pass on leg 1 on trip 3 on roster 1


  @tracking @FS @FS1 @weekend @SKWD-612
  Scenario: Test that FS-FS1 days can be placed with 3 days separation

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "V00204"

    and crew member 1 has a personal activity "FS1" at station "OSL" that starts at 7dec2018 23:00 and ends at 8dec2018 23:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 12dec2018 23:00 and ends at 13dec2018 23:00
    and crew member 1 has a personal activity "FS1" at station "OSL" that starts at 14dec2018 23:00 and ends at 15dec2018 23:00

    Given table account_entry additionally contains the following
    | id | crew          | tim        | account | source          | amount | man  | published | rate | reasoncode     | entrytime | username |
    | 0  | crew member 1 | 8dec2018   | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    | 1  | crew member 1 | 13dec2018  | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    | 2  | crew member 1 | 15dec2018  | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_max_fs_days_month_nkf_snk_cc" shall fail on leg 1 on trip 2 on roster 1

  @tracking @FS @weekend
  Scenario: Test that one FS weekend + one FS day is allowed

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "V00204"

    Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 7dec2018 23:00 and ends at 9dec2018 23:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 16dec2018 23:00 and ends at 17dec2018 23:00

    Given table account_entry additionally contains the following
    | id | crew          | tim       | account | source          | amount | man  | published | rate | reasoncode     | entrytime | username |
    | 0  | crew member 1 | 8dec2018  | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    | 1  | crew member 1 | 9dec2018  | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    | 2  | crew member 1 | 17dec2018 | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_max_fs_days_month_nkf_snk_cc" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_fs_days_month_nkf_snk_cc" shall pass on leg 1 on trip 2 on roster 1


  @tracking @FS @weekend @test_2
  Scenario: Test that one FS weekend + one FS1 day on another weekend is allowed

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "V00204"

    Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 7dec2018 23:00 and ends at 9dec2018 23:00
    and crew member 1 has a personal activity "FS1" at station "OSL" that starts at 14dec2018 23:00 and ends at 15dec2018 23:00

    Given table account_entry additionally contains the following
    | id | crew          | tim       | account | source          | amount | man  | published | rate | reasoncode     | entrytime | username |
    | 0  | crew member 1 | 8dec2018  | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    | 1  | crew member 1 | 9dec2018  | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |

    # Places an entry that gives an FS weekend granted status
       Given table crew_roster_request additionally contains the following
       | crew          | id     | type | st        | et         |
       | crew member 1 | 0001   | FS   | 8Dec2018  | 10Dec2018  |
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall pass on leg 1 on trip 1 on roster 1


  @tracking @FS @weekend
  Scenario: Test that one FS weekend + two FS days is not allowed

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "V00204"

    Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 7dec2018 23:00 and ends at 9dec2018 23:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 16dec2018 23:00 and ends at 17dec2018 23:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 17dec2018 23:00 and ends at 18dec2018 23:00

    Given table account_entry additionally contains the following
    | id | crew          | tim       | account | source          | amount | man  | published | rate | reasoncode     | entrytime | username |
    | 0  | crew member 1 | 8dec2018  | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    | 1  | crew member 1 | 9dec2018  | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    | 2  | crew member 1 | 17dec2018 | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    | 3  | crew member 1 | 18dec2018 | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_max_fs_days_month_nkf_snk_cc" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_fs_days_month_nkf_snk_cc" shall fail on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_max_fs_days_month_nkf_snk_cc" shall fail on leg 1 on trip 3 on roster 1


  @tracking @FS
  Scenario: Test that two FS days are allowed

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "V00204"

    Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 16dec2018 23:00 and ends at 17dec2018 23:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 17dec2018 23:00 and ends at 18dec2018 23:00

    Given table account_entry additionally contains the following
    | id | crew          | tim       | account | source          | amount | man  | published | rate | reasoncode     | entrytime | username |
    | 2  | crew member 1 | 17dec2018 | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    | 3  | crew member 1 | 18dec2018 | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_max_fs_days_month_nkf_snk_cc" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_fs_days_month_nkf_snk_cc" shall pass on leg 1 on trip 2 on roster 1


  @tracking @FS
  Scenario: Test that three FS days are not allowed

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "V00204"

    Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 16dec2018 23:00 and ends at 17dec2018 23:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 17dec2018 23:00 and ends at 18dec2018 23:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 26dec2018 23:00 and ends at 27dec2018 23:00

    Given table account_entry additionally contains the following
    | id | crew          | tim       | account | source          | amount | man  | published | rate | reasoncode     | entrytime | username |
    | 1  | crew member 1 | 17dec2018 | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    | 2  | crew member 1 | 18dec2018 | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    | 3  | crew member 1 | 27dec2018 | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_max_fs_days_month_nkf_snk_cc" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_fs_days_month_nkf_snk_cc" shall fail on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_max_fs_days_month_nkf_snk_cc" shall fail on leg 1 on trip 3 on roster 1


  @tracking @FS1 @weekend
  Scenario: Test that two FS1 days covering a weekend is OK

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "V301"

    Given crew member 1 has a personal activity "FS1" at station "OSL" that starts at 7dec2018 23:00 and ends at 8dec2018 23:00
    and crew member 1 has a personal activity "FS1" at station "OSL" that starts at 8dec2018 23:00 and ends at 9dec2018 23:00

    Given table account_entry additionally contains the following
    | id | crew          | tim       | account | source          | amount | man  | published | rate | reasoncode     | entrytime | username |
    | 1  | crew member 1 | 8dec2018  | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    | 2  | crew member 1 | 9dec2018  | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_max_fs_days_month_nkf_snk_cc" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_fs_days_month_nkf_snk_cc" shall pass on leg 1 on trip 2 on roster 1


  #@tracking @FS @FS1 @test_3

  # TO BE ACTIVATED ONCE CHRISTIFFER ROODRO has created a bug JIRA 
  #Scenario: Test that and additional FS day is not allowed when crew has two FS1 days covering a weekend

    #Given a crew member with
    #| attribute  | value   | valid from  | valid to  |
    #| base       | OSL     |             |           |
    #| title rank | AH      |             |           |
    #| region     | SKN     |             |           |
    #and crew member 1 has contract "V00204"

    #Given crew member 1 has a personal activity "FS1" at station "OSL" that starts at 7dec2018 23:00 and ends at 8dec2018 23:00
    #and crew member 1 has a personal activity "FS1" at station "OSL" that starts at 8dec2018 23:00 and ends at 9dec2018 23:00
    #and crew member 1 has a personal activity "FS" at station "OSL" that starts at 26dec2018 23:00 and ends at 27dec2018 23:00

    #Given table account_entry additionally contains the following
    #| id | crew          | tim       | account | source          | amount | man  | published | rate | reasoncode     | entrytime | username |
    #| 1  | crew member 1 | 8dec2018  | FS1     | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    #| 2  | crew member 1 | 9dec2018  | FS1     | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    #| 3  | crew member 1 | 27dec2018 | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    
    #When I show "crew" in window 1

    #Then the rule "rules_indust_ccr.ind_max_fs_days_month_nkf_snk_cc" shall fail on leg 1 on trip 1 on roster 1
    #and the rule "rules_indust_ccr.ind_max_fs_days_month_nkf_snk_cc" shall fail on leg 1 on trip 2 on roster 1
    #and the rule "rules_indust_ccr.ind_max_fs_days_month_nkf_snk_cc" shall fail on leg 1 on trip 3 on roster 1


  @tracking @FS @weekend @checkin @checkout
  Scenario: Test that late checkout or early checkin is not allowed around FS weekend

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "V301"

    Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 7dec2018 23:00 and ends at 9dec2018 23:00

    Given table account_entry additionally contains the following
    | id | crew          | tim       | account | source          | amount | man  | published | rate | reasoncode     | entrytime | username |
    | 0  | crew member 1 | 8dec2018  | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    | 1  | crew member 1 | 9dec2018  | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 7dec2018 | 14:00 | 14:45 |
    | leg | 002 | GOT     | OSL     | 7dec2018 | 16:00 | 16:46 |
    Given trip 1 is assigned to crew member 1
    
    Given a trip with the following activities
    | act | num | dep stn | arr stn | date      | dep  | arr  |
    | leg | 001 | OSL     | GOT     | 10dec2018 | 5:49 | 6:35 |
    | leg | 002 | GOT     | OSL     | 10dec2018 | 8:00 | 8:45 |
    Given trip 2 is assigned to crew member 1
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_check_out_time_limit_for_wop_all" shall fail on leg 2 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_check_in_time_limit_for_wop_all" shall fail on leg 1 on trip 3 on roster 1
    and rave "trip.%end_od%" shall be "18:01" on leg 2 on trip 1 on roster 1
    and rave "trip.%start_od%" shall be "5:59" on leg 1 on trip 3 on roster 1
    
  @tracking @FS @weekend @checkin @checkout @K20_SKN_CC @To_Be_Checked
  Scenario: Test that late checkout or early checkin is allowed around FS weekend after K20_SKN_CC
    Given planning period from 1may2021 to 31may2021

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "V301"
    # NKF VG

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 2 has contract "SNK_V1002"
    # SNK VG

    Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 7may2021 22:00 and ends at 9may2021 22:00
    Given crew member 2 has a personal activity "FS" at station "OSL" that starts at 7may2021 22:00 and ends at 9may2021 22:00


    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 7may2021 | 16:00 | 18:00 |
    | leg | 002 | GOT     | OSL     | 7may2021 | 20:00 | 21:44 |
    Given trip 1 is assigned to crew member 1
    Given trip 1 is assigned to crew member 2


    Given a trip with the following activities
    | act | num | dep stn | arr stn | date      | dep   | arr  |
    | leg | 001 | OSL     | GOT     | 10may2021 | 00:00 | 1:00 |
    | leg | 002 | GOT     | OSL     | 10may2021 | 7:00  | 7:45 |
    Given trip 2 is assigned to crew member 1
    Given trip 2 is assigned to crew member 2

    When I show "crew" in window 1

    Then rave "trip.%end_od%" shall be "23:59" on leg 2 on trip 1 on roster 1
    and rave "trip.%start_od%" shall be "1:10" on leg 1 on trip 3 on roster 1

    # The rules shall not be valid for the scenario, thus "passing" the rule
    and rave "rules_indust_ccr.%ind_check_out_time_limit_for_wop_ALL_valid%" shall be "True" on leg 2 on trip 1 on roster 1
    and rave "rules_indust_ccr.%ind_check_out_time_limit_for_wop_ALL_valid%" shall be "False" on leg 2 on trip 1 on roster 2
    and the rule "rules_indust_ccr.ind_check_out_time_limit_for_wop_ALL" shall fail on leg 2 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_check_out_time_limit_for_wop_ALL" shall pass on leg 2 on trip 1 on roster 2

    and rave "rules_indust_ccr.%ind_check_in_time_limit_for_wop_ALL_valid%" shall be "True" on leg 1 on trip 3 on roster 1
    and rave "rules_indust_ccr.%ind_check_in_time_limit_for_wop_ALL_valid%" shall be "True" on leg 1 on trip 3 on roster 2
    and the rule "rules_indust_ccr.ind_check_in_time_limit_for_wop_ALL" shall fail on leg 1 on trip 3 on roster 1
    and the rule "rules_indust_ccr.ind_check_in_time_limit_for_wop_ALL" shall fail on leg 1 on trip 3 on roster 2


  @tracking @FS1 @weekend @checkin @checkout @K20_SKN_CC
  Scenario: Test that late checkout or early checkin is allowed around FS1 weekend after K20_SKN_CC
    Given planning period from 30apr2021 to 31may2021

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "V301"
    # NKF VG

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 2 has contract "SNK_V1002"
    # SNK VG

    Given crew member 1 has a personal activity "FS1" at station "OSL" that starts at 7may2021 22:00 and ends at 9may2021 22:00
    Given crew member 2 has a personal activity "FS1" at station "OSL" that starts at 7may2021 22:00 and ends at 9may2021 22:00

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 7may2021 | 16:00 | 18:00 |
    | leg | 002 | GOT     | OSL     | 7may2021 | 20:00 | 21:44 |
    Given trip 1 is assigned to crew member 1
    Given trip 1 is assigned to crew member 2


    Given a trip with the following activities
    | act | num | dep stn | arr stn | date      | dep   | arr  |
    | leg | 001 | OSL     | GOT     | 10may2021 | 00:00 | 1:00 |
    | leg | 002 | GOT     | OSL     | 10may2021 | 7:00  | 7:45 |
    Given trip 2 is assigned to crew member 1
    Given trip 2 is assigned to crew member 2

    When I show "crew" in window 1

    Then rave "trip.%end_od%" shall be "23:59" on leg 2 on trip 1 on roster 1
    and rave "trip.%start_od%" shall be "1:10" on leg 1 on trip 3 on roster 1

    # The rules shall not be valid for the scenario, thus "passing" the rule
    and rave "rules_indust_ccr.%ind_check_out_time_limit_for_wop_ALL_valid%" shall be "False" on leg 2 on trip 1 on roster 1
    and rave "rules_indust_ccr.%ind_check_out_time_limit_for_wop_ALL_valid%" shall be "False" on leg 2 on trip 1 on roster 2
    and the rule "rules_indust_ccr.ind_check_out_time_limit_for_wop_ALL" shall pass on leg 2 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_check_out_time_limit_for_wop_ALL" shall pass on leg 2 on trip 1 on roster 2

    and rave "rules_indust_ccr.%ind_check_in_time_limit_for_wop_ALL_valid%" shall be "False" on leg 1 on trip 3 on roster 1
    and rave "rules_indust_ccr.%ind_check_in_time_limit_for_wop_ALL_valid%" shall be "False" on leg 1 on trip 3 on roster 2
    and the rule "rules_indust_ccr.ind_check_in_time_limit_for_wop_ALL" shall pass on leg 1 on trip 3 on roster 1
    and the rule "rules_indust_ccr.ind_check_in_time_limit_for_wop_ALL" shall pass on leg 1 on trip 3 on roster 2

  @tracking @FS1 @weekend @checkin @checkout
  Scenario: Test that late checkout or early checkin is not allowed around FS1 weekend

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "V301"

    Given crew member 1 has a personal activity "FS1" at station "OSL" that starts at 7dec2018 23:00 and ends at 8dec2018 23:00
    and crew member 1 has a personal activity "FS1" at station "OSL" that starts at 8dec2018 23:00 and ends at 9dec2018 23:00

    Given table account_entry additionally contains the following
    | id | crew          | tim       | account | source          | amount | man  | published | rate | reasoncode     | entrytime | username |
    | 0  | crew member 1 | 8dec2018  | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    | 1  | crew member 1 | 9dec2018  | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 7dec2018 | 14:00 | 14:45 |
    | leg | 002 | GOT     | OSL     | 7dec2018 | 16:00 | 16:46 |
    Given trip 1 is assigned to crew member 1
    
    Given a trip with the following activities
    | act | num | dep stn | arr stn | date      | dep  | arr  |
    | leg | 001 | OSL     | GOT     | 10dec2018 | 5:49 | 6:35 |
    | leg | 002 | GOT     | OSL     | 10dec2018 | 8:00 | 8:45 |
    Given trip 2 is assigned to crew member 1
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_check_out_time_limit_for_wop_all" shall fail on leg 2 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_check_in_time_limit_for_wop_all" shall fail on leg 1 on trip 4 on roster 1
    and rave "trip.%end_od%" shall be "18:01" on leg 2 on trip 1 on roster 1
    and rave "trip.%start_od%" shall be "5:59" on leg 1 on trip 4 on roster 1
    

  @tracking @FS @weekend @checkin @checkout
  Scenario: Test that early checkout or late checkin is allowed around FS weekend

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "V301"

    Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 7dec2018 23:00 and ends at 9dec2018 23:00

    Given table account_entry additionally contains the following
    | id | crew          | tim       | account | source          | amount | man  | published | rate | reasoncode     | entrytime | username |
    | 0  | crew member 1 | 8dec2018  | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    | 1  | crew member 1 | 9dec2018  | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 7dec2018 | 14:00 | 14:45 |
    | leg | 002 | GOT     | OSL     | 7dec2018 | 16:00 | 16:45 |
    Given trip 1 is assigned to crew member 1
    
    Given a trip with the following activities
    | act | num | dep stn | arr stn | date      | dep  | arr  |
    | leg | 001 | OSL     | GOT     | 10dec2018 | 5:50 | 6:35 |
    | leg | 002 | GOT     | OSL     | 10dec2018 | 8:00 | 8:45 |
    Given trip 2 is assigned to crew member 1
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_check_out_time_limit_for_wop_all" shall pass on leg 2 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_check_in_time_limit_for_wop_all" shall pass on leg 1 on trip 3 on roster 1
    and rave "trip.%end_od%" shall be "18:00" on leg 2 on trip 1 on roster 1
    and rave "trip.%start_od%" shall be "6:00" on leg 1 on trip 3 on roster 1
    

  @tracking @FS1 @weekend @checkin @checkout
  Scenario: Test that early checkout or late checkin is allowed around FS1 weekend

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "V301"

    Given crew member 1 has a personal activity "FS1" at station "OSL" that starts at 7dec2018 23:00 and ends at 8dec2018 23:00
    and crew member 1 has a personal activity "FS1" at station "OSL" that starts at 8dec2018 23:00 and ends at 9dec2018 23:00

    Given table account_entry additionally contains the following
    | id | crew          | tim       | account | source          | amount | man  | published | rate | reasoncode     | entrytime | username |
    | 0  | crew member 1 | 8dec2018  | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    | 1  | crew member 1 | 9dec2018  | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 7dec2018 | 14:00 | 14:45 |
    | leg | 002 | GOT     | OSL     | 7dec2018 | 16:00 | 16:45 |
    Given trip 1 is assigned to crew member 1
    
    Given a trip with the following activities
    | act | num | dep stn | arr stn | date      | dep  | arr  |
    | leg | 001 | OSL     | GOT     | 10dec2018 | 5:50 | 6:35 |
    | leg | 002 | GOT     | OSL     | 10dec2018 | 8:00 | 8:45 |
    Given trip 2 is assigned to crew member 1
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_check_out_time_limit_for_wop_all" shall pass on leg 2 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_check_in_time_limit_for_wop_all" shall pass on leg 1 on trip 4 on roster 1
    and rave "trip.%end_od%" shall be "18:00" on leg 2 on trip 1 on roster 1
    and rave "trip.%start_od%" shall be "6:00" on leg 1 on trip 4 on roster 1


  @tracking @FS1 @single_freeday_unbid
  Scenario: Test SingleFUnbid

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "V301"

    Given crew member 1 has a personal activity "FS1" at station "OSL" that starts at 8dec2018 23:00 and ends at 9dec2018 23:00
    and crew member 1 has a personal activity "FS1" at station "OSL" that starts at 15dec2018 23:00 and ends at 16dec2018 23:00

    Given table special_schedules additionally contains the following
    | crewid        | typ          | validfrom | str_val | validto   |
    | crew member 1 | SingleFUnbid | 12dec2018 | *       | 31dec2035 |
    

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_no_fs1_with_single_f_unbid" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_no_fs1_with_single_f_unbid" shall fail on leg 1 on trip 2 on roster 1


  @tracking @single_freeday @SKCMS-1999 @scenario_single_freeday_1
  Scenario: Test that single freeday with less than 38h off is not allowed for SNK_CC_AG

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "SNK_V301"

    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 8dec2018 23:00 and ends at 9dec2018 23:00

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 7dec2018 | 19:00 | 19:45 |
    | leg | 002 | GOT     | OSL     | 7dec2018 | 21:00 | 21:45 |
    Given trip 1 is assigned to crew member 1

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 8dec2018 | 19:00 | 19:45 |
    | leg | 002 | GOT     | OSL     | 8dec2018 | 21:00 | 21:45 |
    Given trip 2 is assigned to crew member 1
    
    Given a trip with the following activities
    | act | num | dep stn | arr stn | date      | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 10dec2018 | 12:49 | 13:35 |
    | leg | 002 | GOT     | OSL     | 10dec2018 | 15:00 | 15:45 |
    Given trip 3 is assigned to crew member 1
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_min_freedays_after_duty_all" shall fail on leg 1 on trip 2 on roster 1


  @tracking @single_freeday @SKCMS-1999 @scenario_single_freeday_2
  Scenario: Test that single freeday with 38h off is allowed for SNK_CC_AG

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "SNK_V301"

    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 8dec2018 23:00 and ends at 9dec2018 23:00

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 7dec2018 | 19:00 | 19:45 |
    | leg | 002 | GOT     | OSL     | 7dec2018 | 21:00 | 21:45 |
    Given trip 1 is assigned to crew member 1

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 8dec2018 | 19:00 | 19:45 |
    | leg | 002 | GOT     | OSL     | 8dec2018 | 21:00 | 21:45 |
    Given trip 2 is assigned to crew member 1
    
    Given a trip with the following activities
    | act | num | dep stn | arr stn | date      | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 10dec2018 | 12:50 | 13:35 |
    | leg | 002 | GOT     | OSL     | 10dec2018 | 15:00 | 15:45 |
    Given trip 3 is assigned to crew member 1
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_min_freedays_after_duty_all" shall pass on leg 1 on trip 2 on roster 1


  @tracking @single_freeday @FS1 @SKCMS-1999 @scenario_single_freeday_3
  Scenario: Test that FS1 with less than 38h off is allowed for SNK_CC_AG

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "SNK_V301"

    Given crew member 1 has a personal activity "FS1" at station "OSL" that starts at 8dec2018 23:00 and ends at 9dec2018 23:00

    Given table account_entry additionally contains the following
    | id | crew          | tim       | account | source          | amount | man  | published | rate | reasoncode     | entrytime | username |
    | 0  | crew member 1 | 9dec2018  | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 7dec2018 | 19:00 | 19:45 |
    | leg | 002 | GOT     | OSL     | 7dec2018 | 21:00 | 21:45 |
    Given trip 1 is assigned to crew member 1

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 8dec2018 | 19:00 | 19:45 |
    | leg | 002 | GOT     | OSL     | 8dec2018 | 21:00 | 21:45 |
    Given trip 2 is assigned to crew member 1
    
    Given a trip with the following activities
    | act | num | dep stn | arr stn | date      | dep  | arr  |
    | leg | 001 | OSL     | GOT     | 10dec2018 | 5:50 | 6:35 |
    | leg | 002 | GOT     | OSL     | 10dec2018 | 8:00 | 8:45 |
    Given trip 3 is assigned to crew member 1
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_min_freedays_after_duty_all" shall pass on leg 1 on trip 2 on roster 1


  @tracking @single_freeday @SKCMS-1999 @scenario_single_freeday_4
  Scenario: Test that single freeday with less than 38h off is not allowed for NKF_CC_AG

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "V301"

    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 8dec2018 23:00 and ends at 9dec2018 23:00

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 7dec2018 | 19:00 | 19:45 |
    | leg | 002 | GOT     | OSL     | 7dec2018 | 21:00 | 21:45 |
    Given trip 1 is assigned to crew member 1

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 8dec2018 | 19:00 | 19:45 |
    | leg | 002 | GOT     | OSL     | 8dec2018 | 21:00 | 21:45 |
    Given trip 2 is assigned to crew member 1
    
    Given a trip with the following activities
    | act | num | dep stn | arr stn | date      | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 10dec2018 | 12:49 | 13:35 |
    | leg | 002 | GOT     | OSL     | 10dec2018 | 15:00 | 15:45 |
    Given trip 3 is assigned to crew member 1
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_min_freedays_after_duty_all" shall fail on leg 1 on trip 2 on roster 1


  @tracking @single_freeday @SKCMS-1999 @scenario_single_freeday_5
  Scenario: Test that single freeday with 38h off is allowed for NKF_CC_AG

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "V301"

    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 8dec2018 23:00 and ends at 9dec2018 23:00

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 7dec2018 | 19:00 | 19:45 |
    | leg | 002 | GOT     | OSL     | 7dec2018 | 21:00 | 21:45 |
    Given trip 1 is assigned to crew member 1

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 8dec2018 | 19:00 | 19:45 |
    | leg | 002 | GOT     | OSL     | 8dec2018 | 21:00 | 21:45 |
    Given trip 2 is assigned to crew member 1
    
    Given a trip with the following activities
    | act | num | dep stn | arr stn | date      | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 10dec2018 | 12:50 | 13:35 |
    | leg | 002 | GOT     | OSL     | 10dec2018 | 15:00 | 15:45 |
    Given trip 3 is assigned to crew member 1
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_min_freedays_after_duty_all" shall pass on leg 1 on trip 2 on roster 1


  @tracking @single_freeday @FS1 @SKCMS-1999 @scenario_single_freeday_6
  Scenario: Test that FS1 with less than 38h off is allowed for NKF_CC_AG

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "V301"

    Given crew member 1 has a personal activity "FS1" at station "OSL" that starts at 8dec2018 23:00 and ends at 9dec2018 23:00

    Given table account_entry additionally contains the following
    | id | crew          | tim       | account | source          | amount | man  | published | rate | reasoncode     | entrytime | username |
    | 0  | crew member 1 | 9dec2018  | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 7dec2018 | 19:00 | 19:45 |
    | leg | 002 | GOT     | OSL     | 7dec2018 | 21:00 | 21:45 |
    Given trip 1 is assigned to crew member 1

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 8dec2018 | 19:00 | 19:45 |
    | leg | 002 | GOT     | OSL     | 8dec2018 | 21:00 | 21:45 |
    Given trip 2 is assigned to crew member 1
    
    Given a trip with the following activities
    | act | num | dep stn | arr stn | date      | dep  | arr  |
    | leg | 001 | OSL     | GOT     | 10dec2018 | 5:50 | 6:35 |
    | leg | 002 | GOT     | OSL     | 10dec2018 | 8:00 | 8:45 |
    Given trip 3 is assigned to crew member 1
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_min_freedays_after_duty_all" shall pass on leg 1 on trip 2 on roster 1


  @tracking @single_freeday @SKCMS-1999 @scenario_single_freeday_7
  Scenario: Test that single freeday is not allowed for SKS_CC_AG

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | STO     |             |           |
    | title rank | AH      |             |           |
    | region     | SKS     |             |           |
    and crew member 1 has contract "V340"

    Given crew member 1 has a personal activity "F" at station "ARN" that starts at 8dec2018 23:00 and ends at 9dec2018 23:00

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | ARN     | GOT     | 7dec2018 | 19:00 | 19:45 |
    | leg | 002 | GOT     | ARN     | 7dec2018 | 21:00 | 21:45 |
    Given trip 1 is assigned to crew member 1

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | ARN     | GOT     | 8dec2018 | 19:00 | 19:45 |
    | leg | 002 | GOT     | ARN     | 8dec2018 | 21:00 | 21:45 |
    Given trip 2 is assigned to crew member 1
    
    Given a trip with the following activities
    | act | num | dep stn | arr stn | date      | dep   | arr   |
    | leg | 001 | ARN     | GOT     | 10dec2018 | 00:00 | 00:45 |
    | leg | 002 | GOT     | ARN     | 10dec2018 | 02:00 | 02:45 |
    Given trip 3 is assigned to crew member 1
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_min_freedays_after_duty_all" shall fail on leg 1 on trip 2 on roster 1


  @tracking @single_freeday @SKCMS-1999 @scenario_single_freeday_8
  Scenario: Test that double freeday is allowed for SKS_CC_AG

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | STO     |             |           |
    | title rank | AH      |             |           |
    | region     | SKS     |             |           |
    and crew member 1 has contract "V340"

    Given crew member 1 has a personal activity "F" at station "ARN" that starts at 8dec2018 23:00 and ends at 10dec2018 23:00

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | ARN     | GOT     | 7dec2018 | 19:00 | 19:45 |
    | leg | 002 | GOT     | ARN     | 7dec2018 | 21:00 | 21:45 |
    Given trip 1 is assigned to crew member 1

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | ARN     | GOT     | 8dec2018 | 19:00 | 19:45 |
    | leg | 002 | GOT     | ARN     | 8dec2018 | 21:00 | 21:45 |
    Given trip 2 is assigned to crew member 1
    
    Given a trip with the following activities
    | act | num | dep stn | arr stn | date      | dep   | arr   |
    | leg | 001 | ARN     | GOT     | 11dec2018 | 00:00 | 00:45 |
    | leg | 002 | GOT     | ARN     | 11dec2018 | 02:00 | 02:45 |
    Given trip 3 is assigned to crew member 1
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_min_freedays_after_duty_all" shall pass on leg 1 on trip 2 on roster 1


  @tracking @single_freeday @SKCMS-1999 @scenario_single_freeday_9
  Scenario: Test that single freeday with less than 40h off is not allowed for SKS_FD_AG V133 (SH)

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | STO     |             |           |
    | title rank | FC      |             |           |
    | region     | SKS     |             |           |
    and crew member 1 has contract "V133"

    Given crew member 1 has a personal activity "F" at station "ARN" that starts at 7dec2018 23:00 and ends at 8dec2018 23:00

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | ARN     | GOT     | 6dec2018 | 19:00 | 19:45 |
    | leg | 002 | GOT     | ARN     | 6dec2018 | 21:00 | 21:45 |
    Given trip 1 is assigned to crew member 1

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | ARN     | GOT     | 7dec2018 | 19:00 | 19:45 |
    | leg | 002 | GOT     | ARN     | 7dec2018 | 21:00 | 21:45 |
    Given trip 2 is assigned to crew member 1
    
    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | ARN     | GOT     | 9dec2018 | 15:04 | 15:50 |
    | leg | 002 | GOT     | ARN     | 9dec2018 | 17:00 | 17:45 |
    Given trip 3 is assigned to crew member 1
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_min_freedays_after_duty_all" shall fail on leg 1 on trip 2 on roster 1


  @tracking @single_freeday @SKCMS-1999 @scenario_single_freeday_10
  Scenario: Test that single freeday with 40h off is allowed for SKS_FD_AG V133 (SH)

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | STO     |             |           |
    | title rank | FC      |             |           |
    | region     | SKS     |             |           |
    and crew member 1 has contract "V133"

    Given crew member 1 has a personal activity "F" at station "ARN" that starts at 7dec2018 23:00 and ends at 8dec2018 23:00

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | ARN     | GOT     | 6dec2018 | 19:00 | 19:45 |
    | leg | 002 | GOT     | ARN     | 6dec2018 | 21:00 | 21:45 |
    Given trip 1 is assigned to crew member 1

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | ARN     | GOT     | 7dec2018 | 19:00 | 19:45 |
    | leg | 002 | GOT     | ARN     | 7dec2018 | 21:00 | 21:45 |
    Given trip 2 is assigned to crew member 1
    
    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | ARN     | GOT     | 9dec2018 | 15:05 | 15:50 |
    | leg | 002 | GOT     | ARN     | 9dec2018 | 17:00 | 17:45 |
    Given trip 3 is assigned to crew member 1
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_min_freedays_after_duty_all" shall pass on leg 1 on trip 2 on roster 1
