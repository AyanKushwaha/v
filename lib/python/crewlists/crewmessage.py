
# [acosta:07/129@15:53] First version, broke out common code.

"""
This file is used by those reports that have crewMessage as root element.
"""

# imports ================================================================{{{1
from utils.xmlutil import XMLDocument, XMLElement
from crewlists.status import schema_version


# Message ================================================================{{{1
class Message(XMLDocument):
    """ XML document that contains a crewMessage. """
    def __init__(self, messageName=None, payload=None):
        XMLDocument.__init__(self)
        self.append(crewMessage(messageName, payload))


# MessageError ==========================================================={{{1
class MessageError(Exception):
    """ Returns diagnostic text message """
    def __init__(self, messageName='Unknown', statusCode=None, statusText=None):
        self.messageName = messageName
        self.statusCode = statusCode
        self.statusText = statusText

    def __str__(self):
        return "%s: ERROR %d: %s - %s" % (
            self.messageName,
            int(self.statusCode),
            str(self.statusCode), 
            str(self.statusText)
        )

    
# crewMessage ============================================================{{{1
class crewMessage(XMLElement):
    """ root element """
    def __init__(self, messageName=None, payload=None):
        XMLElement.__init__(self)
        self['version'] = schema_version
        self.append(XMLElement('messageName', messageName))
        self.append(messageBody(payload))


# messageBody ============================================================{{{1
class messageBody(XMLElement):
    def __init__(self, payload=None):
        XMLElement.__init__(self)
        if not payload is None:
            self.append(payload)


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
