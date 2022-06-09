#!/bin/bash
# Generates the UDM pdf file consisting of both CARMSYS and CARMUSR model entities

# Sets the CARMUSR variable, if it is not set
if [ -z "$CARMUSR" ]; then
    a=`pwd`
    cd `dirname $0`
    while [ `pwd` != '/' -a ! -d "crc" ]; do
	cd ..
    done
    CARMUSR=`pwd`
    export CARMUSR
    cd $a
fi

echo CARMUSR: $CARMUSR

# Sets CARMDATA, CARMSYS, CARMTMP
. $CARMUSR/bin/carmenv.sh

cd ${CARMUSR}/data/config/models/documentation/

# The documentation is generated via a make command
make
if [ "$?" -eq "0" ]; then
    echo "The udm.pdf is in ${CARMUSR}/data/config/models/documentation/"
fi
make clean &> /dev/null

