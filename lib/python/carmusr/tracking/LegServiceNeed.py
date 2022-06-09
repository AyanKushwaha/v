#

#
# Purpose:
#   Reduce or reset a service need exception on a flight leg.
# Interface:
#   Two functions serving as "Assignment Object" and "Trip Object"
#       menu entry points, operating on crew position "AS" or "AH":
#   LegServiceNeed.reduce(pos) - Reduces service need by 1.
#   LegServiceNeed.reset(pos) - Resets service need to default.
# Created by:
#   Stefan Hansson, 27 April 2007
# Major changes:
#   Stefan Hansson, 04 June 2007: Support operation from roster view.
#

# imports ================================================================{{{1

import traceback

import Csl
import Cui
import Gui
import logging

import carmusr.tracking.TripTools as TripTools

from AbsTime import AbsTime
from tm import TM

# logging ================================================================{{{1

log = logging.getLogger('service_need')
log.setLevel(logging.DEBUG)

# menu entries ==========================================================={{{1

def reduce(pos):
    log.debug("LegServiceNeed::reduce(%s)" % pos)
    LegServiceNeed(pos).reduce()
    return 0

def move(pos, to_pos):
    log.debug('LegServiceNeed::move("%s","%s")' % (pos, to_pos))
    LegServiceNeed(to_pos).increase_for_move()
    LegServiceNeed(pos).reduce()
    return 0

def reset(pos):
    log.debug("LegServiceNeed::reset(%s)" % pos)
    LegServiceNeed(pos).reset()
    return 0

def reset_all():
    log.debug("LegServiceNeed::reset_all()")
    LegServiceNeed("AS").reset()
    LegServiceNeed("AH").reset()
    return 0

# classes ================================================================{{{1

class LegServiceNeed(object):
    """
    Handles service need exceptions on flight legs.
    Operates on marked legs in the current window.
    """
    
    def __init__(self, pos):
        """
        Extract rave values regarding marked legs (the legs on which the
        exception is to be applied).
        
        Assumes that CuiWhichArea is in either Roster or Trip mode,
        and that 'pos' is either "AS" or "AH".
        """
        
        # Check position and window mode.
        
        assert pos in ("AS", "AH"), "Only positions allowed are AS and AH"
        self.pos = ((pos == "AS") and 6) or 7
        self.other_pos = ((pos == "AS") and 7) or 6
        
        self.workArea = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        try:
            Cui.CuiCheckAreaMode(Cui.gpc_info, self.workArea, Cui.CrrMode)
            self.isTripMode = True
        except:
            self.isTripMode = False

        # Get info for unique marked legs that are possible to change need on.
        # (We want unique legs, otherwise we'd change the need more than once.)
        
        self.flight_legs = {}
        for leg_id in Cui.CuiGetLegs(Cui.gpc_info, self.workArea, "marked"):
            Cui.CuiSetSelectionObject(Cui.gpc_info, self.workArea, Cui.LegMode, str(leg_id))
            if not self._rbool("crg_crew_pos.%any_need_to_change%"):
                continue
            key = (self._rabstime("leg.%udor%"),
                   self._rstring("leg.%flight_descriptor%"),
                   TM.airport[(self._rstring("departure_airport_name"),)])
            if not key in self.flight_legs:
                self.flight_legs[key] = {
                    "id":
                        leg_id,
                    "booked": self._rint(
                        "crew_pos.%%leg_booked_pos%%(%d)" % self.pos), 
                    "rostered": self._rint(
                        "crg_crew_pos.%%leg_rostered_pos%%(%d)" % self.pos),
                    "service_need_basic": self._rint(
                        "crew_pos.%%service_need_raw_in_pos%%(%d)" % self.pos),
                    "service_need": self._rint(
                        "crew_pos.%%service_need_in_pos%%(%d)" % self.pos),
                    "service_need_other": self._rint(
                        "crew_pos.%%service_need_in_pos%%(%d)" % self.other_pos),
                    }
        
    def reduce(self):
        """
        Reduce service need for all marked legs in the current trip,
        by creating or updating crew_need_exception data for each of the legs.
        Update studio objects if needed.
        """
        if not self.flight_legs:
            return
            
        # Reduce need (= create exception) for all marked legs, if possible.
        for key, leg in self.flight_legs.items():
            # Only if remaining need>0.
            if leg["service_need"] > 0:
                cne_pos = self._getCneTabInfo(key)
                # If no previous exception, init to default service need.
                if cne_pos[self.pos] < 0:
                   cne_pos[self.pos] = leg["service_need_basic"]
                # Reduce the exception need (reset if reduced to basic).
                cne_pos[self.pos] = max(0, cne_pos[self.pos] - 1)
                if cne_pos[self.pos] == leg["service_need_basic"]:
                   cne_pos[self.pos] = -1 
                self._saveCneTabInfo(cne_pos)
        
        Cui.CuiReloadTable("crew_need_exception")
        Cui.gpc_reset_required_cc(Cui.gpc_info) # Recalculate Crew Need
        self._updateStudio()
        self._cleanTrips()
        
    def increase_for_move(self):
        """
        Increase service need for all marked legs in the current trip,
        by creating or updating crew_need_exception data for each of the legs.
        This is done as part of a "Move AS/AH to AH/AS" operation, and it will
        always be followed by a LegServiceNeed.reduce() for the other position.
        (See menu-entry function move() above.)
        """
        if not self.flight_legs:
            return 
            
        # Increase need (=create exception) for all marked legs, if feasible
        for key,leg in self.flight_legs.items():
            # Only if remaining need>0 for the move-from pos.
            if leg["service_need_other"] > 0:
                cne_pos = self._getCneTabInfo(key)
                # If no previous exception, init to default service need.
                if cne_pos[self.pos] < 0:
                   cne_pos[self.pos] = leg["service_need_basic"]
                # Increase the exception need (reset if increased to basic).
                cne_pos[self.pos] = cne_pos[self.pos] + 1
                if cne_pos[self.pos] == leg["service_need_basic"]:
                   cne_pos[self.pos] = -1 
                self._saveCneTabInfo(cne_pos)
        
        Cui.CuiReloadTable("crew_need_exception")
        Cui.gpc_reset_required_cc(Cui.gpc_info) # Recalculate Crew Need
        self._cleanTrips()
          
    def reset(self):
        """
        Reset service need to default for all marked legs in the current trip,
        by updating or removing crew_need_exception data for each of the legs.
        """
        if not self.flight_legs:
            return
            
        # Remove need exception for all marked legs, if possible.
        for key,leg in self.flight_legs.items():
            if leg["service_need"] >= 0:
                cne_pos = self._getCneTabInfo(key)
                cne_pos[self.pos] = -1
                self._saveCneTabInfo(cne_pos)
        Cui.CuiReloadTable("crew_need_exception")
        Cui.gpc_reset_required_cc(Cui.gpc_info) # Recalculate Crew Need
        self._updateStudio()
        self._cleanTrips()
    
    # Helpers (rave variable getters)

    def _rstring(self,expr):
        return Cui.CuiCrcEvalString(Cui.gpc_info, self.workArea, "object", expr)
    def _rbool(self,expr):
        return Cui.CuiCrcEvalBool(Cui.gpc_info, self.workArea, "object", expr)
    def _rint(self,expr):
        return Cui.CuiCrcEvalInt(Cui.gpc_info, self.workArea, "object", expr)
    def _rabstime(self,expr):
        return AbsTime(
            Cui.CuiCrcEvalAbstime(Cui.gpc_info, self.workArea, "object", expr))

    # Access to crew_need_exception (cne) table.
    
    def _getCneTabInfo(self, flight_key):
        """
        Get, into self, crew_need_exception data regarding current studio leg.
        """
        flight_leg = TM.flight_leg[flight_key]
        try:
            self.cnetab_entry = TM.crew_need_exception[(flight_leg,)]
            # If someone entered a void value via the Table Editor...
            if self.cnetab_entry.pos6 is None: self.cnetab_entry.pos6 = -1
            if self.cnetab_entry.pos7 is None: self.cnetab_entry.pos7 = -1
        except:
            self.cnetab_entry = TM.crew_need_exception.create((flight_leg,))
            self.cnetab_entry.pos6 = -1 # -1 means no exception, and >= 0
            self.cnetab_entry.pos7 = -1 #  means exception from basic service need.
            
        return {6: self.cnetab_entry.pos6, 7: self.cnetab_entry.pos7}
        
    def _saveCneTabInfo(self, cne_pos):
        """
        Save crew_need_exception data regarding a leg.
        """
        if cne_pos[6] < 0 and cne_pos[7] < 0:
            self.cnetab_entry.remove()
        else:
            self.cnetab_entry.pos6 = cne_pos[6]
            self.cnetab_entry.pos7 = cne_pos[7]
    
    # Studio interfacing.
    
    def _updateStudio(self):
        """
        Force studio to update the Gui.
        """
        Gui.GuiCallListener(Gui.RefreshListener, "parametersChanged")
        Gui.GuiCallListener(Gui.ActionListener)

    def _cleanTrips(self):
        """
        Remove overbooked trips.
        """

        # Get all marked legs from the object.
        marked_leg_ids = [leg['id'] for leg in self.flight_legs.values()]

        # Call the trip cleaner
        TripTools.tripClean(self.workArea, marked_leg_ids)

