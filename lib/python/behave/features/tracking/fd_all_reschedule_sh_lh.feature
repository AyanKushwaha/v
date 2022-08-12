##########################
# Developed in SKCMS-2381
##########################
@TRACKING @MFF @FD
Feature: Rescheduling of MFF

  Background: set up for tracking
    Given Tracking
    Given planning period from 1mar2020 to 31mar2020

    Given table crew_contract_set is overridden with the following
    |  id  | desclong |
    | V131 | 100%MFF  |

    ##########################
    # FD should not be able to be rescheduled to later check-out time if SH+LH in wop
    ##########################
    @SCENARIO1
    Scenario: MFF FD should not be able to have LH flight rescheduled to later check-out time if SH+LH in wop
    Given a crew member with
      | attribute  | value  |
      | base       | CPH    |
      | title rank | FC     |
      | region     | SKD    |
    Given crew member 1 has contract "V131"
    Given a trip with the following activities
      | act     | car     | num | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
      | leg     | SK      | 101 | CPH     | AMS     | 05MAR2020 14:25 | 05MAR2020 15:50 | 320     |         |
      | leg     | SK      | 102 | AMS     | CPH     | 05MAR2020 16:30 | 05MAR2020 17:50 | 320     |         |
      | leg     | SK      | 103 | CPH     | TXL     | 05MAR2020 18:35 | 05MAR2020 19:35 | 320     |         |
      | leg     | SK      | 104 | TXL     | ARN     | 05MAR2020 20:10 | 05MAR2020 21:10 | 320     |         |
      | leg     | SK      | 105 | ARN     | MIA     | 06MAR2020 08:15 | 06MAR2020 18:55 | 33B     |         |
      | leg     | SK      | 106 | MIA     | ARN     | 07MAR2020 20:45 | 08MAR2020 06:15 | 33B     |         |
    Given trip 1 is assigned to crew member 1 in position FC
    Given crew member 1 has a personal activity "F" at station "CPH" that starts at 8MAR2020 23:00 and ends at 9MAR2020 23:00

    Given the roster is published

    When I show "rosters" in window 1
    When I reschedule leg 6 of crew member 1 flight 106 to depart from MIA 07MAR2020 22:00 and arrive at ARN 08MAR2020 06:30

    Then rave "wop.%is_SH_LH%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_resched_cct.resched_SH_LH_FC_later_co" shall fail on leg 6 on trip 1 on roster 1


    @SCENARIO2
    Scenario: Non-MFF FD should not be able to have LH flight rescheduled to later check-out time if SH+LH in wop
    Given a crew member with
      | attribute  | value  |
      | base       | CPH    |
      | title rank | FC     |
      | region     | SKD    |
    Given crew member 1 has contract "V00145-LH"
    Given a trip with the following activities
      | act     | car     | num | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
      | leg     | SK      | 101 | CPH     | AMS     | 05MAR2020 14:25 | 05MAR2020 15:50 | 320     |         |
      | leg     | SK      | 102 | AMS     | CPH     | 05MAR2020 16:30 | 05MAR2020 17:50 | 320     |         |
      | leg     | SK      | 103 | CPH     | TXL     | 05MAR2020 18:35 | 05MAR2020 19:35 | 320     |         |
      | leg     | SK      | 104 | TXL     | ARN     | 05MAR2020 20:10 | 05MAR2020 21:10 | 320     |         |
      | leg     | SK      | 105 | ARN     | MIA     | 06MAR2020 08:15 | 06MAR2020 18:55 | 33B     |         |
      | leg     | SK      | 106 | MIA     | ARN     | 07MAR2020 20:45 | 08MAR2020 06:15 | 33B     |         |
    Given trip 1 is assigned to crew member 1 in position FC
    Given crew member 1 has a personal activity "F" at station "CPH" that starts at 8MAR2020 23:00 and ends at 9MAR2020 23:00

    Given the roster is published

    When I show "rosters" in window 1
    When I reschedule leg 6 of crew member 1 flight 106 to depart from MIA 07MAR2020 22:00 and arrive at ARN 08MAR2020 06:30

    Then rave "wop.%is_SH_LH%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_resched_cct.resched_SH_LH_FC_later_co" shall fail on leg 6 on trip 1 on roster 1


    @SCENARIO3
    Scenario: FD should not be able to have deadhead flight rescheduled to later check-out time if SH+LH in wop
    Given a crew member with
      | attribute  | value  |
      | base       | CPH    |
      | title rank | FC     |
      | region     | SKD    |
    Given crew member 1 has contract "V131"
    Given a trip with the following activities
      | act     | car     | num | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
      | leg     | SK      | 101 | CPH     | AMS     | 05MAR2020 14:25 | 05MAR2020 15:50 | 320     |         |
      | leg     | SK      | 102 | AMS     | CPH     | 05MAR2020 16:30 | 05MAR2020 17:50 | 320     |         |
      | leg     | SK      | 103 | CPH     | TXL     | 05MAR2020 18:35 | 05MAR2020 19:35 | 320     |         |
      | leg     | SK      | 104 | TXL     | ARN     | 05MAR2020 20:10 | 05MAR2020 21:10 | 320     |         |
      | leg     | SK      | 105 | ARN     | MIA     | 06MAR2020 08:15 | 06MAR2020 18:55 | 33B     |         |
      | leg     | SK      | 106 | MIA     | ARN     | 07MAR2020 20:45 | 08MAR2020 06:15 | 33B     |         |
      | leg     | SK      | 107 | ARN     | CPH     | 08MAR2020 06:55 | 08MAR2020 08:05 | CRH     |         |
    Given trip 1 is assigned to crew member 1 in position FC
    Given crew member 1 has a personal activity "F" at station "CPH" that starts at 8MAR2020 23:00 and ends at 9MAR2020 23:00

    Given the roster is published

    When I show "rosters" in window 1
    and I select leg 7
    and I Change to/from Deadhead
    When I reschedule leg 7 of crew member 1 flight 107 to depart from ARN 08MAR2020 07:00 and arrive at CPH 08MAR2020 08:10

    Then rave "wop.%is_SH_LH%" shall be "True" on leg 1 on trip 1
    and the rule "rules_resched_cct.resched_SH_LH_FC_later_co" shall fail on leg 7 on trip 1


    @SCENARIO4
    Scenario: FD should be able to have deadhead flight rescheduled to later check-out time if only SH in wop
    Given a crew member with
      | attribute  | value  |
      | base       | CPH    |
      | title rank | FC     |
      | region     | SKD    |
    Given crew member 1 has contract "V131"
    Given a trip with the following activities
      | act     | car     | num | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
      | leg     | SK      | 101 | CPH     | AMS     | 05MAR2020 14:25 | 05MAR2020 15:50 | 320     |         |
      | leg     | SK      | 102 | AMS     | CPH     | 05MAR2020 16:30 | 05MAR2020 17:50 | 320     |         |
      | leg     | SK      | 103 | CPH     | TXL     | 05MAR2020 18:35 | 05MAR2020 19:35 | 320     |         |
      | leg     | SK      | 104 | TXL     | ARN     | 05MAR2020 20:10 | 05MAR2020 21:10 | 320     |         |
      | leg     | SK      | 105 | ARN     | CPH     | 05MAR2020 22:00 | 05MAR2020 23:10 | CRH     |         |
    Given trip 1 is assigned to crew member 1 in position FC

    Given the roster is published

    When I show "rosters" in window 1
    and I select leg 5
    and I Change to/from Deadhead
    When I reschedule leg 5 of crew member 1 flight 105 to depart from ARN 05MAR2020 22:10 and arrive at CPH 05MAR2020 23:20

    Then rave "wop.%is_SH_LH%" shall be "False" on leg 1 on trip 1
    and the rule "rules_resched_cct.resched_SH_LH_FC_later_co" shall pass on leg 4 on trip 1


    @SCENARIO5
    Scenario: FD should be able to have deadhead flight rescheduled to later check-out time if only LH in wop
    Given a crew member with
      | attribute  | value  |
      | base       | CPH    |
      | title rank | FC     |
      | region     | SKD    |
    Given crew member 1 has contract "V131"
    Given a trip with the following activities
      | act     | car     | num | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
      | leg     | SK      | 101 | CPH     | ARN     | 06MAR2020 05:00 | 06MAR2020 06:10 | CRH     |         |
      | leg     | SK      | 102 | ARN     | MIA     | 06MAR2020 08:15 | 06MAR2020 18:55 | 33B     |         |
      | leg     | SK      | 103 | MIA     | ARN     | 07MAR2020 20:45 | 08MAR2020 06:15 | 33B     |         |
      | leg     | SK      | 104 | ARN     | CPH     | 08MAR2020 06:55 | 08MAR2020 08:05 | CRH     |         |
    Given trip 1 is assigned to crew member 1 in position FC
    Given crew member 1 has a personal activity "F" at station "CPH" that starts at 8MAR2020 23:00 and ends at 9MAR2020 23:00

    Given the roster is published

    When I show "rosters" in window 1
    and I select leg 1
    and I Change to/from Deadhead
    and I select leg 4
    and I Change to/from Deadhead
    When I reschedule leg 4 of crew member 1 flight 104 to depart from ARN 08MAR2020 07:00 and arrive at CPH 08MAR2020 08:10

    Then rave "wop.%is_SH_LH%" shall be "False" on leg 1 on trip 1
    and the rule "rules_resched_cct.resched_SH_LH_FC_later_co" shall pass on leg 4 on trip 1
