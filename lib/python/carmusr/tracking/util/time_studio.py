import carmensystems.rave.api as rave
from AbsTime import AbsTime


def set_now(abstime_str=None):
        if not abstime_str:
            rave.param("fundamental.%use_now_debug%").setvalue(False)
            return
        rave.param("fundamental.%use_now_debug%").setvalue(True)
        rave.param("fundamental.%now_debug%").setvalue(AbsTime(abstime_str))
        now = rave.eval("fundamental.%now%")[0]
        print "  ## %now% (after set manipulate_now):", now
        return now


def get_now():
    return rave.eval("fundamental.%now%")[0]


