 @JCRT @ROSTERING @TRACKING @PLANNING

Feature: rules_training_ccr.comp_max_nr_crew_performing_training_type_on_flight_ALL validated CC with duty designator U, UX or R. (SUPERNUM/ X SUPERNUM/ RELEASE)

#####################
# JIRA - SKCMS-2721
#####################

    Background: set up
    Given Tracking
   
 @SCENARIO1
    Scenario: Rule should Fail for two CC with duty designator RELEASE  and 1 NEW.
    Given planning period from 1OCT2020 to 31OCT2020

    Given table ac_qual_map additionally contains the following
      | ac_type | aoc | ac_qual_fc | ac_qual_cc |
      | 35X     | SK  | AL         | AL         |

    Given table agreement_validity additionally contains the following
      | id                                  | validfrom | validto   | si |
      |dispensation_al_cc_new_release       | 01FEB2020 | 31DEC2035 |Increase number of allowed CC on ac qual AL Release/ New flights|

   Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    Given crew member 1 has contract "V301"
    Given crew member 1 has qualification "ACQUAL+AL" from 13APR2011 to 31DEC2035

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKD     |             |           |
    Given crew member 2 has contract "V301"
    Given crew member 2 has qualification "ACQUAL+AL" from 13APR2011 to 31DEC2035
    Given crew member 1 has acqual restriction "ACQUAL+AL+NEW+ACTYPE" from 1FEB2020 to 28DEC2020

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | ARN     | 09OCT2020 | 06:00 | 07:10 | SK  | 35X    |
    | leg | 0002 | ARN     | OSL     | 09OCT2020 | 13:20 | 15:45 | SK  | 35X    |
   
    Given trip 1 is assigned to crew member 1 in position AH with attribute TRAINING="RELEASE"
    Given trip 1 is assigned to crew member 2 in position AH with attribute TRAINING="RELEASE"
    
    When I show "crew" in window 1
   
    Then the rule "rules_training_ccr.comp_max_nr_crew_performing_training_type_on_flight_ALL" shall fail on leg 1 on trip 1 on roster 1
    and rave "rules_training_ccr.%limit_comp_max_nr_crew_performing_training_type_on_flight_ALL%" shall be "1" on leg 1 on trip 1 on roster 1

@SCENARIO2
 Scenario: Rule should PASS for two CC with duty designator RELEASE  and O New.
    Given planning period from 1OCT2020 to 31OCT2020

    Given table ac_qual_map additionally contains the following
      | ac_type | aoc | ac_qual_fc | ac_qual_cc |
      | 35X     | SK  | AL         | AL         |

    Given table agreement_validity additionally contains the following
      | id                                  | validfrom | validto   | si |
      |dispensation_al_cc_new_release       | 01FEB2020 | 31DEC2035 |Increase number of allowed CC on ac qual AL Release/ New flights|

   Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    Given crew member 1 has contract "V301"
    Given crew member 1 has qualification "ACQUAL+AL" from 13APR2011 to 31DEC2035

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKD     |             |           |
    Given crew member 2 has contract "V301"
    Given crew member 2 has qualification "ACQUAL+AL" from 13APR2011 to 31DEC2035
    

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | ARN     | 09OCT2020 | 06:00 | 07:10 | SK  | 35X    |
    | leg | 0002 | ARN     | OSL     | 09OCT2020 | 13:20 | 15:45 | SK  | 35X    |
   
    Given trip 1 is assigned to crew member 1 in position AH with attribute TRAINING="RELEASE"
    Given trip 1 is assigned to crew member 2 in position AH with attribute TRAINING="RELEASE"
    
    When I show "crew" in window 1
   
    Then the rule "rules_training_ccr.comp_max_nr_crew_performing_training_type_on_flight_ALL" shall pass on leg 1 on trip 1 on roster 1
    and rave "rules_training_ccr.%limit_comp_max_nr_crew_performing_training_type_on_flight_ALL%" shall be "2" on leg 1 on trip 1 on roster 1

@SCENARIO3
    Scenario: Rule should pass for one CC with duty designator RELEASE.
    Given planning period from 1OCT2020 to 31OCT2020

    Given table ac_qual_map additionally contains the following
      | ac_type | aoc | ac_qual_fc | ac_qual_cc |
      | 35X     | SK  | AL         | AL         |

    Given table agreement_validity additionally contains the following
      | id                                  | validfrom | validto   | si |
      |dispensation_al_cc_new_release       | 01FEB2020 | 31DEC2035 |Increase number of allowed CC on ac qual AL Release/ New flights|

   Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    Given crew member 1 has contract "V301"
    Given crew member 1 has qualification "ACQUAL+AL" from 13APR2011 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | ARN     | 09OCT2020 | 06:00 | 07:10 | SK  | 35X    |
    | leg | 0002 | ARN     | OSL     | 09OCT2020 | 13:20 | 15:45 | SK  | 35X    |
   
    Given trip 1 is assigned to crew member 1 in position AH with attribute TRAINING="RELEASE"
   
    When I show "crew" in window 1
   
    Then the rule "rules_training_ccr.comp_max_nr_crew_performing_training_type_on_flight_ALL" shall pass on leg 1 on trip 1 on roster 1
    and rave "rules_training_ccr.%limit_comp_max_nr_crew_performing_training_type_on_flight_ALL%" shall be "2" on leg 1 on trip 1 on roster 1

  @SCENARIO4
    Scenario: Rule should fail for more than two CC with duty designator RELEASE .
    Given planning period from 1OCT2020 to 31OCT2020
    
    Given table ac_qual_map additionally contains the following
      | ac_type | aoc | ac_qual_fc | ac_qual_cc |
      | 35X     | SK  | AL         | AL         |

    Given table agreement_validity additionally contains the following
      | id                                  | validfrom | validto   | si |
      |dispensation_al_cc_new_release       | 01FEB2020 | 31DEC2035 |Increase number of allowed CC on ac qual AL Release/ New flights|

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    Given crew member 1 has contract "V301"
    Given crew member 1 has qualification "ACQUAL+AL" from 13APR2011 to 31DEC2035
    
    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    Given crew member 2 has contract "V301"
    Given crew member 2 has qualification "ACQUAL+AL" from 13APR2011 to 31DEC2035
    
    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    Given crew member 3 has contract "V301"
    Given crew member 3 has qualification "ACQUAL+AL" from 13APR2011 to 31DEC2035
    
    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    Given crew member 4 has contract "V301"
    Given crew member 4 has qualification "ACQUAL+AL" from 13APR2011 to 31DEC2035
    Given crew member 4 has acqual restriction "ACQUAL+AL+NEW+ACTYPE" from 1FEB2020 to 28DEC2020
    
    Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | CPH     | SMI     | 1OCT2020  | 08:00 | 10:00 | SK  | 35X    |
        | leg | 0002 | SMI     | CPH     | 2OCT2020  | 10:00 | 12:00 | SK  | 35X    |
    Given trip 1 is assigned to crew member 1 in position AH with attribute TRAINING="RELEASE"
    Given trip 1 is assigned to crew member 2 in position AH with attribute TRAINING="RELEASE"
    Given trip 1 is assigned to crew member 3 in position AH with attribute TRAINING="RELEASE"
    Given trip 1 is assigned to crew member 4 in position AH 

    When I show "crew" in window 1

    Then the rule "rules_training_ccr.comp_max_nr_crew_performing_training_type_on_flight_ALL" shall fail on leg 1 on trip 1 on roster 1
  
  @SCENARIO5
    Scenario: Rule should pass for one CC with duty designator X SUPERNUM . 
     Given planning period from 1OCT2020 to 31OCT2020
     
     Given table ac_qual_map additionally contains the following
      | ac_type | aoc | ac_qual_fc | ac_qual_cc |
      | 35X     | SK  | AL         | AL         |

    Given a crew member with
        | attribute       | value     | valid from | valid to |
        | crew rank       | AH        |            |          |
        | base            | CPH       |            |          |
        | region          | SKD       |            |          |

    Given a crew member with
        | attribute       | value     | valid from | valid to |
        | crew rank       | AH        |            |          |
        | base            | CPH       |            |          |
        | region          | SKD       |            |          |
    Given crew member 1 has acqual restriction "ACQUAL+A2+NEW+ACTYPE" from 1JAN2020 to 28DEC2020

    Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | CPH     | SMI     | 1OCT2020  | 08:00 | 10:00 | SK  | 35X    |
        | leg | 0002 | SMI     | CPH     | 2OCT2020  | 10:00 | 12:00 | SK  | 35X    |
    Given trip 1 is assigned to crew member 1 in position AH with attribute TRAINING="X SUPERNUM"
    Given trip 1 is assigned to crew member 2 in position AH
 
    When I show "crew" in window 1
    
    Then the rule "rules_training_ccr.comp_max_nr_crew_performing_training_type_on_flight_ALL" shall pass on leg 1 on trip 1 on roster 1


  
@SCENARIO6
    Scenario: Rule should pass for more than one CC with duty designator SUPERNUM .
     Given planning period from 1OCT2020 to 31OCT2020
  

     Given table ac_qual_map additionally contains the following
      | ac_type | aoc | ac_qual_fc | ac_qual_cc |
      | 35X     | SK  | AL         | AL         |

    Given a crew member with
        | attribute       | value     | valid from | valid to |
        | crew rank       | AL        |            |          |
        | base            | CPH       |            |          |
        | region          | SKD       |            |          |
    Given crew member 1 has qualification "ACQUAL+AL" from 13APR2011 to 31DEC2035
    
    Given a crew member with
        | attribute       | value     | valid from | valid to |
        | crew rank       | AL        |            |          |
        | base            | CPH       |            |          |
        | region          | SKD       |            |          |
    Given crew member 2 has qualification "ACQUAL+AL" from 13APR2011 to 31DEC2035
    Given crew member 2 has acqual restriction "ACQUAL+A2+NEW+ACTYPE" from 1FEB2020 to 28DEC2020
    
    Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | CPH     | SMI     | 1OCT2020  | 08:00 | 10:00 | SK  | 35X    |
        | leg | 0002 | SMI     | CPH     | 2OCT2020  | 10:00 | 12:00 | SK  | 35X    |
    Given trip 1 is assigned to crew member 1 in position AH with attribute TRAINING="SUPERNUM"
    Given trip 1 is assigned to crew member 2 in position AH 
    
    When I show "crew" in window 1
   
    Then the rule "rules_training_ccr.comp_max_nr_crew_performing_training_type_on_flight_ALL" shall pass on leg 1 on trip 1 on roster 1
  
  @SCENARIO7
    Scenario: Rule value comp_max_restricted_new_ALL should pass for no RELEASE AND SUPERNUM(without dispensation).
     Given planning period from 1OCT2020 to 31OCT2020

      Given table ac_qual_map additionally contains the following
      | ac_type | aoc | ac_qual_fc | ac_qual_cc |
      | 35X     | SK  | AL         | AL         |

    Given a crew member with
        | attribute       | value     | valid from | valid to |
        | crew rank       | AL        |            |          |
        | base            | CPH       |            |          |
        | region          | SKD       |            |          |
    Given crew member 1 has qualification "ACQUAL+AL" from 13APR2011 to 31DEC2035
    Given crew member 1 has acqual restriction "ACQUAL+AL+NEW+ACTYPE" from 1FEB2020 to 28DEC2020
    
    Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car |ac_typ |
        | leg | 0001 | CPH     | SMI     | 1OCT2020  | 08:00 | 10:00 | SK  | 35X    |  
        | leg | 0002 | SMI     | CPH     | 2OCT2020  | 10:00 | 12:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position AH 

    
    When I show "crew" in window 1
   
    Then the rule "rules_training_ccr.comp_max_restricted_new_ALL" shall pass on leg 1 on trip 1 on roster 1
    
@SCENARIO8
    Scenario: Rule value_comp_max_restricted_new_ALL should pass for no RELEASE AND no SUPERNUM.(with dispensation)
     Given planning period from 1OCT2020 to 31OCT2020

      Given table ac_qual_map additionally contains the following
      | ac_type | aoc | ac_qual_fc | ac_qual_cc |
      | 35X     | SK  | AL         | AL         |

    Given table agreement_validity additionally contains the following
      | id                                  | validfrom | validto   | si |
      |dispensation_al_cc_new_release       | 01FEB2020 | 31DEC2035 |Increase number of allowed CC on ac qual AL Release/ New flights|

    Given a crew member with
        | attribute       | value     | valid from | valid to |
        | crew rank       | AL        |            |          |
        | base            | CPH       |            |          |
        | region          | SKD       |            |          |
    Given crew member 1 has qualification "ACQUAL+AL" from 13APR2011 to 31DEC2035
    Given crew member 1 has acqual restriction "ACQUAL+AL+NEW+ACTYPE" from 1FEB2020 to 28DEC2020
    
    Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car |ac_typ |
        | leg | 0001 | CPH     | SMI     | 1OCT2020  | 08:00 | 10:00 | SK  | 35X    |  
        | leg | 0002 | SMI     | CPH     | 2OCT2020  | 10:00 | 12:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position AH 

    When I show "crew" in window 1
   
    Then the rule "rules_training_ccr.comp_max_restricted_new_ALL" shall pass on leg 1 on trip 1 on roster 1

@SCENARIO9
    Scenario: Rule comp max restricted new ALL should pass for one RELEASE AND No SUPERNUM CC(with dispensation)
     Given planning period from 1OCT2020 to 31OCT2020

      Given table ac_qual_map additionally contains the following
      | ac_type | aoc | ac_qual_fc | ac_qual_cc |
      | 35X     | SK  | AL         | AL         |

    Given table agreement_validity additionally contains the following
      | id                                  | validfrom | validto   | si |
      |dispensation_al_cc_new_release       | 01FEB2020 | 31DEC2035 |Increase number of allowed CC on ac qual AL Release/ New flights|

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    Given crew member 1 has contract "V301"
    Given crew member 1 has qualification "ACQUAL+AL" from 13APR2011 to 31DEC2035
    Given crew member 1 has acqual restriction "ACQUAL+AL+NEW+ACTYPE" from 1FEB2020 to 28DEC2020
    
    Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car |ac_typ |
        | leg | 0001 | CPH     | SMI     | 1OCT2020  | 08:00 | 10:00 | SK  | 35X    |  
        | leg | 0002 | SMI     | CPH     | 2OCT2020  | 10:00 | 12:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position AH with attribute TRAINING="RELEASE"

    When I show "crew" in window 1
   
    Then rave "rules_training_ccr.%limit_comp_max_restricted_new_ALL%" shall be "3" on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_ALL" shall pass on leg 1 on trip 1 on roster 1

@SCENARIO10
    Scenario: Rule comp max restricted new ALL should fail for two RELEASE AND No SUPERNUM CC and 1 NEW(with dispensation)
     Given planning period from 1OCT2020 to 31OCT2020

      Given table ac_qual_map additionally contains the following
      | ac_type | aoc | ac_qual_fc | ac_qual_cc |
      | 35X     | SK  | AL         | AL         |

    Given table agreement_validity additionally contains the following
      | id                                  | validfrom | validto   | si |
      |dispensation_al_cc_new_release       | 01FEB2020 | 31DEC2035 |Increase number of allowed CC on ac qual AL Release/ New flights|

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    Given crew member 1 has contract "V301"
    Given crew member 1 has qualification "ACQUAL+AL" from 13APR2011 to 31DEC2035
    Given crew member 1 has acqual restriction "ACQUAL+AL+NEW+ACTYPE" from 1FEB2020 to 28DEC2020
    
     Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    Given crew member 1 has contract "V301"
    Given crew member 1 has qualification "ACQUAL+AL" from 13APR2011 to 31DEC2035

    Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car |ac_typ |
        | leg | 0001 | CPH     | SMI     | 1OCT2020  | 08:00 | 10:00 | SK  | 35X    |  
        | leg | 0002 | SMI     | CPH     | 2OCT2020  | 10:00 | 12:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position AH with attribute TRAINING="RELEASE"
    Given trip 1 is assigned to crew member 2 in position AH with attribute TRAINING="RELEASE"
    When I show "crew" in window 1
   
    Then rave "rules_training_ccr.%limit_comp_max_restricted_new_ALL%" shall be "0" on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_ALL" shall fail on leg 1 on trip 1 on roster 1

