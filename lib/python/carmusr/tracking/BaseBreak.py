#

#
# Purpose:
#   Set or remove a Base Break on a crew flight duty.
# Interface:
#   Two functions serving as "Assignment Object" menu entry points:
#   BaseBreak.set() - Sets a Base Break on the current roster leg.
#       Cancels any related passive and hotel bookings.
#   BaseBreak.remove() - Removes any Base Break on the current roster leg.
#       No bookings are currently updated.
# Created by:
#   Stefan Hansson, 25 April 2007
# Major changes:
#   stefanh, 19Sep2007:
#       - Allow breaks on non-flight legs.
#       - Legs can have breaks both before and after.

# imports ================================================================{{{1

import Cui
import Gui
import logging
import AbsTime

from tm import TM
from modelserver import EntityError

# logging ================================================================{{{1

log = logging.getLogger('basebreak.modify')
log.setLevel(logging.DEBUG)

# menu entries ==========================================================={{{1

def set(beforeOrAfter):
    bb =  BaseBreak()
    log.debug("BaseBreak::set(%s)" % beforeOrAfter)
    bb.set({'BEFORE':True,'AFTER':False}[beforeOrAfter.upper()])
    return 0

def remove(beforeOrAfter):
    bb =  BaseBreak()
    log.debug("BaseBreak::remove(%s)" % beforeOrAfter)
    bb.remove({'BEFORE':True,'AFTER':False}[beforeOrAfter.upper()])
    return 0

# classes ================================================================{{{1

class BaseBreak(object):
    """
    Handles the setting and removal of Base Breaks.
    Operates on a specific leg object on a roster in Studio.
    """
    
    def __init__(self, crew=None, is_flight_duty=None, carrier=None, flight_nr=None, tcode=None, \
                 origsuffix=None, st=None, start_station=None, has_before=None, has_after=None):
        """
        Non-specified arguments are calculated via Rave,
          operating on the current leg selection in Studio.
        """
        Cui.CuiSyncModels(Cui.gpc_info, Cui.CUI_SAVE_SILENT)
        self.crew = crew or TM.crew[(self._rstring("crew.%id%"),)]
        
        if is_flight_duty is None:
            self.is_flight_duty = self._rbool("base_break.%is_flight_duty%")
        else:
            self.is_flight_duty = is_flight_duty

        if self.is_flight_duty:
            self.carrier = carrier or self._rstring("base_break.%flight_carrier%")
            self.flight_nr = flight_nr or self._rint("base_break.%flight_nr%")
            self.origsuffix = origsuffix or self._rstring("base_break.%origsuffix%")
        else:
            self.tcode = tcode or self._rstring("base_break.%tcode%")
        self.st = st or AbsTime.AbsTime(self._rabstime("base_break.%st%"))
        self.start_station = start_station or self._rstring("base_break.%start_station%")
        
        if has_before is None:
            self.has_before = self._rbool("base_break.%is_break_before%")
        else:
            self.has_before = has_before
        if has_after is None:
            self.has_after = self._rbool("base_break.%is_break_after%")
        else:
            self.has_after = has_after

    def _getBaseBreakKey(self, isBefore):
        """
        Returns the base break identifiers
        """
        print self.crew
        print self.st

        if self.is_flight_duty: 
            return (self.crew, self.carrier, self.flight_nr, "-", self.origsuffix, self.st, \
                    self.start_station, isBefore)
        else:
            return (self.crew, "-", -1, self.tcode, "-", self.st, self.start_station, isBefore)
            
    def _canBreak(self, isBefore):
        """
        Check if it is allowed to create a base break for the
          currently selected leg in Studio (Deadhead or non-deadhead).
        """
        if isBefore:
            return self._rbool("base_break.%can_break_before%")
        else:
            return self._rbool("base_break.%can_break_after%")
    
    def _canBreakDeadhead(self, isBefore):
        """
        Check if it is allowed to create a base break for the
          currently selected leg in Studio (deadhead).
        """
        if isBefore:
            return self._rbool("base_break.%can_break_deadhead_before%")
        else:
            return self._rbool("base_break.%can_break_deadhead_after%")
    
    def _canBreakOther(self, isBefore):
        """
        Check if it is allowed to create a base break for the
          currently selected leg in Studio (Non-deadhead).
        """
        if isBefore:
            return self._rbool("base_break.%can_break_other_before%")
        else:
            return self._rbool("base_break.%can_break_other_after%")
    
    def _hasBreak(self, isBefore):
        """
        Check if this BaseBreak instance covers a leg with an existing break.
        """
        if isBefore:
            return self.has_before
        else:
            return self.has_after
            
    def set(self, isBefore):
        """
        Create a base break on the currently selected leg in Studio.
        A deadhead leg corresponding to the break
          (before or after the leg) must exist, and is removed.
        """
        assert not self._hasBreak(isBefore), "Attempt to create a base break that already exists."
        assert self._canBreak(isBefore), "Attempt to set an invalid base break."
        if self._canBreakDeadhead(isBefore):
            if isBefore:
                deadhead = self._rint("base_break.%deadhead_leg_identifier_before%")
                remotestation = self._rstring("base_break.%deadhead_depstn_before%")
            else:
                deadhead = self._rint("base_break.%deadhead_leg_identifier_after%")
                remotestation = self._rstring("base_break.%deadhead_arrstn_after%")
            assert deadhead and remotestation, "Can't identify the deadhead to remove."
            try:
                TM.crew_base_break[(self._getBaseBreakKey(isBefore))].remove()
                log.debug("BaseBreak::BaseBreak::set() Removed obsolete crew_base_break entry")
            except:
                pass
            basebreak = TM.crew_base_break.create((self._getBaseBreakKey(isBefore)))
                
            basebreak.remotestation = remotestation
            Cui.CuiReloadTable("crew_base_break")
            if isBefore:
                self.has_before = True
            else:
                self.has_after = True
            Cui.CuiSetSelectionObject(Cui.gpc_info, Cui.CuiWhichArea, Cui.LegMode, str(deadhead))
            Cui.CuiRemoveLeg(Cui.gpc_info)
            self._updateStudio()
            
        elif self._canBreakOther(isBefore):
            if isBefore:
                remotestation = self._rstring("base_break.%other_arrstn_before%")
            else:
                remotestation = self._rstring("base_break.%other_depstn_after%")
            assert remotestation, "Can't identify the remote station."
            try:
                TM.crew_base_break[(self._getBaseBreakKey(isBefore))].remove()
                log.debug("BaseBreak::BaseBreak::set() Removed obsolete crew_base_break entry")
            except:
                pass
            basebreak = TM.crew_base_break.create((self._getBaseBreakKey(isBefore)))
                
            basebreak.remotestation = remotestation
            Cui.CuiReloadTable("crew_base_break")
            if isBefore:
                self.has_before = True
            else:
                self.has_after = True
            self._updateStudio()
        
    def remove(self, isBefore):
        """
        Remove an existing base break from the currently selected leg in Studio.
        """
        assert self._hasBreak(isBefore), "Attempt to remove a non-existing base break."
        if isBefore:
            remotestation = self._rstring("base_break.%depstn_before%")
        else:
            remotestation = self._rstring("base_break.%arrstn_after%")
        basebreak = TM.crew_base_break[(self._getBaseBreakKey(isBefore))]
        basebreak.remove()
        Cui.CuiReloadTable("crew_base_break")
        if isBefore:
            self.has_before = False
        else:
            self.has_after = False
        self._updateStudio()
    
    def removeAny(self):
        """
        Remove any crew_base_break entries for a specific leg.
        Use to tidy up the table when a leg is deassigned from a roster.
        
        The leg to break does not have to be the current selection in Studio,
          provided all arguments were given when creating this BaseBreak instance.
        """
        if self.has_before:
            log.debug("BaseBreak::removeAny removes a before-break")
            TM.crew_base_break[(self._getBaseBreakKey(True))].remove()
            Cui.CuiReloadTable("crew_base_break")
        if self.has_after:
            log.debug("BaseBreak::removeAny removes an after-break")
            TM.crew_base_break[(self._getBaseBreakKey(False))].remove()
            Cui.CuiReloadTable("crew_base_break")
        
    def _updateStudio():
        """Force studio to update the Gui."""
        Gui.GuiCallListener(Gui.RefreshListener, "parametersChanged")
        Gui.GuiCallListener(Gui.ActionListener)
    _updateStudio = staticmethod(_updateStudio)
    
    def _rstring(expr):
        return Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object", expr)
    _rstring = staticmethod(_rstring)
    
    def _rbool(expr):
        return Cui.CuiCrcEvalBool(Cui.gpc_info, Cui.CuiWhichArea, "object", expr)
    _rbool = staticmethod(_rbool)
    
    def _rint(expr):
        return Cui.CuiCrcEvalInt(Cui.gpc_info, Cui.CuiWhichArea, "object", expr)
    _rint = staticmethod(_rint)

    def _rabstime(expr):
        return Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiWhichArea, "object", expr)
    _rabstime = staticmethod(_rabstime)
