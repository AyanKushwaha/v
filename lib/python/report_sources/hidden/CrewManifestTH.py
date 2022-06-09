

"""
CR SASCMS-2318 - Crew Manifest TH

The Thai authorities demand that a Crew Manifest is delivered.

Similar to CN manifest, but visa information is left out.
"""

import report_sources.hidden.CrewManifestPDF as pdf

the_country = "TH"


# CrewManifestTH ========================================================={{{1
class CrewManifestTH(pdf.CrewManifestPDF):
    country = the_country
    show_visa = False


def reportSelectedFlight():
    return pdf.reportSelectedFlight(the_country)


bit = reportSelectedFlight


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    bit()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
