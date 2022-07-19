#!/bin/env python
"""
SKCMS-2052
"Extra connection time at LIFUS / SHOOLFLIGHT / SUPERNUM"
Sprint: SAS2012
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from RelTime import RelTime

__version__ = '0.0.9d'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    validfrom = int(AbsTime('01Jan1986'))
    validto = int(AbsTime('31Dec2035'))
    ops = []

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'PASSTOSIM', 'leg_end_station': 'CPH', 'ac_type': 'N/A',
                                   'min_training_cnx_time': int(RelTime("00:45")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'PASSTOSIM', 'leg_end_station': 'OSL', 'ac_type': 'N/A',
                                   'min_training_cnx_time': int(RelTime("00:30")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'PASSTOSIM', 'leg_end_station': 'ARN', 'ac_type': 'N/A',
                                   'min_training_cnx_time': int(RelTime("00:45")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'PASSTOSIM', 'leg_end_station': '-', 'ac_type': 'N/A',
                                   'min_training_cnx_time': int(RelTime("00:45")), 'validfrom': validfrom,
                                   'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'SIMTOPASS', 'leg_end_station': '-', 'ac_type': 'N/A',
                                   'min_training_cnx_time': int(RelTime("00:45")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'TOLC', 'leg_end_station': 'N/A', 'ac_type': '-',
                                   'min_training_cnx_time': int(RelTime("01:15")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'LCTOPASS', 'leg_end_station': 'N/A', 'ac_type': '-',
                                   'min_training_cnx_time': int(RelTime("01:30")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'LCTOACT', 'leg_end_station': 'N/A', 'ac_type': '-',
                                   'min_training_cnx_time': int(RelTime("01:45")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'TOILC', 'leg_end_station': 'N/A', 'ac_type': '-',
                                   'min_training_cnx_time': int(RelTime("01:15")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'ILCTOPASS', 'leg_end_station': 'N/A', 'ac_type': '-',
                                   'min_training_cnx_time': int(RelTime("01:30")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'ILCTOACT', 'leg_end_station': 'N/A', 'ac_type': '-',
                                   'min_training_cnx_time': int(RelTime("01:45")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'PASSTOLIFUS', 'leg_end_station': 'N/A', 'ac_type': '-',
                                   'min_training_cnx_time': int(RelTime("01:10")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'PASSTOLIFUS', 'leg_end_station': 'N/A', 'ac_type': 'A3',
                                   'min_training_cnx_time': int(RelTime("01:20")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'PASSTOLIFUS', 'leg_end_station': 'N/A', 'ac_type': 'A4',
                                   'min_training_cnx_time': int(RelTime("01:20")), 'validfrom': validfrom,'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'PASSTOLIFUS', 'leg_end_station': 'N/A', 'ac_type': 'A5',
                                   'min_training_cnx_time': int(RelTime("01:20")), 'validfrom': validfrom,'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'PASSTOZFTT', 'leg_end_station': 'N/A', 'ac_type': '-',
                                   'min_training_cnx_time': int(RelTime("01:30")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'PASSTOZFTT CCQ A3-A4', 'leg_end_station': 'N/A', 'ac_type': 'A3',
                                   'min_training_cnx_time': int(RelTime("01:20")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'PASSTOZFTT CCQ A3-A4', 'leg_end_station': 'N/A', 'ac_type': 'A4',
                                   'min_training_cnx_time': int(RelTime("01:20")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'PASSTOZFTT CCQ A3-A4', 'leg_end_station': 'N/A', 'ac_type': 'A5',
                                   'min_training_cnx_time': int(RelTime("01:20")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'PASSTOZFTTX', 'leg_end_station': 'N/A', 'ac_type': 'A3',
                                   'min_training_cnx_time': int(RelTime("01:20")), 'validfrom': validfrom, 'validto': validto}))
    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'PASSTOZFTTX', 'leg_end_station': 'N/A', 'ac_type': 'A4',
                                   'min_training_cnx_time': int(RelTime("01:20")), 'validfrom': validfrom, 'validto': validto}))
    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'PASSTOZFTTX', 'leg_end_station': 'N/A', 'ac_type': 'A5',
                                   'min_training_cnx_time': int(RelTime("01:20")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'PASSTOZFTT TR & CCQ from A2', 'leg_end_station': 'N/A', 'ac_type': 'A3',
                                   'min_training_cnx_time': int(RelTime("02:05")), 'validfrom': validfrom, 'validto': validto}))
    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'PASSTOZFTT TR & CCQ from A2', 'leg_end_station': 'N/A', 'ac_type': 'A4',
                                   'min_training_cnx_time': int(RelTime("02:05")), 'validfrom': validfrom, 'validto': validto}))
    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'PASSTOZFTT TR & CCQ from A2', 'leg_end_station': 'N/A', 'ac_type': 'A5',
                                   'min_training_cnx_time': int(RelTime("02:05")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'PASSTOSUPERNUM', 'leg_end_station': 'N/A', 'ac_type': '-',
                                   'min_training_cnx_time': int(RelTime("01:20")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'PASSTOSCHOOLFLIGHT', 'leg_end_station': 'N/A', 'ac_type': '-',
                                   'min_training_cnx_time': int(RelTime("01:20")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'PASSTOFAMFLT', 'leg_end_station': 'N/A', 'ac_type': '-',
                                   'min_training_cnx_time': int(RelTime("01:20")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'LIFUSTOPASS', 'leg_end_station': 'N/A', 'ac_type': '-',
                                   'min_training_cnx_time': int(RelTime("01:15")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'SUPERNUMTOPASS', 'leg_end_station': 'N/A', 'ac_type': '-',
                                   'min_training_cnx_time': int(RelTime("01:15")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'SCHOOLFLIGHTTOPASS', 'leg_end_station': 'N/A', 'ac_type': '-',
                                   'min_training_cnx_time': int(RelTime("01:15")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'FAMFLTTOPASS', 'leg_end_station': 'N/A', 'ac_type': '-',
                                   'min_training_cnx_time': int(RelTime("01:15")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'LCTOLC', 'leg_end_station': 'N/A', 'ac_type': '-',
                                   'min_training_cnx_time': int(RelTime("02:10")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'ILCTOILC', 'leg_end_station': 'N/A', 'ac_type': '-',
                                   'min_training_cnx_time': int(RelTime("02:45")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'ILCTOLC', 'leg_end_station': 'N/A', 'ac_type': '-',
                                   'min_training_cnx_time': int(RelTime("02:45")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                  {'cnx_type': 'LCTOILC', 'leg_end_station': 'N/A', 'ac_type': '-',
                                   'min_training_cnx_time': int(RelTime("02:45")), 'validfrom': validfrom, 'validto': validto}))

    ops.append(fixrunner.createOp('cnx_time_training', 'N',
                                 {'cnx_type': 'UNKNOWN', 'leg_end_station': '-', 'ac_type': '-',
                                  'min_training_cnx_time': int(RelTime("24:00")), 'validfrom': validfrom, 'validto': validto}))

    return ops

fixit.program = 'skcms_2052_add_training_cnx_time.py (%s)' % __version__
if __name__ == '__main__':
    fixit()