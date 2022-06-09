#!/bin/sh
#  bin/cmsshell should be run before running this script
{
echo "#################################"
echo "### About to execute db talestats at: "$(date)
echo "#################################"
$CARMUSR/bin/cmsshell db tablestats # NOT ON MIGRATION R22
echo "%%%%%%%% Finished dab tablestats %%%%%%% at: "$(date)
echo "###################################"
echo "### About to execute db schemastats at: "$(date)
echo "###################################"
$CARMUSR/bin/cmsshell db schemastats
echo "%%%%% Finished db schemastats %%%%%%% at: "$(date)
echo "####################################"
echo "### About to execute db updatepubrev at: "$(date)
echo "####################################"
$CARMUSR/bin/cmsshell db updatepubrev
echo "%%%%% Finished db updatepubrev %%%%%% at: "$(date)
echo "####################################################"
echo "### About to execute accumulate_cleanup_and_stats.sh at: "$(date)
echo "####################################################"
$CARMUSR/bin/db/accumulate_cleanup_and_stats.sh  # NOT ON MIGRATION R22 it will be run under crontab rescheduled
echo "%%%%% Finished accumulate_cleanup_and_stats.sh %%%%% at: "$(date)
} | tee $CARMTMP/optimizeSchema_$(date "+%Y%m%d_%H%M%S").log
