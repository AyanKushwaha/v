#

#
#
__version__ = "$Revision$"
"""
TrainingInfo
Module for doing: TrainingInfo report showing planned training and new-restrictions on actype
@date: 10jun2008
@author: Per Groenberg (pergr), started by Acosta, F.
@org: Jeppesen Systems AB
"""
# Note: There are some minor distinctions between Tracking and Planning.

from carmensystems.publisher.api import *
import carmensystems.rave.api as r
from report_sources.include.SASReport import SASReport
from AbsDate import AbsDate
from RelTime import RelTime


def htext(*a, **k):
    """Text for header row"""
    k['valign'] = CENTER
    return Text(*a, **k)


def htext_b(*a, **k):
    """Text for header row"""
    k['background'] = '#efefef'
    return htext(*a, **k)


def right(*a, **k):
    """Text aligned right."""
    k['align'] = RIGHT
    k['padding'] = padding(2, 2, 12, 2)
    return Text(*[str(x) for x in a], **k)


def right_b(*a, **k):
    k['background'] = '#efefef'
    return right(*a, **k)


class TrainingInfo(SASReport):
    def create(self, scope='general', context='default_context'):
        SASReport.create(self, 'Training Info', orientation=PORTRAIT,
                usePlanningPeriod=True)

                
        crewExpr = r.foreach(r.iter('iterators.roster_set', 
                                    where='report_common.%crew_has_training_in_pp% or true'),
                             'report_common.%crew_string%',
                             r.foreach(r.times('training.%training_activities_in_pp%',
                                               sort_by='report_common.%course_start_ix%'),
                                       'report_common.%course_type_ix%',
                                       'report_common.%course_start_ix%',
                                       'report_common.%course_end_ix%',
                                       'report_common.%course_index_ix%',
                                       'report_common.%course_attribute_ix%',
                                       'report_common.%course_ac_qual_ix%',
                                       'report_common.%course_maxdays_ix%',
                                       'report_common.%course_req_flights_ix%',
                                       'report_common.%course_perf_flights_ix%',
                                       'report_common.%course_publ_flights_ix%',
                                       'report_common.%course_plan_flights_ix%',
                                       ),
                             r.foreach(r.times('crew.%qrestr_rows%',
                                               where=
                                               'crew.%qrestr_restr_type%(fundamental.%py_index%)="NEW" and '+\
                                               'crew.%qrestr_restr_subtype%(fundamental.%py_index%)="ACTYPE"'),
                                       'crew.%qrestr_qual_type%(fundamental.%py_index%)',         
                                       'crew.%qrestr_qual_subtype%(fundamental.%py_index%)',
                                       'crew.%qrestr_restr_type%(fundamental.%py_index%)',
                                       'crew.%qrestr_restr_subtype%(fundamental.%py_index%)',
                                       'crew.%qrestr_validfrom%(fundamental.%py_index%)',
                                       'crew.%qrestr_validto_excl%(fundamental.%py_index%)',
                                       'report_common.%new_restr_perf_flights_ix%',
                                       'report_common.%new_restr_publ_flights_ix%',
                                       'report_common.%new_restr_plan_flights_ix%',
                                       ),
                             r.foreach(r.times('1',
                                       where='report_training.%consolidation_ac_qual% <> ""'),
                                       '"Consolidation flights"',
                                       'report_training.%consolidation_ac_qual%',
                                       'report_training.%consolidation_course_type%',
                                       'report_training.%consolidation_period_start%',
                                       'report_training.%consolidation_period_end%',
                                       'report_training.%nr_consolidation_sectors_required%',
                                       'report_training.%nr_consolidation_sectors_perf%',
                                       'report_training.%nr_consolidation_sectors_publ%',
                                       'report_training.%nr_consolidation_sectors_plan%',
                                       ),
                             r.foreach(r.times('1',
                                               where='report_training.%etops_training_ac_qual% <> ""'),
                                       '"Consolidation flights"',
                                       'report_training.%etops_training_ac_qual%',
                                       'report_training.%etops_training_course_type%',
                                       'report_training.%etops_training_period_start%',
                                       'report_training.%etops_training_period_end%',
                                       'report_training.%nr_etops_training_sectors_required%',
                                       'report_training.%nr_etops_training_sectors_perf%',
                                       'report_training.%nr_etops_training_sectors_publ%',
                                       'report_training.%nr_etops_training_sectors_plan%',
                                   ))
        crewData, = r.eval(context,crewExpr)
        if crewData:
            for (ix, crewString, courses, restrictions, qualifications1, qualifications2) in crewData:
                
                m_courses, m_restrictions = self.mergeNew(courses, restrictions)
                m_qualifications = qualifications1 + qualifications2
                
                crewBox = Column()
                # Header
                crewBox.add(Row(crewString, font=self.HEADERFONT,
                        background=self.HEADERBGCOLOUR))
                # Courses
                crewBox.add(Row(
                    htext("Type"), 
                    htext("Start"), 
                    htext("End"), 
                    htext("Index"), 
                    htext("Attribute"), 
                    htext("AC Qual"), 
                    htext("Max days"), 
                    htext("Required"), 
                    htext_b("Performed"),
                    htext_b("Published"),
                    htext_b("Planned"),
                    htext("Total"),
                    htext("Needed"),
                    font=Font(weight=BOLD)))
                for (jx, type, start, end, index, attr, ac_qual, _max_days,
                        required_legs, performed_legs, published_legs, 
                        planned_legs, merged) in m_courses:
                    max_days = _max_days or 0

                    performed_legs = performed_legs or 0
                    published_legs = published_legs or 0
                    planned_legs = planned_legs or 0
                    required_legs = required_legs or 0
                    
                    total_legs = performed_legs + published_legs + planned_legs
                    needed_legs = required_legs - total_legs
                    
                    if (index == 1):
                        type = str(type)
                        start = str(AbsDate(start))
                        end = str(AbsDate(end))
                    elif (attr == "NEW" and merged):
                        type = ""
                        start = str(AbsDate(start))
                        end = str(AbsDate(end))
                    else:
                        type = ""
                        start = "        ''"
                        end = "        ''"
                        
                    crewBox.add(Row(
                        type,
                        start,
                        end,
                        right(index),
                        str(attr),
                        str(ac_qual),
                        right(max_days),
                        right(required_legs), 
                        right_b(performed_legs), 
                        right_b(published_legs),
                        right_b(planned_legs), 
                        right(total_legs), 
                        right(needed_legs),
                        ))
                # Restrictions
                crewBox.add(Row(height=1,border=border(0,0,0,1)))
                crewBox.add(Row(height=1))
                for (kx, qln_type, qln_subtype, acr_type, acr_subtype,
                     acr_validfrom, acr_validto, perf, publ, plan) in m_restrictions:
                    crewBox.add(Row(
                        str(acr_type)+' '+str(acr_subtype),
                        str(AbsDate(acr_validfrom)),
                        str(AbsDate(acr_validto)),
                        right('-'),
                        str('-'),
                        str(qln_subtype),
                        right('-'),
                        right('-'), 
                        right_b(perf), 
                        right_b(publ),
                        right_b(plan), 
                        right('-'), 
                        right('-'),
                        ))
                # Consolidation sectors
                crewBox.add(Row(height=1,border=border(0,0,0,1)))
                crewBox.add(Row(height=1))
                for (kx, attribute, ac_qual, course_type, validfrom, validto,
                     required, perf, publ, plan) in m_qualifications:
                    total = perf + publ + plan
                    needed = max(0, required - total)
                    maxdays = int((validto - validfrom) / RelTime('24:00'))
                    crewBox.add(Row(
                        str(course_type),
                        str(AbsDate(validfrom)),
                        str(AbsDate(validto)-RelTime('24:00')),
                        right('-'),
                        str(attribute),
                        str(ac_qual),
                        right(maxdays),
                        right(required), 
                        right_b(perf), 
                        right_b(publ),
                        right_b(plan), 
                        right(total), 
                        right(needed),
                        ))
                crewBox.add(Row(height=12))
                self.add(Row(crewBox))
                self.page0()
        else:
            self.add(Row("No training program was found for the selected crew member(s).",
                    font=self.HEADERFONT, height=36))

    def mergeNew(self, courses, restr):
        
        mergedict = {}
        new_crs = []
        new_restr = []
        
        # Go through all restrictions and pick out info about all NEW restr.
        # We can't remove the restr yet if the NEW is missing in courses
        p = 0
        for (kx, qln_type, qln_subtype, acr_type, acr_subtype,
             acr_validfrom, acr_validto, perf, publ, plan) in restr:
            if acr_type == "NEW":
                # print qln_type, qln_subtype, acr_type, acr_subtype
                # print "Adding     :", qln_subtype
                mergedict[qln_subtype] = (acr_validfrom, acr_validto, perf, publ, plan)
                p += 1
            
        # Build a new list with updated NEW rows in courses with info from restr
        p = 0
        for (jx, ctype, start, end, index, attr, ac_qual, _max_days,
             required_legs, performed_legs, published_legs, planned_legs) in courses:
            merged = False
            if attr == "NEW":
                try:
                    # print "Looking for:", ac_qual
                    (a, b, c, d, e) = mergedict.get(ac_qual)
                    p += 1
                    start = a
                    end = b
                    performed_legs = c
                    published_legs = d
                    planned_legs = e
                    merged = True
                    del mergedict[ac_qual]
                except:
                    pass
            new_crs.append((jx, ctype, start, end, index, attr, ac_qual, _max_days,
                            required_legs, performed_legs, published_legs, planned_legs, merged))
        
        # Remove "used" NEW rows fron restr
        for (kx, qln_type, qln_subtype, acr_type, acr_subtype,
             acr_validfrom, acr_validto, perf, publ, plan) in restr:
            if (acr_type == "NEW" and mergedict.has_key(qln_subtype)):
                new_restr.append((kx, qln_type, qln_subtype, acr_type, acr_subtype,
                                  acr_validfrom, acr_validto, perf, publ, plan))
        
        return new_crs, new_restr
    
# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
