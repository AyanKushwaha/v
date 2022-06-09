#!/usr/bin/env bash
echo '

                  02-install-software.sh

'

sudo yum install -q -y epel-release
sudo yum check-updates -q -y
sudo yum install -q -y tree curl which wget bash java-1.8.0-openjdk-devel

echo 'export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk' | sudo tee --append /etc/profile.d/crew-buddies-05-java-home.sh
echo 'export PATH=$JAVA_HOME/bin:$PATH'                 | sudo tee --append /etc/profile.d/crew-buddies-06-java-bin.sh
