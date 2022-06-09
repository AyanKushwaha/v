Feature: JCRT : Instructor should fly min 2 legs per month in normal position
Background: set up for tracking
Given tracking
Given planning period from 1AUG2020 to 30SEP2020

@SCENARIO1
Scenario: min_legs_per_month_for_instructor should pass for exactly  2 legs in one month for crew with title rank FC

Given a crew member with
| attribute       | value     | valid from | valid to |
| base            | OSL       |            |          |
| title rank      | FC        |            |          |


Given crew member 1 has qualification "ACQUAL+A5" from 1AUG2019 to 31AUG2021
Given crew member 1 has acqual qualification "ACQUAL+A5+INSTRUCTOR+LIFUS" from 1AUG2019 to 31AUG2021

Given a trip with the following activities
| act | num | dep stn | arr stn | date | dep | arr | car | ac_typ |
| leg | 0001 | OSL | DBV | 01AUG2020 | 06:00 | 08:20 | SK | 35X |
| leg | 0002 | DBV | CPH | 01AUG2020 | 15:15 | 16:25 | SK | 35X |


Given trip 1 is assigned to crew member 1

When I show "crew" in window 1

Then the rule "rules_training_ccr.min_legs_per_month_for_instructor" shall pass on leg 2 on trip 1 on roster 1


@SCENARIO2
Scenario: min_legs_per_month_for_instructor should pass for more than or equal to 2 legs in one month without including ZFTT LIFUS

Given a crew member with
| attribute       | value     | valid from | valid to |
| base            | OSL       |            |          |
| title rank      | FC        |            |          |


Given crew member 1 has qualification "ACQUAL+A5" from 1AUG2019 to 31AUG2021
Given crew member 1 has acqual qualification "ACQUAL+A5+INSTRUCTOR+LIFUS" from 1AUG2019 to 31AUG2021


Given a crew member with
| attribute       | value     | valid from | valid to |
| base            | OSL       |            |          |
| title rank      | FP        |            |          |

Given crew member 2 has qualification "ACQUAL+A5" from 1AUG2019 to 31AUG2021

Given a trip with the following activities
| act | num | dep stn | arr stn | date | dep | arr | car | ac_typ |
| leg | 0001 | OSL | DBV | 01AUG2020 | 06:00 | 08:20 | SK | 35X |

Given trip 1 is assigned to crew member 1

Given a trip with the following activities
| act | num | dep stn | arr stn | date | dep | arr | car | ac_typ |
| leg | 0002 | OSL | DBV | 02AUG2020 | 06:00 | 08:20 | SK | 35X |
| leg | 0003 | DBV | CPH | 02AUG2020 | 15:15 | 16:25 | SK | 35X |

Given trip 2 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="ZFTT LIFUS"
Given trip 2 is assigned to crew member 2 in position FP with attribute TRAINING="ZFTT LIFUS"

Given a trip with the following activities
| act | num | dep stn | arr stn | date | dep | arr | car | ac_typ |
| leg | 0004 | OSL | DBV | 03AUG2020 | 06:00 | 08:20 | SK | 35X |

Given trip 3 is assigned to crew member 1

When I show "crew" in window 1

Then the rule "rules_training_ccr.min_legs_per_month_for_instructor" shall pass on leg 1 on trip 3 on roster 1


@SCENARIO3
Scenario: min_legs_per_month_for_instructor should fail for more than or equal to 2 legs in one month without including ZFTT LIFUS

Given a crew member with
| attribute       | value     | valid from | valid to |
| base            | OSL       |            |          |
| title rank      | FC        |            |          |


Given crew member 1 has qualification "ACQUAL+A5" from 1AUG2019 to 31AUG2021
Given crew member 1 has acqual qualification "ACQUAL+A5+INSTRUCTOR+LIFUS" from 1AUG2019 to 31AUG2021


Given a crew member with
| attribute       | value     | valid from | valid to |
| base            | OSL       |            |          |
| title rank      | FP        |            |          |

Given crew member 2 has qualification "ACQUAL+A5" from 1AUG2019 to 31AUG2021

Given a trip with the following activities
| act | num | dep stn | arr stn | date | dep | arr | car | ac_typ |
| leg | 0001 | OSL | DBV | 01AUG2020 | 06:00 | 08:20 | SK | 35X |

Given trip 1 is assigned to crew member 1

Given a trip with the following activities
| act | num | dep stn | arr stn | date | dep | arr | car | ac_typ |
| leg | 0002 | OSL | DBV | 02AUG2020 | 06:00 | 08:20 | SK | 35X |
| leg | 0003 | DBV | CPH | 02AUG2020 | 15:15 | 16:25 | SK | 35X |

Given trip 2 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="ZFTT LIFUS"
Given trip 2 is assigned to crew member 2 in position FP with attribute TRAINING="ZFTT LIFUS"

Given a trip with the following activities
| act | num | dep stn | arr stn | date | dep | arr | car | ac_typ |
| leg | 0004 | OSL | DBV | 03AUG2020 | 06:00 | 08:20 | SK | 35X |

Given trip 3 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="ZFTT LIFUS"
Given trip 3 is assigned to crew member 2 in position FP with attribute TRAINING="ZFTT LIFUS"


When I show "crew" in window 1

Then the rule "rules_training_ccr.min_legs_per_month_for_instructor" shall fail on leg 1 on trip 3 on roster 1


@SCENARIO4
Scenario: min_legs_per_month_for_instructor should pass for more than or equal to 2 legs in one month without including ZFTT X

Given a crew member with
| attribute       | value     | valid from | valid to |
| base            | OSL       |            |          |
| title rank      | FC        |            |          |


Given crew member 1 has qualification "ACQUAL+A5" from 1AUG2019 to 31AUG2021
Given crew member 1 has acqual qualification "ACQUAL+A5+INSTRUCTOR+LIFUS" from 1AUG2019 to 31AUG2021


Given a crew member with
| attribute       | value     | valid from | valid to |
| base            | OSL       |            |          |
| title rank      | FP        |            |          |

Given crew member 2 has qualification "ACQUAL+A5" from 1AUG2019 to 31AUG2021

Given a trip with the following activities
| act | num | dep stn | arr stn | date | dep | arr | car | ac_typ |
| leg | 0001 | OSL | DBV | 01AUG2020 | 06:00 | 08:20 | SK | 35X |

Given trip 1 is assigned to crew member 1

Given a trip with the following activities
| act | num | dep stn | arr stn | date | dep | arr | car | ac_typ |
| leg | 0002 | OSL | DBV | 02AUG2020 | 06:00 | 08:20 | SK | 35X |
| leg | 0003 | DBV | CPH | 02AUG2020 | 15:15 | 16:25 | SK | 35X |

Given trip 2 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="ZFTT X"
Given trip 2 is assigned to crew member 2 in position FP with attribute TRAINING="ZFTT X"

Given a trip with the following activities
| act | num | dep stn | arr stn | date | dep | arr | car | ac_typ |
| leg | 0004 | OSL | DBV | 03AUG2020 | 06:00 | 08:20 | SK | 35X |

Given trip 3 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="ZFTT X"
Given trip 3 is assigned to crew member 2 in position FP with attribute TRAINING="ZFTT X"

Given a trip with the following activities
| act | num | dep stn | arr stn | date | dep | arr | car | ac_typ |
| leg | 0005 | OSL | DBV | 04AUG2020 | 06:00 | 08:20 | SK | 35X |

Given trip 4 is assigned to crew member 1

When I show "crew" in window 1

Then the rule "rules_training_ccr.min_legs_per_month_for_instructor" shall pass on leg 1 on trip 4 on roster 1

@SCENARIO5
Scenario: min_legs_per_month_for_instructor should pass for more than or equal to 2 legs in one month for monthly transitioning flights

Given a crew member with
| attribute       | value     | valid from | valid to |
| base            | OSL       |            |          |
| title rank      | FC        |            |          |

Given crew member 1 has qualification "ACQUAL+A5" from 1AUG2019 to 31AUG2021
Given crew member 1 has acqual qualification "ACQUAL+A5+INSTRUCTOR+TRI" from 1AUG2019 to 31AUG2021

Given a trip with the following activities
| act | num | dep stn | arr stn | date | dep | arr | car | ac_typ |
| leg | 0001 | OSL | DBV | 30AUG2020 | 06:00 | 08:20 | SK | 35X |

Given trip 1 is assigned to crew member 1

Given a trip with the following activities
| act | num | dep stn | arr stn | date | dep | arr | car | ac_typ |
| leg | 0002 | DBV | OSL | 31AUG2020 | 21:45 |     | SK | 35X |
| leg | 0003 | OSL | CPH | 01SEP2020 | 04:15 | 05:25 | SK | 35X |

Given trip 2 is assigned to crew member 1

Given a trip with the following activities
| act | num | dep stn | arr stn | date | dep | arr | car | ac_typ |
| leg | 0004 | CPH | DBV | 01SEP2020 | 06:00 | 08:20 | SK | 35X |

Given trip 3 is assigned to crew member 1

Given a trip with the following activities
| act | num | dep stn | arr stn | date | dep | arr | car | ac_typ |
| leg | 0005 | DBV | OSL | 01SEP2020 | 10:00 | 12:20 | SK | 35X |

Given trip 4 is assigned to crew member 1

When I show "crew" in window 1

Then the rule "rules_training_ccr.min_legs_per_month_for_instructor" shall pass on leg 1 on trip 2 on roster 1



@SCENARIO6
Scenario: min_legs_per_month_for_instructor should pass for A3A5 crew with atleast one A5 legs 

Given a crew member with
| attribute       | value     | valid from | valid to |
| base            | OSL       |            |          |
| title rank      | FC        |            |          |

Given crew member 1 has qualification "ACQUAL+A3" from 1AUG2019 to 31AUG2021
Given crew member 1 has qualification "ACQUAL+A5" from 1AUG2019 to 31AUG2021
Given crew member 1 has acqual qualification "ACQUAL+A5+INSTRUCTOR+LIFUS" from 1AUG2019 to 31AUG2021

Given a trip with the following activities
| act | num | dep stn | arr stn | date | dep | arr | car | ac_typ |
| leg | 0001 | OSL | DBV | 31AUG2020 | 06:00 | 08:20 | SK | 35X |
| leg | 0002 | DBV | CPH | 31AUG2020 | 10:15 | 12:25 | SK | 333 |
| leg | 0002 | CPH | DBV | 31AUG2020 | 14:15 | 16:25 | SK | 333 |
| leg | 0002 | DBV | OSL | 31AUG2020 | 20:15 | 23:25 | SK | 333 |

Given trip 1 is assigned to crew member 1

When I show "crew" in window 1

Then the rule "rules_training_ccr.min_legs_per_month_for_instructor" shall pass on leg 4 on trip 1 on roster 1

@SCENARIO7
Scenario: min_legs_per_month_for_instructor should fail for A3A5 crew without atleast one A5 legs

Given a crew member with
| attribute       | value     | valid from | valid to |
| base            | OSL       |            |          |
| title rank      | FC        |            |          |

Given crew member 1 has qualification "ACQUAL+A3" from 1AUG2019 to 31AUG2021
Given crew member 1 has qualification "ACQUAL+A5" from 1AUG2019 to 31AUG2021
Given crew member 1 has acqual qualification "ACQUAL+A5+INSTRUCTOR+LIFUS" from 1AUG2019 to 31AUG2021

Given a trip with the following activities
| act | num | dep stn | arr stn | date | dep | arr | car | ac_typ |
| leg | 0001 | OSL | DBV | 31AUG2020 | 06:00 | 08:20 | SK | 333 |
| leg | 0002 | DBV | CPH | 31AUG2020 | 10:15 | 12:25 | SK | 333 |
| leg | 0002 | CPH | DBV | 31AUG2020 | 14:15 | 16:25 | SK | 333 |
| leg | 0002 | DBV | OSL | 31AUG2020 | 20:15 | 23:25 | SK | 333 |

Given trip 1 is assigned to crew member 1

When I show "crew" in window 1

Then the rule "rules_training_ccr.min_legs_per_month_for_instructor" shall fail on leg 4 on trip 1 on roster 1

@SCENARIO9
Scenario:  min_legs_per_month_for_instructor should pass for mixed combinations

Given a crew member with
| attribute       | value     | valid from | valid to |
| base            | OSL       |            |          |
| title rank      | FC        |            |          |

Given crew member 1 has qualification "ACQUAL+A3" from 1AUG2019 to 31AUG2021
Given crew member 1 has qualification "ACQUAL+A5" from 1AUG2019 to 31AUG2021
Given crew member 1 has acqual qualification "ACQUAL+A5+INSTRUCTOR+TRE" from 1AUG2019 to 31AUG2021

Given a crew member with
| attribute       | value     | valid from | valid to |
| base            | OSL       |            |          |
| title rank      | FP        |            |          |

Given crew member 2 has qualification "ACQUAL+A5" from 1AUG2019 to 31AUG2021

Given a trip with the following activities
| act | num | dep stn | arr stn | date | dep | arr | car | ac_typ |
| leg | 0001 | OSL | DBV | 28AUG2020 | 06:00 | 08:20 | SK | 35X |
| leg | 0002 | DBV | OSL | 29AUG2020 | 06:00 | 08:20 | SK | 35X |

Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="ZFTT LIFUS"
Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="ZFTT LIFUS"

Given a trip with the following activities
| act | num | dep stn | arr stn | date | dep | arr | car | ac_typ |
| leg | 0003 | OSL | DBV | 31AUG2020 | 17:00 | 19:20 | SK | 333 |
| leg | 0004 | DBV | OSL | 31AUG2020 | 20:00 | 22:00 | SK | 333 |

Given trip 2 is assigned to crew member 1

When I show "crew" in window 1

Then the rule "rules_training_ccr.min_legs_per_month_for_instructor" shall fail on leg 2 on trip 2 on roster 1



