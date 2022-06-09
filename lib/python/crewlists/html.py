

"""
HTML formatting tools (for the R2 reports).
"""

# imports ================================================================{{{1
from utils.xmlutil import XMLElement


# constants =============================================================={{{1
# Embedded CSS
CSS = {
    'screen': """<!--
    body.CMS * { font-family: sans-serif; }
    body.CMS h1 { font-size: 110%; }
    body.CMS { margin: 2ex; }
    body.CMS h2 { font-size: 110%; font-weight: bold; padding-top: 2ex; border-top-style: solid; border-top-width: thin; }
    body.CMS h3 { padding-left: 3ex; }
    body.CMS table { margin-top: 4ex; border-collapse: collapse; }
    body.CMS th { text-align: left; background-color: #cdcdcd; }
    body.CMS th, td { padding: 0.5ex; }
    body.CMS tr.even { background-color: #f1f1f1; }
    body.CMS .right { float: right; }
    body.CMS .floatstop { clear: both; }
    body.CMS { font-size: x-small; }
    body.CMS#CREWSLIP table { width: 90%; }
    body.CMS#CREWSLIP #rules { float: left; width: 60%; }
    body.CMS#CREWSLIP #summary { font-size:x-small; width: 30%; margin-left: 5ex; }
    body.CMS#CREWSLIP #summary + * { clear: both; }
    body.CMS#CREWSLIP #rules ul { list-style: none; padding-left: 0ex; }
    body.CMS#CREWSLIP #roster { font-size:x-small; margin-left: 4ex; padding-left: 3ex; }
    body.CMS#PILOTLOGFLIGHT #basics { border-left: solid thin; }
    body.CMS#PILOTLOGFLIGHT #details { border-left: solid thin; }
    body.CMS #basics { font-size:x-small; margin-left: 4ex; padding-left: 3ex; }
    body.CMS #overview { margin-left: 4ex; padding-left: 3ex; }
    body.CMS #details { font-size:x-small; margin-left: 4ex; padding-left: 3ex; }
    body.CMS#CREWSLIP tr.dayshift td { border-top: thin solid black; }
 -->""",

    'print': """<!--
    body.CMS * { font-family: sans-serif; }
    body.CMS h1 { font-size: 110%; }
    body.CMS { margin: 0cm 0cm 0cm 0cm; }
    body.CMS h2 { font-size: 110%; font-weight: bold; padding-top: 2ex; border-top-style: solid; border-top-width: thin; }
    body.CMS h3 { font-size: small; padding-left: 3ex; }
    body.CMS table { margin-top: 4ex; border-collapse: collapse; }
    body.CMS th { text-align: left; }
    body.CMS th, body.CMS td { padding: 0.5ex; }
    body.CMS tr.even { background-color: #f1f1f1; }
    body.CMS .right { float: right; }
    body.CMS .floatstop { clear: both; }
    body.CMS { font-size: x-small; }
    body.CMS#CREWSLIP th { font-size:x-small;text-align: left; }
    body.CMS#CREWSLIP table { width: 100%; }
    body.CMS#CREWSLIP #rules { font-size:xx-small; float: left; width: 60%; }
    body.CMS#CREWSLIP #summary { font-size:x-small; width: 35%; margin-left: 3ex; }
    body.CMS#CREWSLIP #summary + * { clear: both; }
    body.CMS#CREWSLIP #rules ul { list-style: none; padding-left: 0ex; }
    body.CMS#CREWSLIP #roster th { font-size:x-small;text-align: left; }
    body.CMS#CREWSLIP #roster { font-size:x-small; margin-left: 0ex; padding-left: 0ex; }
    body.CMS#PILOTLOGFLIGHT #basics { border-left: solid thin; }
    body.CMS#PILOTLOGFLIGHT #details { border-left: solid thin; }
    body.CMS#PILOTLOGCREW #details { font-size:x-small; }
    body.CMS #basics { font-size:x-small; margin-left: 2ex; margin-right: 3cm; padding-left: 0ex; }
    body.CMS #overview { margin-left: 4ex; padding-left: 3ex; }
    body.CMS #details { margin-left: 4ex; padding-left: 3ex; }
    body.CMS#CREWSLIP tr.dayshift td { border-top: thin solid black; }
 -->""",
 }

# Not supported by IE with version < 7
#    body.CMS tr.even + tr.odd { border-top: solid; border-width: thin; }
#    body.CMS tr.odd + tr.even { border-top: solid; border-width: thin; }


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
        self.head.append(meta)
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
        XMLElement.append(self, self.head)
        self.body = body(report)
        XMLElement.append(self, self.body)

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


# span_right -------------------------------------------------------------{{{2
class span_right(span):
    """ To mark text that should be right-aligned. """
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
            self.thead = XMLElement('thead', tr(th, *headers))
            XMLElement.append(self, self.thead)
        else:
            self.thead = None
        self.odd = 1
        self.tbody = XMLElement('tbody')
        XMLElement.append(self, self.tbody)

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
