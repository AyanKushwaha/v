"""
Check Legality - Rostering Version

The report has two views.

* The first view displays rule violations, followed by rule exceptions,
  sorted on crew

* The second view shows all crew that violate or have exceptions
  for a specified rule.

This module is meant to be inherited from the check_legality report


@date: 08 Nov 2016
@author: Filip Buric
@org: Jeppesen Systems AB
"""
import Cui
import Gui
import carmensystems.publisher.api as p
import carmensystems.rave.api as rave
from AbsTime import AbsTime
from RelTime import RelTime
from Localization import MSGR
from carmstd import log

import carmstd.area as area
from carmstd.date_extensions import abstime2gui_datetime_string
import carmusr.rule_exceptions as rule_exceptions

from report_sources.include import standardreport as sr
import report_sources.include.check_legality as check_legality


class Report(check_legality.Report):

    def show_rule_info(self):
        # Construct report with all crew that have rule failures
        super(Report, self).show_rule_info()

        if self.exceptions_mode:
            # Show rule exceptions for selected crew without failures,
            # not handled in the base method
            if self.chain_mode:
                crew_with_only_exceptions = []
                for crew_bag in self.bag.iterators.chain_set():

                    if not crew_bag.crg_basic.rule_failure() and crew_bag.rule_exceptions.crew_has():
                        crew_with_only_exceptions.append((crew_bag.crew.id(),
                                                          crew_bag.crew.signature()))

                for crew_id, crew_sig in crew_with_only_exceptions:
                    self.set_chain_header(' %s - %s' % (crew_id, crew_sig), None)
                    self.show_crew_exception_info(crew_id)

            else:
                """
                The base method iterates over rule failures so failures that have
                been excepted in all instances will be missed, thus
                we need to identify these and create report tables here
                """
                for rule_remark in self.get_rules_with_only_exceptions():
                    self.set_chain_header(rule_remark, rule_remark)
                    self.show_rule_exception_info(rule_remark)

    def get_rules_with_only_exceptions(self):
        """Return the list of rules with exceptions but no failures."""
        # Get all excepted rules
        excepted_rules = set()
        for crew_bag in self.bag.iterators.roster_set():
            for i in range(1, crew_bag.rule_exceptions.total_number() + 1):
                rule_text = self.get_rule_remark(crew_bag, i)
                excepted_rules.add(rule_text)

        # Get all failing rules
        failing_rules = set()
        if getattr(self, 'fail_data', None) is not None:
            for rule_remark, _ in self.fail_data.iteritems():
                failing_rules.add(rule_remark)

        return filter(lambda rule: rule not in failing_rules, excepted_rules)

    def show_crew_exception_info(self, crew_id):
        """
        Adds a table with the following information:
        - Crew info
        - Rule exceptions info
        - Link to remove all exceptions

        Clicking on a rule exception will bring up a new report
        listing all crew that has this rule exception.

        Clicking a crew name will bring the corresponding
        roster up in Studio.
        """
        is_current_crew = 'crew.%%id%% = "%s"' % crew_id
        for crew_bag in self.bag.iterators.roster_set(where=is_current_crew):
            crew_info = p.Row(p.Text(MSGR('Rule Exceptions (%s) ') % crew_bag.rule_exceptions.total_number()),
                              p.Column(width=5),
                              p.Text(MSGR('Show'), colspan=2,
                                     action=p.action(self.show_in_studio, args=([crew_id], self.filter_area))),
                              p.Column(width=40),
                              self.get_exception_removal_cell__chain(crew_id))
            exceptions_tab = sr.SimpleTable(title=crew_info)

            if crew_bag.rule_exceptions.crew_has():

                exceptions_tab.add_sub_title(MSGR('Excepted Rule'))
                exceptions_tab.add_sub_title(MSGR('Start'))
                exceptions_tab.add_sub_title(MSGR('Actual'))
                exceptions_tab.add_sub_title(MSGR('Limit'))
                exceptions_tab.add_sub_title(MSGR('Diff'))
                exceptions_tab.add_sub_title(MSGR('Entered'))

                # Loop through the exceptions for this crew member
                # Adds a row of information for each rule exception
                for i in xrange(1, crew_bag.rule_exceptions.total_number() + 1):
                    rule_remark = WideExText(self.get_rule_remark(crew_bag, i),
                                             link=p.link(self.__module__,
                                                         {'rule': self.get_rule_remark(crew_bag, i)}))
                    rule_failtext = WideExText(self.get_exception_failtext(crew_bag, i))
                    rule_link = p.Expandable(rule_remark, rule_failtext)
                    remove_link = self.get_exception_remove_text(crew_id,
                                                                 crew_bag.rule_exceptions.etab_rule_id(i),
                                                                 abstime2gui_datetime_string(crew_bag.rule_exceptions.etab_start(i)))
                    exceptions_tab.add(sr.SimpleTableRow(
                        p.Isolate(rule_link),
                        ExText(abstime2gui_datetime_string(crew_bag.rule_exceptions.etab_start(i))),
                        ExText(crew_bag.rule_exceptions.etab_actual(i)),
                        ExText(crew_bag.rule_exceptions.etab_limit(i)),
                        ExText(crew_bag.rule_exceptions.overshoot_string(i)),
                        ExText('%s %s %s' % (abstime2gui_datetime_string(crew_bag.rule_exceptions.etab_exception_time(i)),
                                             MSGR("by"),
                                             crew_bag.rule_exceptions.etab_system_user(i))),
                        remove_link))
                self.add(exceptions_tab)
                self.page()

        self.add('')

    def show_rule_exception_info(self, rule):
        """
        Show all crew that have an exception for the specified rule.

        The method adds one box for the specified rule exception
        containing all crew that have that rule excepted, irrespective of
        exception start time.

        Contains a link for interacting with Studio where
        all crew included in the box can be filtered out.

        Each crew/exception pair is linked to Studio.
        """
        # Collect all crew that have exceptions for this rule
        # We need it here only for the header link
        crew_list_to_show = []
        n_exceptions = 0
        for crew_bag in self.bag.iterators.roster_set():
            for i in range(1, crew_bag.rule_exceptions.total_number() + 1):
                rule_text = self.get_rule_remark(crew_bag, i)
                if rule_text == rule:
                    crew_list_to_show.append(crew_bag.crew.id())
                    n_exceptions += 1

        rule_info = p.Row(p.Text(MSGR('Rule Exceptions (%s)') % n_exceptions),
                          p.Column(width=5),
                          p.Text(MSGR('Show'), action=p.action(self.show_in_studio,
                                                               args=(crew_list_to_show,
                                                                     self.filter_area))),
                          p.Column(width=40),
                          self.get_exception_removal_cell__rule(rule))

        rule_tab = sr.SimpleTable(rule_info)
        rule_tab.add_sub_title(MSGR('Crew'))
        rule_tab.add_sub_title(MSGR('Date'))
        rule_tab.add_sub_title(MSGR('Actual'))
        rule_tab.add_sub_title(MSGR('Limit'))
        rule_tab.add_sub_title(MSGR('Diff'))
        rule_tab.add_sub_title(MSGR('Entered'))

        found_exceptions_for_rule = False
        for crew_bag in self.bag.iterators.roster_set():
            for i in range(1, crew_bag.rule_exceptions.total_number() + 1):
                rule_text = self.get_rule_remark(crew_bag, i)
                if rule_text == rule:
                    found_exceptions_for_rule = True
                    exception_start = crew_bag.rule_exceptions.etab_start(i)
                    remove_link = self.get_exception_remove_text(crew_bag.crew.id(),
                                                                 crew_bag.rule_exceptions.etab_rule_id(i),
                                                                 exception_start)

                    rule_tab.add(sr.SimpleTableRow(
                        WideExText("%s - %s" % (crew_bag.crew.id(),
                                                crew_bag.crew.signature()),
                                   action=p.action(self.show_in_studio_and_zoom,
                                                   (self.current_area, [crew_bag.crew.id()],
                                                    exception_start))),
                        ExText(abstime2gui_datetime_string(exception_start)),
                        ExText(crew_bag.rule_exceptions.etab_actual(i)),
                        ExText(crew_bag.rule_exceptions.etab_limit(i)),
                        ExText(crew_bag.rule_exceptions.overshoot_string(i)),
                        WideExText(MSGR('{0!s} by {1!s}').format(
                            abstime2gui_datetime_string(crew_bag.rule_exceptions.etab_exception_time(i)),
                            crew_bag.rule_exceptions.etab_system_user(i))),
                        remove_link))

        if found_exceptions_for_rule:
            self.add(rule_tab)
            self.add('')

    @staticmethod
    def show_in_studio_and_zoom(current_area, crew_id_list, zoom=None):
        """
        Alternative to self.show_in_studio() = carmstd.select.show_crew(*args, **kw)
        which allows zooming on a specific date.
        """
        filter_area = area.get_opposite_area(current_area)

        cmd = 'PythonEvalExpr("carmstd.select.display_given_objects(%s, %s, %s, %s)")' % (repr(crew_id_list),
                                                                                          filter_area,
                                                                                          Cui.CrewMode,
                                                                                          Cui.CrewMode)
        Cui.CuiExecuteFunction(cmd,
                               MSGR("Rule Exception filtering"),
                               Gui.POT_REDO,
                               Gui.OPA_OPAQUE)

        #
        # Zooms into the period: start<-->end
        # Zoom is reset (if no zoom value is defined)
        # to show from the earliest departure date
        # to the latest arrival date of the flights in the local plan
        # CuiZoomTo(gpc_info, areaId, startTime, endTime)
        #
        if zoom:
            start = AbsTime(zoom) - RelTime("48:00")  # subtract 2 days
            end = AbsTime(zoom) + RelTime("120:00")  # Add 5 days
            cmd = 'PythonEvalExpr("Cui.CuiZoomTo(Cui.gpc_info, %s, %s, %s)")' % (filter_area,
                                                                                 start.getRep(),
                                                                                 end.getRep())
        else:
            cmd = 'CuiChangeRuler(gpc_info, %s, "all_legs", "pan", "0")' % filter_area

        Cui.CuiExecuteFunction(cmd,
                               MSGR("Zoom by Rule exception filtering"),
                               Gui.POT_REDO,
                               Gui.OPA_OPAQUE)

    def set_chain_header(self, chain_header, crossref):
        """
        In the Rostering rule view it's helpful to visually group rules
        since both failures and exceptions are shown.
        """
        self.add('')
        self.add(p.Isolate(p.Row(p.Text(chain_header,
                                        name=crossref,
                                        font=p.Font(style=p.ITALIC,
                                                    weight=p.BOLD),
                                        width=self.page_width()),
                                 border=p.border(bottom=2))))
        self.add('')

    @staticmethod
    def get_exception_remove_text(crew_id, ruleid, starttime):
        """Add a link for removing a rule exception."""
        remove_exc_action = p.action(rule_exceptions.remove_matching_rule_exceptions,
                                     args=({'crew': crew_id,
                                            'ruleid': ruleid,
                                            'starttime': starttime},))
        return p.Text(MSGR('remove'), font=p.Font(size=8), action=remove_exc_action)

    @staticmethod
    def get_rule_remark(crew_bag, row):
        """
        Get the actual and localized version of the rule remark
        """
        rule_id = crew_bag.rule_exceptions.etab_rule_id(row)
        try:
            rule_remark = rave.rule(rule_id).remark()
        except rave.UsageError:
            rule_remark = MSGR("The rule '%s' does not exist") % rule_id
        return rule_remark

    @staticmethod
    def get_exception_failtext(crew_bag, row):
        """
        Get the failtext stored in the exception table
        """
        failtext = crew_bag.rule_exceptions.etab_rule_text(row)
        return failtext

    @staticmethod
    def get_exception_cell__chain(chain_id, rule_failure, excepted_failures):
        """Add a link for adding a rule exception for chain_id for rule_failure."""
        rule_exception = rule_exceptions.get_rule_exception(rule_failure)
        add_exc_action = p.action(create_rule_exception,
                                  args=(chain_id, [rule_exception], excepted_failures))
        return p.Text(MSGR('except'), font=p.Font(size=8), action=add_exc_action)

    @staticmethod
    def get_exception_cell__rule(fail_tuples, excepted_failures):
        """Add a link for adding rule exceptions for fail_tuples."""
        return p.Text(MSGR("Except all failures"),
                      align=p.RIGHT,
                      action=p.action(create_rule_exceptions,
                                      args=(fail_tuples, excepted_failures)))

    @staticmethod
    def get_exception_removal_cell__chain(crew_id):
        """Add a link for removing all rule exceptions for crew_id."""
        return p.Text(MSGR("Remove all exceptions"),
                      align=p.RIGHT,
                      action=p.action(rule_exceptions.remove_matching_rule_exceptions,
                                      args=({'crew': crew_id},)))

    @staticmethod
    def get_exception_removal_cell__rule(rule_remark):
        """
        Add a link for removing all rule exceptions for rule.
        We use rule remark to search since this is the key supplied
        by he failure data structure.
        """
        return p.Text(MSGR("Remove rule exception from all crew"),
                      align=p.RIGHT,
                      action=p.action(rule_exceptions.remove_matching_rule_exceptions,
                                      args=({'ruleremark': rule_remark},)))


@rule_exceptions.fetch_save_reload_table
def create_rule_exception(etable, crew_id, exceptions, excepted_failures):
    # The decorator is used to trigger a table save and reload,
    # since the called method doesn't normally do this.
    exceptions = get_new_exception_failures(crew_id, exceptions, excepted_failures)
    rule_exceptions.create_for_chain(etable, crew_id, exceptions)


@rule_exceptions.fetch_save_reload_table
def create_rule_exceptions(etable, fail_tuples, excepted_failures):
    # The decorator is used to trigger a table save and reload,
    # since the called method doesn't normally do this.
    for failure, crew_id in fail_tuples:
        rule_exception = rule_exceptions.get_rule_exception(failure)
        exceptions = get_new_exception_failures(crew_id, [rule_exception], excepted_failures)
        rule_exceptions.create_for_chain(etable, crew_id, exceptions)


def get_new_exception_failures(crew_id, exceptions, excepted_failures):
    """
    Filter out and remove old exceptions that has already been handled in a previous iteration.
    """
    new_exception_failures = []

    for exception in exceptions:
        exception_id = (crew_id, exception['ruleid'], exception['starttime'])
        if exception_id in excepted_failures:
            # skip exceptions that has already been handled
            log.info("rule-exception with rule-exception id: " + str(exception_id) + " has already been excepted")
            continue
        else:
            new_exception_failures.append(exception)
            excepted_failures.append(exception_id)
    return new_exception_failures


def ExText(*args, **kw):
    kw['font'] = kw.get('font', p.Font(size=8))
    kw['width'] = kw.get('width', 80)
    return p.Text(*args, **kw)


def WideExText(*args, **kw):
    kw['font'] = kw.get('font', p.Font(size=8))
    kw['width'] = kw.get('width', 160)
    return p.Text(*args, **kw)
