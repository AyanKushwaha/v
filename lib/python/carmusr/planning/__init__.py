import Cui

def set_planning_period(pp_start, pp_end):
    Cui.CuiCrcSetParameterFromString("fundamental.start_para", str(pp_start))
    Cui.CuiCrcSetParameterFromString("fundamental.end_para", str(pp_end))
