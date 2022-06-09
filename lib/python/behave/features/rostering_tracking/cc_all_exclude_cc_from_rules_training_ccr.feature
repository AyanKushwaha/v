@JCRT @ROSTERING @TRACKING @PLANNING

Feature: rules_training_ccr.comp_release_instructor_is_qualified should not be validated for cc

#####################
# JIRA - SKCMS-1857
#####################

    Background: set up
    Given Tracking


    @SCENARIO1
    Scenario: rule should not be validated for CC and pass?
    Given planning period from 1OCT2020 to 31OCT2020

    Given a crew member with
        | attribute       | value     | valid from | valid to |
        | crew rank       | AH        |            |          |
        | base            | CPH       |            |          |
        | region          | SKD       |            |          |

    Given a crew member with
        | attribute       | value     | valid from | valid to |
        | crew rank       | FC        |            |          |
        | base            | CPH       |            |          |
        | region          | SKD       |            |          |

    Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | CPH     | SMI     | 1OCT2020  | 08:00 | 10:00 | SK  | 320    |
        | leg | 0002 | SMI     | CPH     | 2OCT2020  | 10:00 | 12:00 | SK  | 320    |
     Given trip 1 is assigned to crew member 1 in position AH


     When I show "crew" in window 1

     Then the rule "rules_training_ccr.comp_release_instructor_is_qualified" shall pass on leg 1 on trip 1 on roster 2




    @SCENARIO2
    Scenario: rule should be validated for FD and pass
    Given planning period from 1OCT2020 to 31OCT2020

    Given a crew member with
        | attribute       | value     | valid from | valid to |
        | crew rank       | FP        |            |          |
        | base            | CPH       |            |          |
        | region          | SKD       |            |          |

    Given a crew member with
        | attribute       | value     | valid from | valid to |
        | crew rank       | FC        |            |          |
        | base            | CPH       |            |          |
        | region          | SKD       |            |          |

    Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | CPH     | SMI     | 3OCT2020  | 08:00 | 10:00 | SK  | 320    |
        | leg | 0002 | SMI     | CPH     | 4OCT2020  | 10:00 | 12:00 | SK  | 320    |
     Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="RELEASE"
     Given trip 1 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="RELEASE"
     Given crew member 2 has qualification "ACQUAL+A2" from 1Jan2018 to 31DEC2035
     Given crew member 2 has qualification "POSITION+LCP" from 1Jan2018 to 31DEC2035
     Given crew member 2 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 1JAN2018 to 31DEC2035


     When I show "crew" in window 1

     Then the rule "rules_training_ccr.comp_release_instructor_is_qualified" shall pass on leg 1 on trip 1 on roster 1
     Then rave "crew.%is_lifus_matching_instr%(false, leg.%start_utc%)" shall be "True" on leg 1 on trip 1 on roster 2




    @SCENARIO3
    Scenario: rule should not be validated for cc
    Given planning period from 1OCT2020 to 31OCT2020

    Given a crew member with
        | attribute       | value     | valid from | valid to |
        | crew rank       | FP        |            |          |
        | base            | CPH       |            |          |
        | region          | SKD       |            |          |

    Given a crew member with
        | attribute       | value     | valid from | valid to |
        | crew rank       | FC        |            |          |
        | base            | CPH       |            |          |
        | region          | SKD       |            |          |

    Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | CPH     | SMI     | 5OCT2020  | 08:00 | 10:00 | SK  | 320    |
        | leg | 0002 | SMI     | CPH     | 6OCT2020  | 10:00 | 12:00 | SK  | 320    |
     Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="RELEASE"
     Given trip 1 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="RELEASE"


     When I show "crew" in window 1

     Then the rule "rules_training_ccr.comp_release_instructor_is_qualified" shall pass on leg 1 on trip 1 on roster 1
     Then rave "crew.%is_lifus_matching_instr%(false, leg.%start_utc%)" shall be "False" on leg 1 on trip 1 on roster 2
