##############################################
#
# Script for creating F36 target
# values for crew in window.
# Ref: SASCMS-6040
# 
# Input:
# 1. total amount of F36 to assign for
# crew in planning group (region). Total targets
# in f36_total
# 2. Available days
# 3. Current account balance
#
# Output:
# Individual targets saved in f36_targets
#
# Created: September 2013
# By: Ulf Hansryd, Jeppesen

import Cui
import bisect
import carmensystems.rave.api as R
from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator
import modelserver as M

class crew:
    def __init__(self, id, region, availability, balance):
        self.id = id
        self.region = region
        self.availability = availability # int
        self.balance_input = balance  # Float
        self.awarded_f36 = 0
        self.awarded_hidden = 0
        self.balance_avail_ratio = self.get_balance_avail_ratio()

    def __str__(self):
        return "ID: %s, REG: %s, AV: %s, BAL: %s, AW: %s, AWH: %s, X:%s"\
               %(self.id, self.region, str(self.availability), str(self.balance_input), str(self.awarded_f36), str(self.awarded_hidden), str(self.balance_avail_ratio))
        
    def get_balance_avail_ratio(self):
        try:
            x = (self.balance_input-self.awarded_f36-self.awarded_hidden) / self.availability
        except ZeroDivisionError:
            x = 0.0
        return x

def save_crew_target_data(crew_list, target_table, crew_table, period):
    """
    Save F36 target and input data to table
    """
    for crew in crew_list:
        #print "save data for",period, crew
        crew_entity = crew_table[(crew.id,)]
        try:
            row = target_table[(crew_entity, period)]
        except M.EntityNotFoundError:
            row = target_table.create((crew_entity, period))
        
        # Update
        row.target = crew.awarded_f36
        row.balance = "%.2f" % crew.balance_input
        row.availabledays = crew.availability
        row.si = ""
        

def calculate_targets(tot_target, crew_list):
    """
    Calculate individual F36 targets
    """

    if len(crew_list) == 0 or tot_target <= 0:
        return
    # Sort list with highest balance ratio last
    crew_list.sort(lambda x, y: cmp(x.balance_avail_ratio, y.balance_avail_ratio))

    ratio_list = [crew.balance_avail_ratio for crew in crew_list]
    max_target = R.eval("studio_freedays.%max_individual_target_p%")[0]

    # In order to break when all crew reach max target (also when tot_target not used)
    max_f36_to_assign = max_target*len(crew_list)
    
    number_f36_to_assign = tot_target
    if max_f36_to_assign == 0:
        max_f36_to_assign = tot_target
       
    while number_f36_to_assign > max(0,tot_target-max_f36_to_assign):
        ratio = ratio_list.pop()
        if ratio <= 0.0: # no more crew with positive balance
            break

        crew = crew_list.pop() # Get crew with highest ratio (last in list)
        #print "ratio",crew,ratio

        # Move crew away from place with highest ratio (when max_target is reached)
        crew.awarded_hidden += 1

        if max_target == 0 or max_target > crew.awarded_f36:
            crew.awarded_f36 += 1
            crew.awarded_hidden -= 1
            number_f36_to_assign -= 1

        new_ratio = crew.get_balance_avail_ratio()
        crew.balance_avail_ratio = new_ratio

        # Get insert point in sorted list
        insert_point = bisect.bisect(ratio_list, new_ratio) 

        ratio_list.insert(insert_point, new_ratio)
        crew_list.insert(insert_point, crew)

def create_targets_in_window():
    """
    Create F36 targets for all crew in window
    """
    Cui.CuiShowPrompt("Calculating individual F36 targets...")
    area = Cui.CuiWhichArea
    context = CuiContextLocator(area, "window")
    context.reinstate()
    
    # Get total targets per planning group (region) from rave
    region_targets = {}
    region_crew_members = {}
    ix = 1
    while True:
        target = R.eval("studio_freedays.%%total_target%%(%i)" %ix )[0]
        region = R.eval("studio_freedays.%%region_group%%(%i)" %ix )[0]
        if target == None: break
        region_targets[region] = target
        region_crew_members[region] = []
        ix += 1

    # Get crew data
    context_bag = R.context("default_context").bag()
    for crew_bag in context_bag.iterators.roster_set(where = "studio_freedays.%availability% > 0"):
        crew_id = crew_bag.studio_freedays.crew_id()
        region = crew_bag.studio_freedays.crew_region()
        avail = crew_bag.studio_freedays.availability()
        f36_balance_x100 = crew_bag.studio_freedays.balance_F36_x100()
        f36_balance = float(f36_balance_x100)/100
        #print "in",crew_id,region,avail,f36_balance_x100,f36_balance
        cr = crew(crew_id, region, avail, f36_balance)
        try:
            region_crew_members[region].append(cr)
        except KeyError:
            pass  # Region has no total target. Skip crew.

    for region in region_crew_members.keys():
        calculate_targets(region_targets[region], region_crew_members[region])


    # Save individual targets
    tm = M.TableManager.instance()

    tm.loadTable("f36_targets")
    target_table = tm.table("f36_targets")
    crew_table = tm.table("crew")
    planning_period_start = R.eval("studio_freedays.%planning_period_start%")[0]
    for region in region_crew_members.keys():
        save_crew_target_data(region_crew_members[region], target_table, crew_table, planning_period_start)
    Cui.CuiSyncModels(Cui.gpc_info) # don't know if this is necessary

    Cui.CuiShowPrompt("Calculating individual F36 targets... done.")
        
