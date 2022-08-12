Feature: Check that available F0 days can't be exceeded

        @tracking
        Scenario: Crew has enough F0 days for single F0 day
        Given planning period from 1JAN2019 to 31JAN2019

        Given a crew member with
        | attribute  | value  | valid from | valid to
        | base       | OSL    |            |
        | title rank | AH     |            |
        | region     | SKN    |            |

	    Given crew member 1 has a personal activity "F0" at station "OSL" that starts at 25JAN2019 23:00 and ends at 26JAN2019 23:00

        # Legacy(?) code touches this table entry, but it does not affect the end result.
	    # Given table accumulator_int_run additionally contains the following
	    # | accname | acckey | accstart  | accend    | lastrun   |
	    # | balance | C      | 31DEC2012 | 31DEC2012 | 30APR2014 |

        Given table account_entry additionally contains the following
	    | id   | crew          | tim      | account | source           | amount | man   |
	    | 0001 | crew member 1 | 1JAN2018 | F0      | Entitled F0 days | 100    | False |

        When I show "crew" in window 1
        When I load rule set "Tracking"

        Then the rule "rules_studio_ccr.sft_nr_comp_days_must_not_exceed_balance_all" shall pass on leg 1 on trip 1 on roster 1

        ###############################################################################

        @tracking
        Scenario: Crew has does not have enough F0 days for double F0 day
        Given planning period from 1JAN2019 to 31JAN2019

        Given a crew member with
        | attribute  | value  | valid from | valid to
        | base       | OSL    |            |
        | title rank | AH     |            |
        | region     | SKN    |            |

	    Given crew member 1 has a personal activity "F0" at station "OSL" that starts at 24JAN2019 23:00 and ends at 26JAN2019 23:00

        Given table account_entry additionally contains the following
	    | id   | crew          | tim      | account | source           | amount | man   |
	    | 0001 | crew member 1 | 1JAN2018 | F0      | Entitled F0 days | 100    | False |

        When I show "crew" in window 1
        When I load rule set "Tracking"

        Then the rule "rules_studio_ccr.sft_nr_comp_days_must_not_exceed_balance_all" shall fail on leg 1 on trip 1 on roster 1

        ###############################################################################

        @tracking
        Scenario: Crew has does not have enough F0 days for two single F0 days
        Given planning period from 1JAN2019 to 31JAN2019

        Given a crew member with
        | attribute  | value  | valid from | valid to
        | base       | OSL    |            |
        | title rank | AH     |            |
        | region     | SKN    |            |

	    Given crew member 1 has a personal activity "F0" at station "OSL" that starts at 14JAN2019 23:00 and ends at 15JAN2019 23:00
	    Given crew member 1 has a personal activity "F0" at station "OSL" that starts at 24JAN2019 23:00 and ends at 25JAN2019 23:00

        Given table account_entry additionally contains the following
	    | id   | crew          | tim      | account | source           | amount | man   |
	    | 0001 | crew member 1 | 1JAN2018 | F0      | Entitled F0 days | 100    | False |

        When I show "crew" in window 1
        When I load rule set "Tracking"

        Then the rule "rules_studio_ccr.sft_nr_comp_days_must_not_exceed_balance_all" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_studio_ccr.sft_nr_comp_days_must_not_exceed_balance_all" shall fail on leg 1 on trip 2 on roster 1

        ###############################################################################

        @tracking
        Scenario: Crew has does not have any F0 days in account
        Given planning period from 1JAN2019 to 31JAN2019

        Given a crew member with
        | attribute  | value  | valid from | valid to
        | base       | OSL    |            |
        | title rank | AH     |            |
        | region     | SKN    |            |

	    Given crew member 1 has a personal activity "F0" at station "OSL" that starts at 14JAN2019 23:00 and ends at 15JAN2019 23:00


        Given table account_entry additionally contains the following
	    | id   | crew          | tim      | account | source           | amount | man   |
	    | 0001 | crew member 1 | 1JAN2018 | F0      | Entitled F0 days | 0      | False |

        When I show "crew" in window 1
        When I load rule set "Tracking"

        Then the rule "rules_studio_ccr.sft_nr_comp_days_must_not_exceed_balance_all" shall fail on leg 1 on trip 1 on roster 1

