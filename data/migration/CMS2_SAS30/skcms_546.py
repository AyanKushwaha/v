import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table
from AbsTime import AbsTime
from RelTime import RelTime

__version__ = '2015_10_09'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    #New trip areas for area_set   
    ops.append(fixrunner.createOp('property_set', 'N', {
            'id': 'oma16_block_time_in_28_days_buffer',
            'si': 'Max block time in 28 days for early warning'
        }))
    ops.append(fixrunner.createOp('property_set', 'N', {
            'id': 'oma16_block_time_in_calendar_year_buffer',
            'si': 'Max block time in calendar year for early warning'
        }))
    ops.append(fixrunner.createOp('property_set', 'N', {
            'id': 'oma16_block_time_in_12_calendar_months_buffer',
            'si': 'Max block time in 12 calendar months for early warning'
        }))
    ops.append(fixrunner.createOp('property_set', 'N', {
            'id': 'oma16_duty_time_in_7_days_buffer',
            'si': 'Max duty time in 7 days for early warning'
        }))
    ops.append(fixrunner.createOp('property_set', 'N', {
            'id': 'oma16_duty_time_in_14_days_buffer',
            'si': 'Max duty time in 14 days for early warning'
        }))
    ops.append(fixrunner.createOp('property_set', 'N', {
            'id': 'oma16_duty_time_in_28_days_buffer',
            'si': 'Max duty time in 28 days for early warning'
        }))
    ops.append(fixrunner.createOp('property_set', 'N', {
            'id': 'oma16_rest_transition_late_early_buffer',
            'si': 'Prevent crew to start/end duty 5:00-6:00'
        }))
    ops.append(fixrunner.createOp('property', 'N', {
            'id': 'oma16_rest_transition_late_early_buffer',
            'validfrom': int(AbsTime('01Sep2015 0:00')),
            'validto': int(AbsTime('31Dec2035 0:00')),
            'value_rel': int(RelTime('0:30')),
            'si': 'Prevent crew to start/end duty 5:00-6:00'
        }))
    ops.append(fixrunner.createOp('property', 'N', {
            'id': 'oma16_block_time_in_28_days_buffer',
            'validfrom': int(AbsTime('01Sep2015 0:00')),
            'validto': int(AbsTime('31Dec2035 0:00')),
            'value_rel': int(RelTime('2:00')),
            'si': 'Max block time in 28 days for early warning'
        }))
    ops.append(fixrunner.createOp('property', 'N', {
            'id': 'oma16_block_time_in_calendar_year_buffer',
            'validfrom': int(AbsTime('01Sep2015 0:00')),
            'validto': int(AbsTime('31Dec2035 0:00')),
            'value_rel': int(RelTime('2:00')),
            'si': 'Max block time in calendar year for early warning'
        }))
    ops.append(fixrunner.createOp('property', 'N', {
            'id': 'oma16_block_time_in_12_calendar_months_buffer',
            'validfrom': int(AbsTime('01Sep2015 0:00')),
            'validto': int(AbsTime('31Dec2035 0:00')),
            'value_rel': int(RelTime('2:00')),
            'si': 'Max block time in 12 calendar months for early warning'
        }))
    ops.append(fixrunner.createOp('property', 'N', {
            'id': 'oma16_duty_time_in_7_days_buffer',
            'validfrom': int(AbsTime('01Sep2015 0:00')),
            'validto': int(AbsTime('31Dec2035 0:00')),
            'value_rel': int(RelTime('2:00')),
            'si': 'Max duty time in 7 days for early warning'
        }))
    ops.append(fixrunner.createOp('property', 'N', {
            'id': 'oma16_duty_time_in_14_days_buffer',
            'validfrom': int(AbsTime('01Sep2015 0:00')),
            'validto': int(AbsTime('31Dec2035 0:00')),
            'value_rel': int(RelTime('2:00')),
            'si': 'Max duty time in 14 days for early warning'
        }))
    ops.append(fixrunner.createOp('property', 'N', {
            'id': 'oma16_duty_time_in_28_days_buffer',
            'validfrom': int(AbsTime('01Sep2015 0:00')),
            'validto': int(AbsTime('31Dec2035 0:00')),
            'value_rel': int(RelTime('2:00')),
            'si': 'Max duty time in 28 days for early warning'
        }))
    print "done"
    return ops


fixit.program = 'skcms_546.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


