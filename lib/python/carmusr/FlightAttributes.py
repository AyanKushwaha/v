"""
 $Header$

 A module for setting attributes on assigned legs

 Contains:

 0. Imports and constants
 1. Class definition for the form to display
 2. The main functions called by the user
 3. Helper functions called by the main functions


 Created:   January 2007
 By:        Erik Gustafsson, Jeppesen
"""

################################################################################
#
# Section 0: Imports and constants
#
################################################################################

import Attributes
import os
import tempfile
import Cui
import Cfh
import Errlog
import carmensystems.rave.api as R
from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator
import carmstd.cfhExtensions as cfhExtensions
import carmusr.HelperFunctions as HF
import carmusr.modcrew as modcrew

MODULE = "FlightAttributes"
RANGES = ["Clicked leg only","Entire trip","All marked"]
(LEG,TRIP,MARKED) = range(3)
RANGES_STRING = ";"+";".join(RANGES)
# The default value should match what's in the rave code
DEFAULT_VALUE = "NONE"

################################################################################
#
# Section 1: Class definition for the form to display
#
################################################################################

class FlightAttributesForm(Cfh.Box):
    """
    A class for the flight attributes form.

    Builds and displays the correct form and implements a function that returns
    the values of the form.
    """
    def __init__(self, oldAttribute, deadhead, availableAttributes, rangeOption,
                 *args):
        """
        Initializes the form with a behaviour dependent on whether it's called
        on a deadhead or from the assignWithAttribute function. Uses the old
        attribute as default.
        """
        Cfh.Box.__init__(self, *args)
        self.deadhead = deadhead
        self.rangeOption = rangeOption
        # If we're called on a deadhead the standard attributes doesn't apply and
        # the behaviour should be boolean instead of string.
        if deadhead:
            if (oldAttribute == DEFAULT_VALUE):
                initVal = 0
            else:
                initVal = 1
            self.setAttribute = Cfh.Toggle(self,"ATTRIBUTE",initVal)
        else:
            available_attrs = ";".join(availableAttributes)
            self.valid_codes = ";"+ DEFAULT_VALUE + ";"+ available_attrs
            self.setAttribute = Cfh.String(self,"ATTRIBUTE",20,oldAttribute)
            self.setAttribute.setMenuOnly(True)
            self.setAttribute.setMenuString(self.valid_codes)
            # The range option is available on active, already assigned legs.
            # The default is trip.
            if rangeOption:
                self.range = Cfh.String(self,"RANGE",20,RANGES[LEG])
                self.range.setMenuOnly(True)
                self.range.setMenuString(RANGES_STRING)            
        self.setAttribute.setMandatory(True)
        # OK, CANCEL and RESET buttons.
        self.ok = Cfh.Done(self,"B_OK")
        self.quit = Cfh.Cancel(self,"B_CANCEL")
        self.reset = Cfh.Reset(self, "B_RESET") 
        # Creating the form.
        form_layout = """
FORM;FLIGHTATTRIBUTES_FORM;`Set flight attributes`"""
        if deadhead:
            form_layout += """
LABEL;`Private`
COLUMN;
FIELD;ATTRIBUTE;
"""
        elif rangeOption:
            # If the clicked leg isn't a deadhead we should have the option to
            # set the attribute for various ranges.
            form_layout += """
LABEL;`Attribute`
LABEL;`Range`
COLUMN;
FIELD;ATTRIBUTE;
FIELD;RANGE;
"""
        else:
            # When we assign a trip with an attribute we don't set a user
            # specified range.
            form_layout += """
LABEL;`Attribute`
COLUMN;
FIELD;ATTRIBUTE;
"""
        form_layout += """
BUTTON;B_OK;`Ok`;`_Ok`
BUTTON;B_CANCEL;`Cancel`;`_Cancel`
BUTTON;B_RESET;`Reset`;`_Reset`
"""
        attributes_form_file = tempfile.mktemp()
        f = open(attributes_form_file,"w")
        f.write(form_layout)
        f.close()
        self.load(attributes_form_file)
        os.unlink(attributes_form_file)
        self.show(1)

    def getValues(self, verbose=False):
        """
        Returns the values in the form as a tuple.
        """
        FUNK = MODULE + "::FlightAttributesForm:getValues: "
        if self.loop() == Cfh.CfhOk:
            if self.deadhead:
                # For deadheads the range is always leg only.
                int_range = LEG
                # We convert the boolean back to string.
                if self.setAttribute.valof():
                    str_attribute = "PRIVATE"
                else:
                    str_attribute = DEFAULT_VALUE
            else:
                str_attribute = self.setAttribute.valof()
                # If the form has the range option we convert to an integer from
                # the string in the menu.
                # Otherwise we use trip as range.
                if self.rangeOption:
                    int_range = RANGES.index(self.range.valof())
                else:
                    int_range = TRIP
            if verbose:
                Errlog.log(FUNK + "Attribute: %s, Range: %s"
                           %(str_attribute, RANGES[int_range]))
            return (str_attribute,int_range)

    
#######################################################
#
# Section 2: The main functions called by the user
#
#######################################################

def setAttribute():
    """
    Sets an attribute on either a deadhead, or on a specified range of legs.
    """
    FUNK = MODULE + "::setAttribute: "

    Errlog.log(FUNK + "Setting attribute on a range of legs.")

    verbose, = R.eval('fundamental.%debug_verbose_mode%')
    
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)

    leg_object = HF.LegObject()
    trip_object = HF.TripObject()
    
    leg_values = _getValues(leg_object, verbose)

    (crewId, valid_leg, lpc_opc_ots, deadhead, old_attr, training_codes) = leg_values

    if not valid_leg:
        err_mess = "Only valid on flights or LPC/OPC/OTS, in the planning period"
        cfhExtensions.show(err_mess)
        Errlog.log(FUNK + err_mess)
        return None
    
    # Show dialog
    rangeOption = True
    if lpc_opc_ots:
        rangeOption = False
        
    attributes_form = FlightAttributesForm(
        old_attr,
        deadhead,
        training_codes,
        rangeOption,
        "FlightAttributesSetting")

    formValues = attributes_form.getValues(verbose)
    if formValues is None:
        # Cancel was pressed.
        if verbose:
            Errlog.log(FUNK + "Cancelled by user")
        return None
    
    (attribute, range) = formValues
    if (attribute == old_attr and range == LEG):
        # The only case we don't handle is when there will be no change.
        # Since a range other than LEG can affect legs with a different attribute
        # we take the safe option and change all legs to the new attribute.
        if verbose:
            Errlog.log(FUNK + "No change.")
        return
    else:
        Errlog.log(FUNK +
                   "Setting attribute to: %s for range: %s" %(attribute,
                                                              RANGES[range]))
        if range == LEG:
            obj = leg_object
        elif range == TRIP:
            obj = trip_object
        else:
            obj = None
            crewId = None
        legs = _getLegs(obj, area, verbose=verbose)

        _putData(legs, attribute, crewId, lpc_opc_ots)
                
        
#######################################################
#
# Section 3: General helper functions
#
#######################################################


def _getValues(leg_object, verbose=False):
    """
    Returns various values for a clicked leg.
    """
    FUNK = MODULE + "::_getValues: "
    leg_vars = leg_object.eval('crew.%id%',
                               'crew.%is_pilot%',
                               'leg.%can_have_attribute%',
                               'leg.%is_lpc_opc_or_ots%',
                               'leg.%is_deadhead%',
                               'leg.%training_code_safe%',
                               'leg.%starts_in_pp%'
                               )
    (crewId, FC, valid, lpc_opc_ots, dh, attr, in_pp) = leg_vars

    valid = valid and in_pp
    
    if FC:
        if lpc_opc_ots:
            set_var = 'attributes.lpc_opc_or_ots_codes'
        else:
            set_var = 'attributes.training_codes_fc'
    else:
        set_var = 'attributes.training_codes_cc'

    training_codes = R.set(set_var).members()
    if not attr:
        attr = DEFAULT_VALUE
    if verbose:
        Errlog.log(FUNK + "crewId: %s, FC: %s, attr: %s" %(crewId, FC, attr))
        print leg_vars
    
    return (crewId, valid, lpc_opc_ots, dh, attr, training_codes)
               

def _getLegs(object, area, verbose=False):
    """
    Returns the legs in the wanted range.

    'area' is needed to re-set default context to 'window' for marked legs when
    'object' is None.
    """
    FUNK = MODULE + "::_getLegs: "
    Errlog.log(FUNK + "Getting legs to set attribute for")
                   
    legVars = ("leg.%can_have_attribute%",
               "leg.%is_deadhead%",
               "leg.%training_code_safe%",
               "leg.%udor%",
               "leg.%fd_or_uuid%",
               "leg.%start_station%",
               "crew.%id%"
               )

    if (object is None):
        # This means we want all marked legs
        if verbose:
            Errlog.log(FUNK + "Getting values for marked legs in window")
        CCL = CuiContextLocator(area, "window")
        iteration = R.iter("iterators.leg_set", where="marked")
        CCL.reinstate()
        legs, = R.eval('default_context', R.foreach(iteration, *legVars))
    else:
        iteration = "iterators.leg_set"
        legs, = object.eval(R.foreach(iteration, *legVars))
    if verbose:
        print legs
    return legs


def _putData(legs, attribute, crewId, lpc_opc_ots):
    """
    Writes data to etable on file or database.

    'crewId', if supplied, is used instead of the id in the 'legs' tuple.
    """
    oneLegOnly = (len(legs) == 1)

    for (ix, valid, deadhead, old_attr, udor, fd_uuid, adep, crewId) in  legs:
        if (attribute == old_attr):
            # We only write data when necessary.
            pass
        elif not valid:
            # We only set attributes on valid legs (flight duties and LPC/OPC/OTS).
            pass
        else:
            # There are two cases where attributes should be set:
            # 1. When a deadhead was clicked. 'oneLegOnly' will be True and
            #    'deadhead' will also be True.
            # 2. When an active leg was clicked. 'oneLegOnly' can be both True or
            #    False, 'deadhead' will be False for at least the clicked leg.
            #    Only active legs should get the attribute.
            if ((deadhead and oneLegOnly) or not deadhead):
                # If we clicked an active leg, only active legs should
                # get an attribute in the wanted range.
                # In both cases we need to remove the old attribute since only
                # one training attribute per flight is supported
                if old_attr != "NONE":
                    if lpc_opc_ots:
                        Attributes.RemoveCrewGroundDutyAttr(crewId,
                                                            udor, fd_uuid,
                                                            old_attr)
                    else:
                        Attributes.RemoveCrewFlightDutyAttr(crewId,
                                                            udor, fd_uuid, adep,
                                                            old_attr)
                if (attribute != "NONE"):
                    if lpc_opc_ots:
                        Attributes.SetCrewGroundDutyAttr(crewId,
                                                         udor, fd_uuid,
                                                         attribute,
                                                         refresh=False)
                    else:
                        Attributes.SetCrewFlightDutyAttr(crewId,
                                                         udor, fd_uuid, adep,
                                                         attribute,
                                                         refresh=False)
                if (old_attr != "NONE" or attribute != "NONE"):
                    modcrew.add(crewId)

    Attributes._refresh("crew_flight_duty_attr")
    Attributes._refresh("crew_ground_duty_attr")
    
# End of file
