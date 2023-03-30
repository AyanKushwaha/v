'''
Created on 21 Apr 2020

@author: Stefan Hammar

Some code to extract information about rules in the loaded rule set. The following sources are used:
* An XML-file per rule set (produced on demand using the Rave compiler).
* Rave source files.
* The loaded rule-set.
'''

import os
import re
from lxml import etree
import time

import carmensystems.basics.l10n.utilities as l10n_util
import carmensystems.rave.api as rave
import Errlog
import Names


class _BasicRuleInfo(object):
    """
    Mandatory attributes:
    'name', 'level_name', 'label' : str
    'has_required_structure': Boolean
    'valid', 'rhs' and 'lhs': String with Rave expression (None if 'has_required_structure' is False).
    'op': str (None if 'has_required_structure' is False).
    'fail_reason': str or None
    'skip_silently' : boolean
    """

    def content_string(self):
        if self.has_required_structure:
            return " Valid: '{}'\n LHS  : '{}'\n Op   : '{}'\n RHS  : '{}'\n Level: '{}'\n Label: '{}'".format(self.valid,
                                                                                                               self.lhs,
                                                                                                               self.op,
                                                                                                               self.rhs,
                                                                                                               self.level_name,
                                                                                                               self.label)
        else:
            return " F: '%s'" % self.fail_reason


class Rule(_BasicRuleInfo):

    re_comment = re.compile(r"/\*.*?\*/", re.DOTALL | re.MULTILINE)
    op_expr = r"[><]=?"
    re_op = re.compile(op_expr)
    re_white_space = re.compile(r"\s+", re.DOTALL | re.MULTILINE)
    re_exception = re.compile(r"(?:start|end)(?:date|day)\s*=[^;]+?;", re.DOTALL | re.MULTILINE)
    re_variable = re.compile(r"[\da-z_]*\.?%[\da-z_]+%")

    def __init__(self, name, file_path, rave_compile_time):
        self.name = l10n_util.encode(name)
        self._file_path = l10n_util.encode(file_path)
        self.skip_silently = False  # Only used for virtual rules (to imitate a not existing real rule).
        self._rave_compile_time = rave_compile_time
        self._child_module = {}  # Used to add module name to variables in Rave expressions

    @staticmethod
    def lower_except_string_literals(text):
        st = text.split('"')
        for n in xrange(0, len(st), 2):
            st[n] = st[n].lower()
        return '"'.join(st)

    def add_child(self, child_full_name):
        child_full_name = l10n_util.encode(child_full_name)
        if child_full_name.find(".") == -1:  # Skip if keyword
            return
        child_module, child_name = tuple(child_full_name.split("."))
        if (child_name in self._child_module) and (child_module != self.name.split(".")[0]):  # Corner case
            return
        self._child_module[child_name] = child_module

    def __getattr__(self, name):
        if name in ("lhs", "rhs", "valid", "op", "has_required_structure", "fail_reason", "label", "level_name"):
            self._calc_attributes()
            return getattr(self, name)
        raise AttributeError("The class 'Rule' has no attribute '{}'".format(name))

    def _calc_attributes(self):

        def set_attributes_when_fail(reason):
            self.has_required_structure = False
            self.valid = self.lhs = self.rhs = self.op = None
            self.fail_reason = reason

        try:
            rave_rule = rave.rule(self.name)
            self.label = rave_rule.remark() or self.name
            self.level_name = rave_rule.level().name()
        except rave.UsageError:
            self.label = "-"
            self.level_name = "-"
            set_attributes_when_fail("Rule not found in the loaded rule set. Please recompile and reload the rule set.")
            return

        if not os.path.exists(self._file_path):
            set_attributes_when_fail("Rave source file '{}' does not exist. Please recompile and reload the rule set.".format(self._file_path))
            return

        if os.path.getmtime(self._file_path) > self._rave_compile_time:
            fms = "{}. Warning in '{}'. The Rave file '{}' has been changed since the rule set was created. Please compile and reload the rule set."
            Errlog.log(fms.format("CALIBRATION", __name__, os.path.basename(self._file_path)))

        with open(self._file_path) as rave_file:
            file_text = rave_file.read()
        file_text = self.re_comment.sub("", file_text)
        file_text = self.lower_except_string_literals(file_text)
        file_text = self.re_exception.sub("", file_text)

        re_rule_start = r"rule\s*(?:[(ofn)]*)\s*%s\s*=" % self.name.split(".")[1]
        re_expr_valid = r"(?:\s*valid\s*([^;]*?)\s*;)?"
        re_expr_body = r"\s*([^;]*?)\s*;"
        s = r"%s%s%s" % (re_rule_start, re_expr_valid, re_expr_body)
        reg = re.compile(s, re.DOTALL | re.MULTILINE)
        matches = reg.findall(file_text)
        if not matches:
            set_attributes_when_fail("Rule not found in the Rave source code. Please recompile and reload the rule set.")
            return
        self.valid, body = (self._fix_of_expr(exp) for exp in matches[0])
        split_body = self.re_op.split(body)
        if len(split_body) != 2:
            set_attributes_when_fail("Rule body should be on format 'LHS {} RHS'. Is '{}'.".format(self.op_expr, body))
            return

        if self.valid == "":  # No valid statement
            self.valid = "true"

        self.lhs, self.rhs = (it.strip() for it in split_body)

        for exp, name in ((self.valid, "VALID"), (self.lhs, "LHS"), (self.rhs, "RHS")):
            try:
                rave.expr(exp)
            except rave.ParseError:
                set_attributes_when_fail("Incorrect {}. Expression not supported by Rave interpreter, '{}'.".format(name, exp))
                return
        self.op = self.re_op.findall(body)[0]

        self.has_required_structure = True
        self.fail_reason = None

    def _fix_of_expr(self, exp_string):
        exp_string = self.re_white_space.sub(" ", exp_string).strip()
        exp_string = self.re_variable.sub(self._add_module_name, exp_string)
        return exp_string

    def _add_module_name(self, matchobj):
        var_str = matchobj.group(0)
        if "." in var_str:
            return var_str
        return "{}.{}".format(self._child_module.get(var_str, "failed_to_find"), var_str)  # Not compiled Rave changes may give "failed_to_find".


class MyTarget(object):

    def __init__(self, compile_time):
        self.rules = {}
        self.current_rule = None
        self.compile_time = compile_time

    def start(self, tag, attrib):
        if tag == "Child" and self.current_rule:
            self.current_rule.add_child(attrib.get("name"))
        elif tag == "Entry" and attrib.get("class") == "rule":
            self.current_rule = Rule(attrib.get("name"), attrib.get("filename"), self.compile_time)
            self.rules[self.current_rule.name] = self.current_rule

    def end(self, tag):
        if tag == "Entry":
            self.current_rule = None

    def data(self, data):
        pass

    def close(self):
        return self.rules


class RuleInfoHandler(object):
    """
    Extracts information about all rules found in an XML-xref-file created by the Rave compiler.
    The attribute "rules" (a dictionary with rule name as key and Rule object as value)
    is the only "exported" attribute.
    """
    _handlers = {}

    def __new__(cls):
        rule_set_name = rave.eval("rule_set_name")[0]
        if not (rule_set_name in cls._handlers and cls._handlers[rule_set_name].instance_can_be_kept()):
            cls._handlers[rule_set_name] = object.__new__(cls)
            cls._my_init(cls._handlers[rule_set_name], rule_set_name)
        return cls._handlers[rule_set_name]

    def __init__(self):
        pass

    def _my_init(self, rule_set_name):
        Errlog.log("CALIBRATION. Log. A new instance of the RuleInfoHandler class will be created.")
        self._rule_set_name = rule_set_name
        self._xref_file_path = os.path.expandvars('$CARMTMP/crc/rule_set/GPC/{}_xref_CALIBRATION.xml'.format(self._rule_set_name))
        self._xref_file_path_lock = self._xref_file_path + ".lck"
        self.refresh_xref_file()
        self._creation_time_for_used_xref_file = os.path.getmtime(self._xref_file_path)
        self.rules = etree.parse(self._xref_file_path, etree.XMLParser(target=MyTarget(self.get_compilation_time_for_rule_set())))
        Errlog.log("CALIBRATION. Log. A new instance of the RuleInfoHandler class has been created.")

    def instance_can_be_kept(self):
        return self.xml_file_is_up_to_date() and self.xml_file_is_still_the_same()

    def xml_file_is_up_to_date(self):
        return os.path.exists(self._xref_file_path) and os.path.getmtime(self._xref_file_path) > self.get_compilation_time_for_rule_set()

    def xml_file_is_still_the_same(self):
        return self._creation_time_for_used_xref_file == os.path.getmtime(self._xref_file_path)

    def get_compilation_time_for_rule_set(self):
        doc_file_path = os.path.expandvars('$CARMTMP/crc/rule_set/GPC/{}.xml'.format(self._rule_set_name))
        return os.path.getmtime(doc_file_path)

    def refresh_xref_file(self):
        if self.xml_file_is_up_to_date():
            return
        if self.acquire_creation_lock_or_wait():
            self.do_create_xref_file()
            os.unlink(self._xref_file_path_lock)

    def acquire_creation_lock_or_wait(self):
        # Returns True if we have acquired the lock.
        my_lock_file_source = "{}.{}.{}".format(self._xref_file_path_lock, Names.hostname(), os.getpid())
        os.system("touch {}".format(my_lock_file_source))
        try:
            os.link(my_lock_file_source, self._xref_file_path_lock)
            lock_acquired = True
        except OSError:
            lock_acquired = False
        os.unlink(my_lock_file_source)
        if not lock_acquired:
            lock_acquired = self.wait_for_lock_but_also_take_over_very_old_lock()
        return lock_acquired

    def wait_for_lock_but_also_take_over_very_old_lock(self):
        # Returns True if an old lock file has been taken over.
        while True:
            now = time.time()
            mod_time_lock_file = self.get_mod_time_if_file_exists(self._xref_file_path_lock)
            if mod_time_lock_file is None:
                return False
            age_of_lock_file = now - mod_time_lock_file
            if age_of_lock_file > 30:  # This should never happen under normal circumstances.
                Errlog.log("CALIBRATION. Warning. An old lock file for XML file generation has been taken over.")
                os.utime(self._xref_file_path_lock, None)
                return True
            Errlog.log("CALIBRATION. Log. Waiting for XML file generation lock file to be removed.")
            time.sleep(2)

    @staticmethod
    def get_mod_time_if_file_exists(f):
        try:
            return os.path.getmtime(f)
        except OSError:
            return None

    def do_create_xref_file(self):
        Errlog.log("CALIBRATION. Log. Creating XML-file using the Rave compiler.")
        xref_file_path_tmp = "{}.{}.{}.{}".format(self._xref_file_path, "tmp", Names.hostname(), os.getpid())
        cmd = '$CARMSYS/bin/crc_compile -skipcompilation -xmldefinitions {} -gpc $CARMUSR/crc/source/{}'.format(xref_file_path_tmp,
                                                                                                                self._rule_set_name)
        if os.system(cmd):
            Errlog.log("CALIBRATION. Error. Problems when producing XML-file. May cause all kinds of problems.")
            Errlog.log("             Please correct the Rave code and recompile the rule set to avoid problems.")
        if os.path.exists(xref_file_path_tmp):
            os.rename(xref_file_path_tmp, self._xref_file_path)


if __name__ == "__main__":
    import carmusr.calibration.util.rave_code_explorer as me  # @UnresolvedImport
    rh = me.RuleInfoHandler()
    for rule_name in sorted(rh.rules):
        Errlog.log("")
        Errlog.log(rule_name)
        Errlog.log(rh.rules[rule_name].content_string())
        break
