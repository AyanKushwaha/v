"""
****Important: Any changes made into this module should also be done in
$CARMUSR/lib/python/salary/reasoncodes.py in JMP4 Carmusr****

Store reason codes in one place.

Note that reason codes are stored persistently in the database, so from a
change of a reason code follows the need to convert existing data.
"""

__all__ = ['REASONCODES', 'in_accounts', 'out_accounts']
__version__ = "$Revision$"

REASONCODES = {
    'BOUGHT': 'BOUGHT',
    'SOLD': 'SOLD',

    'IN_CONV': 'IN Conversion',
    'OUT_CONV': 'OUT Conversion',

    'IN_CORR': 'IN Correction',
    'OUT_CORR': 'OUT Correction',

    'IN_DEFAULT': 'IN',
    'OUT_DEFAULT': 'OUT',

    'IN_ENTITLEMENT': 'IN Entitlement',   #CMP
    'OUT_ENTITLEMENT': 'OUT Entitlement', #CMP

    'IN_REDUCTION': 'IN Reduction',       #CMP
    'OUT_REDUCTION': 'OUT Reduction',     #CMP

    'IN_ROUND': 'IN Rounded',
    'OUT_ROUND': 'OUT Rounded',

    'IN_ROSTER': 'IN Roster',
    'OUT_ROSTER': 'OUT Roster',

    'IN_SAVED':'IN Saved',
    'OUT_SAVED': 'OUT Saved',

    'IN_TRANSFER': 'IN Transfer',         #CMP
    'OUT_TRANSFER': 'OUT Transfer',       #CMP

    'IN_UNSAVED': 'IN Unsaved',
    'OUT_UNSAVED': 'OUT Unsaved',

    'IN_UNUSED': 'IN Unused',             #CMP
    'OUT_UNUSED': 'OUT Unused',           #CMP

    'IN_ADMIN': 'IN Administrative',
    'IN_FLY_VAF': 'IN Flying on VA/F day',
    'IN_IRR': 'IN Irregularity',
    'IN_MAN': 'IN Manual',
    'IN_MEET': 'IN Meeting',
    'IN_MISC': 'IN Miscellaneous',
    'IN_OT': 'IN Overtime',

    'PAY_CORR': 'IN Payment Correction',
    'PAY': 'OUT Payment',

    'IN_REDUCTION_ROUNDING': 'IN Reduction Rounding',
    'OUT_REDUCTION_ROUNDING': 'OUT Reduction Rounding',
}


in_accounts = [v for v in REASONCODES.itervalues() if v.startswith('IN')]
out_accounts = [v for v in REASONCODES.itervalues() if v.startswith('OUT')]
