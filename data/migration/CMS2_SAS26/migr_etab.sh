#!/bin/bash
pwd
python $CARMUSR/lib/python/adhoc/crew_employment_etab.py <crew_employment >crew_employment.tmp
if [ $? -eq 0 ]
then
	mv crew_employment crew_employment.orig
	mv crew_employment.tmp crew_employment
fi

cp $CARMUSR/data/migration/CMS2_SAS26/planning_group_set .
