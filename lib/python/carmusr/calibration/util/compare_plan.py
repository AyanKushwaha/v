from __future__ import absolute_import
from six.moves import map
from six.moves import range
from six.moves import zip
from collections import namedtuple, defaultdict
import os
import re

import Cui
import Errlog
from Variable import Variable
import carmensystems.rave.api as rave
from Localization import MSGR, bl_msgr

from carmusr.calibration.mappings import studio_palette
from carmusr.calibration.util import complement
from carmusr.calibration.util import basics
from carmusr.calibration.util import common
from carmusr.calibration.util import calibration_rules


def value2colour(value):
    """
    The value must be hashable
    """
    MAX_RED = 221
    MAX_GREEN = 233
    MAX_BLUE = 253
    MIN_RED = 10
    MIN_GREEN = 30
    MIN_BLUE = 40
    MIN_TOT = 230
    MAX_TOT = 650
    hash_value = int((abs(hash(value)) % 1000000000) * 15.3)
    red = hash_value % (MAX_RED - MIN_RED) + MIN_RED
    max_green = min(MAX_GREEN, MAX_TOT - red - (MIN_BLUE + 5))
    min_green = max(MIN_GREEN, MIN_TOT - red - (MAX_BLUE - 5))
    green_diff = max_green - min_green
    hash_value = hash_value // green_diff
    green = hash_value % green_diff + min_green
    max_blue = min(MAX_BLUE, MAX_TOT - red - green)
    min_blue = max(MIN_BLUE, MIN_TOT - red - green)
    blue_diff = max_blue - min_blue
    hash_value = hash_value // blue_diff
    blue = hash_value % blue_diff + min_blue
    return "#%0.2X%0.2X%0.2X" % (red, green, blue)

# Categories ################################################

IN_OTHER_STR = MSGR("In Other")
IN_OTHER_DESC = MSGR("In Comparison plan on same or different crew position")
NOT_IN_OTHER_STR = MSGR("Not in Other")
NOT_IN_OTHER_DESC = MSGR("Not in Comparison Plan")
UNDEF_STR = MSGR("Illegal")

# rank refers to order of presentation in graphs.
CatProperties = namedtuple("CatProperties", "rank color desc")

CAT_PROPERTIES_NOT_IN_OTHER = CatProperties(100, studio_palette.DarkGrey, NOT_IN_OTHER_DESC)
CAT_PROPERTIES_UNDEF = CatProperties(0, basics.ILLEGAL_COLOUR, UNDEF_STR)
CAT_PROPERTIES_SIMPLE_IN_OTHER = CatProperties(1, studio_palette.JeppesenLightBlue, IN_OTHER_DESC)


class CategoriesHandler(object):
    """
    Calculates and keeps track of categories found,
    and what colour and rank to use for them in reports.
    """

    def __init__(self, comp_plan_slices, cri):
        # comp_plan_slices is a PlanSlice object or None
        self.comp_plan_slices = comp_plan_slices
        self.comp_plan_keys = comp_plan_slices and set(comp_plan_slices.values.keys())
        self.comp_key_var = getattr(cri, calibration_rules.COMP_KEY)
        self.cat_var = cri.cat_var
        self.cat_rank_var = cri.cat_rank_var
        self.cat_color_var = cri.cat_color_var
        self.categories = {}
        self.cat_properties_factory = CatPropertiesFactory()

    def has_categories(self):
        return bool([cat for cat in self.categories if cat != UNDEF_STR])

    def register_not_in_other_category(self):
        if NOT_IN_OTHER_STR not in self.categories:
            self.categories[NOT_IN_OTHER_STR] = CAT_PROPERTIES_NOT_IN_OTHER
        return NOT_IN_OTHER_STR

    def bar_color(self, cat):
        return self.categories[cat].color

    def get_sorted_categories(self):

        def key_f(x):
            # Rank can be any data type in Rave and also void, but the rank for CAT_PROPERTIES_NOT_IN_OTHER is int.
            # We must survive a mix of int, None and another data type also in PY3.
            rank = self.categories[x].rank
            if rank is None:
                rank = 0
            return (isinstance(rank, int), rank)

        return sorted(self.categories, key=key_f)

    def get_and_register_cat(self, bag, tripslice_or_crew_comp):
        # Note: If a comparison plan is considered "tripslice_or_crew_comp" must be an instance of "Slice"
        #       else an int is OK. Performance.
        # Returns: sub_cat_name, sequence of (cat_name, num_crew)
        if self.comp_plan_keys:  # True if a comparison plan is considered
            comp_key, = rave.eval(bag, self.comp_key_var)
            is_in_other = comp_key in self.comp_plan_keys
        else:
            is_in_other = None

        if self.cat_var:
            if is_in_other is None:
                cat = bl_msgr(str(rave.eval(bag, self.cat_var)[0]))
                if cat not in self.categories:
                    self.categories[cat] = self.cat_properties_factory.get(bag,
                                                                           cat,
                                                                           self.cat_rank_var,
                                                                           self.cat_color_var,
                                                                           "")
            elif is_in_other:
                cat_0 = bl_msgr(str(rave.eval(bag, self.cat_var)[0]))
                cat = "{}, {}".format(IN_OTHER_STR, cat_0)
                if cat not in self.categories:
                    self.categories[cat] = self.cat_properties_factory.get(bag,
                                                                           cat,
                                                                           self.cat_rank_var,
                                                                           self.cat_color_var,
                                                                           ", ".join(s for s in (IN_OTHER_DESC, cat_0) if s))
            else:
                cat = self.register_not_in_other_category()
        else:  # category definition is missing for the rule
            if is_in_other is None:  # no comparison plan is considered
                cat = UNDEF_STR
                cat_properties = CAT_PROPERTIES_UNDEF
            elif is_in_other:
                cat = IN_OTHER_STR
                cat_properties = CAT_PROPERTIES_SIMPLE_IN_OTHER
            else:
                cat = NOT_IN_OTHER_STR
                cat_properties = CAT_PROPERTIES_NOT_IN_OTHER
            if cat not in self.categories:
                self.categories[cat] = cat_properties

        if is_in_other is None:
            slice_cat_obj = None
            slice_cat_title = None
        elif is_in_other:
            slice_cat_obj = self.comp_plan_slices.get_compare_category_for(tripslice_or_crew_comp)
            slice_cat_title = slice_cat_obj.title
        else:  # performance - we don't need a SliceCompareCategory object in this case.
            slice_cat_obj = None
            slice_cat_title = SliceCompareCategory.NotInOther.title

        crew_comp = tripslice_or_crew_comp if isinstance(tripslice_or_crew_comp, int) else tripslice_or_crew_comp.complement_sum()

        if isinstance(slice_cat_obj, SliceCompareCategory.PartiallyInOther):
            cat2 = self.register_not_in_other_category()
            missing = slice_cat_obj.num_crew_missing_in_other()
            crew_comp -= missing
            return slice_cat_title, ((cat, crew_comp), (cat2, missing))
        else:
            return slice_cat_title, ((cat, crew_comp),)


class CatPropertiesFactory(object):
    """
    Sets colour and order on category.
    Using color defined in rave or fallback color.
    """

    def get(self, bag, cat_key, rank_var, color_var, desc):

        if rank_var is None:
            rank = cat_key
        else:
            try:
                rank, = rave.eval(bag, rank_var)
            except rave.RaveError as e:
                Errlog.log("CALIBRATION: Warning. Exception raised when calculating category rank using Rave variable '%s'. Default rank will be used."
                           % rank_var.name())
                Errlog.log("CALIBRATION: Exception message: %s" % e)
                rank = cat_key

        if color_var is None:
            color = value2colour(cat_key)
        else:
            try:
                color_str, = rave.eval(bag, color_var)
                if color_str is None:
                    Errlog.log("CALIBRATION: Warning. Category colour was calculated to void for Rave variable '%s'. Default colour will be used."
                               % color_var.name())
            except rave.RaveError as e:
                Errlog.log("CALIBRATION: Warning. Exception raised when calculating category colour using Rave variable '%s'."
                           "Default colour will be used."
                           % color_var.name())
                Errlog.log("CALIBRATION: Exception message: %s" % e)
                color_str = None

            if color_str is None:
                color = value2colour(cat_key)
            elif re.match("^#[a-fA-F0-9]{6}$", color_str):
                color = color_str
            else:
                if hasattr(studio_palette, color_str):
                    color = getattr(studio_palette, color_str)
                else:
                    n = color_var.name()
                    Errlog.log("CALIBRATION: Warning. The specified colour name '%s' from the Rave variable '%s'" % (color_str, n))
                    Errlog.log("CALIBRATION: is not present in the Studio palette and is not an RGB code. Default colour will be used.")
                    color = value2colour(cat_key)

        return CatProperties(rank, color, desc)


# Comparison plan ####################################################################

def bag_is_comparison_plan_bag(bag):
    if not ComparisonPlanHandler.a_plan_is_loaded():
        return False
    for leg in bag.atom_set():
        return leg.studio_calibration_compare.is_comparison_plan_chain()


def get_comparison_plan_bag():
    return rave.context("plan_3_sp_crrs").bag()


class ComparisonPlanHandler(object):

    _saved_lists = {}
    _saved_slices = {}
    saved_other = {}   # Used by externals. Cleared by clear_cached_values_if_needed.

    _saved_rave_keyw = rave.keyw("global_fp_name")
    _saved_comp_raw_plan_path = None
    _saved_comp_plan_change_time = None
    _saved_first_leg_id = None

    def __init__(self, *args, **kw):
        raise NotImplementedError("Not supported")

    @classmethod
    def a_plan_is_loaded(cls):
        return Cui.CuiIsRefPlanLoaded({"WRAPPER": Cui.CUI_WRAPPER_NO_EXCEPTION}, Cui.gpc_info, 3)

    @classmethod
    def get_plan_name(cls, reset_cache_if_needed=True):

        if reset_cache_if_needed:
            cls.clear_cached_values_if_needed()

        raw_path = cls._saved_comp_raw_plan_path
        if not raw_path:
            return None

        to_chop = '/subplan'
        if raw_path.endswith(to_chop):
            comp_path = raw_path[:-len(to_chop)]
        return ' / '.join(comp_path.split('/')[-4:])

    @classmethod
    def collect_slices_from_comparison_plan(cls, comp_key_var, level, use_crew_filter=True):

        if comp_key_var is None:
            return PlanSlices()

        my_get_slice_func = filtered_slice_from_bag if use_crew_filter else unfiltered_slice_from_bag

        key = (comp_key_var.name(), level,
               complement.CrewPosFilter.get_pos_filter_param_value() if use_crew_filter else "*")
        if key not in cls._saved_slices:
            slices = PlanSlices()
            for bag in cls._bags(level):
                slices.add(my_get_slice_func(comp_key_var, bag))
            cls._saved_slices[key] = slices
        return cls._saved_slices[key]

    @classmethod
    def get_keys(cls, comp_key_var, level):

        if not comp_key_var:
            return None
        key = (comp_key_var.name(), level)
        if key not in cls._saved_lists:
            comp_keys = list()
            for bag in cls._bags(level):
                comp_key, = rave.eval(bag, comp_key_var)
                comp_keys.append(comp_key)
            cls._saved_lists[key] = comp_keys
        return cls._saved_lists[key]

    @classmethod
    def _bags(cls, level):
        comp_bag = get_comparison_plan_bag()
        comp_iterator = common.get_atomic_iterator_for_level(comp_bag, level)
        for bag in comp_iterator(where=rave.expr("not hidden")):
            yield(bag)

    @classmethod
    def clear_cached_values_if_needed(cls):
    # Must be called before the class can be used when the comparison plan may have been changed.
        def clear_stored_values():
            cls._saved_lists.clear()
            cls._saved_slices.clear()
            cls.saved_other.clear()

        # Test if new rule set
        try:
            rave.eval(cls._saved_rave_keyw)
        except rave.UsageError:
            clear_stored_values()
            cls._saved_rave_keyw = rave.keyw("global_fp_name")

        # Test if new comparison plan
        new_raw_path, new_first_leg_id = cls._get_comparison_raw_plan_path_and_first_leg_id()
        new_plan_change_time = os.path.getmtime(new_raw_path) if new_raw_path and os.path.exists(new_raw_path) else None
        clear_condition = (new_raw_path != cls._saved_comp_raw_plan_path or
                           new_plan_change_time != cls._saved_comp_plan_change_time or
                           new_first_leg_id != cls._saved_first_leg_id)
        if clear_condition:
            clear_stored_values()
            cls._saved_first_leg_id = new_first_leg_id
            cls._saved_comp_raw_plan_path = new_raw_path
            cls._saved_comp_plan_change_time = new_plan_change_time

    @classmethod
    def _get_comparison_raw_plan_path_and_first_leg_id(cls):
        comp_bag = get_comparison_plan_bag()
        for chain_bag in comp_bag.chain_set():  # This takes time for big plans.
            return rave.eval(chain_bag, rave.keyw("reference_plan_name"), rave.first(rave.Level.atom(), rave.keyw("leg_identifier")))
        return None, None


#
# Slice handling
#

def unfiltered_slice_from_bag(comp_key_expr, bag):
    c = complement.CrewCategories
    res = rave.eval(bag, comp_key_expr, *c.assigned_expressions)
    return Slice(comp_key=res[0], crew_vector=res[1:])


def filtered_slice_from_bag(comp_key_expr, bag):
    comp_key_val, crew_vector = complement.CrewPosFilter.filtered_complement_vector(bag, other_expressions=(comp_key_expr,))
    return Slice(comp_key=comp_key_val[0], crew_vector=crew_vector)


class SliceCompareCategory(object):
    """
    When comparing connections or other sequences defined by keys
    between current and comparison plan,
    these are the categories possible.
    """
    class _Category(object):
        title = "Undefined Compare Category Title"
        desc = "Undefined Compare Category Desc"

        def __init__(self, this_compl, other_compl):
            self.this = this_compl
            self.other = other_compl

        def num_crew_current(self):
            return sum(self.this)

        def num_crew_missing_in_other(self):
            return max(0, sum(self.this) - sum(self.other))

        def __repr__(self):
            return "Slice - " + self.title

    class InOther(_Category):
        title = MSGR('Fully in Other')
        desc = MSGR('In Comparison plan with the same crew complement')

    class NotInOther(_Category):
        title = MSGR('No Common Crew Positions')
        desc = MSGR('Does not have any crew positions in common with Comparison plan')

    class CompositionChanged(_Category):
        title = MSGR('Composition Changed in Other')
        desc = MSGR('In Comparison plan, and has a different crew composition, '
                    'with the same or higher crew count in other.')

    class PartiallyInOther(_Category):
        title = MSGR('Partially Covered in Other')
        desc = MSGR('In Comparison plan, but has less crew in other.')

        def num_missing_in_other(self):
            return sum(max(0, count_this - count_other)
                       for count_this, count_other
                       in zip(self.this, self.other))

        def num_covered_in_both(self):
            return sum(min(count_this, count_other)
                       for count_this, count_other
                       in zip(self.this, self.other))

    @staticmethod
    def all():
        """
        Items in the order in which they should be presented
        """
        return (SliceCompareCategory.NotInOther,
                SliceCompareCategory.InOther,
                SliceCompareCategory.PartiallyInOther,
                SliceCompareCategory.CompositionChanged)


class PlanSlices(object):
    """
    Data object

    values :: {comparison_key: [Slice]}

    Used to collect slices grouped by comparison key,
    and to merge slices into 1 (1/0 + 0/1 -> 1/1)
    """
    def __init__(self):
        self.values = defaultdict(list)

    def add(self, slice_values):
        self.values[slice_values.comp_key].append(slice_values)

    def merge_slices_to_trip(self, slice_list):
        """
        [Slice] -> Slice
        """
        merged_slice = slice_list[0]
        for i in range(1, len(slice_list)):
            merged_slice = merged_slice.slice_union(slice_list[i])
        return merged_slice

    def merged_trip_from_key(self, comparison_key):
        """
        comparison_key -> Slice
        """
        # Use get to avoid implicit insertion.
        slices = self.values.get(comparison_key)
        if not slices:
            return None
        return self.merge_slices_to_trip(slices)

    def get_compare_category_for(self, trip):
        """
        Slice -> SliceCompareCategory

        Documented further in the class SliceCompareCategory
        """
        comparison_key = trip.comp_key
        matching_trip = self.merged_trip_from_key(comparison_key)
        common_trip = trip.slice_intersection(matching_trip)

        this_comp = trip.crew_vector
        other_comp = matching_trip.crew_vector if matching_trip else None

        if common_trip is None:
            compare_cat_class = SliceCompareCategory.NotInOther

        elif common_trip == trip:
            compare_cat_class = SliceCompareCategory.InOther

        elif trip.complement_sum() <= matching_trip.complement_sum():
            compare_cat_class = SliceCompareCategory.CompositionChanged
        else:
            compare_cat_class = SliceCompareCategory.PartiallyInOther

        return compare_cat_class(this_comp, other_comp)


class Slice(object):
    """
    This represents one connection's (or other sequence) slice

    Slices can be merged into bigger slices


    @type comp_key : str
    @type crew_vector : tuple(int)
    """
    def __init__(self, comp_key, crew_vector):
        self.comp_key = comp_key
        self.crew_vector = crew_vector

    def slice_intersection(self, other):
        if other is None or not self.comp_key == other.comp_key:
            return None
        common_vector = tuple(map(min, zip(self.crew_vector, other.crew_vector)))
        if not any(common_vector):
            # No positions in common
            return None
        return Slice(comp_key=self.comp_key, crew_vector=common_vector)

    def slice_union(self, other):
        common_vector = tuple(map(sum, zip(self.crew_vector, other.crew_vector)))
        return Slice(comp_key=self.comp_key, crew_vector=common_vector)

    def complement_sum(self):
        return sum(self.crew_vector)

    def __eq__(self, other):
        return self.comp_key == other.comp_key and self.crew_vector == other.crew_vector

    __hash__ = None

    def __str__(self):
        return 'Slice key:"{0}", vector:{1}'.format(self.comp_key, self.crew_vector)

    def __repr__(self):
        return self.__str__()
