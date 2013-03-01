# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

class PageItem(object):
    def __init__(self, report_item):
        self.top = report_item.get_element("Top").value()
        self.left = report_item.get_element("Left").value()
        self.height = report_item.get_element("Height").value()
        self.width = report_item.get_element("Width").value()

        self.style = StyleItem(report_item.get_element("Style"))


class PageLine(PageItem):
    def __init__(self, report_item):
        super(PageLine, self).__init__(report_item)


class PageRectangle(PageItem):
    def __init__(self, report_item):
        super(PageRectangle, self).__init__(report_item)


class StyleItem(object):
    def __init__(self, style):
        self.border_color = BorderColor(style.get_element("BorderColor"))
        self.border_style = BorderStyle(style.get_element("BorderStyle"))
        self.border_width = BorderWidth(style.get_element("BorderWidth"))
        self.background_color = get_color(style.get_element("BackgroundColor"))


class BorderInfo(object):
    def __init__(self, element):
        # get element definition
        self.default = element.get_element('Default')
        self.left = element.get_element('Left')
        self.right = element.get_element('Right')
        self.top = element.get_element('Top')
        self.bottom = element.get_element('Bottom')


class BorderColor(BorderInfo):
    def __init__(self, element):
        super(BorderColor, self).__init__(element)

        # Convert from element to ColorItem()
        self.default = get_color(self.default)
        self.left = get_color(self.left)
        self.right = get_color(self.right)
        self.top = get_color(self.top)
        self.bottom = get_color(self.bottom)


class BorderStyle(BorderInfo):
    def __init__(self, element):
        super(BorderStyle, self).__init__(element)

        # Convert from element to BorderStyleItem()
        self.default = get_border_style(self.default)
        self.left = get_border_style(self.left)
        self.right = get_border_style(self.right)
        self.top = get_border_style(self.top)
        self.bottom = get_border_style(self.bottom)


class BorderWidth(BorderInfo):
    def __init__(self, element):
        super(BorderWidth, self).__init__(element)

        # Convert from element to SizeItem()
        self.default = get_size_item(self.default)
        self.left = get_size_item(self.left)
        self.right = get_size_item(self.right)
        self.top = get_size_item(self.top)
        self.bottom = get_size_item(self.bottom)

class ColorItem(object):
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

class BorderStyleItem(object):
    def __init__(self, border_style=None):
        self.value=None
        if border_style:
            self.value = border_style.value()

class SizeItem(object):
    def __init__(self, size=None):
        self.value=None # Value in millimeters
        if size:
            self.value = size.value() 

def get_color(el):
    if not el:
        return None 
    return ColorItem(el)

def get_border_style(el):    
    if not el:
        return None 
    return BorderStyleItem(el)

def get_size_item(el):
    if not el:
        return None 
    return SizeItem(el)

