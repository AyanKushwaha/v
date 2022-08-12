@planning @FD @FC @LC
Feature:

    Background: Set up for Rostering
        Given Rostering_FC
        Given planning period from 1MAY2019 to 1JUN2019

    Scenario: Check that FAM strings are set correctly after FAM FLT in training log
       Given a crew member with
       | attribute  | value  | valid from | valid to  |
       | base       | CPH    |            |           |
       | title rank | FC     |            |           |
       | region     | SKD    |            |           |
       | contract   | F00469 | 1MAY2019   | 31DEC2035 |

       Given another crew member with
       | attribute  | value  | valid from | valid to  |
       | base       | CPH    |            |           |
       | title rank | FP     |            |           |
       | region     | SKD    |            |           |
       | contract   | F00469 | 1MAY2019   | 31DEC2035 |

       Given crew member 1 has qualification "ACQUAL+A5" from 1APR2019 to 31DEC2035
       Given crew member 2 has qualification "ACQUAL+A5" from 1APR2019 to 31DEC2035

       Given table crew_training_log additionally contains the following
         | crew          | typ     | code | tim            |
	 | crew member 1 | FAM FLT | A5   | 4APR2019 12:22 |
	 | crew member 1 | FAM FLT | A5   | 6APR2019 12:22 |

       Given table ac_qual_map additionally contains the following
         | ac_type | aoc | ac_qual_fc | ac_qual_cc |
	 | 35X     | SK  | A5         | AL         |

       Given a trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
         | leg | 0001 | CPH     | SFO     | 09MAY2019 | 10:25 | 21:45 | SK  | 35X    |
         | leg | 0002 | SFO     | CPH     | 11MAY2019 | 00:35 | 11:15 | SK  | 35X    |

       Given trip 1 is assigned to crew member 1 in position FC
       Given trip 1 is assigned to crew member 2 in position FP

       When I show "crew" in window 1
       and I load rule set "Rostering_FC"
       and I set parameter "fundamental.%start_para%" to "1MAY2019 00:00"
       and I set parameter "fundamental.%end_para%" to "31MAY2019 00:00"

       Then rave "training.%expiry_date_lc_after_fam%" shall be "6Oct2019" on trip 1 on roster 1
       and rave "crg_info.%lc_fam_str%" shall be " FAM: 6Oct2019 (A5)" on trip 1 on roster 1
       and rave "training.%expiry_date_lc_after_fam%" shall be "None" on trip 1 on roster 2
       and rave "crg_info.%lc_fam_str%" shall be "" on trip 1 on roster 2


    Scenario: Check that FAM strings are set correctly after FAM FLT in training log with LC in training log
       Given a crew member with
       | attribute  | value  | valid from | valid to  |
       | base       | CPH    |            |           |
       | title rank | FC     |            |           |
       | region     | SKD    |            |           |
       | contract   | F00469 | 1MAY2019   | 31DEC2035 |

       Given another crew member with
       | attribute  | value  | valid from | valid to  |
       | base       | CPH    |            |           |
       | title rank | FP     |            |           |
       | region     | SKD    |            |           |
       | contract   | F00469 | 1MAY2019   | 31DEC2035 |

       Given crew member 1 has qualification "ACQUAL+A5" from 1APR2019 to 31DEC2035
       Given crew member 2 has qualification "ACQUAL+A5" from 1APR2019 to 31DEC2035

       Given table crew_training_log additionally contains the following
         | crew          | typ     | code | tim             |
	 | crew member 1 | FAM FLT | A5   | 4APR2019 12:22  |
	 | crew member 1 | FAM FLT | A5   | 6APR2019 12:22  |
	 | crew member 1 | LC      | A5   | 26APR2019 12:22 |

       Given table ac_qual_map additionally contains the following
         | ac_type | aoc | ac_qual_fc | ac_qual_cc |
	 | 35X     | SK  | A5         | AL         |

       Given a trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
         | leg | 0001 | CPH     | SFO     | 09MAY2019 | 10:25 | 21:45 | SK  | 35X    |
         | leg | 0002 | SFO     | CPH     | 11MAY2019 | 00:35 | 11:15 | SK  | 35X    |

       Given trip 1 is assigned to crew member 1 in position FC
       Given trip 1 is assigned to crew member 2 in position FP

       When I show "crew" in window 1
       and I load rule set "Rostering_FC"
       and I set parameter "fundamental.%start_para%" to "1MAY2019 00:00"
       and I set parameter "fundamental.%end_para%" to "31MAY2019 00:00"

       Then rave "training.%expiry_date_lc_after_fam%" shall be "None" on trip 1 on roster 1
       and rave "crg_info.%lc_fam_str%" shall be "" on trip 1 on roster 1
       and rave "training.%expiry_date_lc_after_fam%" shall be "None" on trip 1 on roster 2
       and rave "crg_info.%lc_fam_str%" shall be "" on trip 1 on roster 2


    Scenario: Check that FAM strings are set correctly after FAM FLT in training log with LC in roster
       Given a crew member with
       | attribute  | value  | valid from | valid to  |
       | base       | CPH    |            |           |
       | title rank | FC     |            |           |
       | region     | SKD    |            |           |
       | contract   | F00469 | 1MAY2019   | 31DEC2035 |

       Given another crew member with
       | attribute  | value  | valid from | valid to  |
       | base       | CPH    |            |           |
       | title rank | FP     |            |           |
       | region     | SKD    |            |           |
       | contract   | F00469 | 1MAY2019   | 31DEC2035 |

       Given crew member 1 has qualification "ACQUAL+A5" from 1APR2019 to 31DEC2035
       Given crew member 2 has qualification "ACQUAL+A5" from 1APR2019 to 31DEC2035

       Given table crew_training_log additionally contains the following
         | crew          | typ     | code | tim             |
	 | crew member 1 | FAM FLT | A5   | 4APR2019 12:22  |
	 | crew member 1 | FAM FLT | A5   | 6APR2019 12:22  |

       Given table ac_qual_map additionally contains the following
         | ac_type | aoc | ac_qual_fc | ac_qual_cc |
	 | 35X     | SK  | A5         | AL         |

       Given a trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
         | leg | 0001 | CPH     | SFO     | 09MAY2019 | 10:25 | 21:45 | SK  | 35X    |
         | leg | 0002 | SFO     | CPH     | 11MAY2019 | 00:35 | 11:15 | SK  | 35X    |

       Given trip 1 is assigned to crew member 1 in position FC with
         | type      | leg | name     | value |
	 | attribute | 1   | TRAINING | LC    |

       Given trip 1 is assigned to crew member 2 in position FP

       When I show "crew" in window 1
       and I load rule set "Rostering_FC"
       and I set parameter "fundamental.%start_para%" to "1MAY2019 00:00"
       and I set parameter "fundamental.%end_para%" to "31MAY2019 00:00"

       Then rave "training.%expiry_date_lc_after_fam%" shall be "None" on trip 1 on roster 1
       and rave "crg_info.%lc_fam_str%" shall be "" on trip 1 on roster 1
       and rave "training.%expiry_date_lc_after_fam%" shall be "None" on trip 1 on roster 2
       and rave "crg_info.%lc_fam_str%" shall be "" on trip 1 on roster 2


    Scenario: Check that FAM strings are set correctly after FAM FLT in roster
       Given a crew member with
       | attribute  | value  | valid from | valid to  |
       | base       | CPH    |            |           |
       | title rank | FC     |            |           |
       | region     | SKD    |            |           |
       | contract   | F00469 | 1MAY2019   | 31DEC2035 |

       Given another crew member with
       | attribute  | value  | valid from | valid to  |
       | base       | CPH    |            |           |
       | title rank | FP     |            |           |
       | region     | SKD    |            |           |
       | contract   | F00469 | 1MAY2019   | 31DEC2035 |

       Given crew member 1 has qualification "ACQUAL+A5" from 1APR2019 to 31DEC2035
       Given crew member 2 has qualification "ACQUAL+A5" from 1APR2019 to 31DEC2035

       Given table ac_qual_map additionally contains the following
         | ac_type | aoc | ac_qual_fc | ac_qual_cc |
	 | 35X     | SK  | A5         | AL         |

       Given a trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
         | leg | 0001 | CPH     | SFO     | 09MAY2019 | 10:25 | 21:45 | SK  | 35X    |
         | leg | 0002 | SFO     | CPH     | 11MAY2019 | 00:35 | 11:15 | SK  | 35X    |

       Given trip 1 is assigned to crew member 1 in position FC with
         | type      | leg | name     | value   |
	 | attribute | 1-2 | TRAINING | FAM FLT |

       Given trip 1 is assigned to crew member 2 in position FP

       When I show "crew" in window 1
       and I load rule set "Rostering_FC"
       and I set parameter "fundamental.%start_para%" to "1MAY2019 00:00"
       and I set parameter "fundamental.%end_para%" to "31MAY2019 00:00"

       Then rave "training.%expiry_date_lc_after_fam%" shall be "11Nov2019" on trip 1 on roster 1
       and rave "crg_info.%lc_fam_str%" shall be " FAM: 11Nov2019 (A5)" on trip 1 on roster 1
       and rave "training.%expiry_date_lc_after_fam%" shall be "None" on trip 1 on roster 2
       and rave "crg_info.%lc_fam_str%" shall be "" on trip 1 on roster 2


    Scenario: Check that FAM strings are set correctly after FAM FLT in roster with LC in roster
       Given a crew member with
       | attribute  | value  | valid from | valid to  |
       | base       | CPH    |            |           |
       | title rank | FC     |            |           |
       | region     | SKD    |            |           |
       | contract   | F00469 | 1MAY2019   | 31DEC2035 |

       Given another crew member with
       | attribute  | value  | valid from | valid to  |
       | base       | CPH    |            |           |
       | title rank | FP     |            |           |
       | region     | SKD    |            |           |
       | contract   | F00469 | 1MAY2019   | 31DEC2035 |

       Given crew member 1 has qualification "ACQUAL+A5" from 1APR2019 to 31DEC2035
       Given crew member 2 has qualification "ACQUAL+A5" from 1APR2019 to 31DEC2035

       Given table ac_qual_map additionally contains the following
         | ac_type | aoc | ac_qual_fc | ac_qual_cc |
	 | 35X     | SK  | A5         | AL         |

       Given a trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
         | leg | 0001 | CPH     | SFO     | 09MAY2019 | 10:25 | 21:45 | SK  | 35X    |
         | leg | 0002 | SFO     | CPH     | 11MAY2019 | 00:35 | 11:15 | SK  | 35X    |

       Given trip 1 is assigned to crew member 1 in position FC with
         | type      | leg | name     | value   |
	 | attribute | 1-2 | TRAINING | FAM FLT |

       Given trip 1 is assigned to crew member 2 in position FP

       Given another trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
         | leg | 0001 | CPH     | SFO     | 19MAY2019 | 10:25 | 21:45 | SK  | 35X    |
         | leg | 0002 | SFO     | CPH     | 21MAY2019 | 00:35 | 11:15 | SK  | 35X    |

       Given trip 2 is assigned to crew member 1 in position FC with
         | type      | leg | name     | value   |
	 | attribute | 1   | TRAINING | LC      |

       Given trip 2 is assigned to crew member 2 in position FP

       When I show "crew" in window 1
       and I load rule set "Rostering_FC"
       and I set parameter "fundamental.%start_para%" to "1MAY2019 00:00"
       and I set parameter "fundamental.%end_para%" to "31MAY2019 00:00"

       Then rave "training.%expiry_date_lc_after_fam%" shall be "None" on trip 1 on roster 1
       and rave "crg_info.%lc_fam_str%" shall be "" on trip 1 on roster 1
       and rave "training.%expiry_date_lc_after_fam%" shall be "None" on trip 1 on roster 2
       and rave "crg_info.%lc_fam_str%" shall be "" on trip 1 on roster 2


    @SCENARIO6
    Scenario: Check that rule fails when LC after FAM is not performed in time
       Given a crew member with
       | attribute  | value  | valid from | valid to  |
       | base       | CPH    |            |           |
       | title rank | FC     |            |           |
       | region     | SKD    |            |           |
       | contract   | F00469 | 1NOV2018   | 31DEC2035 |

       Given crew member 1 has qualification "ACQUAL+A5" from 1NOV2018 to 31DEC2035

       Given table crew_training_log additionally contains the following
         | crew          | typ     | code | tim             |
	 | crew member 1 | FAM FLT | A5   | 5NOV2018 12:22  |
	 | crew member 1 | FAM FLT | A5   | 10NOV2018 12:22 |

       Given table ac_qual_map additionally contains the following
         | ac_type | aoc | ac_qual_fc | ac_qual_cc |
	 | 35X     | SK  | A5         | AL         |

       Given a trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
         | leg | 0001 | CPH     | SFO     | 05MAY2019 | 10:25 | 21:45 | SK  | 35X    |
         | leg | 0002 | SFO     | CPH     | 07MAY2019 | 00:35 | 11:15 | SK  | 35X    |

       Given a trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
         | leg | 0001 | CPH     | SFO     | 11MAY2019 | 10:25 | 21:45 | SK  | 35X    |
         | leg | 0002 | SFO     | CPH     | 13MAY2019 | 00:35 | 11:15 | SK  | 35X    |

       Given trip 1 is assigned to crew member 1 in position FC
       Given trip 2 is assigned to crew member 1 in position FC

       When I show "crew" in window 1
       and I load rule set "Rostering_FC"
       and I set parameter "fundamental.%start_para%" to "1MAY2019 00:00"
       and I set parameter "fundamental.%end_para%" to "31MAY2019 00:00"

       Then rave "training.%expiry_date_lc_after_fam%" shall be "10May2019" on trip 1 on roster 1
       and the rule "rules_qual_ccr.qln_lc_after_fam_performed_fd" shall pass on trip 1 on roster 1
       and the rule "rules_qual_ccr.qln_lc_after_fam_performed_fd" shall fail on trip 2 on roster 1
