from carmensystems.dave import dmf, baselib
import time
import sys
import os
from optparse import OptionParser
from AbsTime import AbsTime
from RelTime import RelTime


def getTrackingFilters(region = None):
    now = time.gmtime()
    now_time = AbsTime(now[0], now[1], now[2], now[3], now[4])
    print "now:", now_time
    
    given_start = now_time.month_floor() - RelTime(6*24*60)
    given_end = now_time.month_ceil() + RelTime(6*24*60)

    print "given_start", given_start
    print "given_end", given_end

    given_start = int(given_start)
    given_end = int(given_end)

    
    one_month_time = 30*1440;
    one_year_time = 366*24*60;

    # Common parameters
    start_time = given_start
    end_time = given_end
    one_month_before_start = start_time - one_month_time
    one_year_before_start = start_time - one_year_time
    two_year_before_start = start_time - 2*one_year_time
    seven_year_before_start = start_time - 7*one_year_time
    # 02Jun2008, won't  change untill after Jun2010
    baseline = 11790720
    three_month_before_start = start_time - 3*one_month_time
    three_month_after_end = end_time + 3*one_month_time
    start = given_start/1440
    end = given_end/1440
   
    res = []
    paramsPeriod = baselib.Result(7)
    paramsPeriod.setDate(0, start)
    paramsPeriod.setDate(1, end)
    paramsPeriod.setAbsTime(2, start_time)
    paramsPeriod.setAbsTime(3, end_time)
    paramsPeriod.setAbsTime(4, one_year_before_start)
    paramsPeriod.setAbsTime(5, three_month_before_start)
    paramsPeriod.setAbsTime(6, three_month_after_end)
    res.append(("period", paramsPeriod))

    paramsCrew = baselib.Result(2)
    paramsCrew.setAbsTime(0, start_time)
    paramsCrew.setAbsTime(1, end_time)
    res.append(("crew_user_filter_active", paramsCrew))

    paramsAccPeriod = baselib.Result(6)
    paramsAccPeriod.setAbsTime(0, start_time)
    paramsAccPeriod.setAbsTime(1, end_time)
    paramsAccPeriod.setAbsTime(2, one_year_before_start)
    paramsAccPeriod.setAbsTime(3, two_year_before_start)
    paramsAccPeriod.setAbsTime(4, seven_year_before_start)
    paramsAccPeriod.setAbsTime(5, one_month_before_start)
    res.append(("accperiod", paramsAccPeriod))


    if region is not None:
        cct_region_1 = "_|SKI"
        cct_region_2 = "_|SKI"
        cct_qual = "AL"

        if region.upper() == 'SKI':
            cct_region_2 = '_|###'
            cct_qual = '####'
        elif region.upper() == 'SKN':
            cct_region_1 = '_|SKN'
        elif region.upper() == 'SKS':
            cct_region_1 = '_|SKS'
        elif region.upper() == 'SKD':
            cct_region_1 = '_|SKD'
        else:
            print "Unkown region, needs to be SKI, SKS, SKD or SKN"
            import sys
            sys.exit()
        
        paramsCrewRegion = baselib.Result(5)
        paramsCrewRegion.setAbsTime(0,start_time)
        paramsCrewRegion.setAbsTime(1,end_time)
        paramsCrewRegion.setString(2,cct_region_1)
        paramsCrewRegion.setString(3,cct_region_2)
        paramsCrewRegion.setString(4,cct_qual)
        res.append(("crew_user_filter_cct", paramsCrewRegion))

    return res

def getTrackingTables():
    model_tables = [
        "flight_leg",
        "crew_flight_duty",
        "ground_task",
        "crew_ground_duty",
        "published_roster",
        "crew_activity",
        "trip",
        "trip_flight_duty",
        "trip_ground_duty",
        "trip_activity",
        "accumulator_int_run",
        "account_entry",
        "alert_time_exception",
        "bases",
        "bought_days",
        "ci_frozen",
        "cio_event",
        "cio_status",
        "country",
        "country_req_docs",
        "course_type",
        "crew_address",
        "crew_activity_attr",
        "crew_annotations",
        "crew_attr",
        "crew_base_break",
        "crew_contact",
        "crew_contract",
        "crew_contract_valid",
        "crew_document",
        "crew_employment",
        "crew_ext_publication",
        "crew_flight_duty_attr",
        "crew_ground_duty_attr",
        "crew_log_acc_mod",
        "crew_need_exception",
        "crew_not_fly_with",
        "crew_notification",
        "crew_publish_info",
        "crew_qual_acqual",
        "crew_qualification",
        "crew_rehearsal_rec",
        "crew_rest",
        "crew_restr_acqual",
        "crew_restriction",
        "crew_seniority",
        "crew_training_log",
        "crew_training_need",
        "crew_training_t_set",
        "do_not_publish",
        "flight_leg_attr",
        "handover_message",
        "hotel_booking",
        "informed",
        "mcl",
        "notification_message",
        "passive_booking",
        "paxlst_log",
        "published_standbys",
        "rule_exception",
        "sas_40_1_cbr",
        "spec_local_trans",
        "special_schedules",
        "transport_booking"
    ]
    rave_tables = [
        "ac_employer_set",
        "accumulator_rel",
        "accumulator_int",
        "accumulator_time",
        "crew_landing",
        "ground_task_attr",
        "crew_user_filter",
        "crew_extra_info",
        "account_baseline",
        "activity_group_period",
        "activity_set_period",
        "additional_rest",
        "agreement_validity",
        "apt_restrictions",
        "apt_restrictions_course",
        "apt_requirements",
        "cabin_recurrent",
        "cabin_training",
        "ci_exception",
        "coterminals",
        "crew_complement",
        "crew_leased",
        "crew_need_jarops",
        "crew_need_service",
        "crew_passport",
        "crew_recurrent_set",
        "crew_rest",
        "meal_flight_owner",
        "freeday_requirement",
        "hotel_contract",
        "hotel_transport",
        "lh_apt_exceptions",
        "meal_customer",
        "meal_airport",
        "minimum_connect",
        "minimum_connect_pass",
        "pc_opc_composition",
        "preferred_hotel_exc",
        "preferred_hotel",
        "simulator_briefings",
        "simulator_set",
        "spec_weekends",
        "pattern_acts",
        "pc_opc_composition",
        "pgt_need",
        "rave_string_paramset",
        "rest_on_board_cc",
        "rest_on_board_fc",
        "simulator_composition"
        ]

    return model_tables + rave_tables




class DBTransferTest(object):
    def __init__(self, url, schema):
        self._url = url
        self._schema = schema
        self.econn = None

    def connect(self, url = None, schema = None):
        if url is not None:
            self._url = url
        if schema is not None:
            self._schema = schema
            
        self.econn = dmf.EntityConnection()
        self.econn.open(self._url, self._schema)
        
    def disconnect(self):
        self.econn.close()
        self.econn = None

    def run(self, tables, rows_to_download, num_tests, test_sizes, filters = []):
        results = {}
        
        print "This test will select up to %d rows from each of the following tables: %s" % (rows_to_download,", ".join(tables))
        # Begin with warning up the cache
        print "Transfering data..."
        output_string = "Done with run %s using size %s. Transfer time %.2fs (Total: %.2fs, CPU: %.2fs, Select: %.2fs) (Transferred %s rows)"
        for size in test_sizes:
            # os.environ['DAVE_FETCH_SIZE'] = str(size)
            self.econn.setFetchSize(size)
            for i in range(num_tests):
                count, total_time, select_time, cpu_time = self._do_multi_selects(tables, rows_to_download, filters)
                try:
                    results[size].append((count, total_time, select_time, cpu_time))
                except KeyError:
                    results[size] = [(count, total_time, select_time, cpu_time)]
                print output_string % (i+1,
                                       self.econn.getFetchSize(),
                                       total_time-cpu_time-select_time,
                                       total_time,
                                       cpu_time,
                                       select_time,
                                       count)
                
        spec_res = {}
        print "Time is reported as seconds per 1000 rows. Only network time is reported for AVG, MAX, MIN, TRF%."
        print "TOT% includes CPU and selection time(SEL). SEL% is percentage of total. TRF% is transfer time compared to size=100, as percentage"
        print "%s runs were done using each test size" % (num_tests)
        print "SIZE\t\tAVG\t\tMAX\t\tMIN\t\tTRF%\t\tTOT%\t\tSEL\t\tSEL%"
        for size in test_sizes:
            min = 999999
            max = 0
            count = 0
            average = 0
            total_average = 0
            select_average = 0

            for (count, total_time, select_time, cpu_time) in results[size]:
                normalized_transfer_time = (total_time-cpu_time-select_time) / (count/1000.0)
                if normalized_transfer_time > max:
                    max = normalized_transfer_time
                if normalized_transfer_time < min:
                    min = normalized_transfer_time
                average += normalized_transfer_time
                total_average += total_time / (count/1000.0)
                select_average += select_time
            average = average/len(results[size])
            total_average = total_average/len(results[size])
            select_average = select_average/len(results[size])
            spec_res[size] = (size, average, max, min, total_average, select_average, total_time)

        for size in test_sizes:
            (_, transfer_average, max, min, total_average, select_time, total_time) = spec_res[size]
            (_, ref_transfer_average, _, _, ref_total_average, _, _) = spec_res[100]
            print "%s\t\t%.5fs\t%.5fs\t%.5fs\t%.1f%%\t\t%.1f%%\t\t%.2fs\t\t%.1f%%" % (size, transfer_average, max, min,
                                                                                      (transfer_average/ref_transfer_average)*100,
                                                                                      (total_average/ref_total_average)*100,
                                                                                      select_time,
                                                                                      (select_time/total_time)*100)

    def _do_multi_selects(self, tables, max_rows, filters):
        t_count = 0
        t_total_time = 0
        t_select_time = 0
        t_cpu_time = 0

        self.econn.beginReadTxn()
        if len(filters) > 0:
            for (filter_name, filter_def) in filters:
                self.econn.addSelectFilterWithParams(filter_name, filter_def)
                
        # set filters here
        for table in tables:
            count, total_time, select_time, cpu_time = self._do_select(table, max_rows)
            t_count += count
            t_total_time += total_time
            t_select_time += select_time
            t_cpu_time += cpu_time
        self.econn.endReadTxn()
        return t_count, t_total_time, t_select_time, t_cpu_time
            

    def _do_select(self, table, max_rows):
        '''
        return amount of read rows, transfer time for all rows, time it took for select
        '''
        count = 0
        start_time = time.time()
        self.econn.select(table)
        select_time = time.time() - start_time
        start_clock = time.clock()
        
        row = self.econn.readRecord()
        while (row is not None):
            count +=1
            if count >= max_rows:
                break
            row = self.econn.readRecord()

        cpu_time = time.clock() - start_clock
        total_time = (time.time() - start_time)
        return count, total_time, select_time, cpu_time
            

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-c', '--connect', 
            dest="connect", 
            help="Database connect string.")
    parser.add_option('-s', '--schema', 
            dest="schema", 
            help="Database schema string.")
    parser.add_option('-t', '--tables',
                      dest='tables',
                      default="flight_leg,crew_flight_duty,accumulator_rel",
                      help="Comma separated list of tables to measure on, eg: -t 'crew_flight_duty,flight_leg'")
    parser.add_option('-m', '--size',
                      dest='size',
                      default="1000000",
                      help="max transfer size per table, default is 1000000 rows")
    parser.add_option('-n', '--num_runs',
                      dest='num_runs',
                      default='4',
                      help="Number of runs for each size")
    parser.add_option('-b', '--batchsizes',
                      dest='test_sizes',
                      default='50,100,200,500,1000',
                      help="Comma separated list of batch sizes to test, eg -b '50,100,200,500,1000'. 100 will always be tested as a default value")
    parser.add_option('-a', '--application',
                      dest='application',
                      default='',
                      help='emulate load of application, valid values: tracking')
    parser.add_option('-r', '--region',
                      dest='region',
                      default='',
                      help="Region to emulate for application given to --application, default is all regions available for that application")
    
    opts, args = parser.parse_args(list(sys.argv[1:]))

    if opts.schema is None:
        parser.error("Must supply option 'schema'.")
    if opts.connect is None:
        parser.error("Must supply option 'connect'.")

    size_default = 10000000
    size = size_default
    try:
        size = int(opts.size)
    except:
        print "Unknown format of size, must be an integer, will use default"

    num_runs = 4
    try:
        num_runs = int(opts.num_runs)
    except:
        print "Unknown format of number of runs, must be an integer, will use default"

    test_sizes = opts.test_sizes.split(",")
    try:
        test_sizes = [int(i) for i in test_sizes]
    except:
        print "Unkown format in test_sizes list, will use default"
        test_sizes = [50, 100, 200, 500, 1000]

    if 100 not in test_sizes:
        test_sizes.append(100)
    test_sizes.sort()

    tables = opts.tables.split(",")
    tables = [t.strip() for t in tables]

    filters = []
    if opts.application.upper() == 'TRACKING' or opts.application.upper() == 'CCT':
        tables = getTrackingTables()
        if opts.region is not None and opts.region != "":
            filters = getTrackingFilters(opts.region)
        else:
            filters = getTrackingFilters()
        tables.sort()
        if size == size_default:
            size = 9999999
        

    print "connect = %s, schema = %s" % (opts.connect, opts.schema)

    # unset variable, as we will use the API
    # must be done before we create the connection
    if os.environ.has_key('DAVE_FETCH_SIZE'):
        del os.environ['DAVE_FETCH_SIZE']

    transfer_checker = DBTransferTest(opts.connect, opts.schema)
    transfer_checker.connect()
    transfer_checker.run(tables, size, num_runs, test_sizes, filters)
    transfer_checker.disconnect()

    

