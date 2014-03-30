# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import cairo
import pango
import pangocairo
from style import StyleInfo
from decimal import Decimal
from nuntiare.tools import raise_error_with_log, get_element_from_parent, \
    get_expression_value_or_default, get_size_in_unit, dot_2_mm, point_2_mm

class PageItem(object):
    def __init__(self, report_item, parent_top, parent_left):
        self.report_item = report_item
        self.top = get_expression_value_or_default(report_item, "Top", 0) + parent_top
        self.left = get_expression_value_or_default(report_item, "Left", 0) + parent_left
        self.height = get_expression_value_or_default(report_item, "Height", 0)
        self.width = get_expression_value_or_default(report_item, "Width", 0)        
        self.style = StyleInfo(get_element_from_parent(report_item, "Style"))


class PageLine(PageItem):
    def __init__(self, report_item, parent_top, parent_left):
        super(PageLine, self).__init__(report_item, parent_top, parent_left)


class PageRectangle(PageItem):
    def __init__(self, report_item, parent_top, parent_left):
        super(PageRectangle, self).__init__(report_item, parent_top, parent_left)


class PageText(PageItem):
    def __init__(self, report_item, parent_top, parent_left, height=None, width=None):
        super(PageText, self).__init__(report_item, parent_top, parent_left)
        self.value = get_expression_value_or_default(report_item, "Value", None)
        self.can_grow = get_expression_value_or_default(report_item, "CanGrow", False)
        self.can_shrink = get_expression_value_or_default(report_item, "CanShrink", False)

        # If it is in a cell item
        if height:
            self.height = height
        if width:
            self.width = width

        if self.can_grow or self.can_shrink: # We need to recalculate height
            self.height = self.get_height()

    def get_height(self):
        text = self.value
        if not text or text=="":
            return self.height
        top = get_size_in_unit(self.top, 'pt')
        left = get_size_in_unit(self.left, 'pt')
        height = get_size_in_unit(self.height, 'pt')
        width = get_size_in_unit(self.width, 'pt')

        padding_top = get_size_in_unit(self.style.text.padding_top.value, 'pt')
        padding_left = get_size_in_unit(self.style.text.padding_left.value, 'pt')
        padding_right = get_size_in_unit(self.style.text.padding_right.value, 'pt')
        padding_bottom = get_size_in_unit(self.style.text.padding_bottom.value, 'pt')
        max_height = height - padding_top - padding_bottom

        if max_height <= 0:
            raise_error_with_log("Textbox drawable height area must be greater than zero. See height and padding values.")

        font_sz = get_size_in_unit(self.style.text.font_size.value, 'pt')
        name_fd = pango.FontDescription(self.style.text.font_family)
        name_fd.set_size(font_sz * pango.SCALE)

        # Font style
        if self.style.text.font_style == 'Normal':
            name_fd.set_style(pango.STYLE_NORMAL)
        elif self.style.text.font_style == 'Italic':
            name_fd.set_style(pango.STYLE_ITALIC)

        # Font weight
        if self.style.text.font_weight == 'Lighter' or \
                self.style.text.font_weight == '100' or \
                self.style.text.font_weight == '200':
            name_fd.set_weight(pango.WEIGHT_ULTRALIGHT)
        elif self.style.text.font_weight == '300':
            name_fd.set_weight(pango.WEIGHT_LIGHT)
        elif self.style.text.font_weight == 'Normal' or \
                self.style.text.font_weight == '400' or \
                self.style.text.font_weight == '500':
            name_fd.set_weight(pango.WEIGHT_NORMAL)
        elif self.style.text.font_weight == 'Bold' or \
                self.style.text.font_weight == '600' or \
                self.style.text.font_weight == '700':
            name_fd.set_weight(pango.WEIGHT_BOLD)
        elif self.style.text.font_weight == 'Bolder' or \
                self.style.text.font_weight == '800':
            name_fd.set_weight(pango.WEIGHT_ULTRABOLD)
        elif self.style.text.font_weight == '900':
            name_fd.set_weight(pango.WEIGHT_HEAVY)

        # TODO TextDecoration

        ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, 10, 10) #TODO can be cached?
        cr = cairo.Context(ims)
        pc = pangocairo.CairoContext(cr)
        layout = pc.create_layout()
        layout.set_width(int((width - padding_left - padding_right) * pango.SCALE))
        layout.set_font_description(name_fd)

        if self.style.text.text_align == 'General' or self.style.text.text_align == 'Left':
            layout.set_alignment(pango.ALIGN_LEFT) 
        elif self.style.text.text_align == 'Right':
            layout.set_alignment(pango.ALIGN_RIGHT)
        elif self.style.text.text_align == 'Center':
            layout.set_alignment(pango.ALIGN_CENTER)
        elif self.style.text.text_align == 'Justify': # TODO Modify xml definition
            layout.set_justify(True) 

        layout.set_text(text)

        text_x, text_y, text_w, text_h = layout.get_extents()[1]

        rec_height = height
        if self.can_grow and max_height < text_h / pango.SCALE:
            rec_height = (text_h / pango.SCALE) + padding_top + padding_bottom
        elif self.can_shrink and max_height > text_h / pango.SCALE:
            rec_height = (text_h / pango.SCALE) + padding_top + padding_bottom

        return point_2_mm(rec_height) 


class PageGrid(PageItem):
    def __init__(self, report_item, parent_top, parent_left):
        super(PageGrid, self).__init__(report_item, parent_top, parent_left)


