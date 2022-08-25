"""
Basic stuff for Calibration.
"""


from __future__ import absolute_import
from __future__ import division
from functools import reduce
import six
import math
import os

import carmensystems.basics.l10n.utilities as l10n_util
import carmensystems.studio.cpmbuffer as cpmb
from jcms.calibration import plan
import carmensystems.rave.api as rave
from RelTime import RelTime
from AbsTime import AbsTime
from Localization import MSGR

from carmusr.calibration.mappings import studio_palette as sp


# Colours ##########################################################################

HEATMAP_RED = "#CC6677"
HEATMAP_BLUE = "#4477AA"

ILLEGAL_COLOUR = HEATMAP_RED
IN_FIRST_BIN_COLOUR = sp.LightRed
OUTSIDE_FIRST_BIN_COLOUR = "#CFDDEF"

# Labels ###########################################################################

IN_FIRST_BIN_LABEL = MSGR("In 1st bin")
OUTSIDE_FIRST_BIN_LABEL = MSGR("Outside 1st bin")

# Math #############################################################################

PERC_FMT = "%.1f%%"

PERC_1DEC_FORMAT = "{:.1f}%"


def percentile(a, q):
    """
    Takes iterable a of data, and iterable q of percentile values [0.0 - 100.0].
    Returns the qth percentile of the array elements.
    Just as with numpy.percentile, the interpolation does not work with RelTime.
    """
    sa = sorted(a)
    float_ixs = [(len(a) - 1) * qv / 100 for qv in q]
    res = []
    for f_ix in float_ixs:
        ix1 = int(math.floor(f_ix))
        ix2 = int(math.ceil(f_ix))
        w1 = ix2 - f_ix
        w2 = 1 - w1
        res.append(w1 * sa[ix1] + w2 * sa[ix2])
    return res


def mean(sequence):
    # The start argument to sum () is needed for RelTime.
    # Float in the denominator is needed to get adequate rounding for RelTime.
    return sum(sequence, type(sequence[0])(0)) / float(len(sequence))


def round_to_int(v):
    """
    Used instead of 'int(round(v))' to get the same behaviour in python2 and python3.
    """
    return int(v + (0.5 if v > 0 else -0.5))


def percentage_value(numerator, denominator):
    if denominator == 0:
        ratio = 0.0
    else:
        ratio = 100 * numerator / denominator
    return ratio


def percentage_string(number, total):
    percentage = percentage_value(number, total)
    return PERC_1DEC_FORMAT.format(percentage)


def ratio_str(numerator, denominator):
    return PERC_FMT % percentage_value(numerator, denominator)


# Python2to3

def encode_if_py2(unicode_str):
    if six.PY2:
        return l10n_util.encode(unicode_str)
    return unicode_str


# Python

def deep_getattr(obj, attr):
    return reduce(getattr, attr.split("."), obj)


# Rave ##

def is_reltime_rave_expression(expr):
    try:
        rave.expr("(%s) + 01JAN2020" % expr)
        return True
    except rave.RaveError:
        return False


def is_integer_rave_expression(expr):
    try:
        rave.expr("(%s) + 1" % expr)
        return True
    except rave.RaveError:
        return False


def is_boolean_rave_expression(expr):
    try:
        rave.expr("(%s) and true" % expr)
        return True
    except rave.RaveError:
        return False


def is_abstime_rave_expression(expr):
    try:
        rave.expr("(%s) - 01JAN2020" % expr)
        return True
    except rave.RaveError:
        return False


def get_type_of_rave_expression(expr):
    if is_reltime_rave_expression(expr):
        return RelTime
    if is_integer_rave_expression(expr):
        return int
    if is_boolean_rave_expression(expr):
        return bool
    if is_abstime_rave_expression(expr):
        return AbsTime
    return str


# RelTime ##

ONE_DAY = RelTime(1440)
ONE_MINUTE = RelTime(1)


## Path string

def get_nice_looking_path(path):
    res = path.replace(os.getenv("CARMUSR"), "$CARMUSR")
    if plan.sub_plan_is_loaded():
        res = res.replace(get_sp_local_etab_dir(), "$SP_ETAB_DIR")
    return res


## Plan

def no_or_empty_local_plan():
    buf = cpmb.CpmBuffer(cpmb.LOCAL_PLAN_CFC)
    return buf.isEmpty()

'''
Copied from NiceToHaveIQ.

Functions to get the full path to the etable directories with plan tables.
The code works both in Studio and in the optimisers.
If no plan is loaded or if the functions are used in a Python environment
where the Rave API isn't possible to use an exception is raised.

Note: The directory above SpLocal/LpLocal is provided.
'''


def get_sp_local_etab_dir():
    return _common(True)


def get_lp_local_etab_dir():
    return _common(False)


def _common(sp=True):
    try:
        import carmensystems.rave.api  # @UnusedImport
    except ImportError:
        raise Exception("Only supported if the Rave API is supported")

    try:
        import Cui
        from Variable import Variable
        from __main__ import exception as StudioError
        try:
            buf = Variable()
            _f = Cui.CuiGetSubPlanEtabLocalPath if sp else Cui.CuiGetLocalPlanEtabLocalPath
            _f(Cui.gpc_info, buf)
            return os.path.dirname(buf.value)
        except StudioError:
            raise Exception("No %s loaded" % ("sub-plan" if sp else "local plan"))
    except ImportError:  # Probably in an optimiser
        env_var = "SP_ETAB_DIR" if sp else "LP_ETAB_DIR"
        try:
            return os.environ[env_var]
        except KeyError:
            raise Exception("Unexpected error. Environment variable %s not defined." % env_var)
