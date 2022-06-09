
#
#######################################################
#
# Crew Info Audit Trail Report
#
# -----------------------------------------------------
# This report show the Audit Trail for all tables in
# Crew Info. It is meant to be run from the form itself
# -----------------------------------------------------
# Created:    2008-07-09
# By:         Jeppesen, Sten Larsson
#
#######################################################
from carmensystems.publisher.api import *
import modelserver as M
from report_sources.include.SASReport import SASReport
import Dates
import carmusr.AuditTrail2
from RelTime import RelTime
import AbsTime

tables = [('crew_contract', 'Contract', 'crew'),
          ('crew_document', 'Document', 'crew'),
          ('crew_employment', 'Employment', 'crew'),
          ('crew_not_fly_with', 'Prohibited', 'crew1'),
          ('crew_qualification', 'Crew Qualification', 'crew'),
          ('crew_qual_acqual', 'Limited Qualification', 'crew'),
          ('crew_restr_acqual', 'Qualification Restriction', 'crew'),
          ('crew_restriction', 'Restriction', 'crew'),
          ('crew_seniority', 'Seniority', 'crew'),
          ('special_schedules', 'Special Schedule', 'crewid')]

class Report(SASReport):

    def create(self):
        crewid = self.arg('crewid')
        try:
            change_introduced_start = AbsTime.AbsTime(self.arg('period_start'))
        except:
            change_introduced_start = None
        try:
            change_introduced_end = AbsTime.AbsTime(self.arg('period_end'))
        except:
            change_introduced_end = None

        SASReport.create(self,
                         title='Crew Info Audit Trail',
                         showPlanData=False,
                         headerItems={'Crew ': crewid})
        HEADER = Font(size=12, weight=BOLD)
        FBOLD = Font(weight=BOLD)
        MAXLINES = 67
        
        tm = M.TableManager.instance()
        auditTrail2 = carmusr.AuditTrail2.AuditTrail2()

        pagelines = 0
        for entityName, title, crewColumn in tables:
            entityDesc = tm.table(entityName).entityDesc()

            if pagelines + 4 > MAXLINES:
                self.newpage()
                pagelines = 0
                
            self.add(Row(Text('')))
            self.add(Row(Text(title, font=HEADER)))
            self.add(self.getTableHeader(['', 'COLUMN', 'VALUE'],
                                         widths=[50, None, None, None]))
            pagelines += 4

            for keys, entity in auditTrail2.search(entityName,
                                                   {crewColumn: crewid}):
                formattedKeys = []
                for key in keys:
                    if isinstance(key, AbsTime.AbsTime):
                        key = key.ddmonyyyy(True)
                    else:
                        key = str(key)
                    formattedKeys.append(key)
                box = Column()
                row_header = Row(', '.join(formattedKeys), font=FBOLD)
                boxlines = 1

                trail = tm.auditTrailI(entity)

                for commitDiff in trail:
                    commitInfo = commitDiff.commitInfo()
                    diff = commitDiff.diff()
                    

                    time = Dates.FDatInt2DateTime(commitInfo.getCommitTime().getRep())
                    commit_time = AbsTime.AbsTime(time)

                    # Make sure committime is in wanted period
                    if change_introduced_start and \
                           change_introduced_end and \
                           (commit_time <  change_introduced_start or \
                            commit_time > change_introduced_end):
                        continue
                    # Only add header to rows which we actually add
                    if row_header:
                        box.add(row_header)
                        row_header = None
                        
                    for change in diff:
                        # only one change per commit 
                        break
                    else:
                        continue
                    
                    changeType = change.getType()
                    changestr = ['Added', 'Modified', 'Removed'][changeType]
                    commitbox = Column()
                    user = commitInfo.getUser()
                    
                    commitbox.add(Row(Text('%s %s by %s' % (changestr, time, user))))
                    commitboxlines = 1

                    anychanges = changeType != M.Change.MODIFIED
                    if changeType != M.Change.REMOVED:
                        for column, old, new in change:
                            columnType = entityDesc.type(entityDesc.column(column))
                            description = entityDesc.description(entityDesc.column(column))
                            # Lets try and format "new" as long as it is a propper value
                            if new is not None:
                                if columnType == M.TIME:
                                    if column == 'validto':
                                        offset = RelTime('24:00')
                                    else:
                                        offset = RelTime(0)    
                                    new = (new-offset).ddmonyyyy(True)

                                # CR62
                                if entityName == 'crew_document' and \
                                       column == 'docno' and \
                                       keys[1] in ('LICENCE', 'MEDICAL'):
                                    new = new[:-4] + "****"
                                    
                            commitbox.add(Row(Text(''),
                                              Text(description),
                                              Text(new or '')))
                            commitboxlines += 1
                            anychanges = True

                    commitbox.add(Row(Text('')))
                    commitboxlines += 1

                    if changeType != M.Change.MODIFIED or anychanges:
                        box.add(commitbox)
                        boxlines += commitboxlines
                    
                if pagelines + boxlines > MAXLINES:
                    self.newpage()
                    pagelines = 0
                    
                self.add(box)
                pagelines += boxlines
