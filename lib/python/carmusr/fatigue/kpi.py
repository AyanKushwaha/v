"""
KPI definitions.

Use get_kpis(bag) to obtain a list of Kpis to include
into your Custom KPI report.

@author: Angelo Stroppa

Corrected by Stefan Hammar in oct 2011.

"""

import math
from carmensystems import kpi
from Localization import MSGR


def mean(sequence):
    """
    Computes the mean value of the sequence given as input
    """
    return sum(sequence) * 1.0 / (len(sequence))


def std_dev(sequence):
    """
    Computes the standard deviation of the sequence given as input
    """
    avg = mean(sequence)
    return math.sqrt(sum(map(lambda x: (x - avg) * (x - avg), sequence)) / (len(sequence)))


def get_fatigue_kpis(trips_bag, rosters_bag=None):
    alertness_results = alertness_kpi(trips_bag, rosters_bag)
    min_alertness = alertness_results['min']
    avg_alertness = alertness_results['avg']
    std_dev_alertness = alertness_results['std_dev']
    best_alert_worst_5_percent = alertness_results['best_5%']
    best_alert_worst_1_percent = alertness_results['best_1%']
    avg_alert_worst_5_percent = alertness_results['avg_5%']
    avg_alert_worst_1_percent = alertness_results['avg_1%']
    afr = alertness_results['afr']
    nfr = alertness_results['nfr']

    kpis = list()

    kpis.append((MSGR("Minimum alertness"), min_alertness))
    kpis.append((MSGR("Average alertness"), avg_alertness))
    kpis.append((MSGR("Standard deviation alertness"), std_dev_alertness))
    kpis.append((MSGR("Absolute Fatigue Risk"), afr))
    kpis.append((MSGR("Normalized Fatigue Risk"), nfr))
    kpis.append((MSGR("Best alertness for worst 5% legs"), best_alert_worst_5_percent))
    kpis.append((MSGR("Average alertness for worst 5% legs"), avg_alert_worst_5_percent))
    kpis.append((MSGR("Best alertness for worst 1% legs"), best_alert_worst_1_percent))
    kpis.append((MSGR("Average alertness for worst 1% legs"), avg_alert_worst_1_percent))

    return kpi.KpiVector("Fatigue Risk Management", kpis, "FRM", "")


def alertness_kpi(trips_bag, rosters_bag):
    '''
    Percent values to use in alertness statistics
    '''
    percent_1 = 0.01   # 1%
    percent_2 = 0.05   # 5%
    NA = '-'

    alertness_index_list = []
    afr_list = []

    for leg_bag in trips_bag.fatigue_mappings.frms_leg_set(where='fatigue.%leg_should_be_checked_for_alertness%\
 and fatigue.%trip_should_be_checked_for_alertness%'):
        alertness_index_list.append(leg_bag.fatigue.alertness_leg_tod_value())
        afr_list.append(leg_bag.fatigue.leg_afr())
    if rosters_bag:
        for leg_bag in rosters_bag.fatigue_mappings.frms_leg_set(where='fatigue.%leg_should_be_checked_for_aler\
tness% and fatigue.%trip_should_be_checked_for_alertness%'):
            alertness_index_list.append(leg_bag.fatigue.alertness_leg_tod_value())
            afr_list.append(leg_bag.fatigue.leg_afr())

    alertness_index_list.sort()
    no_data_legs = len(alertness_index_list)
    if no_data_legs == 0:
        return {'min': NA,
                'avg': NA,
                'std_dev': NA,
                'afr': NA,
                'nfr': NA,
                'best_5%': NA,
                'best_1%': NA,
                'avg_5%': NA,
                'avg_1%': NA}

    min_alertness = min(alertness_index_list)
    avg_alertness = int(mean(alertness_index_list))
    std_dev_alertness = int(std_dev(alertness_index_list))
    afr = sum(afr_list)
    nfr = int(mean(afr_list))
    best_alert_worst_1_percent = alertness_index_list[max(0, int(no_data_legs * percent_1) - 1)]
    avg_alert_worst_1_percent = int(mean(alertness_index_list[0:max(1, int(no_data_legs * percent_1))]))
    best_alert_worst_5_percent = alertness_index_list[max(0, int(no_data_legs * percent_2) - 1)]
    avg_alert_worst_5_percent = int(mean(alertness_index_list[0:max(1, int(no_data_legs * percent_2))]))

    return {'min': min_alertness,
            'avg': avg_alertness,
            'std_dev': std_dev_alertness,
            'afr': afr,
            'nfr': nfr,
            'best_5%': best_alert_worst_5_percent,
            'best_1%': best_alert_worst_1_percent,
            'avg_5%': avg_alert_worst_5_percent,
            'avg_1%': avg_alert_worst_1_percent}
