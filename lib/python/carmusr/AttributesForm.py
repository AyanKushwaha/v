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
import Crs
import Cfh
import utils.CfhFormClasses as CFC
import Errlog
import carmensystems.rave.api as R
from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator
import Variable
import carmstd.cfhExtensions as cfhExtensions
import carmusr.HelperFunctions as HF
import carmusr.modcrew as modcrew
import carmusr.application as application

MODULE = "AttributesForm"
RANGES = ["Clicked leg only","Entire trip","All marked"]
(LEG,TRIP,MARKED) = range(3)
# The default value should match what's in the rave code
DEFAULT_VALUE = "NONE"

CancelFormError = CFC.CancelFormError
            
################################################################################
#
# Section 1: Class definition for the form to display
#
################################################################################


class AttributesForm(CFC.BasicCfhForm):
    """
    A class for the leg attributes form.

    Builds and displays the correct form and implements a function that returns
    the values of the form.
    """
    def __init__(self, oldAttribute, availableAttributes, rangeOption,
                 title="Set Training attributes",useDefault=True, label=""):
        """
        Initializes the form with a behaviour dependent on whether it's called
        on a deadhead or from the assignWithAttribute function. Uses the old
        attribute as default.
        """
        Errlog.log(MODULE + "::AttributesForm: Initializing form")
        CFC.BasicCfhForm.__init__(self, "Attributes Form")
        self._delta_y = 12
        # If messages in form
        label_height = 0
        if label:
            rows = label.split('\n')
            index = 0
            tmp_label = ""
            added_rows = 0
            for row in rows:
                tmp_label += row + "\n"
                if index == 2:
                    self.add_label(added_rows, 1, 'header_%d'%added_rows, tmp_label)
                    tmp_label = ""
                    index = 0
                    added_rows += 2
                else:
                    index += 1
            if index > 0:
                self.add_label(added_rows, 1, 'header_%s'%added_rows, tmp_label)
            label_height = added_rows+2
            
        availableAttributes = list(availableAttributes)
        if "ETOPS LIFUS" in availableAttributes and "ETOPS LC" in availableAttributes:
            el_index = availableAttributes.index("ETOPS LIFUS")
            elc_index = availableAttributes.index("ETOPS LC")
            availableAttributes[el_index+1], availableAttributes[elc_index] = availableAttributes[elc_index], availableAttributes[el_index+1]
            Errlog.log(MODULE + "::AttributesForm: Atr List changed %s" %availableAttributes)
        if useDefault:
            availableAttributes.append(DEFAULT_VALUE)
            
        self.add_filter_combo(label_height,1,"attribute",'Attribute:',
                              oldAttribute, availableAttributes)

        if rangeOption:
            if application.isTracking or application.isDayOfOps:
                current_range = RANGES[MARKED]
            else:
                current_range = RANGES[TRIP]
            self.add_filter_combo(label_height+1,1,"range","Range:",
                                  current_range,RANGES, upper=False)
        else:
            class no_range_option:
                def valof(self):
                    return RANGES[TRIP]
            self.range_field = no_range_option()
            
    @property
    def attribute(self):
        return self.attribute_field.valof()
    @property
    def range_int(self):
        return RANGES.index(self.range_field.valof())
        
class SelectAttributeForm(AttributesForm):
    def __init__(self,attributes, title, label):
        AttributesForm.__init__(self,'',attributes,False,
                                title=title,
                                useDefault=False,
                                label=label)
        




# End of file
