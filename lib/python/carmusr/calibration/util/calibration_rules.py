"""
Handling of calibration rules for reports and Custom-KPIs
"""
import os
import re
from collections import defaultdict

import carmensystems.rave.api as rave
from carmensystems.mave import etab
import Crs
from Localization import MSGR
from jcms.calibration import plan
import carmensystems.studio.cpmbuffer as cpmb

from carmusr.calibration import mappings
from carmusr.calibration.util import rave_code_explorer
from carmusr.calibration.util import basics
from carmusr.calibration.util import common
from carmusr.calibration.util import config_per_product


# Name of CalibrationRuleItem attributes and for registered attributes also the column names in the registration table.
RULE_NAME = "rule_name"
IS_VALID = "is_valid"
VALUE = "value"
LIMIT = "limit"
OP = "op"
STATION = "station"
BIN = "bin_p"
COMP_KEY = "comp_key"
CATEGORY = "category"
COMMENT = "comment"
DESCRIPTION = "description"


class CalibrationRuleContainer(object):

    def __init__(self, variant=None):

        self.variant = variant or common.CalibAnalysisVariants.Default.key

        self.all_rules = []
        self.all_rules_dict = {}

        self.registration_messages = defaultdict(list)

        self.station_rules = []
        self.station_rules_dict = {}

        all_available_rules = {}
        all_available_rules.update(rave_code_explorer.RuleInfoHandler().rules)
        all_available_rules.update(VirtualRulesHandler().rules)

        eh = CalibRuleRegistrationEtableHandler(variant)
        for row in eh.etable:
            try:
                rule_item = CalibrationRuleItem(all_available_rules, self.registration_messages, row)
            except CalibrationRuleItemError:
                continue
            self._add_rule_item(rule_item)
        self.refresh_of_reg_etable_is_recommended = eh.refresh_is_recommended

        # Temporary for backw. comp.
        self.fix_backw_params()

    def recreate_etab(self):
        CalibRuleRegistrationEtableHandler(self.variant).recreate_etab_from_cr(self)

    def fix_backw_params(self):
        """
        Temporary for backw. comp. of Rave parameter values.
        """
        for param_name in ("dist_rule", "station_rule", "vot_rule_1", "vot_rule_2", "vot_rule_3", "vot_rule_4", "vow_rule"):
            try:
                p = rave.param("report_calibration." + param_name)
            except rave.RaveError:
                continue
            v = p.value()
            if not (v.startswith("vot_") or v.startswith("vos_")):
                break
            v = v[4:]
            if v == "no_rule":
                p.setvalue(v)
                continue
            for cand in self.all_rules_dict:
                if v == cand.replace(".", "_"):
                    p.setvalue(cand)
                    break

    def _add_rule_item(self, rule_item):
        self._add_rule_item_to_all(rule_item)
        if getattr(rule_item, STATION):
            self._add_station_item(rule_item)

    def _add_rule_item_to_all(self, rule_item):
        self.all_rules.append(rule_item)
        key = rule_item.rule_key
        self.all_rules_dict[key] = rule_item

    def get_rule_item(self, key):
        return self.all_rules_dict[key]

    def _add_station_item(self, rule_item):
        self.station_rules.append(rule_item)
        key = rule_item.rule_key
        self.station_rules_dict[key] = rule_item

    def get_station_item(self, key):
            return self.station_rules_dict[key]

    def no_registered_rules_reason(self):
        if self.all_rules:
            return None
        if not self.registration_messages:
            return MSGR("No rules are registered for analysis")
        else:
            return MSGR("The loaded rule set doesn't provide any of the rules registered for analysis")


class VarOrExpr(object):

    re_module = re.compile(r"([\da-z_]*)\.%[\da-z_]+%")

    def __init__(self, rave_expr):
        self.expr_str = rave_expr
        # We use rave-variables if possible for performance.
        try:
            self.rave_obj = rave.var(rave_expr)
            if '%' not in self.expr_str:
                self.expr_str = "{}.%{}%".format(*tuple(rave_expr.split(".")))
        except rave.RaveError:
            self.rave_obj = rave.expr(rave_expr)

    def get_modules(self):
        return set(self.re_module.findall(self.expr_str))


class CalibrationRuleItemError(Exception):
    pass


class CalibrationRuleItem(object):
    """
    For rules which can't be used in calibration an CalibrationRuleItemError exception is raised.
    The attributes STATION, COMP_KEY and LB_CATEGORY may be None.
    """
    registered_attributes = ((RULE_NAME, rave_code_explorer._BasicRuleInfo),
                             (STATION, VarOrExpr),
                             (BIN, rave.param),
                             (COMP_KEY, rave.var),
                             (CATEGORY, rave.var),
                             (DESCRIPTION, str),
                             (COMMENT, str))

    derived_attributes = ((IS_VALID, VarOrExpr, "valid"),
                          (VALUE, VarOrExpr, "lhs"),
                          (LIMIT, VarOrExpr, "rhs"),
                          (OP, str, "op"),
                          ("rule_level", str, "level_name"),
                          ("rule_label", str, "label"))

    type2str = {VarOrExpr: "Rave variable or rave expression",
                rave.param: "Rave parameter",
                rave.var: "Rave variable"}

    def __init__(self, all_available_rules, reg_notes, erow):
        pconfig = config_per_product.get_config_for_active_product()
        rule_name = getattr(erow, RULE_NAME)
        if "." not in rule_name:
            module = None
        else:
            module = rule_name.split(".")[0]

        for attribute, attribute_type in self.registered_attributes:
            if attribute_type is str:
                setattr(self, attribute, self._get_attrib_as_string(erow, attribute))
                continue
            res = self._get_attrib_as_rave_string(erow, module, attribute, attribute_type)

            if attribute == RULE_NAME:
                self.rule_key = res.lower()
                if self.rule_key not in all_available_rules:
                    self.rule_key = res
                if self.rule_key not in all_available_rules:
                    fms = "The registered rule '%s' does not exist in the loaded rule set and is not a virtual rule. Ignored."
                    reg_notes[self.rule_key].append(RuleRegistrationMessage(2, fms % self.rule_key))
                    raise CalibrationRuleItemError
                rule = all_available_rules[self.rule_key]
                if rule.skip_silently:
                    fms = "The rule '%s' has been ignored. Details: %s"
                    rrm = RuleRegistrationMessage(2, fms % (self.rule_key, rule.fail_reason))
                    reg_notes[self.rule_key].append(rrm)
                    raise CalibrationRuleItemError
                if not rule.has_required_structure:
                    fms = "The rule '%s' is not implemented with the required structure. Ignored. Details: %s"
                    rrm = RuleRegistrationMessage(1, fms % (self.rule_key, rule.fail_reason))
                    reg_notes[self.rule_key].append(rrm)
                    raise CalibrationRuleItemError
                if rule.level_name not in pconfig.levels_dict:
                    fms = "The rule '{}' has a level, '{}', which is not supported in calibration. Ignored."
                    rrm = RuleRegistrationMessage(1, fms.format(self.rule_key, rule.level_name))
                    reg_notes[self.rule_key].append(rrm)
                    raise CalibrationRuleItemError
                setattr(self, attribute, rule)
                for attr_name, attr_type, attr_name_in_rule_object in self.derived_attributes:
                    setattr(self, attr_name, attr_type(getattr(rule, attr_name_in_rule_object)))
                continue

            if res is None:
                setattr(self, attribute, None)
                continue

            try:
                setattr(self, attribute, attribute_type(res))
            except rave.RaveError:
                setattr(self, attribute, None)
                level = 2 if attribute == CATEGORY else 1
                fm_s = "Registration of rule '%s'. %s '%s' for attribute '%s' does not exist in the loaded rule set."
                reg_notes[self.rule_key].append(RuleRegistrationMessage(level, fm_s % (self.rule_key, self.type2str[attribute_type], res, attribute)))

        if getattr(self, BIN) is None:
            msg = "The mandatory attribute '%s' is missing for the rule '%s'. The rule is ignored." % (BIN, self.rule_key)
            reg_notes[self.rule_key].append(RuleRegistrationMessage(1, msg))
            raise CalibrationRuleItemError

        value_type = basics.get_type_of_rave_expression(getattr(self, VALUE).expr_str)
        bin_type = type(getattr(self, BIN).value())
        if bin_type != value_type:
            s1 = "The attribute '%s' is not of the same type as the '%s'/'%s' attributes for the rule" % (BIN, VALUE, LIMIT)
            msg = "%s '%s'. The rule is ignored." % (s1, self.rule_key)
            reg_notes[self.rule_key].append(RuleRegistrationMessage(1, msg))
            raise CalibrationRuleItemError

        for attr in (COMP_KEY, CATEGORY):
            if getattr(self, attr) and (getattr(self, attr).level().name() != self.rule_level):
                msg = "Registration of rule '%s'. The attribute '%s', '%s' is not of the same level as the rule. Skipped." % (self.rule_key,
                                                                                                                              attr,
                                                                                                                              getattr(self, attr).name())
                reg_notes[self.rule_key].append(RuleRegistrationMessage(1, msg))
                setattr(self, attr, None)

        self._rule = getattr(self, RULE_NAME)
        self.rule_body_expr = rave.expr("%s %s %s" % (getattr(self, VALUE).expr_str,
                                                      getattr(self, OP),
                                                      getattr(self, LIMIT).expr_str))
        self.op_with_equal_sign = "=" in getattr(self, OP)
        self.bin_value = getattr(self, BIN).value()
        self.data_type = type(self.bin_value)
        self.bin_resolution = self.data_type(1)
        self.min_diff_for_bin_one = self.data_type(0 if self.op_with_equal_sign else 1)
        self.max_diff_for_bin_one = self.min_diff_for_bin_one + self.bin_value - self.bin_resolution

        self.cat_var = getattr(self, CATEGORY)
        self.cat_rank_var = basics.get_rave_variable("{}_rank".format(self.cat_var.name())) if self.cat_var else None
        self.cat_color_var = basics.get_rave_variable("{}_color".format(self.cat_var.name())) if self.cat_var else None

    @staticmethod
    def _get_attrib_as_string(erow, attribute):
        if not hasattr(erow, attribute):
            return None
        return (getattr(erow, attribute) or "").strip(" ") or None

    def _get_attrib_as_rave_string(self, erow, module, attribute, attr_type):
        val = self._get_attrib_as_string(erow, attribute)

        if val is None:
            return None

        if attr_type is VarOrExpr:
            try:
                rave.expr(val)
                return val
            except rave.RaveError:
                pass

        if ("." not in val) and module:
            val = "%s.%s" % (module, val)
        return val


class RuleRegistrationMessage(object):

    level2str = {1: "Error",
                 2: "Note"}

    def __init__(self, level, message):
        self.level = level
        self.message = message


class CalibRuleRegistrationEtableHandler(object):

    def __init__(self, variant_key=None):
        self.refresh_is_recommended = False
        self.variant_class = common.CalibAnalysisVariants.key2class(variant_key)
        self.column_names = (RULE_NAME,
                             BIN,
                             STATION,
                             COMP_KEY,
                             CATEGORY,
                             DESCRIPTION,
                             COMMENT)
        self._etable_real_path = self.get_etab_path(variant_key)
        if not os.path.exists(self._etable_real_path):
            self.create_empty_table()
            self.save_etable()
        else:
            self.etable = etab.load(etab.Session(), self._etable_real_path)
            self._check_update_need_and_fix_backward_comp()  # Temporary while supporting the old column name "lb_category"

    def _check_update_need_and_fix_backward_comp(self):
        col_names_in_loaded_table = set(c.getName() for c in self.etable.getColumns())
        if col_names_in_loaded_table != set(self.column_names):
            self.refresh_is_recommended = True
        if self.etable.getComment() != self.get_header_text():
            self.refresh_is_recommended = True

        old_name_of_category = "lb_category"
        if old_name_of_category in col_names_in_loaded_table:
            self.etable.appendColumn(CATEGORY, str)
            for row in self.etable:
                setattr(row, CATEGORY, getattr(row, old_name_of_category))
            self.etable.removeColumn(old_name_of_category)

    def create_empty_table(self):
        self.etable = etab.create(etab.Session(), self._etable_real_path, self.get_header_text())
        for col_name in self.column_names:
            self.etable.appendColumn(col_name, str)

    def recreate_etab_from_cr(self, cr):
        self.create_empty_table()
        for cri in cr.all_rules:
            self._add_row(cri)
        self.save_etable()

    def _add_row(self, cri):

        def get_val(attr):
            obj = getattr(cri, attr)
            if obj is None:
                return ""
            tup = tuple(obj.name().split("."))
            rule_module = cri._rule.name.split(".")[0]
            if tup[0] != rule_module:
                return "%s.%s" % tup
            return tup[1]

        self.etable.append((cri._rule.name,
                            get_val(BIN),
                            getattr(cri, STATION).expr_str if getattr(cri, STATION) else "",
                            get_val(COMP_KEY),
                            get_val(CATEGORY),
                            getattr(cri, DESCRIPTION) or "",
                            getattr(cri, COMMENT) or ""))

    def save_etable(self):
        self.etable.save()

    def get_header_text(self):
        rows = ['',
                'Registration of rules for %s reports.' % self.variant_class.title,
                '',
                'The columns:',
                '  "rule_name" - The rule in rave, "module.name" or the name of a virtual rule.',
                '  "bin_p" - rave parameter defining the bin size for the rule.',
                '  "station" - If the rule should be analysed in the report "violations over station" this attribute has to be defined.',
                '                  Rave expression or rave variable.',
                '  "comp_key" - rave variable returning a comparison key, to compare planned and actual (reference) chains.',
                '                     Used in reports for flown pairings. E.g. for a connection rule, use a key comparing the legs in the connection.',
                '  "category" - rave variable (any data type) returning a category for a violation',
                '                     e.g. classification depending on delay code.',
                '                     It should also be accompanied with:',
                '                      - a rank (any data type) variable, for ordering the categories, '
                'named the same as the category with a suffix "_rank".',
                '                      - a string colour variable, returning a colour name or an RGB code, named the same as the'
                'category with a suffix "_color".',
                '  "description" - A text with details displayed to the user (\\n can be used for newline in the text).',
                '  "comment" - Not used by the programs.',
                '',
                'Note:',
                " * Format for Rave variable/parameter: 'module.[%]name[%]' (or '').",
                "    For objects found in the same module as the rule just '[%]name[%]' is allowed too.",
                ' * "rule_name" and "bin_p" are mandatory.',
                " * The table is common for all rule sets. Registered rules which don't exist in a rule set are simply ignored.",
                '']

        return "\n".join(rows)

    @staticmethod
    def get_etab_path(variant_key=None):
        return _get_etab_path("calibration", common.CalibAnalysisVariants.key2class(variant_key).crs_table_name)


class VirtualRule(rave_code_explorer._BasicRuleInfo):

    def __init__(self, etab_row, tbh, pconfig):
        self.name = etab_row.name
        self.has_required_structure = True
        self.fail_reason = None
        self.valid = etab_row.valid
        self.lhs = etab_row.value
        self.rhs = etab_row.limit
        self.op = etab_row.op
        self.label = etab_row.remark
        self.level_name = None
        self.skip_silently = False

        def set_attributes_when_fail(reason):
            self.has_required_structure = False
            self.valid = self.lhs = self.rhs = self.op = None
            self.fail_reason = reason

        if etab_row.skip_if_fail:
            try:
                rave.expr(etab_row.skip_if_fail)
            except rave.RaveError:
                set_attributes_when_fail("The 'skip_if_fail' expression, '%s', fails." % etab_row.skip_if_fail)
                self.skip_silently = True
                return

        if not self.valid:
            self.valid = "true"

        for exp, name in ((self.valid, "VALID"), (self.lhs, "LHS"), (self.rhs, "RHS")):
            try:
                rave.expr(exp)
            except (rave.ParseError, TypeError):
                set_attributes_when_fail("Incorrect %s. Expression not supported by Rave interpreter, '%s'." % (name, exp))
                return

        if not basics.is_boolean_rave_expression(self.valid):
            set_attributes_when_fail("Incorrect VALID. Expression most be boolean, '%s'." % self.valid)
            return

        if etab_row.op not in (">=", "<=", ">", "<"):
            set_attributes_when_fail("Incorrect operator '%s'. Use one of '>=', '<=', '>', '<'" % etab_row.op)
            return

        body_expr_str = "%s %s %s" % (self.lhs, self.op, self.rhs)
        try:
            body_expr = rave.expr(body_expr_str)
        except rave.ParseError:
            set_attributes_when_fail("Incorrect rule body expression. Expression not supported by Rave interpreter, '%s'." % body_expr_str)
            return

        # Note. We assume that the levels are hierarchical and that the first is OK for all rules.
        self.level_name = pconfig.levels_ordered[0].name
        for level_candidate in (le.name for le in pconfig.levels_ordered[1:]):
            my_bag_iterator = iter(common.get_atomic_iterator_for_level(tbh.bag, level_candidate)())
            bag = next(my_bag_iterator)
            try:
                rave.eval(bag, body_expr)
                rave.eval(bag, self.valid)
                self.level_name = level_candidate
            except rave.UsageError:
                break
            finally:
                del my_bag_iterator


class VirtualRulesHandler(object):

    _handlers = {}

    column_names = ("name",
                    "skip_if_fail",
                    "remark",
                    "valid",
                    "value",
                    "op",
                    "limit",
                    "comment")

    def __new__(cls):
        rule_set_name = rave.eval("rule_set_name")[0]
        if not (rule_set_name in cls._handlers and cls._handlers[rule_set_name]._is_up_to_date()):
            handler_candidate = object.__new__(cls)
            cls._my_init(handler_candidate, rule_set_name)
            cls._handlers[rule_set_name] = handler_candidate
        return cls._handlers[rule_set_name]

    def __init__(self):
        pass

    @staticmethod
    def get_etab_path():
        return _get_etab_path("calibration", "VirtualRulesDefintionTable")

    def _my_init(self, rule_set_name):
        self._rule_set_name = rule_set_name
        self.rules = {}
        self._doc_file_path = os.path.expandvars('$CARMTMP/crc/rule_set/GPC/%s.xml' % self._rule_set_name)  # created by normal Rave compilation.
        self._saved_compile_time = os.path.getmtime(self._doc_file_path)
        self._etable_real_path = self.get_etab_path()
        if not os.path.exists(self._etable_real_path):
            self.create_empty_table()
        else:
            self._etable = etab.load(etab.Session(), self._etable_real_path)
        self._etab_change_time = os.path.getmtime(self._etable_real_path)

        tbh = OneLegInOneLegSet()  # It takes time to create a one leg context so we do it just once.
        pconfig = config_per_product.get_config_for_active_product()

        if not tbh.bag:
            raise Exception("Calibration: A local plan which not is empty must be loaded for calculation of the level of virtual rules.")

        for row in self._etable:
            self.rules[row.name] = VirtualRule(row, tbh, pconfig)

    def _is_up_to_date(self):
        return (os.path.getmtime(self._doc_file_path) == self._saved_compile_time and
                os.path.exists(self._etable_real_path) and
                os.path.getmtime(self._etable_real_path) == self._etab_change_time and
                self._etable_real_path == self.get_etab_path())

    def create_empty_table(self):
        etab_comment = ("Definition of virtual rules.\n"
                        "Virtual rules behave as Rave rules in the Calibration reports (but without a rule defined in the Rave code).\n"
                        "Virtual rules can be used in calibration rule registration tables.\n"
                        "Columns:\n"
                        "name........: Any string identifying the virtual rule.\n"
                        "skip_if_fail: Optional. A Rave expression. If the expression fails the rule is silently skipped.\n"
                        "remark......: Label of the rule. Used in reports.\n"
                        "valid.......: A boolean Rave expression.\n"
                        "value.......: A Rave expression.\n"
                        "op..........: <=, >=, > or <\n"
                        "limit.......: A Rave expression.\n"
                        "comment.....: Not used by the programs.")
        self._etable = etab.create(etab.Session(), self._etable_real_path, etab_comment)
        for col_name in self.column_names:
            self._etable.appendColumn(col_name, str)
        self._etable.save()


# We need a bag based on a small context to get acceptable performance
# when we calculate level dependency of the virtual rules.
class OneLegInOneLegSet(mappings.bag_handler.PlanLegSets):

    def __init__(self):

        super(OneLegInOneLegSet, self).__init__()

        if self.has_warning():
            return

        for atom_bag in self.bag.atom_set():
            first_leg_id = rave.eval(atom_bag, rave.keyw("leg_identifier"))[0]
            break

        one_leg_buf = cpmb.CpmBuffer()
        one_leg_buf.fillAnyLevel(self._buf, "leg_identifier = %s" % first_leg_id)
        self._buf = one_leg_buf
        self.bag = rave.buffer2context(self._buf).bag()


def _get_etab_path(crs_module, crs_name):
    p = Crs.CrsGetModuleResource(crs_module, Crs.CrsSearchModuleDef, crs_name)
    if p is None:
        raise AttributeError("The mandatory CRS resource '%s.%s' is not defined." % (crs_module, crs_name))

    if plan.sub_plan_is_loaded():
        alternative_path = os.path.join(basics.get_sp_local_etab_dir(),
                                        get_sp_local_directory_for_rule_def_etables(),
                                        os.path.basename(p))
        if os.path.exists(alternative_path):
            return alternative_path

    return p


def get_sp_local_directory_for_rule_def_etables():
    return Crs.CrsGetModuleResource("calibration", Crs.CrsSearchModuleDef, "SpLocalDirForRuleRegTables") or "SpLocal/system"
