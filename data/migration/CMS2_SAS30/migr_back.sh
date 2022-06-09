#!/bin/bash
pwd
#python $CARMUSR/lib/python/adhoc/aircraft_tupe_back.py <aircraft_tupe>aircraft_type.tmp
if [ $? -eq 0 ]
then
	mv aircraft_type.orig aircraft_type
fi

