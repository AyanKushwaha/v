#!/bin/sh

CARMUSR=`readlink -f \`dirname $0\`/..`
if [ ! -f $CARMUSR/lib/java/com.carmensystems.rave.parsers.jar ]; then
  echo "Stealing the cookie jars..."
  mkdir -p $CARMUSR/lib/java/
  cp /carm/proj/skcms/lib/java/* $CARMUSR/lib/java/
fi
_CLASSPTH=$CARMUSR/lib/java/com.carmensystems.rave.parsers.jar:$CARMUSR/lib/java/antlr-3.1.1.jar
if [ ! -f $CARMUSR/java_src/ExtractRuleInfoToCSV.class -o $CARMUSR/java_src/ExtractRuleInfoToCSV.java -nt $CARMUSR/java_src/EExtractRuleInfoToCSV.class ]; then
   echo "Compiling Java code..."
   javac -cp $_CLASSPTH $CARMUSR/java_src/ExtractRuleInfoToCSV.java
fi
echo "Running Java code..."
java -cp $_CLASSPTH:$CARMUSR/java_src ExtractRuleInfoToCSV $CARMUSR > $CARMUSR/data/doc/rules.csv
