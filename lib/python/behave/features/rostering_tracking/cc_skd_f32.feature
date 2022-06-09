Feature: Check rule that prevent more than 5 F3S days to be placed in a sequence.

    Background: The F32 days should cost 1 to 1 

    Given planning period from 1OCT2020 to 31OCT2020
    Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | CPH     |             |           |
        | title rank | CC      |             |           |
        | region     | SKD     |             |           |
		
    ###################################################################################################
    # Scenarios that shall pass for CC, evaluating days in a row
    ###################################################################################################

        @tracking @SCENARIO_1
        Scenario: Case pass if there is 1 F32 days in a sequence (one activity)

        Given planning period from 1OCT2020 to 31OCT2020

        Given crew member 1 has a personal activity "F32" at station "CPH" that starts at 17OCT2020 23:00 and ends at 18OCT2020 23:00

        When I show "crew" in window 1
        When I load rule set "Tracking"

        Then rave "compdays.%leg_affects_amount%(leg.%code%)" shall be "-100" on leg 1 on trip 1 on roster 1

    ###################################################################################################
        
        @tracking @SCENARIO_2
        Scenario: Case pass if there is 2 F32 days in a sequence (one activity)

        Given planning period from 1OCT2020 to 31OCT2020


        Given crew member 1 has a personal activity "F32" at station "CPH" that starts at 17OCT2020 23:00 and ends at 19OCT2020 23:00

        When I show "crew" in window 1
        When I load rule set "Tracking"

        Then rave "compdays.%leg_affects_amount%(leg.%code%)" shall be "-200" on leg 1 on trip 1 on roster 1

    ###################################################################################################
    
        @tracking @SCENARIO_3
        Scenario: Case pass if there is 2 F32 days in two activities

        Given crew member 1 has a personal activity "F32" at station "CPH" that starts at 17OCT2020 23:00 and ends at 18OCT2020 23:00
        Given crew member 1 has a personal activity "F32" at station "CPH" that starts at 21OCT2020 23:00 and ends at 22OCT2020 23:00

        When I show "crew" in window 1
        When I load rule set "Tracking"

        Then rave "compdays.%leg_affects_amount%(leg.%code%)" shall be "-100" on leg 1 on trip 1 on roster 1
        and rave "compdays.%leg_affects_amount%(leg.%code%)" shall be "-100" on leg 1 on trip 2 on roster 1



