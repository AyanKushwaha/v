#

#
"""
Crew Meal Order Report.
"""
import datetime
from meal.MealExceptions import AccumulatedExceptions
import meal.MealOrderRun as MOR

"""
Entry point for the report server
"""
def generate(param):
    """Delegates processing according to param and returns result.
    
    The dictionary containing the inparameters must follow this:
     'commands':    A ;-separated string of commands, se details below.
     'loadAirport': Used as inparam for 'create' Commands
     'fromDate':    Same as above.
     'toDate':      Same as above.
     'company':     Same as above.
     'region':      Same as above.
     'runByUser':   Same as above.
     'emailX':      Email address.
     'orderX':      Meal order nr.
    Note. The X above is the consecutive number of the param starting at zero.
    
    The commands should be one of:
     'cancel':
     'testAllReports':
     'create':
     'send',
     'update':
     
    Note that 'Send' can be used alone or together with one of the others.
    """
    # This flag tells DIG if model changes made by report should be saved to db.
    writeReportWorkerDeltaToDb = True
    
    print "Crew Meal Order Report is called with inparam:"
    print param
    if isinstance(param,list):
        l,d = param
    else:
        d = param

    if d.has_key('forecast'):
        forecast = d['forecast'].lower() == 'true'
    else:
        forecast = False
        
    if d.has_key('weekly'):
        weekly = d['weekly'].lower() == 'true'
    else:
        weekly = False

    if d.has_key('commands'):
        # Clean leading and trailing spaces & semicolons
        commandsStr = d['commands'].strip(' ;')
        commands = commandsStr.split(';')
    else:
        raise ValueError, 'Commands empty! Nothing to do!'

    orders = _popMatchedKeys(keyWord='order', sourceDict=d)
    emails = _popMatchedKeys(keyWord='email', sourceDict=d)
    
    errMsgHeader = "Error message for Crew Meal job,\nstarted in the report server at %s, with parameters:\n%s\n%s%s" % (
                    str(datetime.datetime.now())[:19],
                    d,
                    ("", "for the following order numbers:\n%s\n" % orders)[len(orders)>0],
                    ("", "to the following mailaddresses:\n%s\n" % emails)[len(emails)>0])
    AccumulatedExceptions().setReturnListErrorHeader(errMsgHeader)
    
    if 'cancel' in commands:
        reports = MOR.processMealOrderList(mealOrderList=orders, forecast=forecast, cancel=True)

    elif 'testAllReports' in commands:
        writeReportWorkerDeltaToDb = False
        reports = MOR.processMealOrderList(mealOrderList=orders, forecast=forecast, send=False, testAllTypes=True)
    elif 'create' in commands and not 'update' in commands:
        send = 'send' in commands
        kwds={}
        for paramName in ('loadAirport', 'fromDate', 'toDate', 'region', 'runByUser'):
            if d.has_key(paramName):
                kwds[paramName]= d[paramName]
        reports = MOR.mealOrderRun(forecast=forecast, weekly=weekly, send=send, **kwds)
    elif 'create' in commands and 'update' in commands:
        send = 'send' in commands
        kwds={}
        for paramName in ('loadAirport', 'region', 'runByUser', 'updateTime'):
            if d.has_key(paramName):
                kwds[paramName]= d[paramName]

        reports = MOR.mealOrderUpdate(send=send, **kwds)
    elif 'send' in commands and 'update' in commands:
        reports = MOR.sendMealUpdateOrderList(mealOrderList=orders, mailAddrs=emails)
    elif 'send' in commands:
        reports = MOR.processMealOrderList(mealOrderList=orders, forecast=forecast, send=True, mailAddrs=emails)
    else:
        raise ValueError, 'Not valid Command: %s' % (commands)
    
    return (reports, writeReportWorkerDeltaToDb)


def _popMatchedKeys(keyWord, sourceDict):
    """Returns a list of values, removed from sourceDict, for keys containing keyWord.
    """
    returnList=[]
    for key in sourceDict.keys():
        if keyWord in key:
            returnList.append(sourceDict.pop(key))
    returnList.sort()
    return returnList
