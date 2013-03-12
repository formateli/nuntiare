# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from nuntiare import logger
from nuntiare.definition.size import Size
from nuntiare.definition.string import String
from nuntiare.definition.color import Color
from nuntiare.tools import get_element_from_parent, inch_2_mm

color_list = {}
border_style_list = {}
border_width_list = {}

def get_color_info(id, obj):
    '''
    Returns a cached ColorInfo object. 
    Creates a new one if not exists.
    id: It is the hex_alpha name. Ex: #FF000000
    '''
    return get_style_item('color', id, obj)

def get_border_style_info(id, obj):
    '''
    Returns a cached BorderStyleInfo object. 
    Creates a new one if not exists.
    id: It is the border style name. Ex: None, Dotted, Dashed, Solid
    '''
    return get_style_item('border_style', id, obj)

def get_border_width_info(id, obj):
    '''
    Returns a cached BorderWidthInfo object. 
    Creates a new one if not exists.
    id: It is the size in millimeters
    '''
    return get_style_item('border_width', id, obj)

def get_style_item(name, id, obj):
    item_list = None
    if name == 'color':
        item_list = color_list
    elif name == 'border_style':
        item_list = border_style_list
    elif name == 'border_width':
        item_list = border_width_list

    if item_list.has_key(id):
        logger.debug("Returning item_list '{0}': '{1}'".format(name, id))
        return item_list[id] 

    logger.debug("Creating item_list '{0}': '{1}'".format(name, id))
    if obj:
        item_list[id] = obj
    else:
        if name == 'color':
            item_list[id] = ColorInfo(Color(id))
        elif name == 'border_style':
            item_list[id] = StyleItem(String(id))
        elif name == 'border_width':
            item_list[id] = StyleItem(Size(id))
    return item_list[id]

def get_color_by_element(el):
    if not el:
        return None 
    c = el.value()
    return get_color_info(c['hex_alpha'], ColorInfo(el))
    
def get_border_style_width_by_element(name, el):
    if not el:
        return None
    item = StyleItem(el)
    return get_style_item(name, item.value, item)


class StyleInfo(object):
    def __init__(self, style):
        self.border_color = BorderColorInfo(get_element_from_parent(style, "BorderColor"))
        self.border_style = BorderStyleInfo(get_element_from_parent(style, "BorderStyle"))
        self.border_width = BorderWidthInfo(get_element_from_parent(style, "BorderWidth"))
        self.background_color = get_color_by_element(get_element_from_parent(style, "BackgroundColor"))


class BorderInfo(object):
    def __init__(self, element):
        # get element definition
        self.default = get_element_from_parent(element, 'Default')
        self.left = get_element_from_parent(element, 'Left')
        self.right = get_element_from_parent(element, 'Right')
        self.top = get_element_from_parent(element, 'Top')
        self.bottom = get_element_from_parent(element, 'Bottom')

    def set_default(self):
        if not self.left:
            self.left = self.default
        if not self.right:
            self.right = self.default
        if not self.top:
            self.top = self.default
        if not self.bottom:
            self.bottom = self.default


class BorderStyleInfo(BorderInfo):
    def __init__(self, element):
        super(BorderStyleInfo, self).__init__(element)

        self.default = get_border_style_width_by_element('border_style', self.default)
        if not self.default:
            self.default = get_border_style_info('None', None)
        self.left = get_border_style_width_by_element('border_style', self.left)
        self.right = get_border_style_width_by_element('border_style', self.right)
        self.top = get_border_style_width_by_element('border_style', self.top)
        self.bottom = get_border_style_width_by_element('border_style', self.bottom)
        self.set_default()


class BorderWidthInfo(BorderInfo):
    def __init__(self, element):
        super(BorderWidthInfo, self).__init__(element)

        self.default = get_border_style_width_by_element('border_width', self.default)
        if not self.default:
            self.default = get_border_width_info('1 pt', None)
        self.left = get_border_style_width_by_element('border_width', self.left)
        self.right = get_border_style_width_by_element('border_width', self.right)
        self.top = get_border_style_width_by_element('border_width', self.top)
        self.bottom = get_border_style_width_by_element('border_width', self.bottom)
        self.set_default()


class BorderColorInfo(BorderInfo):
    def __init__(self, element):
        super(BorderColorInfo, self).__init__(element)

        self.default = get_color_by_element(self.default)
        if not self.default:
            self.default = get_color_info('#FF000000', None)
        self.left = get_color_by_element(self.left)
        self.right = get_color_by_element(self.right)
        self.top = get_color_by_element(self.top)
        self.bottom = get_color_by_element(self.bottom)
        self.set_default()


class StyleItem(object):
    def __init__(self, style_item=None):
        self.value=None
        if style_item:
            self.value = style_item.value()


class ColorInfo(object):
    def __init__(self, color=None):
        # Black full opaque  
        self.hex = "#000000"
        self.hex_alpha = "#FF000000"
        self.red_int = 0
        self.green_int = 0
        self.blue_int = 0
        self.alpha_int = 255
        self.red = 0
        self.green = 0
        self.blue = 0
        self.alpha = 65535
        
        if color:
            v = color.value()
            self.hex = v['hex']
            self.hex_alpha = v['hex_alpha']
            self.red_int = v['red_int']
            self.green_int = v['green_int']
            self.blue_int = v['blue_int']
            self.alpha_int = v['alpha_int']
            self.red = v['red']
            self.green = v['green']
            self.blue = v['blue']
            self.alpha = v['alpha']


