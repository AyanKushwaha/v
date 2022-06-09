# This script will start all channels that have MQ interaction
# Need to be run in cms shell
sysmondctl start passive
sysmondctl start crewservices
sysmondctl start flt_execution
sysmondctl start flt_planning
sysmondctl start flt_ownership
sysmondctl start digxml
sysmondctl start crewinfo
sysmondctl start currency
sysmondctl start ldm
sysmondctl start crewnotification_ack
sysmondctl start loadsheet
sysmondctl start baggage
sysmondctl start x1
sysmondctl start x3
sysmondctl start crewnotifications
sysmondctl start meal
