"""
Interface 44.3 Overtime and Allowances
"""

import os

import carmensystems.rave.api as rave
import salary.api as api
import salary.conf as conf
import salary.run as run

from tempfile import mkstemp
from salary.Overtime import OvertimeManager
from tm import TM
from utils.fmt import NVL


class TempCrewRun(run.GenericRun):
    def run(self):
        """Overriding Base class in order to be able to create
        a OvertimeStatement at the same time as the run."""
        runid = run.GenericRun.run(self)
        if self.rundata.admcode == 'R':
            fd, retro_fn = mkstemp(dir=os.environ['CARMTMP'], suffix='.tmp')
            tmpfile = os.fdopen(fd, "w")
            for crewid in set([d.crewid for d in self.data]):
                print >>tmpfile, crewid
            tmpfile.close()
        else:
            retro_fn = None
        args = {
            'firstdate': str(int(self.rundata.firstdate)),
            'lastdate': str(int(self.rundata.lastdate)),
            'starttime': str(int(self.rundata.starttime)),
            'extsys': self.rundata.extsys,
            'note': self.rundata.note or '',
            'admcode': self.rundata.admcode,
        }
        if not retro_fn is None:
            args['retrofile'] = retro_fn
        
        if self.rundata.extsys in ("SE", "S3"):
            ix = run.IndexFile(runid, self.rundata)
            
            basename = "TEMP_CREW_%08d.pdf" % (runid)
            filename = os.path.join(api.reportDirectory(), basename)
            api.runReport('report_sources.hidden.OvertimeTempCrew', runid, args=args, filename=filename)
            ix.add(report="Overtime Temp Crew", filename=basename)

            basename = "RESOURCE_POOL_ILLNESS_%08d.pdf" % (runid)
            filename = os.path.join(api.reportDirectory(), basename)
            api.runReport('report_sources.include.ResourcePoolIllnessReport', runid, args=args, filename=filename)
            ix.add(report="Resource Pool Illness Report", filename=basename)
            
            ix.write(api.reportFileName(runid, ext='.html'))
        else:
            api.runReport('report_sources.hidden.OvertimeTempCrew', runid, args=args)
        
        if not retro_fn is None:
            os.unlink(retro_fn)
        return runid

    def rosters(self):
        # part of the "interface"

        salary_iterator_where = 'not salary.%%crew_excluded%% and salary.%%salary_system%%(%s) = "%s"' % (
            self.rundata.firstdate,
            self.rundata.extsys_for_rave())
        salary_iterator = rave.iter(
                'iterators.roster_set',
                where=salary_iterator_where)

        # Set parameter to limit search for records within start -> end
        old_salary_month_start = rave.param(conf.startparam).value()
        rave.param(conf.startparam).setvalue(self.rundata.firstdate)
        old_salary_month_end = rave.param(conf.endparam).value()
        rave.param(conf.endparam).setvalue(self.rundata.lastdate)
        try:
            rosters = OvertimeManager(conf.context, salary_iterator).getOvertimeRosters()
        finally:
            rave.param(conf.startparam).setvalue(old_salary_month_start)
            rave.param(conf.endparam).setvalue(old_salary_month_end)
        if len(rosters) == 0:
            raise api.SalaryException("No matching rosters found.")
        return rosters

    def save(self, rec, type, value):
        # part of the "interface"
        self.data.append(rec.crewId, rec.empNo, self.articleCodes[type], value)
        

class DK(TempCrewRun):
    def __init__(self, record):
        articles = ['TEMPCREW', 'ILLTEMPCREW', 'TEMP_CC_QA', 'TEMP_CC_QA_HOURS_ATP']
        TempCrewRun.__init__(self, record, articles)

    def TEMP_CC_QA(self, rec):
        return self.times100(rec.getTempCrewDays()) if rec.is_QA_CC_temp else 0

    def TEMP_CC_QA_HOURS_ATP(self, rec):
        return self.hours100(rec.getTempCrewHours()) if rec.is_QA_CC_temp else 0

    def TEMPCREW(self, rec):
        return 0 if rec.is_QA_CC_temp else self.hours100(rec.getTempCrewHours())

    def ILLTEMPCREW(self, rec):
        return 0 if rec.is_QA_CC_temp else self.hours100(rec.getIllTempCrewHours())

    def __str__(self):
        return 'Danish temporary crew hours'


class NO(TempCrewRun):
    def __init__(self, record):
        articles = ['TEMPDAY','TEMPCREW']
        TempCrewRun.__init__(self, record, articles)

    def TEMPDAY(self, rec):
        return self.times100(rec.getTempCrewDays())

    def TEMPCREW(self, rec):
        return self.hours100(rec.getTempCrewHours())

    def __str__(self):
        return 'Norwegian temporary crew hours/days'


class SE(TempCrewRun):
    def __init__(self, record):
        articles = ['TEMPCREW']
        self.isCC4EXNG, = rave.eval('system_db_parameters.%%agreement_valid%%("4exng_cc_ot", %s)' % record.firstdate)
        if not self.isCC4EXNG:
            articles.append('TEMPCREWOT')
        TempCrewRun.__init__(self, record, articles)

    def TEMPCREW(self, rec):
        return self.hours100(rec.getTempCrewHours())

    def TEMPCREWOT(self, rec):
        if rec.isTemporary:
            return self.hours100(rec.getOvertime())
        return 0

    def __str__(self):
        return 'Swedish temporary crew days'


class S3(TempCrewRun):
    def __init__(self, record):
        articles = ['TEMPCREW']
        self.isCC4EXNG, = rave.eval('system_db_parameters.%%agreement_valid%%("4exng_cc_ot", %s)' % record.firstdate)
        if not self.isCC4EXNG:
            articles.append('TEMPCREWOT')
        TempCrewRun.__init__(self, record, articles)
        self.accumulated_rosters = []

    def _normal_test(self):
        self.get_codes()
        self.accumulated_rosters = self.rosters()
        self.save_run(self.accumulated_rosters)

    normal = _normal_test
    test = _normal_test

    def TEMPCREW(self, rec):
        return self.hours100(rec.getTempCrewHours())

    def TEMPCREWOT(self, rec):
        if rec.isTemporary:
            return self.hours100(rec.getOvertime())
        return 0

    def __str__(self):
        return 'Swedish temporary crew days'


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
