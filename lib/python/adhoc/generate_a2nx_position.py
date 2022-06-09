#! /usr/bin/env python

"""
SKCMS-2354: Adds A2LR+POSITION qualification for all crew who completed corresponding
A2LR course (Q2LR for CC and LRP2 for FD) on the day before yesterday.
Job is configured in etc/sysmond/crontab_main.xml.

SKCMS-2613: Renames A2LR POSITION to A2NX POSITION qualification
"""


from datetime import datetime
import logging
import sys
import os

try:
    from carmensystems.dig.framework.dave import DaveConnector, DaveSearch, DaveStorer, createOp
    from AbsTime import AbsTime
except ImportError:
    if sys.executable.startswith('/opt/Carmen'):
        raise Exception("Cannot even start with 'carmpython', check your installation!")
    try:
        os.environ['CARMUSR']
    except:
        raise Exception("Environment CARMUSR must be set.")

# Constants
COURSE_CC = "Q2LR"
COURSE_FD = "LRP2"
DC = DaveConnector(os.environ['DB_URL'], os.environ['DB_SCHEMA'])


def date_interval():
    """
    Get the day before yesterday.
    :return: Tuple with start and end time for the day before yesterday.
    """
    now = AbsTime(str(datetime.now().strftime('%d%b%Y')))
    from_date = now.day_floor().adddays(-4)
    to_date = from_date.adddays(3)

    return from_date, to_date


def crew_with_course(start_date, end_date):
    """
    Finds all crew with A2NX course in training log within the given dates.
    :param start_date: Date which the course should be completed after.
    :param end_date: Date which the course should be completed before.
    :return: List of crew with A2NX course in training log and date when the course started.
    """
    search_query = ["tim>=%s AND tim<%s AND typ='COURSE' AND (code='%s' OR code='%s')" %
                    (int(start_date),
                     int(end_date),
                     COURSE_CC,
                     COURSE_FD)]
    search_result = DC.runSearch(DaveSearch("crew_training_log", search_query))

    return [{'crew_id': entry['crew'], 'course_start': AbsTime(entry['tim'])} for entry in search_result]


def update_database(crew_id, valid_from):
    """
    Updates the database with new POSITION+A2NX qualification for crew.
    :param crew_id: Crew.
    :param valid_from: Qualification validfrom value. Should be the same as course start.
    :return:
    """
    ops = [createOp('crew_qualification', 'N', {'crew': crew_id,
                                                'qual_typ': 'POSITION',
                                                'qual_subtype': 'A2NX',
                                                'validfrom': int(valid_from.day_floor()),
                                                'validto': int(AbsTime("01Jan2036"))})]

    DaveStorer(DC).store(ops)


def validate_crew(crew_id, course_start, interval_start, interval_end):
    """
    Validates if a new POSITION+A2NX row could be added for crew.
    New entry should be added if no previous POSITION+A2NX qualification already exist and
    the course date is within the given interval.
    :param crew_id:
    :param course_start:
    :param interval_start:
    :param interval_end:
    :return: True if new row should be added, otherwise False.
    """
    search_query = ["crew='%s' AND qual_typ='%s' AND qual_subtype='%s'" % (crew_id, "POSITION", "A2NX")]
    if DC.runSearch(DaveSearch("crew_qualification", search_query)):
        return False

    if course_start < interval_start or interval_end < course_start:
        # Just to be sure. This should probably never happen since the DB search filters by date.
        return False

    return True


def add_qualification(crew_list, interval_start, interval_end):
    """
    Iterates crew_list and adds qualification POSITION+A2NX for eligible crew that doesn't already have it.
    :param interval_end:
    :param interval_start:
    :param crew_list:
    :return: Tuple with number of updated and skipped crew.
    """

    updated_crew, skipped_crew = 0, 0
    for crew in crew_list:
        crew_id, course_start_date = crew['crew_id'], crew['course_start']

        if not validate_crew(crew_id, course_start_date, interval_start, interval_end):
            skipped_crew += 1
            continue

        try:
            update_database(crew_id, course_start_date)
        except Exception as e:
            logging.error("Exception occurred: %s" % e)
        else:
            updated_crew += 1

    return updated_crew, skipped_crew


def run():
    logging.info("Start adding of POSITION+A2NX qualification for valid crew.")
    start_time = datetime.now()

    interval_start, interval_end = date_interval()
    crew_list = crew_with_course(interval_start, interval_end)
    logging.info("%s crew with A2NX course between %s and %s. " % (len(crew_list), interval_start, interval_end))

    updated_crew, skipped_crew = add_qualification(crew_list, interval_start, interval_end)
    elapsed = datetime.now() - start_time
    logging.info("Added POSITION+A2NX qualification for %s crew, skipped %s crew." %
                 (updated_crew, skipped_crew))
    logging.info("Elapsed time %s" % elapsed)


if __name__ == '__main__':
    logging.basicConfig(filename=os.environ['CARMUSR'] + '/current_carmtmp/logfiles/generate_a2nx_position.log',
                        format="%(asctime)s: %(filename)s %(levelname)-8s: %(message)s", level=logging.DEBUG)
    run()
    logging.info('*'*70)

