#!/bin/sh
# @(#) $Header: /opt/Carmen/CVS/sk_cms_user/bin/testing/fixTESTdata.sh,v 1.1 2010/02/24 09:59:38 adg239 Exp $


wherami=`dirname $0`
_CARMUSR=`(cd $wherami/..; pwd)`


error ( ) {
    echo "$*" 2>&1
    exit 2
}

echo ""
echo "This script disables ALL pending jobs in the job table"
echo "   and updates email addresses in meal_supplier, meal_customer and"
echo "   and updates email addresses in hotel and transport tables" 
echo "It should only be run after copying PROD data to TEST" 
echo ""
echo "Can be run with '-n' option, then no commit is done to Database"
echo "Can be run with '-d' option, then all updates are printed"
echo ""
read -p "Are you sure you want to continue, then enter yes ? " ans
echo ""
if [ "$ans" != "yes" ];then
    echo "Exiting without doing anything !"
    exit
fi

SK_APP=Tracking
export SK_APP

# If CARMUSR not set, use current directory as reference point.
CARMUSR=${CARMUSR-"${_CARMUSR}"}
export CARMUSR

# Get other environment (CARMSYS, ...)
. $CARMUSR/bin/cmsshell

python $CARMUSR/lib/python/adhoc/disableJobs.py $@
python $CARMUSR/lib/python/adhoc/fixCrewMealEmail.py $@ 
python $CARMUSR/lib/python/adhoc/fixHotelEmail.py $@ 


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
