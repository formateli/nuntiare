# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from .. definition.expression import Expression, Size, String

class Style(object):
    '''
    Style cache. Must be one instance per report.    
    See: nuntiare.report.Report
    '''
    
    _colors={}          #
    _border_styles={}   # Class cache. Shared with all reports
    _sizes={}           #
    _texts={}           #
    
    def __init__(self, report):
        self._report=report #
        self._id_count=-1   # Report cache
        self.styles={}     #

    @staticmethod
    def _get_color(report, color_element, force=False):    
        if not color_element and not force:
            return None
        color = _ColorInfo(report, color_element)
        if color.hex_alpha in Style._colors:
            return Style._colors[color.hex_alpha]
        Style._colors[color.hex_alpha] = color
        return color

    @staticmethod
    def _get_border_style(report, border_style_element, default=None):
        if not border_style_element and not default:
            return None
        border_tyle = _BorderStyleInfo(report, border_style_element, default)
        if border_tyle.value in Style._border_styles:
            return Style._border_styles[border_tyle.value]
        Style._border_styles[border_tyle.value] = border_tyle
        return border_tyle

    @staticmethod
    def _get_size(report, size_element, default=None):
        if not size_element and not default:
            return None
        size = _SizeInfo(report, size_element, default)
        if size.value in Style._sizes:
            return Style._sizes[size.value]
        Style._sizes[size.value] = size
        return size

    @staticmethod
    def _get_text(report, text_element):
        if not text_element:
            return None
        text = _TextInfo(report, text_element)
        if text.sid in Style._texts:
            return Style._texts[text.sid]
        Style._texts[text.sid] = text
        return text

    def get_style_info(self, style_def):
        st = _StyleInfo(self._report, style_def)
        if st.sid in self.styles:
            return self.styles[st.sid]
        sid = self._id_count + 1
        st.id = sid
        self.styles[st.sid] = st
        self._id_count = sid
        return st

     
class _StyleInfo(object):
    def __init__(self, report, style_def):
        self.id = None # Assigned by Style class
        self.sid = ""
        self.border = None
        self.background_color = None
        self.text = None
    
        if not style_def:
            return
    
        self.border = _BorderInfo(report, style_def.get_element("Border"), 
                                style_def.get_element("TopBorder"), 
                                style_def.get_element("BottomBorder"), 
                                style_def.get_element("LeftBorder"), 
                                style_def.get_element("RightBorder"))
        self.background_color = Style._get_color(report, style_def.get_element("BackgroundColor"))
        self.text = Style._get_text(report, style_def)
        
        self.sid ="{0}|{1}|{2}".format(
                self.border.sid, 
                self.background_color.value if self.background_color else "", 
                self.text.sid
            )


class _BorderInfo(object):
    def __init__(self, report, default_def, 
            top_def, bottom_def, left_def, right_def):
            
        self.color = _BorderColorInfo(report, 
                                    default_def.get_element("Color") if default_def else None, 
                                    top_def.get_element("Color") if top_def else None,
                                    bottom_def.get_element("Color") if bottom_def else None,
                                    left_def.get_element("Color") if left_def else None,
                                    right_def.get_element("Color") if right_def else None)
        self.style = _BorderStyleStyleInfo(report, 
                                    default_def.get_element("BorderStyle") if default_def else None, 
                                    top_def.get_element("BorderStyle") if top_def else None,
                                    bottom_def.get_element("BorderStyle") if bottom_def else None,
                                    left_def.get_element("BorderStyle") if left_def else None,
                                    right_def.get_element("BorderStyle") if right_def else None)
        self.width = _BorderWidthInfo(report, 
                                    default_def.get_element("Width") if default_def else None, 
                                    top_def.get_element("Width") if top_def else None,
                                    bottom_def.get_element("Width") if bottom_def else None,
                                    left_def.get_element("Width") if left_def else None,
                                    right_def.get_element("Width") if right_def else None)

        self.sid = "{0}-{1}-{2}".format(
                self.color.sid, self.style.sid, self.width.sid
            )


class _BorderInfoDet(object):
    def __init__(self, default_def, 
            top_def, bottom_def, left_def, right_def):
        # get element definition
        self._default = default_def
        self.top = top_def
        self.bottom = bottom_def
        self.left = left_def
        self.right = right_def
        self.sid=None

    def set_default(self):
        self.sid = str(self._default.value)
        self.left=self._set_default(self.left)
        self.right=self._set_default(self.right)
        self.top=self._set_default(self.top)
        self.bottom=self._set_default(self.bottom)
            
    def _set_default(self, value):
        if value:
            self.sid = self.sid + "-" + str(value.value)
        else:
            value = self._default
            self.sid = self.sid + "-?"
        return value


class _BorderStyleStyleInfo(_BorderInfoDet):
    def __init__(self, report, default_def, 
            top_def, bottom_def, left_def, right_def):
            
        super(_BorderStyleStyleInfo, self).__init__(default_def, 
                top_def, bottom_def, left_def, right_def)

        self._default = Style._get_border_style(report, self._default)
        if not self._default:
            self._default = Style._get_border_style(report, None, "None")
        self.left = Style._get_border_style(report, self.left)
        self.right = Style._get_border_style(report, self.right)
        self.top = Style._get_border_style(report, self.top)
        self.bottom = Style._get_border_style(report, self.bottom)
        self.set_default()


class _BorderWidthInfo(_BorderInfoDet):
    def __init__(self, report, default_def, 
            top_def, bottom_def, left_def, right_def):
            
        super(_BorderWidthInfo, self).__init__(default_def, 
                top_def, bottom_def, left_def, right_def)

        self._default = Style._get_size(report, default_def)
        if not self._default:
            self._default = Style._get_size(report, None, "1pt")
        self.left = Style._get_size(report, self.left)
        self.right = Style._get_size(report, self.right)
        self.top = Style._get_size(report, self.top)
        self.bottom = Style._get_size(report, self.bottom)
        self.set_default()


class _BorderColorInfo(_BorderInfoDet):
    def __init__(self, report, default_def, 
            top_def, bottom_def, left_def, right_def):
            
        super(_BorderColorInfo, self).__init__(default_def, 
                top_def, bottom_def, left_def, right_def)

        self._default = Style._get_color(report, self._default)
        if not self._default:
            self._default = Style._get_color(report, None, force=True) # Returns black
        self.left = Style._get_color(report, self.left)
        self.right = Style._get_color(report, self.right)
        self.top = Style._get_color(report, self.top)
        self.bottom = Style._get_color(report, self.bottom)
        self.set_default()


class _BorderStyleInfo(object):
    def __init__(self, report, style_element=None, default=None):
        self.value=None
        if style_element:
            self.value = style_element.value(report)
        if not style_element and default:
            style = String(default, True)
            self.value = style.value(report)


class _SizeInfo(object):
    def __init__(self, report, size_element=None, default=None):
        self.value=None
        if size_element:
            self.value = size_element.value(report)
        if not size_element and default:
            size = Size(default, True)
            self.value = size.value(report)


class _ColorInfo(object):
    def __init__(self, report, color_element=None):
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
        
        if color_element:
            v = color_element.value(report)
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
            
        self.value=self.hex_alpha


class _TextInfo(object):
    def __init__(self, report, element):
        self.sid=""
    
        self.font_family = Expression.get_value_or_default(
                report, element, 'FontFamily', 'Arial')
        self.sid = self.sid + self.font_family

        # Normal | Italic
        self.font_style = Expression.get_value_or_default(
                report, element, 'FontStyle', 'Normal')
        self.sid = self.sid + "-" + self.font_family

        self.font_size = Style._get_size(report, element.get_element("FontSize"), "10pt").value
        self.sid = self.sid + "-" + str(self.font_size)
        
        # Lighter | Normal | Bold | Bolder | 100 | 
        # 200 | 300 | 400 | 500 | 600 |700 | 800 | 900
        self.font_weight = Expression.get_value_or_default(
                report, element, 'FontWeight', 'Normal')
        self.sid = self.sid + "-" + self.font_weight
                
        self.format = Expression.get_value_or_default(
                report, element, 'Format', None)
        if self.format==None:        
            self.sid = self.sid + "-?"
        else:
            self.sid = self.sid + "-" + self.format
                
        # Underline | Overline | LineThrough | None
        self.text_decoration = Expression.get_value_or_default(
                report, element, 'TextDecoration', 'None') 
        self.sid = self.sid + "-" + self.text_decoration
                
        # General | Left | Right | Center | Justify
        self.text_align = Expression.get_value_or_default(
                report, element, 'TextAlign', 'General')
        self.sid = self.sid + "-" + self.text_align
                
        # Top | Middle | Bottom
        self.vertical_align = Expression.get_value_or_default(
                report, element, 'VerticalAlign', 'Top') 
        self.sid = self.sid + "-" + self.vertical_align

        # Foreground color. Default Black
        color = Style._get_color(report, element.get_element("Color"))
        if not color:
            color =  Style._get_color(report, None, force=True) # Returns black
        self.color = color.value    
        self.sid = self.sid + "-" + self.color

        self.padding_top = Style._get_size(report, element.get_element("PaddingTop"), "0pt").value 
        self.padding_left = Style._get_size(report, element.get_element("PaddingLeft"), "0pt").value 
        self.padding_right = Style._get_size(report, element.get_element("PaddingRight"), "0pt").value 
        self.padding_bottom = Style._get_size(report, element.get_element("PaddingBottom"), "0pt").value 
        self.sid = "{0}-{1}-{2}-{3}-{4}".format(self.sid,
            self.padding_top, self.padding_left,
            self.padding_right, self.padding_bottom)
            
        
