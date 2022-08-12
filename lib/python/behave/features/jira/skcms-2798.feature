Feature: Min 11 F per month


@SCENARIO1
@tracking
        Scenario: Min 11 F per month rule should pass when freedays are more than 12.
        
        Given tracking

        Given planning period from 1Oct2018 to 31Oct2018
   
       Given a crew member with
           | attribute       | value     | valid from | valid to |
           | base            | CPH        | 01OCT2018  | 01JAN2036 |
           | title rank      | AH         | 28OCT2018  | 01JAN2036 |
           | contract        | V300       | 01OCT2018  | 01JAN2036 |
         
      
        Given another trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ  |
         | leg | 0001 | CPH     | LAX     | 01Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0002 | LAX     | CPH     | 02Oct2018 | 10:00 | 21:45 | SK  | 320     |

        and crew member 1 has a personal activity "F" at station "CPH" that starts at 03Oct2018 22:00 and ends at 30oct2018 22:00

        Given trip 1 is assigned to crew member 1
      
        When I show "crew" in window 1
 
        Then the rule "rules_svs_indust_cct.ind_min_freedays_in_1_month_ALL" shall pass on leg 1 on trip 1 on roster 1

           
        
@SCENARIO2
@tracking
        Scenario: Min 11 F per month rule should pass pass when freedays are equal to 12.
        
        Given tracking
        
        Given planning period from 1Oct2018 to 30Oct2018
   
        Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 28JAN2014  | 01JAN2036 |
           | base            | OSL        | 01OCT2018  | 01JAN2036 |
           | title rank      | AH         | 28OCT2018  | 01JAN2036 |
           | contract        | V300       | 01OCT2018  | 01JAN2036 |
         
      
        Given a trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ  |
         | leg | 0001 | CPH     | LAX     | 1Oct2018  | 12:00 | 23:30 | SK  | 320     |
         | leg | 0002 | LAX     | OSL     | 2Oct2018  | 10:00 | 21:45 | SK  | 320     |
         | leg | 0003 | OSL     | LAX     | 03Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0004 | LAX     | OSL     | 04Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0005 | OSL     | LAX     | 05Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0006 | LAX     | OSL     | 06Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0007 | OSL     | LAX     | 07Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0008 | LAX     | OSL     | 08Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0009 | OSL     | LAX     | 09Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0010 | LAX     | OSL     | 10Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0011 | OSL     | LAX     | 11Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0012 | LAX     | OSL     | 12oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0013 | OSL     | CPH     | 13oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0014 | CPH     | LAX     | 14Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0015 | LAX     | OSL     | 15Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0016 | OSL     | LAX     | 16Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0017 | LAX     | OSL     | 17Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0018 | OSL     | LAX     | 18Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0019 | LAX     | CPH     | 19Oct2018 | 10:00 | 21:45 | SK  | 320     |
        
         

        Given trip 1 is assigned to crew member 1

        and crew member 1 has a personal activity "F" at station "CPH" that starts at 20Oct2018 22:00 and ends at 31Oct2018 22:00

        When I show "crew" in window 1
 
        Then the rule "rules_svs_indust_cct.ind_min_freedays_in_1_month_ALL" shall fail on leg 1 on trip 1 on roster 1

@SCENARIO3
@tracking
        Scenario: Min 11 F per month rule should fail when freedays are less than to 12.
        
        Given tracking
        
        Given planning period from 1Oct2018 to 30Oct2018
   
        Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 28JAN2014  | 01JAN2036 |
           | base            | OSL        | 01OCT2018  | 01JAN2036 |
           | title rank      | AH         | 28OCT2018  | 01JAN2036 |
           | contract        | V300       | 01OCT2018  | 01JAN2036 |
         
      
        Given a trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ  |
         | leg | 0001 | CPH     | LAX     | 1Oct2018  | 12:00 | 23:30 | SK  | 320     |
         | leg | 0002 | LAX     | OSL     | 2Oct2018  | 10:00 | 21:45 | SK  | 320     |
         | leg | 0003 | OSL     | LAX     | 03Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0004 | LAX     | OSL     | 04Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0005 | OSL     | LAX     | 05Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0006 | LAX     | OSL     | 06Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0007 | OSL     | LAX     | 07Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0008 | LAX     | OSL     | 08Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0009 | OSL     | LAX     | 09Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0010 | LAX     | OSL     | 10Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0011 | OSL     | LAX     | 11Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0012 | LAX     | OSL     | 12oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0013 | OSL     | CPH     | 13oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0014 | CPH     | LAX     | 14Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0015 | LAX     | OSL     | 15Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0016 | OSL     | LAX     | 16Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0017 | LAX     | OSL     | 17Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0018 | OSL     | LAX     | 18Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0019 | LAX     | CPH     | 19Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0020 | CPH     | LAX     | 20Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0021 | LAX     | OSL     | 21Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0022 | OSL     | LAX     | 22Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0023 | LAX     | OSL     | 23Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0024 | OSL     | LAX     | 24Oct2018 | 12:00 | 23:30 | SK  | 320     |
         | leg | 0025 | LAX     | OSL     | 25Oct2018 | 10:00 | 21:45 | SK  | 320     |
         | leg | 0026 | OSL     | LAX     | 26Oct2018 | 12:00 | 23:30 | SK  | 320     |
         

        Given trip 1 is assigned to crew member 1

        and crew member 1 has a personal activity "F" at station "CPH" that starts at 27Oct2018 22:00 and ends at 30Oct2018 22:00

        When I show "crew" in window 1
 
        Then the rule "rules_svs_indust_cct.ind_min_freedays_in_1_month_ALL" shall fail on leg 1 on trip 1 on roster 1