"""
Support classes and functions for the alertness reports.
"""

import Crs
import Gui
import Cui

import carmensystems.publisher.api as prt

def get_current_area():
    '''
    Returns the area currently associated with default_context.
    '''

    return Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)

def get_opposite_area(area = Cui.CuiWhichArea):
    """
    Returns the id of an opposite area. If no opposite area 
    exists a new one is created.

    :param area: The area whose opposite we want.
    :type area: :carmsys_man:`CuiAreaId`
    :rtype: :carmsys_man:`CuiAreaId`
    """
    
    if area == Cui.CuiWhichArea:
        area = get_current_area()
    
    for area_candidate in range(Cui.CuiAreaN):
        area_mode = Cui.CuiGetAreaMode(Cui.gpc_info, area_candidate)
        if area_mode != None and area != area_candidate:
            return area_candidate

    return create_new_area()

def area_exists(area):
    """
    Checks if an area exists.
    
    :param area: Area to check.
    :type area: :carmsys_man:`CuiAreaId`
    :rtype: `bool`
    """
    ret = not Cui.CuiAreaExists({"WRAPPER" : Cui.CUI_WRAPPER_NO_EXCEPTION},
                                    Cui.gpc_info, area)

    return ret

def get_first_area(mode):
    """
    Returns the first area with the requested mode. If the area 
    does not exist, ``CuiNoArea`` is returned (see :carmsys_man:`CuiAreaId`).

    :param mode: The requested area mode (e.g Cui.CrrMode)
    :type mode: :carmsys_man:`AreaMode`
    :rtype: :carmsys_man:`CuiAreaId`
    """
    for studio_area in range(Cui.CuiAreaN):
        if Cui.CuiGetAreaMode(Cui.gpc_info, studio_area) == mode:
            return studio_area
    return Cui.CuiNoArea
    
def get_area_modes():
    """
    Returns a list with information about the mode of all 
    the areas in Studio. See :carmsys_man:`AreaMode`.

    :return: A list of :carmsys_man:`AreaMode`'s
    :rtype: `list`
    """
    modes = []
    for studio_area in range(Cui.CuiAreaN): 
        modes.append(Cui.CuiGetAreaMode(Cui.gpc_info, studio_area))
    return modes

def create_new_area():
    """
    Creates a new area.
    Note that max 4 areas are supported by Studio.
    
    :returns: The AreaId of the newly created area.
    :rtype: :carmsys_man:`CuiAreaId`
    :raise CuiException: Raised if trying to create a 5th area
    """
    current_mode = get_area_modes()
    Cui.CuiOpenArea(Cui.gpc_info, 0)
    new_mode = get_area_modes()
    for area in range(Cui.CuiAreaN):
        if current_mode[area] != new_mode[area]: 
            return area


class StudioPalette(object):
    """
    This class will hold all available studio colors
    use:

    color = studio_palette.get_color('DarkRed')
    color = studio_palette.get_color('Sunday')
    color = studio_palette.get_color_by_name('Yellow')
    color = studio_palette.get_color_by_resource('Leg_in_RTD')
    color = studio_palette.get_color_by_number(5)
    color = studio_palette.get_color_by_number('5')

    Note: Magic negative numbers will not work,
          e.g. -1 for normal leg color
    """
        
    def __init__(self):
        # This will make color_by_name('DarkRed') available

        # Retrieve all Studio colours
        ln = [Gui.GuiColorNumber2Name(i) for i in range(Gui.C_MAX_COLORS)]
        lv = [Gui.GuiColorName2ColorCode(n) for n in ln]
        self._color_by_name = dict(zip(ln,lv))

        # Add Jeppesen Corporate colours
        self._color_by_name['JeppesenBlue'] = '#3366CC'
        self._color_by_name['JeppesenLightBlue'] = '#8DBCD4'
        self._color_by_name['ReportBlue'] = '#77AAFF'
        self._color_by_name['ReportLightBlue'] = '#CFDDEF'

        # This will make color_by_number('5') available
        self._color_by_number = {}
        for number in xrange(1,33):
            name = Crs.CrsGetModuleResource('colours',
                                            Crs.CrsSearchModuleDef,
                                            'Rule_color_%i' % number)
            code = Gui.GuiColorName2ColorCode(name)
            self._color_by_number[str(number)] = code


        # This will make color_by_name('Sunday') available
        # Retrive all the Studio colour resources
        self._color_by_resource = {}
        resource = Crs.CrsGetFirstResourceInfo() 
        while resource: 
            if (resource.module == "colours"
                and resource.application == "default"):  
                self._color_by_resource[resource.name] = self._color_by_name[resource.rawValue]
            resource = Crs.CrsGetNextResourceInfo()

        # Loop again to make the more detailed 'gpc' resource
        # override the 'default' ones
        resource = Crs.CrsGetFirstResourceInfo() 
        while resource: 
            if (resource.module == "colours"
                and resource.application == "gpc"):  
                self._color_by_resource[resource.name] = self._color_by_name[resource.rawValue]
            resource = Crs.CrsGetNextResourceInfo()


    def get_color(self, key):
        """
        main method to retrieve colour codes
        @param key: the color name, resource name or number of the color
        @type key: string or int
        @return: the color code ('#3366CC'), defaults is Black
        @rtype: string
        """
        key = str(key)
        if self._color_by_name.has_key(key):
            return self._color_by_name[key]
        elif self._color_by_number.has_key(key):
            return self._color_by_number[key]
        elif self._color_by_resource(key):
            return self._color_by_resource[key]
        else:
            return self._color_by_name['Black']

    def get_color_by_name(self, key):
        """
        method to retrieve colour codes using color names
        @param key: the color name of the color
        @type key: string
        @return: the color code ('#3366CC'), defaults is Black
        @rtype: string
        """
        if self._color_by_name.has_key(key):
            return self._color_by_name[key]
        else:
            return self._color_by_name['Black']

    def get_color_by_resource(self, key):
        """
        method to retrieve colour codes using color resource names
        @param key: the resource name of the color
        @type key: string
        @return: the color code ('#3366CC'), defaults is Black
        @rtype: string
        """
        if self._color_by_resource.has_key(key):
            return self._color_by_resource[key]
        else:
            return self._color_by_name['Black']


    def get_color_by_number(self, key):
        """
        method to retrieve colour codes using color numbers
        @param key: the color number as defined by the Rave resources
        @type key: string
        @return: the color code ('#3366CC'), defaults is Black
        @rtype: string
        """
        if self._color_by_number.has_key(key):
            return self._color_by_number[key]
        else:
            return self._color_by_name['Black']


    def get_all_colors(self):
        """
        method to retrive all color codes as an iterator
        @return: iterator with all color codes
        @rtype: itertor of strings
        """
        return self._color_by_name.itervalues()

# Create the instance
studio_palette = StudioPalette()

class SimpleTable(prt.Column):
    """
    The simple table class makes it easier to create simple tables
    with a standardized format:
    Bold Header on ReportBlue background
    [Label | data] on alternating White and ReportLightBlue bg
    Single frame around the table
    """
    def __init__(self, title, cross_name='', use_page=True,
                 expandable=False, image='table.jpg'):
        """
        @param title: The header name of the table
        @type title: prt.Box or string
        @param cross_name: prt object name of the SimpleTable instance
                           used together with prt.Crossref()
        @type cross_name: string
        @param use_page: Should page0 breaks be added, default True
        @type use_page: Boolean
        @param expandable: Specifies whether the data section should be
                           expandable. NOTE: this does not work well with sorting
                           or any linking back to this report
        @type expandable: Boolean
        @param image: image to be shown instead of the default table icon
        @type image: string
        """
        prt.Column.__init__(self)
        self.use_page = use_page
        self.image = image

        self.num_rows = 0
        self.set(border=prt.border_frame(1))

        # The title_row will make sure the background is completely colored
        self.title_row = prt.Row(font=prt.font(size=10, weight=prt.BOLD),
                                 background=studio_palette.\
                                 get_color_by_name('ReportBlue')
                                 )
        # The title contains the actual objects (icon + texts)
        # which will be isolated from the rest of the table
        self.title = prt.Row(prt.Image(self.image,
                                       name=cross_name,
                                       padding=prt.padding(2,2,2,2)))
        self.title_row.add(prt.Isolate(self.title))

        self.add_title(title)
                
        self.link_row = prt.Row(font=prt.font(size=8),
                                background=studio_palette.\
                                get_color_by_name('Grey'),
                                border=prt.border(bottom=2,
                                                  colour=studio_palette.\
                                                  get_color_by_name('DarkGrey')))
        self.num_link = 0

        self.sub_title = prt.Row(font=prt.font(size=6),
                                 border=prt.border(bottom=2,
                                                   colour=studio_palette.\
                                                   get_color_by_name('DarkGrey')),
                                 background=studio_palette.\
                                 get_color_by_name('ReportBlue'))
        self.num_st = 0


        self.table = prt.Column()

        if expandable:
            prt.Column.add(self, prt.Expandable(self.title_row,
                                                self.table,
                                                background=studio_palette.\
                                                get_color_by_name('ReportBlue')))
        else:
            prt.Column.add(self, self.title_row)
            prt.Column.add(self, self.table)


        #self.table.add(self.link_row), added later if needed
        #self.table.add(self.sub_title), added later if needed

    def add_title(self, title):
        """
        Method to add table headers
        @param title: column header
        @type title: string or report object

        @returns: the title object that was just added
        @rtype: report object
        """
        return self.title.add(prt.Isolate(title))
 
    def add_link(self, link):
        """
        Method to add links and arrow image to other versions
        or other reports
        @param link: the link to the other report, or header text
        @type link: prt link object, string

        @returns: the link that was just added
        @rtype: report object
        """
        if self.num_link == 0:
            self.table.add(self.link_row)

        if isinstance(link, str):
            ret = prt.Text(link) # Makes it possible to add a link header
        else:
            ret = prt.Row(prt.Image('arrow.jpg',
                                    valign=prt.CENTER,
                                    align=prt.RIGHT),
                          link) # Assume proper link object
            
        self.link_row.add(ret)
        self.num_link += 1

        return ret

    
    def add_sub_title(self, sub_title):
        """
        Method to add column headers
        @param sub_title: column header
        @type sub_title: string or report object

        @returns: the sub title that was just added
        @rtype: report object
        """
        if self.num_st == 0:
            self.table.add(self.sub_title)
                    
        if isinstance(sub_title, str):
            ret = prt.Text(sub_title)
        else:
            ret = sub_title # Assume report object
            
        self.sub_title.add(ret)
        self.num_st += 1

        return ret

    
    def add(self, row):
        """
        Method to add one table row of data
        @param row: data row to add to the table
        @type row: report ojbect or string
        @returns: the same row that was just added
        @rtype: report row
        """
        
        if isinstance(row, prt.Row):
            ret = row
        else:
            ret = prt.Row(row)
        
        ret.set(background=[studio_palette.get_color_by_name('White'),
                            studio_palette.get_color_by_name('ReportLightBlue')] \
                [self.num_rows % 2])

        self.table.add(ret)
        self.num_rows += 1

        # Decrease risk of having single rows on next page
        if self.use_page and self.num_rows % 5 == 0:
            self.table.page0()

        return ret


class SimpleDiagram(SimpleTable):
    """
    The simple diagram class inherits from SimpleTable and will override
    the icon to display a diagram image instead.
    """
    def __init__(self, title, cross_name=''):
        """
        @param title: The header name of the table
        @type title: prt.Box or string
        @param cross_name: prt object name of the SimpleDiagram instance
                           used together with prt.Crossref()
        @type cross_name: string
        """
        SimpleTable.__init__(self, title, cross_name=cross_name,
                             use_page=False, expandable=False,
                             image='diagram.jpg')

