# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import gtk
import cairo
import pango
import pangocairo
from decimal import Decimal
from nuntiare import __pixels_per_inch__
from nuntiare.pages.page_item import PageLine, PageRectangle, PageText, PageGrid
from nuntiare.pages.style import StyleItem
from nuntiare.tools import get_size_in_unit, raise_error_with_log

class ViewerWidget(gtk.ScrolledWindow):

    def __init__(self, report):
        super(ViewerWidget, self).__init__()

        self.report = report
        self.pages = report.pages

        self.set_border_width(10)
        self.set_policy(gtk.POLICY_ALWAYS, gtk.POLICY_ALWAYS)

        self.width = self.Mm2Dot(report.pages.width) 
        self.height = self.Mm2Dot(report.pages.height) 

        self.darea = gtk.DrawingArea()
        self.darea.set_size_request(self.Mm2Dot(report.pages.width) + 100, 
                self.Mm2Dot(report.pages.height) + (len(report.pages.pages) + 100))
        self.darea.connect("expose-event", self.expose)

        self.add_with_viewport(self.darea)


    def expose(self, widget, event):
        cr = widget.window.cairo_create()

        for pg in self.pages.pages:
            curr_info = self.draw_blank_page(cr)

            for it in pg.page_items:
                curr_info = self.draw_figure(it, curr_info, cr)


    def draw_figure(self, it, curr_info, cr):
        if isinstance(it, PageLine):
            curr_info = self.draw_line(cr, curr_info, 
                            it.style.border_color.default, 
                            it.style.border_style.default, 
                            it.style.border_width.default, 
                            self.Mm2Dot(it.top), self.Mm2Dot(it.left), 
                            self.Mm2Dot(it.height), self.Mm2Dot(it.width))

        if isinstance(it, PageText):
            text = it.value
            top = self.Mm2Dot(it.top)
            left = self.Mm2Dot(it.left)
            height = self.Mm2Dot(it.height)
            width = self.Mm2Dot(it.width)

            if not text or text=="":
                curr_info = self.draw_rectangle(it.style, top, left, 
                        height, it.width, curr_info, cr)
                return curr_info

            padding_top = self.Mm2Dot(it.style.text.padding_top.value)
            padding_left = self.Mm2Dot(it.style.text.padding_left.value)
            padding_right = self.Mm2Dot(it.style.text.padding_right.value)
            padding_bottom = self.Mm2Dot(it.style.text.padding_bottom.value)
            max_height = height - padding_top - padding_bottom

            if max_height <= 0:
                raise_error_with_log("Textbox drawable height area must be greater than zero. See height and padding values.")

            font_sz = get_size_in_unit(it.style.text.font_size.value, 'pt')

            name_fd = pango.FontDescription(it.style.text.font_family)
            name_fd.set_size(font_sz * pango.SCALE)

            # Font style
            if it.style.text.font_style == 'Normal':
                name_fd.set_style(pango.STYLE_NORMAL)
            elif it.style.text.font_style == 'Italic':
                name_fd.set_style(pango.STYLE_ITALIC)

            # Font weight
            if it.style.text.font_weight == 'Lighter' or \
                    it.style.text.font_weight == '100' or \
                    it.style.text.font_weight == '200':
                name_fd.set_weight(pango.WEIGHT_ULTRALIGHT)
            elif it.style.text.font_weight == '300':
                name_fd.set_weight(pango.WEIGHT_LIGHT)
            elif it.style.text.font_weight == 'Normal' or \
                    it.style.text.font_weight == '400' or \
                    it.style.text.font_weight == '500':
                name_fd.set_weight(pango.WEIGHT_NORMAL)
            elif it.style.text.font_weight == 'Bold' or \
                    it.style.text.font_weight == '600' or \
                    it.style.text.font_weight == '700':
                name_fd.set_weight(pango.WEIGHT_BOLD)
            elif it.style.text.font_weight == 'Bolder' or \
                    it.style.text.font_weight == '800':
                name_fd.set_weight(pango.WEIGHT_ULTRABOLD)
            elif it.style.text.font_weight == '900':
                name_fd.set_weight(pango.WEIGHT_HEAVY)

            # TODO TextDecoration

            pc = pangocairo.CairoContext(cr)
            layout = pc.create_layout()
            layout.set_width(int((width - padding_left - padding_right) * pango.SCALE))
            layout.set_font_description(name_fd)

            if it.style.text.text_align == 'General' or it.style.text.text_align == 'Left':
                layout.set_alignment(pango.ALIGN_LEFT) 
            elif it.style.text.text_align == 'Right':
                layout.set_alignment(pango.ALIGN_RIGHT)
            elif it.style.text.text_align == 'Center':
                layout.set_alignment(pango.ALIGN_CENTER)
            elif it.style.text.text_align == 'Justify': # TODO Modify xml definition
                layout.set_justify(True) 

            layout.set_text(text)

            text_x, text_y, text_w, text_h = layout.get_extents()[1]

            rec_height = height

            if it.can_grow and max_height < text_h / pango.SCALE:
                rec_height = (text_h / pango.SCALE) + padding_top + padding_bottom
            elif it.can_shrink and max_height > text_h / pango.SCALE:
                rec_height = (text_h / pango.SCALE) + padding_top + padding_bottom
            elif not it.can_grow and not it.can_shrink and max_height < text_h / pango.SCALE:
                #TODO There must be a better way to do this.. Ex. Text clipping           
                while text_h / pango.SCALE > max_height:
                    line = layout.get_line(layout.get_line_count() - 1) # Get last line
                    text = text[:line.start_index - 1] # Remove last text
                    layout.set_text(text) # Set new text
                    text_x, text_y, text_w, text_h = layout.get_extents()[1]

            x = left + padding_left
            y = top + padding_top
            if it.style.text.vertical_align == 'Middle':
                y = y + ((max_height - (text_h / pango.SCALE)) / 2)
            elif it.style.text.vertical_align == 'Bottom':
                y = y + ((height - padding_bottom - (text_h / pango.SCALE)))

            curr_info = self.draw_rectangle(it.style, top, left, rec_height, width, curr_info, cr)

            # Draw text
            curr_info['color'] = self.set_curr_color(None, it.style.text.color, cr)
            cr.move_to(x, y)
            pc.show_layout(layout)


        if isinstance(it, PageRectangle):
            curr_info = self.draw_rectangle(it.style, self.Mm2Dot(it.top), self.Mm2Dot(it.left), 
                     self.Mm2Dot(it.height), self.Mm2Dot(it.width), curr_info, cr)

        if isinstance(it, PageGrid):
            curr_info = self.draw_rectangle(it.style, self.Mm2Dot(it.top), self.Mm2Dot(it.left), 
                     self.Mm2Dot(it.height), self.Mm2Dot(it.width), curr_info, cr)

        return curr_info

    def draw_rectangle(self, style, top, left, height, width, 
                        curr_info, cr):
        cr.set_line_width(0.0)
        curr_info['border_width'] = 0.0
        curr_info['border_style'] = None
        curr_info['background_color'] = self.set_curr_color(None, style.background_color, cr)
        if curr_info['background_color']: # if not, background color is Transparent, nothing to draw
            cr.rectangle(left, top, width, height)
            cr.fill()
        self.draw_rectangle_borders(cr, curr_info, style, top, left, height, width)
        return curr_info

    def draw_rectangle_borders(self, cr, curr_info, style, top, left, height, width):
        curr_info = self.draw_line(cr, curr_info, 
                            style.border_color.top, 
                            style.border_style.top, 
                            style.border_width.top, 
                            top, left, 0, width)
        curr_info = self.draw_line(cr, curr_info, 
                            style.border_color.left,
                            style.border_style.left,
                            style.border_width.left,
                            top, left, height, 0)
        curr_info = self.draw_line(cr, curr_info, 
                            style.border_color.bottom,
                            style.border_style.bottom,
                            style.border_width.bottom,
                            top + height, left, 0, width)
        curr_info = self.draw_line(cr, curr_info, 
                            style.border_color.right,
                            style.border_style.right,
                            style.border_width.right,
                            top, left + width, height, 0)

    def draw_blank_page(self, cr):
        cr.set_line_width(1.0)
        cr.set_dash([])
        cr.set_source_rgba(self.get_float_rgba(65235), 
                    self.get_float_rgba(65235), 
                    self.get_float_rgba(65235),
                    self.get_float_rgba(65235))
        cr.rectangle(0, 0, self.width, self.height)
        cr.fill()

        curr_info = {'background_color':None, 
                     'color':None, 
                     'border_width':1.0, 
                     'border_style':'Solid'
                    }
        
        self.draw_section_style(self.pages.header, self.Mm2Dot(self.pages.margin_top), 
                self.Mm2Dot(self.pages.margin_left), self.Mm2Dot(self.pages.header.height),
                self.Mm2Dot(self.pages.width - self.pages.margin_left - self.pages.margin_right),
                curr_info, cr)
        self.draw_section_style(self.pages.body, self.Mm2Dot(self.pages.margin_top + self.pages.header.height), 
                self.Mm2Dot(self.pages.margin_left), self.Mm2Dot(self.pages.body.height),
                self.Mm2Dot(self.pages.width - self.pages.margin_left - self.pages.margin_right),
                curr_info, cr)
        self.draw_section_style(self.pages.footer, 
                self.Mm2Dot(self.pages.height - self.pages.margin_bottom - self.pages.footer.height), 
                self.Mm2Dot(self.pages.margin_left), 
                self.Mm2Dot(self.pages.footer.height),
                self.Mm2Dot(self.pages.width - self.pages.margin_left - self.pages.margin_right),
                curr_info, cr)

        return curr_info

    def draw_section_style(self, section, top, left, height, width, curr_info, cr):
        if not section or not section.style:
            return curr_info
        return self.draw_rectangle(section.style, top, left, height, width, curr_info, cr)

    def draw_line(self, cr, curr_info, 
                color, border_style, border_width,
                top, left, height, width):

        curr_info['border_style'] = self.set_curr_border_style(curr_info['border_style'], border_style, cr)
        if curr_info['border_style'] == 'None':
            return curr_info # Nothing to draw

        curr_info['background_color'] = self.set_curr_color(curr_info['background_color'], color, cr)
        curr_info['border_width'] = self.set_curr_border_width(curr_info['border_width'], border_width, cr)

        cr.move_to(left, top)
        cr.rel_line_to(width, height)
        cr.close_path()
        cr.stroke()
        return curr_info

    def set_curr_color(self, curr_color, new_color, cr):
        if not new_color:
            return None 
        if curr_color == new_color.hex_alpha:
            return curr_color 
        # Change current color
        cr.set_source_rgba(self.get_float_rgba(new_color.red), 
                    self.get_float_rgba(new_color.green), 
                    self.get_float_rgba(new_color.blue),
                    self.get_float_rgba(new_color.alpha))
        return new_color.hex_alpha

    def set_curr_border_style(self, curr_border_style, new_border_style, cr):
        if curr_border_style == new_border_style.value:
            return curr_border_style 
        # Change current border_style
        st = new_border_style.value

        if st.lower() == 'solid' or st.lower() == 'none':
            cr.set_dash([])
            return st

        # TODO - for now, only resolve to 'Dotted' for others than None or Solid
        cr.set_dash([5.0])
        return st

    def set_curr_border_width(self, curr_border_width, new_border_width, cr):
        if curr_border_width == new_border_width.value:
            return curr_border_width 
        # Change current border_width
        st = new_border_width.value
        cr.set_line_width(self.Mm2Dot(st))
        return st

    def get_float_rgba(self, c):
        return float(c) / float(65535) 

    def Mm2Dot(self, mm):
        return (mm * __pixels_per_inch__) / Decimal(25.4)

