import carmensystems.kpi as k
import carmensystems.rave.api as R
import carmusr.fatigue.kpi as fatigue_kpi

class CustomKPI(k.KPI):
    def calcTotProdDays(self, trips_bag):
        no_crew_1_day_trips = trips_bag.kpi.no_crew_1_day_trips()
        no_crew_2_day_trips = trips_bag.kpi.no_crew_2_day_trips()
        no_crew_3_day_trips = trips_bag.kpi.no_crew_3_day_trips()
        no_crew_4_day_trips = trips_bag.kpi.no_crew_4_day_trips()
        no_crew_5_day_trips = trips_bag.kpi.no_crew_5_day_trips()

        return float(no_crew_1_day_trips + no_crew_2_day_trips*2 + no_crew_3_day_trips*3 + no_crew_4_day_trips*4 + no_crew_5_day_trips*5)

    def getCatSet(self):
        cat = R.set('fundamental.cat_set')
        return cat.members()

    def getFairnessElements(self, roster_bag):
        for ix in range(0,39):
            if roster_bag.fairness.any_crew_has(ix):
                yield ix

    @property
    def showCompFree(self):
        retVal, = R.eval('kpi.%show_compensation_free%')
        return retVal

    @property
    def showSimpleFairness(self):
        retVal, = R.eval('kpi.%show_simplified_fairness%')
        return retVal

    def create(self):
        bags = self.get_bags()
        trips_bag = bags['trips']
        roster_bag = bags['rosters']

        self.add(k.KpiValue("Unassigned days ", self.calcTotProdDays(trips_bag)))
        self.add(k.KpiValue("Unassigned flight days ",trips_bag.kpi.no_crew_days()))
        self.add(k.KpiValue("Troublesome days ",trips_bag.kpi.tot_crew_troublesome_days()))
        self.add(k.KpiMatrix("Unassigned per length and position",
                             [ ((cat, dutylength), trips_bag.kpi.no_cat_with_x_day_trips(cat, dutylength))
                               for cat in self.getCatSet() for dutylength in range(1,6) ],
                             "Cat", "dutylength", "no of duties"))

        self.add(k.KpiVector("Unassigned per position",
                             [ (cat, trips_bag.kpi.no_trips_for(cat))
                               for cat in self.getCatSet() ],
                             "Cat", "count"))

        self.add(k.KpiVector("Unassigned standby per position",
                             [ (cat, trips_bag.kpi.no_sb_trips_for(cat))
                               for cat in self.getCatSet() ],
                             "Cat", "count"))

        self.add(k.KpiVector("Unassigned standby line per position",
                             [ (cat, trips_bag.kpi.no_sb_line_trips_for(cat))
                               for cat in self.getCatSet() ],
                             "Cat", "count"))

        self.add(k.KpiValue("==========Second level==========","") )

        self.add(k.KpiVector("BL per position",
                             [ (cat, roster_bag.kpi.no_bl_trips_for(cat))
                               for cat in self.getCatSet() ],
                             "Cat", "count"))

        # LIFESTYLE SECTIONS
        lifestyle_fulfillment_per_ls = [
              ("Morning Person", roster_bag.kpi.avg_fulfillment_morning_person()),
              ("Evening Person", roster_bag.kpi.avg_fulfillment_evening_person()),
              ("Nights at Home", roster_bag.kpi.avg_fulfillment_nights_home()),

              ("Nights at Home + Morning Person", roster_bag.kpi.avg_fulfillment_nights_at_home_early_ends()),
              ("Nights at Home + Evening Person", roster_bag.kpi.avg_fulfillment_nights_at_home_late_starts()),

              ("Nights Away from Home 2-3 days", roster_bag.kpi.avg_fulfillment_commuter_2_3_days()),
              ("Nights Away from Home 2-3 days + Morning Person", roster_bag.kpi.avg_fulfillment_commuter_2_3_days_early_ends()),
              ("Nights Away from Home 2-3 days + Evening Person", roster_bag.kpi.avg_fulfillment_commuter_2_3_days_late_starts()),

              ("Nights Away from Home 3-5 days", roster_bag.kpi.avg_fulfillment_commuter_3_5_days()),
              ("Nights Away from Home 3-5 days + Morning Person", roster_bag.kpi.avg_fulfillment_commuter_3_5_days_early_ends()),
              ("Nights Away from Home 3-5 days + Evening Person", roster_bag.kpi.avg_fulfillment_commuter_3_5_days_late_starts()),

              ("Longhaul West/U.S", roster_bag.kpi.avg_fulfillment_west_destinations()),
              ("Longhaul East/Asia", roster_bag.kpi.avg_fulfillment_east_destinations()),
              ("Longhaul Any", roster_bag.kpi.avg_fulfillment_any_longhaul_destinations())]

        self.add(k.KpiVector("Lifestyle - fulfillment details", lifestyle_fulfillment_per_ls, "Element", "Value"))

        lifestyle_distr = [
              ("Morning Person", roster_bag.kpi.distribution_morning_person()),
              ("Evening Person", roster_bag.kpi.distribution_evening_person()),
              ("Nights at Home", roster_bag.kpi.distribution_nights_home()),

              ("Nights at Home + Morning Person", roster_bag.kpi.distribution_nights_at_home_early_ends()),
              ("Nights at Home + Evening Person", roster_bag.kpi.distribution_nights_at_home_late_starts()),

              ("Nights Away from Home 2-3 days", roster_bag.kpi.distribution_commuter_2_3_days()),
              ("Nights Away from Home 2-3 days + Morning Person", roster_bag.kpi.distribution_commuter_2_3_days_early_ends()),
              ("Nights Away from Home 2-3 days + Evening Person", roster_bag.kpi.distribution_commuter_2_3_days_late_starts()),

              ("Nights Away from Home 3-5 days", roster_bag.kpi.distribution_commuter_3_5_days()),
              ("Nights Away from Home 3-5 days + Morning Person", roster_bag.kpi.distribution_commuter_3_5_days_early_ends()),
              ("Nights Away from Home 3-5 days + Evening Person", roster_bag.kpi.distribution_commuter_3_5_days_late_starts()),

              ("Longhaul West/U.S", roster_bag.kpi.distribution_west_destinations()),
              ("Longhaul East/Asia", roster_bag.kpi.avg_fulfillment_east_destinations()),
              ("Longhaul Any", roster_bag.kpi.distribution_east_destinations())]

        self.add(k.KpiVector("Lifestyle - distribution", lifestyle_distr, "Element", "Value"))

        dated_bid_kpis = [
              ("Avg. points", roster_bag.kpi.avg_dated_bid_roster_points()),
              ("Avg. points above target", roster_bag.kpi.average_dated_bid_ratio()),
              ("Total dated bid cost", roster_bag.kpi.tot_dated_bid_cost())]
        self.add(k.KpiVector("Dated bids", dated_bid_kpis, "Element", "Value"))

        if self.showSimpleFairness:
            self.add(k.KpiValue("Fairness cost", roster_bag.kpi.tot_crew_fairness()))
        else:
            self.add(k.KpiMatrix("Fairness",
                                 [ ((group_bag.fairness.kpi_fairness_crew_group(),   group_bag.fairness.text_element(ix)),
                                    group_bag.fairness.std_dev_ix_index(ix))
                                   for group_bag in roster_bag.fairness.crew_fairness_group_set(sort_by = 'fairness.%fairness_crew_group%')
                                   for ix in self.getFairnessElements(group_bag) ],
                                 "group", "Element", "std dev"))

        self.add(k.KpiValue("FBR days", roster_bag.kpi.no_fbr_days()))
        self.add(k.KpiValue("Excessive free days", roster_bag.kpi.tot_freeday_deviation()))
        self.add(k.KpiValue("Critical layovers",roster_bag.kpi.num_critical_layovers()))

        # Shift Changes
        shift_change_wop_length = roster_bag.shift_change.minimum_days_to_check()
        self.add(k.KpiValue("Shift Changes", roster_bag.kpi.num_shift_changes()))
        self.add(k.KpiValue("Shift Changes ({0}+ day wop)".format(shift_change_wop_length),
                            roster_bag.kpi.num_shift_changes_checked()))
        self.add(k.KpiValue("Excess Shift Changes", roster_bag.kpi.num_excess_shift_changes()))

        if self.showCompFree:
            self.add(k.KpiVector("Compensation days per cal. day",
                                 [ (roster_bag.kpi.pp_date_ix(ix), roster_bag.kpi.no_comp_days_on_day_ix(ix))
                                   for ix in range(0,39) ],
                                 "Date", "count"))

        try:
            self.add(fatigue_kpi.get_fatigue_kpis(roster_bag))
        except:
            pass


# If run from Admin Tools > Python File Manager in Studio
if __name__ == '__main__':

    # For debugging in Studio.
    # Uses the Studio window where the cursor was last in as default_context.
    # Shows xml output in a text message window.
    # Prints xml output to a file, and shows it in the log.

    import os

    import Cui
    from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator

    # Activate the default_context
    CuiContextLocator(Cui.CuiWhichArea, "window").reinstate()

    # Print the xml result on file
    kpi_file = '/tmp/KpiTempFile.xml'
    k.writeKPI('kpi.customRostering', kpi_file)

    # Show xml result in log
    os.system('cat %s' % kpi_file)

    os.unlink(kpi_file)

