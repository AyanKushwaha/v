Feature: Check F0 handling throught changed activity group for SKN
  Background: Setup data tables

    Given table account_entry additionally contains the following
	| id   | crew          | tim      | account | source           | amount | man   |
	| 0001 | crew member 1 | 1JAN2019 | F0      | Entitled F0 days | 200    | False |

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    and crew member 1 has contract "SNK_V301"


    @SCENARIO_1
    Scenario: Crew has a single F0 day
    Given planning period from 1JAN2019 to 31JAN2019
    Given Rostering_CC

    Given crew member 1 has a personal activity "F0" at station "OSL" that starts at 8jan2019 23:00 and ends at 9jan2019 23:00

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 7jan2019 | 19:00 | 19:45 |
    | leg | 002 | GOT     | OSL     | 7jan2019 | 21:00 | 21:45 |
    Given trip 1 is assigned to crew member 1

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 8jan2019 | 19:00 | 19:45 |
    | leg | 002 | GOT     | OSL     | 8jan2019 | 21:00 | 21:45 |
    Given trip 2 is assigned to crew member 1
    
    Given a trip with the following activities
    | act | num | dep stn | arr stn | date      | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 10jan2019 | 12:49 | 13:35 |
    | leg | 002 | GOT     | OSL     | 10jan2019 | 15:00 | 15:45 |
    Given trip 3 is assigned to crew member 1
    
    When I show "crew" in window 1
    Then the rule "rules_indust_ccr.ind_min_freedays_after_duty_all" shall fail on leg 1 on trip 2 on roster 1
    and rave "rules_indust_ccr.%ind_min_freedays_after_duty_ALL_valid%" shall be "True" on leg 1 on trip 2 on roster 1


    @SCENARIO_2
    Scenario: Crew has a single F0 day during weekend
    Given planning period from 1JAN2019 to 31JAN2019
    Given Rostering_CC

    Given crew member 1 has a personal activity "F0" at station "OSL" that starts at 12jan2019 23:00 and ends at 13jan2019 23:00

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 11jan2019 | 19:00 | 19:45 |
    | leg | 002 | GOT     | OSL     | 11jan2019 | 21:00 | 21:45 |
    Given trip 1 is assigned to crew member 1

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 12jan2019 | 19:00 | 19:45 |
    | leg | 002 | GOT     | OSL     | 12jan2019 | 21:00 | 21:45 |
    Given trip 2 is assigned to crew member 1
    
    Given a trip with the following activities
    | act | num | dep stn | arr stn | date      | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 14jan2019 | 13:49 | 15:35 |
    | leg | 002 | GOT     | OSL     | 14jan2019 | 16:00 | 18:45 |
    Given trip 3 is assigned to crew member 1
    
    When I show "crew" in window 1
    Then the rule "rules_indust_ccr.ind_min_freedays_after_duty_all" shall fail on leg 1 on trip 2 on roster 1
    and rave "rules_indust_ccr.%ind_min_freedays_after_duty_ALL_valid%" shall be "True" on leg 1 on trip 2 on roster 1


    @SCENARIO_3
    Scenario: Crew has a two F0 days
    Given planning period from 1JAN2019 to 31JAN2019
    Given Rostering_CC

    Given crew member 1 has a personal activity "F0" at station "OSL" that starts at 8jan2019 23:00 and ends at 10jan2019 23:00

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 7jan2019 | 19:00 | 19:45 |
    | leg | 002 | GOT     | OSL     | 7jan2019 | 21:00 | 21:45 |
    Given trip 1 is assigned to crew member 1

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 8jan2019 | 19:00 | 19:45 |
    | leg | 002 | GOT     | OSL     | 8jan2019 | 21:00 | 21:45 |
    Given trip 2 is assigned to crew member 1
    
    Given a trip with the following activities
    | act | num | dep stn | arr stn | date      | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 11jan2019 | 12:49 | 13:35 |
    | leg | 002 | GOT     | OSL     | 11jan2019 | 15:00 | 15:45 |
    Given trip 3 is assigned to crew member 1
    
    When I show "crew" in window 1
    Then the rule "rules_indust_ccr.ind_min_freedays_after_duty_all" shall pass on leg 1 on trip 2 on roster 1
    and rave "rules_indust_ccr.%ind_min_freedays_after_duty_ALL_valid%" shall be "True" on leg 1 on trip 2 on roster 1


    @SCENARIO_4
    Scenario: Crew has a one F0 day before a F day
    Given planning period from 1JAN2019 to 31JAN2019
    Given Rostering_CC

    Given crew member 1 has a personal activity "F0" at station "OSL" that starts at 8jan2019 23:00 and ends at 9jan2019 23:00

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 7jan2019 | 19:00 | 19:45 |
    | leg | 002 | GOT     | OSL     | 7jan2019 | 21:00 | 21:45 |
    Given trip 1 is assigned to crew member 1

    Given a trip with the following activities
    | act | num | dep stn | arr stn | date     | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 8jan2019 | 19:00 | 19:45 |
    | leg | 002 | GOT     | OSL     | 8jan2019 | 21:00 | 21:45 |
    Given trip 2 is assigned to crew member 1
    
    Given a trip with the following activities
    | act | num | dep stn | arr stn | date      | dep   | arr   |
    | leg | 001 | OSL     | GOT     | 11jan2019 | 12:49 | 13:35 |
    | leg | 002 | GOT     | OSL     | 11jan2019 | 15:00 | 15:45 |
    Given trip 3 is assigned to crew member 1
    
    When I show "crew" in window 1
    Then the rule "rules_indust_ccr.ind_min_freedays_after_duty_all" shall pass on leg 1 on trip 2 on roster 1
    and rave "rules_indust_ccr.%ind_min_freedays_after_duty_ALL_valid%" shall be "True" on leg 1 on trip 2 on roster 1
