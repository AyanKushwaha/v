"""
Implementation of the Calibration report Compare Trips with Other Plan.
"""

from collections import defaultdict

import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave
from Localization import MSGR
import Cui

from carmusr.calibration import mappings
from carmusr.calibration.mappings import translation_type_ext
from carmusr.calibration.util import report_util
from carmusr.calibration.util import compare_plan
from carmusr.calibration.util import basics
from carmusr.calibration.util import common


def get_planned_ac_change_rave_variable():
    if basics.move_table_is_considered():
        return rave.var("calibration_move_mappings.lb_not_planned_as_turn")
    else:
        return rave.var("calibration_mappings.aircraft_change")


def get_connection_setting_info_strings():
    ac_info = MSGR("Current plan aircraft rotation info comes from:")
    if basics.move_table_is_considered():
        ac_from = MSGR("Rotations before move")
    else:
        ac_from = MSGR("Local plan rotations")
    return ac_info, ac_from


def fill_int_range(values):
    """Fills integers to range of min/max value. Keeps non-ints (i.e. None), placed last"""
    integers = filter(lambda x: isinstance(x, int), values)
    non_integers = filter(lambda x: not isinstance(x, int), values)
    return range(min(integers), max(integers) + 1) + non_integers


class ReportComparePlans(report_util.CalibrationReport):

    has_table_view = False

    @staticmethod
    def get_header_text():
        return report_util.CalibReports.COMP.title

    @staticmethod
    def get_form_handler(_variant):
        from carmusr.calibration.util import report_forms as rf
        return rf.comp_param_form_handler

    def create(self):

        self.setpaper(orientation=prt.LANDSCAPE)

        super(ReportComparePlans, self).create()

        def test():

            self.test_if_report_can_be_generated_and_store_bag()

            if self.skip_reason:
                return

            if not self.comparison_plan_name:
                self.add_warning_text(MSGR("No comparison plan loaded"))
                self.skip_reason = "NO_COMPARE_PLAN"
                return

            if self.current_area_mode != Cui.CrrMode:
                self.add_warning_text(MSGR("The report can only be generated from the trip window"))
                self.skip_reason = "NO_TRIPS_IN_WINDOW"
                return

        test()
        if self.skip_reason:
            self.add_warnings_and_links()
            return

        # Data ##

        self.current_data = PlanData(self, None, get_planned_ac_change_rave_variable())
        self.add_warnings_and_links()

        self.subplan_name = rave.eval('global_sp_name')[0]
        self.comparison_subplan_name = self.comparison_plan_name.split('/')[-1]

        self.ref_data = compare_plan.ComparisonPlanHandler.saved_other.get("PLAN_DATA", None)
        if not self.ref_data:
            self.ref_data = PlanData(self, compare_plan.get_comparison_plan_bag(),
                                     rave.var("calibration_mappings.aircraft_change"))
            compare_plan.ComparisonPlanHandler.saved_other["PLAN_DATA"] = self.ref_data

        # Layout ##
        self.add_overview_table()
        self.add("")
        self.page()
        if self.pconfig.level_trip_defined:
            self.add_trip_base_table()
            self.add("")
            self.page()
            self.add_trip_length_table()
            self.add("")
            self.page()
        if self.pconfig.level_duty_defined:
            self.add_duty_length_table()
            self.add("")
            self.page()
        self.add_connection_settings_table()
        self.add("")
        self.page()
        self.add_connection_overview_table()
        self.add("")
        self.page()
        self.add_stn_connection_table()
        self.add("")
        self.page()
        self.add_stn_turn_table()

    def add_connection_settings_table(self):
        title = MSGR("Analyse Turn/Connection Changes")
        ac_info, ac_from = get_connection_setting_info_strings()
        table = report_util.SimpleTable(title, use_page=True)
        row = table.add(prt.Text(ac_info,
                                 align=prt.LEFT,
                                 font=report_util.BOLD))
        row.add(prt.Text(ac_from))
        self.add(prt.Isolate(table))

    def add_overview_table(self):
        table = self.add_table_with_header(MSGR('Comparison Overview'))
        if self.pconfig.level_trip_defined:
            self.add_kpi_row(table, 'Trips', self.current_data.trip_keys['trip'], self.ref_data.trip_keys['trip'])
            self.add_kpi_row(table, 'Trips, ignoring deadheads', self.current_data.trip_keys['trip_no_dh'], self.ref_data.trip_keys['trip_no_dh'])
            self.add_empty_kpi_row(table)
        if self.pconfig.level_duty_defined:
            self.add_kpi_row(table, 'Duties', self.current_data.duty_keys['duty'], self.ref_data.duty_keys['duty'])
            self.add_kpi_row(table, 'Duties, ignoring deadheads', self.current_data.duty_keys['duty_no_dh'], self.ref_data.duty_keys['duty_no_dh'])
            self.add_kpi_row(table, 'FDP:s', self.current_data.duty_keys['fdp'], self.ref_data.duty_keys['fdp'])
            self.add_kpi_row(table, 'Layovers', self.current_data.duty_keys['layo'], self.ref_data.duty_keys['layo'])
            self.add_empty_kpi_row(table)
        self.add_kpi_row(table, 'Active legs', self.current_data.leg_keys['active'], self.ref_data.leg_keys['active'])
        self.add_kpi_row(table, 'Deadheads', self.current_data.leg_keys['dh'], self.ref_data.leg_keys['dh'])

        return table

    # Trip statistics ####
    def add_trip_base_table(self):
        table = self.add_table_with_header(MSGR("Trip Statistics: Home Base"), MSGR("Home Base"))
        current = self.current_data.trip_keys['trip_base']
        other = self.ref_data.trip_keys['trip_base']
        all_bases = current.groups().union(other.groups())
        bases = sorted(all_bases, key=current.count_in_group, reverse=True)
        for base in bases:
            self.add_kpi_row(table,
                             translation_type_ext.homebase_id2gui(base),
                             current.get_group(base),
                             other.get_group(base))
        return table

    def add_trip_length_table(self):
        table = self.add_table_with_header(MSGR("Trip Statistics: Duty Days"), MSGR("Duty Days"))
        current = self.current_data.trip_keys['trip_duty_days']
        other = self.ref_data.trip_keys['trip_duty_days']
        all_lengths = current.groups().union(other.groups())
        for ln in fill_int_range(all_lengths):
            self.add_kpi_row(table, ln, current.get_group(ln), other.get_group(ln))
        return table

    # Duty Statistics ####
    def add_duty_length_table(self):
        table = self.add_table_with_header(MSGR("Duty Statistics: Number of Legs"), MSGR("Number of Legs in Duty"))
        current = self.current_data.duty_keys['duty_legs']
        other = self.ref_data.duty_keys['duty_legs']
        all_lengths = current.groups().union(other.groups())
        for ln in fill_int_range(all_lengths):
            self.add_kpi_row(table, ln, current.get_group(ln), other.get_group(ln))
        return table

    # Leg keys ####
    def add_connection_overview_table(self):
        table = self.add_conn_table_with_header(title=MSGR('Connections and Turns Overview'),
                                                dimension=MSGR("Statistics"),
                                                last_header=(MSGR("Connection > Turn or"), MSGR("Turn > Connection")))
        #                                       last_header=(MSGR("Changed Turn"), "<-> " + MSGR("Connection")))
        self.add_conn_kpi_row(table, 'Connections', self.current_data.leg_keys['conn'], self.ref_data.leg_keys['conn'],
                              self.ref_data.leg_keys['turn'])
        self.add_conn_kpi_row(table, 'Turns', self.current_data.leg_keys['turn'], self.ref_data.leg_keys['turn'],
                              self.ref_data.leg_keys['conn'])
        self.add_conn_kpi_row(table, 'Connections & Turns',
                              self.current_data.leg_keys['conn'], self.ref_data.leg_keys['conn'], self.ref_data.leg_keys['turn'],
                              self.current_data.leg_keys['turn'], self.ref_data.leg_keys['turn'], self.ref_data.leg_keys['conn'])

        return table

    def add_stn_connection_table(self):
        table = self.add_conn_table_with_header(title=MSGR("Connection Statistics"),
                                                dimension=MSGR("Airport"),
                                                last_header=(MSGR("Changed"), MSGR("to Turn")))
        current = self.current_data.leg_keys['conn_stn']
        other = self.ref_data.leg_keys['conn_stn']
        other_turns = self.ref_data.leg_keys['turn_stn']
        all_stns = current.groups().union(other.groups())
        # Sort by:
        # * largest number of occurrences in CURRENT data
        # * largest number of occurrences in OTHER data
        # * alphabetical
        stns = sorted(all_stns,
                      key=lambda stn: (- current.count_in_group(stn),
                                       - other.count_in_group(stn),
                                       stn),
                      )
        for stn in stns:
            self.add_conn_kpi_row(table,
                                  translation_type_ext.station_id2gui(stn),
                                  current.get_group(stn),
                                  other.get_group(stn),
                                  other_turns.get_group(stn))
        return table

    def add_stn_turn_table(self):
        table = self.add_conn_table_with_header(title=MSGR("Turn Statistics"),
                                                dimension=MSGR("Airport"),
                                                last_header=(MSGR("Changed to"), MSGR("Connection")))
        current = self.current_data.leg_keys['turn_stn']
        other = self.ref_data.leg_keys['turn_stn']
        other_connections = self.ref_data.leg_keys['conn_stn']

        all_stns = current.groups().union(other.groups())
        # Sort by:
        # * largest number of occurrences in CURRENT data
        # * largest number of occurrences in OTHER data
        # * alphabetical
        stns = sorted(all_stns,
                      key=lambda stn: (- current.count_in_group(stn),
                                       - other.count_in_group(stn),
                                       stn)
                      )
        for stn in stns:
            self.add_conn_kpi_row(table,
                                  translation_type_ext.station_id2gui(stn),
                                  current.get_group(stn),
                                  other.get_group(stn),
                                  other_connections.get_group(stn))
        return table

    #  General table layout ####
    def add_table_with_header(self, title, dimension=MSGR("Statistics")):
        table = report_util.SimpleTable(title, use_page=True)
        table.add_sub_title(prt.Text(dimension))

        table.add_sub_title(self.two_line_text(MSGR("In current plan"), self.subplan_name, align=prt.RIGHT))
        table.add_sub_title(self.two_line_text(MSGR("In other plan"), self.comparison_subplan_name,
                                               align=prt.RIGHT, border=prt.border(right=1)))
        table.add_sub_title(prt.Text(MSGR("Unchanged"), align=prt.RIGHT))
        table.add_sub_title(prt.Text(MSGR("Of current"), align=prt.RIGHT, border=prt.border(right=1)))
        table.add_sub_title(self.two_line_text(MSGR("Only in"), MSGR("current"), align=prt.RIGHT))
        table.add_sub_title(prt.Text(MSGR("Of current"), align=prt.RIGHT, border=prt.border(right=1)))
        table.add_sub_title(self.two_line_text(MSGR("Only"), MSGR("in other"), align=prt.RIGHT))
        table.add_sub_title(prt.Text(MSGR("Of other"), align=prt.RIGHT))
        self.add(table)
        return table

    def add_conn_table_with_header(self, title, dimension=MSGR("Statistics"), last_header=""):
        table = report_util.SimpleTable(title, use_page=True)
        table.add_sub_title(prt.Text(dimension))
        table.add_sub_title(self.two_line_text(MSGR("In current plan"), self.subplan_name, align=prt.RIGHT))
        table.add_sub_title(self.two_line_text(MSGR("In other plan"), self.comparison_subplan_name,
                                               align=prt.RIGHT, border=prt.border(right=1)))

        table.add_sub_title(prt.Text(MSGR("Unchanged"), align=prt.RIGHT))
        table.add_sub_title(prt.Text(MSGR("Of current"), align=prt.RIGHT, border=prt.border(right=1)))

        table.add_sub_title(self.two_line_text(MSGR("Only in"), MSGR("current"), align=prt.RIGHT))
        table.add_sub_title(prt.Text(MSGR("Of current"), align=prt.RIGHT, border=prt.border(right=1)))

        if type(last_header) == tuple and len(last_header) == 2:
            table.add_sub_title(self.two_line_text(*last_header, align=prt.RIGHT))

        else:
            table.add_sub_title(prt.Text(last_header, align=prt.RIGHT))

        table.add_sub_title(prt.Text(MSGR("Of current"), align=prt.RIGHT))
        self.add(table)
        return table

    def add_empty_kpi_row(self, table):
        def right_border_text():
            return prt.Text("", border=prt.border(right=1))
        row = prt.Row("", "", right_border_text(), "", right_border_text(), "", right_border_text(), "", "")
        table.add(row)

    def add_kpi_row(self, table, title, s1, s2, do_ref_action=True):
        # Data ##
        assert isinstance(s1, SingleData)

        common_current_data = s1.common_data(s2)
        unique_current_data = s1.unique_data(s2)
        unique_other_data = s2.unique_data(s1)

        common_action = prt.action(report_util.calib_show_and_mark_legs,
                                   (self.current_area, common_current_data.all_leg_keys()))
        unique_action = prt.action(report_util.calib_show_and_mark_legs,
                                   (self.current_area, unique_current_data.all_leg_keys()))
        if do_ref_action:
            # Additive select does not work in an adequate way for ref. plan objects. Always use simple replace.
            always_use_replace = True
            ref_action = prt.action(report_util.calib_show_and_mark_legs,
                                    (self.current_area, unique_other_data.all_leg_keys(), always_use_replace))
        else:
            ref_action = None

        num_current = len(s1)
        num_other = len(s2)
        num_common = len(common_current_data)

        num_unique_in_current = len(unique_current_data)
        num_unique_in_other = len(unique_other_data)

        # Layout ##
        row = table.add(prt.Text(title))
        row.add(prt.Text(num_current,
                         align=prt.RIGHT,
                         action=report_util.get_select_action(self.current_area, s1.all_leg_keys())))
        row.add(prt.Text(num_other,
                         align=prt.RIGHT, border=prt.border(right=1)))

        row.add(prt.Text(num_common,
                         align=prt.RIGHT, action=common_action))
        row.add(prt.Text(basics.percentage_string(num_common, num_current),
                         align=prt.RIGHT, action=common_action,
                         border=prt.border(right=1)))

        row.add(prt.Text(num_unique_in_current,
                         align=prt.RIGHT, action=unique_action))
        row.add(prt.Text(basics.percentage_string(num_unique_in_current, num_current),
                         align=prt.RIGHT, action=unique_action,
                         border=prt.border(right=1)))

        row.add(prt.Text(num_unique_in_other,
                         align=prt.RIGHT, action=ref_action))
        row.add(prt.Text(basics.percentage_string(num_unique_in_other, num_other),
                         align=prt.RIGHT, action=ref_action))

        return row

    def add_conn_kpi_row(self, table, title, s1, s2, s3, s1b=None, s2b=None, s3b=None):
        # Data ##
        assert isinstance(s1, SingleData)

        s12 = s1.common_data(s2)
        s13 = s1.common_data(s3)
        unique_current_data = s1.unique_data(s2).unique_data(s3)

        current_ids = s1.all_leg_keys()
        common_ids = s12.all_leg_keys()
        changed_ids = s13.all_leg_keys()
        unique_ids = unique_current_data.all_leg_keys()

        num_current = len(s1)
        num_other = len(s2)
        num_common = len(s12)
        num_changed = len(s13)
        num_unique = len(unique_current_data)

        if s1b:
            s12b = s1b.common_data(s2b)
            s13b = s1b.common_data(s3b)
            unique_current_data_b = s1b.unique_data(s2b).unique_data(s3b)

            current_ids += s1b.all_leg_keys()
            common_ids += s12b.all_leg_keys()
            changed_ids += s13b.all_leg_keys()
            unique_ids += unique_current_data_b.all_leg_keys()
            num_current += len(s1b)
            num_other += len(s2b)
            num_common += len(s12b)
            num_changed += len(s13b)
            num_unique += len(unique_current_data_b)

        current_action = report_util.get_select_action(self.current_area, current_ids)
        common_action = report_util.get_select_action(self.current_area, common_ids)
        unique_action = report_util.get_select_action(self.current_area, unique_ids)
        changed_action = report_util.get_select_action(self.current_area, changed_ids)

        # Layout ##
        row = table.add(prt.Text(title))
        row.add(prt.Text(num_current, align=prt.RIGHT, action=current_action))
        row.add(prt.Text(num_other,
                align=prt.RIGHT, border=prt.border(right=1)))

        row.add(prt.Text(num_common,
                         align=prt.RIGHT, action=common_action))
        row.add(prt.Text(basics.percentage_string(num_common, num_current),
                         align=prt.RIGHT, action=common_action,
                         border=prt.border(right=1)))

        row.add(prt.Text(num_unique,
                         align=prt.RIGHT, action=unique_action))
        row.add(prt.Text(basics.percentage_string(num_unique, num_current),
                         align=prt.RIGHT, action=unique_action,
                         border=prt.border(right=1)))

        row.add(prt.Text(num_changed,
                         align=prt.RIGHT, action=changed_action))
        row.add(prt.Text(basics.percentage_string(num_changed, num_current),
                         align=prt.RIGHT, action=changed_action,
                         border=prt.border(right=1)))
        return row

    def two_line_text(self, line1, line2, **settings):
        column = prt.Column()
        column.add(prt.Text(line1, **settings))
        column.add(prt.Text(line2, **settings))
        return column


class SingleData(object):

    def __init__(self):
        self.data_points = dict()

    def add(self, key, leg_keys, complement):
        if not key:
            return
        prev_legs, prev_complement = self.data_points.get(key, ([], 0))
        prev_legs += leg_keys
        self.data_points[key] = (prev_legs, complement + prev_complement)

    def keys(self):
        return set(self.data_points.keys())

    def leg_keys(self, key):
        return self.data_points[key][0]

    def complement(self, key):
        return self.data_points[key][1]

    def __len__(self):
        return sum(complement for _, complement in self.data_points.itervalues())

    def all_leg_keys(self):
        return reduce(list.__iadd__, (leg_keys for leg_keys, _ in self.data_points.itervalues()), [])

    def common_data(self, other):
        """
        Returns data object keeping all data with keys COMMON to the other data object
        """
        data = SingleData()
        common_keys = self.keys().intersection(set(other.keys()))
        for key in common_keys:
            leg_keys, complement = self.data_points[key]
            data.add(key, leg_keys, complement)
        return data

    def unique_data(self, other):
        """
        Returns data object keeping all data with keys NOT IN to the other data object
        """
        data = SingleData()
        unique_keys = self.keys() - other.keys()
        for key in unique_keys:
            leg_keys, complement = self.data_points[key]
            data.add(key, leg_keys, complement)
        return data


class GroupedData(object):
    def __init__(self):
        self._groups = defaultdict(SingleData)

    def add_in_group(self, group, key, leg_keys, complement):
        if group:
            self._groups[group].add(key, leg_keys, complement)

    def count_in_group(self, group):
        return len(self.get_group(group))

    def groups(self):
        return set(self._groups.keys())

    def get_group(self, group):
        # get() instead of [] avoids insertion
        return self._groups.get(group, SingleData())


class PlanData(object):

    def __init__(self, report, top_bag, ac_change_rave_variable, reduced_set_of_data=False):
        pconfig = report.pconfig
        self.not_deadhead_rave_expr = rave.expr("not calibration_mappings.%leg_is_deadhead%")
        self.reduced_set_of_data = reduced_set_of_data
        if top_bag:
            legs_top_bag = trips_top_bag = duties_top_bag = top_bag
        else:
            legs_top_bag = report.bag
            duties_top_bag = report.get_top_bag_for_level_and_write_warning_once(pconfig.level_duty_name) if pconfig.level_duty_defined else None
            trips_top_bag = report.get_top_bag_for_level_and_write_warning_once(pconfig.level_trip_name) if pconfig.level_trip_defined else None

        self.leg_keys = self.get_leg_keys(legs_top_bag, ac_change_rave_variable)
        if pconfig.level_trip_defined:
            self.trip_keys = self.get_trip_keys(trips_top_bag)
        if pconfig.level_duty_defined:
            self.duty_keys = self.get_duty_keys(duties_top_bag)

    def get_trip_keys(self, top_bag):
        if top_bag:
            trip_bags_iter = common.get_atomic_iterator_for_level(top_bag, mappings.LEVEL_TRIP)(where="not hidden")
        else:
            trip_bags_iter = ()
        keys = {'trip': SingleData(),
                'trip_no_dh': SingleData(),
                'trip_base': GroupedData(),
                'trip_duty_days': GroupedData()}
        for trip_bag in trip_bags_iter:
            complement = trip_bag.calibration_mappings.crew_complement()
            trip_leg_ids = [leg_bag.leg_identifier() for leg_bag in trip_bag.atom_set()]

            trip_key_no_deadheads = trip_bag.studio_calibration_compare.same_trip_key_ignore_all_deadheads()
            keys['trip_no_dh'].add(trip_key_no_deadheads, trip_leg_ids, complement)

            if self.reduced_set_of_data:
                continue

            trip_key = trip_bag.studio_calibration_compare.same_trip_key_all_legs()
            keys['trip'].add(trip_key, trip_leg_ids, complement)
            keys['trip_base'].add_in_group(trip_bag.calibration_mappings.homebase(),
                                           trip_key, trip_leg_ids, complement)
            keys['trip_duty_days'].add_in_group(trip_bag.calibration_mappings.trip_duty_days_hb(),
                                                trip_key, trip_leg_ids, complement)

        return keys

    def get_duty_keys(self, top_bag):
        if top_bag:
            duty_bags_iter = common.get_atomic_iterator_for_level(top_bag, mappings.LEVEL_DUTY)(where="not hidden")
        else:
            duty_bags_iter = ()

        keys = {'fdp': SingleData(),
                'layo': SingleData(),
                'duty': SingleData(),
                'duty_no_dh': SingleData(),
                'duty_legs': GroupedData()}
        for duty_bag in duty_bags_iter:
            complement = duty_bag.calibration_mappings.crew_complement()
            duty_identifiers = [leg_bag.leg_identifier() for leg_bag in duty_bag.atom_set()]

            keys['duty_no_dh'].add(duty_bag.studio_calibration_compare.same_duty_key_ignore_all_deadheads(),
                                   duty_identifiers,
                                   complement)
            if self.reduced_set_of_data:
                continue

            keys['fdp'].add(duty_bag.studio_calibration_compare.same_fdp_key(), duty_identifiers, complement)
            keys['layo'].add(duty_bag.studio_calibration_compare.same_layover_key(), duty_identifiers, complement)
            duty_key = duty_bag.studio_calibration_compare.same_duty_key_all_legs()
            keys['duty'].add(duty_key, duty_identifiers, complement)
            keys['duty_legs'].add_in_group(duty_bag.calibration_mappings.duty_num_legs(),
                                           duty_key, duty_identifiers, complement)

        return keys

    def get_leg_keys(self, top_bag, ac_change_rave_var):

        leg_bags_iter = top_bag.atom_set(where="not hidden")

        keys = {'active': SingleData(),
                'dh': SingleData(),
                'conn': SingleData(),
                'turn': SingleData(),
                'conn_stn': GroupedData(),
                'turn_stn': GroupedData()}
        for leg_bag in leg_bags_iter:
            conn_key = leg_bag.studio_calibration_compare.same_connection_key()
            stn = None if self.reduced_set_of_data else leg_bag.studio_calibration_compare.connection_airport_name()
            is_ac_change = rave.eval(leg_bag, ac_change_rave_var)[0]
            leg_id = leg_bag.leg_identifier()
            complement = leg_bag.calibration_mappings.crew_complement()

            if is_ac_change:
                keys['conn'].add(conn_key, [leg_id], complement)
                if stn and conn_key:
                    keys['conn_stn'].add_in_group(stn, conn_key, [leg_id], complement)
            elif is_ac_change is False:
                # Skip when void
                keys['turn'].add(conn_key, [leg_id], complement)
                if stn and conn_key:
                    keys['turn_stn'].add_in_group(stn, conn_key, [leg_id], complement)
            if leg_bag.calibration_mappings.leg_is_deadhead():
                keys['dh'].add(leg_bag.studio_calibration_compare.flight_key(), [leg_id], complement)
            else:
                keys['active'].add(leg_bag.studio_calibration_compare.flight_key(), [leg_id], complement)

        return keys
