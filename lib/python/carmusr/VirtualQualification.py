"""This module handles virtual qualifications, i.e. qualifications that are valid for multiple acquals"""

VIRTUAL_TO_REAL_MAP = {"AWB" : ["A3", "A4", "A5"]}
VIRTUAL_TO_REAL_US_AIRPORT_MAP = {"AWB" : ["A2", "A3", "A4", "A5"]}

def virtual_to_real_US_airport_quals(virtual):
    """Figure out which quals that are valid for "virtual" subtypes, e.g. AWB"""
    return VIRTUAL_TO_REAL_US_AIRPORT_MAP.get(virtual, [virtual])

def virtual_to_real_quals(virtual):
    """Figure out which quals that are valid for "virtual" subtypes, e.g. AWB"""
    return VIRTUAL_TO_REAL_MAP.get(virtual, [virtual])

def real_to_virtual_qual(real):
    """Figure out which qual that is the virtual equivalent of a real qual"""
    for virtual in VIRTUAL_TO_REAL_MAP.keys():
        if real in VIRTUAL_TO_REAL_MAP[virtual]:
            return virtual
    return real
