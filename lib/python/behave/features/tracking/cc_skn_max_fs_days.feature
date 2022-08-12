@TRACKING @SKAM-820
Feature: FS days counted by looking at table account_entry

  Background:
    Given Tracking

      ###################################################################
      @TEST_1
      Scenario: FS weekend increases the limit of FS days from 2 to 3.
      Given planning period from 25Dec2019 to 05Feb2020

      Given a crew member with homebase "OSL"

      Given table account_entry additionally contains the following
      | id   | crew          | tim              | account        | source          | amount | published | rate | reasoncode     |
      | 1    | crew member 1 | 11JAN2020 00:00  | FS             | Granted daysoff | -100   | true      | -100 | OUT Correction |
      | 2    | crew member 1 | 12JAN2020 00:00  | FS             | Granted daysoff | -100   | true      | -100 | OUT Correction |
      | 3    | crew member 1 | 15JAN2020 00:00  | FS             | Granted daysoff | -100   | true      | -100 | OUT Correction |

      Given crew member 1 has contract "SNK_V1025"

      and crew member 1 has a personal activity "FS" at station "OSL" that starts at 10JAN2020 23:00 and ends at 11JAN2020 23:00
      and crew member 1 has a personal activity "FS" at station "OSL" that starts at 11JAN2020 23:00 and ends at 12JAN2020 23:00
      and crew member 1 has a personal activity "FS" at station "OSL" that starts at 14JAN2020 23:00 and ends at 15JAN2020 23:00

      When I show "crew" in window 1
      Then rave "freedays.%no_of_fs_weekends_in_month%" shall be "1" on leg 1 on trip 1 on roster 1
      and  rave "rules_indust_ccr.%max_number_fs_in_month_nkf_snk_cc%" shall be "3" on leg 1 on trip 1 on roster 1
      and the rule "rules_indust_ccr.ind_max_fs_days_month_nkf_snk_cc" shall pass on leg 1 on trip 1 on roster 1

      ###################################################################
      @TEST_2
      Scenario: Placing 3rd FS day should be impossible when granted FS weekend is not in roster
      Given planning period from 1Jan2020 to 31Jan2020

      Given a crew member with homebase "OSL"

      Given table account_entry additionally contains the following
      | id   | crew          | tim              | account        | source          | amount | published | rate | reasoncode     |
      | 1    | crew member 1 | 03JAN2020 23:00  | FS             | Granted daysoff | -100   | true      | -100 | OUT Correction |
      | 2    | crew member 1 | 15JAN2020 23:00  | FS             | Granted daysoff | -100   | true      | -100 | OUT Correction |
      | 3    | crew member 1 | 21JAN2020 23:00  | FS             | Granted daysoff | -100   | true      | -100 | OUT Correction |

      Given crew member 1 has contract "SNK_V1025"
      and crew member 1 has a personal activity "FS" at station "OSL" that starts at 02JAN2020 23:00 and ends at 03JAN2020 23:00
      and crew member 1 has a personal activity "FS" at station "OSL" that starts at 14JAN2020 23:00 and ends at 15JAN2020 23:00
      and crew member 1 has a personal activity "FS" at station "OSL" that starts at 20JAN2020 23:00 and ends at 21JAN2020 23:00

      When I show "crew" in window 1
      Then rave "freedays.%no_of_fs_weekends_in_month%" shall be "0" on leg 1 on trip 1 on roster 1
      and  rave "rules_indust_ccr.%max_number_fs_in_month_nkf_snk_cc%" shall be "2" on leg 1 on trip 1 on roster 1
      and the rule "rules_indust_ccr.ind_max_fs_days_month_nkf_snk_cc" shall fail on leg 1 on trip 1 on roster 1


      ###################################################################
      @TEST_3
      Scenario: Having a FS1 on Saturday but no FS on Sunday should mean max_fs_days is 2
      Given planning period from 1Jan2019 to 31Jan2019

      Given a crew member with homebase "OSL"


      Given table account_entry additionally contains the following
      | id   | crew          | tim              | account        | source          | amount | published | rate | reasoncode     |
      | 1    | crew member 1 | 18JAN2020 00:00  | FS             | Granted daysoff | -100   | true      | -100 | OUT Correction |
      | 2    | crew member 1 | 22JAN2020 00:00  | FS             | Granted daysoff | -100   | true      | -100 | OUT Correction |

      Given crew member 1 has contract "SNK_V1025"
      and crew member 1 has a personal activity "FS1" at station "OSL" that starts at 17JAN2020 23:00 and ends at 18JAN2020 23:00
      and crew member 1 has a personal activity "FS" at station "OSL" that starts at 21JAN2020 23:00 and ends at 22JAN2020 23:00

      When I show "crew" in window 1
      Then rave "freedays.%no_of_fs_weekends_in_month%" shall be "0" on leg 1 on trip 1 on roster 1
      and  rave "rules_indust_ccr.%max_number_fs_in_month_nkf_snk_cc%" shall be "2" on leg 1 on trip 1 on roster 1
      and the rule "rules_indust_ccr.ind_max_fs_days_month_nkf_snk_cc" shall pass on leg 1 on trip 1 on roster 1

      ###################################################################
      @TEST_4
      Scenario: FS weekend crossing end of month should not count towards this month
      Given planning period from 01Feb2020 to 29Feb2020

      Given a crew member with homebase "OSL"

      Given table account_entry additionally contains the following
      | id   | crew          | tim              | account        | source          | amount | published | rate | reasoncode     |
      | 1    | crew member 1 | 29FEB2020 00:00  | FS             | Granted daysoff | -100   | true      | -100 | OUT Correction |
      | 2    | crew member 1 | 01MAR2020 00:00  | FS             | Granted daysoff | -100   | true      | -100 | OUT Correction |

      Given crew member 1 has contract "SNK_V1025"
      and crew member 1 has a personal activity "FS" at station "OSL" that starts at 28FEB2020 23:00 and ends at 29FEB2020 23:00
      and crew member 1 has a personal activity "FS" at station "OSL" that starts at 29FEB2020 23:00 and ends at 01MAR2020 23:00

      When I show "crew" in window 1
      Then rave "freedays.%no_of_fs_weekends_in_month%" shall be "0" on leg 1 on trip 1 on roster 1
      and  rave "rules_indust_ccr.%max_number_fs_in_month_nkf_snk_cc%" shall be "2" on leg 1 on trip 1 on roster 1
      and the rule "rules_indust_ccr.ind_max_fs_days_month_nkf_snk_cc" shall pass on leg 1 on trip 1 on roster 1

      ###################################################################
      @TEST_5
      Scenario: Having a FS weekend on Sunday as the first day of the month shall make that weekend count as a full weekend for that month.
      Given planning period from 1Dec2019 to 31Dec2019

      Given a crew member with homebase "OSL"

      Given table account_entry additionally contains the following
      | id   | crew          | tim              | account        | source          | amount | published | rate | reasoncode     |
      | 1    | crew member 1 | 01DEC2019 00:00  | FS             | Granted daysoff | -100   | true      | -100 | OUT Correction |
      | 2    | crew member 1 | 30NOV2019 00:00  | FS             | Granted daysoff | -100   | true      | -100 | OUT Correction |

      Given crew member 1 has contract "SNK_V1025"
      and crew member 1 has a personal activity "FS1" at station "OSL" that starts at 01DEC2019 00:00 and ends at 01DEC2019 23:00
      and crew member 1 has a personal activity "FS1" at station "OSL" that starts at 30NOV2019 00:00 and ends at 30NOV2019 23:00

      When I show "crew" in window 1
      Then rave "freedays.%no_of_fs_weekends_in_month%" shall be "1" on leg 1 on trip 1 on roster 1
      and rave "rules_indust_ccr.%max_number_fs_in_month_nkf_snk_cc%" shall be "3" on leg 1 on trip 1 on roster 1
      and the rule "rules_indust_ccr.ind_max_fs_days_month_nkf_snk_cc" shall pass on leg 1 on trip 1 on roster 1


      ###################################################################
      @TEST_6 @TRACKING @SKAM-820
      Scenario: FS days in table account_entry counts towards FS weekends
      Given planning period from 1Jan2019 to 31Jan2019
      Given a crew member with homebase "OSL"
      Given table account_entry additionally contains the following
      | id   | crew          | tim             | account | source          | amount |
      | 1    | crew member 1 | 5JAN2019 22:00  | FS      | Granted daysoff | -100   |
      | 2    | crew member 1 | 6JAN2019 22:00  | FS      | Granted daysoff | -100   |
      Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 1JAN2019 22:00 and ends at 10JAN2019 22:00
      When I show "crew" in window 1
      Then rave "freedays.%no_of_fs_weekends_in_month%" shall be "1" on leg 1 on trip 1 on roster 1


      ###################################################################
      @TEST_7 @TRACKING @SKAM-820
      Scenario: Placing 3rd FS day should be possible when granted FS weekend is not in roster
      Given planning period from 1Jan2019 to 31Jan2019
      Given a crew member with homebase "OSL"
      Given table account_entry additionally contains the following
      | id   | crew          | tim             | account | source          | amount |
      | 1    | crew member 1 | 5JAN2019 22:00  | FS      | Granted daysoff | -100   |
      | 2    | crew member 1 | 6JAN2019 22:00  | FS      | Granted daysoff | -100   |
      Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 1JAN2019 22:00 and ends at 10JAN2019 22:00
      Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 16JAN2019 22:00 and ends at 17JAN2019 22:00
      When I show "crew" in window 1
      Then rave "freedays.%no_of_fs_weekends_in_month%" shall be "1" on leg 1 on trip 2 on roster 1
      and the rule "rules_indust_ccr.ind_max_fs_days_month_nkf_snk_cc" shall pass on leg 1 on trip 2 on roster 1