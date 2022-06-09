@PLANNING @ROSTERING @SKCMS-2690 @TRACKING

Feature: After completion of the ILC flight and prior to vacation or leave of absence, the pilot shall be scheduled.
  Background: set up for tracking
        Given planning period from 01JAN2020 to 31JAN2020
        Given Tracking
        
        Given table crew_training_log additionally contains the following
        |crew         | typ | code | tim       | attr |
        |crew member 1| ILC | A2   | 20DEC2019 |      |

        Given crew member 1 has the following training need
        | part    | attribute  | valid from | valid to   | flights | max days | 
        | 1       | ILC        | 01DEC2019  | 01FEB2020  | 1       | 0        | 
        @SCENARIO1
        Scenario: Sufficient active sectors to receive VA,LOA(for A2 qual)

        Given table agreement_validity is overridden with the following
        | id                             | validfrom | validto   |   
        | no_va_loa_after_ilc_17         | 01FEB2018 | 31Dec2035 | 

        Given a crew member with
        | attribute       | value     | valid from | valid to |
        | base            | OSL       |            |          |
        | title rank      | FC        |            |          |
        Given crew member 1 has qualification "ACQUAL+A2" from 1FEB2018 to 28FEB2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | SFO     | 02JAN2020 | 05:00 | 23:00 | SK  | 320    |
        | leg | 0002 | SFO     | PUS     | 03JAN2020 | 05:00 | 23:00 | SK  | 320    |
        | leg | 0003 | PUS     | OSL     | 04JAN2020 | 05:00 | 23:00 | SK  | 320    |
        | leg | 0004 | OSL     | LHR     | 05JAN2020 | 10:00 | 11:00 | SK  | 320    |
        | leg | 0005 | LHR     | OSL     | 06JAN2020 | 12:00 | 13:00 | SK  | 320    |
        | leg | 0006 | OSL     | LHR     | 07JAN2020 | 10:00 | 11:00 | SK  | 320    |
        | leg | 0007 | LHR     | OSL     | 08JAN2020 | 12:00 | 13:00 | SK  | 320    |
        | leg | 0008 | OSL     | LHR     | 09JAN2020 | 10:00 | 11:00 | SK  | 320    |
        | leg | 0009 | LHR     | OSL     | 10JAN2020 | 12:00 | 13:00 | SK  | 320    |
        | leg | 0010 | OSL     | LHR     | 11JAN2020 | 10:00 | 11:00 | SK  | 320    |
        | leg | 0011 | LHR     | OSL     | 12JAN2020 | 12:00 | 13:00 | SK  | 320    |
        | leg | 0012 | OSL     | LHR     | 13JAN2020 | 12:00 | 13:00 | SK  | 320    |
        | leg | 0013 | LHR     | OSL     | 14JAN2020 | 10:00 | 11:00 | SK  | 320    |
        | leg | 0014 | OSL     | LHR     | 15JAN2020 | 12:00 | 13:00 | SK  | 320    |
        | leg | 0015 | LHR     | OSL     | 16JAN2020 | 12:00 | 13:00 | SK  | 320    |
        | leg | 0016 | OSL     | LHR     | 17JAN2020 | 12:00 | 13:00 | SK  | 320    |
        | leg | 0017 | LHR     | OSL     | 18JAN2020 | 12:00 | 13:00 | SK  | 320    |

        Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 19JAN2020 22:00 and ends at 22JAN2020 22:00

        Given trip 1 is assigned to crew member 1 in position FC

        When I show "crew" in window 1

        then the rule "rules_training_ccr.trng_no_vacation_loa_after_ilc" shall pass on leg 1 on trip 1 on roster 1
     
        @SCENARIO2
        Scenario: Insufficient active sectors to receive VA,LOA(for 38 qual)

        Given table agreement_validity is overridden with the following
        | id                             | validfrom | validto   |   
        | no_va_loa_after_ilc_17         | 01FEB2018 | 31Dec2035 | 

        
        Given a crew member with
        | attribute       | value     | valid from | valid to |
        | base            | OSL       |            |          |
        | title rank      | FC        |            |          |
        Given crew member 1 has qualification "ACQUAL+38" from 1FEB2018 to 28FEB2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | SFO     | 02JAN2020 | 05:00 | 23:00 | SK  | 38    |
        | leg | 0002 | SFO     | PUS     | 03JAN2020 | 05:00 | 23:00 | SK  | 38    |
        | leg | 0003 | PUS     | OSL     | 04JAN2020 | 05:00 | 23:00 | SK  | 38    |
        | leg | 0004 | OSL     | LHR     | 05JAN2020 | 10:00 | 11:00 | SK  | 38    |
        | leg | 0005 | LHR     | OSL     | 06JAN2020 | 12:00 | 13:00 | SK  | 38    |
        | leg | 0006 | OSL     | LHR     | 07JAN2020 | 10:00 | 11:00 | SK  | 38    |
        | leg | 0007 | LHR     | OSL     | 08JAN2020 | 12:00 | 13:00 | SK  | 38    |
        | leg | 0008 | OSL     | SFO     | 09JAN2020 | 05:00 | 23:00 | SK  | 38    |
        | leg | 0009 | SFO     | PUS     | 10JAN2020 | 05:00 | 23:00 | SK  | 38    |
        | leg | 0010 | PUS     | OSL     | 11JAN2020 | 05:00 | 23:00 | SK  | 38    |
        | leg | 0011 | OSL     | LHR     | 12JAN2020 | 10:00 | 11:00 | SK  | 38    |
        | leg | 0012 | LHR     | CPH     | 13JAN2020 | 12:00 | 13:00 | SK  | 38    |
        | leg | 0013 | CPH     | OSL     | 14JAN2020 | 10:00 | 11:00 | SK  | 38    |
        | leg | 0014 | OSL     | LHR     | 15JAN2020 | 12:00 | 13:00 | SK  | 38    |
        | leg | 0015 | LHR     | OSL     | 16JAN2020 | 12:00 | 13:00 | SK  | 38    |

        Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 19JAN2020 22:00 and ends at 22JAN2020 22:00

        Given trip 1 is assigned to crew member 1 in position FC

        When I show "crew" in window 1

        then the rule "rules_training_ccr.trng_no_vacation_loa_after_ilc" shall pass on leg 1 on trip 1 on roster 1
    
        @SCENARIO3
        Scenario: Sufficient active sectors to receive VA,LOA(for A5 qual)

        Given table agreement_validity is overridden with the following
        | id                             | validfrom | validto   |   
        | no_va_loa_after_ilc_17         | 01FEB2018 | 31Dec2035 | 


        Given a crew member with
        | attribute       | value     | valid from | valid to |
        | base            | OSL       |            |          |
        | title rank      | FC        |            |          |
        Given crew member 1 has qualification "ACQUAL+A5" from 1FEB2018 to 28FEB2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | SFO     | 02JAN2020 | 05:00 | 23:00 | SK  | 350    |
        | leg | 0002 | SFO     | PUS     | 03JAN2020 | 05:00 | 23:00 | SK  | 350    |
        | leg | 0003 | PUS     | OSL     | 04JAN2020 | 05:00 | 23:00 | SK  | 350    |
        | leg | 0004 | OSL     | LHR     | 05JAN2020 | 10:00 | 11:00 | SK  | 350    |
        | leg | 0005 | LHR     | OSL     | 06JAN2020 | 12:00 | 13:00 | SK  | 350    |
        | leg | 0006 | OSL     | LHR     | 07JAN2020 | 10:00 | 11:00 | SK  | 350    |
        | leg | 0007 | LHR     | OSL     | 08JAN2020 | 12:00 | 13:00 | SK  | 350    |
        
        Given another trip with the following activities
        | act    | code | dep stn | arr stn | date      | dep   | arr   | 
        | ground | VA   | CPH     | CPH     | 20JAN2020 | 00:00 | 23:59 |  
        | ground | VA   | CPH     | CPH     | 21JAN2020 | 00:00 | 23:59 |  
        | ground | VA   | CPH     | CPH     | 22JAN2020 | 00:00 | 23:59 |  
        | ground | VA   | CPH     | CPH     | 23JAN2020 | 00:00 | 23:59 | 
        
        Given trip 1 is assigned to crew member 1 in position FC
        Given trip 2 is assigned to crew member 1 in position FC

        When I show "crew" in window 1

        then the rule "rules_training_ccr.trng_no_vacation_loa_after_ilc" shall pass on leg 1 on trip 1 on roster 1
     
        @SCENARIO4
        Scenario: sufficient active sectors to receive VA,LOA(for A3 qual)

        Given table agreement_validity is overridden with the following
        | id                             | validfrom | validto   |   
        | no_va_loa_after_ilc_17         | 01FEB2018 | 31Dec2035 | 

        Given a crew member with
        | attribute       | value     | valid from | valid to |
        | base            | OSL       |            |          |
        | title rank      | FC        |            |          |
        Given crew member 1 has qualification "ACQUAL+A3" from 1FEB2018 to 28FEB2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | SFO     | 02JAN2020 | 05:00 | 23:00 | SK  | 330    |
        | leg | 0002 | SFO     | PUS     | 03JAN2020 | 05:00 | 23:00 | SK  | 330    |
        | leg | 0003 | PUS     | OSL     | 04JAN2020 | 05:00 | 23:00 | SK  | 330    |
        | leg | 0004 | OSL     | LHR     | 05JAN2020 | 10:00 | 11:00 | SK  | 330    |
        | leg | 0005 | LHR     | OSL     | 06JAN2020 | 12:00 | 13:00 | SK  | 330    |
        
        Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 9JAN2020 22:00 and ends at 22JAN2020 22:00

        
        Given trip 1 is assigned to crew member 1 in position FC
        

        When I show "crew" in window 1

        then the rule "rules_training_ccr.trng_no_vacation_loa_after_ilc" shall pass on leg 1 on trip 1 on roster 1
     
       @SCENARIO5
        Scenario: Insufficient active sectors to receive VA,LOA(for A3 qual)

        Given table agreement_validity is overridden with the following
        | id                             | validfrom | validto   |   
        | no_va_loa_after_ilc_17         | 01FEB2018 | 31Dec2020 | 

        Given crew member 1 has the following training need
        | part | course           | attribute  | valid from | valid to   | flights | max days | acqual |
        | 1    | CCQ from SH      | ILC        | 01DEC2019  | 30JAN2020  | 1       | 0        | A2     |
 
        Given a crew member with
        | attribute       | value     | valid from | valid to |
        | base            | OSL       |            |          |
        | title rank      | FC        |            |          |
        Given crew member 1 has qualification "ACQUAL+A3" from 1FEB2018 to 28FEB2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | SFO     | 02JAN2020 | 05:00 | 23:00 | SK  | 330    |
        | leg | 0002 | SFO     | PUS     | 03JAN2020 | 05:00 | 23:00 | SK  | 330    |
        
        Given another trip with the following activities
        | act    | code | dep stn | arr stn | date      | dep   | arr   | 
        | ground | VA   | CPH     | CPH     | 20JAN2020 | 00:00 | 23:59 |  
        | ground | VA   | CPH     | CPH     | 21JAN2020 | 00:00 | 23:59 |  
        | ground | VA   | CPH     | CPH     | 22JAN2020 | 00:00 | 23:59 |  
        | ground | VA   | CPH     | CPH     | 23JAN2020 | 00:00 | 23:59 |

        Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 9JAN2020 22:00 and ends at 22JAN2020 22:00

        Given trip 1 is assigned to crew member 1 in position FC
        Given trip 2 is assigned to crew member 1 in position FC
        
        When I show "crew" in window 1
        
        then the rule "rules_training_ccr.trng_no_vacation_loa_after_ilc" shall fail on leg 1 on trip 2 on roster 1
     
       @SCENARIO6
        Scenario: Insufficient active sectors to receive VA,LOA(for A3 qual)

        Given table agreement_validity is overridden with the following
        | id                             | validfrom | validto   |   
        | no_va_loa_after_ilc_17         | 01FEB2018 | 31Dec2020 |

        Given crew member 1 has the following training need
        | part | course           | attribute  | valid from | valid to   | flights | max days | acqual |
        | 1    | CCQ from SH      | ILC        | 01DEC2019  | 30JAN2020  | 1       | 0        | A2     |
 

        Given a crew member with
        | attribute       | value     | valid from | valid to |
        | base            | OSL       |            |          |
        | title rank      | FC        |            |          |
        Given crew member 1 has qualification "ACQUAL+A3" from 1FEB2018 to 28FEB2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | SFO     | 02JAN2020 | 05:00 | 23:00 | SK  | 330    |
        | leg | 0002 | SFO     | OSL     | 03JAN2020 | 05:00 | 23:00 | SK  | 330    |
        
        Given another trip with the following activities
        | act    | code | dep stn | arr stn | date      | dep   | arr   | 
        | ground | VA   | CPH     | CPH     | 20JAN2020 | 00:00 | 23:59 |  
        | ground | VA   | CPH     | CPH     | 21JAN2020 | 00:00 | 23:59 |  
        | ground | VA   | CPH     | CPH     | 22JAN2020 | 00:00 | 23:59 |  
        | ground | VA   | CPH     | CPH     | 23JAN2020 | 00:00 | 23:59 | 

        Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 9JAN2020 22:00 and ends at 22JAN2020 22:00

      
        Given trip 1 is assigned to crew member 1 in position FC
        Given trip 2 is assigned to crew member 1 in position FC
        
        When I show "crew" in window 1
        
        then the rule "rules_training_ccr.trng_no_vacation_loa_after_ilc" shall fail on leg 1 on trip 2 on roster 1
     
       @SCENARIO7
        Scenario: Insufficient active sectors to receive VA,LOA(for 38 qual)

        Given table agreement_validity is overridden with the following
        | id                             | validfrom | validto   |   
        | no_va_loa_after_ilc_17         | 01FEB2018 | 31Dec2020 |

        Given crew member 1 has the following training need
        | part | course           | attribute  | valid from | valid to   | flights | max days | acqual |
        | 1    | CCQ from SH      | ILC        | 01DEC2019  | 30JAN2020  | 1       | 0        | A2     |
 
        Given a crew member with
        | attribute       | value     | valid from | valid to |
        | base            | OSL       |            |          |
        | title rank      | FC        |            |          |
        Given crew member 1 has qualification "ACQUAL+38" from 1FEB2018 to 28FEB2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | SFO     | 02JAN2020 | 05:00 | 23:00 | SK  | 380    |
        | leg | 0002 | SFO     | OSL     | 03JAN2020 | 05:00 | 23:00 | SK  | 380    |
        
        Given another trip with the following activities
        | act    | code | dep stn | arr stn | date      | dep   | arr   | 
        | ground | VA   | CPH     | CPH     | 20JAN2020 | 00:00 | 23:59 |  
        | ground | VA   | CPH     | CPH     | 21JAN2020 | 00:00 | 23:59 |  
        | ground | VA   | CPH     | CPH     | 22JAN2020 | 00:00 | 23:59 |  
        | ground | VA   | CPH     | CPH     | 23JAN2020 | 00:00 | 23:59 | 

        Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 9JAN2020 22:00 and ends at 22JAN2020 22:00
        Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="ILC"
        Given trip 2 is assigned to crew member 1 in position FC
        
        When I show "crew" in window 1
        
        then the rule "rules_training_ccr.trng_no_vacation_loa_after_ilc" shall fail on leg 1 on trip 2 on roster 1
     
       @SCENARIO8
        Scenario: Insufficient active sectors to receive VA,LOA(for A2 qual)

        Given table agreement_validity is overridden with the following
        | id                             | validfrom | validto   |   
        | no_va_loa_after_ilc_17         | 01FEB2018 | 31Dec2020 | 

        Given crew member 1 has the following training need
        | part | course           | attribute  | valid from | valid to   | flights | max days | acqual |
        | 1    | CCQ from SH      | ILC        | 01DEC2019  | 30JAN2020  | 1       | 0        | A2     |


        Given a crew member with
        | attribute       | value     | valid from | valid to |
        | base            | OSL       |            |          |
        | title rank      | FC        |            |          |
        Given crew member 1 has qualification "ACQUAL+A2" from 1FEB2018 to 28FEB2035

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | SFO     | 02JAN2020 | 05:00 | 23:00 | SK  | 320    |
        | leg | 0002 | SFO     | OSL     | 03JAN2020 | 05:00 | 23:00 | SK  | 320    |
        
        Given another trip with the following activities
        | act    | code | dep stn | arr stn | date      | dep   | arr   | 
        | ground | VA   | CPH     | CPH     | 20JAN2020 | 00:00 | 23:59 |  
        | ground | VA   | CPH     | CPH     | 21JAN2020 | 00:00 | 23:59 |  
        | ground | VA   | CPH     | CPH     | 22JAN2020 | 00:00 | 23:59 |  
        | ground | VA   | CPH     | CPH     | 23JAN2020 | 00:00 | 23:59 | 

        Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 9JAN2020 22:00 and ends at 22JAN2020 22:00

      
        Given trip 1 is assigned to crew member 1 in position FC
        Given trip 2 is assigned to crew member 1 in position FC
        
        When I show "crew" in window 1
        
        then the rule "rules_training_ccr.trng_no_vacation_loa_after_ilc" shall fail on leg 1 on trip 2 on roster 1
     
       