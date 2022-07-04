Feature: Max duty 7 days

@SCENARIO1
@tracking
        Scenario: Max_duty_7_days rules should pass when duty hours is less than 45:00
        
        Given TRACKING

        Given planning period from 1Oct2018 to 31Oct2018
   
       Given a crew member with
           | attribute       | value     | valid from | valid to |
           | base            | CPH       | 01OCT2018  | 01JAN2036 |
           | title rank      | AH        | 28OCT2018  | 01JAN2036 |
           | contract        | VSVS-001  | 01OCT2018  | 01JAN2036 |
         
        Given a trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ  |
         | leg | 0001 | CPH     | LAX     | 01Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0002 | LAX     | CPH     | 02Oct2018 | 10:00 | 21:45 | SK  | 320     |

        Given trip 1 is assigned to crew member 1
      
        When I show "crew" in window 1
 
        Then the rule "rules_svs_indust_cct.ind_max_duty_time_in_7_days_start_day_ALL" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_svs_indust_cct.ind_max_duty_time_in_7_days_end_day_ALL" shall pass on leg 2 on trip 1 on roster 1


@SCENARIO2
@tracking
        Scenario: Max_duty_7_days rules should give soft warning when duty hours are between 45:00 and 55:00
        
        Given TRACKING

        Given planning period from 1Oct2018 to 31Oct2018
   
       Given a crew member with
           | attribute       | value     | valid from | valid to |
           | base            | CPH       | 01OCT2018  | 01JAN2036 |
           | title rank      | AH        | 28OCT2018  | 01JAN2036 |
           | contract        | VSVS-001  | 01OCT2018  | 01JAN2036 |
         
        Given a trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ  |
         | leg | 0001 | CPH     | LAX     | 01Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0002 | LAX     | OSL     | 02Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0003 | OSL     | LAX     | 03Oct2018 | 10:00 | 23:30 | SK  | 320     |
         | leg | 0004 | LAX     | CPH     | 04Oct2018 | 10:00 | 21:45 | SK  | 320     | 

        Given trip 1 is assigned to crew member 1
      
        When I show "crew" in window 1
 
        Then the rule "rules_svs_indust_cct.ind_max_duty_time_in_7_days_start_day_ALL" shall fail on leg 1 on trip 1 on roster 1
        and the rule "rules_svs_indust_cct.ind_max_duty_time_in_7_days_end_day_ALL" shall fail on leg 4 on trip 1 on roster 1

           
        
@SCENARIO3
@tracking
        Scenario: Max_duty_7_days rules should fail when duty hours is more than 55:00
        
        Given TRACKING

        Given planning period from 1Oct2018 to 31Oct2018
   
        Given a crew member with
           | attribute       | value     | valid from | valid to |
           | base            | CPH       | 01OCT2018  | 01JAN2036 |
           | title rank      | AH        | 28OCT2018  | 01JAN2036 |
           | contract        | VSVS-001  | 01OCT2018  | 01JAN2036 |
         
        Given a trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ  |
         | leg | 0001 | CPH     | LAX     | 01Oct2018 | 10:00 | 23:30 | SK  | 320     |
         | leg | 0002 | LAX     | OSL     | 02Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0003 | OSL     | LAX     | 03Oct2018 | 10:00 | 23:30 | SK  | 320     |
         | leg | 0004 | LAX     | OSL     | 04Oct2018 | 10:00 | 21:45 | SK  | 320     | 
         | leg | 0005 | OSL     | LAX     | 05Oct2018 | 10:00 | 23:30 | SK  | 320     |
         | leg | 0006 | LAX     | CPH     | 06Oct2018 | 10:00 | 21:45 | SK  | 320     |
        
        Given trip 1 is assigned to crew member 1
      
        When I show "crew" in window 1
 
        Then the rule "rules_svs_indust_cct.ind_max_duty_time_in_7_days_start_day_ALL" shall fail on leg 1 on trip 1 on roster 1
        and the rule "rules_svs_indust_cct.ind_max_duty_time_in_7_days_end_day_ALL" shall fail on leg 6 on trip 1 on roster 1
