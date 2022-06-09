

"""
33.9 Crew Manifest CN

The Chinese authorities demand that a Crew Manifest is delivered as the flight
arrives in China.  For safety reasons the lists for the next four days are
sent to base every day.

When:
- Early in the morning on the day of departure.

How:
- An automated process, where the Crew Manifest is send in a mail to the SAS
  base (CPH, STO) and is printed there, to be signed by the Captain and having
  the SAS seal.  

Crew Manifest:
- All crew flying active or deadhead to China have to be present in the crew
  manifest.

Contents:
- Passport number, Full name, Nationality, Sex, Date of Birth, Occupation, Visa
  number, Document type.

Other information:
- All headings are written in English.
"""

import report_sources.hidden.CrewManifestPDF as pdf

the_country = "CN"


# CrewManifestCN ========================================================={{{1
class CrewManifestCN(pdf.CrewManifestPDF):
    country = the_country
    show_visa = True
    show_passport_expiry = True


def reportSelectedFlight():
    return pdf.reportSelectedFlight(the_country)


bit = reportSelectedFlight


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    bit()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
