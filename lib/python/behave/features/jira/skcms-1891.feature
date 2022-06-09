Feature: Test that number of temp CC crew for SKD is according to limits - Tracking & Planning Studio

  Background: Tests will be performed in both Tracking and Planning Studio as the behavior is expected to be different.

###################################################################################
    @tracking
    Scenario: Check rule does warn if there is no AP and 3 temp crew on flight.
    Given Tracking
    Given planning period from 1feb2018 to 28feb2018

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 2 has contract "V345"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 3 has contract "V345"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 4 has contract "V345"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | LHR     | 03FEB2018 | 10:00 | 11:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 2 in position AH
    Given trip 1 is assigned to crew member 3 in position AH
    Given trip 1 is assigned to crew member 4 in position AH

    When I show "crew" in window 1
    Then rave "rules_training_ccr.%max_temp_crew_on_flight%" shall be "2" on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_max_temp_crew_on_flight_cc" shall fail on leg 1 on trip 1 on roster 2

###################################################################################
    @tracking
    Scenario: Check rule does not warn if there is AP and 3 temp crew on flight.
    Given Tracking
    Given planning period from 1sep2018 to 30sep2018

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 2 has contract "V345"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 3 has contract "V345"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 4 has contract "V345"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | LHR     | 03SEP2018 | 10:00 | 11:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AP
    Given trip 1 is assigned to crew member 2 in position AH
    Given trip 1 is assigned to crew member 3 in position AH
    Given trip 1 is assigned to crew member 4 in position AH

    When I show "crew" in window 1
    When I set parameter "fundamental.%use_now_debug%" to "TRUE"
    When I set parameter "fundamental.%now_debug%" to "1SEP2018 00:00"
    Then rave "rules_training_ccr.%max_temp_crew_on_flight%" shall be "3" on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_max_temp_crew_on_flight_cc" shall pass on leg 1 on trip 1 on roster 2

###################################################################################
    @tracking
    Scenario: Check rule does warn if there is AP and 3 temp crew on flight but date is pre 1st Sep.
    Given Tracking
    Given planning period from 1sep2018 to 30sep2018

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 2 has contract "V345"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 3 has contract "V345"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 4 has contract "V345"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | LHR     | 03SEP2018 | 10:00 | 11:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AP
    Given trip 1 is assigned to crew member 2 in position AH
    Given trip 1 is assigned to crew member 3 in position AH
    Given trip 1 is assigned to crew member 4 in position AH

    When I show "crew" in window 1
    When I set parameter "fundamental.%use_now_debug%" to "TRUE"
    When I set parameter "fundamental.%now_debug%" to "31AUG2018 00:00"
    Then rave "rules_training_ccr.%max_temp_crew_on_flight%" shall be "2" on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_max_temp_crew_on_flight_cc" shall fail on leg 1 on trip 1 on roster 2

###################################################################################
    @tracking
    Scenario: Check rule does warn if there is AP and 3 temp crew on flight but not all are SKD.
    Given Tracking
    Given planning period from 1sep2018 to 30sep2018

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKS       |            |          |
    Given crew member 2 has contract "F00863"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 3 has contract "V345"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 4 has contract "V345"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | LHR     | 03SEP2018 | 10:00 | 11:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AP
    Given trip 1 is assigned to crew member 2 in position AH
    Given trip 1 is assigned to crew member 3 in position AH
    Given trip 1 is assigned to crew member 4 in position AH

    When I show "crew" in window 1
    When I set parameter "fundamental.%use_now_debug%" to "TRUE"
    When I set parameter "fundamental.%now_debug%" to "1SEP2018 00:00"
    Then rave "rules_training_ccr.%max_temp_crew_on_flight%" shall be "2" on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_max_temp_crew_on_flight_cc" shall fail on leg 1 on trip 1 on roster 2
    and rave "rules_training_ccr.%max_temp_crew_on_flight%" shall be "2" on leg 1 on trip 1 on roster 3
    and the rule "rules_training_ccr.comp_max_temp_crew_on_flight_cc" shall fail on leg 1 on trip 1 on roster 3

###################################################################################
    @tracking
    Scenario: Check rule does not warn if there is AP (SKS) and 3 temp crew on flight.
    Given Tracking
    Given planning period from 1sep2018 to 30sep2018

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKS       |            |          |
    Given crew member 1 has contract "F340"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 2 has contract "V345"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 3 has contract "V345"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 4 has contract "V345"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | LHR     | 03SEP2018 | 10:00 | 11:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AP
    Given trip 1 is assigned to crew member 2 in position AH
    Given trip 1 is assigned to crew member 3 in position AH
    Given trip 1 is assigned to crew member 4 in position AH

    When I show "crew" in window 1
    When I set parameter "fundamental.%use_now_debug%" to "TRUE"
    When I set parameter "fundamental.%now_debug%" to "1SEP2018 00:00"
    Then rave "rules_training_ccr.%max_temp_crew_on_flight%" shall be "3" on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_max_temp_crew_on_flight_cc" shall pass on leg 1 on trip 1 on roster 2

    ###################################################################################
    @tracking
    Scenario: Check rule does warn if there is AP (SKJ) and 3 temp crew on flight.
    Given Tracking
    Given planning period from 1sep2018 to 30sep2018

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKJ       |            |          |
    Given crew member 1 has contract "F340"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 2 has contract "V345"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 3 has contract "V345"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 4 has contract "V345"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | LHR     | 03SEP2018 | 10:00 | 11:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AP
    Given trip 1 is assigned to crew member 2 in position AH
    Given trip 1 is assigned to crew member 3 in position AH
    Given trip 1 is assigned to crew member 4 in position AH

    When I show "crew" in window 1
    When I set parameter "fundamental.%use_now_debug%" to "TRUE"
    When I set parameter "fundamental.%now_debug%" to "1SEP2018 00:00"
    Then rave "rules_training_ccr.%max_temp_crew_on_flight%" shall be "2" on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_max_temp_crew_on_flight_cc" shall fail on leg 1 on trip 1 on roster 2

###################################################################################
    @planning
    Scenario: Check rule does not warn if there is AP and 2 temp crew on flight.
    Given planning period from 01FEB2018 to 28FEB2018


    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 2 has contract "V345"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 3 has contract "V345"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 4 has contract "V345"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | LHR     | 03FEB2018 | 10:00 | 11:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AP
    Given trip 1 is assigned to crew member 2 in position AH
    Given trip 1 is assigned to crew member 3 in position AH

    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1FEB2018 00:00"
    When I set parameter "fundamental.%end_para%" to "28FEB2018 00:00"
    Then rave "rules_training_ccr.%max_temp_crew_on_flight%" shall be "2" on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_max_temp_crew_on_flight_cc" shall pass on leg 1 on trip 1 on roster 2

###################################################################################
    @planning
    Scenario: Check rule does not warn if there is no AP and 2 temp crew on flight.
    Given planning period from 01FEB2018 to 28FEB2018

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 2 has contract "V345"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 3 has contract "V345"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 4 has contract "V345"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | LHR     | 03FEB2018 | 10:00 | 11:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 2 in position AH
    Given trip 1 is assigned to crew member 3 in position AH

    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1FEB2018 00:00"
    When I set parameter "fundamental.%end_para%" to "28FEB2018 00:00"
    Then rave "rules_training_ccr.%max_temp_crew_on_flight%" shall be "2" on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_max_temp_crew_on_flight_cc" shall pass on leg 1 on trip 1 on roster 2

###################################################################################
    @planning
    Scenario: Check rule does warn if there is AP and 3 temp crew on flight in JCP
    Given planning period from 01FEB2018 to 28FEB2018

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 2 has contract "V345"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 3 has contract "V345"

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 4 has contract "V345"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | LHR     | 03FEB2018 | 10:00 | 11:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AP
    Given trip 1 is assigned to crew member 2 in position AH
    Given trip 1 is assigned to crew member 3 in position AH
    Given trip 1 is assigned to crew member 4 in position AH

    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1FEB2018 00:00"
    When I set parameter "fundamental.%end_para%" to "28FEB2018 00:00"
    Then rave "rules_training_ccr.%max_temp_crew_on_flight%" shall be "2" on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_max_temp_crew_on_flight_cc" shall fail on leg 1 on trip 1 on roster 2