#!/bin/env python

"""
SKCMS-1794 Adds INSTRUCTOR+LIFUS qualification to crew who already doesn't hold the qualification and are qualified
to hold it. A crew is INSTRUCTOR+LIFUS qualified if they hold any of SFI, SFE, TRI, or TRE qualification.
"""

import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table
from AbsTime import AbsTime

__version__ = '2018-07-04'
START_TIME = AbsTime("1JUN2018")

@fixrunner.once
@fixrunner.run
def fixit(dave_connection, *args, **kwargs):
  # Blacklist of FP instructors not qualified for the LIFUS qualification.
  FP_instructors = ['20376', '22808', '38471', '25250', '23849', '22268', '22593', '85688',
                    '85542', '85685', '17397', '63469', '11072']

  # List of qualifications that is required for a crew to be eligeble for the LIFUS qualification.
  required_qualifications_subtype = ['SFI', 'SFE', 'TRI', 'TRE', 'LIFUS']
  column_names = ['crew', 'acqqual_typ', 'acqqual_subtype', 'qual_subtype', 'validfrom', 'validto', 'lvl', 'si']
  crew_qual_acqual = migrate_table.MigrateTable(dave_connection,
                                                fixrunner,
                                                'crew_qual_acqual',
                                                column_names,
                                                4)
  crew_qual_acqual.load(None)

  to_be_lifus_instructors = get_crew_with_qualifications(crew_qual_acqual,
                                                         required_qualifications_subtype,
                                                         FP_instructors)

  lifus_qualifications = create_lifus_qualification(to_be_lifus_instructors)

  return create_operations(lifus_qualifications)

def get_crew_with_qualifications(crew_qual_acqual, qualifications, blacklist=None):
  """
  Retrieves all crew in 'crew_qual_acqual' that holds at least one of the qualifications
  listed in 'qualifications'.
  :param crew_qual_acqual: MigrateTable.
  :param qualifications: list of qualifications that the crew should hold.
  :param blacklist: optional list of crew IDs that should be excluded from the result.
  :return: a dictionary containing all crew, and a list of their current qualification rows,
  that holds at least one of the required qualifications.
  """
  qualified_crew_rows = list()
  for qualification in qualifications:
    qualified_crew_rows.append(crew_qual_acqual.get_matching_rows({"acqqual_subtype" : qualification}))

  result = dict()
  for qualification_groups in qualified_crew_rows:
    for qualified_crew_row in qualification_groups:
      crew_id = qualified_crew_row['crew']
      if crew_id not in blacklist:
        if crew_id in result:
          result[crew_id].append(qualified_crew_row)
        else:
          result[crew_id] = [qualified_crew_row]
  return result

def has_valid_qualification(qualification_rows, qualification):
  for qualification_row in qualification_rows:
    if str(qualification_row['acqqual_subtype']) == qualification\
      and AbsTime(qualification_row['validto']) > START_TIME:
      return True
  return False

def get_qualification_valid_period(qualification_rows):
  """
  Use existing qualification with the longest valid
  period to determine the 'validfrom' value.
  LIFUS qualification is always 'UFN', i.e. end date
  is 31DEC2035 so 'validto' is hard coded to 31 Dec 2035.
   """
  valid_from = valid_to = None
  for qualification_row in qualification_rows:
    if qualification_row['validto'] > valid_to:
      valid_to = qualification_row['validto']
      valid_from = qualification_row['validfrom']

  return valid_from, int(AbsTime("31DEC2035"))

def get_ac_qual_type(qualification_rows):
  ac_quals = []
  for qualification_row in qualification_rows:
    qual = str(qualification_row['qual_subtype'])
    if AbsTime(qualification_row['validto']) > START_TIME and qual not in ac_quals:
      ac_quals.append(str(qualification_row['qual_subtype']))

  if 'A3' and 'A4' in ac_quals:
    return 'A3A4'
  elif len(ac_quals) > 0:
    return ac_quals[0]
  else:
    return None

def has_any_valid_qualification(qualification_rows):
  for qualification_row in qualification_rows:
    if AbsTime(qualification_row['validto']) > START_TIME:
      return True
  return False

def create_lifus_qualification(lifus_instructors):
  """
  Creates the LIFUS qualification rows needed to create for crew provided in the list 'lifus_instructors'.
  If the crew already holds an 'INSTRUCTOR+LIFUS' qualification, nothing will be changed for that crew.
  :param lifus_instructors: dictionary that should contain every crew that should be qualified to hold,
  or already holds, the LIFUS qualification.
  :return: list containing all LIFUS table operations. Crew who already holds 'INSTRUCTOR+LIFUS' qualification
  will not be changed.
  """
  instructors = list()
  for crew_id, current_qualifications in lifus_instructors.iteritems():
    if has_valid_qualification(current_qualifications, 'LIFUS') or not has_any_valid_qualification(current_qualifications):
      # Ignore crew that already are LIFUS qualified or doesn't hold any other valid qualification.
      continue

    valid_from, valid_to = get_qualification_valid_period(current_qualifications)
    qual = get_ac_qual_type(current_qualifications)

    if qual == 'CJ':
      # Ignore CJ (CityJet) since SAS do not operate CJ any more.
      continue

    assert qual is not None, ("Error creating LIFUS qualification for crew ID " + crew_id + ": 'qual' cannot be None.")

    lifus_qualification = {'crew': crew_id,
                           'qual_typ': 'ACQUAL',
                           'qual_subtype': qual,
                           'acqqual_typ': 'INSTRUCTOR',
                           'acqqual_subtype': 'LIFUS',
                           'validfrom': valid_from,
                           'validto': valid_to,
                           'lvl': None,
                           'si': 'Added in SKCMS-1794'}

    instructors.append(lifus_qualification)

  return instructors

def create_operations(lifus_quals):
  """
  :param lifus_quals:
  :return: list of table operations needed to add new 'INSTRUCTOR+LIFUS' qualification rows
  to table 'crew_qual_acqual'.
  """
  ops = []
  for lifus_qual in lifus_quals:
    ops.append(fixrunner.createOp('crew_qual_acqual', 'N', lifus_qual))

  return ops

fixit.program = 'skcms-1794.py (%s)' % __version__
if __name__ == '__main__':
  fixit()
