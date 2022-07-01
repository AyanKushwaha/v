from itertools import compress
import re

import carmensystems.rave.api as rave

from carmusr.calibration.util import config_per_product


# This function must be called before anything in this module can be
# used and after (re)load of rule-set or change of the filter parameter.
# It returns an error text if something is wrong (typically the value of the filter parameter).
def refresh_and_get_error_message_if_something_is_wrong():
    try:
        CrewCategories._refresh_if_needed()
        CrewPosFilter._refresh()
        return None
    except Exception as e:
        return str(e)


class CrewCategories(object):
    """
    Methods on defined crew categories
    """
    saved_rave_keyw = "This is not a keyword"

    def __init__(self, *args, **kw):
        raise NotImplementedError("Not supported")

    @classmethod
    def _refresh_if_needed(cls):
        try:
            rave.eval(cls.saved_rave_keyw)  # raises exception if the rule set has been changed or reloaded.
        except rave.RaveError:
            cls.saved_rave_keyw = rave.keyw("global_fp_name")
            cls.num_positions = rave.eval('calibration_mappings.%no_of_positions%')[0]
            cls.vector_all = [1] * cls.num_positions
            _pos_code_expressions = ['calibration_mappings.%pos_code%({})'.format(i) for i in range(1, cls.num_positions + 1)]
            cls.all_category_codes = rave.eval(*_pos_code_expressions)
            cls.assigned_expressions = tuple(rave.first(rave.Level.atom(),
                                                        rave.keyw("assigned_crew_position_{}".format(i)))
                                             for i in range(1, cls.num_positions + 1))

    @classmethod
    def ccode2pos(cls, pos_code):
        return cls.all_category_codes.index(pos_code) + 1

    @classmethod
    def mask_from_pos_comma_sep(cls, pos_comma_sep):
        # Raises ValueError
        # * or empty means all.
        if pos_comma_sep in ('*', ''):
            return cls.vector_all

        unknown_codes = []
        pos_used = []
        # Accept both ',' and space as separators
        for pos_code in filter(None, re.split('[, ]+', pos_comma_sep)):
            try:
                # positions start on 0
                pos_used.append(cls.ccode2pos(pos_code))
            except ValueError:
                unknown_codes.append(pos_code)
        if unknown_codes:
            msg = 'Unknown positions "{}". Known positions are "{}" or *'
            msg = msg.format(', '.join(unknown_codes),
                             ', '.join(cls.all_category_codes))
            raise ValueError(msg)
        pos_mask = [pos in pos_used for pos in range(1, cls.num_positions + 1)]
        return pos_mask


class CrewPosFilter(object):
    """
    When counting complement, we can limit what positions are considered.
    This class uses the rave parameter to calculated filtered complements.
    Values are cached.
    If the product attribute "allow_pos_filtering" is set to False the
    Rave parameter is ignored and the value "*" is used.
    """
    rave_param_name = 'report_calibration.crew_pos_filter_p'
    _pos_filter_str = None  # e.g. "*" or "CP,FO"
    _pos_filter_mask = None  # e.g [1,1,0,0,0,0,0,0,0]
    _saved_assigned_expression_0 = None

    def __init__(self, *args, **kw):
        raise NotImplementedError("Not supported")

    @classmethod
    def filtered_complement_sum(cls, bag):
        return sum(rave.eval(bag, *cls._filtered_assigned_expressions))

    @classmethod
    def filtered_complement_vector(cls, bag, other_expressions=()):
        assert type(other_expressions) == tuple
        expressions = other_expressions + cls._filtered_assigned_expressions
        values = rave.eval(bag, *expressions)
        num_other = len(other_expressions)

        return values[:num_other], values[num_other:]

    @classmethod
    def get_pos_filter_mask(cls):
        return cls._pos_filter_mask

    @classmethod
    def get_pos_filter_param_value(cls):
        if cls.pconfig_allow_pos_filtering:
            return rave.param(cls.rave_param_name).getValue()
        else:
            return "*"

    @classmethod
    def get_pos_filter_param_remark(cls):
        if cls.pconfig_allow_pos_filtering:
            return rave.param(cls.rave_param_name).getBriefRemark()
        else:
            return None

    @classmethod
    def _refresh(cls):
        cls.pconfig_allow_pos_filtering = config_per_product.get_config_for_active_product().allow_pos_filtering
        param_changed = False
        val = cls.get_pos_filter_param_value()
        if val != cls._pos_filter_str:
            cls._pos_filter_mask = CrewCategories.mask_from_pos_comma_sep(val)  # We get an exception if the parameter is incorrect
            cls._pos_filter_str = val
            param_changed = True
        if param_changed or not (CrewCategories.assigned_expressions[0] is cls._saved_assigned_expression_0):
            cls._saved_assigned_expression_0 = CrewCategories.assigned_expressions[0]
            cls._filtered_assigned_expressions = tuple(compress(CrewCategories.assigned_expressions, cls._pos_filter_mask))
