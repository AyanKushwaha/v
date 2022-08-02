
"""
Common entry point for:

SKCMS-3051 Crew Manifest IE - unwanted files to be placed in separate directory
"""

from report_sources.report_server.rs_if import argfix, default_destination, default_content_type, fallback

import carmusr.paxlst.crew_manifest as cm
import os

@argfix
def generate(*a, **k):
    try:
        try:
            # NOTE: We remove any FCMERROR attribute on the flight leg first.
            # If manifest completes, then this attribute will be removed and
            # errors are cleared, if instead the manifest fails, then we don't
            # care about model server deltas, instead the FCM error attribute
            # is set (by 'fallback()').
            cm.remove_fcmerror(k['fd'], k['udor'], k['adep'])
        except:
            print "Could not remove 'flight_leg_attr' (fd=%(fd)s, udor=%(udor)s, adep=%(adep)s)." % k
        return _generate(**k)
    except Exception, e:
        # In case something went wrong, DIG will set the flight_leg_attr
        return [fallback(e, *a, **k)], True


def _generate(fd=None, origsuffix='', udor=None, adep=None, country=None, fileName=None):
    return_list = []
    dir = os.path.join(os.environ['CARMUSR'], 'current_carmdata/REPORTS/EXPORT/ARR_NOT_REQ/')
    for message in cm.crewlist(fd=fd, udor=udor, adep=adep, country=country):
        # Will result in a list of text messages.
        return_list.append({
            'content':  message,
            'content-type': default_content_type,
            'destination': [('ARR_NOT_REQ',{})],
            'filename': fileName,
        })
    return return_list, True


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
