#!/bin/bash
# Clean up script to remove containers, project images and untagged images.'
# Input arguments:
# $1 - profile to apply

echo "Remove project containers and images" ;
./mvnw ${MAVEN_CLI_OPTS} -q -f dev/docker -P $1 ;
echo "Remove other containers"
for i in $(docker ps -aq) ; do docker rm -fv $i ; done
echo "Remove untagged images"
for j in $(docker images -q -f "dangling=true"); do docker rmi -f $j ; done
