"""
 $Header$
 
 Standby Line Distribution

 Lists the number of FTE (full time equivalent)
 standby lines for each day in pp, separated by
 category (rank and base and total sum).
 
 Created:    March 2007
 By:         Jonas Carlsson, Jeppesen Systems AB

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from RelTime import RelTime
import Cui
import copy

# constants =============================================================={{{1
TITLE = 'Standby Line Distribution'
FONTSIZEHEAD = 9
FONTSIZEBODY = 8

FROM_IX = 0
TO_IX = 1
TARGET_FTE_IX = 2
ACTUAL_FTE_IX = 3
ACTUAL_NO_IX = 4

def keys_match(long_key, short_key):
    """
    Compares the n first elements in two tuples
    where one is n elements long and the other n+1
    """
    return short_key == long_key[:-1]

def find_matching_keys(long_keys, short_key):
    matching_keys = [x for x in long_keys if keys_match(x,short_key)]
    return matching_keys

class StandbyLineDistribution(SASReport):
    """
    The report class, subclass of SASReport
    """

    def create_key(self, base, rank, start_od):
        """
        Local method to create a constraint key
        """
        return " ".join([base, rank, str(start_od)])
                        
    def header_row(self, dates):
        """
        Local method that creates a row with the dates in the planning period
        """
        tmpRow = self.getCalendarRow(dates, leftHeader='Type', rightHeader='Sum')
        return tmpRow
    
    def format_validity(self, validfrom, validto):
        """
        Local method that formats a validity interval
        """
        return str(validfrom)[:-6] + ' - ' + str(validto - RelTime(24,00))[:-6]

    def prepare_dict(self, dates, target = None, validfrom = None, validto = None):
        """
        Local method that creates a dictionary with the dates as keys and
        either target or None as the data
        """
        data = dict()
        for date in dates:
            if target and date < validto and date >= validfrom:
                data[date] = target
        return data


    
    def create(self, reportType, context='default_context'):
        """
        The main report method
        """
        self.context = context
        self.modify_pp()
        self.objectReport = (reportType == "object")
        self.generalReport = not self.objectReport
        # Basic setup
        SASReport.create(self, TITLE, orientation=LANDSCAPE, usePlanningPeriod=True)
        
        # Get Planning Period start and end
        pp_start, pp_end = R.eval('fundamental.%pp_start%','fundamental.%pp_end%')
        pp_length = (pp_end - pp_start) / RelTime(24, 00)
        date = pp_start
        dates = []
        while date < pp_end:
            dates.append(date)
            date += RelTime(24,0)


        # Set up data structure for the relevant constraints,
        # i.e. those that have crew that matches rank and base
        # For each constraint we need actual and target for each day
        # in the planning period
        constraint_data = dict()
        self.constraint_list = list()
        
        constraint_expr = R.foreach(
            R.times('roster_constraints.%nr_sby_line_need_constraints%',
                    where = 'roster_constraints.%any_crew_match_constraint_pp_start%(fundamental.%py_index%)'),
            'roster_constraints.%constraint_base%(fundamental.%py_index%)',
            'roster_constraints.%constraint_rank%(fundamental.%py_index%)',
            'roster_constraints.%constraint_starttime%(fundamental.%py_index%)',
            'roster_constraints.%constraint_validfrom%(fundamental.%py_index%)',
            'roster_constraints.%constraint_validto%(fundamental.%py_index%)',
            'roster_constraints.%constraint_target%(fundamental.%py_index%)',
            'roster_constraints.%constraint_active%(fundamental.%py_index%)',
            'fundamental.%pp_start%',
            'fundamental.%pp_end%',)

        constraints, = R.eval(self.context, constraint_expr)

        for (ix, base, rank, starttime, validfrom, validto, target, active, ppstart, ppend) in constraints:
            # Create the key for the data and add it to the list
            ##key = self.create_key(base, rank, starttime, validto)

            #Check that the constraint is valid for the planning period
            if active and validfrom <= ppend and validto >= ppstart:
            
            
                key = (base, rank, starttime, validfrom)
                self.constraint_list.append(key)
                
                # Add to a dictionary, with data on the target and a boolean
                # to mark it as used or not
                constraint_data[key] = [validfrom, validto, self.prepare_dict(dates, target, validfrom, validto), {}, {}]

        crew_wrapper = R.foreach(
            R.iter('iterators.roster_set', where = ('roster_constraints.%crew_has_sby_line_in_pp%')),
            'report_common.%crew_id%',
            'report_common.%crew_string%')

        if self.objectReport:
            # For object report, the object report is presented for each selected crew
            # the constraint_data dict is copied each time and used as a base data structure
            crew_collection, = R.eval(self.context, crew_wrapper)
            for ix, crew_id, crew_string in crew_collection:
                constraint_data_per_crew = copy.deepcopy(constraint_data)
                constraint_data_per_crew = self.getRosterData(constraint_data_per_crew, crew_id)
                self.presentData(dates, constraint_data_per_crew, crew_string)
                self.newpage()
        else:
            constraint_data = self.getRosterData(constraint_data)
            self.presentData(dates, constraint_data)

    def getRosterData(self, constraint_data, crewid = None):
        # Collect actual data from the roster, assume each duty day in a standby
        # line trip has the same start time
        day_expr = R.foreach(
            R.times('trip.%pp_days%'),
            'nmax(trip.%start_day%, fundamental.%pp_start%) + (fundamental.%py_index% - 1) * 24:00',
            'report_common.%crew_part_time_factor_at_date%(nmax(trip.%start_day%, fundamental.%pp_start%) + (fundamental.%py_index% - 1) * 24:00)')

        trip_expr = R.foreach(
            R.iter('iterators.trip_set', where = ('trip.%is_standby_line%', 'trip.%in_pp%')),
            'trip.%start_od%',
            'trip.%start_hb%',
            day_expr)

        whereStatement = 'roster_constraints.%crew_has_sby_line_in_pp%'
        if crewid:
            whereStatement += ' and report_common.%crew_id% = "{0}"'.format(crewid)
        crew_expr = R.foreach(
            R.iter('iterators.roster_set', where = whereStatement),
            # No real need to check if crew match a constraint, because if crew has a standby line
            # he/she most likely will match a constraint
            #'roster_constraints.%crew_match_any_constraint_pp_start%')),
            'report_common.%crew_homebase%',
            'report_common.%crew_rank%',
            trip_expr)

        crew, = R.eval(self.context, crew_expr)
        for (ix1, base, rank, trips) in crew:
            for (ix2, start_od, trip_start, days) in trips:
                # Crew might belong to two keys, one with the normal base
                # and one with base = "*"

                key1 = (base, rank, start_od)
                key2 = ('*', rank, start_od)

                keys = find_matching_keys(self.constraint_list, key1)
                keys2 = find_matching_keys(self.constraint_list, key2)
                keys.extend(keys2)

                tmp_dict_FTE = {}
                tmp_dict_NO = {}

                for key in keys:
                    try:
                        tmp_dict_FTE = constraint_data[key][ACTUAL_FTE_IX]
                        tmp_dict_NO = constraint_data[key][ACTUAL_NO_IX]
                    except KeyError:
                        # Do nothing, key was not found among the constraints
                        pass
                    for (ix3, day, fte) in days:
                        tmp_dict_FTE[day] = tmp_dict_FTE.get(day, 0.0) + float(fte) / 100
                        tmp_dict_NO[day] = tmp_dict_NO.get(day, 0) + 1

        return constraint_data

    def presentData(self, dates, constraint_data, crew_string=None):
        # Format output
        if crew_string:
            self.add(Row(Text(crew_string, font=self.HEADERFONT)))
        for constraint in self.constraint_list:
            print_constraint = self.create_key(constraint[0],constraint[1],constraint[2])
            header = print_constraint + ", " + self.format_validity(constraint_data[constraint][FROM_IX], constraint_data[constraint][TO_IX])

            categoryBox = Column()
            categoryBox.add(Row(Text(header), font=self.HEADERFONT))
            categoryBox.add(self.header_row(dates))
            dataBox = Column()

            actualFTERow = Row(Text('Actual (FTE)', font=Font(weight=BOLD)))
            actualNORow = Row(Text('Actual (No)', font=Font(weight=BOLD)))
            targetFTERow = Row(Text('Target', font=Font(weight=BOLD)))

            #targetFTERow = Row(Text('Target (FTE)', font=Font(weight=BOLD)))
            actualFTESum = 0.0
            actualNOSum = 0
            targetFTESum = 0.0
            for date in dates:
                tmpFTEActual = constraint_data[constraint][ACTUAL_FTE_IX].get(date, 0)
                actualFTERow.add(Text(tmpFTEActual, align=RIGHT))
                actualFTESum += tmpFTEActual
                tmpNOActual = constraint_data[constraint][ACTUAL_NO_IX].get(date, 0)
                actualNORow.add(Text(tmpNOActual, align=RIGHT))
                actualNOSum += tmpNOActual
                tmpFTETarget = constraint_data[constraint][TARGET_FTE_IX].get(date, 0)
                if tmpFTETarget:
                    targetFTERow.add(Text(float(tmpFTETarget) / 100, align=RIGHT))
                    targetFTESum += float(tmpFTETarget) / 100
                else: # If no target correspond to this date
                    targetFTERow.add(Text(''))

            actualFTERow.add(Text(actualFTESum, font=Font(weight=BOLD), align=RIGHT))
            actualNORow.add(Text(actualNOSum, font=Font(weight=BOLD), align=RIGHT))
            targetFTERow.add(Text(targetFTESum, font=Font(weight=BOLD), align=RIGHT))
            # SKCMS-337
            #dataBox.add(actualFTERow)
            dataBox.add(actualNORow)
            dataBox.add(targetFTERow)

            categoryBox.add(dataBox)

            self.add(Row(categoryBox))
            self.add(Row(" "))
            self.page0()

        self.reset_pp()

# End of file
