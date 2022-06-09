
# changelog {{{2
# [acosta:06/297@09:09] Error codes for crew lists.
# [acosta:07/094@15:28] Clean-up
# [acosta:07/095@09:39] 
# }}}

"""
Common code for request/reply with crewlists in XML format.

These are the error codes for the crew list package.
cf. the document 'Use of "statusCode"'.

It also contains parts common to all reports.
"""

schema_version = "2.2" # Crew2.2.zip


# StatusCode handling ===================================================={{{1

# StatusCode -------------------------------------------------------------{{{2
class StatusCode:
    __statusCode = 999
    __errorText = '???'
    def __init__(self, statusCode=999, errorText=''):
        self.__statusCode = statusCode
        self.__errorText = errorText

    def __str__(self):
        return self.__errorText

    def __int__(self):
        return self.__statusCode

    def __float__(self):
        return float(self.__statusCode)


# constants =============================================================={{{1
OK                        = StatusCode(  0, "Ok")
NO_CIO                    = StatusCode(100, "Checkin/Checkout operation failed.")
FLIGHT_NOT_FOUND          = StatusCode(201, "Flight not found.")
CREW_NOT_FOUND            = StatusCode(202, "Crew not found.")
REPORT_NOT_FOUND          = StatusCode(208, "Report not found.")
CREW_NOT_VALID            = StatusCode(210, "Crew not valid.")
FLIGHT_NOT_VALID          = StatusCode(211, "Flight not valid.")
REQUEST_NOT_SUPPORTED     = StatusCode(212, "Request not supported.")
NOT_AVAILABLE             = StatusCode(900, "Cannot perform requested action.")
INPUT_PARSER_FAILED       = StatusCode(990, "Input parser failed.")
WRONG_NUMBER_OF_ARGUMENTS = StatusCode(996, "Wrong number of arguments.")
DATA_ERROR                = StatusCode(997, "Data Error.")
UNEXPECTED_ERROR          = StatusCode(999, "Unexpected system error.")


# flags =================================================================={{{1
debug               = False


# BasicReply ============================================================={{{1
class BasicReply:
    """
    Simplest of all possible replies:

    response to crewMessage, 0
    ...
    """
    def __init__(self, requestName='Unknown', statusCode=OK, payload=None):
        self.requestName = requestName
        self.statusCode = statusCode
        self.payload = payload

    def __str__(self):
        """
        Returns a one-liner with status info: request type, a numeric status
        code, and the optional full-text response.
        """
        return "response to %s, %d\n" % (self.requestName, int(self.statusCode)) + self.response()

    def response(self):
        """ To be overridden by subclasses. """
        if self.payload is None:
            return ""
        else:
            return str(self.payload)


# BasicReplyError ========================================================{{{1
class BasicReplyError(BasicReply, Exception):
    """ Exception with the same string representation as BasicReply.
    Use this construct:
    class Reply(crewlists.status.CrewServiceReply):
        def response(self):
            return str(XMLDocument(replyBody(self)))

    -*- and create your own ReplyError like this -*-

    class ReplyError(Reply, CrewServiceReplyError):
        pass
    """
    pass


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
