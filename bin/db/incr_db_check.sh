#!/bin/bash

# Sets the CARMUSR env, if it is not set
if [ -z "$CARMUSR" ]; then
  a=`pwd`
  cd `dirname $0`
  while [ `pwd` != '/' -a ! -d "crc" ]; do
    cd ..
  done
  CARMUSR=`pwd`
  export CARMUSR
  cd $a

  . $CARMUSR/bin/carmenv.sh
fi

MAILTO=`xmlconfig /carmen/config[1]/programs/dig/dig_settings/mail/to | cut -d ' ' -f 3`
SANITYDIR=$CARMDATA/sanity
mkdir -p $SANITYDIR
LASTLOG=`ls -t $SANITYDIR/sanity-*.log | head -n 1`
THISLOG=$SANITYDIR/sanity-`date +%Y%m%d%H%M%S`.log
ERRLOG=$SANITYDIR/sanity-stderr-`date +%Y%m%d%H%M%S`.log

$CARMUSR/bin/db/db_check.sh -q > $THISLOG 2> $ERRLOG
retVal=$?
if [ $retVal -ne 0 ]; then
    echo "ERROR: DB sanity check failed"
    cat $ERRLOG
    mail -s "CMS: DB sanity check failed" $MAILTO < $ERRLOG
    exit $retVal
fi

# For debugging
# echo "Error `date +%Y%m%d%H%S`" >> $THISLOG

sort $LASTLOG | uniq > $LASTLOG.sorted
sort $THISLOG | uniq > $THISLOG.sorted

diff $LASTLOG.sorted $THISLOG.sorted | grep '^>' | cut -d ' ' -f 2- > $THISLOG.new

if [ -s "$THISLOG.new" ]
then
    mail -s "CMS: New problems in db" $MAILTO < $THISLOG.new
fi

diff $LASTLOG.sorted $THISLOG.sorted | grep '^<' | cut -d ' ' -f 2- > $THISLOG.fixed

if [ -s "$THISLOG.fixed" ]
then
    mail -s "CMS: Fixed problems in db" $MAILTO < $THISLOG.fixed
fi

# Clean up
rm $LASTLOG.sorted $THISLOG.sorted
ls -t $SANITYDIR/sanity-*.log | tail -n +8 | xargs rm
