'''

Basic functions for in OTS considered TranslationTypes.

Created on 4 Aug 2016

@author: stefan
'''

from carmensystems.basics.l10n import translation_type


def homebase_id2gui(homebase):
    return translation_type.id2gui("homebaseCodes", homebase)


def homebase_gui2id(homebase_in_gui):
    return translation_type.gui2id("homebaseCodes", homebase_in_gui)


def station_id2gui(airport):
    return translation_type.id2gui("airportCodes", airport)


def station_gui2id(airport_in_gui):
    return translation_type.gui2id("airportCodes", airport_in_gui)
