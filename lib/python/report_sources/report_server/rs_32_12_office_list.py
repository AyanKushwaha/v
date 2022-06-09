

"""
32.12 Office List

See ../../crewlists/office_list.py for details.
"""

from report_sources.report_server.rs_if import add_reportprefix, argfix, default_destination
from crewlists.office_list import run


@argfix
@add_reportprefix
def generate(*a, **k):
    """Create a number of Office lists in PDF. See crewlists.office_list for
    details.

    Input parameters:
        runidx  -   Optional. Possibility to only generate a subset of the
                    officelist reports by specifying a string of comma
                    separated indices corresponding to reports in order
                    of execution. E.g. "5,6"
    """

    try:
        runidx = [int(x) for x in k['runidx'].split(',')]
    except:
        runidx = []
    return [{
        'content-location': message,
        'content-type': "application/pdf",
        'destination': default_destination,
    } for message in run(st=k.get('st'), et=k.get('et'), runidx=runidx)], False


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    # Just for basic tests
    print generate()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
