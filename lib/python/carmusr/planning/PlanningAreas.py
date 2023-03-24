############################################################
#

#
############################################################
__version__ = "$Revision$"
"""
PlanningAreas.py
Module for doing:
Module containing the available planning area definitions
Filter definitions (incomplete)
 1. trip_area_planning
    Params area_planning_group and area_qual, maps to trip.area in model
    6 char string in format MAINCAT+REGION+ACQUAL, e.g. FSKS38.
    Selecting F and SKS should load all Flightdeck SKS trips, hence
    filter is area_planning_group=FSKS and area_qual = FSKS__ (like-operator used in filter)
    No area_qual filter for cabin, since there are to many cominations (e.g. A2+90)
    EG 090422: Qual removed from filtering due to problems caused by trafic changes.
@date: 01jul2008
@author: Jonas Carlsson
@org: Jeppesen Systems AB
"""

DB_ALL_ANY_CHARS = '%' #Replaces DB_ALL_3_CHARS. JIRA SKCMS-660
DB_ALL_1_CHAR = '_'

def create_filters(filter_dict):
    try:
        maincat = filter_dict['maincat'].upper()
        planning_group = filter_dict['planning_group'].upper()
        quals = filter_dict['quals'].upper()
        area_planning_group = filter_dict['area_planning_group'].upper()
        area_qual = filter_dict['area_qual'].upper()
    except KeyError:
        raise Exception('carmusr.planning.PlanningAreas::create_filters: '+\
                        'Malformed filter defs (%s)'%str(filter_dict))
    ret = []
    # Add time period to needed filters
    try:
        #ACTIVE
        ret.append(("crew_user_filter_active","start","%start"))
        ret.append(("crew_user_filter_active","end","%end"))

        #EMPLOYMENT
        if maincat != 'ALL' or planning_group != 'ALL':
            if planning_group == 'ALL':
                planning_group = DB_ALL_ANY_CHARS 
            if maincat == 'ALL':
                maincat = DB_ALL_1_CHAR
            empl = maincat+'|'+planning_group
            ret.append(("crew_user_filter_employment","start","%start"))
            ret.append(("crew_user_filter_employment","end","%end"))
            ret.append(("crew_user_filter_employment", "rank_planning_group",empl))
        #ACQUALS
        if quals != 'ALL':
            quals = quals.split('|')
            quals.sort()
            quals = '|'.join(quals) #Filter depends on sort
            ret.append(("crew_user_filter_quals","start","%start"))
            ret.append(("crew_user_filter_quals","end","%end"))
            ret.append(("crew_user_filter_quals", "quals",quals))
    except KeyError:
        raise Exception('carmusr.planning.PlanningAreas::create_filters: '+\
                        'Malformed filter defs (%s)'%str(filter_dict))                      
    
    ret.append(("trip_area_planning","area_planning_group",area_planning_group))
    ret.append(("trip_area_planning","area_qual",area_qual))
    
    return ret

# First element in tuple is filter settings, second is rave settings.
planning_areas = {
                    "ALL_SK":({'maincat':'ALL',
                          'planning_group':'SK_',
                          'quals':'ALL',
                          "area_planning_group":"%",
                          "area_qual":"______"},{}),
                    
                    "ALL_SVS":({'maincat':'ALL',
                          'planning_group':'SVS',
                          'quals':'ALL',
                          "area_planning_group":"%",
                          "area_qual":"______"},
                          {"planning_area.planning_area_crew_planning_group_p":"SVS_PG",
                           "planning_area.planning_area_trip_planning_group_p":"SVS_PG",
                           "planning_area.planning_area_leg_ac_planning_group_p":"SVS_PG"}),

# Add when go live for SZS (SAS Connect) into CMS                             
#                       "ALL_SZS":({'maincat':'ALL',
#                                'planning_group':'SZS',
#                                'quals':'ALL',
#                                "area_planning_group":"%",
#                                "area_qual":"______"},
#                               {"planning_area.planning_area_crew_planning_group_p":"SZS_PG",
#                                "planning_area.planning_area_trip_planning_group_p":"SZS_PG",
#                                "planning_area.planning_area_leg_ac_planning_group_p":"SZS_PG"}),  
            
                    "ALL_CC_SK":({'maincat':'C',
                             'planning_group':'SK_',
                             'quals':'ALL',
                             "area_planning_group":"C%",
                             "area_qual":"C_____"},
                            {"planning_area.planning_area_crew_category_p":"CC_CAT",
                             "planning_area.planning_area_trip_category_p":"CC_CAT"}),

                    "ALL_FD_SK":({'maincat':'F',
                             'planning_group':'SK_',
                             'quals':'ALL',
                             "area_planning_group":"F%",
                             "area_qual":"F_____"},
                            {"planning_area.planning_area_crew_category_p":"FD_CAT",
                             "planning_area.planning_area_trip_category_p":"FD_CAT"}),
                
# Added in Nov2021. SVS is a part of SAS
                             
                  "CC_SVS":({'maincat':'C',
                             'planning_group':'SVS',
                             'quals':'ALL',
                             "area_planning_group":"C%",
                             "area_qual":"C_____"},
                            {"planning_area.planning_area_crew_category_p":"CC_CAT",
                             "planning_area.planning_area_trip_category_p":"CC_CAT",
                             "planning_area.planning_area_crew_planning_group_p":"SVS_PG",
                             "planning_area.planning_area_trip_planning_group_p":"SVS_PG",
                             "planning_area.planning_area_leg_ac_planning_group_p":"SVS_PG"}),


# Add when go live for SZS (SAS Connect) into CMS                             
#                 "CC_SZS":({'maincat':'C',
#                                'planning_group':'SZS',
#                                'quals':'ALL',
#                                "area_planning_group":"C%",
#                                "area_qual":"C_____"},
#                               {"planning_area.planning_area_crew_category_p":"CC_CAT",
#                                "planning_area.planning_area_trip_category_p":"CC_CAT",
#                                "planning_area.planning_area_crew_planning_group_p":"SZS_PG",
#                                "planning_area.planning_area_trip_planning_group_p":"SZS_PG",
#                                "planning_area.planning_area_leg_ac_planning_group_p":"SZS_PG"}),  
                            
                  "CC_SKD":({'maincat':'C',
                             'planning_group':'SKD',
                             'quals':'ALL',
                             "area_planning_group":"C%",
                             "area_qual":"C_____"},
                            {"planning_area.planning_area_crew_category_p":"CC_CAT",
                             "planning_area.planning_area_trip_category_p":"CC_CAT",
                             "planning_area.planning_area_crew_planning_group_p":"SKD_PG",
                             "planning_area.planning_area_trip_planning_group_p":"SKD_PG",
                             "planning_area.planning_area_leg_ac_planning_group_p":"SKD_PG"}),                             
                             
                  "CC_SKN":({'maincat':'C',
                             'planning_group':'SKN',
                             'quals':'ALL',
                             "area_planning_group":"C%",
                             "area_qual":"C_____"},
                            {"planning_area.planning_area_crew_category_p":"CC_CAT",
                             "planning_area.planning_area_trip_category_p":"CC_CAT",
                             "planning_area.planning_area_crew_planning_group_p":"SKN_PG",
                             "planning_area.planning_area_trip_planning_group_p":"SKN_PG",
                             "planning_area.planning_area_leg_ac_planning_group_p":"SKN_PG"}),
                
                  "CC_SKS":({'maincat':'C',
                             'planning_group':'SKS',
                             'quals':'ALL',
                             "area_planning_group":"C%",
                             "area_qual":"C_____"},
                            {"planning_area.planning_area_crew_category_p":"CC_CAT",
                             "planning_area.planning_area_trip_category_p":"CC_CAT",
                             "planning_area.planning_area_crew_planning_group_p":"SKS_PG",
                             "planning_area.planning_area_trip_planning_group_p":"SKS_PG",
                             "planning_area.planning_area_leg_ac_planning_group_p":"SKS_PG"}),
                  
                        
                  "CC_AL":({'maincat':'C',
                             'planning_group':'ALL',
                             'quals':'AL',
                             "area_planning_group":"C%",
                             "area_qual":"C_____"},
                           {"planning_area.planning_area_crew_category_p":"CC_CAT",
                            "planning_area.planning_area_trip_category_p":"CC_CAT",
                            "planning_area.planning_area_trip_planning_group_p":"ANY_PG",
                            "planning_area.planning_area_leg_ac_planning_group_p":"ANY_PG",
                            "planning_area.planning_area_crew_qualification_p":"AL_QUAL",
                            "planning_area.planning_area_trip_ac_fam_p":"A330_350_FAM",
                            "planning_area.planning_area_leg_ac_fam_p":"A330_350_FAM"}),
                  
                  "CC_ASIA":({'maincat':'C',
                             'planning_group':'SKI',
                             'quals':'ALL',
                             "area_planning_group":"C%",
                             "area_qual":"C_____"},
                             {"planning_area.planning_area_crew_category_p":"CC_CAT",
                              "planning_area.planning_area_trip_category_p":"CC_CAT",
                              "planning_area.planning_area_crew_planning_group_p":"SKI_PG",
                              "planning_area.planning_area_trip_planning_group_p":"SKI_PG",
                              "planning_area.planning_area_leg_ac_planning_group_p":"SKI_PG",
                              #"planning_area.planning_area_crew_qualification_p":"AL_QUAL",
                              "planning_area.planning_area_trip_ac_fam_p":"A330_350_FAM",
                              "planning_area.planning_area_leg_ac_fam_p":"A330_350_FAM"}),

                  "CC_JAPAN":({'maincat':'C',
                             'planning_group':'SKJ',
                             'quals':'ALL',
                             "area_planning_group":"C%",
                             "area_qual":"C_____"},
                             {"planning_area.planning_area_crew_category_p":"CC_CAT",
                              "planning_area.planning_area_trip_category_p":"CC_CAT",
                              "planning_area.planning_area_crew_planning_group_p":"SKJ_PG",
                              "planning_area.planning_area_trip_planning_group_p":"SKJ_PG",
                              "planning_area.planning_area_leg_ac_planning_group_p":"SKJ_PG",
                              #"planning_area.planning_area_crew_qualification_p":"AL_QUAL",
                              "planning_area.planning_area_trip_ac_fam_p":"A330_350_FAM",
                              "planning_area.planning_area_leg_ac_fam_p":"A330_350_FAM"}),
                  
                  "CC_CHINA":({'maincat':'C',
                             'planning_group':'SKK',
                             'quals':'ALL',
                             "area_planning_group":"C%",
                             "area_qual":"C_____"},
                             {"planning_area.planning_area_crew_category_p":"CC_CAT",
                              "planning_area.planning_area_trip_category_p":"CC_CAT",
                              "planning_area.planning_area_crew_planning_group_p":"SKK_PG",
                              "planning_area.planning_area_trip_planning_group_p":"SKK_PG",
                              "planning_area.planning_area_leg_ac_planning_group_p":"SKK_PG",
                              #"planning_area.planning_area_crew_qualification_p":"AL_QUAL",
                              "planning_area.planning_area_trip_ac_fam_p":"A330_350_FAM",
                              "planning_area.planning_area_leg_ac_fam_p":"A330_350_FAM"}),
                  
# Added Nov 2021. SVS is a part of SAS                              
                  "FD_SVS":({'maincat':'F',
                                'planning_group':'SVS',
                                'quals':'ALL',
                                "area_planning_group":"F%",
                                "area_qual":"F_____"},
                               {"planning_area.planning_area_crew_category_p":"FD_CAT",
                                "planning_area.planning_area_trip_category_p":"FD_CAT",
                                "planning_area.planning_area_crew_planning_group_p":"SVS_PG",
                                "planning_area.planning_area_trip_planning_group_p":"SVS_PG",
                                "planning_area.planning_area_leg_ac_planning_group_p":"SVS_PG"}),                              

# Add when go live for SZS (SAS Connect) into CMS                             
#                 "FD_SZS":({'maincat':'F',
#                                'planning_group':'SZS',
#                                'quals':'ALL',
#                                "area_planning_group":"F%",
#                                "area_qual":"F_____"},
#                               {"planning_area.planning_area_crew_category_p":"FD_CAT",
#                                "planning_area.planning_area_trip_category_p":"FD_CAT",
#                                "planning_area.planning_area_crew_planning_group_p":"SZS_PG",
#                                "planning_area.planning_area_trip_planning_group_p":"SZS_PG",
#                                "planning_area.planning_area_leg_ac_planning_group_p":"SZS_PG"}),  
                                
                  "FD_SKI":({'maincat':'F',
                             'planning_group':'SKI',
                             'quals':'ALL',
                             "area_planning_group":"F%",
                             "area_qual":"F_____"},
                            {"planning_area.planning_area_crew_category_p":"FD_CAT",
                             "planning_area.planning_area_trip_category_p":"FD_CAT",
                             "planning_area.planning_area_crew_planning_group_p":"SKI_PG",
                             "planning_area.planning_area_trip_planning_group_p":"SKI_PG",
                             "planning_area.planning_area_leg_ac_planning_group_p":"SKI_PG",
                             "planning_area.planning_area_trip_ac_fam_p":"A330_350_FAM",
                             "planning_area.planning_area_leg_ac_fam_p":"A330_350_FAM"}),

                   "FD_B737":({'maincat':'F',
                             'quals':'37|38',
                             'planning_group':DB_ALL_ANY_CHARS,
                             "area_planning_group":"F%",
                             "area_qual":"F_____"},
                            {"planning_area.planning_area_crew_category_p":"FD_CAT",
                             "planning_area.planning_area_trip_category_p":"FD_CAT",
                             "planning_area.planning_area_crew_qualification_p":"B737_QUAL",
                             "planning_area.planning_area_trip_ac_fam_p":"B737_FAM",
                             "planning_area.planning_area_leg_ac_fam_p":"B737_FAM"}),              
              
                  "FD_A320":({'maincat':'F',
                             'quals':'A2',
                             'planning_group':DB_ALL_ANY_CHARS,
                             "area_planning_group":"F%",
                             "area_qual":"F_____"},
                            {"planning_area.planning_area_crew_category_p":"FD_CAT",
                             "planning_area.planning_area_trip_category_p":"FD_CAT",
                             "planning_area.planning_area_crew_qualification_p":"A320_QUAL",
                             "planning_area.planning_area_trip_ac_fam_p":"A320_FAM",
                             "planning_area.planning_area_leg_ac_fam_p":"A320_FAM"}),

                  }

