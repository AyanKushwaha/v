
# -*- coding: latin-1 -*-
# [acosta:06/313@16:52] Redesign, added coding

"""
Norwegian salary system.
HTML format.
"""

from salary.fmt import HTMLFormatter

class NO_HTML(HTMLFormatter):
    class Headings:
        admcode   = 'Slag'
        amount    = 'Beløp'
        extartid  = 'Slag'
        extperkey = 'Extperkey'
        extsys    = 'Lønneskontor'
        firstdate = 'Første dato'
        lastdate  = 'Siste dato'
        note      = 'Kommentar'
        runid     = 'Løpenummer'
        starttime = 'Kjørelse dato'
        selector  = 'Utvalg'
        total     = 'Samlet'

# EOF
