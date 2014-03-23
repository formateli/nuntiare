# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from nuntiare.definition.size import Size
from nuntiare.definition.string import String
from nuntiare.definition.color import Color
from nuntiare.tools import get_element_from_parent, get_expression_value_or_default

# Cache of objects
color_list = {}
style_list = {}
size_list = {}

def get_color_info(id, obj):
    '''
    Returns a cached ColorInfo object. 
    Creates a new one if not exists.
    id: It is the hex_alpha name. Ex: #FF000000
    '''
    return get_style_item('color', id, obj)

def get_style_info(id, obj):
    '''
    Returns a cached BorderStyleInfo object. 
    Creates a new one if not exists.
    id: It is the border style name. Ex: None, Dotted, Dashed, Solid
    '''
    return get_style_item('style', id, obj)

def get_size_info(id, obj):
    '''
    Returns a cached BorderWidthInfo object. 
    Creates a new one if not exists.
    id: It is the size in millimeters
    '''
    return get_style_item('size', id, obj)

def get_style_item(name, id, obj):
    item_list = None
    if name == 'color':
        item_list = color_list
    elif name == 'style':
        item_list = style_list
    elif name == 'size':
        item_list = size_list

    if item_list.has_key(id):
        return item_list[id] 

    if obj:
        item_list[id] = obj
    else:
        if name == 'color':
            item_list[id] = ColorInfo(Color(id))
        elif name == 'style':
            item_list[id] = StyleItem(String(id))
        elif name == 'size':
            item_list[id] = StyleItem(Size(id))
    return item_list[id]

def get_color_by_element(el):
    if not el:
        return None 
    c = el.value()
    return get_color_info(c['hex_alpha'], ColorInfo(el))
    
def get_style_size_by_element(name, el):
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
        self.text = TextInfo(style)


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

        self.default = get_style_size_by_element('style', self.default)
        if not self.default:
            self.default = get_style_info('None', None)
        self.left = get_style_size_by_element('style', self.left)
        self.right = get_style_size_by_element('style', self.right)
        self.top = get_style_size_by_element('style', self.top)
        self.bottom = get_style_size_by_element('style', self.bottom)
        self.set_default()


class BorderWidthInfo(BorderInfo):
    def __init__(self, element):
        super(BorderWidthInfo, self).__init__(element)

        self.default = get_style_size_by_element('size', self.default)
        if not self.default:
            self.default = get_size_info('1 pt', None)
        self.left = get_style_size_by_element('size', self.left)
        self.right = get_style_size_by_element('size', self.right)
        self.top = get_style_size_by_element('size', self.top)
        self.bottom = get_style_size_by_element('size', self.bottom)
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


class TextInfo(object):
    def __init__(self, element):
        self.font_family = get_expression_value_or_default(element, 'FontFamily', 'Arial')

        # Normal | Italic
        self.font_style = get_expression_value_or_default(element, 'FontStyle', 'Normal')
        self.font_size = self.get_size('FontSize', element, '10 pt') 
        # Lighter | Normal | Bold | Bolder | 100 | 200 | 300 | 400 | 500 | 600 |700 | 800 | 900
        self.font_weight = get_expression_value_or_default(element, 'FontWeight', 'Normal')
        self.format = get_expression_value_or_default(element, 'Format', None)
        # Underline | Overline | LineThrough | None
        self.text_decoration = get_expression_value_or_default(element, 'TextDecoration', 'None') 
        # General | Left | Right | Center | Justify
        self.text_align = get_expression_value_or_default(element, 'TextAlign', 'General') 
        # Top | Middle | Bottom
        self.vertical_align = get_expression_value_or_default(element, 'VerticalAlign', 'Top') 

        # Foreground color. Default Black
        self.color = get_color_by_element(get_element_from_parent(element, "Color"))
        if not self.color:
            self.color =  get_color_info('#FF000000', None)

        self.padding_top = self.get_size('PaddingTop', element) 
        self.padding_left = self.get_size('PaddingLeft', element) 
        self.padding_right = self.get_size('PaddingRight', element) 
        self.padding_bottom = self.get_size('PaddingBottom', element) 

    def get_size(self, name, element, default='0 pt'):
        sz = get_style_size_by_element('size', get_element_from_parent(element, name))
        if not sz:  
            sz = get_size_info(default, None) 
        return sz

