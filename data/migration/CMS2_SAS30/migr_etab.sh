#!/bin/bash
pwd
python $CARMUSR/lib/python/adhoc/aircraft_type_etab.py <aircraft_type >aircraft_type.tmp
if [ $? -eq 0 ]
then
	mv aircraft_type aircraft_type.orig
	mv aircraft_type.tmp aircraft_type
fi

