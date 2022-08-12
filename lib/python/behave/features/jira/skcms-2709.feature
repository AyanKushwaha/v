@TRACKING 

Feature: Add legality for extra course day on CC recurrent REC.
 Background:
  Given Tracking
    
  @SCENARIO1
  Scenario:rule qln_rec_in_correct_order_CC should pass (web_training-cx6-cx7)
    
    Given planning period from 1SEP2021 to 30NOV2021

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AP         | 1SEP2019   | 01JAN2036 |
           | region          | SKN        | 1APR2019   | 01JAN2036 |
           | base            | OSL        | 1APR2019   | 01JAN2036 |
           | title rank      | AP         | 1APR2019   | 01JAN2036 |
           | main function   | C          | 1SEP2021   | 01JAN2036 |
      
    
    Given table agreement_validity additionally contains the following
        | id                             | validfrom | validto   |   
        | additional_CX6_rec_trng        | 01MAR2018 | 31Dec2035 |

    Given table crew_document additionally contains the following
      | crew          | doc_typ | doc_subtype | validfrom | validto   | docno | maindocno | issuer | si | ac_qual |
      | crew member 1 | REC     | REC         | 01Jan2020 | 31Dec2022 | ""    | ""        | ""     | "" | ""      |
      | crew member 1 | REC     | N3         | 01OCT2021 | 30OCT2022| ""    |""         | " "    | " "| ""      |
    
    Given table cabin_recurrent additionally contains the following
      | base         | acquals   |validfrom  | validto   | reccode | 
      | OSL          | A238      | 01Jan2020 | 31Dec2035 | 20     | 
     
              
    Given crew member 1 has qualification "ACQUAL+A2" from 15APR2019 to 01JAN2036
    Given crew member 1 has qualification "ACQUAL+38" from 23JUL2019 to 01JAN2036
    
   
    Given a trip with the following activities
      | act    | num | code | dep stn | arr stn | dep             | arr             | ac_typ |
      | ground |     | N3   | OSL     | OSL     | 25OCT2021 11:00 | 25OCT2021 14:00  | A238   |
      | ground |     | CX6  | OSL     | OSL     | 26OCT2021 11:00 | 26OCT2021 14:00  |        |
      | ground |     | CX7  | OSL     | OSL     | 27OCT2021 06:15 | 27OCT2021 14:00 |        |
      
    Given trip 1 is assigned to crew member 1 in position AP
    
    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.qln_rec_in_correct_order_CC" shall pass on leg 3 on trip 1 on roster 1

@SCENARIO2
Scenario:rule qln_rec_in_correct_order_CC should fail (cx6-web_training-cx7)
    
    Given planning period from 1SEP2021 to 30NOV2021

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AP         | 1SEP2019   | 01JAN2036 |
           | region          | SKN        | 1APR2019   | 01JAN2036 |
           | base            | OSL        | 1APR2019   | 01JAN2036 |
           | title rank      | AP         | 1APR2019   | 01JAN2036 |
           | main function   | C          | 1SEP2021   | 01JAN2036 |
      
    
    Given table agreement_validity additionally contains the following
        | id                             | validfrom | validto   |   
        | additional_CX6_rec_trng        | 01MAR2018 | 31Dec2035 |

    Given table crew_document additionally contains the following
      | crew          | doc_typ | doc_subtype | validfrom | validto   | docno | maindocno | issuer | si | ac_qual |
      | crew member 1 | REC     | REC         | 01Jan1986 | 31Dec2022 | ""    | ""        | ""     | "" | ""      |
      
    Given table cabin_recurrent additionally contains the following
      | base         | acquals   |validfrom  | validto   | reccode | 
      | OSL          | A238      | 01Jan2020 | 31Dec2035 | 20     | 
     
              
    Given crew member 1 has qualification "ACQUAL+A2" from 15APR2019 to 01JAN2036
    Given crew member 1 has qualification "ACQUAL+38" from 23JUL2019 to 01JAN2036
    
   
    Given a trip with the following activities
      | act    | num | code | dep stn | arr stn | dep             | arr             | ac_typ |
      | ground |     | CX7  | OSL     | OSL     | 27OCT2021 06:15 | 27OCT2021 14:00 |        |
      
    Given trip 1 is assigned to crew member 1 in position AP
    
    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.qln_rec_in_correct_order_CC" shall fail on leg 1 on trip 1 on roster 1
  
  @SCENARIO3
  Scenario:rule qln_rec_in_correct_order_CC should pass (web_training-cx7)
    
    Given planning period from 1SEP2021 to 30NOV2021

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AP         | 1SEP2019   | 01JAN2036 |
           | region          | SKN        | 1APR2019   | 01JAN2036 |
           | base            | OSL        | 1APR2019   | 01JAN2036 |
           | title rank      | AP         | 1APR2019   | 01JAN2036 |
           | main function   | C          | 1SEP2021   | 01JAN2036 |
      
    
    Given table agreement_validity additionally contains the following
        | id                             | validfrom | validto   |   
        | additional_CX6_rec_trng        | 01MAR2018 | 31Dec2035 |

    Given table crew_document additionally contains the following
      | crew          | doc_typ | doc_subtype | validfrom | validto   | docno | maindocno | issuer | si | ac_qual |
      | crew member 1 | REC     | REC         | 01Jan1986 | 31Dec2022 | ""    | ""        | ""     | "" | ""      |
      
    Given table cabin_recurrent additionally contains the following
      | base         | acquals   |validfrom  | validto   | reccode | 
      | OSL          | A238      | 01Jan2020 | 31Dec2035 | 20     | 
     
              
    Given crew member 1 has qualification "ACQUAL+A2" from 15APR2019 to 01JAN2036
    Given crew member 1 has qualification "ACQUAL+38" from 23JUL2019 to 01JAN2036
    
   
    Given a trip with the following activities
      | act    | num | code | dep stn | arr stn | dep             | arr             | ac_typ |
      | ground |     | N3   | OSL     | OSL     | 25OCT2021 11:00 | 25OCT2021 14:00  | A238   |
      | ground |     | CX7  | OSL     | OSL     | 27OCT2021 06:15 | 27OCT2021 14:00 |        |
      | ground |     | N3   | OSL     | OSL     | 28OCT2021 11:00 | 28OCT2021 14:00  | A238   |

    Given trip 1 is assigned to crew member 1 in position AP
    
    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.qln_rec_in_correct_order_CC" shall pass on leg 1 on trip 1 on roster 1
  
@SCENARIO4
  Scenario:rule qln_rec_in_correct_order_CC should fail 
    
    Given planning period from 1SEP2021 to 30NOV2021

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AP         | 1SEP2019   | 01JAN2036 |
           | region          | SKN        | 1APR2019   | 01JAN2036 |
           | base            | OSL        | 1APR2019   | 01JAN2036 |
           | title rank      | AP         | 1APR2019   | 01JAN2036 |
           | main function   | C          | 1SEP2021   | 01JAN2036 |
      
    
    Given table agreement_validity additionally contains the following
        | id                             | validfrom | validto   |   
        | additional_CX6_rec_trng        | 01MAR2018 | 31Dec2035 |

    Given table crew_document additionally contains the following
      | crew          | doc_typ | doc_subtype | validfrom | validto   | docno | maindocno | issuer | si | ac_qual |
      | crew member 1 | REC     | REC         | 01Jan1986 | 31Dec2022 | ""    | ""        | ""     | "" | ""      |
      
    Given table cabin_recurrent additionally contains the following
      | base         | acquals   |validfrom  | validto   | reccode | 
      | OSL          | A238      | 01Jan2020 | 31Dec2035 | 20     | 
     
              
    Given crew member 1 has qualification "ACQUAL+A2" from 15APR2019 to 01JAN2036
    Given crew member 1 has qualification "ACQUAL+38" from 23JUL2019 to 01JAN2036
    
   
    Given a trip with the following activities
      | act    | num | code | dep stn | arr stn | dep             | arr             | ac_typ |
      | ground |     | CX6  | OSL     | OSL     | 27OCT2021 06:15 | 27OCT2021 14:00 |        |
      | ground |     | N3   | OSL     | OSL     | 28OCT2021 11:00 | 28OCT2021 14:00 | A238   |
      | ground |     | CX7  | OSL     | OSL     | 29OCT2021 06:15 | 29OCT2021 14:00 |        |
      | ground |     | CX6  | OSL     | OSL     | 30OCT2021 06:15 | 30OCT2021 14:00 |        |

    Given trip 1 is assigned to crew member 1 in position AP
    
    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.qln_rec_in_correct_order_CC" shall pass on leg 4 on trip 1 on roster 1
  
