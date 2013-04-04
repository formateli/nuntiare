# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import gtk
import pango
import pangocairo
from decimal import Decimal
from nuntiare.pages.page_item import PageLine, PageRectangle, PageText
from nuntiare.pages.style import StyleItem
from nuntiare.tools import get_size_in_unit

# A Gtk widget that shows rendered pages in a form.

#PIXELS_PER_INCH=Decimal(72) # We use the standard 72dpi
PIXELS_PER_INCH=Decimal(85) # TODO--> get dpi, should be in a cfg file?

class ViewerWidget(gtk.ScrolledWindow):

    def __init__(self, report):
        super(ViewerWidget, self).__init__()

        self.report = report

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

        for pg in self.report.pages.pages:
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
            curr_info = self.draw_rectangle(it.style, self.Mm2Dot(it.top), self.Mm2Dot(it.left), 
                     self.Mm2Dot(it.height), self.Mm2Dot(it.width), curr_info, cr)

            if not it.value:
                return curr_info

            pc = pangocairo.CairoContext(cr)

            font_sz = get_size_in_unit(it.style.text.font_size.value, 'pt')

            name_fd = pango.FontDescription(it.style.text.font_family)
            name_fd.set_size(font_sz * pango.SCALE)

            layout = pc.create_layout()
            layout.set_width(int(self.Mm2Dot(it.width) * pango.SCALE))
            layout.set_font_description(name_fd)

            layout.set_text(it.value)

            if it.style.text.text_align == 'General' or it.style.text.text_align == 'Left':
                layout.set_alignment(pango.ALIGN_LEFT) 
            elif it.style.text.text_align == 'Right':
                layout.set_alignment(pango.ALIGN_RIGHT)
            elif it.style.text.text_align == 'Center':
                layout.set_alignment(pango.ALIGN_CENTER)
            elif it.style.text.text_align == 'Justify':
                layout.set_justify(True) 

            text_x, text_y, text_w, text_h = layout.get_extents()[1]

            # Default Top position
            x = self.Mm2Dot(it.left)
            y = self.Mm2Dot(it.top)   
            if it.style.text.vertical_align == 'Middle':
                y = y + ((self.Mm2Dot(it.height) - (text_h / pango.SCALE)) / 2)
            elif it.style.text.vertical_align == 'Bottom':
                y = y + ((self.Mm2Dot(it.height) - (text_h / pango.SCALE)))

            curr_info['color'] = self.set_curr_color(curr_info['color'], it.style.text.color, cr)
            cr.move_to(x, y)
            pc.show_layout(layout)


        if isinstance(it, PageRectangle):
            curr_info = self.draw_rectangle(it.style, self.Mm2Dot(it.top), self.Mm2Dot(it.left), 
                     self.Mm2Dot(it.height), self.Mm2Dot(it.width), curr_info, cr)

        return curr_info

    def draw_rectangle(self, style, top, left, height, width, 
                        curr_info, cr):
        cr.set_line_width(0.0)
        curr_info['border_width'] = 0.0
        curr_info['border_style'] = None
        curr_info['background_color'] = self.set_curr_color(curr_info['background_color'], style.background_color, cr)
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
        
        self.draw_section_style(self.report.pages.header, self.Mm2Dot(self.report.pages.margin_top), 
                self.Mm2Dot(self.report.pages.margin_left), self.Mm2Dot(self.report.pages.header.height),
                self.Mm2Dot(self.report.pages.width - self.report.pages.margin_left - self.report.pages.margin_right),
                curr_info, cr)
        self.draw_section_style(self.report.pages.body, self.Mm2Dot(self.report.pages.margin_top + self.report.pages.header.height), 
                self.Mm2Dot(self.report.pages.margin_left), self.Mm2Dot(self.report.pages.body.height),
                self.Mm2Dot(self.report.pages.width - self.report.pages.margin_left - self.report.pages.margin_right),
                curr_info, cr)
        self.draw_section_style(self.report.pages.footer, 
                self.Mm2Dot(self.report.pages.height - self.report.pages.margin_bottom - self.report.pages.footer.height), 
                self.Mm2Dot(self.report.pages.margin_left), 
                self.Mm2Dot(self.report.pages.footer.height),
                self.Mm2Dot(self.report.pages.width - self.report.pages.margin_left - self.report.pages.margin_right),
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
            return curr_info

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
        return (mm * PIXELS_PER_INCH) / Decimal(25.4)

