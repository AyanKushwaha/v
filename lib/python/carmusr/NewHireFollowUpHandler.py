#####################################################
#
# NewHireFollowUpHandler:: Module for functions related to updating the new_hire_follow_up table
#
# 2014-09-17 - Mikael Larsson (HiQ)

import Cui
import Errlog
import carmensystems.rave.api as R
import carmusr.HelperFunctions as HF

from AbsTime import AbsTime

### This functionality only works while on DB-plans
try:
    from tm import TM
except:
    # This handles when the script is called when product=cas and
    # modelserver isn't available
    pass


# constants
MODULE = "NewHireFollowUpHandler:: "
CONTEXT = 'default_context'


def update_new_hire_follow_up_table() :

    FUNCTION = MODULE + "update_new_hire_follow_up_table:: "
    try:
        assert HF.isDBPlan()
    except:
        Errlog.log(FUNCTION + "Only available in database plans")

    # Display roster
    Cui.CuiDisplayObjects(Cui.gpc_info, Cui.CuiArea0, Cui.CrewMode, Cui.CuiShowAll)
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiArea0, "window")
    
    add_new_hires_to_table()    


def add_new_hires_to_table() :

    FUNCTION = MODULE + "add_new_hires_to_table:: "

    # Find all new-hired crew that has performed ILC and add them to the table new_hire_follow_up
    # RAVE expressions are loctaed in the file training_gpc
    ctx = R.context(CONTEXT)    
    for roster in ctx.bag().chain_set() :
        for leg in roster.iterators.leg_set() :
            if leg.training.crew_has_performed_first_ilc() :
           
                Errlog.log(FUNCTION + "Detected ILC on %s for crew %s." %(str(leg.training.new_hire_init_ilc_date()),str(leg.crew.id())))
                Errlog.log(FUNCTION + "Adding crew %s to new_hire_follow_up table." %str(leg.crew.id())) 
               
                new_entry = TM.new_hire_follow_up.create((TM.crew[(leg.crew.id(),)],))

                new_entry.ilc_date               = AbsTime(leg.training.new_hire_init_ilc_date())
                new_entry.mentor                 = TM.crew[(leg.training.new_hire_init_mentor(),)]
                new_entry.follow_up_1_start_date = AbsTime(leg.training.new_hire_init_follow_up_1_start_date())
                new_entry.follow_up_1_end_date   = AbsTime(leg.training.new_hire_init_follow_up_1_end_date()) 
                new_entry.follow_up_2_start_date = AbsTime(leg.training.new_hire_init_follow_up_2_start_date())
                new_entry.follow_up_2_end_date   = AbsTime(leg.training.new_hire_init_follow_up_2_end_date())
                new_entry.follow_up_3_start_date = AbsTime(leg.training.new_hire_init_follow_up_3_start_date())
                new_entry.follow_up_3_end_date   = AbsTime(leg.training.new_hire_init_follow_up_3_end_date())





if __name__ == "__main__":
    print "NewHireFollowUpHandler::running self test"
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiArea0, "window")
    remove_old_new_hires_from_table() 
