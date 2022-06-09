#!/usr/bin/env bash
echo '

                  04-crewportal-application.sh(prepare-application-to-run-in-docker)

'

echo 'Running applications in docker container...'
cd /tmp/

echo "Starting oracle, xmlrpc..."
sudo docker-compose up -d oracle xmlrpc
sudo docker-compose logs -f -t &

echo "Starting jboss app..."
sudo docker-compose up -d jboss
