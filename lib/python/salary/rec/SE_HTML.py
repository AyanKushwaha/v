
# -*- coding: latin-1 -*-
# [acosta:06/313@16:52] Redesign, added coding

"""
Swedish salary system.
HTML format.
"""

from salary.fmt import HTMLFormatter

class SE_HTML(HTMLFormatter):
    class Headings:
        admcode   = 'Körningstyp'
        amount    = 'Belopp'
        extartid  = 'Slag'
        extperkey = 'Extperkey'
        extsys    = 'Lönekontor'
        firstdate = 'Första datum'
        lastdate  = 'Sista datum'
        note      = 'Kommentar'
        runid     = 'Löpnummer'
        starttime = 'Kördatum'
        selector  = 'Urval'
        total     = 'Totalsumma'

# EOF
