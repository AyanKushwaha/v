"""
Common entry point for:

33.9 Master Crew List
"""

from report_sources.report_server.rs_if import add_reportprefix, argfix, default_destination, default_content_type

import carmusr.paxlst.crew_manifest as cm


@argfix
@add_reportprefix
def generate(*a, **k):
    """Create Master Crew List (incremental or full) in format suitable for
    Report Server, will result in list of text messages."""

    return_list = []

    try:
        if k.has_key('incremental'):
            # NOTE: the value of 'incremental' will be *string* "0" or "1"!
            incr = bool(int(k['incremental']))
        else:
            incr = True
    except:
        raise ValueError("generate(): The value of inparameter 'incremental' must be one of (0, 1, '0', '1', True, False).")

    if 'country' in k:
        country = k['country']
    else:
        country = 'US'

    if incr:
        func = cm.mcl
    else:
        func = cm.complete_mcl

    sa = cm.SITAAddresses(country)

    # Change func() to func(country) to enable other countries.
    for message in func():
        for recipient in sa.recipients:
            # Add SITA addresses to message
            return_list.append({
                'content': sa.add_recipient(recipient, message),
                'content-type': default_content_type,
                'destination': default_destination,
            })

    return return_list, True

