"""
 $Header$
 
 Rostering Statistics

 This report shows all key figures used in the optimizer cost function. 
 
 Created:    March 2007
 By:         Svante Bengtsson, Jeppesen Systems AB

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
import Cui
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator as CCL
# constants =============================================================={{{1
TITLE = 'Rostering Statistics'
cellWidths = (200,50,50,50)
aligns = (LEFT,RIGHT,RIGHT,RIGHT)

class RosteringStatistics(SASReport):

    def sectionHeader(self, headerItems):
        inputRow = Row(font=self.HEADERFONT, border=None,
                       background=self.HEADERBGCOLOUR)
        return self.dataRow(headerItems, inputRow)
        
    def dataRow(self, headerItems, inputRow=None, pad=None):
        if inputRow is None:
            inputRow = Row()
        if pad is None:
            pad = padding(2,2,2,2)
        items = zip(headerItems,cellWidths,aligns)
        for (item,itemwidth, itemalign) in items:
            inputRow.add(Text(item, width=itemwidth, align=itemalign,
                              padding=pad))
        return inputRow
    
    def create(self, reportType, context='default_context', fd=True):
        # Basic setup
        self.modify_pp()
        SASReport.create(self, TITLE, usePlanningPeriod=True)

        objectReport = False
        if reportType == 'object':
            # If one crew member is selected, the old 'object' version is run
            # otherwise, run a sum report on the selected crew
            crewData, = R.eval(context,
                               R.foreach('iterators.roster_set',
                                         'report_common.%crew_string%'))
            if len(crewData) < 2:
                objectReport = True

        if objectReport:
            (foo, crewString) = crewData[0]
            crewRow = Row(font=self.HEADERFONT)
            crewRow.add(crewString)
            self.add(crewRow)
        summaryBox = Column()
        summaryBox.add(self.sectionHeader(("Summary"," "," ","Cost")))
        #########################################################################
        #
        # Rosters section
        #
        #########################################################################
        assignedBox = Column()

        costElementsExpr = R.foreach(
            R.times(40),
            'roster_cost.%element_exist_ix1_ix%',
            'roster_cost.%element_name_ix1_ix%',
            'roster_cost.%element_cost_ix1_ix%',
            'report_ccr.%rosters_assigned_ix1_ix%',
            'report_ccr.%volume_assigned_ix1_ix%')

        costSectionsExpr = R.foreach(
            R.times(11),
            'roster_cost.%section_exist_ix%',
            'roster_cost.%section_name_ix%',
            'roster_cost.%section_factor_ix%',
            'report_ccr.%cost_assigned_ix%',
            'report_ccr.%rosters_assigned_ix%',
	    costElementsExpr)
        
        (assignedRosters,
         assignedCost,
         costSections) = R.eval(context,
                                'report_ccr.%rosters_assigned%',
                                'report_ccr.%cost_assigned%',
                                costSectionsExpr)
        
        for ix, exists, name, weight, cost, rosters, elements in costSections:
            if exists:
                summaryBox.add(self.dataRow(
                    (name," "," ",cost)))
                
                sectionBox = Column()
                sectionHeader = "%s (weight: %s)" %(name,weight)
                if (weight != 0):
                    sectionBox.add(
                        self.sectionHeader((sectionHeader,"Volume",
                                            "Rosters","Cost")))
                    sectionTotal = self.dataRow(
                        ("Total","-",rosters,cost),
                        Row(font=Font(weight=BOLD)))
                    for jx, exists, name, cost, rosters, volume in elements:
                        if exists:
                            if volume < 0:
                                volume = "-"
                            sectionBox.add(
                                self.dataRow(("%s.%s %s" %(ix,jx,name),
                                              volume,rosters,cost)))
                    sectionBox.add(sectionTotal)
                else:
                    sectionBox.add(
                        self.sectionHeader((sectionHeader,)))
                sectionBox.add(" ")
                assignedBox.add(Row(sectionBox))
                assignedBox.page0()
                
        totalString = "rosters"
        if objectReport:
            totalString = "roster"
        summaryBox.add(self.dataRow(
            ("Total cost of %s" %totalString," "," ",assignedCost),
            Row(font=Font(weight=BOLD)), pad=padding(2,5,2,2)))

        #########################################################################
        #
        # Constraint section
        #
        #########################################################################
        globConstraintRowsExpr = R.foreach(
            R.times(100),
            'roster_constraints.%active_ix1_ix%',
            'roster_constraints.%validfrom_ix1_ix%',
            'roster_constraints.%validto_ix1_ix%',
            'roster_constraints.%target_ix1_ix%',
            R.foreach(R.times('pp.%days%'),
                      'fundamental.%date_index%',
                      'roster_constraints.%crew_value_ix2_ix1_ix%',
                      )
            )
        
        globConstraintExpr = R.foreach(
            R.times(20),
            'roster_constraints.%glob_name_ix%',
            'roster_constraints.%glob_full_name_ix%',
            'roster_constraints.%nr_constraints_ix%',
            'roster_constraints.%upper_limit_ix%',
            'roster_constraints.%cost_ix%',
            globConstraintRowsExpr
            )

        global_constraint_cost = 0
        constraints = {}
        if not objectReport and fd:
            constraintsBox = Column()
            constraintsBox.add(
                self.sectionHeader(("Constraints","","","Cost")))

            globConstraints, = R.eval(context,
                                      globConstraintExpr)
            
            for (ix, name, full_name, nr_constraints, is_upper, cost, rows) in globConstraints:
                tot_cost = 0
                if name is not None:
                    if R.constraint('roster_constraints.%s' %name).on():
                        for (jx, active, vfrom, vto, target, values) in rows:
                            if active:
                                for (kx, day, value) in values:
                                    diff = target - value
                                    if is_upper:
                                        diff = -diff
                                    tot_cost += cost*max(0,diff)
                        global_constraint_cost += tot_cost
                    else:
                        tot_cost = "-"
                    constraints["8.%s %s" %(ix,full_name)] = tot_cost
                
            # Leg constraints couldn't be implemented in a nice way in rave
            if R.constraint('roster_constraints.soft_max_crew_on_lpc').on():
                tot_cost, = R.eval(context,
                                   'report_ccr.%cost_soft_max_crew_on_lpc%',
                                   )
                global_constraint_cost += tot_cost
            else:
                tot_cost = "-"
            constraints["8.7 Soft: Max allowed crew on 2X2h LPC"] = tot_cost
                
            if R.constraint('roster_constraints.sim_fully_assigned').on():
                cost_of_sim, = R.eval(context,
                                      'roster_constraints.%cost_of_simulator_p%',
                                      )
                sim_expr = R.foreach('iterators.roster_set',
                                     R.foreach(R.iter('iterators.trip_set',
                                                      where = ('trip.%is_simulator%',
                                                               'trip.%starts_in_pp%',
                                                               'training.%sim_trip_assigned_to_student%')),
                                               'report_ccr.%sim_uuid%',
                                               )
                                     )
                                     
                sims, = R.eval(context, sim_expr)
                used_sims = 0
                sim_keys = []
                for (ix, crew) in sims:
                    for (jx, key) in crew:
                        if key in sim_keys:
                            # Already added
                            continue
                        else:
                            sim_keys.append(key)
                            used_sims += 1

                tot_cost = cost_of_sim * used_sims
                global_constraint_cost += tot_cost
            else:
                tot_cost = "-"
            constraints["8.8 Cost of used simulator"] = tot_cost

            keys = constraints.keys()
            keys.sort()
            for key in keys:
                constraintsBox.add(
                    self.dataRow((key," "," ",constraints[key])))
                
            constraintsBox.add(
                self.dataRow(
                ("Total",
                 " ",
                 " ",
                 global_constraint_cost),
                Row(font=Font(weight=BOLD))))

            summaryBox.add(self.dataRow(
                ("Total cost of constraints", " "," ",global_constraint_cost),
                Row(font=Font(weight=BOLD)), pad=padding(2,5,2,2)))
            
        #########################################################################
        #
        # Unassigned section
        #
        #########################################################################
        if not objectReport:

            saved = None
            unassigned_trips = []
            try:
                saved = CCL().fetchcurrent()
                CCL(Cui.CuiArea1,"window").reinstate()
                (unassignedWeight,
                 unassigned_trips) = R.eval('default_context',
                                            'roster_cost.%unassigned_factor_p%',
                                            R.foreach('iterators.trip_set',
                                                      'crr_identifier',
                                                      R.foreach(R.times(40,
                                                                        where="roster_cost."+\
                                                                        "%exist_element_unassigned_ix%"),
                                                                'roster_cost.%name_unassigned_ix%',
                                                                'report_ccr.%trip_days_unassigned_ix%',
                                                                'report_ccr.%trip_unassigned_ix%',
                                                                'report_ccr.%trip_cost_unassigned_ix%')))
            finally:
                if saved:
                    saved.reinstate()
            unassigned_stats = {}
            total_unassigned_days = 0
            total_unassigned_trips = 0
            total_unassigned_cost = 0
            for trip in unassigned_trips:
                trip_nr, trip_id, trip_values = trip
                trip_cost = 0
                for ix, name, days, trips, cost in trip_values:
                    key = str(ix)+':'+name
                    total_unassigned_days += days
                    total_unassigned_cost += cost
                    trip_cost += cost
                    if unassigned_stats.has_key(key):
                        old_days, old_trips, old_cost  = unassigned_stats[key]
                        unassigned_stats[key] = (days + old_days,
                                                  trips + old_trips,
                                                  cost + old_cost)
                    else:
                        unassigned_stats[key] = (days,trips, cost)
                if trip_cost > 0:
                    total_unassigned_trips += 1 
            

            unassignedBox = Column()
            unassignedHeader = "Unassigned (weight: %s)" %unassignedWeight
            unassignedBox.add(
                self.sectionHeader((unassignedHeader,"Days","Trips","Cost")))
            ix = 0
            keys = unassigned_stats.keys()
            keys.sort()
            for key in keys:
                ix,name = key.split(':')
                days, slots, cost = unassigned_stats[key]
                unassignedBox.add(self.dataRow(("1.%s %s" %(ix,name),days,slots,cost)))

            unassignedBox.add(
                self.dataRow(
                ("Total",
                 total_unassigned_days,
                 total_unassigned_trips,
                 total_unassigned_cost),
                Row(font=Font(weight=BOLD))))

            summaryBox.add(self.dataRow(
                ("Total cost of unassigned trips"," "," ",total_unassigned_cost),
                Row(font=Font(weight=BOLD)), pad=padding(2,5,2,2)))

            summaryBox.add(self.dataRow(
                ("Total cost of plan"," "," ",total_unassigned_cost+assignedCost+global_constraint_cost),
                Row(font=Font(weight=BOLD)), pad=padding(2,5,2,2)))

        self.add(summaryBox)
        self.page0()
        if not objectReport and fd:
            self.add(" ")
            self.add(constraintsBox)
            self.add(" ")
            self.add(unassignedBox)
            self.page0()
        self.add(" ")
        self.add(assignedBox)
        self.reset_pp()
# End of file
