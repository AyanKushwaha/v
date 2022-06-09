#!/bin/bash
cd $CARMDATA/LOCAL_PLAN/
find . -name "aircraft_type.orig" -execdir $CARMUSR/data/migration/CMS2_SAS30/migr_back.sh \; 
