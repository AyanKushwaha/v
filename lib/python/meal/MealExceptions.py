import sys
import traceback

def change_exception_args(e, new_args):
    """ Changes the arguments for the exception """
    e.args = (new_args,)

class AccumulatedExceptions(Exception):
    """This class will let exceptions register to be processed together at a later time.
    """
    __shared_state = {}
    _exceptionList = []
    errorMsgHeader = ""

    def __init__(self):
        """Makes it a singleton.
        """
        self.__dict__ = self.__shared_state

    def __str__(self):
        """Return somthing like ""
        """
        return "%s: %s" % (self.__class__.__name__, self.args)

    def register(self, exceptionObj=None):
        """Registers an exception ie. stores it for future processing.
        """
        if exceptionObj is None:
            exceptionObj = self
        self._exceptionList.append(exceptionObj)
        traceback.print_exc()

    def unregister(self, exceptionObj=None, all=False):
        """Unregisters one/all exceptions ie. removes it from storage.
        """
        if all:
            self._exceptionList = []
        elif exceptionObj:
            if exceptionObj in self._exceptionList:
                self._exceptionList.remove(exceptionObj)
        else:
            raise ValueError, 'Nothing to do for inparams: exceptionObj=%s, all=%s' % (exceptionObj, all)

    def setReturnListErrorHeader(self, errorMsgHeader=""):
        """Sets a header prepended to the error msg of makeDigReturnList()
        """
        self.errorMsgHeader = errorMsgHeader

    def makeDigReturnList(self):
        """Returns a list intended to be returned from reportserver.

        The returnlist will be processed by Dig according to it's configuration,
        so this method should be reimplemented in a subclass to fit that configuration.
        This implementation is intended for the SAS user 080228.
        """
        if len(self._exceptionList) == 0:
            return []
        devider = '='*80+'\n'
        errorList= [devider]
        if self.errorMsgHeader:
            errorList.append(self.errorMsgHeader)
            errorList.append(devider)
        for i, exc in enumerate(self._exceptionList):
            errorList.append('Error nr %s:\n%s\n' % (i+1, str(exc)))
        errorList.append(devider)
        errorstr = ''.join(errorList)


        return [{'content': errorstr,
                'content-type': 'text/plain',
                'destination': [("CREW_MEAL", {'subtype':'ERROR'})]}]


class MissingData(AccumulatedExceptions):
    """Base class for exceptions where data not found
    """
    def __init__(self, *args):
        Exception.__init__(self, *args)
        self.wrapped_exc = sys.exc_info()
        self.register()


class Inconsistency(AccumulatedExceptions):
    """Base class for exceptions where inconsistency is found
    """
    def __init__(self, *args):
        Exception.__init__(self, *args)
        self.wrapped_exc = sys.exc_info()
        self.register()


class OrderNotFoundError(MissingData):
    """Exception class used when meal order is not found
    """


class CustomerNotFoundError(MissingData):
    """Exception class used when customer is not found
    """


class SupplierNotFoundError(MissingData):
    """Exception class used when supplier is not found
    """


class StationNotFoundError(MissingData):
    """Exception class used when station is not found
    """


class FlightNotFoundError(MissingData):
    """Exception class used when flight is not found
    """


class CrewCategoryNotFoundError(MissingData):
    """Exception class used when crew category is not found
    """


class OrderLineNotFoundError(MissingData):
    """Exception class used when meal order line is not found
    """


class MealCodeNotFoundError(MissingData):
    """Exception class used when meal code is not found
    """


class ArgumentInconsistencyError(Inconsistency):
    """Exception class used when argument inconsistency is found
    """


class MultipleEntries(Inconsistency):
    """Exception class used when multiple entries are found but only one is expected
    """


class DataError(AccumulatedExceptions):
    """Exception class used when db data is not OK.
    """
    def __init__(self, *args):
        Exception.__init__(self, *args)
        self.wrapped_exc = sys.exc_info()
        self.register()


class InParamError(AccumulatedExceptions):
    """Exception class used when call inparameters is not OK.
    """
    def __init__(self, *args):
        Exception.__init__(self, *args)
        self.wrapped_exc = sys.exc_info()
        self.register()
