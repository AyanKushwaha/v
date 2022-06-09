

"""
TEST REPORT

Use this report to see which rule category (alert group) the 
different rules will fall into.
"""


import Cui
import re

import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave

from report_sources.include.SASReport import SASReport


class Report(SASReport):
    def create(self):
        SASReport.create(self, 'Rule Categories (case sensitive)')
        
        self.add(prt.Isolate(
            prt.Row(H1('Rule Categories'))))

        rc = rule_categories()

        for category in sorted(rc):
            self.add(prt.Row(H2(category)))
            for rule in sorted(rc[category]):
                self.add(prt.Row(Indent(rule)))
                self.page()
            self.add(VSpace())


def H1(*a, **k):
    k['font'] = prt.Font(size=10, weight=prt.BOLD)
    k['padding'] = prt.padding(2, 12, 2, 2)
    return prt.Text(*a, **k)


def H2(*a, **k):
    k['font'] = prt.Font(size=8, weight=prt.BOLD)
    return prt.Text(*a, **k)


def Indent(*a, **k):
    """Simulate indention by adding empty column first on row."""
    return prt.Isolate(
            prt.Row(prt.Column(width=12), prt.Column(prt.Row(*a, **k))))


def VSpace(*a, **k):
    """Empty row of height 16."""
    k['height'] = 16
    return prt.Row(*a, **k)


class RuleGroupList(list):
    def __init__(self):
        i = 1
        while True:
            (re_str, grp) = rave.eval(
                    'alert_server.%%alert_group_regexp%%(%d)' % i,
                    'alert_server.%%alert_group%%(%d)' % i)
            if re_str is None or re_str == '':
                break
            self.append((re.compile(re_str), grp))
            i += 1

    def match(self, rule):
        for regexp, grp in self:
            if regexp.match(rule):
                return grp
        return "Ungrouped"


def get_rules():
    rules = []
    for mod in Cui.CuiCrcModuleList():
        for rule in Cui.CuiCrcRuleList(mod):
            rules.append("%s.%s" % (mod, rule))
    return rules


def rule_categories():
    rules = {}
    rgl = RuleGroupList()
    for rule in get_rules():
        grp = rgl.match(rule)
        if grp in rules:
            rules[grp].append(rule)
        else:
            rules[grp] = [rule]
    return rules


if __name__ == '__main__':
    report = 'rule_categories.py'
    Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, Cui.CuiNoArea, 'plan', report, 0)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
