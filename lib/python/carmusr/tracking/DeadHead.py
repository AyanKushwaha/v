#

#
#
# Purpose: DeadHead is a wrapper to the crew complement menu
#          This is to make an update to the whole model instead of
#          just the studio model.
#
# Author:  David Kihlstrom
# Date:    2008-01-14
#

import Cui
import modelserver
import carmensystems.rave.api as R

import carmstd.cfhExtensions

import carmusr.tracking.Publish as Publish
import carmusr.tracking.TripTools as TripTools

from carmusr.Attributes import RemoveCrewFlightDutyAttr,SetCrewFlightDutyAttr
from carmstd.studio.area import promptPush
from utils.rave import RaveEvaluator
from AbsDate import AbsDate

def convertFromToDeadHead():
    """
    Change target leg from/to deadhead.
    Remove any overbooked trips connected to changed leg afterwards.
    
    """
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    sel = RaveEvaluator(area, Cui.LegMode,
                        leg_identifier='leg_identifier',
                        is_deadhead='leg.%is_deadhead%',
                        extra_seat="studio_config.%extra_seat%",
                        crew='crew.%id%',
                        udor='leg.%udor%',
                        fd='leg.%flight_descriptor%',
                        adep='leg.%start_station%',
                        is_skj_cc='crew.%is_homebase_skj% and crew.%is_cabin%'
                        )
    if sel.extra_seat:
        # Leg is already an extra seat; convert it to a deadhead
        Cui.CuiExtraSeatFromTo(Cui.gpc_info,
                               Cui.CUI_EXTRA_SEAT_FROM_TO_SILENT
                               | Cui.CUI_EXTRA_SEAT_FROM_TO_ALLOW_ILLEGAL)
    else:
        # Toggle flight between active and passive.
        Cui.CuiChangeToFromPassive(Cui.gpc_info, area, "OBJECT", 
                                   Cui.CUI_CHANGE_TO_FROM_SILENT
                                   | Cui.CUI_CHANGE_TO_FROM_FORCE)
        # If this was a dh, then remove the PRIVATE attribute, if it exists
        if sel.is_deadhead:
            RemoveCrewFlightDutyAttr(sel.crew, sel.udor, sel.fd, sel.adep, "PRIVATE")
        
    # Handling of JP CC overtime for legs that originally were active duty
    if sel.is_skj_cc:
        if sel.is_deadhead:
            RemoveCrewFlightDutyAttr(sel.crew, sel.udor, sel.fd, sel.adep, "JP_OVERTIME")
        else:
            SetCrewFlightDutyAttr(sel.crew, sel.udor, sel.fd, sel.adep, "JP_OVERTIME")

    # Clean booked values of trips where focused leg was involved.
    TripTools.tripClean(area, [sel.leg_identifier])

    return 0
    
def convertFromToPrivate():
    """
    Menu function that converts a deadhead to/from Private.
    Assumes current selection is a deadhead flight on a roster.
    """
    
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    sel = RaveEvaluator(area, Cui.LegMode,
                        crew='crew.%id%',
                        udor='leg.%udor%',
                        fd='leg.%flight_descriptor%',
                        adep='leg.%start_station%',
                        rdor='leg.%rdor%',
                        sobt='leg.%activity_scheduled_start_time_UTC%',
                        )
                            
    # If already private, just toggle the PRIVATE attribute off, and return.
    if RemoveCrewFlightDutyAttr(sel.crew, sel.udor, sel.fd, sel.adep, "PRIVATE") == 0:
        print "convertFromToPrivate: Removed PRIVATE attribute for", sel
        promptPush("Changed leg from PRIVATE")
        return 0

    # Find out what deadhead flights have been removed from the published roster.
    diffs_per_crew = Cui.CuiDiffPublishedRoster(Cui.gpc_info, [sel.crew],
        int(sel.rdor) - 24*60, int(sel.rdor) + 24*60, Publish.TRACKING_PUBLISHED_TYPE)
    # A removed flight has both a 'crew_flight_duty' and a 'flight_leg'
    # component. Merge them, and then eliminate the non-DH:s.
    removed_flights = {}
    for chg in diffs_per_crew.values()[0]: # (Only one crew in this diffset)
        typ,tab,key = chg.getType(), chg.getTableName(), str(chg.getEntityI())
        if typ == modelserver.Change.REMOVED and 'flight' in tab:
            if tab == 'crew_flight_duty':
                key = key[:-6] # strip crew id part of key
                removed_flights[key] = {
                    'udor': key.split('+')[0],
                    'fd': key.split('+')[1],
                    'adep': key.split('+')[2]}
            for attr,org,rev in chg:
                removed_flights[key][attr] = org
                
    removed_deadheads = [rf for rf in removed_flights.values() if str(rf.get('pos')) == 'DH']
    # Basic check that that at least one removed dead head was found.        
    if len(removed_deadheads) == 0:
        carmstd.cfhExtensions.show(
            "Cannot convert to Private.\n\n"
            "To be able to convert to Private, the deadhead has to have been changed \n"
	    "since the last save/publish",
            title="Not possible to convert to Private")
        promptPush("Function cancelled")
        return 1    
        
    # We need to find the dead head that we are replacing with a PRIVATE dead head
    # This is done by finding the removed dead head where the difference of the 
    # departing time is closest to the new PRIVATE dead head.
    original_deadhead = min(removed_deadheads, key = lambda x: abs(sel.sobt - x['sobt']))

    # Make a sanity check that the new and original dead head is actually departing on the
    # same day                    
    if AbsDate(original_deadhead['udor']) != AbsDate(sel.udor):
        if not carmstd.cfhExtensions.confirm("The original deadhead (%s) and " % (AbsDate(original_deadhead['udor'])) +
                                             "the new deadhead (%s) have " % (AbsDate(sel.udor)) +
                                             "different udors's.\n\n" +
                                             "Do you want to continue?",
                                             title="Warning"):
            promptPush("Function cancelled")
            return 1    
        
    # Create a PRIVATE attribute with values from removed dead head:
    # - abs = Scheduled departure time UTC (AbsTime)
    # - rel = Scheduled block time (RelTime)
    # - str = flight_leg-key + ades, e.g. "20091119+SK 001417 +ARN+CPH"    
    a = original_deadhead['sobt']
    r = original_deadhead['sibt'] - original_deadhead['sobt']
    
    orgiginal_info = "%s+%s+%s+%s" % (original_deadhead['udor'], original_deadhead['fd'], original_deadhead['adep'], original_deadhead['ades'])
    new_info = "%s+%s+%s" % (sel.udor, sel.fd, sel.adep)
    print "convertFromToPrivate: Converting", new_info, "to PRIVATE with values", a, r, orgiginal_info
    SetCrewFlightDutyAttr(
        sel.crew, sel.udor, sel.fd, sel.adep, "PRIVATE", abs=a, rel=r, str=orgiginal_info)

    promptPush("Changed leg to PRIVATE")        
    return 0
