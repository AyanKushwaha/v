"""
Script to process results of cabin initial training pre-run
and store the results needed for main run.

@author: Mattias Lindby <mattias.lindby@jeppesen.com>
@since: 2018-10-23
"""
import os

import Cui
import Localization as L
from carmensystems.mave import etab

import carmstd.bag_handler
import carmstd.etab_ext


INITIAL_TRAINING_TABLE_NAME = 'allocated_initial_cabin_training.etab'

def parse_and_process_pre_run():
    etab_path = os.path.join(carmstd.etab_ext.get_splocal_path(), INITIAL_TRAINING_TABLE_NAME)
    create_allocated_training_table(etab_path)
    lock_trips_from_pre_run()
    Cui.CuiReloadTables(0)
    

def create_allocated_training_table(etab_path):
    """
    Parse training rosters and store supernum & release flights in table
    """
    fields = [('crew_id', str),
              ('leg_key', str),
              ('training_sub_type', str)]
    session = etab.Session()
    initial_training_table = etab.create(session, etab_path)
    for field_name, field_type in fields:
        initial_training_table.appendColumn(field_name, field_type)
    
    plan_crew = carmstd.bag_handler.PlanRosters()
    roster_bag = plan_crew.bag
    
    if roster_bag:
        for roster in roster_bag.iterators.roster_set(where='training_matador.%roster_has_cabin_training_allocated%'):
            crew_id = roster.crew.id()
            for leg in roster.iterators.leg_set():
                leg_key = leg.training.cabin_training_leg_key()
                training_sub_type = leg.training_matador.leg_training_sub_type()
                if training_sub_type:
                    row = (crew_id, leg_key, training_sub_type)
                    initial_training_table.append(row)
        initial_training_table.save()
    else:
        raise ValueError("No rosters in subplan")


def lock_trips_from_pre_run():
    window = Cui.CuiArea0
    byp = [('FORM', 'form_crew_filter'),
           ('DEFAULT', ''),
           ('FILTER_PRINCIP', L.bl_msgr('ANY')),
           ('FILTER_METHOD', L.bl_msgr('REPLACE')),
           ('FILTER_MARK', L.bl_msgr('Trip')),
           ('CRC_VARIABLE_0', 'training_matador.%leg_is_assigned_as_cabin_training%'),
           ('CRC_VALUE_0', 'T')]
    Cui.CuiFilterObjects(byp, Cui.gpc_info,
                         window, 'CrewFilter',
                         'form_crew_filter', 0)
    Cui.CuiUpdateTripLocks(Cui.gpc_info, window, "MARKED", 1)
