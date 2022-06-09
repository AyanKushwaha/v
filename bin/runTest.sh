#!/bin/sh
# Wrapper script to start TextTest
#

cd `dirname $0`
while [ `pwd` != '/' -a ! -d "crc" ]
do
  cd ..
done
CARMUSR=`pwd`

if [ -n "$CARMSYS" ]; then 
    unset CARMSYS
fi

# Assume carmtmp is located beside the carmusr
# and has a similar name ending with tmp insted of usr/user
checkout=`dirname $CARMUSR`/`basename $CARMUSR | sed 's/_user$//g' | sed 's/_usr$//g'`
CARMTMP=${checkout}_tmp

# Consider creating a CARMTMP
if [ ! -d "$CARMTMP" ]
then
  echo "Cannot find CARMTMP. Creating one in $CARMTMP"
  mkdir $CARMTMP
fi

# Set TextTest to create temporary files in CARMTMP
TEXTTEST_TMP=$CARMTMP/TextTest
if [ ! -d "$TEXTTEST_TMP" ]
then
  mkdir $TEXTTEST_TMP
fi

# Instruct TextTest to look for test suites in CARMUSR/Testing
TEXTTEST_HOME=$CARMUSR/Testing

export TEXTTEST_HOME TEXTTEST_TMP
echo "TEXTTEST_HOME  : $TEXTTEST_HOME"
echo "TEXTTEST_TMP   : $TEXTTEST_TMP"
echo

# Run various testsuites depending on arguments
if [ $# -gt 0 ]; then
    while getopts abuft: OPTION
      do
      case ${OPTION} in
        # Run all testsuites
	  a) texttest -a rul_cas,rul_cct -g -c ${CARMUSR}/..
	     #texttest -a apc,cas,pyt -g -c ${CARMUSR}/..

             # Set carmtmp directory to texttest to that the report tests
             # will use the newly compiled rule set
             rm current_carmtmp
             ln -s $CARMTMP/TextTest current_carmtmp
	     texttest -a rep -g -c ${CARMUSR}/..
	     # Reset carmtmp
             rm current_carmtmp
	     ln -s $CARMTMP current_carmtmp;;
             
	  
        # Run the specified testsuite
	  t) echo "Running testsuite for app=${OPTARG}";
	     texttest -a ${OPTARG} -g -c ${CARMUSR}/..;;
	# Run night batch setup!
	  b)
	      
	      echo "Running nighjob testsuite";
	      export CARMUSR
	      if [[ -f "$CARMUSR/CVS/Tag" ]]; then
		  CVS_TAG=`cat "$CARMUSR/CVS/Tag" | sed 's/^.//g'`
	      else
		  CVS_TAG=`cat "$CARMUSR/CVS/Repository"`
	      fi
	      echo $CVS_TAG
	      export CVS_TAG
	      texttest -b nightjob -a unittest 
	      texttest -b nightjob -a unittest_reqreply

	      texttest -b nightjob -a unittest,unittest_reqreply  -coll web.performance_and_memory
	      texttest -b nightjob -a unittest,unittest_reqreply  -coll
	     ;;
	  u)
	      echo "Running testsuite unittest, unittest_reqreply";
	      export CARMUSR
	      texttest -a unittest,unittest_reqreply -c ${CARMUSR}/..
	      ;;
	  f)
	      echo "Running analyze rulesets test";
	      texttest -a analyze_cas,analyze_cct -g -c ${CARMUSR}/..
	      ;;
        # Usage text
	  \?) echo "Usage: runTest.sh [ -a -b -f -t app ]"
	      echo "  -a,      Run all tests";
	      echo "  -b,      Run nightjob test suite!";  
	      echo "  -u,      Open test suite with GUI";
	      echo "  -f,      Analyze rulesets";
              echo "  -t app,  Run the testsuite for application app (config.<app>)";
	  exit 2;;
      esac
    done
else
    # Default to running only the rule compile test
    texttest -a rul_cas,rul_cct -g -c ${CARMUSR}/..
fi

#texttest -a rul_cas,rul_cct -g -c ${CARMUSR}/..
#texttest -a apc,cas,rep,pyt -g -c ${CARMUSR}/..

if [ -d "$TEXTTEST_TMP/compile" ]; then
    echo "Removing temporary files in $TEXTTEST_TMP"
    rm -rf $TEXTTEST_TMP/compile
fi
if [ -d "$TEXTTEST_TMP/crc" ]; then
    rm -rf $TEXTTEST_TMP/crc
fi
