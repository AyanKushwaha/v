#!/bin/bash

# gather errors/fatals from active containers and save them to files: test_<container name>.log
rm -fr logs ; mkdir logs ; cd logs ;
export ERROR_FILTER='.*(ERROR|FATAL|ORA-|[E|e]rror:|CRITICAL|CRASH).{1,500}' ;
for name in $(docker ps -a --format "{{.Names}}") ; do
  export LOG_FILE="test_$name.log" ;
  docker logs $name 2>/dev/null | sed "s/^.\{1,10\}[0-9]\+m//" > $LOG_FILE ;
  export COUNT=$(cat $LOG_FILE | grep -oE $ERROR_FILTER | grep -cE '.*') ;
  if [ $COUNT -ge 1 ] ; then
    echo "$name contains $COUNT error/s. The last 5 errors are shown." ;
    grep -oE $ERROR_FILTER < $LOG_FILE | tail --lines=5 ;
    echo '----------------------------------------------------------------------------------------' ;
  fi ;
done
echo 'List of saved logs from containers:'
for file in $(ls --format=single-column); do echo "$(pwd)/$file" ; done
cd ..
