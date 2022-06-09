Feature: Test max duty per month for parttime crew


Background: setup planning period
     Given planning period from 1MAR2018 to 30SEP2018


###################################################################################
    @skcms-1882

    Scenario: Check the correct max duty time for 51 percent dutypercent contract

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AS        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "F00661" 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | LHR     | 03SEP2018 | 10:00 | 11:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AS

    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1SEP2018 00:00"
    When I set parameter "fundamental.%end_para%" to "30SEP2018 00:00"
    Then rave "duty_time.%max_duty_in_calendar_month_pt_cc%(leg.%start_hb%)" shall be "84:39" on leg 1 on trip 1 on roster 1 
    and rave "duty_time.%max_duty_in_3_months_pt_cc%(leg.%start_hb%)" shall be "253:58" on leg 1 on trip 1 on roster 1 

####################################################################################
    @skcms-1882

    Scenario: Check the correct max duty time
    
    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AS        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V363"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | LHR     | 10SEP2018 | 10:00 | 11:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1SEP2018 00:00"
    When I set parameter "fundamental.%end_para%" to "30SEP2018 00:00"
    Then rave "duty_time.%max_duty_in_calendar_month_pt_cc%(leg.%start_hb%)" shall be "149:24" on leg 1 on trip 1 on roster 1 
    and rave "duty_time.%max_duty_in_3_months_pt_cc%(leg.%start_hb%)" shall be "448:12" on leg 1 on trip 1 on roster 1 

####################################################################################
    @skcms-1882
  
    Scenario: Check the correct max duty time
    
    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AS        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V341"


    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | LHR     | 10SEP2018 | 10:00 | 11:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1SEP2018 00:00"
    When I set parameter "fundamental.%end_para%" to "30SEP2018 00:00"
    Then rave "duty_time.%max_duty_in_calendar_month_pt_cc%(leg.%start_hb%)" shall be "999:00" on leg 1 on trip 1 on roster 1 
    and rave "duty_time.%max_duty_in_3_months_pt_cc%(leg.%start_hb%)" shall be "999:00" on leg 1 on trip 1 on roster 1 

####################################################################################
