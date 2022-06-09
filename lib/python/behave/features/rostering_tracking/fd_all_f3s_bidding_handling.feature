Feature: Check rule that prevent more than 5 F3S days to be placed in a sequence.

    Background: The K19 agreement included an entitlement of 2 F3S per calendar year. Which should follow rules described in SKCMS-2286.
		
    ###################################################################################################
    # Scenarios that shall pass for FD, evaluating days in a row
    ###################################################################################################

        @planning @SCENARIO_1
        Scenario: Case pass if there is 5 F3S days in a sequence (one activity)

        Given planning period from 1JAN2020 to 31JAN2020

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | FC      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "F00102"

        Given crew member 1 has a personal activity "F3S" at station "ARN" that starts at 17JAN2020 23:00 and ends at 22JAN2020 23:00

        When I show "crew" in window 1
        When I load rule set "rule_set_jcr_fc"
        When I set parameter "fundamental.%start_para%" to "1JAN2020 00:00"
        When I set parameter "fundamental.%end_para%" to "31JAN2020 00:00"

        Then rave "base_product.%is_rostering%" shall be "True" on leg 1 on trip 1 on roster 1
        and rave "rules_indust_ccr.%ind_max_f3s_in_sequence_valid%" shall be "True" on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_max_f3s_in_sequence" shall pass on leg 1 on trip 1 on roster 1


    ###################################################################################################

        @planning @SCENARIO_2
        Scenario: Case pass if there is 2 F3S days in a sequence (split activity)

        Given planning period from 1JAN2020 to 31JAN2020

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | FC      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "F00102"

        Given crew member 1 has a personal activity "F3S" at station "ARN" that starts at 17JAN2020 23:00 and ends at 19JAN2020 23:00
        Given crew member 1 has a personal activity "F3S" at station "ARN" that starts at 19JAN2020 23:00 and ends at 22JAN2020 23:00

        When I show "crew" in window 1
        When I load rule set "rule_set_jcr_fc"
        Then rave "base_product.%is_rostering%" shall be "True" on leg 1 on trip 1 on roster 1
        and rave "rules_indust_ccr.%ind_max_f3s_in_sequence_valid%" shall be "True" on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_max_f3s_in_sequence" shall pass on leg 1 on trip 1 on roster 1

    ###################################################################################################

        @planning @SCENARIO_3
        Scenario: Case pass if there is 5 F3S days in a sequence (split activity)

        Given planning period from 1JAN2020 to 31JAN2020

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | FC      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "F00102"

        Given crew member 1 has a personal activity "F3S" at station "ARN" that starts at 17JAN2020 23:00 and ends at 18JAN2020 23:00
        Given crew member 1 has a personal activity "F3S" at station "ARN" that starts at 18JAN2020 23:00 and ends at 19JAN2020 23:00
        Given crew member 1 has a personal activity "F3S" at station "ARN" that starts at 19JAN2020 23:00 and ends at 20JAN2020 23:00
        Given crew member 1 has a personal activity "F3S" at station "ARN" that starts at 20JAN2020 23:00 and ends at 21JAN2020 23:00
        Given crew member 1 has a personal activity "F3S" at station "ARN" that starts at 21JAN2020 23:00 and ends at 22JAN2020 23:00

        When I show "crew" in window 1
        When I load rule set "rule_set_jcr_fc"
        Then rave "base_product.%is_rostering%" shall be "True" on leg 1 on trip 1 on roster 1
        and rave "rules_indust_ccr.%ind_max_f3s_in_sequence_valid%" shall be "True" on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_max_f3s_in_sequence" shall pass on leg 1 on trip 1 on roster 1


    ###################################################################################################
    # Scenarios that shall fail for FD, evaluating days in a row
    ###################################################################################################

        @planning @SCENARIO_4
        Scenario: Case fails if there is more than 5 F3S days in a sequence (one activity)

	    Given planning period from 1JAN2020 to 31JAN2020

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | FC      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "F00102"

        Given crew member 1 has a personal activity "F3S" at station "ARN" that starts at 17JAN2020 23:00 and ends at 23JAN2020 23:00

        When I show "crew" in window 1
        When I load rule set "rule_set_jcr_fc"
        Then rave "base_product.%is_rostering%" shall be "True" on leg 1 on trip 1 on roster 1
        and rave "rules_indust_ccr.%ind_max_f3s_in_sequence_valid%" shall be "True" on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_max_f3s_in_sequence" shall fail on leg 1 on trip 1 on roster 1

    ###################################################################################################

        @planning @SCENARIO_5
        Scenario: Case fails if there is more than 5 F3S days in a sequence (split activity)

	    Given planning period from 1JAN2020 to 31JAN2020

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | FC      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "F00102"

        Given crew member 1 has a personal activity "F3S" at station "ARN" that starts at 17JAN2020 23:00 and ends at 18JAN2020 23:00
        Given crew member 1 has a personal activity "F3S" at station "ARN" that starts at 18JAN2020 23:00 and ends at 19JAN2020 23:00
        Given crew member 1 has a personal activity "F3S" at station "ARN" that starts at 19JAN2020 23:00 and ends at 20JAN2020 23:00
        Given crew member 1 has a personal activity "F3S" at station "ARN" that starts at 20JAN2020 23:00 and ends at 21JAN2020 23:00
        Given crew member 1 has a personal activity "F3S" at station "ARN" that starts at 21JAN2020 23:00 and ends at 22JAN2020 23:00
        Given crew member 1 has a personal activity "F3S" at station "ARN" that starts at 22JAN2020 23:00 and ends at 23JAN2020 23:00

        When I show "crew" in window 1
        When I load rule set "rule_set_jcr_fc"
        Then rave "base_product.%is_rostering%" shall be "True" on leg 1 on trip 1 on roster 1
        and rave "rules_indust_ccr.%ind_max_f3s_in_sequence_valid%" shall be "True" on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_max_f3s_in_sequence" shall fail on leg 1 on trip 6 on roster 1

    ###################################################################################################
    # Scenarios that shall pass for FD, same scenarios as scenario 1 but with VG
    ###################################################################################################

        @tracking @SCENARIO_6
        Scenario: Case pass if there is 5 F3S days in a sequence (one activity)

        Given planning period from 1JAN2020 to 31JAN2020

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | FC      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V133"

        Given crew member 1 has a personal activity "F3S" at station "ARN" that starts at 17JAN2020 23:00 and ends at 22JAN2020 23:00

        When I show "crew" in window 1
        When I load rule set "rule_set_jcr_fc"
        Then rave "base_product.%is_rostering%" shall be "True" on leg 1 on trip 1 on roster 1
        and rave "rules_indust_ccr.%ind_max_f3s_in_sequence_valid%" shall be "True" on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_max_f3s_in_sequence" shall pass on leg 1 on trip 1 on roster 1

    ###################################################################################################
    # Scenarios that shall pass for FD, same scenarios as scenario 1 but with VG - in tracking
    ###################################################################################################

        @tracking @SCENARIO_7
        Scenario: Case pass if there is 5 F3S days in a sequence (one activity)

        Given planning period from 1JAN2020 to 31JAN2020

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | FC      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V133"

        Given crew member 1 has a personal activity "F3S" at station "ARN" that starts at 17JAN2020 23:00 and ends at 22JAN2020 23:00

        When I show "crew" in window 1
        When I load rule set "rule_set_jct"
        Then rave "base_product.%is_tracking%" shall be "True" on leg 1 on trip 1 on roster 1
        and rave "rules_indust_ccr.%ind_max_f3s_in_sequence_valid%" shall be "True" on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_max_f3s_in_sequence" shall pass on leg 1 on trip 1 on roster 1

    ###################################################################################################
    # Scenarios that shall pass for FD, 2 weekends
    ###################################################################################################

        @tracking @SCENARIO_8
        Scenario: Case pass if already granted VA or LOA weekend

        Given planning period from 1JAN2020 to 31JAN2020

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | FC      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "V130"

        Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 01JAN2020 23:00 and ends at 08JAN2020 23:00
        Given crew member 1 has a personal activity "F3S" at station "OSL" that starts at 17JAN2020 23:00 and ends at 19JAN2020 23:00

        When I show "crew" in window 1
        When I load rule set "rule_set_jct"

        Then the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall pass on leg 1 on trip 2 on roster 1
	
   ###################################################################################################

        @planning @SCENARIO_9
        Scenario: Case pass if already granted VA or LOA weekend

        Given planning period from 1JAN2020 to 31JAN2020

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | FC      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "F00102"

        Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 01JAN2020 23:00 and ends at 08JAN2020 23:00
        Given crew member 1 has a personal activity "F3S" at station "ARN" that starts at 17JAN2020 23:00 and ends at 19JAN2020 23:00

        When I show "crew" in window 1
        When I load rule set "rule_set_jct"

        Then the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall pass on leg 1 on trip 2 on roster 1

