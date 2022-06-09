@JCRT @CC @TRACKING @TRAINING
Feature: Exclude crew with supernum position when counting number of temporary crew on flight

########################
# JIRA - SKCMS-2021
########################

  Background:
    Given Tracking

  @tracking @SKN_1
  Scenario: Region SKN, too many temporary crew, no supernum.

    Given planning period from 1JUL2019 to 31JUL2019

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AP      |             |           |
    | region     | SKN     |             |           |
    Given crew member 1 has contract "V345"

    Given another crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    Given crew member 2 has contract "V345"

    Given another crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    Given crew member 3 has contract "V345"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | ARN     | 09JUL2019 | 06:00 | 07:10 | SK  | 320    |
    | leg | 0002 | ARN     | CPH     | 09JUL2019 | 07:55 | 09:10 | SK  | 320    |
    | leg | 0003 | CPH     | DBV     | 09JUL2019 | 10:10 | 12:30 | SK  | 32W    |
    | leg | 0004 | DBV     | OSL     | 09JUL2019 | 13:20 | 15:45 | SK  | 32W    |

    Given trip 1 is assigned to crew member 1 in position AP
    Given trip 1 is assigned to crew member 2 in position AH
    Given trip 1 is assigned to crew member 3 in position AH

    When I show "crew" in window 1
    Then rave "rules_training_ccr.%max_temp_crew_on_flight%" shall be "2" on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_max_temp_crew_on_flight_cc" shall fail on leg 1 on trip 1 on roster 2
    and rave "rules_training_ccr.%nr_temp_crew_on_flight%" shall be "3" on leg 1 on trip 1 on roster 1
    and rave "rules_training_ccr.%nr_temp_crew_on_flight%" shall be "3" on leg 1 on trip 1 on roster 2
    and rave "rules_training_ccr.%nr_temp_crew_on_flight%" shall be "3" on leg 1 on trip 1 on roster 3
    and rave "crew_pos.%is_supernum%" shall be "False" on leg 1 on trip 1 on roster 3
    and rave "leg.%is_x_supernum%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "leg.%is_x_supernum%" shall be "False" on leg 1 on trip 1 on roster 2
    and rave "leg.%is_x_supernum%" shall be "False" on leg 1 on trip 1 on roster 3

  @tracking @SKN_2
  Scenario: Region SKN, max number of temporary crew, one is supernum.

    Given planning period from 1JUL2019 to 31JUL2019

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AP      |             |           |
    | region     | SKN     |             |           |
    Given crew member 1 has contract "V345"

    Given another crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    Given crew member 2 has contract "V345"

    Given another crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    Given crew member 3 has contract "V345"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | ARN     | 09JUL2019 | 06:00 | 07:10 | SK  | 320    |
    | leg | 0002 | ARN     | CPH     | 09JUL2019 | 07:55 | 09:10 | SK  | 320    |
    | leg | 0003 | CPH     | DBV     | 09JUL2019 | 10:10 | 12:30 | SK  | 32W    |
    | leg | 0004 | DBV     | OSL     | 09JUL2019 | 13:20 | 15:45 | SK  | 32W    |

    Given trip 1 is assigned to crew member 1 in position AP
    Given trip 1 is assigned to crew member 2 in position AH
    Given trip 1 is assigned to crew member 3 in position 8 with attribute TRAINING="X SUPERNUM"

    When I show "crew" in window 1
    and I load rule set "Rostering_CC"
    Then rave "rules_training_ccr.%max_temp_crew_on_flight%" shall be "2" on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_max_temp_crew_on_flight_cc" shall pass on leg 1 on trip 1 on roster 2
    and rave "rules_training_ccr.%nr_temp_crew_on_flight%" shall be "2" on leg 1 on trip 1 on roster 1
    and rave "rules_training_ccr.%nr_temp_crew_on_flight%" shall be "2" on leg 1 on trip 1 on roster 2
    and rave "rules_training_ccr.%nr_temp_crew_on_flight%" shall be "2" on leg 1 on trip 1 on roster 3
#    and the constraint "roster_constraints.temp_crew_skn_cc" shall be "0" on leg 1 on trip 1 on roster 1
    and rave "crew_pos.%is_supernum%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "crew_pos.%is_supernum%" shall be "False" on leg 1 on trip 1 on roster 2
    and rave "crew_pos.%is_supernum%" shall be "True" on leg 1 on trip 1 on roster 3

@tracking @SKN_3
  Scenario: Region SKN, all temporary crew are supernum.

    Given planning period from 1JUL2019 to 31JUL2019

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AP      |             |           |
    | region     | SKN     |             |           |
    Given crew member 1 has contract "V200"

    Given another crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    Given crew member 2 has contract "V345"

    Given another crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    Given crew member 3 has contract "V345"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | ARN     | 09JUL2019 | 06:00 | 07:10 | SK  | 320    |
    | leg | 0002 | ARN     | CPH     | 09JUL2019 | 07:55 | 09:10 | SK  | 320    |
    | leg | 0003 | CPH     | DBV     | 09JUL2019 | 10:10 | 12:30 | SK  | 32W    |
    | leg | 0004 | DBV     | OSL     | 09JUL2019 | 13:20 | 15:45 | SK  | 32W    |

    Given trip 1 is assigned to crew member 1 in position AP
    Given trip 1 is assigned to crew member 2 in position 8 with attribute TRAINING="X SUPERNUM"
    Given trip 1 is assigned to crew member 3 in position 8 with attribute TRAINING="X SUPERNUM"

    When I show "crew" in window 1
    Then rave "rules_training_ccr.%max_temp_crew_on_flight%" shall be "2" on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_max_temp_crew_on_flight_cc" shall pass on leg 1 on trip 1 on roster 2
    and rave "rules_training_ccr.%nr_temp_crew_on_flight%" shall be "0" on leg 1 on trip 1 on roster 1
    and rave "rules_training_ccr.%nr_temp_crew_on_flight%" shall be "0" on leg 1 on trip 1 on roster 2
    and rave "rules_training_ccr.%nr_temp_crew_on_flight%" shall be "0" on leg 1 on trip 1 on roster 3
    and rave "crew_pos.%is_supernum%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "crew_pos.%is_supernum%" shall be "True" on leg 1 on trip 1 on roster 2
    and rave "crew_pos.%is_supernum%" shall be "True" on leg 1 on trip 1 on roster 3

@tracking @SKD_1
    Scenario: Region SKD, too many temporary crew, no supernum.

    Given planning period from 1JUL2019 to 31JUL2019

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AP      |             |           |
    | region     | SKD     |             |           |
    Given crew member 1 has contract "V345"

    Given another crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKD     |             |           |
    Given crew member 2 has contract "V345"

    Given another crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKD     |             |           |
    Given crew member 3 has contract "V345"

    Given another crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKD     |             |           |
    Given crew member 4 has contract "V345"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | ARN     | 09JUL2019 | 06:00 | 07:10 | SK  | 320    |
    | leg | 0002 | ARN     | CPH     | 09JUL2019 | 07:55 | 09:10 | SK  | 320    |
    | leg | 0003 | CPH     | DBV     | 09JUL2019 | 10:10 | 12:30 | SK  | 32W    |
    | leg | 0004 | DBV     | OSL     | 09JUL2019 | 13:20 | 15:45 | SK  | 32W    |

    Given trip 1 is assigned to crew member 1 in position AP
    Given trip 1 is assigned to crew member 2 in position AH
    Given trip 1 is assigned to crew member 3 in position AH
    Given trip 1 is assigned to crew member 4 in position AH

    When I show "crew" in window 1
    Then rave "rules_training_ccr.%max_temp_crew_on_flight%" shall be "3" on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_max_temp_crew_on_flight_cc" shall fail on leg 1 on trip 1 on roster 2
    and rave "rules_training_ccr.%nr_temp_crew_on_flight%" shall be "4" on leg 1 on trip 1 on roster 1
    and rave "rules_training_ccr.%nr_temp_crew_on_flight%" shall be "4" on leg 1 on trip 1 on roster 2
    and rave "rules_training_ccr.%nr_temp_crew_on_flight%" shall be "4" on leg 1 on trip 1 on roster 3
    and rave "crew_pos.%is_supernum%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "crew_pos.%is_supernum%" shall be "False" on leg 1 on trip 1 on roster 2
    and rave "crew_pos.%is_supernum%" shall be "False" on leg 1 on trip 1 on roster 3
    and rave "crew_pos.%is_supernum%" shall be "False" on leg 1 on trip 1 on roster 4

@tracking @SKD_2
  Scenario: Region SKD, max number of temporary crew, one is supernum.

    Given planning period from 1JUL2019 to 31JUL2019

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AP      |             |           |
    | region     | SKD     |             |           |
    Given crew member 1 has contract "V345"

    Given another crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKD     |             |           |
    Given crew member 2 has contract "V345"

    Given another crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKD     |             |           |
    Given crew member 3 has contract "V345"

    Given another crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKD     |             |           |
    Given crew member 4 has contract "V345"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | ARN     | 09JUL2019 | 06:00 | 07:10 | SK  | 320    |
    | leg | 0002 | ARN     | CPH     | 09JUL2019 | 07:55 | 09:10 | SK  | 320    |
    | leg | 0003 | CPH     | DBV     | 09JUL2019 | 10:10 | 12:30 | SK  | 32W    |
    | leg | 0004 | DBV     | OSL     | 09JUL2019 | 13:20 | 15:45 | SK  | 32W    |

    Given trip 1 is assigned to crew member 1 in position AP
    Given trip 1 is assigned to crew member 2 in position AH
    Given trip 1 is assigned to crew member 3 in position AH
    Given trip 1 is assigned to crew member 4 in position 8 with attribute TRAINING="X SUPERNUM"

    When I show "crew" in window 1
    Then rave "rules_training_ccr.%max_temp_crew_on_flight%" shall be "3" on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_max_temp_crew_on_flight_cc" shall pass on leg 1 on trip 1 on roster 2
    and rave "rules_training_ccr.%nr_temp_crew_on_flight%" shall be "3" on leg 1 on trip 1 on roster 1
    and rave "rules_training_ccr.%nr_temp_crew_on_flight%" shall be "3" on leg 1 on trip 1 on roster 2
    and rave "rules_training_ccr.%nr_temp_crew_on_flight%" shall be "3" on leg 1 on trip 1 on roster 3
    and rave "crew_pos.%is_supernum%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "crew_pos.%is_supernum%" shall be "False" on leg 1 on trip 1 on roster 2
    and rave "crew_pos.%is_supernum%" shall be "False" on leg 1 on trip 1 on roster 3
    and rave "crew_pos.%is_supernum%" shall be "True" on leg 1 on trip 1 on roster 4
