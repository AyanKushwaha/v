
# [acosta:07/095@10:09] First version, broke out code from elements to be able
# to import in GetReport-reports without having to import the huge elements.py

"""
This file is used by all reports that have replyBody as root element to format
the response string.

These are currently:
    CrewList
    CrewBasic
    CrewRoster
    CrewFlight
    (GetReportList not implemented here - trivial)
    GetReport
    CrewLanding
    CheckInOut
"""

# imports ================================================================{{{1
import crewlists.status as status
from utils.xmlutil import XMLDocument, XMLElement, CDATA, escape

schema_version = status.schema_version


# Reply =================================================================={{{1
class Reply(status.BasicReply):
    """
    Reply of form:
    
    response to CrewBasic, 0
    <?xml version="1.0" encoding="iso-8859-1"?>
    <replyBody>
        ...
    </replyBody>
    """
    def __init__(self, requestName='Unknown', statusCode=status.OK, statusText=None, payload=None, inparams=None):
        """ Add optional statusText. """
        status.BasicReply.__init__(self, requestName=requestName, statusCode=statusCode, payload=payload)
        self.inparams = inparams
        if statusText is None:
            self.statusText = str(statusCode)
        else:
            # additional status text supplied by programmer
            self.statusText = str(statusCode) + " - " + statusText

    def response(self):
        """ Create response consisting of 'replyBody'. """
        xdoc = XMLDocument()
        # Question: Convert to UTF-8 ??
        xdoc.encoding = "iso-8859-1"
        xdoc.append(replyBody(self))
        return str(xdoc)


# ReplyError ============================================================={{{1
class ReplyError(Reply, status.BasicReplyError):
    """ Create exceptions that will look like a normal answer. """
    pass


# replyBody =============================================================={{{1
# This is the root element.
class replyBody(XMLElement):
    """ root element """
    version = schema_version
    def __init__(self, reply):
        """
        NOTE: the argument 'reply' is an object reference to a 'Reply' instance.
        """
        XMLElement.__init__(self)
        self['version'] = self.version
        self.append(XMLElement('requestName', reply.requestName))
        self.append(XMLElement('statusCode', '%03d' % (reply.statusCode)))
        self.append(XMLElement('statusText',  CDATA(reply.statusText)))
        if reply.payload is None:
            # Ugly, but has to be imported here because of cross-dependencies.
            from crewlists.elements import dummy_reply
            self.append(dummy_reply(reply.requestName, reply.inparams))
        else:
            self.append(reply.payload)


# HTMLDocument ==========================================================={{{1
DOCTYPE = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
"""
class HTMLDocument(XMLDocument):
    def __init__(self, html):
        XMLDocument.__init__(self)
        # Question: Convert to UTF-8 ??
        self.encoding = 'iso-8859-1'
        self.append(DOCTYPE)
        self.append(html)


# getReportReply ========================================================={{{1
class getReportReply(XMLElement):
    """
    For reports of type R1 and R2, some additional info is presented in
    the reply.
    """
    def __init__(self, reportId, params, reportBody=None):
        XMLElement.__init__(self)
        self.append(XMLElement('reportId', reportId))
        parameters = XMLElement('parameters')
        for p in params:
            parameters.append(XMLElement('parameter', escape(p)))
        self.append(parameters)
        if reportBody is None:
            # If error, no payload
            self.append(XMLElement('reportBody'))
        else:
            # Encapsulate HTML document in the reportBody tag.
            self.append(XMLElement('reportBody', CDATA(HTMLDocument(reportBody))))


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
