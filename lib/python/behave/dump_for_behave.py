from carmensystems.dave import dmf
import os
import sys
import utils.dave as dave
from AbsTime import AbsTime
from RelTime import RelTime

DUMP_AIRCRAFT_ROTATIONS = False


def get_abstime(record, field):
    if field in record and record[field] is not None:
        return str(AbsTime(record[field]))[:9]
    else:
        return ''


def print_qualifications_and_restrictions(ec, crewid, sql_start_time, sql_end_time):
    for name, table, prefixes in [("qualification", ec.crew_qualification, ["qual"]),
                                  ("acqual qualification", ec.crew_qual_acqual, ["qual", "acqqual"]),
                                  ("restriction", ec.crew_restriction, ["rest"]),
                                  ("acqual restriction", ec.crew_restr_acqual, ["qual", "acqrestr"])]:
        records = [ce for ce in table.search("crew = '%s' and validfrom < %s and validto > %s" % (crewid, sql_end_time, sql_start_time))]
        for record in records:
            parts = []
            for prefix in prefixes:
                parts = parts + [record["%s_typ" % prefix], record["%s_subtype" % prefix]]

            print '    Given crew member 1 has %s "%s" from %s to %s' % (name, '+'.join(parts), get_abstime(record, "validfrom"), get_abstime(record, "validto"))


def get_leg(ec, udor, fd, adep):
    legs = [leg for leg in ec.flight_leg.search("udor = %s and fd = '%s' and adep = '%s'" % (udor, fd, adep))]
    if len(legs) != 1:
        raise Exception("Not matching exactly one leg!")
    return legs[0]


def get_crew_flight_duty_attrs(ec, crewid, udor, fd, adep):
    crew_flight_duty_attrs = [crew_flight_duty_attr for crew_flight_duty_attr in ec.crew_flight_duty_attr.search("cfd_crew = %s and cfd_leg_udor = %s and cfd_leg_fd = '%s' and cfd_leg_adep = '%s'" % (crewid, udor, fd, adep))]
    return crew_flight_duty_attrs


def get_ground_task(ec, task_udor, task_id):
    tasks = [leg for leg in ec.ground_task.search("udor = %s and id = '%s'" % (task_udor, task_id))]
    if len(tasks) != 1:
        raise Exception("Not matching exactly one leg!")
    return tasks[0]


def get_crew_ground_duty_attrs(ec, crewid, udor, id):
    crew_ground_duty_attrs = [crew_ground_duty_attr for crew_ground_duty_attr in ec.crew_ground_duty_attr.search("cgd_crew = %s and cgd_task_udor = %s and cgd_task_id = '%s'" % (crewid, udor, id))]
    return crew_ground_duty_attrs


def get_aircraft_flight_duty(ec, udor, fd, adep):
    entities = [entity for entity in ec.aircraft_flight_duty.search("leg_udor = %s and leg_fd = '%s' and leg_adep = '%s'" % (udor, fd, adep))]
    if len(entities) != 1:
        raise Exception("Not matching exactly one aircraft flight duty!")

    return entities[0]


def escape_string(v):
    if isinstance(v, str):
        return "'%s'" % v
    else:
        return str(v)


def single_search_string(keys_values):
    return "(%s)" % ' and '.join(["%s = %s" % (k, escape_string(v)) for k, v in keys_values.iteritems()])


def get_entities(table, keys):
    search_string = ' or '.join([single_search_string(key) for key in keys])
    entities = [entity for entity in table.search(search_string)]
    return entities


def print_table(name, entities, exclude_fields=['branchid', 'deleted', 'revid'], minute_fields=[], day_fields=[], reltime_fields=[], crewid_fields=[]):
    if len(entities) > 0:
        print "    Given table %s additionally contains the following" % name
        lengths = {}
        str_entities = []
        for entity in entities:
            str_entity = {}
            for column in entity.keys():
                if not column in exclude_fields:
                    if entity[column] is None:
                        str_value = ''
                    elif column in day_fields:
                        str_value = str(AbsTime(entity[column] * 24 * 60))[:9]
                    elif column in minute_fields:
                        str_value = str(AbsTime(entity[column]))
                    elif column in reltime_fields:
                        str_value = str(RelTime(entity[column]))
                    elif column in crewid_fields:
                        str_value = "crew member 1"  # Might need to be extended eventually
                    else:
                        str_value = str(entity[column])
                    if len(str_value) >= lengths.get(column, 0):
                        lengths[column] = len(str_value)
                    str_entity[column] = str_value
            str_entities.append(str_entity)
        columns = lengths.keys()
        for column in columns:
            if len(column) > lengths[column]:
                lengths[column] = len(column)
        print "           | %s |" % ' | '.join([column + ' ' * (lengths[column] - len(column)) for column in columns])
        for str_entity in str_entities:
            for column in columns:
                if column in str_entity.keys():
                    str_entity[column] = str_entity[column] + ' ' * (lengths[column] - len(str_entity[column]))
                else:
                    str_entity[column] = ' ' * lengths[column]
            print "           | %s |" % ' | '.join([str_entity[column] for column in columns])


def print_trips(ec, crewid, sql_start_date, sql_end_date):
    personaltrips = {}
    trips = {}
    aircraft_flight_duties = []
    crew_flight_duties = [ce for ce in ec.crew_flight_duty.search("crew = '%s' and leg_udor < %s and leg_udor >= %s" % (crewid, sql_end_date, sql_start_date))]
    for crew_flight_duty in crew_flight_duties:
        if crew_flight_duty.trip_id is not None and crew_flight_duty.personaltrip is not None:
            raise Exception("Flight duty has personaltrip and trip")
        if crew_flight_duty.trip_id is None and crew_flight_duty.personaltrip is None:
            raise Exception("Flight duty has neither personaltrip nor trip")
        leg = get_leg(ec, int(crew_flight_duty.leg_udor) / 60 / 24, crew_flight_duty.leg_fd, crew_flight_duty.leg_adep)
        aircraft_flight_duties.append(get_aircraft_flight_duty(ec, int(crew_flight_duty.leg_udor) / 60 / 24, crew_flight_duty.leg_fd, crew_flight_duty.leg_adep))

        leg_attrs = get_crew_flight_duty_attrs(ec, crewid, int(crew_flight_duty.leg_udor) / 60 / 24, crew_flight_duty.leg_fd, crew_flight_duty.leg_adep)
        cfd_tuple = ('flight', crew_flight_duty, leg, leg_attrs)
        if crew_flight_duty.trip_id is not None:
            trips[crew_flight_duty.trip_id] = trips.get(crew_flight_duty.trip_id, []) + [cfd_tuple]
        if crew_flight_duty.personaltrip is not None:
            personaltrips[crew_flight_duty.personaltrip] = personaltrips.get(crew_flight_duty.personaltrip, []) + [cfd_tuple]

    crew_ground_duties = [ce for ce in ec.crew_ground_duty.search("crew = '%s' and task_udor < %s and task_udor >= %s" % (crewid, sql_end_date, sql_start_date))]
    gd_index = 0
    for crew_ground_duty in crew_ground_duties:
        if crew_ground_duty.trip_id is not None and crew_ground_duty.personaltrip is not None:
            raise Exception("Ground duty has personaltrip and trip")
        ground_task = get_ground_task(ec, int(crew_ground_duty.task_udor) / 60 / 24, crew_ground_duty.task_id)
        crew_ground_duty_attrs = get_crew_ground_duty_attrs(ec, crewid, int(crew_ground_duty.task_udor) / 60 / 24, crew_ground_duty.task_id)
        cgd_tuple = ('ground', crew_ground_duty, ground_task, [])
        if crew_ground_duty.trip_id is not None:
            trips[crew_ground_duty.trip_id] = trips.get(crew_ground_duty.trip_id, []) + [cgd_tuple]
        elif crew_ground_duty.personaltrip is not None:
            personaltrips[crew_ground_duty.personaltrip] = personaltrips.get(crew_ground_duty.personaltrip, []) + [cgd_tuple]
        else:
            personaltrips[str(gd_index)] = [cgd_tuple]
            gd_index = gd_index + 1

    if DUMP_AIRCRAFT_ROTATIONS:
        rotation_ids = set()
        aircraft_ids = set()
        for aircraft_flight_duty in aircraft_flight_duties:
            rotation_ids.add(aircraft_flight_duty.rot_id)
            aircraft_ids.add(aircraft_flight_duty.ac)
        aircrafts = get_entities(ec.aircraft, [{'id': aircraft_id} for aircraft_id in aircraft_ids])
        rotations = get_entities(ec.rotation, [{'id': rotation_id} for rotation_id in rotation_ids])
        print_table("aircraft", aircrafts)
        print_table("rotation", rotations, day_fields=['udor'])
        print_table("aircraft_flight_duty", aircraft_flight_duties, day_fields=['leg_udor', 'rot_udor'])

    trip_num = 1
    for trips_dict in [trips, personaltrips]:
        for trip_id in trips_dict:
            lines = [('act', 'car', 'num', 'dep stn', 'arr stn', 'dep            ', 'arr            ', 'ac_typ', 'code')]
            position = None

            leg_nr = 1
            attr_dict = {}
            for duty_type, duty, leg, leg_attrs in sorted(trips_dict[trip_id], key=sort_legs):
                if duty_type == 'flight':
                    if duty.pos == 'DH':
                        activity = 'dh'
                    else:
                        activity = 'leg'
                        if position is None:
                            position = duty.pos
                        else:
                            if position != duty.pos:
                                raise Exception("Not the same position throughout trip")

                    carrier = leg.fd.split(' ')[0]
                    number = leg.fd.split(' ')[1]
                    lines.append((activity, carrier, number, leg.adep, leg.ades, str(leg.sobt), str(leg.sibt), leg.actype, ''))
                else: # Ground duty
                    lines.append(('ground', '', '', leg.adep, leg.ades, str(leg.st), str(leg.et), '', leg.activity))
                    position = duty.pos

                for leg_attr in leg_attrs:
                    key = (leg_attr['attr'], leg_attr['value_str'])
                    attr_dict[key] = attr_dict.get(key, []) + [leg_nr]

                leg_nr = leg_nr + 1

            assignments = []

            for key, legs_list in sorted(attr_dict.iteritems(), reverse=True, key=lambda (key, value): len(value)):
                name, value = key
                legs = ','.join([str(leg) for leg in legs_list])
                assignments.append(['attribute', legs, name, value])

            print "    Given a trip with the following activities"
            for line in lines:
                print "           | %s |" % (' | '.join(["%-7s" % part for part in line]))

            if len(assignments) == 0:
                print "    Given trip %s is assigned to crew member 1 in position %s" % (trip_num, position)
            else:
                print "    Given trip %s is assigned to crew member 1 in position %s with" % (trip_num, position)
                print "           | type      | leg             | name            | value           |"

                for typ, legs, attr_name, attr_value in assignments:
                    print "           | %-9s | %-15s | %-15s | %-15s |" % (typ, legs, attr_name, attr_value)
            trip_num = trip_num + 1


def print_personal_activities(ec, crewid, sql_start_time, sql_end_time):
    crew_activities = [ce for ce in ec.crew_activity.search("crew = '%s' and st < %s and st >= %s" % (crewid, sql_end_time, sql_start_time))]
    for crew_activity in crew_activities:
        print '    Given crew member 1 has a personal activity "%s" at station "%s" that starts at %s and ends at %s' % (crew_activity.activity, crew_activity.adep, AbsTime(crew_activity.st), AbsTime(crew_activity.et))


def print_crew_publish_info(ec, crewid, sql_start_date, sql_end_date):
    entities = [entity for entity in ec.crew_publish_info.search("crew = '%s' and start_date < %s and end_date > %s" % (crewid, sql_end_date, sql_start_date))]
    print_table("crew_publish_info", entities, reltime_fields=["prev_informed_duty_time", "duty_time"], minute_fields=["checkin", "checkout", "refcheckin", "refcheckout", "sched_end_time"], day_fields=["start_date", "end_date"], crewid_fields=["crew"])


def print_published_roster(ec, crewid, sql_start_time, sql_end_time):
    entities = [entity for entity in ec.published_roster.search("crew = '%s' and pubstart < %s and pubend > %s" % (crewid, sql_end_time, sql_start_time))]
    print_table("published_roster", entities, minute_fields=["pubstart", "pubend"], crewid_fields=["crew"])


def print_cio_status(ec, crewid):
    entities = [entity for entity in ec.cio_status.search("crew = '%s'" % crewid)]
    print_table("cio_status", entities, minute_fields=["ciotime", "st", "et"], crewid_fields=["crew"])


def print_crew_training_log(ec, crewid):
    entities = [entity for entity in ec.crew_training_log.search("crew = '%s'" % crewid)]
    print_table("crew_training_log", entities, minute_fields=["tim"], crewid_fields=["crew"])

def print_crew_document(ec, crewid):
    entities = [entity for entity in ec.crew_document.search("crew = '%s'" % crewid)]
    print_table("crew_document", entities, minute_fields=["validto", "validfrom"], crewid_fields=["crew"])

def print_roster_attr(ec, crewid, sql_start_time, sql_end_time):
    entities = [entity for entity in ec.roster_attr.search("crew = '%s' and start_time < %s and end_time > %s" % (crewid, sql_end_time, sql_start_time))]
    print_table("roster_attr", entities, minute_fields=["start_time", "end_time"], crewid_fields=["crew"])


def print_privately_traded_days(ec, crewid, sql_start_time, sql_end_time):
    entities = [entity for entity in ec.privately_traded_days.search("crew = '%s' and duty_start < %s and duty_end > %s" % (crewid, sql_end_time, sql_start_time))]
    print_table("privately_traded_days", entities, minute_fields=["duty_start", "duty_end", "period_start", "period_end"], reltime_fields=["duty_time", "duty_overtime"], crewid_fields=["crew"])


def sort_legs(item):
    duty_type, _, leg, _ = item
    if duty_type == 'flight':
        return leg.sobt
    else:
        return leg.st # For ground tasks


def get_latest_commit_id(ec, latest_time):
    translation = (('commitid', 'Integer'),
                   ('committs', 'Integer'))

    maxcommitts = int(latest_time) * 60
    records = []
    for x in dave.L1(dmf.BorrowConnection(ec)).search("select commitid, committs from dave_revision where committs <= %s and rownum <= 1 order by committs desc" % maxcommitts):
        records.append(dict(dave.L1Record.fromRow(x, translation)))

    latest_commit_id = records[0]['commitid']
    latest_commit_time = AbsTime(records[0]['committs'] / 60)
    print("# Based on commit id %s @ %s" % (latest_commit_id, latest_commit_time))

    return latest_commit_id


def main(crewid, start_time, end_time, snapshot_time_or_max_commit_id=None):
    connstr = os.environ['DB_URL']
    schema = os.environ['DB_SCHEMA']

    sql_start_time = int(start_time)
    sql_end_time = int(end_time)
    sql_start_date = int(start_time) / 60 / 24
    sql_end_date = int(end_time) / 60 / 24

    ec = dave.EC(connstr, schema)

    if snapshot_time_or_max_commit_id is not None:
        try:
            max_commit_id = int(snapshot_time_or_max_commit_id)
        except:
            max_commit_id = get_latest_commit_id(ec, AbsTime(snapshot_time_or_max_commit_id))
        print("Using maxcid %s" % max_commit_id)
        ec._rev_filter(maxcid=max_commit_id)

    crew_entries = [ce for ce in ec.crew.search("id = '%s' and employmentdate < %s and ((retirementdate > %s) or (retirementdate is null))" % (crewid, sql_end_date, sql_start_date))]
    if len(crew_entries) == 0:
        raise Exception("No crew record was found")
    if len(crew_entries) > 1:
        raise Exception("Multiple crew records were found")
    crew_entry = crew_entries[0]

    crew_employments = [ce for ce in ec.crew_employment.search("crew = '%s' and validfrom < %s and validto > %s" % (crewid, sql_end_time, sql_start_time))]

    crew_contracts = [ce for ce in ec.crew_contract.search("crew = '%s' and validfrom < %s and validto > %s" % (crewid, sql_end_time, sql_start_time))]

    crew_attrs = [ce for ce in ec.crew_attr.search("crew = '%s'" % (crewid))]

    mappables = [([crew_entry], {'empno': 'employee number',
                                 'sex': 'sex',
                                 'maincat': 'main function'}),
                 (crew_employments, {'base': 'base',
                                     'crewrank': 'crew rank',
                                     'titlerank': 'title rank',
                                     'region': 'region'}),
                 (crew_contracts, {'contract': 'contract'})]

    to_print = [('attribute', 'value', 'valid from', 'valid to')]
    for table, mapping in mappables:
        for row in table:
            validfrom = get_abstime(row, 'validfrom')
            validto = get_abstime(row, 'validto')
            for field, value in mapping.iteritems():
                if row[field] is not None:
                    to_print.append((value, row[field], validfrom, validto))

    map_crew_attr = {'PUBLISHED': ('published', 'value_abs')}
    for crew_attr in crew_attrs:
        if crew_attr['attr'] in map_crew_attr:
            name, field = map_crew_attr[crew_attr['attr']]
            if field == 'value_abs':
                value = str(AbsTime(crew_attr[field]))[:9]
            else:
                value = str(crew_attr[field])
            validfrom = get_abstime(crew_attr, 'validfrom')
            validto = get_abstime(crew_attr, 'validto')

            to_print.append((name, value, validfrom, ''))

    print "    Given a crew member with"
    for attribute, value, validfrom, validto in to_print:
        print "           | %-15s | %-10s | %-10s | %-9s |" % (attribute, value, validfrom, validto)

    print_qualifications_and_restrictions(ec, crewid, sql_start_time, sql_end_time)
    print
    print_crew_document(ec, crewid)
    print
    print_trips(ec, crewid, sql_start_date, sql_end_date)
    print
    print_personal_activities(ec, crewid, sql_start_time, sql_end_time)
    print
    print_crew_training_log(ec, crewid)
    print
    print_roster_attr(ec, crewid, sql_start_time, sql_end_time)
    print
    print_privately_traded_days(ec, crewid, sql_start_time, sql_end_time)


if __name__ == '__main__':
    if len(sys.argv) == 4:
        main(sys.argv[1], AbsTime(sys.argv[2]), AbsTime(sys.argv[3]))
    elif len(sys.argv) == 5:
        main(sys.argv[1], AbsTime(sys.argv[2]), AbsTime(sys.argv[3]), sys.argv[4])
    else:
        print "%s <crew id> <start date> <end date> [<snapshot datetime> | <max commit id>]" % sys.argv[0]
