# Custom extension to the data_setup module
import util

from behave import *
from AbsTime import AbsTime

use_step_matcher('re')

@given(u'crew member %(roster_ix)s has homebase "%(homebase)s"' % util.matching_patterns)
def set_crew_homebase(context, roster_ix, homebase):
    """
    Given crew member 1 has homebase "OSL"
    """
    roster_ix = util.verify_int(roster_ix)
    context.ctf.set_crew_homebase(roster_ix, homebase)


@given(u'crew member %(roster_ix)s has contract "%(contract)s"' % util.matching_patterns)
def set_crew_contract(context, roster_ix, contract):
    """
    Given crew member 1 has contract "V133-LH"
    """
    roster_ix = util.verify_int(roster_ix)
    context.ctf.set_crew_contract(roster_ix, contract)

@given(u'crew member %(roster_ix)s has contract "%(contract)s" from %(date)s to %(date2)s' % util.matching_patterns)
def set_crew_contract(context, roster_ix, contract, date, date2):
    """
    Given crew member 1 has contract "V133-LH from 01JAN2018 to 01JAN2019"
    """
    roster_ix = util.verify_int(roster_ix)
    context.ctf.set_crew_contract(roster_ix, contract, AbsTime(str(date)), AbsTime(str(date2)))


@given(u'crew member %(roster_ix)s has document "%(doc)s" from %(date)s to %(date2)s' % util.matching_patterns)
def set_crew_document(context, roster_ix, doc, date, date2):
    """
    Example with only main document:
        Given crew member 1 has document "MEDICAL" from 1JAN2019 to 30JAN2019

    Example with sub document:
        Given crew member 1 has document "REC+LC" from 1JAN2019 to 30JAN2019
    """
    roster_ix = util.verify_int(roster_ix)
    context.ctf.set_crew_document(roster_ix, doc, AbsTime(str(date)), AbsTime(str(date2)))


@given(u'crew member %(roster_ix)s has document "%(doc)s" from %(date)s to %(date2)s and has qualification "%(qualification)s"' % util.matching_patterns)
def set_crew_document_sub(context, roster_ix, doc, date, date2, qualification):
    """
    Given crew member 1 has document "REC+LC" from 1JAN2019 to 30JAN2019 and has qualification "A2"
    """
    roster_ix = util.verify_int(roster_ix)
    context.ctf.set_crew_document(roster_ix, doc, AbsTime(str(date)), AbsTime(str(date2)), ac_qual=qualification)


@given(u'crew member %(roster_ix)s has document "%(doc)s" from %(date)s to %(date2)s with number "%(docno)s"' % util.matching_patterns)
def set_crew_document_sub(context, roster_ix, doc, date, date2, docno):
    """
    Given crew member 1 has document "PASSPORT+SE" from  1JAN2019 to 30JAN2019 with number "12345678"
    """
    roster_ix = util.verify_int(roster_ix)
    context.ctf.set_crew_document(roster_ix, doc, AbsTime(str(date)), AbsTime(str(date2)), docno=docno)


@given(u'crew member %(roster_ix)s has document "%(doc)s" from %(date)s to %(date2)s with number "%(docno)s" and maindoc number "%(maindocno)s"' % util.matching_patterns)
def set_crew_document_sub(context, roster_ix, doc, date, date2, docno, maindocno):
    """
    Given crew member 1 has document "VISA+CN,CREW" from 1JAN2019 to 30JAN2019 with number "AN123456" and maindoc number "12345678"
    """
    roster_ix = util.verify_int(roster_ix)
    context.ctf.set_crew_document(roster_ix, doc, AbsTime(str(date)), AbsTime(str(date2)), docno=docno, maindocno=maindocno)


@given(u'crew member %(roster_ix)s has qualification "%(qualification)s" from %(date)s to %(date2)s' % util.matching_patterns)
def set_crew_qualification(context, roster_ix, qualification, date, date2):
    """
    Given crew member 1 has qualification "ACQUAL+A3 from 1JAN2019 to 30JAN2019"
    """
    roster_ix = util.verify_int(roster_ix)
    context.ctf.set_crew_qualification(roster_ix, qualification, AbsTime(str(date)), AbsTime(str(date2)))


@given(u'crew member %(roster_ix)s has restriction "%(restriction)s" from %(date)s to %(date2)s' % util.matching_patterns)
def set_crew_restriction(context, roster_ix, restriction, date, date2):
    """
    Given crew member 1 has restriction "TRAINING+CAPT" from 1JAN2019 to 30JAN2019"
    """
    roster_ix = util.verify_int(roster_ix)
    context.ctf.set_crew_restriction(roster_ix, restriction, AbsTime(str(date)), AbsTime(str(date2)))


@given(u'crew member %(roster_ix)s has acqual qualification "%(qualification)s" from %(date)s to %(date2)s' % util.matching_patterns)
def set_crew_qual_acqual(context, roster_ix, qualification, date, date2):
    """
    Given crew member 1 has acqual qualification "ACQUAL+A3+NEW+ACTYPE" from 1MAY2018 to 2MAY2018
    """
    roster_ix = util.verify_int(roster_ix)
    context.ctf.set_crew_qual_acqual(roster_ix, qualification, AbsTime(str(date)), AbsTime(str(date2)))


@given(u'crew member %(roster_ix)s has acqual restriction "%(qualification)s" from %(date)s to %(date2)s' % util.matching_patterns)
def set_crew_restr_acqual(context, roster_ix, qualification, date, date2):
    """
    Given crew member 1 has acqual restriction "ACQUAL+A3+NEW+ACTYPE" from 1MAY2018 to 2MAY2018
    """
    roster_ix = util.verify_int(roster_ix)
    context.ctf.set_crew_restr_acqual(roster_ix, qualification, AbsTime(str(date)), AbsTime(str(date2)))

def _replace_heading_name(context, from_value, to_value):
    count = context.table.headings.count(from_value)
    if count is 1:
        context.table.headings[context.table.headings.index(from_value)] = to_value
    elif count > 1:
        assert "Expected at most one column with name %s, found %d" % (from_value, count)


@given(u'crew member %(roster_ix)s has the following training need' % util.matching_patterns)
def add_crew_member_training_need(context, roster_ix):
    """
    Given crew member 1 has the following training need
    | part | valid from | valid to   | course          | attribute  | flights | max days | acqual | completion | si | course subtype |
    | 1    | 1feb2018   | 28feb2018  | CONV TYPERATING | ZFTT LIFUS | 4       | 0        | A4     |            |    |                |
    """

    _replace_heading_name(context, "valid from", "validfrom")
    _replace_heading_name(context, "valid to", "validto")
    _replace_heading_name(context, "course subtype", "course_subtype")
    _replace_heading_name(context, "max days", "maxdays")

    columns = ["crew"] + context.table.headings #[x for x in context.table.headings]
    crew_id = context.ctf.make_crew_id(util.verify_int(roster_ix))

    rows = []
    for row in context.table:
        util.verify_date(row["validfrom"])
        if not row["validfrom"]:
            row["validfrom"] = "01JAN1901"
        util.verify_date(row["validto"])
        rows.append([crew_id] + row.cells)

    context.ctf.add_table_data("crew_training_need", columns, rows)

@given(u'dynamic planning period for %(date)s' % util.matching_patterns)
def new_dynamic_planning_period(context, date):
    """
    Given dynamic planning period for this month
    """
    context.ctf.set_dynamic_planning_period(date)


@given(u'table %(table_name)s additionally contains the following' % util.matching_patterns)
def table_add_data(context, table_name):
    """
    Given table briefing_override additionally contains the following
    | station | deadhead | interval_start_lt | interval_end_lt | briefing |
    | GOT     | False    | 10:00             | 15:00           | 0:45     |
    """
    context.ctf.add_table_data(table_name, context.table.headings, context.table)


@given(u'table %(table_name)s is overridden with the following' % util.matching_patterns)
def table_add_data(context, table_name):
    """
    Given table briefing_override is overridden with the following
    | station | deadhead | interval_start_lt | interval_end_lt | briefing |
    | GOT     | False    | 10:00             | 15:00           | 0:45     |
    """
    context.ctf.add_table_data(table_name, context.table.headings, context.table, replace=True)


# This enables generation of informed published etab data, needed for any rescheduling steps
@given(u'the roster is published')
def table_add_data(context):
    """
    Given the roster is published
    """
    context.ctf.set_roster_emulate_publish()

#
# Personal activity setup extensions
#
@given(u'crew member %(roster_ix)s has a %(un_locked)s %(on_off)s-duty personal activity "%(personal_activity)s" at station "%(stn)s" that starts at %(date)s %(time)s and ends at %(date2)s %(time2)s' % util.matching_patterns)
def create_personal_activity(context, roster_ix, personal_activity, stn, date, time, date2, time2, un_locked, on_off):
    """
    Given crew member 1 has a locked on-duty personal activity "F7" at station "OSL" that starts at 1Aug2018 00:00 and ends at 2Aug2018 01:00
    """
    roster_ix = util.verify_int(roster_ix)
    start_date = util.verify_date(date)
    start_time = util.verify_time(time)
    end_date = util.verify_date(date2)
    end_time = util.verify_time(time2)
    stn = util.verify_stn(stn)
    context.ctf.create_personal_activity(crew_ix=roster_ix, personal_activity=personal_activity, start_date=start_date, start_time=start_time, end_date=end_date, end_time=end_time, stn=stn)

    duty = 'N' if on_off == 'on' else 'F'
    lock = 'L' if un_locked == 'locked' else '*'

    crew_id = context.ctf.make_crew_id(util.verify_int(roster_ix))
    context.ctf.crew[crew_id].personal_activities[-1].onDutyCode = duty
    context.ctf.crew[crew_id].personal_activities[-1].lock = lock


@given(u'personal activity %(leg_ix)s of crew member %(roster_ix)s is %(on_off)s-duty' % util.matching_patterns)
def set_personal_activity_duty(context, leg_ix, roster_ix, on_off):
    """
    Given personal activity 1 of crew member 1 is off-duty
    """
    duty = 'N' if on_off == 'on' else 'F'

    leg_ix = util.verify_int(leg_ix)
    crew_id = context.ctf.make_crew_id(util.verify_int(roster_ix))
    context.ctf.crew[crew_id].personal_activities[leg_ix-1].onDutyCode = duty


@given(u'personal activity %(leg_ix)s of crew member %(roster_ix)s is %(un_locked)s' % util.matching_patterns)
def set_personal_activity_lock(context, leg_ix, roster_ix, un_locked):
    """
    Given personal activity 1 of crew member 1 is unlocked
    """
    lock = 'L' if un_locked == 'locked' else '*'

    leg_ix = util.verify_int(leg_ix)
    crew_id = context.ctf.make_crew_id(util.verify_int(roster_ix))
    context.ctf.crew[crew_id].personal_activities[leg_ix-1].lock = lock


# Personal activity table columns
pact_columns = ('code', 'stn', 'start_date', 'start_time', 'end_date', 'end_time', 'lock', 'duty')


@given(u'crew member %(roster_ix)s has the following personal activities' % util.matching_patterns)
def create_personal_activities_from_table(context, roster_ix):
    """
    Given crew member 1 has the following personal activities
    | code | stn  | start_date | start_time | end_date  | end_time | lock  | duty |
    | R2   | OSL  | 11JAN2011  | 11:11      | 11JAN2011 | 13:13    | False | On   |
    | F    | ARN  | 12JAN2011  |  0:00      | 15JAN2011 |  0:00    | True  | Off  |

Available columns:

        code:               Activity code               (Example: R2)
        stn:                Station                     (Example: OSL)
        start date:         Start date                  (Example: 11JAN2011)
        start time:         Start time                  (Example: 11:11)
        end date:           End date                    (Example: 11JAN2011)
        end time:           End time                    (Example: 11:11)
        lock:               Is the pact (un)locked      (Example: False)
        duty:               Is the pact on/off-duty     (Example: On)
    """

    roster_ix = util.verify_int(roster_ix)
    crew_id = context.ctf.make_crew_id(roster_ix)

    # Add all needed columns, default value to ''
    for column in pact_columns:
        context.table.ensure_column_exists(column)

    # Verify that all columns can be handled
    for column in context.table.headings:
        assert column in pact_columns, 'Cannot handle column %s, use: %s' % (column, ", ".join(pact_columns))

    # Add all personal activities from table
    for row in context.table:
        code = util.verify_str(row[context.table.get_column_index('code')])
        stn = util.verify_str(row[context.table.get_column_index('stn')])
        start_date = util.verify_date(row[context.table.get_column_index('start_date')])
        start_time = util.verify_time(row[context.table.get_column_index('start_time')])
        end_date = util.verify_date(row[context.table.get_column_index('end_date')])
        end_time = util.verify_time(row[context.table.get_column_index('end_time')])
        is_locked = util.verify_boolean(row[context.table.get_column_index('lock')])
        lock = 'L' if is_locked == 'locked' else '*'
        is_on_duty = util.verify_str(row[context.table.get_column_index('duty')])
        duty = 'N' if is_on_duty == 'On' else 'F'

        context.ctf.create_personal_activity(crew_ix=roster_ix, personal_activity=code,
            start_date=start_date, start_time=start_time, end_date=end_date, end_time=end_time, stn=stn)
        context.ctf.crew[crew_id].personal_activities[-1].onDutyCode = duty
        context.ctf.crew[crew_id].personal_activities[-1].lock = lock

