"""
Export Scenarios SAS Link

Uses ExportScenarios.py to export a different set of etables
and then modify the data structures as required by SAS Link Rostering

"""
import Cui
import Errlog
import os
import shutil
import utils.time_util as time_util
import carmusr.planning.ExportScenarios as ES
import carmensystems.mave.etab as etab
import carmensystems.rave.api as R
import carmstd.cfhExtensions as cfhExtensions
import carmstd.studio.plan as plan
from carmstd import etab_ext
from carmstd.date_extensions import abstime2gui_datetime_string
from carmstd.studio.datetoolkit import minus_minute as mm
from AbsTime import AbsTime
from Select import selectTripsOutsidePlanningAreaBaseFilter


def saveLinkScenario(test_mode_params=None):
    timer = time_util.Timer('Exporting Optimizer Scenario')
    if not ES._assert_db():
        return False

    # Only exports tables relevant for Link data reformatting
    # or to avoid warnings during the process
    lptabs = [
        'accumulator_rel',
        'accumulator_time',
        'ac_qual_map',
        'activity_group',
        'activity_group_period',
        'activity_set',
        'activity_set_period',
        'agreement_validity',
        'aircraft_type',
        'ci_exception',
        'crew',
        'crew_complement',
        'crew_contract',
        'crew_document',
        'crew_employment',
        'crew_need_exception',
        'crew_need_jarops_period',
        'crew_need_service',
        'crew_not_fly_with',
        'crew_qual_acqual',
        'crew_qualification',
        'crew_rank_set',
        'crew_restr_acqual',
        'crew_restriction',
        'crew_seniority',
        'flight_leg_attr',
        'flyover',
        'hotel_contract',
        'hotel_transport',
        'lh_apt_exceptions',
        'minimum_connect',
        'lpc_opc_or_ots_composition',
        'preferred_hotel',
        'preferred_hotel_exc',
        'property',
        'rave_string_paramset',
        'simulator_briefings',
        'simulator_composition',
        'simulator_set',
    ]

    sptabs = [
        'crew_flight_duty_attr',
        'crew_ground_duty_attr',
        'ground_task_attr',
    ]

    sptabs += ES._TMP_TABLES_SP.keys()  # Dummy export tables, use model to write them!
    lptabs += ES._TMP_TABLES_LP.keys()

    lptabs.sort()
    sptabs.sort()

    lptabs_str = ' '.join(lptabs)  # Shell array of string (space separated string)
    sptabs_str = ' '.join(sptabs)  # Shell array of string (space separated string)
    os.environ['LP_TABS'] = lptabs_str
    os.environ['SP_TABS'] = sptabs_str

    if not ES.confirmExport(test_mode_params, True):
        return False

    Errlog.log('ExportScenariosSVS:: Removing trips outside of planning area')
    selection_criteria = {'FILTER_MARK': 'Trip'}
    selectTripsOutsidePlanningAreaBaseFilter(selection_criteria, Cui.CuiArea1)
    Cui.CuiRemoveActivities(Cui.gpc_info, Cui.CuiArea1, 'MARKED', 'CRR', 'LEG', 'DISSOLVE', 3)

    Errlog.log('ExportScenariosSVS:: Calling ExportScenarios.saveScenario')
    if not ES.saveScenario(sptabs_str, lptabs_str, timer, test_mode_params, True):
        return False

    Errlog.log('ExportScenariosSVS:: Reformatting tables')
    LTM = LinkTableManipulator(timer, lptabs, sptabs)
    LTM.run()

    lp_path = plan.getCurrentLocalPlanPath()
    sp_name = plan.getCurrentSubPlanName()

    Errlog.log('ExportScenariosSVS:: Saving final plan and then unloading')
    plan.saveLocalPlan()
    plan.saveSubPlan()
    plan.unload()
    timer.tick('Save Exported plan')

    timetable, version, lp_name = lp_path.split('/')
    src_path = os.path.expandvars(os.path.join('$CARMDATA', 'LOCAL_PLAN', lp_path))

    dst_carmdata = '$CARMUSR/current_link_carmdata'
    dst_message = 'Link carmdata'
    # If current_link_carmdata has not been setup, fallback is $CARMTMP
    if not os.path.isdir(os.path.expandvars(dst_carmdata)):
        dst_carmdata = '$CARMTMP'
        dst_message = '$CARMTMP'
    dst_path = os.path.expandvars(os.path.join(dst_carmdata, 'LOCAL_PLAN', timetable, version))

    Errlog.log('ExportScenariosSVS:: Moving plan to Link data')
    Errlog.log('ExportScenariosSVS:: Source: {}'.format(src_path))
    Errlog.log('ExportScenariosSVS:: Destination: {}'.format(dst_path))
    try:
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)
        shutil.move(src_path, dst_path)
    except:
        message = 'Error moving plan to Link data'
        Errlog.log('ExportScenariosSVS:: ' + message)
        cfhExtensions.show(message)
        return False
    timer.tick('Move plan to Link data')

    final_sp_path = os.path.join('LOCAL_PLAN', lp_path, sp_name)

    timer.display()
    message = 'Link Planning Export Finished'
    message += '\n\nPlan is in {} at:'.format(dst_message)
    message += '\n   {}'.format(final_sp_path)
    Errlog.log('ExportScenariosSVS:: ' + message)
    cfhExtensions.show(message)

    return True


class LinkTableManipulator():
    def __init__(self, timer=None, lptabs=None, sptabs=None):
        self.template_path = os.path.join('$CARMUSR', 'crc', 'etable', 'LinkExport')
        self.sp_path = os.path.join(etab_ext.get_splocal_path())
        self.session = etab.Session()
        self.lptabs = lptabs
        self.sptabs = sptabs
        self.timer = timer
        self.lp_start = R.eval('keywords.%global_lp_period_start%')[0]
        self.lp_end = R.eval('keywords.%global_lp_period_end%')[0]

        # These three cases for None below are intended for
        # debugging, to allow the creation of a LinkTableManipulator
        # object without needing to run the full export process
        # It is expected that in production it will always be called
        # from saveLinkScenario
        if self.timer is None:
            self.timer = time_util.Timer('LTM Debug')

        if self.lptabs is None:
            self.lptabs = [
                'accumulator_rel',
                'accumulator_time',
                'ac_qual_map',
                'activity_group',
                'activity_group_period',
                'activity_set',
                'activity_set_period',
                'aircraft_type',
                'crew',
                'crew_contract',
                'crew_document',
                'crew_employment',
                'crew_not_fly_with',
                'crew_qual_acqual',
                'crew_qualification',
                'crew_rank_set',
                'crew_restr_acqual',
                'crew_restriction',
                'crew_seniority',
                'simulator_briefings',
                'simulator_set',
            ]

        if self.sptabs is None:
            self.sptabs = [
                'crew_flight_duty_attr',
                'crew_ground_duty_attr',
                'ground_task_attr',
            ]

        # Extra tables
        self.lptabs.append('export_data')
        self.sptabs.append('gnd_key_mappings')

        # List of blank templated tables
        self.otstabs = [
            'crew_associatedTravelDocument',
            'crew_coworkRestriction',
            'crew_employment',
            'crew_homebase',
            'crew_info',
            'crew_qualification',
            'crew_qualificationEvent',
            'crew_rank',
            'crew_restriction',
            'crew_seniority',
            'crew_travelDocument',
            'blocktime_crew_history',
            'dutytime_crew_history',
            'landing_crew_history',
            'recency_crew_history',
        ]

    def run(self):
        self.load_tables()
        self.timer.tick('Load etables for reformatting')

        self.reformat_tables()
        self.timer.tick('Reformat etables')

        self.edit_tables()
        self.timer.tick('Update attr table references')

        # Cleans new tables and saves them
        self.clean_tables()
        self.save_tables()
        self.timer.tick('Save reformatted etables')

        # Removes the old tables (lptabs and sptabs)
        self.remove_tables()
        self.timer.tick('Remove original etables')

    def load_tables(self):
        # Wrapper to load all the tables
        self.load_source_tables()
        self.load_ots_tables()

    def load_source_tables(self):
        self.source_tables = {}
        for lptab in self.lptabs:
            self.source_tables[lptab] = etab_ext.load(self.session, os.path.join('LpLocal', lptab))
        for sptab in self.sptabs:
            self.source_tables[sptab] = etab_ext.load(self.session, os.path.join('SpLocal', sptab))

    def load_ots_tables(self):
        self.ots_tables = {}
        for otstab in self.otstabs:
            otstab_path = os.path.join(self.template_path, otstab + '.etab')
            self.ots_tables[otstab] = etab_ext.load(self.session, otstab_path)

    def reformat_tables(self):
        # These tables are built from mapped data
        self.crew_associatedTravelDocument()
        self.crew_coworkRestriction()
        self.crew_employment()
        self.crew_homebase()
        self.crew_info()
        self.crew_qualification()
        self.crew_qualificationEvent()
        self.crew_rank()
        self.crew_restriction()
        self.crew_seniority()
        self.crew_travelDocument()
        self.blocktime_crew_history()
        self.dutytime_crew_history()
        self.landing_crew_history()
        self.recency_crew_history()

    def edit_tables(self):
        # These tables are edits of the existing data
        self.crew_flight_duty_attr()
        self.crew_ground_duty_attr()

    def clean_tables(self):
        # Removes identical rows from all tables
        # Assumes tables have already been sorted
        for otstab in self.otstabs:
            table = self.ots_tables[otstab]
            prev_row = None
            row_ixs = []
            for row in table:
                if prev_row is not None and tuple(row) == tuple(prev_row):
                    row_ixs.append(table.getRowIndex(row))
                else:
                    prev_row = row
            row_ixs.sort(reverse=True)  # Reverse order to modify table in place
            for row_ix in row_ixs:
                table.remove(row_ix)

    def save_tables(self):
        # Saves tables into subplan
        for otstab in self.otstabs:
            self.ots_tables[otstab].save(os.path.join(self.sp_path, otstab + '.etab'))

    def remove_tables(self):
        # Removes old tables now data has been reformatted
        for lptab in self.lptabs:
            self.remove_table(etab_ext.expand_etab_path(os.path.join('LpLocal', lptab)))
        for sptab in self.sptabs:
            self.remove_table(etab_ext.expand_etab_path(os.path.join('SpLocal', sptab)))

    def remove_table(self, table_path):
        if os.path.isfile(table_path):
            os.remove(table_path)

    def _lp_overlap(self, start, end):
        # Returns overlap with the lp period, used to only
        # include relevant rows in tables
        return time_util.overlap(self.lp_start, self.lp_end, start, end)

    def crew_associatedTravelDocument(self):
        """
        crew_associatedTravelDocument.etab
        Source: crew_document
        Selection: Rows with doc_typ = VISA
        Mapping: crew > crewId, doc_typ > type, issuer > issueCountry, validfrom > issueDate, validto > expiryDate
        """
        table = self.ots_tables['crew_associatedTravelDocument']

        for row in self.source_tables['crew_document']:
            if row.doc_typ == 'VISA' and self._lp_overlap(row.validfrom, row.validto):
                table.append((row.crew, row.doc_typ, row.issuer, row.validfrom, mm(row.validto)))

        table.sort(('crewId', 'expiryDate'))

    def crew_coworkRestriction(self):
        """
        crew_coworkRestriction.etab
        Source: crew_not_fly_with
        Mapping: crew1 > crewId, crew2 > crew2, validfrom > validFrom, validto > validTo
        Additional fields: coworkRestrictionType: populate with "Prohibit"
        """
        table = self.ots_tables['crew_coworkRestriction']

        for row in self.source_tables['crew_not_fly_with']:
            if self._lp_overlap(row.validfrom, row.validto):
                table.append((row.crew1, row.validfrom, mm(row.validto), row.crew2, None, None))

        table.sort(('crewId', 'validFrom'))

    def crew_employment(self):
        """
        Source: crew (c), crew_contract (cc), crew_employment (ce)
        Mapping: c.id> crewId, c.empno > employeeNumber, ce.company > employer, ce.titlerank > titleRank,
                 cc.contract > contract, cc.validfrom > validFrom, cc.validto > validTo, ce.crewrank > crewCategory
        Translations: crewrank mapped to crewCategory
        Notes: The data is retrieved from three tables, theoretically contract and employment validity don't
               match, would make sense to create based on contract data.
        Rave required: crew_rank_set
        """
        table = self.ots_tables['crew_employment']

        # Avoid repeated searching of employment table by gathering required info once
        # Table is exported from db already sorted so the list preserves validfrom order
        # this is important in a moment
        employment_info = {}
        for employment_row in self.source_tables['crew_employment']:
            crew = employment_row.crew
            if not crew in employment_info:
                employment_info[crew] = []
            employment_info[crew].append({'validfrom': employment_row.validfrom,
                                          'validto': employment_row.validto,
                                          'company': employment_row.company,
                                          'titlerank': employment_row.titlerank,
                                          'crewrank': employment_row.crewrank})

        for row in self.source_tables['crew']:
            crewId = row.id
            employeeNumber = row.empno

            for contract_row in self.source_tables['crew_contract'].search('(crew={})'.format(crewId)):
                contract = contract_row.contract
                validFrom = contract_row.validfrom
                validTo = contract_row.validto

                employer, titleRank, crewCategory = None, None, None
                for crew_info in employment_info[crewId]:
                    # Takes info from the earliest overlapping employment period
                    if time_util.overlap(crew_info['validfrom'], crew_info['validto'],
                                         validFrom, validTo):
                        employer = crew_info['company']
                        titleRank = crew_info['titlerank']
                        crewCategory = R.eval('crew.%maincat_for_rank%("{}")'.format(crew_info['crewrank']))[0]
                        break

                if self._lp_overlap(validFrom, validTo):
                    table.append((crewId, employeeNumber, employer, titleRank, contract, validFrom, mm(validTo), crewCategory))

        table.sort(('crewId', 'validFrom'))

    def crew_homebase(self):
        """
        Source: crew_employment
        Mapping: crew > crewId, base > homebase, validfrom > validFrom, validto > validTo
        """
        table = self.ots_tables['crew_homebase']

        for row in self.source_tables['crew_employment']:
            if self._lp_overlap(row.validfrom, row.validto):
                table.append((row.crew, row.base, row.validfrom, mm(row.validto)))

        table.sort(('crewId', 'validFrom'))

    def crew_info(self):
        """
        Source: crew
        Mapping: id > crewId, name > surName, forenames > givenName, title > title, sex > gender, birthday > birthDate
        """
        table = self.ots_tables['crew_info']

        for row in self.source_tables['crew']:
            table.append((row.id, row.name, row.forenames, row.title, row.sex, row.birthday, None, None, None))

        table.sort(('crewId'))

    def crew_qualification(self):
        """
        Source: crew_qualification
        Mapping: crew > crewId, validfrom > validFrom, validto > validTo, qual_typ > qualificationCategory,
                 qual_subtype > qualification
        Translations: - qual_typ ACQUAL translated to AIRCRAFT
                      - qual_typ POSITION translated to INSTRUCTOR when qual_subtype is LCP or LCS
                      - qual_typ POSITION translated to OPS when qual_subtype is SCC or RHS

        Source 2: crew_qual_acqual
        Mapping: crew > crewId, validfrom > validFrom, validto > validTo, acqqual_typ > qualificationCategory,
                 acqqual_subtype > qualification
        Notes: Link is single fleet, we can ignore the qual_* fields.
        """
        table = self.ots_tables['crew_qualification']
        instructor_subtypes = ['LCP', 'LCS']
        ops_subtypes = ['SCC', 'RHS']

        def _qual_typ(qual_typ, qual_subtype):
            if qual_typ == 'ACQUAL':
                return 'AIRCRAFT'
            elif qual_typ == 'POSITION' and qual_subtype in instructor_subtypes:
                return 'INSTRUCTOR'
            elif qual_typ == 'POSITION' and qual_subtype in ops_subtypes:
                return 'OPS'
            else:
                return qual_typ

        for row in self.source_tables['crew_qualification']:
            if self._lp_overlap(row.validfrom, row.validto):
                table.append((row.crew, row.validfrom, mm(row.validto), row.qual_subtype, _qual_typ(row.qual_typ, row.qual_subtype)))

        for row in self.source_tables['crew_qual_acqual']:
            if self._lp_overlap(row.validfrom, row.validto):
                table.append((row.crew, row.validfrom, mm(row.validto), row.acqqual_subtype, row.acqqual_typ))

        table.sort(('crewId', 'validFrom'))

    def crew_qualificationEvent(self):
        """
        Source: crew_document
        Selection: Rows with doc_typ = REC
        Mapping: crew > crewId, doc_subtype > eventType, ac_qual > requiredEquipment, validto > needEnd
        Notes: ac_qual field should be translated to the family.
        Rave required: ac_qual_map, aircraft_type
        """
        table = self.ots_tables['crew_qualificationEvent']

        def _ac_qual(ac_qual):
            ac_type = R.eval('leg.%ac_type_by_qual%("{}")'.format(ac_qual))[0]
            ac_family = R.eval('leg.%_ac_family%("{}")'.format(ac_type))[0]
            return ac_family

        for row in self.source_tables['crew_document'].search('(doc_typ=REC)'):
            if self._lp_overlap(AbsTime('19860101'), row.validto):
                table.append((row.crew, row.doc_subtype, _ac_qual(row.ac_qual), None, mm(row.validto),
                              None, None, None, None, None))

        table.sort(('crewId', 'needEnd'))

    def crew_rank(self):
        """
        Source: crew_employment
        Mapping: crew > crewId, crewrank > rank, validfrom > validFrom, validto > validTo, crewrank > category
        Translations: crewrank mapped to category
        Rave required: crew_rank_set
        """
        table = self.ots_tables['crew_rank']

        for row in self.source_tables['crew_employment']:
            if self._lp_overlap(row.validfrom, row.validto):
                category = R.eval('crew.%maincat_for_rank%("{}")'.format(row.crewrank))[0]
                table.append((row.crew, row.crewrank, row.validfrom, mm(row.validto), category))

        table.sort(('crewId', 'validFrom'))

    def crew_restriction(self):
        """
        Source: crew_restriction
        Mapping: crew > crewId, validfrom > validFrom, validto > validTo, rest_typ > restrictionCategory,
                 rest_subtype > restriction

        Source 2: crew_restr_acqual
        Mapping: crew > crewId, validfrom > validFrom, validto > validTo, acqrestr_typ > restrictionCategory,
                 acqrestr_subtype > restriction
        Notes: Link is single fleet, we can ignore the qual_* fields.
        """
        table = self.ots_tables['crew_restriction']

        for row in self.source_tables['crew_restriction']:
            if self._lp_overlap(row.validfrom, row.validto):
                table.append((row.crew, row.validfrom, mm(row.validto), row.rest_subtype, row.rest_typ, None, None))

        for row in self.source_tables['crew_restr_acqual']:
            if self._lp_overlap(row.validfrom, row.validto):
                table.append((row.crew, row.validfrom, mm(row.validto), row.acqrestr_subtype, row.acqrestr_typ, None, None))

        table.sort(('crewId', 'validFrom'))

    def crew_seniority(self):
        """
        Source: crew_seniority
        Mapping: crew > crewId, validfrom > validFrom, validto > validTo, seniority> seniority, grp> group
        """
        table = self.ots_tables['crew_seniority']

        for row in self.source_tables['crew_seniority']:
            if self._lp_overlap(row.validfrom, row.validto):
                table.append((row.crew, row.grp, row.seniority, row.validfrom, mm(row.validto)))

        table.sort(('crewId', 'validFrom'))

    def crew_travelDocument(self):
        """
        Source: crew_document
        Selection: Rows with doc_typ = PASSPORT
        Mapping: crew > crewId, doc_typ > type, issuer > issueCountry, validfrom > issueDate, validto > expiryDate
        """
        table = self.ots_tables['crew_travelDocument']

        for row in self.source_tables['crew_document'].search('(doc_typ=PASSPORT)'):
            if self._lp_overlap(row.validfrom, row.validto):
                table.append((row.crew, row.doc_typ, row.issuer, row.validfrom, mm(row.validto)))

        table.sort(('crewId', 'issueDate'))

    def blocktime_crew_history(self):
        """
        Source: accumulator_rel
        Selection: Rows with name = block_time_daily_acc & block_time_acc
        Mapping: acckey > crewId, tim > timestamp, val > value
        Notes: CMS stores the value as accumulated from a historic starting point, OTS expects the value
               until start of pp.  The logic could probably be: newvalue = last value - oldvalue, where
               last value is the last entry in the CMS table.
        """
        table = self.ots_tables['blocktime_crew_history']

        self._recalc_accumulator_rel(table, '(name=accumulators.block_time_acc)')
        self._recalc_accumulator_rel(table, '(name=accumulators.block_time_daily_acc)')

        table.sort(('crewId', 'timestamp'))

    def dutytime_crew_history(self):
        """
        Source: accumulator_rel
        Selection: Rows with name = duty_time_acc & duty_time_in_period_caa_acc
        Mapping: acckey > crewId, tim > timestamp, val > value
        Notes: Same as for block_time_crew_history.etab
        """
        table = self.ots_tables['dutytime_crew_history']

        self._recalc_accumulator_rel(table, '(name=accumulators.duty_time_acc)')
        self._recalc_accumulator_rel(table, '(name=accumulators.duty_time_in_period_caa_acc)')

        table.sort(('crewId', 'timestamp'))

        prev_row = None
        row_ixs = []
        for row in table:
            if prev_row is not None and tuple(row) == tuple(prev_row):
                row_ixs.append(table.getRowIndex(row))
            else:
                prev_row = row
        row_ixs.sort(reverse=True)  # Reverse order as modifying table in place
        for row_ix in row_ixs:
            table.remove(row_ix)

    def _recalc_accumulator_rel(self, table, ldap):
        """
        Sub-function used by blocktime and dutytime to recalculate accumulator_rel values
        to value until start of PP instead of from historic starting point
        """
        # Gather dict of crew with list of tuples of (date, value)
        acc_dict = {}
        for row in self.source_tables['accumulator_rel'].search(ldap):
            crew = row.acckey
            if not crew in acc_dict:
                acc_dict[crew] = []
            acc_dict[crew].append((row.tim, row.val))

        # Sort each list of tuples, this puts them in AbsTime order
        # Then, taking the latest value in the table, use that as the 0 point for
        # calculating all the block time backwards.
        for crew in acc_dict:
            acc_dict[crew].sort()
            latest_date, latest_value = acc_dict[crew][-1]
            for date, value in acc_dict[crew]:
                new_value = latest_value - value
                table.append((crew, date, new_value))

    def landing_crew_history(self):
        """
        Source: accumulator_time
        Selection: Rows with name = last_landing_*
        Mapping: acckey > crewId, tim > timestamp, name > ac_family
        Notes: The ac_family should be retrieved from the name of the accumulator, capitalized.
        """
        table = self.ots_tables['landing_crew_history']

        def _ac_family(name):
            # Get uppercase AC fam from string e.g. 'last_landing_a320'
            return name.split('_')[2].upper()

        for row in self.source_tables['accumulator_time'].search('(name=*last_landing_*)'):
            table.append((row.acckey, _ac_family(row.name), row.tim))

        table.sort(('crewId', 'timestamp'))

    def recency_crew_history(self):
        """
        Source: accumulator_time
        Selection: Rows with name = last_flown_*
        Mapping: acckey > crewId, tim > timestamp, name > ac_family
        Notes: The ac_family should be retrieved from the name of the accumulator, capitalized.
        """
        table = self.ots_tables['recency_crew_history']

        def _ac_family(name):
            # Get uppercase AC fam from string e.g. 'last_flown_a320'
            return name.split('_')[2].upper()

        for row in self.source_tables['accumulator_time'].search('(name=*last_flown_*)'):
            table.append((row.acckey, _ac_family(row.name), row.tim))

        table.sort(('crewId', 'timestamp'))

    def crew_flight_duty_attr(self):
        """
        Source: crew_flight_duty_attr
        Mapping: None
        Selection: Rows with attr = TRAINING or INSTRUCTOR
        Notes: Model in OTS is quite different, but the CMS one can be read, we keep as is.
        """
        source = self.source_tables['crew_flight_duty_attr']

        # Clone the source table and empty it to get a clean etab
        table = etab.clone(self.session, source, os.path.join(self.sp_path, 'crew_flight_duty_attr.etab'))
        table.clear()

        for row in source.search('(|(attr=TRAINING)(attr=INSTRUCTOR))'):
            table.append(tuple(row))

        table.sort(('cfd_crew', 'cfd_leg_udor'))
        table.save()

    def crew_ground_duty_attr(self):
        """
        Source: crew_ground_duty_attr & gnd_key_mappings
        Mapping: None
        Notes: Replace cgd_task_id with code & st from gnd_key_mappings. Model in OTS is quite different,
               but the CMS one can be read, we keep as is.
        """
        source = self.source_tables['crew_ground_duty_attr']
        table = etab.clone(self.session, source, os.path.join(self.sp_path, 'crew_ground_duty_attr.etab'))

        task_id_mapping = {}
        for row in self.source_tables['gnd_key_mappings']:
            task_id_mapping[row.uuid] = row.code + '_' + abstime2gui_datetime_string(row.st)

        for row in table:
            row.cgd_task_id = task_id_mapping[row.cgd_task_id]

        table.sort(('cdg_crew', 'cdg_task_udor'))
        table.save()
