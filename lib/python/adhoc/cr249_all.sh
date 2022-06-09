#!/bin/sh


cmd="./cr249.sh"
paths="
/opt/Carmen/CARMUSR/sp4_livefeed_user/
/opt/Carmen/CARMUSR/sp4_livefeed_II_user/
/opt/Carmen/CARMUSR/sp4_sync_user/
"

for path in $paths
do
    echo "******************************************************************************"
    echo "Running $cmd in $path"
    echo "******************************************************************************"
    if
        $cmd $path
    then
        :
    else
        echo "!!! $cmd in $path FAILED !!!" 1>&2
        break
    fi
done
