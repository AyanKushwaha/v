import os

import StartTableEditor
import carmensystems.rave.api as rave
from tm import TM
from tm import TempTable
from modelserver import StringColumn, IntColumn


def startCrewAdditionForm(formname="CrewAddition"):
    """
    Opens a form for viewing and editing crew.
    """

    form = StartTableEditor.StartTableEditor(['-P', 'form_id=%s' % formname,
                                            '-P', 'form_name=%s' % formname,
                                            '-f', '$CARMUSR/data/form/add_crew_from_sap.xml'],
                                            "CrewAddition")

def openCrewAdditionForm():
    CMS_ROOT = os.getenv('CARMUSR')
    
    crewTable = NewCrewTempTable()
    crewTable.removeAll()

    for crew_unknown in TM.crew_unknown:
        if str(crew_unknown.corrected) in ['false', '0']:
            crew = next(TM.crew.search('(&(empno=%s))' % str(crew_unknown.extperkey)), None)

            if not crew:
                createTemporaryTable(int(crew_unknown.extperkey), crewTable)
                tmpCrew = createTemporaryCrew(crew_unknown)
                createCrewEntry(tmpCrew)
    startCrewAdditionForm()


def createCrewEntry(tmpCrew):
    crewEntry = next(TM.tmp_new_crew_tbl.search('(&(empno=%s))' % tmpCrew.get('empno', '')), None)
    if crewEntry:
        crewEntry.id = tmpCrew.get('empno', '')
        crewEntry.name = tmpCrew.get('name', '')
        crewEntry.forenames = tmpCrew.get('forenames', '')
        crewEntry.bcountry = tmpCrew.get('country', '')



def createTemporaryTable(extperkey, crewTable):
    crewTable.create((extperkey,))


def createTemporaryCrew(crew):

    country = ''
    region = ''
    homebase = ''
    if str(crew.empcountry) == '09':
        country = 'DK'
        region = 'SKD'
        homebase = 'CPH'
    elif str(crew.empcountry) == '20':
        country = 'NO'
        region = 'SKN'
        homebase = 'OSL'
    elif str(crew.empcountry) == '23':
        country = 'SE'
        region = 'SKS'
        homebase = 'STO'
    elif str(crew.empcountry) == '99':
        country = 'HK'
        region = 'SKK'
        homebase = 'HKG'

    return dict(
        empno = str(crew.extperkey),
        name = crew.name,
        forenames = crew.forenames,
        country = country,
        company = 'SK',
        region = region,
        homebase = homebase,
        validto = '31Dec2035 00:00'
    )


class NewCrewTempTable(TempTable):
    _name = "tmp_new_crew_tbl"
    
    _keys = [
        IntColumn("empno", "e"),
    ]
    
    _cols = [
        StringColumn("id", "i"),
        StringColumn("name", "n"),
        StringColumn("forenames", "f"),
        StringColumn("bcity", "bc"),
        StringColumn("bcountry", "b"),
        StringColumn("employmentdate", "ed"),
        StringColumn("employmentcountry", "ec"),
        StringColumn("region", "r"),
        StringColumn("homebase", "hb"),
        StringColumn("rank", "rk"),
        StringColumn("contract", "c"),
    ]


if __name__ == '__main__':
    pass

# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof