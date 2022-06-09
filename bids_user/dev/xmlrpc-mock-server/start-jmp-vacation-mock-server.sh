#!/bin/bash

set -e

JAR=target/xmlrpc-mock-server-all.jar
PORT=24054
NAME=jmp-vacation
BACKEND=ReportServer
BACKEND_PORT="${NAME}-${BACKEND}-${PORT}"
CACHE_PATH=data/$NAME
STDOUT=logs/${BACKEND_PORT}.stdout
STDERR=logs/${BACKEND_PORT}.stderr
PID_FILE=logs/${BACKEND_PORT}.pid

if [ ! -d logs ] ; then 
	mkdir logs
fi

echo "Starting server $NAME ($BACKEND XMLRPCMockServer) on port $PORT, reading data from $CACHE_PATH"
java -jar $JAR -port $PORT -cachePath $CACHE_PATH -backend $BACKEND 2> $STDERR > $STDOUT &
PID=$!

head $STDOUT
echo $PID > $PID_FILE
echo "PID: $PID saved in $PID_FILE"
