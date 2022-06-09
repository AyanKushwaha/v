#!/bin/sh

CARMUSR=`readlink -f \`dirname $0\`/..`
if [ ! -f $CARMUSR/lib/java/com.carmensystems.rave.parsers.jar ]; then
  echo "Stealing the cookie jars..."
  mkdir -p $CARMUSR/lib/java/
  cp /carm/proj/skcms/lib/java/* $CARMUSR/lib/java/
fi
_CLASSPTH=$CARMUSR/lib/java/com.carmensystems.rave.parsers.jar:$CARMUSR/lib/java/antlr-3.1.1.jar
if [ ! -f $CARMUSR/java_src/DocumentRules.class -o $CARMUSR/java_src/DocumentRules.java -nt $CARMUSR/java_src/DocumentRules.class ]; then
   echo "Compiling Java code..."
   javac -cp $_CLASSPTH $CARMUSR/java_src/DocumentRules.java
fi
echo "Running Java code..."
java -cp $_CLASSPTH:$CARMUSR/java_src DocumentRules $CARMUSR > $CARMUSR/data/doc/rules.tex
cd /tmp
echo "Compiling LaTeX..."
pdflatex $CARMUSR/data/doc/rules.tex
pdflatex $CARMUSR/data/doc/rules.tex
mv rules.pdf $CARMUSR/data/doc/
cd -
