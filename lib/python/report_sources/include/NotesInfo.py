"""
 $Header$
 
 Main module for annotations, notes, and special schedule reports.

 Created:    April 2007
 By:         Erik K Gustafsson, Jeppesen Systems AB

"""

import Cui, Variable
from carmensystems.publisher.api import *
import carmensystems.rave.api as rave
from AbsDate import AbsDate

from report_sources.include.SASReport import SASReport

REPORT_NAMES = ("Special Schedule Info", "Annotations Info")
WIDTHS = (180,80,360,45,45)

class NotesInfo(SASReport):
    TYPE_SPEC_SCHED = 0
    TYPE_ANNOTATIONS = 1

    def noteRow(self, textItems):
        output = Row()
        for (textItem, cellWidth) in zip(textItems, WIDTHS):
            output.add(Text(textItem, width=cellWidth))
        return output

    def create(self, reportType, context='default_context'):
        # Basic setup
        SASReport.create(self, REPORT_NAMES[reportType], False, orientation=LANDSCAPE)
                
        specSchedExpr = rave.foreach(
            rave.times('crew.%spec_sched_count%'),
            'crew.%spec_sched_type%(fundamental.%py_index%)',
            'crew.%spec_sched_descr%(fundamental.%py_index%)',
            'crew.%spec_sched_start%(fundamental.%py_index%)',
            'crew.%spec_sched_end%(fundamental.%py_index%)',
            'crew.%spec_sched_si%(fundamental.%py_index%)',
            )
        annotationExpr = rave.foreach(
            rave.times('annotations.%annotation_count%'),
            'annotations.%annotation_code%(fundamental.%py_index%)',
            'annotations.%annotation_descr%(fundamental.%py_index%)',
            'annotations.%annotation_period_start%(fundamental.%py_index%)',
            'annotations.%report_annotation_period_end%(fundamental.%py_index%)',
            )
        rostersExpr = rave.foreach(
            'iterators.roster_set',
            'report_common.%crew_string%',
            'annotations.%on_crew%',
            annotationExpr,
            'crew.%has_spec_sched%',
            specSchedExpr)
        
        if reportType == NotesInfo.TYPE_ANNOTATIONS:
            Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiWhichArea, "window")
        rosters, = rave.eval(context, rostersExpr)
        
        header = self.getDefaultHeader()

        planningPeriod, = rave.eval(
            'crg_date.%print_period%(annotations.%search_start%, annotations.%search_end%-0:01)')
        buf = Variable.Variable()

        Cui.CuiGetSubPlanPath(Cui.gpc_info, buf)
        if not buf.value:
            Cui.CuiGetLocalPlanPath(Cui.gpc_info,buf)
        plan = buf.value or "-"

        ruleSet, = rave.eval('rule_set_name')
        items = SASReport.getTableHeader(self,[
                                "Period: " + planningPeriod,
                                "Rule set: " + ruleSet,
                                "Plan: " + plan
                            ],
                            vertical=False, widths=None, aligns=None)
        header.add(items)
        header.add(self.getTableHeader(('Crew','Type','Note','Valid from','Valid until'), widths=WIDTHS))
        header.add(Text(""))
        header.set(border=border(bottom=0))
        self.setHeader(header)

        crewString = ""
        for (ix,crewString,hasAnnotations,annotations, hasSpecSched, specScheds) in rosters:
            oneCrew = Column()
            addCrew = False
            if ((reportType == NotesInfo.TYPE_SPEC_SCHED) and hasSpecSched):
                for (jx,type,note,start,end,si) in specScheds:
                    oneRow = self.noteRow(
                        (crewString, type, note, AbsDate(start), AbsDate(end))
                        )
                    oneCrew.add(oneRow)
                    if si is not None:
                        si_row = self.noteRow(("","",si,"",""))
                        oneCrew.add(si_row)
                    crewString = " "
                    addCrew = True
            if hasAnnotations:
                for (jx,code,descr,start,end) in annotations:
                    if ((reportType == NotesInfo.TYPE_ANNOTATIONS) or (code == "J4")):
                        oneRow = self.noteRow(
                            (crewString, code, descr, AbsDate(start), AbsDate(end))
                            )
                        oneCrew.add(oneRow)
                        crewString = " "
                        addCrew = True
                        oneCrew.page()
            if addCrew:
                self.add(oneCrew)
                self.add(' ')
                self.page0()
        if not crewString:
            self.add("No crew information, try again ............ !")


