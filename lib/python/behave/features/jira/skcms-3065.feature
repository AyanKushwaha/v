Feature: Max duty hrs in 7 days 

@SCENARIO1
@tracking
Scenario: Max_duty_7_days rules should pass when duty hours is less than 60:00 for FD
        Given Tracking
        Given planning period from 1Oct2018 to 30Oct2018
        Given a crew member with
          | attribute  | value     |
          | crew rank  | FC        | 
          | region     | SKI       | 
          | base       | STO       |
          | title rank | FC        | 
          | contract   | V00004    | 
          
        Given a trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ  |
         | leg | 0001 | CPH     | LAX     | 01Oct2018 | 12:00 | 14:30 | SK  | 320     |
         | leg | 0002 | LAX     | OSL     | 02Oct2018 | 10:00 | 15:45 | SK  | 320     |
         
        Given another trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ  |
         | leg | 0001 | CPH     | LAX     | 07Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0002 | LAX     | OSL     | 08Oct2018 | 10:00 | 21:45 | SK  | 320     |
         

        Given trip 1 is assigned to crew member 1
        Given trip 2 is assigned to crew member 1
      
        When I show "crew" in window 1
 
        Then the rule "rules_indust_ccp.ind_max_duty_time_in_7_days_start_day_ALL" shall pass on leg 3 on trip 1 on roster 1
        and the rule "rules_indust_ccp.ind_max_duty_time_in_7_days_end_day_ALL" shall pass on leg 4 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_max_duty_time_in_7_days_start_day_ALL" shall pass on leg 3 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_max_duty_time_in_7_days_end_day_ALL" shall pass on leg 4 on trip 1 on roster 1
        

@SCENARIO2
Scenario: Max_duty_7_days rules should give warning when duty hrs exceeds 60 for FD
        Given Tracking
        Given planning period from 1Oct2018 to 30Oct2018
        Given a crew member with
          | attribute  | value     |
          | crew rank  | FC        | 
          | region     | SKI       | 
          | base       | STO       |
          | title rank | FC        | 
          | contract   | V00004    | 
          
        Given a trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ  |
         | leg | 0001 | CPH     | LAX     | 01Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0002 | LAX     | OSL     | 02Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0002 | OSL     | CPH     | 03Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0003 | CPH     | LAX     | 04Oct2018 | 10:00 | 23:30 | SK  | 320     |
         | leg | 0004 | LAX     | OSL     | 05Oct2018 | 10:00 | 23:45 | SK  | 320     | 
         
        Given another trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ  |
         | leg | 0001 | CPH     | LAX     | 07Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0002 | LAX     | OSL     | 08Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0003 | OSL     | LAX     | 09Oct2018 | 10:00 | 23:30 | SK  | 320     |
         | leg | 0004 | LAX     | CPH     | 10Oct2018 | 10:00 | 21:45 | SK  | 320     | 
         | leg | 0005 | CPH     | LAX     | 11Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0006 | LAX     | OSL     | 12Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0007 | OSL     | LAX     | 13Oct2018 | 10:00 | 23:30 | SK  | 320     |
         | leg | 0008 | LAX     | CPH     | 14Oct2018 | 10:00 | 21:45 | SK  | 320     | 

        Given trip 1 is assigned to crew member 1
        Given trip 2 is assigned to crew member 1
      
        When I show "crew" in window 1
 
        Then the rule "rules_indust_ccp.ind_max_duty_time_in_7_days_start_day_ALL" shall fail on leg 6 on trip 1 on roster 1
        and the rule "rules_indust_ccp.ind_max_duty_time_in_7_days_end_day_ALL" shall fail on leg 13 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_max_duty_time_in_7_days_start_day_ALL" shall fail on leg 6 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_max_duty_time_in_7_days_end_day_ALL" shall fail on leg 13 on trip 1 on roster 1
       
@SCENARIO3
@tracking
        Scenario: Max_duty_7_days rules should fail when duty hours exceeds 47:30 for CC
        Given Tracking
        Given planning period from 1Oct2018 to 31Oct2018
   
        Given a crew member with
          | attribute  | value     |
          | crew rank  | FC        | 
          | region     | SKI       | 
          | base       | STO       |
          | title rank | AH        | 
          | contract   | V300      | 
            
        Given a trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ  |
         | leg | 0001 | CPH     | LAX     | 01Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0002 | LAX     | OSL     | 02Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0002 | OSL     | CPH     | 03Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0003 | CPH     | LAX     | 04Oct2018 | 10:00 | 23:30 | SK  | 320     |
         | leg | 0004 | LAX     | OSL     | 05Oct2018 | 10:00 | 23:45 | SK  | 320     | 
         
        Given another trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ  |
         | leg | 0001 | CPH     | LAX     | 07Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0002 | LAX     | OSL     | 08Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0003 | OSL     | LAX     | 09Oct2018 | 10:00 | 23:30 | SK  | 320     |
         | leg | 0004 | LAX     | CPH     | 10Oct2018 | 10:00 | 21:45 | SK  | 320     | 
         | leg | 0005 | CPH     | LAX     | 11Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0006 | LAX     | OSL     | 12Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0007 | OSL     | LAX     | 13Oct2018 | 10:00 | 23:30 | SK  | 320     |
         | leg | 0008 | LAX     | CPH     | 14Oct2018 | 10:00 | 21:45 | SK  | 320     | 

        Given trip 1 is assigned to crew member 1
        Given trip 2 is assigned to crew member 1
      
        When I show "crew" in window 1
 
        Then the rule "rules_indust_ccp.ind_max_duty_time_in_7_days_start_day_ALL" shall fail on leg 6 on trip 1 on roster 1
        and the rule "rules_indust_ccp.ind_max_duty_time_in_7_days_end_day_ALL" shall fail on leg 13 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_max_duty_time_in_7_days_start_day_ALL" shall fail on leg 6 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_max_duty_time_in_7_days_end_day_ALL" shall fail on leg 13 on trip 1 on roster 1
       
@SCENARIO4
@tracking
        Scenario: Max_duty_7_days rules should pass when duty hours is less than 47:30 for CC
        Given Tracking
        Given planning period from 1Oct2018 to 31Oct2018
   
        Given a crew member with
          | attribute  | value     |
          | crew rank  | FC        | 
          | region     | SKI       | 
          | base       | STO       |
          | title rank | AH        | 
          | contract   | V300      | 
            
        Given a trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ  |
         | leg | 0001 | CPH     | LAX     | 01Oct2018 | 12:00 | 14:30 | SK  | 320     |
         | leg | 0002 | LAX     | OSL     | 02Oct2018 | 10:00 | 14:45 | SK  | 320     |
         
        Given another trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ  |
         | leg | 0001 | CPH     | LAX     | 07Oct2018 | 12:00 | 16:30 | SK  | 320     |
         | leg | 0002 | LAX     | OSL     | 08Oct2018 | 10:00 | 21:45 | SK  | 320     |
         

        Given trip 1 is assigned to crew member 1
        Given trip 2 is assigned to crew member 1
      
        When I show "crew" in window 1
 
        Then the rule "rules_indust_ccp.ind_max_duty_time_in_7_days_start_day_ALL" shall pass on leg 3 on trip 1 on roster 1
        and the rule "rules_indust_ccp.ind_max_duty_time_in_7_days_end_day_ALL" shall pass on leg 4 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_max_duty_time_in_7_days_start_day_ALL" shall pass on leg 3 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_max_duty_time_in_7_days_end_day_ALL" shall pass on leg 4 on trip 1 on roster 1
       