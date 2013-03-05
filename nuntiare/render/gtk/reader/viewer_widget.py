# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import gtk
from decimal import Decimal
from nuntiare.pages.page_item import PageLine, PageRectangle, ColorItem, SizeItem, BorderStyleItem

# A Gtk widget that shows rendered pages in a form.

PIXELS_PER_INCH=Decimal(72)

class ViewerWidget(gtk.ScrolledWindow):

    def __init__(self, report):
        super(ViewerWidget, self).__init__()

        self.report = report

        self.set_border_width(10)
        self.set_policy(gtk.POLICY_ALWAYS, gtk.POLICY_ALWAYS)

        self.width = self.Mm2Dot(report.pages.width)
        self.height = self.Mm2Dot(report.pages.height)

        darea = gtk.DrawingArea()
        darea.set_size_request(1000, 1000)
        darea.connect("expose-event", self.expose)

        self.add_with_viewport(darea)


    def expose(self, widget, event):
        cr = widget.window.cairo_create()

        for pg in self.report.pages.pages:
            curr_info = self.draw_blank_page(cr)

            for it in pg.page_items:
                curr_info = self.draw_figure(it, curr_info, cr)


    def draw_figure(self, it, curr_info, cr):
        if isinstance(it, PageLine):
            curr_info = self.draw_line(cr, curr_info, 
                            None, it.style.border_color.default, 
                            None, it.style.border_style.default, 
                            None, it.style.border_width.default, 
                            it.top, it.left, it.height, it.width)

        if isinstance(it, PageRectangle):
            cr.set_line_width(0.0)
            curr_info['border_width'] = 0.0
            curr_info['border_style'] = None
            curr_info['color'] = self.set_curr_color(curr_info['color'], it.style.background_color, cr)
            if curr_info['color']: # if not, background color is Transparent, nothing to draw
                cr.rectangle(self.Mm2Dot(it.left), self.Mm2Dot(it.top), self.Mm2Dot(it.width), self.Mm2Dot(it.height))
                cr.fill()

            # Draw each border
            curr_info = self.draw_line(cr, curr_info, 
                            it.style.border_color.top, it.style.border_color.default, 
                            it.style.border_style.top, it.style.border_style.default, 
                            it.style.border_width.top, it.style.border_width.default, 
                            it.top, it.left, 0, it.width)
            curr_info = self.draw_line(cr, curr_info, 
                            it.style.border_color.left, it.style.border_color.default, 
                            it.style.border_style.left, it.style.border_style.default, 
                            it.style.border_width.left, it.style.border_width.default, 
                            it.top, it.left, it.height, 0)
            curr_info = self.draw_line(cr, curr_info, 
                            it.style.border_color.bottom, it.style.border_color.default, 
                            it.style.border_style.bottom, it.style.border_style.default, 
                            it.style.border_width.bottom, it.style.border_width.default, 
                            it.top + it.height, it.left, 0, it.width)
            curr_info = self.draw_line(cr, curr_info, 
                            it.style.border_color.right, it.style.border_color.default, 
                            it.style.border_style.right, it.style.border_style.default, 
                            it.style.border_width.right, it.style.border_width.default, 
                            it.top, it.left + it.width, it.height, 0)

        return curr_info

    def draw_blank_page(self, cr):
        cr.set_line_width(1.0)
        cr.set_dash([])
        cr.set_source_rgba(self.get_float_rgba(65235), 
                    self.get_float_rgba(65235), 
                    self.get_float_rgba(65235),
                    self.get_float_rgba(65235))
        cr.rectangle(10, 10, self.width, self.height)
        cr.fill()

        return {'color':None, 'border_width':1.0, 'border_style':'Solid'}

    def draw_line(self, cr, curr_info, 
                new_color, default_color, 
                new_border_style, default_border_style, 
                new_border_width, default_border_width, 
                top, left, height, width):

        border_style = self.select_default (new_border_style, default_border_style)
        if not border_style: # Use default border style: solid
            border_style = BorderStyleItem()
        curr_info['border_style'] = self.set_curr_border_style(curr_info['border_style'], border_style, cr)
        if curr_info['border_style'] == 'None':
            return curr_info

        color = self.select_default (new_color, default_color)
        if not color: # Use default color black full opaque
            color = ColorItem()
        curr_info['color'] = self.set_curr_color(curr_info['color'], color, cr)

        border_width = self.select_default (new_border_width, default_border_width)
        if not border_width: # Use default border width: 1.0 pt
            border_width = SizeItem()
        curr_info['border_width'] = self.set_curr_border_width(curr_info['border_width'], border_width, cr)

        cr.move_to(self.Mm2Dot(left), self.Mm2Dot(top))
        cr.rel_line_to(self.Mm2Dot(width), self.Mm2Dot(height))
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

        if not st or st.lower() == 'solid' or st.lower() == 'none':
            cr.set_dash([])
            if not st:
                return 'Solid' 
            else:
                return st

        # TODO - for now, only resolve to 'Dotted' for others than None or Solid
        cr.set_dash([5.0])
        return st

    def set_curr_border_width(self, curr_border_width, new_border_width, cr):
        if curr_border_width == new_border_width.value:
            return curr_border_width 
        # Change current border_width
        st = new_border_width.value
        if not st:
            cr.set_line_width(1.0) # TODO make convertion from mm to dot?
            return 1.0

        cr.set_line_width(self.Mm2Dot(st))
        return st

    def select_default(self, new, default):
        res = default
        if new:
            res = new
        return res

    def get_float_rgba(self, c):
        return float(c) / float(65535) 

    def Mm2Dot(self, mm):
        return (mm * PIXELS_PER_INCH) / Decimal(25.4)
