
# changelog {{{2
# [acosta:07/078@13:59] First version
# [acosta:07/095@10:31] Moved file to crewlists package
# }}}

"""
Common functionality for all R2 reports.
"""

# imports ================================================================{{{1
from utils.xmlutil import XMLDocument, XMLElement, CDATA


# constants =============================================================={{{1
# Embedded CSS
CSS = {
    'screen': """<!--
    body.CMS * { font-family: sans-serif; }
    body.CMS h1 { font-size: 150%; }
    body.CMS { margin: 2ex; }
    body.CMS table { margin-top: 4ex; border-collapse: collapse; }
    body.CMS th { text-align: left; background-color: #cdcdcd; }
    body.CMS th, td { padding: 0.5ex; }
    body.CMS tr.even { background-color: #f1f1f1; }
    body.CMS .right { float: right; }
    body.CMS#CREWSLIP { font-size: small; }
    body.CMS#CREWSLIP table { width: 100%; }
    body.CMS#CREWSLIP #rules { float: left; width: 60%; }
    body.CMS#CREWSLIP #summary { width: 30%; margin-left: 5ex; }
    body.CMS#CREWSLIP #summary + * { clear: both; }
    body.CMS#CREWSLIP #rules ul { list-style: none; padding-left: 0ex; }
 -->""",

    'print': """<!--
    body.CMS * { font-family: sans-serif; }
    body.CMS h1 { font-size: 150%; }
    body.CMS { margin: 0cm 0.5cm 0cm 0.5cm; }
    body.CMS table { margin-top: 4ex; border-collapse: collapse; }
    body.CMS th { text-align: left; border-bottom: solid; }
    body.CMS th, body.CMS td { padding: 0.5ex; }
    body.CMS tr.even { background-color: #f1f1f1; }
    body.CMS .right { float: right; }
    body.CMS#CREWSLIP { font-size: small; }
    body.CMS#CREWSLIP table { width: 100%; }
    body.CMS#CREWSLIP #rules { float: left; width: 60%; }
    body.CMS#CREWSLIP #summary { width: 30%; margin-left: 5ex; }
    body.CMS#CREWSLIP #summary + * { clear: both; }
    body.CMS#CREWSLIP #rules ul { list-style: none; padding-left: 0ex; }
    body.CMS#CREWSLIP table#roster { margin-right: 3cm; }
    body.CMS tr.even + tr.odd { border-top: solid; border-width: thin; }
    body.CMS tr.odd + tr.even { border-top: solid; border-width: thin; }
 -->""",
 }

# Document type
DOCTYPE = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
"""

# HTMLDocument ==========================================================={{{1
class HTMLDocument(XMLDocument):
    def __init__(self, html):
        XMLDocument.__init__(self)
        # Question: Convert to UTF-8 ??
        self.encoding = 'iso-8859-1'
        self.append(DOCTYPE)
        self.append(html)


# XMLElement classes (XML) ==============================================={{{1

# getReportReply ---------------------------------------------------------{{{2
class getReportReply(XMLElement):
    def __init__(self, reportId, params, reportBody=None):
        XMLElement.__init__(self)
        self.append(XMLElement('reportId', reportId))
        parameters = XMLElement('parameters')
        for p in params:
            parameters.append(XMLElement('parameter', p))
        self.append(parameters)
        if reportBody is None:
            # If error, no payload
            self.append(XMLElement('reportBody'))
        else:
            # Encapsulate HTML document in the reportBody tag.
            self.append(XMLElement('reportBody', CDATA(HTMLDocument(reportBody))))


# XMLElement classes (HTML) =============================================={{{1

# body -------------------------------------------------------------------{{{2
class body(XMLElement):
    def __init__(self, report_name):
        XMLElement.__init__(self)
        self['class'] = "CMS"
        self['id'] = report_name


# html -------------------------------------------------------------------{{{2
class html(XMLElement):
    def __init__(self, title=None, report=None, srcid=None):
        XMLElement.__init__(self)
        self['xmlns'] = "http://www.w3.org/1999/xhtml"
        self.head = XMLElement('head')
        meta = XMLElement('meta')
        meta['http-equiv'] = "Content-Type"
        meta['content'] = "text/html; charset=ISO-8859-1"
        if not title is None:
            self.head.append(XMLElement('title', title))
        if not report is None:
            meta = XMLElement('meta')
            meta['name'] = "generator"
            meta['content'] = report
            self.head.append(meta)
        if not srcid is None:
            meta = XMLElement('meta')
            meta['name'] = "srcid"
            meta['content'] = srcid
            self.head.append(meta)
        self.head.append(style('screen'))
        self.head.append(style('print'))
        self.data.append(self.head)
        self.body = body(report)
        self.data.append(self.body)

    def srcid(self, i):
        meta = XMLElement('meta')
        meta['name'] = "srcid"
        meta['content'] = i
        self.head.append(meta)

    def append(self, x):
        """ Append to <body /> """
        self.body.append(x)


# span -------------------------------------------------------------------{{{2
class span(XMLElement):
    def __init__(self, *a, **k):
        XMLElement.__init__(self, 'span', *a, **k)


# right (span) -----------------------------------------------------------{{{2
class right(span):
    """ To mark text that should be aligned right """
    def __init__(self, *a, **k):
        span.__init__(self, *a, **k)
        self['class'] = "right"


# style ------------------------------------------------------------------{{{2
class style(XMLElement):
    def __init__(self, media):
        XMLElement.__init__(self)
        self['type'] = "text/css"
        self['media'] = media
        self.append(CSS[media])


# table ------------------------------------------------------------------{{{2
class table(XMLElement):
    def __init__(self, *headers):
        XMLElement.__init__(self)
        # So that subclasses don't have to define this.
        self.tag = 'table'
        if headers:
            self.data.append(XMLElement('thead', tr(th, *headers)))
        self.odd = 1
        self.tbody = XMLElement('tbody')
        self.data.append(self.tbody)

    def append(self, *columns):
        row = tr(td, *columns)
        row['class'] = ('even', 'odd')[self.odd > 0]
        self.odd = -self.odd
        self.tbody.append(row)


# tr ---------------------------------------------------------------------{{{2
class tr(XMLElement):
    """
    A table row with 'td' or 'th' elements.
    """
    def __init__(self, element, *columns):
        XMLElement.__init__(self)
        # So that subclasses don't have to define this.
        self.tag = 'tr'
        colNo = 1
        for c in columns:
            self.append(element(c, colNo))
            colNo += 1


# th ---------------------------------------------------------------------{{{2
class th(XMLElement):
    """
    The HTML <th>...</th> tag.
    """
    def __init__(self, data, colno):
        """ sets class='colN' attributes """
        XMLElement.__init__(self)
        self['class'] = "col%d" % (colno)
        self.append(data)


# td ---------------------------------------------------------------------{{{2
class td(th):
    """
    The HTML <th>...</th> tag.
    """
    # The same as for <th>
    pass


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
