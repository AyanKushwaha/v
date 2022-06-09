
# Starting standalone applications from the launcher bar may need some modules
# to be imported. This is the file to do it in.
# Taken from Finair.
import carmusr.crewinfo.CrewInfo
import carmusr.CrewBlockHours
import carmusr.CrewTraining
import meal.MealOrderFormHandler
import salary.mmi
import carmusr.tracking.handover_report

print "StartingMiradorModelserver..."
import carmensystems.mirador.tablemanager
