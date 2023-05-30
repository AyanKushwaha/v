
"""
This script will download rotation data from CMS and upload data to the Calibration data base
It is called from bin/calibration/rotation_data.sh

Usage:
    bin/startMirador.sh --script -s carmusr.calibration.util.data_transfer_from_cms --pmp <PMP> --hours_to_op <HOURS>


"""
__author__ = ", Jeppesen"

import sys
import os
import commands
import Crs
from tm import TM
from AbsTime import AbsTime
from AbsDate import AbsDate
from RelTime import RelTime
import carmensystems.mave.etab as etab
import utils.dt
import datetime
import Errlog
import argparse
from subprocess import Popen, PIPE

DATA_DIRECTORY = "MasterRotationData"


class MasterRotationData(object):
    def __init__(self, schema, dburl, save=False):
        self._schema = str(schema)
        self._dburl = str(dburl)
        self._save = save

    def connect(self):
        """
        Creates and opens connection to a DAVE database
        """
        sys.stdout.write("Connecting to url = %s, schema = %s ..." % (self._dburl, self._schema))
        TM.connect(self._dburl, self._schema, '')
        TM.loadSchema()
        sys.stdout.write(" ...Connected!\n")

    def __del__(self):
        """
        Closes down connections to the DAVE database
        """
        sys.stdout.write("Closing down database connection ...")
        TM.disconnect()
        sys.stdout.write(" Done!\n")

    def get_rotation_flight_leg(self, leg, tail_id):
        ac_flight_leg = dict()

        ac_flight_leg["chain_ref"] = tail_id

        ac_flight_leg["count"] = 1
        ac_flight_leg["activity_code"] = ""

        ac_flight_leg["departure_utc"] = leg.sobt  # scheduled off-block
        ac_flight_leg["arrival_utc"] = leg.sibt    # scheduled in-block

        ac_flight_leg["departure_airport_name"] = leg.adep.id
        ac_flight_leg["arrival_airport_name"] = leg.ades.id

        ac_flight_leg["departure_terminal"] = ""
        ac_flight_leg["arrival_terminal"] = ""

        ac_flight_leg["flight_carrier"] = leg.fd[0:3].strip()
        ac_flight_leg["flight_number"] = int(leg.fd[3:10].strip("MNGH"))
        ac_flight_leg["flight_suffix"] = "*" if leg.fd <= 9 else leg.fd[9:10]

        ac_flight_leg["leg_number"] = leg.seq if leg.seq else 1

        ac_flight_leg["service_type"] = leg.stc
        ac_flight_leg["aircraft_owner"] = leg.aco
        ac_flight_leg["cabin_crew_employer"] = leg.cae
        ac_flight_leg["cockpit_crew_employer"] = leg.cpe

        # Optional data, currently not available in CMS:
        # ------------------------------------
        # number_of_first_class_seats, number_of_business_class_seats, number_of_economy_class_seats
        # number_of_fourth_class_seats, delay_code1, delay_duration1, delay_code2, delay_duration2
        # cancel_code, custom_field1, custom_field2

        return ac_flight_leg

    def get_rotation_data(self, extract_day_udor):

        TM(["aircraft_flight_duty", "rotation_flight_duty"])

        master_data_dict = dict()
        rotation_leg_list = []

        extract_day = AbsTime(extract_day_udor * 1440)

        Errlog.log("get_rotation_data -- Extracting data for {ed}".format(ed=extract_day))

        extract_period_start = extract_day - RelTime("24:00")
        extract_period_end = extract_day + RelTime("24:00")

        ac_rot_legs_set = set()

        # 1. Add legs from aircraft rotations (with assigned aircraft)
        for ac_leg in TM.aircraft_flight_duty.search("(&(leg.udor>=%s)(leg.udor<=%s))" % (extract_period_start, extract_period_end)):

            tail_id = ac_leg.ac.id
            if tail_id in master_data_dict:
                if master_data_dict[tail_id]["ac_type"] != ac_leg.ac.actype.id:
                    Errlog.log("ERROR")
                    raise ValueError("Tail ID mismatch in aircraft rotation")
            else:
                master_rot = {"ac_type": ac_leg.ac.actype.id, "persistent": True}
                master_data_dict[tail_id] = master_rot

            try:
                ac_flight_leg = self.get_rotation_flight_leg(ac_leg.leg, tail_id)
                rotation_leg_list.append(ac_flight_leg)

                leg_key = (ac_leg.leg.udor, ac_leg.leg.fd, ac_leg.leg.adep.id)
                ac_rot_legs_set.add(leg_key)

            except:
                Errlog.log("Warning: leg not found for {}".format(tail_id))
        tail_assigned_leg_count = len(rotation_leg_list)

        # 2. Add legs from anonymous rotations (no assigned aircraft)
        anon_rot_leg_count = 0
        uuid_dict = {}
        id_count = 0
        for rot_leg in TM.rotation_flight_duty.search("(&(leg.udor>=%s)(leg.udor<=%s))" % (extract_period_start, extract_period_end)):
            anon_rot_leg_count += 1
            try:
                uuid = rot_leg.rot.id
            except:
                Errlog.log("Warning: rotation not found for anonymous rotation leg.")
                uuid = anon_rot_leg_count

            if not uuid in uuid_dict:
                id_count += 1
                uuid_dict[uuid] = id_count
            rot_id = "ar_{}".format(uuid_dict[uuid])

            try:
                master_rot = {"ac_type": rot_leg.leg.actype.id, "persistent": False}
                master_data_dict[rot_id] = master_rot
                flight_leg = self.get_rotation_flight_leg(rot_leg.leg, rot_id)
                rotation_leg_list.append(flight_leg)
                leg_key = (rot_leg.leg.udor, rot_leg.leg.fd, rot_leg.leg.adep.id)
                ac_rot_legs_set.add(leg_key)
            except:
                Errlog.log("Warning: leg not found for anonymous rotation.")
        print(" Print Aircraft roatation set {0} ".format(ac_rot_legs_set))
        # 3. Add single leg rotations without assigned aircraft
        single_leg_count = 0
        for fl in TM.flight_leg.search("(&(udor>=%s)(udor<=%s)(!(statcode.id=C)))" % (extract_period_start, extract_period_end)):
            print ("Print the fl {0}".format(fl))
            print ("Print the fl.udor {0}".format(fl.udor))
            print ("Print the fl.fd {0}".format(fl.fd))
            print ("Print the fl.adep.id {0}".format(fl.adep.id))            
            if not (fl.udor, fl.fd, fl.adep.id) in ac_rot_legs_set:
                single_leg_count += 1
                rot_id = "cr_{}".format(single_leg_count)
                if fl.actype is None:
                    fl_id =  '' 
                else:
                    fl_id= fl.actype.id
                master_rot = {"ac_type": fl_id, "persistent": False}
                master_data_dict[rot_id] = master_rot

                flight_leg = self.get_rotation_flight_leg(fl, rot_id)
                rotation_leg_list.append(flight_leg)

        Errlog.log("Rotation legs with assigned_tail: {}".format(tail_assigned_leg_count))
        Errlog.log("Rotation legs without assigned_tail: {}".format(anon_rot_leg_count))
        Errlog.log("Single leg rotations: {}".format(single_leg_count))

        return master_data_dict, rotation_leg_list

    def export_data(self, extract_day_udor):
        Errlog.log("Loading tables")
        Errlog.log("Destination directory: {d}".format(d=destination_directory()))
        self.master_data, self.rotation_data = self.get_rotation_data(extract_day_udor)


def destination_directory():
    """
    Returns path to destination directory
    """

    data_source_dir = Crs.CrsGetModuleResource("calibration", Crs.CrsSearchModuleDef, "dataSourceDir")
    return os.path.join(data_source_dir, DATA_DIRECTORY)


def create_md_etab(master_data_dict, extract_day_udor, pmp=350):
    """
    Create master data etable
    """

    db_data_dir = destination_directory()

    file_suffix = AbsDate(extract_day_udor * 1440).yyyymmdd()
    md_file_name = "master_data_{date}.etab".format(date=file_suffix)
    md_file_path = os.path.join(db_data_dir, md_file_name)

    Errlog.log("Creating file: {md}".format(md=md_file_path))

    session = etab.Session()

    etab_comments = ("",
                     "@pmp {p}".format(p=pmp),
                     "@valid_period_start {period_start} 02:00".format(period_start=AbsDate(extract_day_udor * 1440)),
                     "@valid_period_end {period_end} 02:00".format(period_end=AbsDate((extract_day_udor + 1) * 1440)),
                     "")

    md_etab = etab.create(session, md_file_path, "\n".join(etab_comments))

    md_etab.appendColumn('chain_ref', str, help="Tail ID")
    md_etab.appendColumn('aircraft_type', str)
    md_etab.appendColumn('persistent', bool, help="If true, the chain_ref is a persistent identity (tail ID)")

    for key in master_data_dict.keys():
        md_etab.append((key, master_data_dict[key]["ac_type"], master_data_dict[key]["persistent"]))

    md_etab.sort(("chain_ref",))
    md_etab.save()


def create_rd_etab(rotation_data_list, extract_day_udor):
    """
    Create rotation data etable
    """

    db_data_dir = destination_directory()

    file_suffix = AbsDate(extract_day_udor * 1440).yyyymmdd()
    rd_file_name = "rotation_data_{date}.etab".format(date=file_suffix)
    rd_file_path = os.path.join(db_data_dir, rd_file_name)

    Errlog.log("Creating file: {rd}".format(rd=rd_file_path))

    session = etab.Session()
    etab_comments = ("")

    rd_etab = etab.create(session, rd_file_path, "\n".join(etab_comments))

    rd_etab.appendColumn("chain_ref", str, help="Ref to MD file")
    rd_etab.appendColumn("count", int)
    rd_etab.appendColumn("activity_code", str)
    rd_etab.appendColumn("departure_utc", AbsTime)
    rd_etab.appendColumn("arrival_utc", AbsTime)
    rd_etab.appendColumn("departure_airport_name", str)
    rd_etab.appendColumn("arrival_airport_name", str)
    rd_etab.appendColumn("departure_terminal", str)
    rd_etab.appendColumn("arrival_terminal", str)
    rd_etab.appendColumn("flight_carrier", str)
    rd_etab.appendColumn("flight_number", int)
    rd_etab.appendColumn("flight_suffix", str)
    rd_etab.appendColumn("leg_number", int)
    rd_etab.appendColumn("service_type", str)
    rd_etab.appendColumn("aircraft_owner", str)
    rd_etab.appendColumn("cabin_crew_employer", str)
    rd_etab.appendColumn("cockpit_crew_employer", str)

    for rotation_leg in rotation_data_list:
        rd_etab.append(rotation_leg)

    rd_etab.sort(("chain_ref", "departure_utc",))

    rd_etab.save()


def usage():
    print __doc__


def check_or_create_data_directory():
    data_dir = destination_directory()
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, 0775)  # mode "drwxrwsr-x"


def download_from_cms(schema, db_url, extract_day_udor, pmp=350):
    dbObj = MasterRotationData(schema, db_url)
    dbObj.connect()
    dbObj.export_data(extract_day_udor)
    check_or_create_data_directory()
    create_md_etab(dbObj.master_data, extract_day_udor, pmp)
    create_rd_etab(dbObj.rotation_data, extract_day_udor)


def main(args):

    parser = argparse.ArgumentParser()
    parser.add_argument('--pmp', help='Process measuring point')
    parser.add_argument('--hours_to_op', help='Hours to day of operation')
    options = parser.parse_args(args)

    hours_to_op = int(options.hours_to_op)
    pmp = options.pmp

    db_url = os.environ["DB_URL"]
    schema = os.environ["SCHEMA"]

    now = utils.dt.dt2m(datetime.datetime.now() -  datetime.timedelta(days=59))  # UTC time

    extract_day_udor = (now + hours_to_op * 60) / 1440

    Errlog.log("Extracting data for {ed}".format(ed=AbsDate(extract_day_udor * 1440)))

    Errlog.log("Calibration: Download rotation data from CMS")
    download_from_cms(schema, db_url, extract_day_udor, pmp)

main(sys.argv[1:])
