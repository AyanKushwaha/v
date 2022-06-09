@tracking
Feature: Test correction of hotel night calculation

  Background: Setup for tracking
      Given planning period from 1jan2020 to 31jan2020
      Given tracking

      @SCENARIO1
      Scenario: Check that date is correct for checkout when time is close to being on the next day (AH)
        Given a crew member with
            | attribute       | value      | valid from | valid to  |
            | crew rank       | AH         |            |           |
            | region          | SKN        |            |           |
            | base            | OSL        |            |           |


        Given a trip with the following activities
            | act     | num     | dep stn | arr stn | dep             | arr             | car     | ac_typ  | code    |
            | leg     | 000177  | CPH     | TOS     | 08JAN2020 14:25 | 08JAN2020 16:55 | SK      | 73K     |         |
            | leg     | 000178  | TOS     | OSL     | 08JAN2020 17:30 | 08JAN2020 19:00 | SK      |  73K    |         |

        Given trip 1 is assigned to crew member 1 in position AH

        When I show "crew" in window 1

        Then rave "report_hotel.%check_out%" shall be "08JAN2020 00:00"

        @SCENARIO2
        Scenario: Check that date is correct when checkout is close to being on the next day (FC)
        Given a crew member with
            | attribute       | value      | valid from | valid to  |
            | crew rank       | FC         |            |           |
            | region          | SKN        |            |           |
            | base            | OSL        |            |           |


        Given a trip with the following activities
            | act     | num     | dep stn | arr stn | dep             | arr             | car     | ac_typ  | code    |
            | leg     | 000177  | CPH     | TOS     | 08JAN2020 14:25 | 08JAN2020 16:55 | SK      | 73K     |         |
            | leg     | 000178  | TOS     | OSL     | 08JAN2020 17:30 | 08JAN2020 19:00 | SK      | 73K     |         |

        Given trip 1 is assigned to crew member 1 in position AH

        When I show "crew" in window 1

        Then rave "report_hotel.%check_out%" shall be "08JAN2020 00:00"

        @SCENARIO3
        Scenario: Check that date is when checkout is on next day, but close to previous day, for FC.
        Given a crew member with
            | attribute       | value      | valid from | valid to  |
            | crew rank       | AH         |            |           |
            | region          | SKN        |            |           |
            | base            | OSL        |            |           |


        Given a trip with the following activities
            | act     | num     | dep stn | arr stn | dep             | arr             | car     | ac_typ  | code    |
            | leg     | 000177  | CPH     | TOS     | 08JAN2020 15:25 | 08JAN2020 17:55 | SK      | 73K     |         |
            | leg     | 000178  | TOS     | OSL     | 08JAN2020 19:30 | 08JAN2020 21:00 | SK      | 73K     |         |

        Given trip 1 is assigned to crew member 1 in position AH

        When I show "crew" in window 1

        Then rave "report_hotel.%check_out%" shall be "09JAN2020 00:00"

        @SCENARIO4
        Scenario: Check that date is when checkout is on next day, but close to previous day, for FC.
        Given a crew member with
            | attribute       | value      | valid from | valid to  |
            | crew rank       | AH         |            |           |
            | region          | SKN        |            |           |
            | base            | OSL        |            |           |


        Given a trip with the following activities
            | act     | num     | dep stn | arr stn | dep             | arr             | car     | ac_typ  | code    |
            | leg     | 000177  | CPH     | TOS     | 08JAN2020 15:00 | 08JAN2020 17:25 | SK      | 73K     |         |
            | leg     | 000178  | TOS     | OSL     | 08JAN2020 19:00 | 08JAN2020 20:30 | SK      | 73K     |         |

        Given trip 1 is assigned to crew member 1 in position AH

        When I show "crew" in window 1

        Then rave "report_hotel.%check_out%" shall be "09JAN2020 00:00"

