@TRACKING @ALL @HOTEL
Feature: Tests that hotel booking reports uses next flight duty and not any "standby at hotel" activities when
  setting departure flight information (flight number and departure time) in hotel bookings.

###################################################################################################

  @SCENARIO1
  Scenario: Departure flight from hotel should be next flight duty (HC).
    Given Tracking
    Given planning period from 01Feb2020 to 01Mar2020

    Given a crew member with
      | attribute  | value     | valid from | valid to  |
      | crew rank  | FP        | 28NOV2014  | 01JAN2036 |
      | region     | SKD       | 28NOV2014  | 01JAN2036 |
      | base       | CPH       | 28NOV2014  | 01JAN2036 |
      | title rank | FP        | 28NOV2014  | 01JAN2036 |
      | contract   | F00469    | 08JAN2017  | 05MAR2020 |
      | published  | 01AUG2020 | 01JAN1986  |           |

    Given crew member 1 has qualification "ACQUAL+A2" from 28NOV2014 to 01JAN2036

    Given a trip with the following activities
      | act | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | leg | SK  | 002679 | ARN     | TXL     | 09FEB2020 16:25 | 09FEB2020 18:00 | 31W    |      |
      | leg | SK  | 002680 | TXL     | ARN     | 09FEB2020 18:40 | 09FEB2020 20:20 | 31W    |      |
      | leg | SK  | 006003 | ARN     | AGP     | 10FEB2020 12:05 | 10FEB2020 16:25 | 32N    |      |
      | leg | SK  | 006004 | AGP     | ARN     | 10FEB2020 17:15 | 10FEB2020 21:40 | 32N    |      |
      | leg | SK  | 000411 | ARN     | CPH     | 11FEB2020 19:05 | 11FEB2020 20:20 | 32W    |      |

    Given trip 1 is assigned to crew member 1 in position FP

    Given crew member 1 has a personal activity "HC" at station "ARN" that starts at 11FEB2020 13:40 and ends at 11FEB2020 18:15
    Given crew member 1 has a personal activity "F" at station "CPH" that starts at 11FEB2020 23:00 and ends at 14FEB2020 23:00

    When I show "crew" in window 1
    Then rave "report_hotel.%dep_flight_nr%" shall be "SK 0411" on leg 4 on trip 1 on roster 1
  and rave "report_hotel.%dep_flight_start%" shall be "11FEB2020 20:05" on leg 4 on trip 1 on roster 1
  and rave "report_hotel.%dep_flight_dep_stn%" shall be "ARN" on leg 4 on trip 1 on roster 1
  and rave "report_hotel.%dep_flight_passive%" shall be "False" on leg 4 on trip 1 on roster 1
  and rave "report_hotel.%next_leg_start_hotel%" shall be "11FEB2020 20:05" on leg 4 on trip 1 on roster 1

###################################################################################################

  @SCENARIO2
  Scenario: Departure flight from hotel should be next flight duty (H).
    Given Tracking
    Given planning period from 01Jul2020 to 01Aug2020

    Given a crew member with
      | attribute  | value       | valid from | valid to  |
      | crew rank  | FC          | 01JAN2016  | 31DEC2035 |
      | region     | SKN         | 01JAN2016  | 31DEC2035 |
      | base       | TRD         | 01JAN2016  | 31DEC2035 |
      | title rank | FC          | 01JAN2016  | 31DEC2035 |
      | contract   | V00008-CV50 | 28JUN2020  | 01SEP2020 |
      | published  | 01AUG2020   | 01JAN1986  |           |

    Given crew member 1 has qualification "ACQUAL+38" from 29APR1996 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+KKN" from 09APR2014 to 31DEC2020
    Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+LYR" from 04APR2014 to 31OCT2020
    Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+TOS" from 03NOV2014 to 31MAR2021

    Given a trip with the following activities
      | act | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | leg | SK  | 004556 | TRD     | BOO     | 02JUL2020 06:40 | 02JUL2020 07:40 | 73V    |      |
      | leg | SK  | 004556 | BOO     | TOS     | 02JUL2020 08:05 | 02JUL2020 08:55 | 73V    |      |
      | leg | SK  | 004571 | TOS     | BOO     | 02JUL2020 09:25 | 02JUL2020 10:15 | 73V    |      |
      | leg | SK  | 004571 | BOO     | TRD     | 02JUL2020 10:40 | 02JUL2020 11:35 | 73V    |      |
      | leg | SK  | 000375 | TRD     | OSL     | 02JUL2020 14:35 | 02JUL2020 15:30 | 73H    |      |

    Given trip 1 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | leg | SK  | 000215 | OSL     | KRS     | 04JUL2020 06:25 | 04JUL2020 07:10 | 73S    |      |
      | leg | SK  | 000216 | KRS     | OSL     | 04JUL2020 07:35 | 04JUL2020 08:25 | 73S    |      |
      | leg | SK  | 001467 | OSL     | CPH     | 04JUL2020 09:55 | 04JUL2020 11:05 | 73K    |      |
      | leg | SK  | 001456 | CPH     | OSL     | 04JUL2020 11:45 | 04JUL2020 12:55 | 73K    |      |
      | dh  | SK  | 000354 | OSL     | TRD     | 04JUL2020 14:30 | 04JUL2020 15:25 | 73S    |      |

    Given trip 2 is assigned to crew member 1 in position FC

    Given crew member 1 has a personal activity "H" at station "OSL" that starts at 03JUL2020 05:00 and ends at 03JUL2020 15:00

    When I show "crew" in window 1
    Then rave "report_hotel.%dep_flight_nr%" shall be "SK 0215" on leg 5 on trip 1 on roster 1
  and rave "report_hotel.%dep_flight_start%" shall be "04JUL2020 08:25" on leg 5 on trip 1 on roster 1
  and rave "report_hotel.%dep_flight_dep_stn%" shall be "OSL" on leg 5 on trip 1 on roster 1
  and rave "report_hotel.%dep_flight_passive%" shall be "False" on leg 5 on trip 1 on roster 1
  and rave "report_hotel.%next_leg_start_hotel%" shall be "04JUL2020 08:25" on leg 5 on trip 1 on roster 1

###################################################################################################

  @SCENARIO3
  Scenario: Standby at airport shall be used as next flight duty (A).
    Given Tracking
    Given planning period from 01Jul2020 to 01Aug2020

    Given a crew member with
      | attribute  | value       | valid from | valid to  |
      | crew rank  | FC          | 01JAN2016  | 31DEC2035 |
      | region     | SKN         | 01JAN2016  | 31DEC2035 |
      | base       | TRD         | 01JAN2016  | 31DEC2035 |
      | title rank | FC          | 01JAN2016  | 31DEC2035 |
      | contract   | V00008-CV50 | 28JUN2020  | 01SEP2020 |
      | published  | 01AUG2020   | 01JAN1986  |           |

    Given crew member 1 has qualification "ACQUAL+38" from 29APR1996 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+KKN" from 09APR2014 to 31DEC2020
    Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+LYR" from 04APR2014 to 31OCT2020
    Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+TOS" from 03NOV2014 to 31MAR2021

    Given a trip with the following activities
      | act | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | leg | SK  | 004556 | TRD     | BOO     | 02JUL2020 06:40 | 02JUL2020 07:40 | 73V    |      |
      | leg | SK  | 004556 | BOO     | TOS     | 02JUL2020 08:05 | 02JUL2020 08:55 | 73V    |      |
      | leg | SK  | 004571 | TOS     | BOO     | 02JUL2020 09:25 | 02JUL2020 10:15 | 73V    |      |
      | leg | SK  | 004571 | BOO     | TRD     | 02JUL2020 10:40 | 02JUL2020 11:35 | 73V    |      |
      | leg | SK  | 000375 | TRD     | OSL     | 02JUL2020 14:35 | 02JUL2020 15:30 | 73H    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    Given another trip with the following activities
      | act | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | leg | SK  | 000215 | OSL     | KRS     | 04JUL2020 06:25 | 04JUL2020 07:10 | 73S    |      |
      | leg | SK  | 000216 | KRS     | OSL     | 04JUL2020 07:35 | 04JUL2020 08:25 | 73S    |      |
      | leg | SK  | 001467 | OSL     | CPH     | 04JUL2020 09:55 | 04JUL2020 11:05 | 73K    |      |
      | leg | SK  | 001456 | CPH     | OSL     | 04JUL2020 11:45 | 04JUL2020 12:55 | 73K    |      |
      | dh  | SK  | 000354 | OSL     | TRD     | 04JUL2020 14:30 | 04JUL2020 15:25 | 73S    |      |

    Given trip 2 is assigned to crew member 1 in position FP

    Given crew member 1 has a personal activity "A" at station "OSL" that starts at 03JUL2020 05:00 and ends at 03JUL2020 15:00

    When I show "crew" in window 1
    Then rave "report_hotel.%dep_flight_nr%" shall be " -001" on leg 5 on trip 1 on roster 1
  and rave "report_hotel.%dep_flight_start%" shall be "03JUL2020 07:00" on leg 5 on trip 1 on roster 1
  and rave "report_hotel.%dep_flight_dep_stn%" shall be "OSL" on leg 5 on trip 1 on roster 1
  and rave "report_hotel.%dep_flight_passive%" shall be "False" on leg 5 on trip 1 on roster 1
  and rave "report_hotel.%next_leg_start_hotel%" shall be "03JUL2020 07:00" on leg 5 on trip 1 on roster 1

