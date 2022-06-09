#!/bin/bash
echo "********************************************"
echo "*   - Running `basename $BASH_SOURCE`"
echo "********************************************"
echo " - Running adhoc script for sascms-2537 ..."
python $CARMUSR/lib/python/adhoc/sascms-2537.py
