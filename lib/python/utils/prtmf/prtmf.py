__mf = None


LEFT=11
RIGHT=12
CENTER=13
BOTTOM=15
SERIF=21
SANSSERIF=22
MONOSPACE=23
BOLD=31
ITALIC=41
LANDSCAPE=50
PORTRAIT=51
LETTER=55
LEGAL=56
EXECUTIVE=61
A4=57

class PrtMFObject(object):
    def __init__(self):
        self._children = []
        self._attrs = {}
        
    def _set(self, **kwargs):
        self._attrs.update(kwargs)
        
    def _get(self, k):
        return self._attrs.get(k, None)
        
    def _add(self, component, pos='', **kwargs):
        self._children.append((pos, component, kwargs))
        
    def _attr(self):
        return ':%s:' % type(self).__name__ + ';'.join(['%s=%s' % (x, _fmtattr(self._attrs[x])) for x in self._attrs])+':'
        
    def _write_extras(self, f, indent=0):
        pass
        
    def _write(self, f, indent=0):
        attrs = ' '.join(['%s="%s"' % (x, _fmtattr(self._attrs[x])) for x in self._attrs])
        if indent>0: f.write('  ' * indent)
        f.write('<%s' % type(self).__name__)
        if attrs:
            f.write(' ')
            f.write(attrs)
        self._write_extras(f, indent)
        if self._children:
            f.write('>\n')
            inNewRep = False
            for pos,component,kwargs in self._children:
                if isinstance(component, ReportDelimiter):
                    if inNewRep: f.write("</newReport>\n")
                    f.write('<newReport name="%s">\n' % component.name)
                    inNewRep =True
                else:
                    attrs = ' '.join(['%s="%s"' % (x, _fmtattr(kwargs[x])) for x in kwargs])
                    if indent>=0: f.write('  ' * (indent+1))
                    f.write('<add')
                    if pos: f.write(' p="%s"' % pos)
                    if attrs:
                        f.write(' ')
                        f.write(attrs)
                    f.write('>\n')
                    if isinstance(component, PrtMFObject):
                        component._write(f, (indent>=0) and indent+2 or indent)
                    elif not component is None:
                        if indent>=0: f.write('  ' * (indent+2))
                        f.write("<s>%s</s>\n" % component)
                    if indent>=0: f.write('  ' * (indent+1))
                    f.write('</add>\n')
            if inNewRep: f.write("</newReport>")
            if indent>0: f.write('  ' * indent)
            f.write('</%s>\n' % type(self).__name__)
        else:
            f.write('/>\n')
            
def _fmtattr(x):
    if isinstance(x, PrtMFObject):
        return x._attr()
    else:
        return x

class ReportDelimiter(PrtMFObject):
    name = ""
    def __init__(self, name):
        self.name = name
    
class Box(PrtMFObject):
    def annotate(self):
        raise NotImplementedError()
        
    def set(self, **properties):
        self._set(**properties)
        
class Canvas(Box):
    def __init__(self, width, height, **properties):
        PrtMFObject.__init__(self)
        self._set(width=width, height=height, **properties)

    def draw(self, gc):
        raise NotImplementedError()
        
    def set(self, **properties):
        self._set(**properties)
    
    def size(self):
        return (self._get('width'), self._get('height'))
        
class Chart(Canvas):
    pass
    
class ColourPalette(PrtMFObject):
    def __init__(self, **properties):
        pass
    
class Container(Box):
    def add(self, box):
        self._add(box)
    
class Column(Container):
    def __init__(self, *components, **properties):
        PrtMFObject.__init__(self)
        if properties:
            self.set(**properties)
        for component in components:
            self.add(component)
            
    def add_footer(self, box):
        self._add(box,'footer')
        
    def add_header(self, box):
        self._add(box,'header')
        
    def newpage(self):
        self._add(None, 'newpage')
        
    def page(self):
        self._add(None, 'page')
        
    def page0(self):
        self._add(None, 'page0')
        
    def set(self, **properties):
        self._set(**properties)
    
class Crossref(PrtMFObject):
    def __init__(self, name, size=None, format=None):
        PrtMFObject.__init__(self)
        self._set(name=name, size=size, format=format)
    
class Expandable(Box):
    pass
    
class FillPattern(PrtMFObject):
    pass
    
class Footer(Box):
    def __init__(self, box=None, **properties):
        PrtMFObject.__init__(self)
        self._set(**properties)
        if box: self._add(box)
        
    def set(self, **properties):
        self._set(**properties)
        
    def add(self, box):
        self._add(box)
    
class Graph(PrtMFObject):
    pass
    
class Area(Graph):
    def __init__(self, fill=None):
        PrtMFObject.__init__(self)
        self._set(fill=fill)
    
class Bar(Graph):
    pass
    
class Graphic(PrtMFObject):
    pass
    
class Header(Box):
    def __init__(self, box=None, **properties):
        PrtMFObject.__init__(self)
        #import traceback
        #traceback.print_stack()
        #print "Creating HEADER"
        self._set(**properties)
        if box: self._add(box)
        
    def set(self, **properties):
        self._set(**properties)
        
    def add(self, box):
        self._add(box)
    
class Image(Box):
    def __init__(self, path, width=None, height=None, name=None, **properties):
        PrtMFObject.__init__(self)
        self._set(path=path, width=width, height=height, name=name, **properties)
        
    def set(self, **properties):
        self._set(**properties)
        
    
class ImagePattern(FillPattern):
    pass
    
class Isolate(Box):
    def __init__(self, box, **properties):
        PrtMFObject.__init__(self)
        self._set(**properties)
        self._add(box)
        
    def set(self, **properties):
        self._set(self, **properties)
        
    
class Layer(PrtMFObject):
    def __init__(self, **properties):
        PrtMFObject.__init__(self)
        self._set(**properties)
    
class Combine(Layer):
    def __init__(self, *layers, **properties):
        PrtMFObject.__init__(self)
        raise NotImplementedError()
    
class Limit(Graph):
    pass
    
class Line(Graph):
    def __init__(self, width=1, colour=None):
        PrtMFObject.__init__(self)
        self._set(width=width, colour=colour)
    
class Marker(Graph):
    def __init__(self, **properties):
        PrtMFObject.__init__(self)
        self._set(**properties)
    
class Move(PrtMFObject):
    def __init__(self, x, y):
        PrtMFObject.__init__(self)
        self._set(x=x, y=y)
    
class Pattern(FillPattern):
    def __init__(self, background=None):
        PrtMFObject.__init__(self)
        self._set(background=background)
        
    def hline(self, **properties):
        self._add(None, 'hline', **properties)
        
    def vline(self, distance, **properties):
        self._add(None, 'vline', **properties)
        
class PublisherError(object):
    pass
    
class ImageError(PublisherError):
    pass
    
A4 = 'A4'
LETTER = 'LETTER'
LEGAL = 'LEGAL'
A3 = 'A3'
B5 = 'B5'
C5 = 'C5'
DL = 'DL'
EXECUTIVE = 'EXECUTIVE'
PORTRAIT = 'PORTRAIT'
LANDSCAPE = 'LANDSCAPE'
  
class Report(Column):
    def __init__(self):
        import os
        PrtMFObject.__init__(self)
        self._args = {}
        for v in ('CARMUSR', 'CARMSYS', 'USER', 'HOST'):
            if os.environ.has_key(v):
                self._set(**{v : os.environ[v]})
    def create(self):
        raise NotImplementedError()
        
    def set(self, **properties):
        self._set(**properties)
        
    def arg(self, name):
        return self._args.get(name, None)
    
    def setpaper(self, orientation, size=A4):
        self._set(orientation=orientation, size=size)
        
    def _write(self, f, indent=0):
        f.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
        Column._write(self, f, indent)
    
class Row(Container):
    def __init__(self, *components, **properties):
        PrtMFObject.__init__(self)
        if properties:
            self.set(**properties)
        for component in components:
            self.add(component)
            
    def add(self, box):
        self._add(box)
        
    def set(self, **properties):
        self._set(**properties)
        
class Series(Layer):
    def __init__(self, data, **properties):
        PrtMFObject.__init__(self)
        self._set(**properties)

    def aggregate(self, x, ys):
        self._add(None, 'aggregate', x=x, ys=ys)
        
class Text(Box):
    def __init__(self, *texts, **properties):
        PrtMFObject.__init__(self)
        if properties:
            self.set(**properties)
        for text in texts:
            self._add(text)
            
    def set(self, **properties):
        self._set(**properties)
        
class UsageError(PublisherError):
    pass
    
# Pseudo-classes (is really functions within PRT)
class border(PrtMFObject):
    def __init__(self, left=None, top=None, right=None, bottom=None, **properties):
        PrtMFObject.__init__(self)
        self._set(**properties)
        if left != None: self._set(left=left)
        if top != None: self._set(top=top)
        if right != None: self._set(right=right)
        if bottom != None: self._set(bottom=bottom)
        
def border_all(w=1, colour='#000000'):
    if colour != '#000000':
        return border(left=w, top=w, right=w, bottom=w, inner_floor=w, inner_wall=w, colour=colour)
    else:
        return border(left=w, top=w, right=w, bottom=w, inner_floor=w, inner_wall=w)
        
def border_frame(w=1, colour='#000000'):
    if colour != '#000000':
        return border(left=w, top=w, right=w, bottom=w, colour=colour)
    else:
        return border(left=w, top=w, right=w, bottom=w)
        
class font(PrtMFObject):
    def __init__(self, **properties):
        PrtMFObject.__init__(self)
        self._set(**properties)
        
Font = font
        
class link(PrtMFObject):
    def __init__(self, module, params={}, context=None):
        PrtMFObject.__init__(self)
        self._set(module=module)
        if params: self._set(params=params)
        if context: self._set(context=context)
        
class padding(PrtMFObject):
    def __init__(self, left=None, top=None, right=None, bottom=None):
        PrtMFObject.__init__(self)
        if left != None: self._set(left=left)
        if top != None: self._set(top=top)
        if right != None: self._set(right=right)
        if bottom != None: self._set(bottom=bottom)

def url(path, params={}):
    if params:
        path += "?" + '&'.join(["%s=%s" % (x, params[x]) for x in params])
    return path
        
def subreport(box, name, newpage=False):
    box._add(ReportDelimiter(name))
        
def generateReport(*args, **kwargs):
    raise UsageError
        