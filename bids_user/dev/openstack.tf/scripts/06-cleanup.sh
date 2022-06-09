#!/usr/bin/env bash
echo '

                  07-cleanup.sh

'

sudo yum autoremove -y -qq        || echo 'oops... cannot yum autoremove'
sudo yum clean all  -y -qq        || echo 'oops... cannot yum clean all'
sudo rm -rf /tmp/* /var/cache/yum || echo 'oops... cannot remote temp files'
