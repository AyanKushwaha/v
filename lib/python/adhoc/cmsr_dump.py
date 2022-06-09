#! /usr/bin/env python

import report_sources.report_server.rs_bt_dt_stat
import os
##  this directory should contain .dtbt and .cid 
##  .dtbt the date of last calculation usually yesterday date like cat .dtbt =>  20191114
##  .cid  the last commit id that previous run included like cat .cid =>  152906316

directory = "/tmp/datadump"
if not os.path.exists(directory):
    os.makedirs(directory)

report_sources.report_server.rs_bt_dt_stat.generate(directory)

print "$$$$$$$$$$$$$$$$$$$$$$ done and exit!!!"

import utils.datadump as cmsrdmp

schema = os.getenv('DB_SCHEMA','sk_nov_live')
connect = os.getenv('DB_URL','oracle:sk_nov_live/sk_nov_live@cmsdb01:1521/CMSDEV')

cmsrdmp.run(schema=schema, connect=connect, dir=directory)

print "$$$$$$$$$$$$$$$$$$$$$$CMSR dump is done and exit!!!"

exit(0)
