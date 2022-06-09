

"""
CR SASCMS-2372

PDF report with Flight Crew Manifest (FCM) for Japan (JP).
"""

import report_sources.hidden.CrewManifestPDF as pdf

the_country = "JP"


# CrewManifestJP ========================================================={{{1
class CrewManifestJP(pdf.CrewManifestPDF):
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
