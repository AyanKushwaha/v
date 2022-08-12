@JCRT @ALL @FD @SKCMS-2177 @K19
Feature: Rule checks that max working days arent exceeded.

  ##############################################################################
  # Notes:
  # K19 - It is decided that variable group crew should all have a maximum of 19 production days per month.
  # Case 1-3 is SKN VG
  # Case 4-6 is SKS VG
  # Case 7-9 is SKD VG
  # Developer: Oscar Grandell <oscar.grandell@hiq.se>

  ##############################################################################
  Background:
    Given planning period from 1JAN2019 to 31JAN2019


  ##############################################################################
  @PASS_1
  Scenario: Rule passes for SKN less then 19 days

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | FD     |
    | region     | SKN    |
    Given crew member 1 has contract "V00210"

    # Each trip generated in behave avg 8 hrs 18 days 144 hrs
    Given crew member 1 with homebase "OSL" has duty time that exceeds 144 hours in month JAN in 2019
    
    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
    When I set parameter "fundamental.%end_para%" to "31JAN2019 00:00"

    Then rave "rules_indust_ccr.%_max_prod_days_in_calendar_month_vg_fc_valid%" shall be "True" on leg 1 on trip 18 on roster 1
    and the rule "rules_indust_ccr.ind_max_prod_days_in_calendar_month_vg_fc" shall pass on leg 1 on trip 18 on roster 1

  ##############################################################################
  @PASS_2
  Scenario: Rule passes for SKN equals 19 days

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | FD     |
    | region     | SKN    |
    Given crew member 1 has contract "V00210"

    # Each trip generated in behave avg 8 hrs 19 days 152 hrs
    Given crew member 1 with homebase "OSL" has duty time that exceeds 152 hours in month JAN in 2019

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
    When I set parameter "fundamental.%end_para%" to "31JAN2019 00:00"

    Then rave "rules_indust_ccr.%_max_prod_days_in_calendar_month_vg_fc_valid%" shall be "True" on leg 1 on trip 19 on roster 1
    and the rule "rules_indust_ccr.ind_max_prod_days_in_calendar_month_vg_fc" shall pass on leg 1 on trip 19 on roster 1

  ##############################################################################
  @PASS_3
  Scenario: Rule fails for SKN greater then 19 days

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | FD     |
    | region     | SKN    |
    Given crew member 1 has contract "V00210"

    # Each trip generated in behave avg 8 hrs 20 days 160 hrs
    Given crew member 1 with homebase "OSL" has duty time that exceeds 160 hours in month JAN in 2019
    
    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
    When I set parameter "fundamental.%end_para%" to "31JAN2019 00:00"

    Then rave "rules_indust_ccr.%_max_prod_days_in_calendar_month_vg_fc_valid%" shall be "True" on leg 1 on trip 20 on roster 1
    and the rule "rules_indust_ccr.ind_max_prod_days_in_calendar_month_vg_fc" shall fail on leg 1 on trip 20 on roster 1

  ##############################################################################
  @PASS_4
  Scenario: Rule passes for SKS less then 19 days

    Given a crew member with
    | attribute  | value  |
    | base       | STO    |
    | title rank | FD     |
    | region     | SKS    |
    Given crew member 1 has contract "V133"

    # Each trip generated in behave avg 8 hrs 18 days 144 hrs
    Given crew member 1 with homebase "ARN" has duty time that exceeds 144 hours in month JAN in 2019
    
    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
    When I set parameter "fundamental.%end_para%" to "31JAN2019 00:00"

    #Then rave "rules_indust_ccr.%_max_prod_days_in_calendar_month_vg_fc_valid%" shall be "True" on leg 1 on trip 18 on roster 1
    #and the rule "rules_indust_ccr.ind_max_prod_days_in_calendar_month_vg_fc" shall pass on leg 1 on trip 18 on roster 1

  ##############################################################################
  @PASS_5
  Scenario: Rule passes for SKS equals 19 days

    Given a crew member with
    | attribute  | value  |
    | base       | STO    |
    | title rank | FD     |
    | region     | SKS    |
    Given crew member 1 has contract "V133"

    # Each trip generated in behave avg 8 hrs 19 days 152 hrs
    Given crew member 1 with homebase "ARN" has duty time that exceeds 152 hours in month JAN in 2019
    
    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
    When I set parameter "fundamental.%end_para%" to "31JAN2019 00:00"

    Then rave "rules_indust_ccr.%_max_prod_days_in_calendar_month_vg_fc_valid%" shall be "True" on leg 1 on trip 19 on roster 1
    and the rule "rules_indust_ccr.ind_max_prod_days_in_calendar_month_vg_fc" shall pass on leg 1 on trip 19 on roster 1

  ##############################################################################
  @PASS_6
  Scenario: Rule fails for SKS greater than 19 days

    Given a crew member with
    | attribute  | value  |
    | base       | STO    |
    | title rank | FD     |
    | region     | SKS    |
    Given crew member 1 has contract "V133"

    # Each trip generated in behave avg 8 hrs 20 days 160 hrs
    Given crew member 1 with homebase "ARN" has duty time that exceeds 160 hours in month JAN in 2019
    
    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
    When I set parameter "fundamental.%end_para%" to "31JAN2019 00:00"

    Then rave "rules_indust_ccr.%_max_prod_days_in_calendar_month_vg_fc_valid%" shall be "True" on leg 1 on trip 20 on roster 1
    and the rule "rules_indust_ccr.ind_max_prod_days_in_calendar_month_vg_fc" shall fail on leg 1 on trip 20 on roster 1

  ##############################################################################
  @PASS_7
  Scenario: Rule passes for SKD less then 19 days

    Given a crew member with
    | attribute  | value  |
    | base       | CPH    |
    | title rank | FD     |
    | region     | SKD    |
    Given crew member 1 has contract "V131"

    # Each trip generated in behave avg 8 hrs 18 days 144 hrs
    Given crew member 1 with homebase "CPH" has duty time that exceeds 144 hours in month JAN in 2019
    
    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
    When I set parameter "fundamental.%end_para%" to "31JAN2019 00:00"

    #Then rave "rules_indust_ccr.%_max_prod_days_in_calendar_month_vg_fc_valid%" shall be "True" on leg 1 on trip 18 on roster 1
    #and the rule "rules_indust_ccr.ind_max_prod_days_in_calendar_month_vg_fc" shall pass on leg 1 on trip 18 on roster 1

    ##############################################################################
  @PASS_8
  Scenario: Rule passes for SKD equals 19 days

    Given a crew member with
    | attribute  | value  |
    | base       | CPH    |
    | title rank | FD     |
    | region     | SKD    |
    Given crew member 1 has contract "V131"

    # Each trip generated in behave avg 8 hrs 19 days 152 hrs
    Given crew member 1 with homebase "CPH" has duty time that exceeds 152 hours in month JAN in 2019

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
    When I set parameter "fundamental.%end_para%" to "31JAN2019 00:00"

    Then rave "rules_indust_ccr.%_max_prod_days_in_calendar_month_vg_fc_valid%" shall be "True" on leg 1 on trip 19 on roster 1
    and the rule "rules_indust_ccr.ind_max_prod_days_in_calendar_month_vg_fc" shall pass on leg 1 on trip 19 on roster 1

      ##############################################################################
  @PASS_9
  Scenario: Rule fails for SKD greater than 19 days

    Given a crew member with
    | attribute  | value  |
    | base       | CPH    |
    | title rank | FD     |
    | region     | SKD    |
    Given crew member 1 has contract "V131"

    # Each trip generated in behave avg 8 hrs 20 days 160 hrs
    Given crew member 1 with homebase "CPH" has duty time that exceeds 160 hours in month JAN in 2019
    
    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
    When I set parameter "fundamental.%end_para%" to "31JAN2019 00:00"

    Then rave "rules_indust_ccr.%_max_prod_days_in_calendar_month_vg_fc_valid%" shall be "True" on leg 1 on trip 20 on roster 1
    and the rule "rules_indust_ccr.ind_max_prod_days_in_calendar_month_vg_fc" shall fail on leg 1 on trip 20 on roster 1

