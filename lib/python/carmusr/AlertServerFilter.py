#

#
"""
AlertServerFilter

This module is used to set the Alert Server Filter
The AlertServerLoadFilter Resource must point to this module

"""

import AbsTime
import RelTime
from tm import TM

def setAlertServerFilter(current_day, period_start, period_end):
    """
    Sets the filters for the Servers
    Only used if AlertServerLoadFilter Resource is set
    """
    dbPeriodStart = AbsTime.AbsTime(period_start)
    dbPeriodEnd = AbsTime.AbsTime(period_end) + RelTime.RelTime(24*60-1)
    threeyrsbefstart = dbPeriodStart - RelTime.RelTime(3*366*24*60)
    oneyrbefstart = dbPeriodStart - RelTime.RelTime(366*24*60)
    threemonthsbefstart = dbPeriodStart - RelTime.RelTime(3*30*1440)
    threemonthsafterend = dbPeriodEnd + RelTime.RelTime(3*30*1440)
    max_trip_length = 5
    max_number_of_days_with_optional_variant_deadheads_before_trip = 1
    trip_start = dbPeriodStart - RelTime.RelTime(max_trip_length*1440)
    trip_end = dbPeriodEnd + RelTime.RelTime(max_number_of_days_with_optional_variant_deadheads_before_trip*1440)
    leg_start = trip_start - RelTime.RelTime(max_number_of_days_with_optional_variant_deadheads_before_trip*1440)
    leg_end = trip_end + RelTime.RelTime(max_trip_length*1440)

    TM.addSelection("period", "start", str(dbPeriodStart)[0:9])
    TM.addSelection("period", "end", str(dbPeriodEnd)[0:9])
    TM.addSelection("period", "start_time", str(dbPeriodStart))
    TM.addSelection("period", "end_time", str(dbPeriodEnd))
    TM.addSelection("period", "threeyrsbefstart", str(threeyrsbefstart))
    TM.addSelection("period", "oneyrbefstart", str(oneyrbefstart))
    TM.addSelection("period", "threemonthsbefstart", str(threemonthsbefstart))
    TM.addSelection("period", "threemonthsafterend", str(threemonthsafterend))
    TM.addSelection("period", "trip_start", str(trip_start))
    TM.addSelection("period", "trip_end", str(trip_end))
    TM.addSelection("period", "leg_start", str(leg_start))
    TM.addSelection("period", "leg_end", str(leg_end))

    return 0
