# This script will stop all DIG channels with MQ interaction
# Need to be run in cms-shell
sysmondctl stop passive
sysmondctl stop crewservices
sysmondctl stop flt_execution
sysmondctl stop flt_planning
sysmondctl stop flt_ownership
sysmondctl stop digxml
sysmondctl stop crewinfo
sysmondctl stop currency
sysmondctl stop ldm
sysmondctl stop crewnotification_ack
sysmondctl stop loadsheet
sysmondctl stop baggage
sysmondctl stop x1
sysmondctl stop x3
sysmondctl stop crewnotifications
sysmondctl stop meal
