
import Cui
import Variable
import carmusr.HelperFunctions as helpers


def get_leg_object():
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    current_leg = Variable.Variable("")
    Cui.CuiGetSelectionObject(Cui.gpc_info, area, Cui.LegMode, current_leg)
    leg_id = current_leg.value
    return helpers.LegObject(leg_id, area)