#!/bin/bash
cd $CARMDATA/LOCAL_PLAN/
find . -name "crew_employment" -execdir $CARMUSR/data/migration/CMS2_SAS26/migr_etab.sh \; 
