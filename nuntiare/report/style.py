# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from .. definition.types.size import Size
from .. definition.types.string import String
from .. definition.types.color import Color
from .. tools import get_element_from_parent, get_expression_value_or_default

# Cache of objects
color_list = {}
style_list = {}
size_list = {}

def get_color_info(report, id, obj):
    '''
    Returns a cached ColorInfo object. 
    Creates a new one if not exists.
    id: It is the hex_alpha name. Ex: #FF000000
    '''
    return get_style_item(report, 'color', id, obj)

def get_style_info(report, id, obj):
    '''
    Returns a cached BorderStyleInfo object. 
    Creates a new one if not exists.
    id: It is the border style name. Ex: None, Dotted, Dashed, Solid
    '''
    return get_style_item(report, 'style', id, obj)

def get_size_info(report, id, obj):
    '''
    Returns a cached BorderWidthInfo object. 
    Creates a new one if not exists.
    id: It is the size in millimeters
    '''
    return get_style_item(report, 'size', id, obj)

def get_style_item(report, name, id, obj):
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
            item_list[id] = ColorInfo(report, Color(id, True))
        elif name == 'style':
            item_list[id] = StyleItem(report, String(id, True))
        elif name == 'size':
            item_list[id] = StyleItem(report, Size(id, True))
    return item_list[id]
    
def get_color_by_element(report, el):
    if not el:
        return None
    c = el.value(report)
    return get_color_info(report, c['hex_alpha'], ColorInfo(report, el))
    
def get_style_size_by_element(report, name, el):
    if not el:
        return None
    item = StyleItem(report, el)
    return get_style_item(report, name, item.value, item)


class StyleInfo(object):
    def __init__(self, report, style_def):
        self.border = BorderInfo(report, get_element_from_parent(style_def, "Border"), 
                                get_element_from_parent(style_def, "TopBorder"), 
                                get_element_from_parent(style_def, "BottomBorder"), 
                                get_element_from_parent(style_def, "LeftBorder"), 
                                get_element_from_parent(style_def, "RightBorder"))
        self.background_color = get_color_by_element(report, get_element_from_parent(style_def, "BackgroundColor"))
        self.text = TextInfo(report, style_def)


class BorderInfo(object):
    def __init__(self, report, default_def, top_def, bottom_def, left_def, right_def):
        self.color = BorderColorInfo(report, get_element_from_parent(default_def, "Color"), 
                                    get_element_from_parent(top_def, "Color"),
                                    get_element_from_parent(bottom_def, "Color"),
                                    get_element_from_parent(left_def, "Color"),
                                    get_element_from_parent(right_def, "Color"))
        self.style = BorderStyleInfo(report, get_element_from_parent(default_def, "Style"), 
                                    get_element_from_parent(top_def, "Style"),
                                    get_element_from_parent(bottom_def, "Style"),
                                    get_element_from_parent(left_def, "Style"),
                                    get_element_from_parent(right_def, "Style"))
        self.width = BorderWidthInfo(report, get_element_from_parent(default_def, "Width"), 
                                    get_element_from_parent(top_def, "Width"),
                                    get_element_from_parent(bottom_def, "Width"),
                                    get_element_from_parent(left_def, "Width"),
                                    get_element_from_parent(right_def, "Width"))
        

class BorderInfoDet(object):
    def __init__(self, default_def, top_def, bottom_def, left_def, right_def):
        # get element definition
        self.default = default_def
        self.top = top_def
        self.bottom = bottom_def
        self.left = left_def
        self.right = right_def

    def set_default(self):
        if not self.left:
            self.left = self.default
        if not self.right:
            self.right = self.default
        if not self.top:
            self.top = self.default
        if not self.bottom:
            self.bottom = self.default


class BorderStyleInfo(BorderInfoDet):
    def __init__(self, report, default_def, top_def, bottom_def, left_def, right_def):
        super(BorderStyleInfo, self).__init__(default_def, top_def, bottom_def, left_def, right_def)

        self.default = get_style_size_by_element(report, 'style', self.default)
        if not self.default:
            self.default = get_style_info(report, 'None', None)
        self.left = get_style_size_by_element(report, 'style', self.left)
        self.right = get_style_size_by_element(report, 'style', self.right)
        self.top = get_style_size_by_element(report, 'style', self.top)
        self.bottom = get_style_size_by_element(report, 'style', self.bottom)
        self.set_default()


class BorderWidthInfo(BorderInfoDet):
    def __init__(self, report, default_def, top_def, bottom_def, left_def, right_def):
        super(BorderWidthInfo, self).__init__(default_def, top_def, bottom_def, left_def, right_def)

        self.default = get_style_size_by_element(report, 'size', self.default)
        if not self.default:
            self.default = get_size_info(report, '1 pt', None)
        self.left = get_style_size_by_element(report, 'size', self.left)
        self.right = get_style_size_by_element(report, 'size', self.right)
        self.top = get_style_size_by_element(report, 'size', self.top)
        self.bottom = get_style_size_by_element(report, 'size', self.bottom)
        self.set_default()


class BorderColorInfo(BorderInfoDet):
    def __init__(self, report, default_def, top_def, bottom_def, left_def, right_def):
        super(BorderColorInfo, self).__init__(default_def, top_def, bottom_def, left_def, right_def)

        self.default = get_color_by_element(report, self.default)
        if not self.default:
            self.default = get_color_info(report, '#FF000000', None)
        self.left = get_color_by_element(report, self.left)
        self.right = get_color_by_element(report, self.right)
        self.top = get_color_by_element(report, self.top)
        self.bottom = get_color_by_element(report, self.bottom)
        self.set_default()


class StyleItem(object):
    def __init__(self, report, style_item=None):
        self.value=None
        if style_item:
            self.value = style_item.value(report)


class ColorInfo(object):
    def __init__(self, report, color=None):
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
            v = color.value(report)
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
    def __init__(self, report, element):
        self.font_family = get_expression_value_or_default(report, element, 'FontFamily', 'Arial')

        # Normal | Italic
        self.font_style = get_expression_value_or_default(report, element, 'FontStyle', 'Normal')
        self.font_size = self.get_size(report, 'FontSize', element, '10 pt') 
        # Lighter | Normal | Bold | Bolder | 100 | 200 | 300 | 400 | 500 | 600 |700 | 800 | 900
        self.font_weight = get_expression_value_or_default(report, element, 'FontWeight', 'Normal')
        self.format = get_expression_value_or_default(report, element, 'Format', None)
        # Underline | Overline | LineThrough | None
        self.text_decoration = get_expression_value_or_default(report, element, 'TextDecoration', 'None') 
        # General | Left | Right | Center | Justify
        self.text_align = get_expression_value_or_default(report, element, 'TextAlign', 'General') 
        # Top | Middle | Bottom
        self.vertical_align = get_expression_value_or_default(report, element, 'VerticalAlign', 'Top') 

        # Foreground color. Default Black
        self.color = get_color_by_element(report, get_element_from_parent(element, "Color"))
        if not self.color:
            self.color =  get_color_info(report, '#FF000000', None)

        self.padding_top = self.get_size(report, 'PaddingTop', element) 
        self.padding_left = self.get_size(report, 'PaddingLeft', element) 
        self.padding_right = self.get_size(report, 'PaddingRight', element) 
        self.padding_bottom = self.get_size(report, 'PaddingBottom', element) 

    def get_size(self, report, name, element, default='0 pt'):
        sz = get_style_size_by_element(report, 'size', get_element_from_parent(element, name))
        if not sz:  
            sz = get_size_info(report, default, None) 
        return sz

