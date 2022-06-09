import Cui
import carmstd.studio.area as StdArea
from carmstd import bag_handler
import carmensystems.rave.api as rave

def find_bid_trips():
    _find_trips('crew.%id%', 'bid.%filter_crew_id_override_p%', 'bid.%trip_grants_any%')
    return

def find_lifestyle_trips():
    _find_trips('crew.%homeairport%', 'lifestyle.%filter_crew_homeairport_override_p%', 'lifestyle.%filter_trip_satisfied%')
    return

def _find_trips(crew_override_p_value_name, crew_override_p_name, filter_trip_satisfied):
    crew_area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    opposit_area = StdArea.getOppositArea(crew_area)

    bag_wrapper = bag_handler.CurrentChain()
    bag = bag_wrapper.bag

    crew_id = rave.eval(bag, 'crew.%id%')[0]

    crew_bid_id_override_p = rave.param('bid.%filter_crew_id_override_p%')
    crew_bid_id_override_p.setvalue(crew_id)

    crew_value = rave.eval(bag, crew_override_p_value_name)[0]

    crew_override_p = rave.param(crew_override_p_name)
    crew_override_p.setvalue(crew_value)
    crew_rank = rave.eval(bag, 'crew.%rank_not_void%')[0]

    crew_comp_string = crew_comp(crew_rank)

    byp_crew = {'FORM': 'form_crew_filter',
                'FL_TIME_BASE': 'UDOP',
                'FILTER_PRINCIP': 'ANY',
                'FILTER_METHOD': 'REPLACE',
                'FILTER_MARK': 'NONE',
                'FCREW_ID': '%s' % crew_id,
                'OK': '',
                }

    byp_crr = {'FORM': 'form_crr_filter',
               'FL_TIME_BASE': 'UDOP',
               'FILTER_PRINCIP': 'ANY',
               'FILTER_METHOD': 'REPLACE',
               'FILTER_MARK': 'NONE',
               crew_comp_string : '>0',
               'CRC_VARIABLE_0': filter_trip_satisfied,
               'CRC_VALUE_0': 'T',
               'OK': '',
               }

    byp_crr_default = {'FORM': 'form_crr_filter',
                       'FL_TIME_BASE': 'UDOP',
                       'FILTER_PRINCIP': 'ANY',
                       'FILTER_METHOD': 'REPLACE',
                       'FILTER_MARK': 'NONE',
                       'DEFAULT' : '',
                       'OK': '',
                       }

    if Cui.CuiAreaExists({"WRAPPER": Cui.CUI_WRAPPER_NO_EXCEPTION},Cui.gpc_info, opposit_area):
        Cui.CuiOpenArea(Cui.gpc_info, 0)

    Cui.CuiFilterObjects(byp_crew, Cui.gpc_info, crew_area, 'CrewFilter', 0, 0)
    Cui.CuiDisplayFilteredObjects(byp_crr_default, Cui.gpc_info,opposit_area, Cui.CrrMode,"trip_in_planning_area.sel",1)
    Cui.CuiFilterObjects(byp_crr_default, Cui.gpc_info, opposit_area, 'CrrFilter', 0, 0)
    Cui.CuiFilterObjects(byp_crr, Cui.gpc_info, opposit_area, 'CrrFilter', 0, 0)

    #crew_cat = rave.eval(bag, 'crew.%%maincat_for_rank%%("%s")' % crew_rank)[0]
    #Cui.CuiFindAssignableCrr(Cui.gpc_info, crew_cat, crew_rank, 'WINDOW')

    crew_override_p.setvalue("")
    crew_bid_id_override_p.setvalue("")

def crew_comp(rank):

    data = {'FC': 'FC_DATA_CC_0',
            'FP': 'FC_DATA_CC_1',
            'FR': 'FC_DATA_CC_2',
            'FU': 'FC_DATA_CC_3',
            'AP': 'FC_DATA_CC_4',
            'AS': 'FC_DATA_CC_5',
            'AH': 'FC_DATA_CC_6',
            'AU': 'FC_DATA_CC_7',
            'TL': 'FC_DATA_CC_8',
            'TR': 'FC_DATA_CC_9',
            }

    return data.get(rank)
