from collections import defaultdict

from carmensystems import kpi
from Localization import MSGR
import carmensystems.rave.api as rave
from RelTime import RelTime
import Cui
import carmensystems.studio.cuibuffer as cuib

from carmusr.calibration import mappings
from carmusr.calibration.util import basics
from carmusr.calibration.util import common
from carmusr.calibration.util import compare_plan
from carmusr.calibration.util import calibration_rules as calib_rules


def _use_only_these_kpis_for_legs_or_acrots(kpiself, add_matrix, add_vectors):

    if kpiself._scope != 'window':
        return False

    if Cui.CuiGetAreaMode(Cui.gpc_info, Cui.CuiArea0) not in (Cui.AcRotMode, Cui.LegMode):
        return False

    legs_buf = cuib.CuiBuffer(Cui.CuiArea0, 'window')
    _add_kpis(kpiself,
              rave.buffer2context(legs_buf).bag(),
              add_matrix,
              add_vectors,
              common.CalibAnalysisVariants.TimetableAnalysis.key)
    return True


def _add_kpis(kpiself, bag, add_matrix, add_vectors, variant):

    cr = calib_rules.CalibrationRuleContainer(variant)
    if not cr.all_rules:
        kpiself.add(kpi.KpiValue(MSGR("Calibration rule analysis"), cr.no_registered_rules_reason()))
        return

    matrix, vectors = get_calib_matrix_and_vectors(collect_data(bag, cr), variant)
    if add_matrix:
        kpiself.add(matrix)
    if add_vectors:
        for vector in vectors:
            kpiself.add(vector)


def get_calib_matrix_and_vectors(rule_datas, variant):

    matrix_values = []
    vector_list = []

    for rule_data in rule_datas:
        vector_values = []
        rule_label = rule_data.label
        current_group = None
        for label1, _cs, label2, _delim, value_calc, type_s, _act, _kw in get_kpi_defs(variant)[1:]:
            if label1:
                current_group = label1
            kpi_label = "%s %s" % (current_group, label2)
            value = kpi_round_etc(rule_data, type_s, value_calc(rule_data))
            matrix_values.append(((rule_label, kpi_label), value))
            vector_values.append(("[%s]     %s" % (truncate_rule_label(rule_label), kpi_label),
                                  value or 0))
        vector_list.append(kpi.KpiVector(MSGR("Calibration: ") + rule_label,
                                         vector_values,
                                         MSGR("KPI"), MSGR("Value")))
    matrix = kpi.KpiMatrix(MSGR("Calibration rule analysis"),
                           matrix_values,
                           MSGR("Rule"),
                           MSGR("KPI"),
                           MSGR("Rule Evaluation Summary"))
    return matrix, vector_list


def collect_data(bag, cr):
    rule_datas = []

    for calib_rule_item in cr.all_rules:
        rule_datas.append(RuleData(calib_rule_item,
                                   common.get_atomic_iterator_for_level(bag, calib_rule_item.rule_level)(),
                                   consider_leg_identifiers=False))  # No need for them in CustomKPIs
    return rule_datas


def truncate_rule_label(my_str, n=mappings.LENGTH_SHORT_RULE_LABEL):
    return "%s..." % my_str[:n] if len(my_str) > n else my_str


def kpi_round_etc(rd, type_s, val):
    if val is None:
        return None
    if type_s == "S":
        return val
    if type_s == "I":
        return val or None
    if type_s == "P":
        return int(round(val * 10)) if val else None
    if isinstance(val, float):
        if val.is_integer():
            return int(val)
        elif rd.data_type is int:
            return int(round(val))  # No decimals for KPIs of int rules.
        else:
            return int(round(val))  # No decimals for KPIs of RelTime rules.
    return val


class RuleData(object):

    def __init__(self, rule_item, bags, consider_categories=False, consider_leg_identifiers=True):
        self.rave_objects = []
        bin_size = getattr(rule_item, calib_rules.BIN).value()
        self.data_type = type(bin_size)
        self.bin_size = int(bin_size)
        max_diff_for_bin_one = int(rule_item.max_diff_for_bin_one)
        self.label = rule_item.rule_label
        self.description = getattr(rule_item, calib_rules.DESCRIPTION)
        self.key = rule_item.rule_key
        is_valid_var = getattr(rule_item, calib_rules.IS_VALID).rave_obj
        rule_body_expr = rule_item.rule_body_expr

        # Avoid RelTime for better performance
        if self.data_type is RelTime:
            limit_rave_obj = rave.expr("(%s) / 0:01" % getattr(rule_item, calib_rules.LIMIT).expr_str)
            value_rave_obj = rave.expr("(%s) / 0:01" % getattr(rule_item, calib_rules.VALUE).expr_str)
        else:
            limit_rave_obj = getattr(rule_item, calib_rules.LIMIT).rave_obj
            value_rave_obj = getattr(rule_item, calib_rules.VALUE).rave_obj

        is_acrot_or_free_leg = None
        value_per_bag_from_first_loop = []
        for bag in bags:
            if is_acrot_or_free_leg is None:
                is_acrot_or_free_leg = any(rave.eval(bag, rave.keyw("is_free_leg"), rave.keyw("is_acrot")))
            crew_comp = 1 if is_acrot_or_free_leg else bag.calibration_mappings.crew_complement()
            if not crew_comp:
                value_per_bag_from_first_loop.append(None)
                continue
            is_valid = rave.eval(bag, is_valid_var)[0]
            if not is_valid:
                value_per_bag_from_first_loop.append(None)
                continue
            is_legal = rave.eval(bag, rule_body_expr)[0]
            if is_legal is None:
                value_per_bag_from_first_loop.append(None)
                continue
            limit, value = rave.eval(bag, limit_rave_obj, value_rave_obj)
            ids = [leg_bag.leg_identifier() for leg_bag in bag.atom_set()] if consider_leg_identifiers else []
            ro = RaveObject(crew_comp, is_legal, value, limit, max_diff_for_bin_one, ids)
            self.rave_objects.append(ro)
            value_per_bag_from_first_loop.append(ro)

        # The rest is for calculation of categories.
        # For acceptable performance we do this in a second loop and we only do it if:
        # * it is requested by the argument consider_categories
        # * there are valid objects
        # * all valid objects are illegal
        if not consider_categories:
            return
        if not self.rave_objects:
            return
        if self.get_num_legal_crew_slices() > 0:
            return

        self._num_crew_per_ranked_category = defaultdict(int)
        self._leg_identifiers_crew_per_ranked_category = defaultdict(list)

        if is_acrot_or_free_leg:
            comp_plan_slices = None
        else:
            comp_key_var = getattr(rule_item, calib_rules.COMP_KEY)
            comp_plan_slices = compare_plan.ComparisonPlanHandler.collect_slices_from_comparison_plan(comp_key_var,
                                                                                                      rule_item.rule_level,
                                                                                                      use_crew_filter=False)

        self.cat_handler = compare_plan.CategoriesHandler(comp_plan_slices, rule_item)

        for ix, bag in enumerate(bags):
            rave_object = value_per_bag_from_first_loop[ix]
            if not rave_object:
                continue
            tripslice_or_crew_comp = compare_plan.unfiltered_slice_from_bag(comp_key_var, bag) if comp_plan_slices else rave_object.crew_comp
            _sub_cat, cats_and_crew = self.cat_handler.get_and_register_cat(bag, tripslice_or_crew_comp)
            for cat, num_crew in cats_and_crew:
                self._num_crew_per_ranked_category[cat] += num_crew
                self._leg_identifiers_crew_per_ranked_category[cat] += rave_object.ids

    # categories
    def categories_have_been_calculated(self):
        return hasattr(self, "_num_crew_per_ranked_category")

    def get_num_crew_per_category(self):
        return self._num_crew_per_ranked_category

    def get_leg_identifiers_per_crew_category(self):
        return self._leg_identifiers_crew_per_ranked_category

    # valid
    def get_num_valid_crew_slices(self):
        try:
            self._num_valid_crew_slices
        except AttributeError:
            self._num_valid_crew_slices = sum(ro.crew_comp for ro in self.rave_objects)
        return self._num_valid_crew_slices

    def get_all_ids(self):
        return reduce(list.__iadd__, [ro.ids for ro in self.rave_objects], [])

    # value
    def get_total_value(self):
        return sum(ro.crew_comp * ro.value for ro in self.rave_objects) if self.rave_objects else None

    def get_fully_sliced_values(self):
        try:
            self._fully_sliced_values
        except AttributeError:
            self._fully_sliced_values = reduce(list.__iadd__, ([ro.value] * ro.crew_comp for ro in self.rave_objects), [])
        return self._fully_sliced_values

    def get_max_value(self):
        return max(self.get_fully_sliced_values()) if self.rave_objects else None

    def get_min_value(self):
        return min(self.get_fully_sliced_values()) if self.rave_objects else None

    def get_average_value(self):
        return basics.mean(self.get_fully_sliced_values()) if self.rave_objects else None

    def get_percentile_value(self, perc):
        return basics.percentile(self.get_fully_sliced_values(), [perc])[0] if self.rave_objects else None

    # diff
    def get_fully_sliced_diffs(self):
        try:
            self._fully_sliced_diffs
        except AttributeError:
            self._fully_sliced_diffs = reduce(list.__iadd__, ([ro.diff] * ro.crew_comp for ro in self.rave_objects), [])
        return self._fully_sliced_diffs

    def get_total_diff(self):
        try:
            self._total_diff
        except AttributeError:
            self._total_diff = sum(ro.crew_comp * ro.diff for ro in self.rave_objects) if self.rave_objects else None
        return self._total_diff

    def get_total_diff_for_illegal(self):
        try:
            self._total_diff_for_illegal
        except AttributeError:
            self._total_diff_for_illegal = (sum(ro.crew_comp * ro.diff for ro in self.rave_objects if not ro.is_legal)
                                            if self.get_num_illegal_crew_slices() else
                                            None)
        return self._total_diff_for_illegal

    def get_total_diff_for_legal(self):
        if not self.get_num_legal_crew_slices():
            return None
        return self.get_total_diff() - (self.get_total_diff_for_illegal() or 0)

    def get_average_diff(self):
        return basics.mean(self.get_fully_sliced_diffs()) if self.rave_objects else None

    def get_percentile_diff(self, perc):
        if not self.rave_objects:
            return None
        return basics.percentile(self.get_fully_sliced_diffs(), [perc])[0]

    def get_max_diff(self):
        return max(self.get_fully_sliced_diffs()) if self.rave_objects else None

    def get_min_diff(self):
        return min(self.get_fully_sliced_diffs()) if self.rave_objects else None

    # limit
    def get_fully_sliced_limits(self):
        try:
            self._fully_sliced_limits
        except AttributeError:
            self._fully_sliced_limits = reduce(list.__iadd__, ([ro.limit] * ro.crew_comp for ro in self.rave_objects), [])
        return self._fully_sliced_limits

    def get_average_limit(self):
        return basics.mean(self.get_fully_sliced_limits()) if self.rave_objects else None

    def get_percentile_limit(self, perc):
        return basics.percentile(self.get_fully_sliced_limits(), [perc])[0] if self.rave_objects else None

    def get_max_limit(self):
        return max(self.get_fully_sliced_limits()) if self.rave_objects else None

    def get_min_limit(self):
        return min(self.get_fully_sliced_limits()) if self.rave_objects else None

    # illegal
    def get_num_illegal_crew_slices(self):
        try:
            self._num_illegal_crew_slices
        except AttributeError:
            self._num_illegal_crew_slices = sum(ro.crew_comp for ro in self.rave_objects if not ro.is_legal)
        return self._num_illegal_crew_slices

    def get_illegal_ids(self):
        try:
            self._illegal_ids
        except AttributeError:
            self._illegal_ids = reduce(list.__iadd__, [ro.ids for ro in self.rave_objects if not ro.is_legal], [])
        return self._illegal_ids

    def get_percent_illegal_crew_slices(self):
        return basics.percentage_value(self.get_num_illegal_crew_slices(), self.get_num_valid_crew_slices())

    # legal
    def get_num_legal_crew_slices(self):
        return self.get_num_valid_crew_slices() - self.get_num_illegal_crew_slices()

    def get_legal_ids(self):
        return set(self.get_all_ids()) - set(self.get_illegal_ids())

    def get_percent_legal_crew_slices(self):
        return basics.percentage_value(self.get_num_legal_crew_slices(), self.get_num_valid_crew_slices())

    # 1st bin
    def get_num_crew_slices_in_first_bin(self):
        try:
            self._num_crew_slices_in_first_bin
        except AttributeError:
            self._num_crew_slices_in_first_bin = sum(ro.crew_comp for ro in self.rave_objects if ro.in_first_bin)
        return self._num_crew_slices_in_first_bin

    def get_in_first_bin_ids(self):
        try:
            self._in_first_bin_ids
        except AttributeError:
            self._in_first_bin_ids = reduce(list.__iadd__, [ro.ids for ro in self.rave_objects if ro.in_first_bin], [])
        return self._in_first_bin_ids

    def get_percent_in_first_bin_crew_slices(self):
        return basics.percentage_value(self.get_num_crew_slices_in_first_bin(), self.get_num_valid_crew_slices())


class RaveObject(object):

    def __init__(self, crew_comp, is_legal, value, limit, max_diff_for_bin_one, ids):
        self.is_legal = is_legal
        self.value = value
        self.limit = limit
        abs_diff = abs(limit - value)
        self.diff = abs_diff if is_legal else -abs_diff
        self.in_first_bin = is_legal and abs_diff <= max_diff_for_bin_one
        self.crew_comp = crew_comp
        self.ids = ids


# Returns an array defining the Calibration Rule KPIs both for the PRT-report and the Custom-KPIs.
# Items (in a tuple) for each KPI:
#  - label1
#  - colspan
#  - label2
#  - end-delimiter-bits (for borders in PRT)
#  - value calculator (with "U" as type-info prt-object creator)
#  - type-info (RT: rule type, S:String, P: percent, I: Int, U: see above)
#  - action-def: leg-identifiers-calc or report-id
#  - additional properties for prt object in data rows (fixed value or callable taking RuleData instance as arg)

def get_kpi_defs(variant_key):
    defs = []

    defs.append((MSGR("Rule"), 1, "", 3, lambda rd: rd.label, "S", "RVD", {}))

    defs.append((MSGR("Valid"), 1, "#", 3, RuleData.get_num_valid_crew_slices, "I", RuleData.get_all_ids, {}))

    if variant_key == common.CalibAnalysisVariants.TimetableAnalysis.key:
        defs.append((MSGR("Legal"), 2, "#", 2, RuleData.get_num_legal_crew_slices, "I", RuleData.get_legal_ids, {}))
        defs.append((None, None, "%x10", 1, RuleData.get_percent_legal_crew_slices, "P", RuleData.get_legal_ids, {}))

    defs.append((MSGR("Illegal"), 2, "#", 2, RuleData.get_num_illegal_crew_slices, "I", RuleData.get_illegal_ids, {}))
    defs.append((None, None, "%x10", 1, RuleData.get_percent_illegal_crew_slices, "P", RuleData.get_illegal_ids, {}))

    defs.append((MSGR("In 1st bin"), 2, "#", 0, RuleData.get_num_crew_slices_in_first_bin, "I", RuleData.get_in_first_bin_ids, {}))
    defs.append((None, None, "%x10", 0, RuleData.get_percent_in_first_bin_crew_slices, "P", RuleData.get_in_first_bin_ids, {}))
    defs.append((MSGR("Bin"), 1, MSGR("size"), 3, lambda rd: rd.bin_size, "RT", None, {}))

    defs.append((MSGR("Limit"), 4, MSGR("Min"), 2, RuleData.get_min_limit, "RT", None, {}))
    defs.append((None, None, MSGR("50%"), 0, lambda rd: RuleData.get_percentile_limit(rd, 50), "RT", None, {}))
    defs.append((None, None, MSGR("Avg"), 0, RuleData.get_average_limit, "RT", None, {}))
    defs.append((None, None, MSGR("Max"), 1, RuleData.get_max_limit, "RT", None, {}))

    defs.append((MSGR("Value"), 5, MSGR("Tot"), 2, RuleData.get_total_value, "RT", None, {}))
    defs.append((None, None, MSGR("Min"), 0, RuleData.get_min_value, "RT", None, {}))
    defs.append((None, None, MSGR("50%"), 0, lambda rd: RuleData.get_percentile_value(rd, 50), "RT", None, {}))
    defs.append((None, None, MSGR("Avg"), 0, RuleData.get_average_value, "RT", None, {}))
    defs.append((None, None, MSGR("Max"), 1, RuleData.get_max_value, "RT", None, {}))

    defs.append((MSGR("Diff"), 10, MSGR("Tot illeg"), 0, RuleData.get_total_diff_for_illegal, "RT", None, {}))
    defs.append((None, None, MSGR("Tot legal"), 0, RuleData.get_total_diff_for_legal, "RT", None, {}))
    defs.append((None, None, MSGR("Tot"), 0, RuleData.get_total_diff, "RT", None, {}))
    defs.append((None, None, MSGR("Min"), 0, RuleData.get_min_diff, "RT", None, {}))
    defs.append((None, None, MSGR("5%"), 0, lambda rd: RuleData.get_percentile_diff(rd, 5), "RT", None, {}))
    defs.append((None, None, MSGR("10%"), 0, lambda rd: RuleData.get_percentile_diff(rd, 10), "RT", None, {}))
    defs.append((None, None, MSGR("25%"), 0, lambda rd: RuleData.get_percentile_diff(rd, 25), "RT", None, {}))
    defs.append((None, None, MSGR("50%"), 0, lambda rd: RuleData.get_percentile_diff(rd, 50), "RT", "VOS", {}))
    defs.append((None, None, MSGR("Avg"), 0, RuleData.get_average_diff, "RT", "VOT", {}))
    defs.append((None, None, MSGR("Max"), 0, RuleData.get_max_diff, "RT", "VOW", {}))

    return defs
