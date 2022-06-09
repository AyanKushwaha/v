

"""
Report Server interface to Passive Bookings
"""

import carmensystems.rave.api as R

from AbsTime import AbsTime
from RelTime import RelTime
from carmensystems.dig.framework.utils import convertToBoolean
from passive.passive_bookings import initial_bookings, update_bookings
from report_sources.report_server.rs_if import argfix


@argfix
def generate(*a, **d):
    files = []

    date_param = d.get('date', None)
    if date_param is None:
        from_date, = R.eval('fundamental.%now%')
    else:
        from_date = AbsTime(date_param)
    
    if convertToBoolean(d.get('bookingUpdate', 'False')):
        # Run update from now (or given date) and 10 days ahead
        to_date = from_date + RelTime(11, 0, 0)
        files = update_bookings(from_date, to_date, 
                modified_crew=[v for (k, v) in d.iteritems() if 'crew' in k])
    else:
        # Run from now + 10d (or given date + 0d) and one day ahead.
        if date_param is None:
            from_date += RelTime(10, 0, 0)
        to_date = from_date + RelTime(1, 0, 0)
        files = initial_bookings(from_date, to_date)

    reports = []
    for fileName in files:
        reports.append(
        {
            'content-location': fileName,
            'content-type': 'text/plain',
            'destination': [('default', {})],
        })

    return reports, True

# eof
