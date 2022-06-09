

# Purpose: This script is run on a nightly basis

import carmensystems.rave.api as R
from tm import TM
from utils.rave import RaveIterator
import AbsTime
from AbsTime import PREV_VALID_DAY
import modelserver

global accumulatorTypes

accumulatorTypes = {'block_time': 'leg.%block_time%'}

class Accumulators(RaveIterator):
    fields = {}
    
    def setFields(self, newFields):
        self.fields = newFields
        return

def setIterator(nowTime, acc):
    '''
    Sets the iterator corresponding to the current time.
    '''
    # Convert to string and then back to abstime to make a copy of the abstime
    # rather than another reference to the object.
    todayStart = AbsTime.AbsTime(str(nowTime))
    todayStart = todayStart.day_floor()
    monthStart = AbsTime.AbsTime(str(nowTime))
    monthStart = monthStart.month_floor()
    return RaveIterator(RaveIterator.iter('iterators.leg_set',
                                          where=('fundamental.%is_roster%',
                                                 'leg.%%end_UTC%%<%s' \
                                                 %todayStart,
                                                 'leg.%%start_UTC%%>%s' \
                                                 %monthStart)),acc)

def create_accumulator_set():
    global accumulatorTypes
    for acc_type in accumulatorTypes:
        try:
            TM.acc_type_set.create((acc_type,))
        except modelserver.EntityError:
            pass
    #end for
    return

def accumulate():
    '''
    The function is responsible to accumulate all values in the
    accumulatorTypes dictionary and create the corresponding entries i the
    acc_table.
    '''

    create_accumulator_set()
    
    global accumulatorTypes
    
    nowTime, = R.eval('fundamental.%now%')
    year = nowTime.split()[0]
    month = nowTime.split()[1]
    previousMonth = AbsTime.AbsTime(str(nowTime))
    previousMonth = previousMonth.addmonths(-1,PREV_VALID_DAY)
    previousMonth = previousMonth.split()[1]
    
    fields = {'crew' :'crew.%id%',
              'ac_type' :'leg.%ac_type%'}
    
    accumulator = Accumulators()
    
    for acc_type in accumulatorTypes:
        fields[acc_type] = accumulatorTypes[acc_type]
        accumulator.setFields(fields)

        fi = setIterator(nowTime, accumulator)
        results = fi.eval('sp_crew')

        crew = None

        # Remove all old entries from the table corresponding to the particular
        # month and year.
        for row in TM.acc_table.search("(&(year=%s)(month=%s))" %(year,month)):
            row.value = None
            row.total = 0
        #end for
        for result in results:
            crewRef = TM.crew.getOrCreateRef((result.crew))
            accRef = TM.acc_type_set.getOrCreateRef((acc_type))
            acRef = TM.aircraft_type.getOrCreateRef((result.ac_type))

            if result.ac_type == "":
                continue
            #end if

            try:
                newRow = TM.acc_table[(crewRef,
                                       accRef,
                                       acRef,
                                       year, month)]
            except:
                newRow = TM.acc_table.create((crewRef,
                                              accRef,
                                              acRef,
                                              year, month))
            #end
            try:
                previousRow = TM.acc_table.getRef((crewRef,
                                                   accRef,
                                                   acRef,
                                                   year, previousMonth))
            except:
                previousRow = None
            #end

            # Find the value amongst the attributes of the result object
            value = int(result.__dict__[acc_type])  

            if newRow.value is None:
                newRow.value = value
            else:
                newRow.value = newRow.value + value
                
            if previousRow is None:
                newRow.total = newRow.value
            else:
                newRow.total = newRow.value + previousRow.total
            #end if
        #end for
    #end for
    return
