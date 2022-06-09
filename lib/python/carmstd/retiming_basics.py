'''
Some retiming functions needed also in APC have been 
moved to this module. 

Created by Stefan Hammar in Nov 2010.
Modified for SAS on March 2012 by Stefan Hammar.

'''

if __name__ == "__main__":
    raise NotImplementedError, "Do not execute as script"

from RelTime import RelTime
import re

def regularity_cost_in_bag(bag):
    """
    Calculate:
    * the cost for violated retiming regularity for the legs in the bag 
    * number of not regular groups
    * Number of regularity changes in the groups. 
    
    """
    tot_cost = tot_nig = tot_g = 0
    for group_bag in bag.retiming.retiming_group():
        any_change_in_group = 0
        fr = 0
        cr = 0
        cost_per_change = group_bag.retiming.regularity_penalty()
        for n, leg_bag in enumerate(group_bag.retiming.unique_leg_set(sort_by="retiming.normalized_leg_start_utc")):
            cr = (leg_bag.retiming_leg.amount_retimed_start(), 
                  leg_bag.retiming_leg.amount_retimed_end())
            if n == 0:
                fr = pr = cr
            else:
                if pr != cr:
                    tot_cost += cost_per_change
                    tot_nig += 1
                    any_change_in_group = 1
                    pr = cr
        if fr != cr: 
            tot_cost += cost_per_change
            tot_nig += 1
        if any_change_in_group:
            tot_g += 1
       
    return tot_cost, tot_nig, tot_g
                        
def ret_alt_value_to_tuple(value_str):
    """
    Converts a single value in a retiming alternative string to a 2-item tuple 
    with RelTime objects. 
    """
    value_str = value_str.strip()
    if value_str[0] == "(":
        v = value_str[1:-1].split(",")
        if len(v) != 2:
            raise ValueError("Exactly one comma in value is expected: '%s'" % value_str)
        return (RelTime(v[0].strip()), RelTime(v[1].strip())) 
    else:
        return (RelTime(value_str), RelTime(value_str)) 

    
crex = re.compile(r"\s*([^,\(\)\s]+|\([^\(\)]*\))\s*,?")

def get_retimings_as_list(retiming_alt_str):
    """
    Returns a list of tuples with RelTime objects given a retiming alternative string.
    """
    return [ret_alt_value_to_tuple(item) for item in crex.findall(retiming_alt_str)]

def max_starting_earlier(retiming_alt_str):
    return RelTime(0) - min(item[0] for item in get_retimings_as_list(retiming_alt_str))
    
def max_ending_later(retiming_alt_str):
    return max(item[1] for item in get_retimings_as_list(retiming_alt_str))   

def get_retiming_array(retiming_alt_str):
    """
    Takes a retiming string and converts it to a list of retiming element strings.
    Example, the string '0:01,(0:05,0:05)' gives the list with 2 elements ['0:01','(0:05,0:05)']
    
    If the retiming string can't be converted. It raises an 'ValueError' exception.
    Any white-spaces in the string are removed.
    
    @param retiming_alt_str: A string of retiming alternatives. 
                             The retiming alternatives are separated using a comma.
    @type retiming_alt_str: string
    @return: Returns a list of retiming elements as strings extracted 
             from the retiming_alt_str.
    @rtype: list
    """
    try:
        return [item[0] == item[1] and str(item[0]) or "(%s,%s)" % item
                for item in get_retimings_as_list(retiming_alt_str)]
    except Exception, e:
        raise ValueError("String is incorrect: %s" % e)
