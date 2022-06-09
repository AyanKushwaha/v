Feature: Setup for applying rule to enable F0 on full weekend even if full FS weekend already granted. Opposite is
however not legal. Full FS weekend is not to be granted if F0 weekend is already granted. Testing both ind_fs_on_weekend
and ind_fs_weekend_can_be_granted in rules_indust_ccr

    ##############################################################################################################
    # Scenarios that shall pass
    ##############################################################################################################
        @tracking @pass_1
        Scenario: Rule passes if FS weekend is existant in month and F0 weekend is requested.

        Given planning period from 1Nov2018 to 30Nov2018

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "V00204"

         # Places an entry that gives an FS weekend granted status
        Given table crew_roster_request additionally contains the following
	    | crew          | id     | type | st        | et        |
	    | crew member 1 | 0001   | FS   | 3Nov2018  | 5Nov2018  |

        Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 3NOV2018 23:00 and ends at 5NOV2018 23:00
        Given crew member 1 has a personal activity "F0" at station "OSL" that starts at 10NOV2018 23:00 and ends at 12NOV2018 23:00

        When I show "crew" in window 1
        When I load rule set "rule_set_jcr"
        When I set parameter "fundamental.%start_para%" to "1NOV2018 00:00"
        When I set parameter "fundamental.%end_para%" to "30NOV2018 00:00"
        Then the rule "rules_indust_ccr.ind_fs_on_weekend" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall pass on leg 1 on trip 1 on roster 1

    ##############################################################################################################
        @tracking @pass_2
        Scenario: Rule passes if FS weekend is requested and F0 weekend occurs on month break

        Given planning period from 1Aug2019 to 30Sep2019

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "V00204"

        Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 3AUG2019 23:00 and ends at 5AUG2019 23:00
        Given crew member 1 has a personal activity "F0" at station "OSL" that starts at 31AUG2019 23:00 and ends at 2SEP2019 23:00

        When I show "crew" in window 1
        When I load rule set "rule_set_jcr"
        When I set parameter "fundamental.%start_para%" to "1AUG2019 00:00"
        When I set parameter "fundamental.%end_para%" to "30SEP2019 00:00"
        Then the rule "rules_indust_ccr.ind_fs_on_weekend" shall pass on leg 1 on trip 1 on roster 1

    ##############################################################################################################
    # Scenarios that shall fail
    ##############################################################################################################
        @tracking @fail_1
        Scenario: Rule fails if F0 weekend is already existant when FS weekend is requested.

        Given planning period from 1Nov2018 to 30Nov2018

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "V00204"

        Given crew member 1 has a personal activity "F0" at station "OSL" that starts at 3NOV2018 23:00 and ends at 5NOV2018 23:00
        Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 10NOV2018 23:00 and ends at 12NOV2018 23:00

        When I show "crew" in window 1
        When I load rule set "rule_set_jcr"
        When I set parameter "fundamental.%start_para%" to "1NOV2018 00:00"
        When I set parameter "fundamental.%end_para%" to "30NOV2018 00:00"
        Then the rule "rules_indust_ccr.ind_fs_on_weekend" shall fail on leg 1 on trip 2 on roster 1
        and rave "rules_indust_ccr.%has_no_more_than_1_weekend_with_fs_in_month%" shall be "False" on leg 1 on trip 2 on roster 1



