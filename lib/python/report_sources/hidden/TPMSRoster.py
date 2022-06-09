from report_sources.include.SASReport import SASReport
import carmensystems.rave.api as r
import os, stat
import glob
from datetime import datetime
import csv
import shutil

"""
  Writes the data to the CSV file
"""
EVENT_NOTIFIED_AT_STR = '2016-01-01 00:00:00'


def nn(v):
    "never returns None"
    return "" if v == None else v


def nns(v):
    "always returns a str or unicode"
    if v == None:
        return ""
    if type(v) in [str, unicode]:
        return v
    return str(v)


def write_data(fieldnames, rows, crew_roster_file):
    if len(rows) != 0 and len(fieldnames) == len(rows[0]):
        data = []
        for row in rows:
            data.append(dict(zip(fieldnames, row)))
        writer = csv.DictWriter(crew_roster_file, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_ALL)

        for row_dict in data:
            writer.writerow(dict([(k, nns(v).encode("utf-8")) for k, v in row_dict.items()]))
        return True
    else:
        print
        "Data and header not equal"
        return False


"""
  Converts a Rave abstime string on format DDMONYYY HH24:MI to YYYY-MM-DD
"""


def cvt_dstr_to_YYYY_MM_DD(date_str):
    return datetime.strptime(date_str, "%d%b%Y %H:%S").strftime('%Y-%m-%d')


"""
  Converts a Rave abstime string on format DDMONYYY HH24:MI to YYYY-MM-DD HH24:MI
"""


def cvt_dstr_to_YYYY_MM_DD_HH24_MI(date_str):
    return datetime.strptime(date_str, "%d%b%Y %H:%M").strftime('%Y-%m-%d %H:%M:%S')


class TPMSExport(SASReport):
    def create(self):
        csvRows = []

        period_start = datetime.now().date()

        # Add rows
        rosters_bag = r.context('sp_crew').bag()

        # Define field names
        ac_reg_key = 'CIRO_AC_REG'
        arrival_airport_key = 'CIRO_ARRIVAL_AIRPORT'
        carrier_code_key = 'CIRO_CARRIER_CODE'
        departure_airport_key = 'CIRO_DEPARTURE_AIRPORT'
        emp_number_first_key = 'CIRO_EMP_NUMBER_FIRST'
        event_ac_type_code_key = 'CIRO_EVENT_AC_TYPE_CODE'
        event_ack_at_key = 'CIRO_EVENT_ACK_AT'
        event_airline_key = 'CIRO_EVENT_AIRLINE'
        event_duty_code_key = 'CIRO_EVENT_DUTY_CODE'
        event_end_hkg_key = 'CIRO_EVENT_END_HKG'
        event_end_loc_key = 'CIRO_EVENT_END_LOC'
        event_end_utc_key = 'CIRO_EVENT_END_UTC'
        event_id_key = 'CIRO_EVENT_ID'
        event_not_at_key = 'CIRO_EVENT_NOT_AT'
        event_rank_key = 'CIRO_EVENT_RANK'
        event_start_hkg_key = 'CIRO_EVENT_START_HKG'
        event_start_loc_key = 'CIRO_EVENT_START_LOC'
        event_start_utc_key = 'CIRO_EVENT_START_UTC'
        event_training_code_key = 'CIRO_EVENT_TRAINING_CODE'
        event_type_key = 'CIRO_EVENT_TYPE'
        flight_date_key = 'CIRO_FLIGHT_DATE'
        flight_no_key = 'CIRO_FLIGHT_NO'
        sim_name_key = 'CIRO_SIM_NAME'
        job_id = 'CIRO_JOB_ID'
        qual_to_update = 'CIRO_QUAL_TO_BE_UPDATED'

        # fieldnames = [  ac_reg_key,
        #                arrival_airport_key,
        #                carrier_code_key,
        #                departure_airport_key,
        #                emp_number_first_key,
        #                event_ac_type_code_key,
        #                event_ack_at_key,
        #                event_airline_key,
        #                event_duty_code_key,
        #                event_end_hkg_key,
        #                event_end_loc_key,
        #                event_end_utc_key,
        #                event_id_key,
        #                event_not_at_key,
        #                event_rank_key,
        #                event_start_hkg_key,
        #                event_start_loc_key,
        #                event_start_utc_key,
        #                event_training_code_key,
        #                event_type_key,
        #                flight_date_key,
        #                flight_no_key,
        #                sim_name_key,
        #                job_id,
        #                qual_to_update,]

        fieldnames = [event_start_utc_key,
                      event_end_utc_key,

                      event_start_loc_key,
                      event_end_loc_key,

                      event_start_hkg_key,
                      event_end_hkg_key,

                      event_type_key,
                      event_duty_code_key,
                      qual_to_update,
                      sim_name_key,

                      event_id_key,
                      event_ac_type_code_key,

                      event_rank_key,
                      event_training_code_key,

                      emp_number_first_key,

                      flight_date_key,
                      flight_no_key,
                      departure_airport_key,
                      arrival_airport_key,
                      ac_reg_key,
                      carrier_code_key,
                      event_airline_key,

                      event_not_at_key,
                      event_ack_at_key,

                      job_id, ]  # PY 2020-09-17: Reorder and regroup the variables.

        time_line = ''

        hdr = ''
        for field in fieldnames:
            hdr = hdr + '"' + field + '";'
        # Remove last ;
        hdr = hdr[0:len(hdr) - 1]
        print
        for leg_bag in rosters_bag.iterators.leg_set(sort_by=("leg.%start_utc%"), where=("report_tpms.%leg_selected%")):
            if time_line == '':
                time_line = "###Range###" + cvt_dstr_to_YYYY_MM_DD_HH24_MI(
                    str(leg_bag.report_tpms.tpms_roster_period_start())) + "##" + \
                            cvt_dstr_to_YYYY_MM_DD_HH24_MI(str(leg_bag.report_tpms.tpms_roster_period_end())) + "###"

            # Event ID
            event_id = str(leg_bag.report_tpms.leg_id()).strip()

            # If event_id contains either of the two instructor codes ('OLOCRC' for CC, 'OXOCR'C for FD) remap it so that it matches trainees event_id (OCRC).
            if event_id[4:10] == 'OLOCRC' or event_id[4:10] == 'OXOCRC':
                event_id = event_id[0: 4:] + event_id[6::]

            # If event_id contains either of the two instructor codes ('OLCRMC' for CC, 'OXCRMC' for FD) remap it so that it matches trainees event_id (CRMC).
            if event_id[4:10] == 'OLCRMC' or event_id[4:10] == 'OXCRMC':
                event_id = event_id[0: 4:] + event_id[6::]

            event_type = leg_bag.report_tpms.leg_training_type();
            if event_id == "":
                event_id = "DUMMY"

            # First emp. nr.
            emp_number_first = leg_bag.report_tpms.leg_crew_id()

            # Event rank
            event_rank = str(leg_bag.report_tpms.leg_titlerank())

            # *TODO: Event duty code and event_training_code need to  have good values. A discussion with prodefis is needed.

            # Event training code 1
            event_duty_code = leg_bag.report_tpms.leg_type()

            # This shows if instructor TR och Trainee TL
            event_training_code = leg_bag.report_tpms.event_training_code()

            # Event airline
            carrier_code = leg_bag.report_tpms.leg_flight_carrier()

            # *TODO: We do not have a good value for simulator name. leg.code is deliverired. Prodefis need this info in order to show where crew shall go when he/she has his/hers simulator pass.
            # Simulator name
            sim_name = leg_bag.report_tpms.leg_sim_name()

            # Flight no
            flight_no = leg_bag.report_tpms.leg_flight_no()

            # AC registration
            ac_reg = leg_bag.report_tpms.leg_ac_reg()

            # Event AC type
            event_ac_type_code = leg_bag.report_tpms.leg_ac_family()

            # Qualification to update
            if event_duty_code != "CRM":
                # Handling of the case when instructor is supervisor, but we don't want leg_bag.report_tpms.qual_to_update() in column qual_to_update
                if leg_bag.crew_pos.assigned_function() == "FU" and event_duty_code == "OXCRM":
                    qual_to_update = ""
                else:
                    qual_to_update = leg_bag.report_tpms.qual_to_update()
            else:
                qual_to_update = sim_name

            if event_ac_type_code == "---":
                event_ac_type_code = ''

            if leg_bag.leg.is_flight_duty():
                departure_airport = leg_bag.leg.start_station()  # Departure airport
                arrival_airport = leg_bag.leg.end_station()  # Arrival airport
                flight_date = cvt_dstr_to_YYYY_MM_DD(str(leg_bag.leg.leg_start_utc()))  # Flight date
            else:
                departure_airport = leg_bag.leg.start_station()  # Departure airport
                arrival_airport = ""  # Arrival airport
                flight_date = ""  # Flight date

            # Event start UTC
            event_start_utc = cvt_dstr_to_YYYY_MM_DD_HH24_MI(str(leg_bag.leg.start_utc()))

            # Event end UTC
            event_end_utc = cvt_dstr_to_YYYY_MM_DD_HH24_MI(str(leg_bag.leg.end_utc()))

            # Event start local
            event_start_loc = cvt_dstr_to_YYYY_MM_DD_HH24_MI(str(leg_bag.leg.start_lt()))

            # Event end local
            event_end_loc = cvt_dstr_to_YYYY_MM_DD_HH24_MI(str(leg_bag.leg.end_lt()))

            # Event start Home Base
            event_start_hkg = cvt_dstr_to_YYYY_MM_DD_HH24_MI(str(leg_bag.leg.start_hb()))

            # Event end Home Base
            event_end_hkg = cvt_dstr_to_YYYY_MM_DD_HH24_MI(str(leg_bag.leg.end_hb()))

            event_not_at = EVENT_NOTIFIED_AT_STR

            # Event acknowledged at
            event_ack_at = ""
            ac_owner = leg_bag.report_tpms.leg_ac_owner()
            if ac_owner == 'SVS':
                event_airline = 'LK'
            else:
                event_airline = 'SK'

            # row=[   ac_reg,
            #        arrival_airport,
            #        carrier_code,
            #        departure_airport,
            #        emp_number_first,
            #        event_ac_type_code,
            #        event_ack_at,
            #        event_airline,
            #        event_duty_code,
            #        event_end_hkg,
            #        event_end_loc,
            #        event_end_utc,
            #        event_id,
            #        event_not_at,
            #        event_rank,
            #        event_start_hkg,
            #        event_start_loc,
            #        event_start_utc,
            #        event_training_code,
            #        event_type,
            #        flight_date,
            #        flight_no,
            #        sim_name,
            #        "",
            #        qual_to_update, ]

            row = [event_start_utc,
                event_end_utc,

                event_start_loc,
                event_end_loc,

                event_start_hkg,
                event_end_hkg,

                event_type,
                event_duty_code,
                qual_to_update,
                sim_name,

                event_id,

                event_ac_type_code,

                event_rank,
                event_training_code,

                emp_number_first,

                flight_date,
                flight_no,
                departure_airport,
                arrival_airport,
                ac_reg,
                carrier_code,
                event_airline,

                event_not_at,
                event_ack_at,
                "", ]  # PY 2020-09-17: Reorder and regroup the variables to make it easier to read and work with in TPMS.

            # Event id equals empty string is personal activity that shall not be inserted
            if not event_duty_code.startswith("-"):
                csvRows.append(row)
            
        dir_path = os.getenv('CARMDATA')

        archivePath = dir_path + "/REPORTS/TPMS_ARCHIVE/"
        mypath = dir_path + "/REPORTS/TPMS_EXPORT/"

        if not os.path.exists(mypath):
            os.makedirs(mypath)
        if not os.path.exists(archivePath):
            os.makedirs(archivePath)

        tmp_str = str(datetime.now())
        date_str = tmp_str.replace(" ", "_")
        date_str = date_str.replace(":", "")
        date_str = date_str[:-9]

        reportName = "TPMS_Roster_" + date_str
        myFile = mypath + reportName + '.csv'

        # Write to file
        with open(myFile, 'wb') as roster_export_file:
            roster_export_file.write(time_line + "\n")
            roster_export_file.write('###CpaInterfaceRoster###\n')
            roster_export_file.write(hdr + "\n")
            write_data(fieldnames, csvRows, roster_export_file)

        os.chmod(myFile, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        shutil.copyfile(myFile, archivePath + reportName + '.csv')

    def check_dup(self):
        print
        "Check dup starting"
        rosters_bag = r.context('sp_crew').bag()
        events = {}
        for leg_bag in rosters_bag.iterators.leg_set(sort_by=("leg.%start_utc%"),
                                                     where=("report_tpms.%is_instructor%")):
            k = leg_bag.report_tpms.leg_id()
            if k in events:
                items = events[k]
            else:
                items = []
                events[k] = items
            items.append((leg_bag.leg.start_utc(), leg_bag.crew.id(), leg_bag.leg.code()))
        print
        "Check dup found", len(events.keys())

        for k in events.keys():
            print
            len(events[k]), k, events[k][0][0]
            for items in events[k]:
                print
                "    ", items
        print
        "Check dup done"


def main():
    export = TPMSExport()
    # export.check_dup()
    export.create()

# main()
