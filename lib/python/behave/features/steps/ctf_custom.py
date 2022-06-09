# -*- coding: utf-8 -*-

import os
import io
from datetime import date

import Cui
from AbsTime import AbsTime
from AbsDate import AbsDate
from RelTime import RelTime
from utils.rave import RaveIterator
import carmensystems.rave.api as rave
import carmensystems.studio.cpmbuffer as cpmb
import carmensystems.studio.cuibuffer as cuib
import carmusr.tracking.Rescheduling as Rescheduling

from dateutil.relativedelta import relativedelta

import util
import ctf
from ctf import etab_str

class CTFCustom(ctf.CTF):
    def __init__(self, *args, **kwargs):
        super(CTFCustom, self).__init__(*args, **kwargs)
        self.should_emulate_publish = False
        self.roster_published = False


    def init_sp_table(self, table_name, replace=False):
        if not self.sp_etables.has_key(table_name):
            self.sp_etables[table_name] = EtableCustom(table_name, replace)
        return self.sp_etables[table_name]


    def set_crew_homebase(self, crew_ix, homebase):
        """Set the homebase for crew"""
        row_dict = {"crew": self.make_crew_id(crew_ix),
                    "validfrom": "01JAN1901",
                    "validto": "31DEC2099",
                    "carrier": "SK",
                    "company": "SK",
                    "base": homebase,
                    "crewrank": "FP",
                    "titlerank": "FP",
                    "si": "",
                    "region": "SKI",
                    "civicstation": homebase,
                    "station": homebase,
                    "country": "NO",
                    "extperkey": "66666",
                    "planning_group": "SKI"}

        self.add_row_dict("crew_employment", row_dict)

    def set_crew_attr(self, crew_ix, validfrom=None, validto=None, attr=None, value_rel=None, value_abs=None, value_int=None, value_str=None, si=None):
        """Set attr parameters for crew"""
        row_dict = {"crew": self.make_crew_id(crew_ix),
                    "validfrom": util.default(validfrom, "01JAN1901"),
                    "validto": validto,
                    "attr": attr,
                    "value_rel": value_rel,
                    "value_abs": value_abs,
                    "value_int": value_int,
                    "value_str": value_str,
                    "si": si}
        self.add_row_dict("crew_attr", row_dict)

    def set_crew_employment(self, crew_ix, validfrom=None, validto=None, base="ARN", crewrank="FP", titlerank="FP", region="SKI"):
        """Set employment parameters for crew"""

        row_dict = {"crew": self.make_crew_id(crew_ix),
                    "validfrom": util.default(validfrom, "01JAN1901"),
                    "validto": util.default(validto, "31DEC2099"),
                    "carrier": "SK",
                    "company": "SK",
                    "base": base,
                    "crewrank": crewrank,
                    "titlerank": titlerank,
                    "si": "",
                    "region": region,
                    "civicstation": base,
                    "station": base,
                    "country": "NO",
                    "extperkey": "66666",
                    "planning_group": region}
        self.add_row_dict("crew_employment", row_dict)

    def set_crew_contract(self, crew_ix, contract, validfrom=AbsTime("1JAN1901"), validto=AbsTime("31DEC2099")):
        """Set the contract for crew"""
        row_dict = {"crew": self.make_crew_id(crew_ix),
                    "validfrom": str(validfrom),
                    "validto": str(validto),
                    "contract": contract,
                    "si": "",
                    "endreason": "",
                    "patternstart": 0,
                    "cyclestart": 0}
        self.add_row_dict("crew_contract", row_dict)

    def set_crew_document(self, crew_ix, doc, validfrom, validto, docno=None, maindocno=None, ac_qual=None):
        if '+' in doc:
            doc_typ, doc_subtyp = doc.split('+')
        else:
            doc_typ = doc
            doc_subtyp = None

        row_dict = {"crew": self.make_crew_id(crew_ix),
                    "doc_typ": doc_typ,
                    "doc_subtype": doc_subtyp,
                    "validfrom": validfrom,
                    "validto": validto,
                    "docno": docno,
                    "maindocno": maindocno,
                    "issuer": None,
                    "si": None,
                    "ac_qual": ac_qual}
        self.add_row_dict("crew_document", row_dict)

    def set_crew_qualification(self, crew_ix, qualification, validfrom, validto):
        """Set the qualification for crew"""
        qual_typ, qual_subtype = qualification.split('+')
        row_dict = {"crew": self.make_crew_id(crew_ix),
                    "qual_typ": qual_typ,
                    "qual_subtype": qual_subtype,
                    "validfrom": validfrom,
                    "validto": validto,
                    "lvl": None,
                    "si": None,
                    "acstring": None}
        self.add_row_dict("crew_qualification", row_dict)

    def set_crew_restriction(self, crew_ix, restriction, validfrom, validto):
        """Set restriction for a crew"""
        rest_type, rest_subtype = restriction.split('+')
        row_dict = {"crew": self.make_crew_id(crew_ix),
                    "rest_typ": rest_type,
                    "rest_subtype": rest_subtype,
                    "validfrom": validfrom,
                    "validto": validto,
                    "lvl": None,
                    "si": None}
        self.add_row_dict("crew_restriction", row_dict)

    def set_crew_qual_acqual(self, crew_ix, acqqual, validfrom, validto):
        """Set the qualification for crew"""
        qual_typ, qual_subtype, acqqual_typ, acqqual_subtype = acqqual.split('+')
        row_dict = {"crew": self.make_crew_id(crew_ix),
                    "qual_typ": qual_typ,
                    "qual_subtype": qual_subtype,
                    "acqqual_typ": acqqual_typ,
                    "acqqual_subtype": acqqual_subtype,
                    "validfrom": validfrom,
                    "validto": validto,
                    "lvl": None,
                    "si": None}
        self.add_row_dict("crew_qual_acqual", row_dict)

    def set_crew_restr_acqual(self, crew_ix, acqrestr, validfrom, validto):
        """Set the qualification for crew"""
        qual_typ, qual_subtype, acqrestr_typ, acqrestr_subtype = acqrestr.split('+')
        row_dict = {"crew": self.make_crew_id(crew_ix),
                    "qual_typ": qual_typ,
                    "qual_subtype": qual_subtype,
                    "acqrestr_typ": acqrestr_typ,
                    "acqrestr_subtype": acqrestr_subtype,
                    "validfrom": validfrom,
                    "validto": validto,
                    "lvl": None,
                    "si": None}
        self.add_row_dict("crew_restr_acqual", row_dict)

    def set_dynamic_planning_period(self, pp_month):
        if pp_month == 'this month':
            month_start = date.today() + relativedelta(day=1)
            pp_start = AbsTime(month_start.strftime("%d") + month_start.strftime("%b").upper() + month_start.strftime("%Y"))
            month_end = date.today() + relativedelta(day=1, months=+1, days=-1)
            pp_end = AbsTime(month_end.strftime("%d") + month_end.strftime("%b").upper() + month_end.strftime("%Y"))
            self.set_planning_period(pp_start, pp_end)

    def add_to_accumulators(self, the_activity, crews):
        """ TODO: Make the accumulators read from the tables """
        accumulator_int_table = self.init_sp_table('accumulator_int')
        accumulator_rel_table = self.init_sp_table('accumulator_rel')
        accumulator_time_table = self.init_sp_table('accumulator_time')

        for crew, value in crews.iteritems():
            self.accumulate_block_time(the_activity, crew, accumulator_rel_table)


    def accumulate_block_time(self, the_activity, crew, accumulator):
        name = 'accumulators.block_time_acc'
        acckey = crew # TODO: Should be empno instead of crew_id
        time = AbsTime(date.today().strftime('%d') + date.today().strftime('%b').upper() + date.today().strftime('%Y'))
        duration = the_activity.arrival - the_activity.departure
        the_line = {'name': name,'acckey' : acckey, 'tim' : time, 'val' : duration}
        headers = filter(None, [x.strip()[1:-1] for x in accumulator.header.split('\n')]) # Create a list with all header keys and remove any empty strings from the list

        accumulator.add_accumulator_line(the_line, headers)

    def add_table_data(self, table_name, columns, rows, replace=False):
        """Adds the rows to the specified etable in the order defined by the etable,
           regardless of the order specified by the columns. Set replace to True if
           existing rows shall be deleted.
        """
        etab = self.init_sp_table(table_name, replace=replace)

        for row in rows:
            row_dict = {}
            for k, val in zip(columns, row):
                row_dict[k] = self.substitute_reference(val)
            etab.add_line_by_dict(row_dict)

    def add_row_dict(self, table_name, row_dict, replace=False):
        """Adds a row to the specified etable as specified by the given dictionary.
           Keys corresponds to column names. Set replace to True if existing rows shall be deleted.
        """
        etab = self.init_sp_table(table_name, replace=replace)
        etab.add_line_by_dict(row_dict)

    def substitute_reference(self, string):
        crew_member_str = 'crew member '
        if string.startswith(crew_member_str):
            crew_ix = int(string[len(crew_member_str):])
            string = self.make_crew_id(crew_ix)

        return string


    def copy_baseline_etables(self, localplan, subplan):
        super(CTFCustom, self).copy_baseline_etables(localplan, subplan)

        # Some etabs need to be present in the local plan to be found by studio, copy those over
        # This is probably an issue with paths and resources, but for now this workaround will do
        localplan_etabs = ['activity_group_period',
                           'activity_set']

        etable_dir = os.path.expandvars('$CARMDATA/ETABLES/')
        localplan_etable_dir = os.path.expandvars('$CARMDATA/LOCAL_PLAN/%s/etable/LpLocal/' % localplan)

        for etab in localplan_etabs:
            util.copy_file(os.path.join(etable_dir, etab + '.etab'), 
                           os.path.join(localplan_etable_dir, etab))


    def set_roster_emulate_publish(self):
        # Mark this scenario as working with published data, which creates publish info when the plan is created
        self.should_emulate_publish = True


    def roster_was_published(self):
        # Indicates if the roster publish emulation has happened or not
        return self.roster_published


    def create_and_load_plan(self, application):
        if self.should_emulate_publish == True:
            # Create the publish table header in the ctf file so that studio loads it.
            publish_table = self.init_sp_table('crew_publish_info')
            # Load the plan and ctf file so that we can work with rave on existing data
            super(CTFCustom, self).create_and_load_plan(application)
            # Fill publish tables with data and reload tables
            self.create_crew_publish_info_table()
        else:
            # If not emulating published data, load as normal
            super(CTFCustom, self).create_and_load_plan(application)
 

    def create_crew_publish_info_table(self):
        publish_table = self.init_sp_table('crew_publish_info')

        Rescheduling.Plan.init(Rescheduling.ROSTER_PUBLISH)

        # Load rosters in window 0
        # TODO This could possibly cause issues with what's loaded in area 0
        # Ideally we would reload whatever was loaded before when we're done
        # Given that this is executed before the When steps, it should be mostly ok
        _, cui_mode = util.verify_window_mode('rosters')
        Cui.CuiDisplayObjects(Cui.gpc_info, 0, cui_mode, Cui.CuiShowAll)
        # Grab a rave context from the objects in window 0
        cui_buf = cuib.CuiBuffer(0, cuib.WindowScope)
        cpm_buf = cpmb.CpmBuffer(cui_buf, 'true')
        context = rave.buffer2context(cpm_buf)

        # Get a set of iterators from rosters and down the chains
        rosters = RaveIterator(rave.iter('iterators.roster_set'),{
            'crewid':      'crew.%id%',
            },{
            'wops':RaveIterator(rave.iter('iterators.wop_set'),{
                'start_hb':   'rescheduling.%wop_start_date_hb%',
                'end_hb':     'rescheduling.%wop_end_date_hb%',
                'is_on_duty': 'wop.%is_on_duty%',
                'is_ignore':  'rescheduling.%wop_pcat_ignore%',
                'duty_times_per_day': 'rescheduling.%wop_duty_times_per_day%',
                },{
                'trips':RaveIterator(rave.iter('iterators.trip_set'),{
                    'pcat':         'rescheduling.%trip_pcat%',
                    'start_hb':     'rescheduling.%trip_start_date_hb%',
                    'end_hb':       'rescheduling.%trip_end_date_hb%',
                    'checkin_hb':   'rescheduling.%trip_checkin_hb%',
                    'checkout_hb':  'rescheduling.%trip_scheduled_checkout_hb%',
                    'flags':        'rescheduling.%trip_flags%',
                    },{
                    'duties':RaveIterator(rave.iter('iterators.duty_set'),{
                        'pcat':               'rescheduling.%duty_pcat%',
                        'code':               'concat(default(duty.%code%,"?CODE?"),"/",default(duty.%group_code%,"?GRP?"))',
                        'start_hb':           'rescheduling.%duty_start_date_hb%',
                        'end_hb':             'rescheduling.%duty_end_date_hb%',
                        'rest_start_hb':      'rescheduling.%duty_start_date_hb%',
                        'rest_end_hb':        'rescheduling.%duty_rest_end_date_hb%',
                        'flags':              'rescheduling.%duty_flags%',
                        'rest_flags':         'rescheduling.%duty_rest_flags%',
                        'checkin_hb':         'rescheduling.%duty_closest_checkin%',
                        'checkout_hb':        'rescheduling.%duty_closest_scheduled_checkout_hb%',
                        'reference_check_in': 'rescheduling.%reference_check_in%',
                        'refcheckin_valid':   'rescheduling.%reference_check_in_valid%', 
                        'do_not_update_prev_inf_duty_time':'rescheduling.%do_not_update_prev_inf_duty_time%',
                        },{
                        'legs':RaveIterator(rave.iter('iterators.leg_set'),{
                            'start_hb': 'rescheduling.%leg_start_date_hb%',
                            'end_hb':   'rescheduling.%leg_end_date_hb%',
                            'flags':    'rescheduling.%leg_flags%',
                            })
                        })
                    })
                })
            }).eval(context)

        # Iterate over each roster, populating an activity map for that crew and getting their table lines
        for roster in rosters:
            if not roster.crewid:
                continue

            activity_map = ActivityMapCustom(roster.crewid, AbsTime(self.pp_start), AbsTime(self.pp_end))

            for wop in roster.chain('wops'):
                activity_map.addWop(wop)
                for trip in wop.chain('trips'):
                    activity_map.addTrip(trip)
                    for duty in trip.chain('duties'):
                        activity_map.updateDuty(duty)
                        for leg in duty.chain('legs'):
                            activity_map.updateLeg(leg)
            
            publish_table.add_line(activity_map.get_etab_lines())

        # Grab the path of the temporary shadow table that studio is using, and alter that directly
        # Preferably we would be able to add to and reload the table from a normal path, 
        # but test studio seems to have problems with the paths, so this is a workaround
        table_absolute_path = rave.search_etable_identifier('crew_publish_info')

        # Write over the shadow table with the new data
        # Remove the first line with table name, as it's only needed in CTF etab definitions
        data = publish_table.get_ctf_lines().split('\n', 1)[-1]
        with io.open(table_absolute_path, mode='w', encoding='iso-8859-1') as etab_file:
            etab_file.writelines(data)
            etab_file.flush()

        # Reload all tables as reloading a specific table that was added by 
        # CTF file seems to cause problems with path lookups
        Cui.CuiReloadTables(0)

        # Mark the roster publishing as done, enabling rescheduling steps in behave
        self.roster_published = True


# Custom version of ActivityMap from Rescheduling.py
# Contains logic for storing informed data to etab file rather than database
class ActivityMapCustom(Rescheduling.ActivityMap):
    def __init__(self,
                 crewid,
                 start_date,
                 end_date):
                    
        self.crewid = crewid
        # Removing the TableManager lookup as it seems to have problems with loading any table
        self.crew = None
        self.start_date = Rescheduling.copyAsDate(start_date)
        self.end_date = Rescheduling.copyAsDate(end_date)
        self.db_before = self.db_after = None

        # Store a dictionary of (day, activity) to emulate the database
        self.etab_data = {}


    def get_etab_lines(self):
        # This method is a stripped down version of the re-publish/re-inform fuctionality 
        # in ActivityMap.store() in Rescheduling.py, removing any db storage and lookup 
        # of previously informed data. Currently does not support skip days.
        if self.crewid:     
            # Expand map data to cover the full publish/inform period
            self[self.dayInPeriod(self.end_date - RelTime("24:00"))]
            self.data_end_date = self.dateInPeriod(len(self))

            # Iterate over all days in the map, create etab entries when activities are found
            day = 0
            lastday = len(self) - 1
            while day <= lastday:
                # Create a new entry for a new activity
                self.etab_entry_update_or_create(day, self[day])

                startday = day
                day += 1
                
                # Check the following days to see if the activity extends
                # If so, update the end date of the original activity and continue
                while day <= lastday and self[day].canMerge(self[startday]):
                    merge_end_date = AbsDate(self[startday].end_date)
                    self[startday].end_date = max(self[day].end_date, merge_end_date)
                    self[day].end_date = self[startday].end_date
                    self.etab_entry_update_or_create(startday, self[startday])
                    day += 1
                
                # If the original end date for any activity exceeds the date it could
                # be extended to, the limit it
                thisday = day - 1
                nextdate = self.dateInPeriod(thisday) + RelTime("24:00")
                if thisday < lastday:
                    if self[thisday].end_date > nextdate:
                        self[thisday].end_date = nextdate
                        self.etab_entry_update_or_create(thisday, self[thisday])

        lines = ""
        for day, activity in self.etab_data.iteritems():
            lines += '%s\n' % self.make_crew_publish_info_line(activity)

        return lines


    def etab_entry_update_or_create(self, day, activity):
        self.etab_data[day] = activity


    def make_crew_publish_info_line(self, activity):
        _crew_id = '"%s"' % self.crewid

        _start_date = activity.start_date.ddmonyyyy()
        _end_date = activity.end_date.ddmonyyyy()

        # Period category values are ints, and computed on different levels of chains
        # The lowest value in a set has priority, see the values in the rescheduling rave file
        _pcat = '%s' % Rescheduling.PubCat.dbValue(activity.pcat)       

        # Check in/out seems to only be present for on-duty activities
        _checkin = activity.checkin and activity.checkin.ddmonyyyy() or 'VOID'
        # Checkin is often later than the activity starts, probably based on rave rules
        _checkout = activity.checkout and activity.checkout.ddmonyyyy() or 'VOID'

        # Flags correspond to many things, like start/end of working periods and info from previously
        # informed rosters. These always match previously published info, rather than current studio state
        # More info can be found in the rescheduling rave file
        _flags = '"%s"' % (activity.flags and str(activity.flags) or '')

        # TODO these times do not seem to always match up with live studio data.
        # Could be that the scenarios need to be longer, or some other data is missing
        # If your test case needs specific duty times, it's best to hardcode these
        _duty_time = activity.duty_time and activity.duty_time.getValue() or 'VOID'
        _prev_inf_duty_time = activity.prev_informed_duty_time \
            and activity.prev_informed_duty_time.getValue() or 'VOID'

        # Seems unused except for extremely rare cases, needs more investigation
        _ref_checkin = activity.refcheckin and activity.refcheckin.ddmonyyyy() or 'VOID'

        # These seem to be needed, but are not present in the data we fetch from Rescheduling.py
        # Based on data we just assume that if a checkout exists, these should too
        _ref_checkout = activity.checkout and _checkout or 'VOID'
        _sched_end_time = activity.checkout and _checkout or 'VOID'

        parts = [_crew_id, _start_date, _end_date, _pcat, _checkin, _checkout, _flags, _duty_time,
                _prev_inf_duty_time, _ref_checkin, _ref_checkout, _sched_end_time] 
        line = ', '.join(parts) + ';' 
        return line



class EtableCustom(ctf.Etable):

    def __init__(self, etab_name='', replace=False, *args, **kwargs):
        etab_path = os.path.expandvars('$CARMDATA/ETABLES/%s.etab' % etab_name)
        with io.open(etab_path, mode='r', encoding='iso-8859-1') as etab_file:
            etab_data = etab_file.readlines()
        number_of_columns = int(etab_data[0])
        self.columns = []
        for i in range(1, number_of_columns + 1):
            self.columns.append(etab_data[i].split(' ')[0])

        etab_name = super(EtableCustom, self).__init__(etab_name, *args, **kwargs)


        self.header = self.get_header(etab_name)
        self.etab_name = etab_name

        if replace == False:
            # Add the lines from the global etab, if any
            for line in etab_data[number_of_columns + 2:]:
                line = line.rstrip()
                self.add_line(line)


    def get_header(self, etab_name):
        if etab_name == 'dummy':
            return
        else:
            return str(len(self.columns)) + '\n' + ',\n'.join(self.columns + [''])
# FIXME:            assert False, 'Cannot handle etab name %s' % etab_name

    def make_header(self, etab_name):
        """Generate etab header for table"""

    def verify_columns(self, columns):
        column_names = [column[1:] for column in self.columns]
        for column in columns:
            assert column in column_names, "Column %s not found in table %s, use one of | %s |" % (column, self.etab_name, ' | '.join(column_names))


    def add_line_by_dict(self, row_dict):
        self.verify_columns(row_dict.keys())
        parts = []
        for typ, name in [(column[0], column[1:]) for column in self.columns]:
            value = row_dict.get(name)
            if value:
                if typ == 'S':
                    s = util.verify_str(value)
                    if len(s) >= 2 and s.startswith('"') and s.endswith('"'):
                        s = s[1:-1]
                    parts.append(s)
                elif typ == 'B':
                    parts.append(util.verify_boolean(value))
                elif typ == 'A':
                    parts.append(util.verify_abstime(value))
                elif typ == 'I':
                    parts.append(util.verify_int(value))
                elif typ == 'R':
                    parts.append(util.verify_reltime(value))
                else:
                    assert False, "Etab type %s not supported yet" % typ
            else:
                parts.append(None)
        the_line = ', '.join([etab_str(part) for part in parts]) + ';'
        self.add_line(the_line)


    def add_accumulator_line(self, line, headers):
        tmp_x = []
        for k in line:
            if k in headers:
                tmp_x.insert(headers.index(k), line[k])

        for l in self.lines:
            if l[0] == line[headers[0]] and l[1] == line[headers[1]]:
                l[3] += line[headers[3]]
            else:
                self.add_line(tmp_x)

        if not self.lines:
            self.add_line(tmp_x)
