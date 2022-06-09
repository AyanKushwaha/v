"""
Logic for creating ADSF archive from a pre-populated ADSF python-dict.

Re-written to use generators and record-by-record writers instead of keeping
entire datastructure in memory. Useful when exporting year+ long roster database
plans.

Arvid M-A, Jeppesen 2016
"""

import datetime
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED
import shutil
import os.path
import carmusr.concert.log
logger = carmusr.concert.log.get_logger()


class ADSFWriter(object):
    def __init__(self, settings):
        self.settings = settings
        self.chain_count = 0
        self.leg_count = 0

        _basetempdir = os.path.expandvars("$CARMTMP/ADSF/")
        if not os.path.isdir(_basetempdir):
            os.makedirs(_basetempdir)
        self.tempdir = tempfile.mkdtemp(dir=_basetempdir)

        self.md_file = open(tempfile.mktemp(suffix="md", dir=self.tempdir), "w")
        self.cd_file = open(tempfile.mktemp(suffix="cd", dir=self.tempdir), "w")
        self.cd_file.write(CD_HEADER)
        self.__make_custom_md_header()

    def write(self, md, cd_list):
        if len(cd_list) > 0:
            self.write_md_entry(md)
            self.write_cd_entry(cd_list)
            logger.debug("Writing MD/CD entries for chain %s to tempfile." % str(md[0]))
        else:
            logger.warn("Skipping empty chain: %s" % str(md))

    def write_md_entry(self, md):
        self.md_file.write('"%s", %s, "%s", %s, %s, "%s", %s, %d, %s, %s, %s, "%s", "%s", "%s", "%s",\n' % tuple(md))
        self.chain_count += 1

    def write_cd_entry(self, cd_list):
        for cd in cd_list:
            self.leg_count += 1
            self.cd_file.write('"%s", %s, %s, %s, %s, %s, "%s", "%s", "%s", "%s", %d, %d, %d, '
                               '%d, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "%s", %s, %s, %s, '
                               '%s, %s, "%s", "%s",\n' % tuple(cd[:32]))

    def finalize(self):
        # We're done writing to these files.
        self.md_file.close()
        self.cd_file.close()
    
        filebase = self.settings["airline"] + "_" + datetime.date.today().strftime('%Y%m%d') + "_"
    
        filenum = 1
        while True:
            if os.path.isfile(self.settings["adsf_location"] + "/" + filebase + "%04i" % filenum + ".zip"):
                filenum += 1
            else:
                break
    
        filebase = filebase + "%04i" % filenum
    
        md_name = filebase + "_MD_01.adsf"
        cd_name = filebase + "_CD_01.adsf"
        zip_target_name = self.settings["adsf_location"] + "/" + filebase + ".zip"
        zip_tmp_name = tempfile.mktemp(dir=self.tempdir)
    
        zf = ZipFile(zip_tmp_name, "w", compression=ZIP_DEFLATED)
        zf.write(self.md_file.name, arcname=md_name)
        zf.write(self.cd_file.name, arcname=cd_name)
        zf.close()
    
        shutil.copy(zip_tmp_name, zip_target_name)
        shutil.rmtree(self.tempdir)
    
        adsf_archive_size = os.path.getsize(self.settings["adsf_location"] + filebase + ".zip")
    
        return "\n Zipped archive %s is %i kilobytes." % (filebase, int(adsf_archive_size / 1024))

    def __make_custom_md_header(self):
        extra_headers = ""
        if "planning_area" in self.settings.keys():
            extra_headers += "# @PlanningArea %s\n" % self.settings["planning_area"]
        if "scenario_name" in self.settings.keys():
            extra_headers += "# @ScenarioName %s\n" % self.settings["scenario_name"]

        self.md_file.write("""# @StatPeriodStart %s
# @StatPeriodEnd %s
# @PMP %i
# @ForecastTime %s
%s""" % (self.settings["pp_start"], self.settings["pp_end"],
           self.settings["pmp"], self.settings["forecast_time"],
           extra_headers))

        self.md_file.write(MD_HEADER)


MD_HEADER = """15
SChainRef,
IBirthyear,
SGender,
IWeight,
IHeight,
SPosition,
IDiurnalType,
IHabitualSleepLength,
IHomeBaseCommute,
IFTERatio,
IHomeBaseTZ,
SHomeBase,
SAcQual,
SCustomAttribute1,
SCustomAttribute2,

"""

CD_HEADER = """32
SChainRef,
ICount,
ADepartureUTC,
AArrivalUTC,
ADepartureLT,
AArrivalLT,
SDepartureStation,
SArrivalStation,
SFlightNum,
SAcFamily,
IBriefing,
IDebriefing,
IWakeBefore,
IWakeAfter,
ISleepTypeBefore,
INap1Start,
INap1End,
INap1Type,
INap2Start,
INap2End,
INap2Type,
INap3Start,
INap3End,
INap3Type,
SActivityType,
IArrLatitude,
IArrLongitude,
IAcChange,
IFirstInDuty,
IAugmentation,
SCustomAttribute1,
SCustomAttribute2,
"""

