"""
This script will download rotation data from CMS and upload data to the Calibration data base
It is called from bin/calibration/rotation_data.sh

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


def upload_to_calibration_db():
    """
    Upload using carmsys python script directly
    """

    import_master_file = "{data_dir}/master_data_20220625.etab".format(data_dir=DATA_DIRECTORY)
    import_rotations_file = "{data_dir}/rotation_data_20220625.etab".format(data_dir=DATA_DIRECTORY)
    cmd_list = ["carmrunner", os.path.expandvars("$CARMSYS/lib/python/jcms/calibration/data_import.py"),
                "--master_data", import_master_file, "--rotation_data", import_rotations_file]

    p = Popen(cmd_list, stdout=PIPE, stderr=PIPE, shell=False)
    output, err = p.communicate()
    rc = p.returncode

    Errlog.log("Upload finished with return code {r}.".format(r=rc))
    Errlog.log(output)
    Errlog.log(err)


def main():

    Errlog.log("Calibration: Upload rotation data to calibration postgres database")
    upload_to_calibration_db()

main()
