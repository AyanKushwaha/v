"""
Fetch SAS Link Pairing/Rostering plan data into Tracking
"""

import Attributes
import Cfh
import Cui
import Errlog
import os
import re
import shutil
import tempfile
import time
import weakref

import carmensystems.mave.etab as etab
import carmensystems.rave.api as rave
import carmstd.cfhExtensions as cfhExtensions

from collections import OrderedDict
from carmstd import etab_ext
from carmstd.date_extensions import abstime2gui_date_string, abstime2gui_datetime_string
from carmusr.ground_duty_handler import change_ground_task_status
from carmusr.trip_area_handler import set_area

####################################
######### Entry Functions ##########
####################################


def fetchTrips():
    fetch = FetchTrips()
    fetch.run()


def fetchAssignments():
    fetch = FetchAssignments()
    fetch.run()


####################################
########## Fetch Classes ###########
####################################


class FetchBase(object):
    """Base class for Fetch """
    def __init__(self):
        self.link_carmdata = os.path.expandvars(os.path.join('$CARMUSR', 'current_link_carmdata', 'LOCAL_PLAN'))
        self.plans = Plans(self.link_carmdata)
        self.success = True
        self.method = 'Base'  # This should be redefined

    def run(self):
        # Cfh form pop-up to select Plan
        self.fetchgui = LinkFetchForm(self.plans.LP, self.plans.SP, self.method)
        self.fetchgui.show(True)
        val = self.fetchgui.loop()
        if val != Cfh.CfhOk:
            Errlog.log('FetchSVS:: Plan selection cancelled')
            return

        # Get details from form
        self.chosen_lp, self.chosen_sp = self.fetchgui.chosen_plan()
        self.ok_mode = 0 if self.fetchgui.manual_fetch() else ''
        self.log_mode = 0 if self.fetchgui.fetch_log() else 1
        Errlog.log('FetchSVS:: {}/{} selected'.format(self.chosen_lp, self.chosen_sp))

        # The timetable is changed to 'SVS_Fetch_<currentdatetime>'
        self.target_carmdata = os.path.expandvars('$CARMDATA/LOCAL_PLAN')
        _, version, localplan = self.chosen_lp.split('/')
        self.timetable = time.strftime('SVS_Fetch_%Y%m%d_%H%M')
        self.target_lp = os.path.join(self.timetable, version, localplan)
        self.target_lp_dir = os.path.join(self.target_carmdata, self.target_lp)

        # Copy, Fetch and Processing is wrapped in a try:
        # so that cleanup is in the finally: step
        # Base class assumes fetch() and process() will be defined
        # in child classes
        try:
            # Create target dir if needed
            if not os.path.exists(self.target_lp_dir):
                os.makedirs(self.target_lp_dir)

            # Copy plan from link carmdata to tracking carmdata
            for src in ['etable', 'localplan', '.Dated', self.chosen_sp]:
                src_path = os.path.join(self.link_carmdata, self.chosen_lp, src)
                dst_path = os.path.join(self.target_lp_dir, src)
                try:
                    shutil.copytree(src_path, dst_path)
                except:
                    try:
                        shutil.copy(src_path, dst_path)
                    except:
                        message = 'Link Fetch {} Failed'.format(self.method)
                        message += '\n\nSee logfile for more details'
                        Errlog.log('FetchSVS:: Error copying {} to {}'.format(src_path, dst_path))
                        cfhExtensions.show(message)
                        self.success = False

            if self.success:
                Errlog.log('FetchSVS:: Copied Link plan for fetch')
                Errlog.log('FetchSVS:: Source: {}'.format(os.path.join(self.link_carmdata, self.chosen_lp)))
                Errlog.log('FetchSVS:: Target: {}'.format(self.target_lp_dir))

            if self.success:
                Errlog.log('FetchSVS:: Starting Fetch')
                self.fetch()

            if self.success:
                Errlog.log('FetchSVS:: Starting Processing')
                self.process()

        except Exception as err:
            Errlog.log('FetchSVS:: Exception: {}'.format(err))
            self.success = False

        finally:
            if self.success and self.fetchgui.keep_copy():
                Errlog.log('FetchSVS:: Successful Fetch of {} and Option selected: Keeping copied data'.format(self.method))
            else:
                self.clean_up()

        if self.success:
            message = 'Link Fetch {} Finished'.format(self.method)
            message += '\n\nSource plan: {}/{}'.format(self.chosen_lp, self.chosen_sp)
            Errlog.log('FetchSVS:: ' + message)
            cfhExtensions.show(message)

    def fetch(self):
        """Define in child"""
        raise Exception('FetchSVS: fetch() Not Implemented')

    def process(self):
        """Define in child"""
        raise Exception('FetchSVS: process() Not Implemented')

    def clean_up(self):
        """Generic clean_up, extend in child if necessary"""
        self.target_timetable = os.path.join(self.target_carmdata, self.timetable)
        try:
            shutil.rmtree(self.target_timetable)
            Errlog.log('FetchSVS:: Removed {}'.format(self.target_timetable))
        except:
            Errlog.log('FetchSVS:: Error removing {}'.format(self.target_timetable))


class FetchTrips(FetchBase):
    """Extend FetchBase for Trips"""
    def __init__(self):
        super(FetchTrips, self).__init__()
        self.method = 'Trips'

    def fetch(self):
        """Fetch trips from chosen plan"""
        # Find the start of the pp of the plan being fetched from
        full_sp_path = os.path.expandvars('$CARMDATA/LOCAL_PLAN/{}/{}'.format(self.target_lp, self.chosen_sp))
        pp_etab_path = os.path.join(full_sp_path, 'etable/SpLocal/system/planning_period_and_problem.etab')
        session = etab.Session()
        pp_etab = etab_ext.load(session, pp_etab_path)
        fetch_start = abstime2gui_date_string(pp_etab[0][0])  # first entry in first row

        # Open usual fetch form with selected plans automatically filled in
        fetch_dict = {'FORM': 'FETCH_CRRS_DATED',
                      'AVAILABLE_LP_FILES': self.target_lp,
                      'AVAILABLE_SP_FILES': self.chosen_sp,
                      'FETCH_DATE_START': fetch_start,
                      'BORDER_HANDLING': 'Start Inside',
                      'OK': self.ok_mode}
        try:
            Cui.CuiFetchCRRs(fetch_dict, Cui.gpc_info, self.log_mode)
        except Exception as err:
            Errlog.log('FetchSVS:: CuiFetchCRRs returned: {}'.format(err))
            self.success = False

    def process(self):
        """Activate Ground Duties, Set trip area to SVS"""
        # After the Fetch, Window 0 shows fetched trips
        # this is good, as there is no need to try to identify
        # what is new or old in the plan as long as operations
        # can be run on these trips
        area = Cui.CuiArea0
        # Mark them all
        Cui.CuiMarkAllLegs(Cui.gpc_info, area, 'WINDOW')
        # Set trip area to SVS
        set_area('MARKED', 'SVS', area)
        # Activate Marked Ground Duties
        change_ground_task_status('A')
        # Unmark
        Cui.CuiUnmarkAllLegs(Cui.gpc_info, area, 'WINDOW')
        return


class FetchAssignments(FetchBase):
    """Extend FetchBase for Assignments"""
    def __init__(self):
        super(FetchAssignments, self).__init__()
        self.method = 'Assignments'
        self.crewplan_path = None

    def fetch(self):
        """Fetch assignments from chosen plan"""
        self.crewplan_dir = os.path.expandvars('$CARMDATA/CREW_PLAN')
        self.crewplan_name = 'TO_BE_DETERMINED'  # TODO THIS MUST BE UPDATED
        self.crewplan_path = os.path.join(self.crewplan_dir, self.crewplan_name)
        crewplan = open(self.crewplan_path, 'w')
        crewplan.write("""
/*
Dummy table used during SAS Link Fetch Assignments
*/
18
SCrewId,
SEmpno,
SSurname,
SFirstName,
SSignature,
SMainCat,
SMainFunc,
SComplFunc,
SSndFunc,
STelno,
SSkill,
SPOBox,
SGender,
AMainFuncStart,
AComplFuncStart,
ASndFuncStart,
AExperienceDate1,
AExperienceDate2,
""")
        crewplan.close()
        Errlog.log('FetchSVS:: Created dummy crewplan: {}'.format(self.crewplan_path))

        # Open usual fetch form with selected plans automatically filled in
        fetch_dict = {'FORM': 'FETCH_ASSIGNMENTS',
                      'AVAILABLE_LP_FILES': self.target_lp,
                      'AVAILABLE_SP_FILES': self.chosen_sp,
                      'FETCH_BY': '*',
                      'OK': self.ok_mode}
        try:
            Cui.CuiFetchAssignments(fetch_dict, Cui.gpc_info, self.log_mode)
        except Exception as err:
            Errlog.log('FetchSVS:: CuiFetchAssignments returned: {}'.format(err))
            self.success = False

    def process(self):
        """Set Training Tags on fetched trips"""
        tags = TrainingTags(self.target_lp, self.chosen_sp)
        tags.run()

    def clean_up(self):
        """Extended FetchBase clean_up function"""
        super(FetchAssignments, self).clean_up()
        if self.crewplan_path:
            try:
                os.remove(self.crewplan_path)
                Errlog.log('FetchSVS:: Removed {}'.format(self.crewplan_path))
            except:
                Errlog.log('FetchSVS:: Error removing {}'.format(self.crewplan_path))


####################################
########### Plan Scraper ###########
####################################


class Plans():
    """
    Given a LOCAL_PLAN directory, scrapes it for LP/SP data and exposes it
        - self.LP is a list of local plan paths Timetable/Version/Localplan
        - self.SP is a dict of lists of sub plans under the above local plan paths
    At each point, strips dotfiles from the list AND confirms that anything left is
    a directory as expected.
    """
    def __init__(self, lp_dir):
        self.lp_dir = lp_dir
        self.lp_dict = OrderedDict()
        self._scrape()
        self._process()

    def _scrape(self):
        """Path scraper"""
        timetables = self._remove(os.listdir(self.lp_dir), ['^\.'])
        for timetable in timetables:
            self.lp_dict[timetable] = OrderedDict()
            timetable_path = os.path.join(self.lp_dir, timetable)
            if os.path.isdir(timetable_path):
                versions = self._remove(os.listdir(timetable_path), ['^\.'])
                for version in versions:
                    self.lp_dict[timetable][version] = OrderedDict()
                    version_path = os.path.join(timetable_path, version)
                    if os.path.isdir(version_path):
                        localplans = self._remove(os.listdir(version_path), ['^\.'])
                        for localplan in localplans:
                            localplan_path = os.path.join(version_path, localplan)
                            if os.path.isdir(localplan_path):
                                subplans = os.listdir(localplan_path)
                                subplans = self._remove(subplans, ['^\.', 'etable', 'localplan'])
                                self.lp_dict[timetable][version][localplan] = subplans

    def _process(self):
        """Data processor"""
        self.LP = []
        self.SP = OrderedDict()
        for timetable in self.lp_dict:
            for version in self.lp_dict[timetable]:
                for localplan in self.lp_dict[timetable][version]:
                    lp_string = '{}/{}/{}'.format(timetable, version, localplan)
                    self.LP.append(lp_string)
                    self.SP[lp_string] = []
                    for subplan in self.lp_dict[timetable][version][localplan]:
                        self.SP[lp_string].append(subplan)

    def _remove(self, list, items=[]):
        """Remove items from list using regexps"""
        for item in items:
            regexp = re.compile(item)
            list = [i for i in list if not regexp.match(i)]
        return list


####################################
######## Data Process Steps ########
####################################


class TrainingTags():
    """
    In the current data that has just been fetched, loads the attr tables from the
    fetch plan and applies any new tags to the loaded data
    """
    def __init__(self, lp, sp):
        Errlog.log('FetchSVS:: TrainingTags:: Initialising')
        self.session = etab.Session()
        sp_etab_dir = os.path.expandvars(os.path.join('$CARMDATA/LOCAL_PLAN', lp, sp, 'etable', 'SpLocal'))
        crew_flight_duty_table_path = os.path.join(sp_etab_dir, 'crew_flight_duty_attr.etab')
        crew_ground_duty_table_path = os.path.join(sp_etab_dir, 'crew_ground_duty_attr.etab')
        self.crew_flight_duty_table = etab_ext.load(self.session, crew_flight_duty_table_path)
        self.crew_ground_duty_table = etab_ext.load(self.session, crew_ground_duty_table_path)
        self.ground_duties = self._get_ground_duty_info()

    def run(self):
        self._add_flight_duty_entries()
        self._add_ground_duty_entries()

    def _get_ground_duty_info(self):
        """
        Gets list of ground duties assigned to crew by code and date to map uuids
        """
        self.ground_duty_uuids = {}
        default_bag = rave.context('sp_crew_chains').bag()
        for roster_bag in default_bag.iterators.roster_set():
            crew_id = roster_bag.crew.id()
            self.ground_duty_uuids[crew_id] = {}
            for leg_bag in roster_bag.iterators.leg_set():
                if leg_bag.ground_activity():
                    task_id = leg_bag.leg.code() + '_' + abstime2gui_datetime_string(leg_bag.leg.start_utc())
                    self.ground_duty_uuids[crew_id][task_id] = leg_bag.leg.uuid()

    def _add_flight_duty_entries(self):
        """
        Run through the crew_flight_duty_attr.etab from the fetch plan and
        add all attributes into the database crew_flight_duty_attr table
        """
        for row in self.crew_flight_duty_table:
            udor = row.cfd_leg_udor
            fd = row.cfd_leg_fd
            adep = row.cfd_leg_adep
            crew = row.cfd_crew
            attr = row.attr
            values = {'rel': row.value_rel,
                      'abs': row.value_abs,
                      'int': row.value_int,
                      'str': row.value_str,
                      'si': row.si}
            Attributes.SetCrewFlightDutyAttr(crew, udor, fd, adep, attr, refresh=False, **values)
        Attributes._refresh('crew_flight_duty_attr')
        Errlog.log('FetchSVS:: TrainingTags:: Added Flight Duty Attributes')

    def _add_ground_duty_entries(self):
        """
        Run through the crew_ground_duty_table.etab from the fetch plan and
        set all attributes. Pulls uuid from the roster, if a uuid is not found
        (date out of loaded plan range?) then it is skipped
        """
        missed_ground_duties = []
        for row in self.crew_ground_duty_table:
            udor = row.cgd_task_udor
            task_id = row.cgd_task_id
            crew = row.cgd_crew
            attr = row.attr
            try:
                uuid = self.ground_duty_uuids[crew][task_id]
            except:
                missed_ground_duties.append((task_id, crew))
                continue
            values = {'rel': row.value_rel,
                      'abs': row.value_abs,
                      'int': row.value_int,
                      'str': row.value_str,
                      'si': row.si}
            Attributes.SetCrewGroundDutyAttr(crew, udor, uuid, attr, refresh=False, **values)
        Attributes._refresh('crew_ground_duty_attr')
        Errlog.log('FetchSVS:: TrainingTags:: Added Ground Duty Attributes')
        if missed_ground_duties:
            Errlog.log('FetchSVS:: TrainingTags:: These ground duties in the fetched table could not be found:')
            for task_id, crew in missed_ground_duties:
                Errlog.log('FetchSVS:: TrainingTags:: {}: {}'.format(crew, task_id))


####################################
####### Cfh form definitions #######
####################################


class LinkFetchForm(Cfh.Box):
    """Dynamic form to select Link Fetch plan"""
    def __init__(self, local_plans, sub_plans, method):
        Cfh.Box.__init__(self, "Link_fetch_gui")
        self.local_plans = local_plans
        self.sub_plans = sub_plans
        self.link_local_plans = LinkLocalPlanField(self, self.local_plans)
        self.link_sub_plans = LinkSubPlanField(self, self.sub_plans)
        self.link_keep_copy = KeepCopyField(self)
        self.link_manual_fetch = FetchField(self)
        self.link_fetch_log = FetchLog(self)
        self.ok = Cfh.Done(self, "B_OK")
        self.cancel = Cfh.Cancel(self, "B_CANCEL")

        #CFH Layout
        layout = 'FORM;PLAN_INFO;`SAS Link Fetch {}`'.format(method)
        layout += """
FIELD;LINK_LOCAL_PLANS;`Local Plan`;
FIELD;LINK_SUB_PLANS;`Sub-Plan`;
FIELD;KEEP_COPY;`Keep copy of Link data`;
FIELD;MANUAL_FETCH;`Display Fetch Form`;
FIELD;FETCH_LOG;`Display Fetch Log`;
BUTTON;B_OK;`Ok`;`_Ok`
BUTTON;B_CANCEL;`Cancel`;`_Cancel`
"""

        # Create layout as temp file, load it and then delete
        fd, filepath = tempfile.mkstemp()
        os.write(fd, layout)
        os.close(fd)
        self.load(filepath)
        os.unlink(filepath)

    def chosen_plan(self):
        return self.link_local_plans.valof(), self.link_sub_plans.valof()

    def keep_copy(self):
        return self.link_keep_copy.valof()

    def manual_fetch(self):
        return self.link_manual_fetch.valof()

    def fetch_log(self):
        return self.link_fetch_log.valof()


class LinkLocalPlanField(Cfh.String):
    """LocalPlan field, calls SubPlan field to update menu when LP is chosen"""
    def __init__(self, parent, local_plans):
        self.parent = weakref.proxy(parent)
        super(LinkLocalPlanField, self).__init__(parent, 'LINK_LOCAL_PLANS', 0)

        menu_list = ['Link Local Plans']
        menu_list.extend(local_plans)
        self.setMenu(menu_list)
        self.setMandatory(1)
        self.setMenuOnly(1)

    def compute(self):
        self.parent.link_sub_plans.set_menu(self.getValue())
        self.parent.link_sub_plans.setValue('')


class LinkSubPlanField(Cfh.String):
    """SubPlan field, default empty until LP chosen"""
    def __init__(self, parent, sub_plans):
        self.parent = weakref.proxy(parent)
        self.sub_plans = sub_plans
        self.menu_header = 'Link Sub-plans'
        super(LinkSubPlanField, self).__init__(parent, 'LINK_SUB_PLANS', 0)

        menu_list = [self.menu_header]
        self.setMenu(menu_list)
        self.setMandatory(1)
        self.setMenuOnly(1)

    def set_menu(self, chosen_lp):
        menu_list = [self.menu_header]
        menu_list.extend(self.sub_plans[chosen_lp])
        self.setMenu(menu_list)


class KeepCopyField(Cfh.Toggle):
    """Simple Toggle"""
    def __init__(self, parent):
        self.parent = weakref.proxy(parent)
        super(KeepCopyField, self).__init__(parent, 'KEEP_COPY', 0)


class FetchField(Cfh.Toggle):
    """Simple Toggle"""
    def __init__(self, parent):
        self.parent = weakref.proxy(parent)
        super(FetchField, self).__init__(parent, 'MANUAL_FETCH', 0)


class FetchLog(Cfh.Toggle):
    """Simple Toggle"""
    def __init__(self, parent):
        self.parent = weakref.proxy(parent)
        super(FetchLog, self).__init__(parent, 'FETCH_LOG', 0)
