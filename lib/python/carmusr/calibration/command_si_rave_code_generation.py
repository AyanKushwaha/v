"""
Calibration Rave code generation for SI components.
"""
import os
from collections import defaultdict

import Errlog
import carmensystems.rave.api as rave
from carmensystems.mave import etab
import Gui

from carmusr.calibration.util import config_per_product
from carmusr.calibration.util import basics
from carmusr.calibration.util import rave_code_explorer
from carmusr.calibration.util import calibration_rules as calib_rules


# Column name in registration etable
SI_COMPONENT = "si_component"

RAVE_PARENT_MODULE_NAME = "calibration_mappings"
RAVE_MODULE_SUFFIX_VARIABLE = "calibration_mappings.generated_files_suffix"


class SIRegistrationHandler(object):

    def __init__(self):
        si_comps = config_per_product.get_config_for_active_product().si_components
        self.si_components_dict = dict((si_comp.name, si_comp) for si_comp in si_comps)
        self.supported_si_components = set(sic.name for sic in si_comps)
        self.ordered_supported_si_components = sorted(self.supported_si_components, reverse=True)
        self.level_per_supported_si_component = dict((sic.name, sic.level) for sic in si_comps)

        self.si_component_rules = defaultdict(list)
        self.registration_messages = []
        self.populate()

    def get_label_for_component_rule(self, component_name):
        return self.si_components_dict[component_name].calib_component_rule_ref

    def populate(self):
        all_available_rules = {}
        all_available_rules.update(rave_code_explorer.RuleInfoHandler().rules)
        all_available_rules.update(calib_rules.VirtualRulesHandler().rules)

        for ix, etab_row in enumerate(SIRegistrationEtableHandler().etable, 1):
            rule_name = getattr(etab_row, calib_rules.RULE_NAME)
            si_comp = getattr(etab_row, SI_COMPONENT)
            if si_comp not in self.supported_si_components:
                fms = "Found SI component '{}' on row {}. The only supported SI component{} {}. The row will be ignored."
                mess = fms.format(si_comp, ix,
                                  " is" if len(self.ordered_supported_si_components) <= 1 else "s are",
                                  " and ".join("'{}'".format(v) for v in self.ordered_supported_si_components))
                self.registration_messages.append(mess)
                continue
            if rule_name not in all_available_rules:
                fms = "The registered rule '{}' on row {} does not exist in the loaded rule set and is not a virtual rule. The row will be ignored."
                mess = fms.format(rule_name, ix)
                self.registration_messages.append(mess)
                continue
            rule = all_available_rules[rule_name]
            if not rule.has_required_structure:
                fms = "The registered rule '{}' on row {} is not implemented with the required structure. The row will be ignored."
                mess = fms.format(rule_name, ix)
                self.registration_messages.append(mess)
                continue
            if rule.level_name != self.level_per_supported_si_component[si_comp]:
                fms = "The registered rule '{}' on row {} is on level '{}'. The SI component '{}' requires level '{}'. The row will be ignored."
                mess = fms.format(rule_name, ix, rule.level_name, si_comp, self.level_per_supported_si_component[si_comp])
                self.registration_messages.append(mess)
                continue
            self.si_component_rules[si_comp].append(SICompRule.create_from_basic_rule_info(rule, si_comp))

        for si_comp in self.ordered_supported_si_components:
            if not self.si_component_rules[si_comp]:
                mess = "No accepted rule registration found for the si component '{}'. Fallback code will be produced.".format(si_comp)
                self.registration_messages.append(mess)
                self.si_component_rules[si_comp].append(SICompRule(si_comp, **self.si_components_dict[si_comp].fallback._asdict()))

    def get_si_enums_rows(self):
        rows = [""]
        for key in self.ordered_supported_si_components:
            rows += self.get_si_component_enum_rows(self.si_component_rules[key], key)
        return rows

    def get_si_component_enum_rows(self, items, component):
        comp_str = "si_%s" % component
        rows = ["export enum enum_%s =" % comp_str]
        items.sort(key=lambda x: x.rule_label)
        for ri in items:
            rows += ri.get_si_comp_enum_rows()
            e_name = ri.get_si_comp_enum()
        rows += ['    remark "Pick rule for SI component %s";' % component,
                 'end',
                 "",
                 "export %%%s_rule_p%% =" % comp_str,
                 "    parameter %s" % e_name,
                 '    remark "Retrieve value, limit and valid statement for rule {} from";'.format(self.get_label_for_component_rule(component)),
                 ""]
        return rows

    def get_si_mappings_rows(self):
        rows = []
        for si_comp in self.ordered_supported_si_components:
            rows += self.get_si_component_mapping_rows(self.si_component_rules[si_comp], si_comp)
        return rows

    def get_si_component_mapping_rows(self, si_component_rules, si_component_name):

        rows = ["table %s_mapping =" % si_component_name,
                "    %%si_%s_rule_p%% ->" % si_component_name]
        rows += ["        export %%%s_valid%%," % si_component_name,
                 "        export %%%s_value%%," % si_component_name,
                 "        export %%%s_limit%%;" % si_component_name]
        for si_comp_rule in si_component_rules:
            rows += si_comp_rule.get_si_table_rows()
        rows += ["end",
                 ""]
        return rows

    def get_all_required_si_import_rows(self):
        rows = [""]
        rave_modules = set()
        for si_comp_rules in self.si_component_rules.itervalues():
            for si_comp_rule in si_comp_rules:
                rave_modules |= si_comp_rule.rave_modules
        for module in sorted(rave_modules):
            if module != "calibration_mappings":
                rows += ["import %s;" % module]
        rows += [""]
        return rows

    def get_table_info_rows(self):
        return ["   Registrations made in the file '%s'" % SIRegistrationEtableHandler.get_etab_path_nice_format(),
                "   were considered."]

    def get_all_rave_code_rows_as_list(self):
        rows = ["/* -*- crc -*- */",
                "",
                "/*",
                "   The Rave code in this module has been generated by",
                "   the class '%s' in" % self.__class__.__name__,
                "   '%s'." % python_module_file_name()]
        rows += self.get_table_info_rows()
        rows += ["   Don't change this file manually. Modify the source and regenerate it instead.",
                 "   Use the command 'Admin Tools> Calibration Admin> Generate SI Rave Module[, Fallback Version]' to generate.",
                 "*/",
                 "",
                 "module %s inherits %s" % (self.get_rave_module_name(), RAVE_PARENT_MODULE_NAME),
                 ""]
        rows += self.get_all_required_si_import_rows()
        rows += self.get_si_enums_rows()
        rows += [""]
        rows += self.get_si_mappings_rows()
        return rows

    def get_rave_code_as_string(self):
        attr_name = "_rave_code_as_string"
        if not hasattr(self, attr_name):
            setattr(self, attr_name, "\n".join(self.get_all_rave_code_rows_as_list()))
        return getattr(self, attr_name)

    @staticmethod
    def get_rave_module_name():
        try:
            suffix = rave.eval(RAVE_MODULE_SUFFIX_VARIABLE)[0]
        except rave.RaveError:
            suffix = "_gen"
        return "%s_si%s" % (RAVE_PARENT_MODULE_NAME, suffix)

    @classmethod
    def get_rave_module_full_path_nice_format(cls):
        directory = "$CARMUSR/crc/modules"
        module_name = cls.get_rave_module_name()
        return os.path.join(directory, module_name)

    @classmethod
    def get_rave_module_full_path(cls):
        return os.path.expandvars(cls.get_rave_module_full_path_nice_format())

    @classmethod
    def rave_module_exist(cls):
        return os.path.exists(cls.get_rave_module_full_path())

    def rave_module_is_up_to_date(self):
        if not self.rave_module_exist():
            return False

        with open(self.get_rave_module_full_path(), "r") as f:
            prev_cont = f.read()

        return prev_cont == self.get_rave_code_as_string()


class SIRegistrationPureFallbackHandler(SIRegistrationHandler):

    def populate(self):
        for si_comp in self.ordered_supported_si_components:
            self.si_component_rules[si_comp].append(SICompRule(si_comp, **self.si_components_dict[si_comp].fallback._asdict()))

    def get_table_info_rows(self):
        return ["   A fallback version of the code was requested. The registration table was not considered."]


class SICompRule(object):

    def __init__(self, si_comp, rule_name, valid_str, lhs_str, rhs_str, rule_label, rave_modules):
        self.si_comp = si_comp
        self.rule_name = rule_name
        self.valid_str = valid_str
        self.lhs_str = lhs_str
        self.rhs_str = rhs_str
        self.rule_label = rule_label
        self.rave_modules = rave_modules

    @classmethod
    def create_from_basic_rule_info(cls, basic_rule_info, si_comp):
        valid = calib_rules.VarOrExpr(basic_rule_info.valid)
        lhs = calib_rules.VarOrExpr(basic_rule_info.lhs)
        rhs = calib_rules.VarOrExpr(basic_rule_info.rhs)
        rave_modules = valid.get_modules() | lhs.get_modules() | rhs.get_modules()
        return cls(si_comp,
                   basic_rule_info.name,
                   valid.expr_str,
                   lhs.expr_str,
                   rhs.expr_str,
                   basic_rule_info.label,
                   rave_modules)

    def get_si_comp_enum(self):
        enum_str = "si_%s_%s" % (self.si_comp, self.rule_name.replace(".", "_"))
        return enum_str.lower()

    def get_si_comp_enum_rows(self):
        return get_enum_item_rows(self.get_si_comp_enum(), self.rule_label)

    def get_si_table_rows(self):
        rows = ["",
                "    %s ->" % self.get_si_comp_enum()]
        rows += ["        ({})".format(self.valid_str),  # We must survive rules where rhs or lhs is void when valid is True.
                 "        and not void({})".format(self.lhs_str),
                 "        and not void({}),".format(self.rhs_str),
                 "        {},".format(self.lhs_str),
                 "        {};".format(self.rhs_str)]
        return rows


def get_enum_item_rows(enum, remark):
    rows = ["    %s" % enum,
            '        remark "%s";' % remark]
    return rows


class SIRegistrationEtableHandler(object):

    def __init__(self):
        self.column_names = (calib_rules.RULE_NAME,
                             SI_COMPONENT,
                             calib_rules.COMMENT)
        self._etable_real_path = self.get_etab_path()
        if not os.path.exists(self._etable_real_path):
            self.create_empty_table()
            self.etable.save()
        else:
            self.etable = etab.load(etab.Session(), self._etable_real_path)

    def create_empty_table(self):
        self.etable = etab.create(etab.Session(), self._etable_real_path, self.get_header_text())
        for col_name in self.column_names:
            self.etable.appendColumn(col_name, str)

    def get_header_text(self):
        rows = [""]
        rows.append("Registration of rules for SI index.")
        rows += ["",
                 'The columns:',
                 '  "rule_name" - The rule in rave, "module.name" or the name of a virtual rule.',
                 '  "si_component" - Name of si-component the rule should be mapped to.',
                 '  "comment" - Not used by the programs.',
                 "",
                 "Note:",
                 " * Rave variables/parameters used in rules registered for use in SI index must be exported.",
                 ""]
        return "\n".join(rows)

    @staticmethod
    def get_etab_path():
        return calib_rules._get_etab_path("calibration", "SensitivityIndexRegistrationTable")

    @classmethod
    def get_etab_path_nice_format(cls):
        return basics.get_nice_looking_path(cls.get_etab_path())


def create_rave_module(pure_fallback=False):
    if pure_fallback:
        si_handler = SIRegistrationPureFallbackHandler()
        msg = "Generate SI Rave Module, Fallback Version\n\n"
    else:
        if basics.no_or_empty_local_plan():
            Errlog.set_user_message("The command requires a loaded local plan which not is empty.")
            return
        si_handler = SIRegistrationHandler()
        msg = "Generate SI Rave Module\n\n"

    if si_handler.rave_module_is_up_to_date():
        Errlog.set_user_message(msg + "'%s' is already up-to-date." % (si_handler.get_rave_module_full_path_nice_format()))
        return

    if si_handler.rave_module_exist():
        action_string = "replaced"
    else:
        action_string = "created"

    message_txts = []
    if si_handler.registration_messages:
        message_txts = [" * " + message for message in si_handler.registration_messages]
        msg += "Problem(s) found in '{}':\n".format(SIRegistrationEtableHandler.get_etab_path_nice_format())
        msg += "\n".join(message_txts)
        msg += "\n\n"

    msg += "'%s' will be %s. Continue?" % (si_handler.get_rave_module_full_path_nice_format(), action_string)
    if not Gui.GuiYesNo(__name__, msg):
        return

    with open(si_handler.get_rave_module_full_path(), "w") as f:
        f.write(si_handler.get_rave_code_as_string())

    msg = "'%s' has been %s.\n" % (si_handler.get_rave_module_full_path_nice_format(), action_string)
    msg += "Please compile and reload the rule set."
    Errlog.set_user_message(msg)


def python_module_file_name():
    module_path = __file__
    if module_path.endswith("pyc") or module_path.endswith("pyo"):
        module_path = module_path[:-1]
    module_path = module_path.replace(os.path.expandvars("$CARMUSR"), "$CARMUSR")
    return module_path


if __name__ == '__main__':
    import carmusr.calibration.command_si_rave_code_generation as me  # @UnresolvedImport
    me.create_rave_module(pure_fallback=False)
