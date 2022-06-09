#!/bin/bash
echo 'must be run as root'

# 26214400 = 25 MB
echo 'net.core.wmem_max=26214400' >> /etc/sysctl.conf
echo 'net.core.rmem_max=26214400' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_rmem= 10240 87380 26214400' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_wmem= 10240 87380 26214400' >> /etc/sysctl.conf
