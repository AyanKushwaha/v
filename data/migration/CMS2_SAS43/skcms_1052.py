import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2016_11_29_1'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):

    ops = []

    # Removing all current S3 rows from 'salary_crew_activity'
    for row in fixrunner.dbsearch(dc, 'salary_crew_activity', "extsys='S3'"):
        ops.append(fixrunner.createop('salary_crew_activity','D',row))

    # Removing all current S3 rows from 'salary_article'
    for row in fixrunner.dbsearch(dc, 'salary_article', "extsys='S3'"):
        ops.append(fixrunner.createop('salary_article','D',row))

    # Dates range for 'salary_crew_activity' and 'salary_article'
    validfrom = int(AbsTime('01Jan2016'))
    validto   = int(AbsTime('31Dec2035'))

    # Data for salary_crew_activity
    absence_act = [ ("ABS_ACT_IL",      "0500",	"Sjuk 100%"),
                    ("ABS_ACT_ILV",	    "0500", "Sjuk 100%"),
                    ("ABS_ACT_IL12",	"0500",	"Sjuk 100%"),
                    ("ABS_ACT_IL2",	    "0500",	"Sjuk 100%"),
                    ("ABS_ACT_IL7",	    "0805",	"Illness while on duty"),
                    ("ABS_ACT_LA20",	"0805",	"Sjuk del av dag - Crew"),
                    ("ABS_ACT_LA20",	"1525",	"Tjl studier, ej sem gr HR"),
                    ("ABS_ACT_LA21_CC",	"1525",	"Tjl studier, ej sem gr HR"),
                    ("ABS_ACT_LA31",	"1500",	"Tjanstledig"),
                    ("ABS_ACT_LA41",	"1500",	"Kort Tjl Flygande HR"),
                    ("ABS_ACT_LA42",	"1502",	"Kort Tjl Flygande HR"),
                    ("ABS_ACT_LA44",	"1500",	"Tjanstledig"),
                    ("ABS_ACT_LA51",	"1500",	"Tjanstledig"),
                    ("ABS_ACT_LA57",	"1500",	"Tjanstledig"),
                    ("ABS_ACT_LA64",	"1002",	"Kort Foraldr.led. Flyg HR"),
                    ("ABS_ACT_LA7",	    "1500",	"Tjanstledig"),
                    ("ABS_ACT_LA70",	"1500",	"Tjanstledig"),
                    ("ABS_ACT_LA89",	"1500",	"Tjanstledig"),
                    ("ABS_ACT_LA91",	"1060",	"Tillf foraldrapenn 100%"),
                    ("ABS_ACT_LA92",	"1075",	"Tillf foraldrp deltid 50%"),
                    ("ABS_ACT_VA_CC",	"0100",	"Semester"),
                    ("ABS_ACT_VA1_FC",	"0110",	"Obetald semester - F/D (kontrollera!") ]

    schedule_act = [ "F_ACT_F",
                     "F_ACT_F0",
                     "F_ACT_F1",
                     "F_ACT_F14",
                     "F_ACT_F20",
                     "F_ACT_F22",
                     "F_ACT_F3",
                     "F_ACT_F31",
                     "F_ACT_F33",
                     "F_ACT_F34",
                     "F_ACT_F35",
                     "F_ACT_F3S",
                     "F_ACT_F4",
                     "F_ACT_F61",
                     "F_ACT_F7",
                     "F_ACT_F7S",
                     "F_ACT_F8",
                     "F_ACT_F88",
                     "F_ACT_FK",
                     "F_ACT_FN",
                     "F_ACT_FS",
                     "F_ACT_FW",
                     "F_ACT_LA55",
                     "F_ACT_LA8",
                     "F_ACT_LA84" ]

    # Updating salary_crew_activity
    for intartid, extartid, note in absence_act:
        ops.append( fixrunner.createOp("salary_crew_activity", "W", {
                    "extsys":    "S3",
                    "intartid":  intartid,
                    "validfrom": validfrom,
                    "validto":   validto,
                    "extartid":  extartid,
                    "extent":    100,
                    "note":      note }))

    for intartid in schedule_act:
        ops.append( fixrunner.createOp("salary_crew_activity", "W", {
                    "extsys":    "S3",
                    "intartid":  intartid,
                    "validfrom": validfrom,
                    "validto":   validto,
                    "extartid":  "FREEDAY",
                    "extent":    100,
                    "note":      "" }))

    # Data for salary_article
    articles = [("2400", int(AbsTime('01Jan2006')), int(AbsTime('29Feb2016')), "OTPT",                 "Overtime for part time crew"),
                ("2401", int(AbsTime('01Jan2006')), int(AbsTime('31Dec2035')), "CALM_OTFC",            "Overtime for calendar month / flight crew"),
                ("2402", int(AbsTime('01Jan2006')), int(AbsTime('31Dec2034')), "CALW",                 "Calender week (42 hrs)"),
                ("2403", int(AbsTime('01Jan2006')), int(AbsTime('31Dec2034')), "BOUGHT",               "Bought day ( > 6 hours) FC and CC 14 pct"),
                ("2404", int(AbsTime('01Jan2013')), int(AbsTime('31Dec2035')), "BOUGHT_8",             "Bought day (<= 6 hours) CC and FC 8 pct"),
                ("2405", int(AbsTime('01Jan2006')), int(AbsTime('31Dec2034')), "DUTYP",                "Duty pass overtime (former L204)"),
                ("2406", int(AbsTime('01Oct2015')), int(AbsTime('31Dec2035')), "OT_CO_LATE_FC",        "Overtime pr half hour for FD"),
                ("2407", int(AbsTime('01May2016')), int(AbsTime('31Dec2035')), "BOUGHT_FORCED",        "Forced Bought day when co after 00:00 delay"),
                ("2408", int(AbsTime('01Jan2006')), int(AbsTime('31Dec2034')), "BOUGHT_B",             "Bought BL day"),
                ("2409", int(AbsTime('01Jul2016')), int(AbsTime('31Dec2035')), "SNGL_SLIP_LONGHAUL",   "Extra salary for a single-slipping longhaul flight"),
                ("2412", int(AbsTime('01Jan2006')), int(AbsTime('31Dec2034')), "F7S",                  "F7S days"),
                ("2413", int(AbsTime('01Jan2006')), int(AbsTime('31Dec2034')), "F0_F3",                "Comp days other"),
                ("2414", int(AbsTime('01Jan2011')), int(AbsTime('31Dec2034')), "TEMPCREW",             "Temporary crew hours"),
                ("5100", int(AbsTime('01Jan2006')), int(AbsTime('31Dec2034')), "INST_CLASS",           "Instructor - Classroom"),
                ("5101", int(AbsTime('01Jan2006')), int(AbsTime('31Dec2034')), "INST_LCI",             "Instructor - LCI"),
                ("5102", int(AbsTime('01Dec2012')), int(AbsTime('31Dec2035')), "INST_CC",              "Instructor - CC"),
                ("5103", int(AbsTime('01Jan2006')), int(AbsTime('31Dec2035')), "INST_CRM",             "Instructor - CRM"),
                ("5104", int(AbsTime('01May2013')), int(AbsTime('31Dec2035')), "INST_LCI_LH",          "Instructor - LCI (LH)"),
                ("5105", int(AbsTime('01Dec2012')), int(AbsTime('31Dec2035')), "INST_LIFUS_ACT",       "Instructor - Simulator"),
                ("5106", int(AbsTime('01Jan2016')), int(AbsTime('31Dec2035')), "INST_NEW_HIRE",        "Instructor - New Hire Follow Up"),
                ("5107", int(AbsTime('01Dec2012')), int(AbsTime('31Dec2035')), "INST_SIM",             "Instructor - Simulator"),
                ("5108", int(AbsTime('01Dec2012')), int(AbsTime('31Dec2035')), "INST_SIM_BR",          "Instructor - Simulator (Brief/Debrief)"),
                ("5109", int(AbsTime('01Apr2012')), int(AbsTime('31Dec2035')), "INST_SKILL_TEST",      "Instructor - Skill-Test"),
                ("5110", int(AbsTime('01Jan2006')), int(AbsTime('31Dec2034')), "SCC",                  "Senior cabin crew allowance"),
                ("5111", int(AbsTime('01Jan2006')), int(AbsTime('31Dec2034')), "VA_REMAINING_YR",      "VA days year account"),
                ("8800", int(AbsTime('01Jan2006')), int(AbsTime('30Sep2034')), "PERDIEM_TAX_DAY",      "Endagstraktement skatt"),
                ("8801", int(AbsTime('01Jan2006')), int(AbsTime('31Dec2034')), "PERDIEM_TAX_DOMESTIC", "Inrikes traktement skatt"),
                ("8802", int(AbsTime('01Jan2006')), int(AbsTime('31Dec2034')), "PERDIEM_TAX_INTER",    "Utrikes traktement skatt"),
                ("9100", int(AbsTime('01Jan2006')), int(AbsTime('31Dec2034')), "PERDIEM_SALDO",        "Per Diem saldo, pos and neg"),
                ("9300", int(AbsTime('01Jan2006')), int(AbsTime('31Dec2034')), "MEAL",                 "Meal on board deduction FC and CC")]

    # Updating salary_article
    for extartid, validfrom, validto, intartid, note in articles:
        ops.append( fixrunner.createOp("salary_article", "W", {
                    "extsys":    "S3",
                    "extartid":  extartid,
                    "validfrom": validfrom,
                    "validto":   validto,
                    "intartid":  intartid,
                    "note":      note }))

    return ops

fixit.program = 'skcms_1052.py (%s)' % __version__

if __name__ == '__main__':
    try:
        fixit()
    except fixrunner.OnceException:
        print "    - migration already run with key ",__version__
