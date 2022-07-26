"""
Rave parameter forms provided by the reports
"""

if __name__ == "__main__":
    raise NotImplementedError("Do not run this module as a script")

# Reload handling. Just to simplify development. ##############
try:
    is_being_reloaded  # @UndefinedVariable
    is_being_reloaded = True
except NameError:
    is_being_reloaded = False

if is_being_reloaded:
    close_and_free_all_forms()  # @UndefinedVariable


####################################################################

import weakref
from tempfile import NamedTemporaryFile

import carmensystems.rave.api as rave
from Localization import MSGR, bl_msgr
from RelTime import RelTime
import Cfh
import Gui

from report_sources.calibration import check_rule_consistency
from carmusr.calibration import report_violations_over_time as vot
from carmusr.calibration import report_violations_over_station as vos
from carmusr.calibration import report_violations_over_weekdays as vow
from carmusr.calibration import report_rule_value_distribution as rvd
from carmusr.calibration import report_rule_details as rd
from carmusr.calibration import report_rule_kpis as kpi
from carmusr.calibration import report_compare_plans as rc
from carmusr.calibration import report_pattern_analysis as rp
from carmusr.calibration import report_si as si
from carmusr.calibration import report_dashboard as dabo
from carmusr.calibration.util import basics
from carmusr.calibration.util import calibration_rules as calib_rules
from carmusr.calibration.util import complement
from carmusr.calibration.util import report_util as ru
from carmusr.calibration.util import config_per_product


LISTENER_TAG = "CalibReportParamChanged"


# Objects used in the forms #####################################

class RaveParam(Cfh.String):
    """
    The base class for Rave parameter fields.
    Can be used "as is" for any normal Rave parameter.
    Just provide the name of the parameter as the
    named argument "param_name" to the constructor.
    """
    @staticmethod
    def get_rave_param_class(param_name):
        if not param_name:
            return None
        try:
            rave.param(param_name)
            return rave.param
        except rave.UsageError:
            try:
                rave.paramset(param_name)
                return rave.paramset
            except rave.UsageError:
                pass
        return None

    def __init__(self, *args, **kw):
        self.parent = weakref.ref(args[0])
        self.param_name = None
        if "param_name" in kw:
            self.param_name = kw["param_name"]
            del kw["param_name"]
        super(RaveParam, self).__init__(*args, **kw)

    def get_param_class(self):
        return self.get_rave_param_class(self.param_name)

    def get_rave_param(self):
        return self.get_param_class()(self.param_name)

    def get_rave_param_value(self):
        if self.get_param_class() is rave.param:
            return self.get_rave_param().value()
        elif self.get_param_class() is rave.paramset:
            return set(self.get_rave_param().members())
        return None

    def get_rave_param_value_type(self):
        return type(self.get_rave_param_value())

    def rave_value2string(self, rave_value):
        if self.get_param_class() is rave.param:
            if self.get_rave_param_value_type() is bool:
                return bl_msgr(str(rave_value))
            return str(rave_value)
        if self.get_param_class() is rave.paramset:
            return ",".join(sorted(rave_value))
        return MSGR("n/a")

    def get_string_value_from_rave(self):
        return self.rave_value2string(self.get_rave_param_value())

    def string2rave_value(self, text):
        if self.get_param_class() is rave.param:
            if self.get_rave_param_value_type() is bool:
                return self.get_rave_param_value_type()(text == MSGR("True"))
            return self.get_rave_param_value_type()(text)
        return set(item.strip() for item in text.split(","))

    def set_rave_param_value(self, text):
        if text != self.get_string_value_from_rave():
            if self.get_param_class() is rave.param:
                self.get_rave_param().setvalue(self.string2rave_value(text))
            else:
                self.get_rave_param().clear()
                for item in self.string2rave_value(text):
                    self.get_rave_param().add(item)

    def get_default_value(self):
        if self.get_param_class() is rave.param:
            return self.get_rave_param().getDefaultValue()
        if self.get_param_class() is rave.paramset:
            return self.get_rave_param().getDefaultValues()
        return MSGR("n/a")

    def refresh_when_rule_set_changed(self):
        pass

    def refresh_when_rave_param_changed(self):
        if self.get_param_class() is None:
            self.setEnable(0)
        else:
            self.setEnable(1)
        self.setDescription(MSGR("Default value: {0}      Name: {1}").format(self.rave_value2string(self.get_default_value()),
                                                                             self.param_name))
        self.setValue(self.get_string_value_from_rave())

    def check(self, text):
        if self.param_name is None:
            return

        ret = super(RaveParam, self).check(text)
        if ret:
            return ret

        # We have to check this ourselves. The check is done by core,
        # but no string is returned from the check method. Bug?!
        if self.getMenu() and self.getMenuOnly():
            if text not in self.getMenu():
                return MSGR("Only the values in the menu are allowed")

        try:
            self.string2rave_value(text)
        except Exception:
            return MSGR("Incorrect format for %s") % {RelTime: MSGR("time, use 'HH:MM'"),
                                                      int: MSGR("integer, use 'D'")}.get(self.get_rave_param_value_type(),
                                                                                         str(self.get_rave_param_value_type()))

        if self.get_rave_param_value_type() in (RelTime, int):
            mi = self.get_rave_param().getMinValue()
            if mi is not None and self.string2rave_value(text) < mi:
                return MSGR("%s is the minimum value") % mi
            ma = self.get_rave_param().getMaxValue()
            if ma is not None and self.string2rave_value(text) > ma:
                return MSGR("%s is the maximum value") % ma

    def compute(self):
        if self.param_name is None:
            return
        self.set_rave_param_value(self.getValue())
        Gui.GuiCallListener(Gui.TaggedListener, LISTENER_TAG)

    def verify(self, var):  # Change the Rave parameter already during editing of field.
        if self.param_name is None:
            return
        if not self.parent().isShown():  # Skip during form creation.
            return
        if self.check(var.value):
            return
        self.set_rave_param_value(var.value)


class CrewPosFilter(RaveParam):

    def __init__(self, *args, **kw):
        super(CrewPosFilter, self).__init__(*args, **kw)
        self.setMandatory(1)

    def check(self, text):
        ret = super(CrewPosFilter, self).check(text)
        if ret:
            return ret
        try:
            complement.CrewCategories.mask_from_pos_comma_sep(text)
        except ValueError, e:
            return str(e)

    def compute(self):
        self.setValue(", ".join(filter(None, (item.strip() for item in self.getValue().split(",")))))
        super(CrewPosFilter, self).compute()


class Method(RaveParam):

    def __init__(self, *args, **kw):
        super(Method, self).__init__(*args, **kw)
        self.setMenu(["", MSGR("REPLACE"), MSGR("ADD")])
        self.setMenuOnly(1)
        self.setMandatory(1)

    def rave_value2string(self, rave_value):
        return bl_msgr(str(rave_value).split(".")[-1].upper())

    def string2rave_value(self, text):
        rave_module_name = str(self.get_rave_param_value()).split(".")[0]
        return rave.enumval("%s.%s" % (rave_module_name, "replace" if (text == self.getMenu()[1]) else "add"))


class BoolToggle(RaveParam):

    def __init__(self, *args, **kw):

        super(BoolToggle, self).__init__(*args, **kw)
        self.setMenu(["", MSGR("True"), MSGR("False")])
        self.setMenuOnly(1)
        self.setMandatory(1)


class Bin(RaveParam):

    def rulekey2bin(self, rule_key):
        try:
            return getattr(self.parent().cr.get_rule_item(rule_key), calib_rules.BIN).name()
        except KeyError:
            return None

    def __init__(self, *args, **kw):
        self.rule_param_name = kw["rule_param_name"]  # Mandatory argument
        del kw["rule_param_name"]
        super(Bin, self).__init__(*args, **kw)
        self._set_derived_attributes()
        self.setMandatory(1)

    def refresh_when_rave_param_changed(self):
        self._set_derived_attributes()
        super(Bin, self).refresh_when_rave_param_changed()

    def _set_derived_attributes(self):
        rule_key = str(rave.param(self.rule_param_name).value())
        self.param_name = self.rulekey2bin(rule_key)


class VowBinsPerDay(RaveParam):

    def __init__(self, *args, **kw):
        super(VowBinsPerDay, self).__init__(*args, **kw)
        self.setMenu(["", "2", "3", "4", "6", "8", "12", "24", "48", "96"])


class Gamma(RaveParam):

    def __init__(self, *args, **kw):
        super(Gamma, self).__init__(*args, **kw)
        self.setMenu(["", "25", "50", "75", "100", "150", "200", "400"])


class RuleNameParam(RaveParam):

    no_rule_value = "no_rule"
    no_rule_str = MSGR("No rule")

    def get_ordered_rule_items(self):  # Define in sub-class
        pass

    def __init__(self, *args, **kw):
        super(RuleNameParam, self).__init__(*args, **kw)
        self._set_derived_attributes()
        self.setMenu(self.rule_menu)
        self.setMenuOnly(1)
        self.setMandatory(1)

    def string2rave_value(self, text):
        return self.remark2rule_key[text]

    def rave_value2string(self, rave_value):
        return self.rule_key2remark.get(str(rave_value), self.no_rule_str)

    def _set_derived_attributes(self):
        self.rule_menu = []
        self.remark2rule_key = {}
        self.rule_key2remark = {}
        for cri in self.get_ordered_rule_items():
            rule_label_no_colon = cri.rule_label.replace(":", "<colon>")
            self.rule_menu.append(rule_label_no_colon)
            self.remark2rule_key[rule_label_no_colon] = cri.rule_key
            self.rule_key2remark[cri.rule_key] = rule_label_no_colon
        self.rule_menu = [MSGR("Pick rule for analysis"), self.no_rule_str] + self.rule_menu
        self.remark2rule_key[self.no_rule_str] = self.no_rule_value
        self.rule_key2remark[self.no_rule_value] = self.no_rule_str

    def refresh_when_rule_set_changed(self):
        self._set_derived_attributes()
        self.setMenu(self.rule_menu)
        super(RuleNameParam, self).refresh_when_rule_set_changed()


class VotRuleNameParam(RuleNameParam):

    def get_ordered_rule_items(self):
        return self.parent().cr.all_rules


class VosRuleNameParam(RuleNameParam):

    def get_ordered_rule_items(self):
        return self.parent().cr.station_rules


class TimeZone(RaveParam):

    items = [("reference", MSGR("Reference Airport"))]
    for ix in xrange(12, 0, -1):
        items.append(("utc_minus_%d" % ix, MSGR("UTC-%d") % ix))
    items.append(("utc_plus_0", MSGR("UTC")))
    for ix in xrange(1, 13):
        items.append(("utc_plus_%d" % ix, MSGR("UTC+%d") % ix))
    value2string = dict(items)
    string2value = dict([(item[1], item[0]) for item in items])
    menu = [MSGR("Time Zone")] + [item[1] for item in items]

    def __init__(self, *args, **kw):
        super(TimeZone, self).__init__(*args, **kw)
        self.setMenu(self.menu)
        self.setMenuOnly(1)
        self.setMandatory(1)

    def string2rave_value(self, text):
        module_name = str(self.get_rave_param_value()).split(".")[0]
        return rave.enumval("%s.%s" % (module_name, self.string2value[text]))

    def rave_value2string(self, rave_value):
        return self.value2string[str(rave_value).split(".")[1]]


class NumberedMenu(RaveParam):

    def __init__(self, *args, **kw):
        super(NumberedMenu, self).__init__(*args, **kw)
        self.setMenu(self.menu)
        self.setMenuOnly(1)
        self.setMandatory(1)

    def rave_value2string(self, rave_value):
        return self.menu[rave_value]

    def string2rave_value(self, text):
        return int(text[0])


class PatColourOnAttr(NumberedMenu):
    menu = rp.DetailsViewSettingAlternatives.colouring_menu


class PatSortOnAttr(PatColourOnAttr):
    menu = rp.DetailsViewSettingAlternatives.sorting_menu


class PatMatchBin(NumberedMenu):
    menu = rp.BinMatchingPatternHandler.alternatives


class PatMatchComp(NumberedMenu):
    menu = rp.CompMatchingPatternHandler.alternatives


class PatFilterParam(RaveParam):

    def refresh_when_rave_param_changed(self):
        super(PatFilterParam, self).refresh_when_rave_param_changed()
        if rave.param("report_calibration.pat_use_filter").value():
            self.setEnable(1)
        else:
            self.setEnable(0)


class PatFilterBoolToggle(PatFilterParam, BoolToggle):
    pass


class Close(Cfh.Function):

    def __init__(self, *args, **kw):
        self.callback = None
        Cfh.Function.__init__(self, *args, **kw)

    def register_callback(self, callback):
        self.callback = callback

    def action(self):
        self.finishForm(0, 0)
        if self.callback:
            self.callback()


class SetDefault(Cfh.Function):

    def __init__(self, *args, **kw):
        self.parent = weakref.ref(args[0])
        Cfh.Function.__init__(self, *args, **kw)

    def action(self):
        for field in self.parent().entries:
            if field.get_param_class():
                field.get_rave_param().setDefault()
        Gui.GuiCallListener(Gui.TaggedListener, LISTENER_TAG)


# The forms #########################################

class ParameterFormForCalibrationReport(Cfh.Box):

    initial_items = (("LAYOUT", "EMPTY"),)
    rave_parameters = ()  # Redefine in sub-class. ((class, rule_param_name),)
    final_parameters = ((Method, ru.SELECT_METHOD_PARAMETER_NAME),)

    form_name = None  # Redefine in sub-class
    report_title = None  # Redefine in sub-class

    def refresh_when_rule_set_changed(self):
        self.cr = calib_rules.CalibrationRuleContainer(self.variant)
        for item in self.entries:
            item.refresh_when_rule_set_changed()
        self.refresh_when_rave_param_changed()

    def refresh_when_rave_param_changed(self):
        for item in self.entries:
            item.refresh_when_rave_param_changed()

    def __init__(self, variant):

        title = MSGR("Parameters for the report '%s'") % self.report_title

        super(ParameterFormForCalibrationReport, self).__init__(self.form_name, title)

        self.variant = variant
        self.cr = calib_rules.CalibrationRuleContainer(self.variant)  # A fresh one is required by field classes.

        self.entries = []
        layout = ["FORM;%s;%s" % (self.form_name, title)]

        for num, (cls, rave_param) in enumerate(self.initial_items + self.rave_parameters + self.final_parameters):
            if cls == "LAYOUT":
                layout.append(rave_param)
                continue
            if RaveParam.get_rave_param_class(rave_param) is None:
                continue
            field = cls(self, "RAVE_PARAM_%d" % num, 0, "", param_name=rave_param)
            self.entries.append(field)
            layout.append("FIELD;RAVE_PARAM_%d;%s" % (num, field.get_rave_param().remark()))
            if isinstance(field, RuleNameParam):
                bin_field = Bin(self, "BIN_%d" % num, max(5, len(MSGR("n/a"))), "", rule_param_name=rave_param)
                self.entries.append(bin_field)
                layout.append("FIELD;BIN_%d;%s" % (num, MSGR("Bin size")))
                layout.append("EMPTY")

        self.close = Close(self, "CLOSE")
        layout.append("BUTTON;CLOSE;%s;%s" % (MSGR("Close"), MSGR("_Close")))
        self.set_default = SetDefault(self, "DEFAULT")
        layout.append("BUTTON;DEFAULT;%s;%s" % (MSGR("Default"), MSGR("_Default")))

        with NamedTemporaryFile() as f:
            f.write("\n".join(layout))
            f.flush()
            self.load(f.name)

        self.refresh_when_rave_param_changed()


class ParameterFormRVD(ParameterFormForCalibrationReport):

    form_name = "RVD_PARAM_FORM"
    report_title = ru.CalibReports.RVD.title

    def __getattribute__(self, attr):
        if attr != "rave_parameters":
            return super(ParameterFormRVD, self).__getattribute__(attr)

        items = ()
        if config_per_product.get_config_for_active_product().allow_pos_filtering:
            items += ((CrewPosFilter, "report_calibration.crew_pos_filter_p"),
                      ("LAYOUT", "EMPTY"))
        items += ((VotRuleNameParam, rvd.RuleValueDistribution.RULE_PARAM),)
        return items


class ParameterFormRD(ParameterFormForCalibrationReport):

    form_name = "RD_PARAM_FORM"
    report_title = ru.CalibReports.RD.title

    def __getattribute__(self, attr):
        if attr != "rave_parameters":
            return super(ParameterFormRD, self).__getattribute__(attr)

        items = ()
        if config_per_product.get_config_for_active_product().allow_pos_filtering:
            items += ((CrewPosFilter, "report_calibration.crew_pos_filter_p"),
                      ("LAYOUT", "EMPTY"))
        items += ((VotRuleNameParam, rd.Report.RULE_PARAM),)
        return items


class ParameterFormVOT(ParameterFormForCalibrationReport):

    form_name = "VOT_PARAM_FORM"
    report_title = ru.CalibReports.VOT.title

    def __getattribute__(self, attr):
        if attr != "rave_parameters":
            return super(ParameterFormVOT, self).__getattribute__(attr)

        items = ((RaveParam, "studio_calibration.delay_codes_of_interest"),)
        if config_per_product.get_config_for_active_product().allow_pos_filtering:
            items += ((CrewPosFilter, "report_calibration.crew_pos_filter_p"),)
        items += (("LAYOUT", "EMPTY"),
                  (VotRuleNameParam, "report_calibration.vot_rule_1"),
                  (VotRuleNameParam, "report_calibration.vot_rule_2"),
                  (VotRuleNameParam, "report_calibration.vot_rule_3"),
                  (VotRuleNameParam, "report_calibration.vot_rule_4"),
                  (TimeZone, "report_calibration.vot_time_zone"),
                  (BoolToggle, "report_calibration.use_scheduled_time_as_rule_time_p"),
                  (BoolToggle, "report_calibration.use_end_time_of_object_as_rule_failure_time_p"),
                  ("LAYOUT", "EMPTY"))
        return items


class ParameterFormVOS(ParameterFormForCalibrationReport):

    form_name = "VOS_PARAM_FORM"
    report_title = ru.CalibReports.VOS.title

    def __getattribute__(self, attr):
        if attr != "rave_parameters":
            return super(ParameterFormVOS, self).__getattribute__(attr)

        items = ((RaveParam, "studio_calibration.delay_codes_of_interest"),)
        if config_per_product.get_config_for_active_product().allow_pos_filtering:
            items += ((CrewPosFilter, "report_calibration.crew_pos_filter_p"),)
        items += (("LAYOUT", "EMPTY"),
                  (VosRuleNameParam, "report_calibration.station_rule"))
        return items


class ParameterFormVOW(ParameterFormForCalibrationReport):

    form_name = "VOW_PARAM_FORM"
    report_title = ru.CalibReports.VOW.title

    def __getattribute__(self, attr):
        if attr != "rave_parameters":
            return super(ParameterFormVOW, self).__getattribute__(attr)

        items = ()
        if config_per_product.get_config_for_active_product().allow_pos_filtering:
            items += ((CrewPosFilter, "report_calibration.crew_pos_filter_p"),
                      ("LAYOUT", "EMPTY"))
        items += ((VotRuleNameParam, vow.RuleViolationsOverWeekdays.RULE_PARAM),
                  (VowBinsPerDay, "report_calibration.vow_bins_per_day"),
                  (Gamma, "report_calibration.vow_centi_gamma"),
                  ("LAYOUT", "EMPTY"),
                  (TimeZone, "report_calibration.vot_time_zone"),
                  (BoolToggle, "report_calibration.use_scheduled_time_as_rule_time_p"),
                  (BoolToggle, "report_calibration.use_end_time_of_object_as_rule_failure_time_p"),
                  ("LAYOUT", "EMPTY"))
        return items


class ParameterFormComp(ParameterFormForCalibrationReport):

    form_name = "COMP_PARAM_FORM"
    report_title = ru.CalibReports.COMP.title


class ParameterFormSI(ParameterFormForCalibrationReport):

    form_name = "SI_PARAM_FORM"
    report_title = ru.CalibReports.SI.title


class ParameterFormDABO(ParameterFormForCalibrationReport):

    form_name = "DABO_PARAM_FORM"
    report_title = ru.CalibReports.DABO.title


class ParameterFormDABOforTTA(ParameterFormForCalibrationReport):

    form_name = "DABO_TTA_PARAM_FORM"
    report_title = ru.CalibReports.DABO.timetable_title


class ParameterFormKPI(ParameterFormForCalibrationReport):

    initial_items = (("LAYOUT", "COLUMN;6"),)
    final_parameters = (("LAYOUT", "EMPTY"),
                        ("LAYOUT", "LABEL;%s" % MSGR("Interaction")),
                        (Method, ru.SELECT_METHOD_PARAMETER_NAME))

    form_name = "KPI_PARAM_FORM"
    report_title = ru.CalibReports.RKPI.title

    def __getattribute__(self, attr):
        if attr != "rave_parameters":
            return super(ParameterFormKPI, self).__getattribute__(attr)
        bin_param_names = set(getattr(cri, calib_rules.BIN).name() for cri in self.cr.all_rules_dict.itervalues())
        if not bin_param_names:
            return ()
        else:
            items = (("LAYOUT", "EMPTY"),
                     ("LAYOUT", "LABEL;%s" % MSGR("Bin Sizes")))
            return items + tuple((RaveParam, bin_param_name) for bin_param_name in sorted(bin_param_names, reverse=True))


class ParameterFormKPIforTTA(ParameterFormKPI):

    form_name = "KPI_TTA_PARAM_FORM"
    report_title = ru.CalibReports.RKPI.timetable_title


class ParameterFormPat(ParameterFormForCalibrationReport):

    rave_parameters = (("LAYOUT", "LABEL;%s" % MSGR("General")),
                       (PatMatchBin, rp.BinMatchingPatternHandler.parameter_name),
                       (PatMatchComp, rp.CompMatchingPatternHandler.parameter_name),
                       ("LAYOUT", "EMPTY"),
                       (Gamma, "report_calibration.pat_centi_gamma"),
                       ("LAYOUT", "EMPTY"),
                       ("LAYOUT", "LABEL;%s" % MSGR("Filter")),
                       (BoolToggle, "report_calibration.pat_use_filter"),
                       (PatFilterParam, "report_calibration.pat_filter_max_completion"),
                       (PatFilterBoolToggle, "report_calibration.pat_filter_keep_one_leg_patterns"),
                       (PatFilterBoolToggle, "report_calibration.pat_filter_keep_two_legs_patterns"),
                       (PatFilterBoolToggle, "report_calibration.pat_filter_keep_three_legs_patterns"),
                       (PatFilterBoolToggle, "report_calibration.pat_filter_keep_four_legs_patterns"),
                       (PatFilterBoolToggle, "report_calibration.pat_filter_keep_five_legs_patterns"),
                       (PatFilterBoolToggle, "report_calibration.pat_filter_keep_six_or_more_legs_patterns"),
                       ("LAYOUT", "EMPTY"),
                       ("LAYOUT", "LABEL;%s" % MSGR("Overview view")),
                       (RaveParam, "report_calibration.pat_slices_bin_size_1"),
                       (RaveParam, "report_calibration.pat_slices_num_bins_with_size_1"),
                       (RaveParam, "report_calibration.pat_slices_bin_size_2"),
                       ("LAYOUT", "EMPTY"),
                       ("LAYOUT", "LABEL;%s" % MSGR("Details view")),
                       (PatColourOnAttr, "report_calibration.pat_details_colour_based_on"),
                       (BoolToggle, "report_calibration.pat_details_reversed_colouring"),
                       (PatSortOnAttr, "report_calibration.pat_details_sort_order"),
                       (BoolToggle, "report_calibration.pat_details_reversed_sort_order"),
                       ("LAYOUT", "EMPTY"),
                       ("LAYOUT", "LABEL;%s" % MSGR("Interaction")))

    form_name = "PAT_PARAM_FORM"
    report_title = ru.CalibReports.PAT.title


class ParameterFormRCC(ParameterFormForCalibrationReport):

    form_name = "RCC_PARAM_FORM"
    report_title = ru.CalibReports.RCC.title


# Handlers for the forms ########################################

class ParameterFormHandler(object):

    listener_values = [("action_callb", Gui.ActionListener, "", "CalibReportActionListener"),
                       ("refresh_form_when_rave_param_changed", Gui.RefreshListener, "parametersChanged", "CalibReportRefreshListener"),
                       ("refresh_form_when_rave_param_changed", Gui.TaggedListener, LISTENER_TAG, "CalibReportTaggedListener")]

    def __init__(self, variable_name_in_module, form_class, report_class):
        self.form = None
        self.unique_suffix = str(id(self))
        self.form_class = form_class
        self.report_class = report_class
        self.variable_name_in_module = variable_name_in_module

    def show_form(self, variant):
        if not self.report_class.critical_rave_parameter_exist():
            Gui.GuiMessage(MSGR("Impossible to set parameters. No calibration enabled rule set loaded."))
            return
        if basics.no_or_empty_local_plan():
            Gui.GuiMessage(MSGR("Impossible to set parameters. No or an empty local plan is loaded."))
            return
        if not self.form:
            self.prev_form = None
            self.form = self.form_class(variant)
            self.form.close.register_callback(self.free_form)
            self.test_param = rave.parameters().next()

            for method, kind, tag, name in self.listener_values:
                Gui.GuiCreateListener('''PythonEvalExpr("%s.%s.%s()")''' % (__name__, self.variable_name_in_module, method),
                                      kind, tag, name + self.unique_suffix)

        elif self.form.variant != variant:
            self.form.variant = variant
            self.form.refresh_when_rule_set_changed()

        self.form.show(1)

    def free_form(self):
        if self.form:
            self.prev_form = self.form  # We must keep the reference for a while to avoid error messages in the log
            self.form = None
            for _callb, kind, _tag, name in self.listener_values:
                Gui.GuiDestroyListener(name + self.unique_suffix, kind)

    def close_and_free_form(self):
        if self.form:
            self.form.close.compute()

    def refresh_form_when_rave_param_changed(self):
        if self.form:
            self.form.refresh_when_rave_param_changed()

    def action_callb(self):
        if not self.form:
            return
        if not self.report_class.critical_rave_parameter_exist() or basics.no_or_empty_local_plan():
            self.close_and_free_form()
            return
        try:
            self.test_param.value()
        except rave.UsageError:  # Changed rule set
            self.form.refresh_when_rule_set_changed()
            self.test_param = rave.parameters().next()


def close_and_free_all_forms():
    rvd_param_form_handler.close_and_free_form()  # @UndefinedVariable
    rd_param_form_handler.close_and_free_form()  # @UndefinedVariable
    kpi_param_form_handler.close_and_free_form()  # @UndefinedVariable
    kpi_tta_param_form_handler.close_and_free_form()  # @UndefinedVariable
    vot_param_form_handler.close_and_free_form()  # @UndefinedVariable
    vos_param_form_handler.close_and_free_form()  # @UndefinedVariable
    vow_param_form_handler.close_and_free_form()  # @UndefinedVariable
    comp_param_form_handler.close_and_free_form()  # @UndefinedVariable
    pat_param_form_handler.close_and_free_form()  # @UndefinedVariable
    si_param_form_handler.close_and_free_form()  # @UndefinedVariable
    dabo_param_form_handler.close_and_free_form()  # @UndefinedVariable
    dabo_tta_param_form_handler.close_and_free_form()  # @UndefinedVariable
    rcc_param_form_handler.close_and_free_form()  # @UndefinedVariable


rvd_param_form_handler = ParameterFormHandler("rvd_param_form_handler", ParameterFormRVD, rvd.RuleValueDistribution)
rd_param_form_handler = ParameterFormHandler("rd_param_form_handler", ParameterFormRD, rd.Report)
kpi_param_form_handler = ParameterFormHandler("kpi_param_form_handler", ParameterFormKPI, kpi.Report)
kpi_tta_param_form_handler = ParameterFormHandler("kpi_tta_param_form_handler", ParameterFormKPIforTTA, kpi.Report)
vot_param_form_handler = ParameterFormHandler("vot_param_form_handler", ParameterFormVOT, vot.RuleViolationsOverTime)
vos_param_form_handler = ParameterFormHandler("vos_param_form_handler", ParameterFormVOS, vos.RuleViolationsOverStation)
vow_param_form_handler = ParameterFormHandler("vow_param_form_handler", ParameterFormVOW, vow.RuleViolationsOverWeekdays)
comp_param_form_handler = ParameterFormHandler("comp_param_form_handler", ParameterFormComp, rc.ReportComparePlans)
pat_param_form_handler = ParameterFormHandler("pat_param_form_handler", ParameterFormPat, rp.ReportPatternAnalysis)
si_param_form_handler = ParameterFormHandler("si_param_form_handler", ParameterFormSI, si.SensitivityIndexDistributionReport)
dabo_param_form_handler = ParameterFormHandler("dabo_param_form_handler", ParameterFormDABO, dabo.Report)
dabo_tta_param_form_handler = ParameterFormHandler("dabo_tta_param_form_handler", ParameterFormDABOforTTA, dabo.Report)
rcc_param_form_handler = ParameterFormHandler("rcc_param_form_handler", ParameterFormRCC, check_rule_consistency.Report)
