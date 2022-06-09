
"""
This script will merge all single american airport qualifications into a
common AIRPORT+US qualifications. It is only meant to be run once during
production taking.

Usage:
    mirador -s adhoc.MergeUSQuals <dburl> <schema> 

"""
__verision__ = "$Revision$"
__author__ = "Per Gronberg, Jeppesen"

import sys
from tm import TM
from modelserver import EntityError
from modelserver import ReferenceError
from modelserver import EntityNotFoundError
import Errlog

def merge_US_airports():
    """
    Coverts and merges all airport quals in USA to one (or more if gaps) US airport qual(s)
    """
    #sort quals
    def _sort_by_validto(a1, a2):
        return cmp(a1.validto, a2.validto)
    # Def merge function
    def _merge_quals(crew, sorted_qual_list):
        """
        Gets or creates a staring US qual and extends the validto from the sorted quals.
        If a gap is found, a new US qual will be created
        """
        try:
            # get US qual from set
            US_qual = TM.crew_qualification_set[('AIRPORT','US')]
            # Crew already has one and only one valid US qual
            if len(sorted_qual_list) == 1 and sorted_qual_list[0].qual == US_qual:
                return
            #logit
            Errlog.log('MergeUSQuals:: merge airport quals : Trying to merge '+\
                       '%d quals into AIRPORT+US for crewid %s'%(len(sorted_qual_list),
                                                                 crew.id))
            
            min_date = min([qual.validfrom for qual in sorted_qual_list])
            max_date = max([qual.validto for qual in sorted_qual_list])

            #create or get starting US qual
            try:
                current_us_qual = TM.crew_qualification[(crew,US_qual,
                                                         min_date)]
            except EntityNotFoundError:
                current_us_qual = TM.crew_qualification.create((crew,US_qual,
                                                                min_date))
            # In case we run script again, we do not want to remove US already created
            quals_to_keep = set([current_us_qual])
            for qual in sorted_qual_list:
                if current_us_qual.validto is None or \
                   (current_us_qual.validfrom <= qual.validfrom and \
                    current_us_qual.validto >= qual.validfrom and \
                    current_us_qual.validto <= qual.validto):
                    # Extend current
                    current_us_qual.validto = qual.validto
                elif current_us_qual.validto < qual.validfrom:
                    # A gap, create or get new current
                    try:
                        current_us_qual = TM.crew_qualification[(crew,US_qual,
                                                                 qual.validfrom)]
                        if current_us_qual.validto < current_us_qual.validto:
                            current_us_qual.validto = qual.validto
                    except EntityNotFoundError:
                        current_us_qual = TM.crew_qualification.create((crew,US_qual,
                                                                        qual.validfrom))
                        current_us_qual.validto = qual.validto
                    quals_to_keep.add(current_us_qual)
            # In case created last in loop
            current_us_qual.validto = max_date
            for qual in sorted_qual_list:
                if qual not in quals_to_keep:
                    qual.remove() # Remove old ones
        except (EntityError, ReferenceError), err:
            Errlog.log('MergeUSQuals:: merge airport quals: %s'%err)
    # Start
    Errlog.log('MergeUSQuals:: merge_US_airports: Starting merge of US airport quals...')
    # get US airports
    us_airports = set([airport.id for airport in  TM.airport if airport.country.id == 'US'])
    # cache interesting airport quals
    crew_cache = {}
    warnings = set()
    # get quals and cache them
    for airport_qual in TM.crew_qualification.search('(qual.typ=AIRPORT)'):
        try:
            crewid = airport_qual.crew.id # check crew reference
            if airport_qual.qual.subtype not in us_airports and \
                   airport_qual.qual.subtype != 'US' :
                continue # we don't need these
            if crew_cache.has_key(airport_qual.crew):
                crew_cache[airport_qual.crew].append(airport_qual) #add to cache
            else:
                crew_cache[airport_qual.crew] = [airport_qual] #create cache
        except (EntityError, ReferenceError), err:
            if str(err) not in warnings: # only warn once for each crew
                Errlog.log('MergeUSQuals:: merge airport quals: %s'%err)
                warnings.add(str(err))
    # sort and merge US airport quals
    for crew, qual_list in crew_cache.items():
        qual_list.sort(cmp=_sort_by_validto)
        _merge_quals(crew, qual_list)

    Errlog.log('MergeUSQuals:: merge_US_airports: Finished  merge of US airport quals.')


if __name__ == 'adhoc.MergeUSQuals':
    Errlog.log("MergeUSQuals:: connecting to %s with url %s" % (sys.argv[2], sys.argv[1]))
    TM.connect(sys.argv[1], sys.argv[2], '')
    TM.loadSchema()
    TM(['crew','crew_qualification', 'crew_qualification_set','airport','country'])
    TM.newState()
    merge_US_airports()
    Errlog.log('MergeUSQuals:: Saving')
    TM.save()
    Errlog.log('MergeUSQuals:: Save done, exiting')
