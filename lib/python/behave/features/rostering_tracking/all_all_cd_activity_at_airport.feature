@JCRT @ALL

Feature: include CD activity as airport activity

########################
# JIRA - SKCMS-2500
########################

Background:
    Given Tracking
    Given planning period from 1OCT2020 to 31OCT2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | employee number | 38411      |            |           |
           | sex             | M          |            |           |
           | crew rank       | FC         | 03OCT2020  | 02OCT2021 |
           | region          | SKN        | 03OCT2020  | 02OCT2021 |
           | base            | OSL        | 03OCT2020  | 02OCT2021 |
           | title rank      | FC         | 03OCT2020  | 02OCT2021 |
           | contract        | V00007     | 03OCT2020  | 23NOV2020 |
           | published       | 01OCT2020  | 01JAN1986  |           |

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | dh      | SK      | 002551  | OSL     | AMS     | 11OCT2020 06:15 | 11OCT2020 07:45 | CRC     |         |
    Given trip 1 is assigned to crew member 1 in position TL

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | dh      | SK      | 002551  | AMS     | OSL     | 28OCT2020 06:15 | 28OCT2020 07:45 | CRC     |         |
    Given trip 2 is assigned to crew member 1 in position TL

  @SCENARIO_1
  Scenario: Before CD book an airport hotel

  Given crew member 1 has a personal activity "CD" at station "AMS" that starts at 11OCT2020 22:00 and ends at 14OCT2020 22:00

  When I show "crew" in window 1
  Then rave "hotel.%use_airport_hotel%" shall be "True" on leg 1
  and rave "hotel.%_activity_at_airport%" shall be "True" on leg 2

  @SCENARIO_2
  Scenario: Before other activities not on airport, do not book airport hotel

  Given crew member 1 has a personal activity "F20" at station "AMS" that starts at 11OCT2020 22:00 and ends at 14OCT2020 22:00

  When I show "crew" in window 1
  Then rave "hotel.%use_airport_hotel%" shall be "False" on leg 1
  and rave "hotel.%_activity_at_airport%" shall be "False" on leg 2
