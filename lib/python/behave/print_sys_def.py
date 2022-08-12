# Carm variables need to be set for the tests to work properly
import os

def main(as_main=False, args=None):
    ret = []
    carmusr = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
    ret.append('os.environ["CARMSYSTEM"]="%s"' % carmusr)
    ret.append('os.environ["CARMSYSTEMROOT"]="%s"' % carmusr)
    ret.append('os.environ["CARMSYS"]="%s/carmsys"' % carmusr)
    ret.append('os.environ["CARMUSR"]="%s"' % carmusr)
    ret.append('os.environ["CARMDATA"]="%s/carmdata_behave"' % carmusr)
    ret.append('os.environ["CARMTMP"]="%s/carmtmp_behave"' % carmusr)

    return ret
