#!/usr/bin/env bash
echo '

                  01-install-update.sh

'

echo "127.0.0.1 localhost $(cat /etc/hostname)" | sudo tee /etc/hosts

sudo yum check-updates -y -q
sudo yum update -y -q --security
