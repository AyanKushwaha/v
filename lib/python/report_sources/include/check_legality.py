"""
Check Legality

The report has two views.
The first view displays rule violations sorted on crew / trip.
The second view shows all crew / trips that violate a specified rule.

The second view takes a rule name as an argument and displays
crew/trips that violate that specific rule.

This module is meant to be inherited from the check_legality reports
for crr, crew, ac_rot, et.c.


@date: 01 Sep 2009
@author: Mattias Lindqvist
@org: Jeppesen Systems AB

"""
import os

import Cui
from Localization import MSGR
import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave
from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator
from AbsTime import AbsTime

from report_sources.include import standardreport
from report_sources.include.studiopalette import studio_palette as sp
from carmstd import area
from carmstd.date_extensions import abstime2gui_datetime_string
from carmstd import rave_ext
from report_sources.include.standardreport import SimpleTableRow
from report_sources.include.standardreport import StandardReport


class Report(StandardReport):

    def get_report_view_name(self):
        """
        The name visual in the report. E.g. Trip or Rotation.
        @rtype: string
        @return: Name of the objects checked. This is visual in the report.
        """
        raise NotImplementedError()

    def get_identifier(self, bag):
        """Shall return the identifier for the rule chain, trip_identifier,
        crr_crew_id, et.c.
        This will be used to select the object in studio"""
        raise NotImplementedError()

    def get_name(self, bag):
        """Shall return the name of the chain, trip.%name%, crew.%id% et.c.
        This will be used in the report"""
        raise NotImplementedError()

    @staticmethod
    def show_in_studio(*args, **kw):
        raise NotImplementedError()

    def create(self):
        """
        Creates the actual report and chooses version
        (grouped by rule or chain) depending on argument
        'rule'
        """
        self.is_roster = self.get_type() == "roster"
        self.setpaper(orientation=prt.LANDSCAPE)

        super(Report, self).create()
        if not self.bag:
            return

        # Using the explicit role name is a bit crude
        # An arguably better solution would be to create
        # a resource which determines whether the explore
        # action should be available.
        admin_roles = ['Administrator', 'Developer', 'SystemSpecialist', 'Superuser']
        self.show_explore_action = os.environ['CARMROLE'] in admin_roles
        self.current_context = CuiContextLocator().fetchcurrent()
        active_font = prt.Font(size=8, style=prt.ITALIC, weight=prt.BOLD)
        passive_font = prt.Font(size=8, style=prt.ITALIC)
        base_chain_name = self.get_report_view_name() + MSGR(' name')
        self.unknown_chain_name = MSGR('No %s') % base_chain_name.lower()

        # Setup options for Rule or Chain mode
        if self.arg('rule') == 'True':
            self.chain_mode = False
            chain_font = passive_font
            rule_font = active_font
            self.subtitle = base_chain_name
        else:
            self.chain_mode = True
            chain_font = active_font
            rule_font = passive_font
            self.subtitle = MSGR('Violated Rule')

        # Setup options for Exceptions mode
        if self.arg('exceptions') == 'True':
            self.exceptions_mode = True
            show_font = active_font
            hide_font = passive_font
        else:
            self.exceptions_mode = False
            show_font = passive_font
            hide_font = active_font

        self.current_area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        self.filter_area = area.get_opposite_area(self.current_area)
        views = prt.Row(prt.Image("arrow_on_white.jpg", valign=prt.CENTER),
                        prt.Text(MSGR("View:"),
                                 font=prt.Font(size=8, weight=prt.BOLD)),
                        prt.Text(self.get_report_view_name(),
                                 link=prt.link(self.__module__, {'rule': 'False', 'exceptions': str(self.exceptions_mode)}),
                                 font=chain_font,
                                 align=prt.CENTER,
                                 width=30),
                        prt.Text(MSGR("Rule"),
                                 link=prt.link(self.__module__, {'rule': 'True', 'exceptions': str(self.exceptions_mode)}),
                                 font=rule_font,
                                 align=prt.CENTER,
                                 width=30))
        if self.is_roster:
            views = prt.Column(views,
                               prt.Row(prt.Image("arrow_on_white.jpg", valign=prt.CENTER),
                                       prt.Text(MSGR("Exceptions:"),
                                                font=prt.Font(size=8, weight=prt.BOLD)),
                                       prt.Text(MSGR("Show"),
                                                link=prt.link(self.__module__, {'rule': str(not self.chain_mode), 'exceptions': 'True'}),
                                                font=show_font,
                                                align=prt.CENTER,
                                                width=30),
                                       prt.Text(MSGR("Hide"),
                                                link=prt.link(self.__module__, {'rule': str(not self.chain_mode), 'exceptions': 'False'}),
                                                font=hide_font,
                                                align=prt.CENTER,
                                                width=30)))
        self.add(prt.Isolate(views, align=prt.RIGHT))
        self.add(prt.Text(" ", width=500))

        self.show_rule_info()

    def get_toc(self, fail_data):
        # Table of contents
        toc = prt.Column()

        # toc_dict used to name all the toc rows so that it is possible
        # to add number of failing chains later
        toc_dict = {}
        toc.add(prt.Text(MSGR("Table of contents"), font=prt.Font(weight=prt.BOLD)))
        rule_remarks = fail_data.keys()
        rule_remarks.sort()
        for rule_remark in rule_remarks:
            toc_dict[rule_remark] = prt.Row()
            toc_dict[rule_remark].add(prt.Text(
                prt.Crossref(rule_remark, format="%s" % rule_remark),
                font=prt.Font(size=8)))
            toc_dict[rule_remark].add(prt.Text(' (%i)' % len(fail_data[rule_remark]),
                                               font=prt.Font(size=8)))
            toc.add(toc_dict[rule_remark])

        # We may only have exceptions for some rules in Rostering
        if self.is_roster and self.exceptions_mode:
            for rule_remark in self.get_rules_with_only_exceptions():
                toc_dict[rule_remark] = prt.Row()
                toc_dict[rule_remark].add(prt.Text(
                    prt.Crossref(rule_remark, format="%s" % rule_remark),
                    font=prt.Font(size=8)))
                toc_dict[rule_remark].add(prt.Text(' (only exceptions)', font=prt.Font(size=8)))
                toc.add(toc_dict[rule_remark])

        self.add(prt.Isolate(toc))
        self.add("")

    def add_table_headings(self, rule_tab):
        if self.is_roster:
            rule_tab.add_sub_title(MSGR('Wop'))
            rule_tab.add_sub_title(MSGR('Trip'))
        rule_tab.add_sub_title(MSGR('Duty'))
        rule_tab.add_sub_title(MSGR('Leg'))
        rule_tab.add_sub_title(MSGR('Time'))
        rule_tab.add_sub_title(MSGR('Actual'))
        rule_tab.add_sub_title(MSGR('Limit'))
        rule_tab.add_sub_title(MSGR('Diff'))

    def show_rule_info(self):
        """
        Displays all violations grouped on rule/chain name.

        The method adds one box for the specified rule/chain
        containing all violated rules/chains.

        Contains a link for interacting with Studio where
        all chains in a box can be filtered out.
        """
        # Extract the rule failure information and save it for future use
        # since it'a costly operation
        self.chain_info_map, self.fail_data = self.get_fails()

        # Store all excepted failures in the report since last refresh
        self.excepted_failures = []

        if not self.chain_mode:
            self.get_toc(self.fail_data)
        # Iterate the broken rules
        for key, fails in self.fail_data.iteritems():
            if self.chain_mode:
                (chain_id, chain_name) = self.chain_info_map[key]
                chain_name = chain_name or self.unknown_chain_name
                identifiers = [chain_id]
                table_heading = chain_name
                crossref = None
            else:
                rule_remark = key
                identifiers = [x[1] for x in fails]
                table_heading = rule_remark
                crossref = table_heading
            if filter(lambda x: x is None, identifiers):
                action = None
            else:
                action = prt.action(self.show_in_studio,
                                    args=(identifiers,
                                          self.filter_area))

            if self.is_roster:
                # For the roster report, the failures and exceptions are grouped
                self.set_chain_header(table_heading, crossref)
                table_heading = MSGR('Show')

            title_row = prt.Row(prt.Text(MSGR('Rule Failures (%s) ') % len(fails)),
                                prt.Column(width=10),
                                prt.Text(table_heading, name=crossref, action=action),
                                prt.Column(width=40))
            rule_tab = standardreport.SimpleTable(title_row)

            rule_tab.add_sub_title(self.subtitle)
            self.add_table_headings(rule_tab)

            fail_tuples = []
            for fail_info in fails:
                fail_tuples.append(fail_info[:2])
                rule_tab.add(self._get_fail_row(fail_info))
                rule_tab.page()

            if self.is_roster:
                except_link = self.get_exception_cell__rule(fail_tuples, self.excepted_failures)
                if except_link:
                    rule_tab.add_title(except_link)
            self.add(rule_tab)
            self.add("")

            # Append rule exception information
            if self.is_roster and self.exceptions_mode:
                if self.chain_mode:
                    self.show_crew_exception_info(chain_id)
                else:
                    self.show_rule_exception_info(rule_remark)
                self.add("")

        if not self.fail_data:
            self.add(prt.Column(' ', MSGR('No illegal %s found') % self.get_report_view_name()))
        self.add('')

    def get_level_info(self, rule_bag):
        level_items = []
        if self.is_roster:
            try:
                wop_num = rule_bag.wop.nr()
            except:
                wop_num = "-"
            try:
                trip_num = rule_bag.trip.trip_num_in_wop()
            except:
                trip_num = "-"
            level_items.extend([wop_num, trip_num])
        try:
            duty_num = rule_bag.duty.duty_num_in_trip()
        except:
            duty_num = '-'
        try:
            leg_num = rule_bag.leg.leg_num_in_duty()
        except:
            leg_num = '-'
        level_items.extend([duty_num, leg_num])
        return level_items

    def get_fails(self):
        """
        Return a collection of rule failure information for all marked chains.
        It allows having different views (indexing) of this data, by chain or failure.
        Construction is potentially slow (quadratic): O(n_chains * n_failures)

        Example:
        {1: [(<RuleFail>, '34', '34 - AAust', 'rest_jcr.min_rest',
              'RULE: Crew must have at least min [..]',
              201418668, [5, 4, 1, '-'])],

         2: [(<RuleFail>, '56', '56 - AAyal', 'recency.must_be_recent_on_ac_type',
              'RECENCY RULE: Flight crew member must be recent for aircraft type',
              201395304, [2, 1, 1, 2]),
             (<RuleFail>, '56', '56 - AAyal', 'recency.must_be_recent_on_ac_type',
             'RECENCY RULE: Flight crew member must be recent for aircraft type',
             201395300, [2, 1, 1, 1])]}
        """
        fail_data = {}
        chain_ix = 0
        chain_info_map = {}
        for chain_bag in self.bag.chain_set():
            chain_ix += 1
            chain_id = self.get_identifier(chain_bag)
            chain_name = self.get_name(chain_bag)
            chain_info_map[chain_ix] = (chain_id, chain_name)
            for rule_bag, fail in chain_bag.rulefailures():
                rule_remark = fail.rule.remark()
                rule_name = fail.rule.name()
                explorer_id, = rave.eval(rule_bag,
                                         rave.first(rave.Level.atom(),
                                                    "leg_identifier"))
                level_items = self.get_level_info(rule_bag)
                if self.chain_mode:
                    dict_key = chain_ix
                else:
                    # Rule remarks can be non-unique, but that will only lead to several rules being grouped together,
                    # the fail itself has the unique info
                    dict_key = rule_remark
                this_fail = (fail, chain_id, chain_name, rule_name, rule_remark, explorer_id, level_items)
                fail_data.setdefault(dict_key, list()).append(this_fail)
        return chain_info_map, fail_data

    def _get_fail_row(self, fail_data):
        (fail,
         chain_id, chain_name,
         _rule_name, rule_remark,
         explorer_id, level_items) = fail_data
        first_col_width = 280
        if self.chain_mode:
            if fail.failtext:
                remark = prt.Text(rule_remark, width=first_col_width)
                failtext = prt.Text(fail.failtext,
                                    font=prt.Font(style=prt.ITALIC),
                                    colour=sp.Blue,
                                    width=first_col_width)
                first_column = prt.Expandable(remark, failtext)
            else:
                first_column = prt.Text("  %s" % rule_remark,
                                        colour=sp.DarkBlue, width=first_col_width)
        else:
            if chain_id:
                action = prt.action(self.show_in_studio,
                                    args=([chain_id],
                                          self.filter_area))
            else:
                action = None

            first_column = prt.Text("%s" % chain_name or self.unknown_chain_name,
                                    action=action,
                                    width=150)
        level_items_prt = []
        for level_item in level_items:
            level_items_prt.append(prt.Text(level_item, width=30))

        limit = fail.limitvalue
        actual = fail.actualvalue
        if isinstance(limit, AbsTime):
            limit = abstime2gui_datetime_string(limit)
        if isinstance(actual, AbsTime):
            actual = abstime2gui_datetime_string(actual)

        trip_items = [prt.Text(abstime2gui_datetime_string(fail.startdate) if fail.startdate else "-", width=100),
                      prt.Text("-" if actual is None else actual, width=40),
                      prt.Text("-" if limit is None else limit, width=40),
                      prt.Text("-" if fail.overshoot is None else fail.overshoot, width=40)]
        columns = [first_column] + level_items_prt + trip_items

        if self.show_explore_action:
            explore_action = prt.action(rave_ext.explore_leg,
                                        args=(fail.rule,
                                              self.current_area,
                                              explorer_id))
            explore_column = prt.Text(MSGR('explore'), action=explore_action)
            columns.append(explore_column)

        row = SimpleTableRow(font=prt.font(size=8), *columns)
        if self.is_roster:
            except_link = self.get_exception_cell__chain(chain_id, fail, self.excepted_failures)
            if except_link:
                row.add(except_link)
        return row

    def set_chain_header(self, chain_header, crossref):
        """
        Create header for current chain.
        In the Rostering rule view it's helpful to visually group rules
        since both failures and exceptions are shown.
        """
        pass

    @staticmethod
    def get_rules_with_only_exceptions():
        """Return the list of rules with exceptions but no failures."""
        pass

    @staticmethod
    def get_exception_cell__chain(chain_id, rule_failure, excepted_failures):
        """Add a link for adding a rule exception for chain_id for rule_failure."""
        pass

    @staticmethod
    def get_exception_cell__rule(fail_tuples, excepted_failures):
        """Add a link for adding rule exceptions for fail_tuples."""
        pass
