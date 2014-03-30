# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository.
# contains the full copyright notices and license terms.

import gtk
from nuntiare.tools import get_size_in_unit, get_float_rgba
from nuntiare.render.gtk.context import Context

class ViewerWidget(gtk.ScrolledWindow):

    def __init__(self, report):
        super(ViewerWidget, self).__init__()

        self.report = report
        self.pages = report.pages

        self.set_border_width(get_size_in_unit(10, 'dot'))
        self.set_policy(gtk.POLICY_ALWAYS, gtk.POLICY_ALWAYS)

        self.width = get_size_in_unit(report.pages.width, 'dot') 
        self.height = get_size_in_unit(report.pages.height, 'dot') 

        self.darea = gtk.DrawingArea()
        self.darea.set_size_request(get_size_in_unit(report.pages.width, 'dot') + 100, 
                get_size_in_unit(report.pages.height, 'dot') + (len(report.pages.pages) + 100))
        self.darea.connect("expose-event", self.expose)

        self.add_with_viewport(self.darea)

    def expose(self, widget, event):
        cr = widget.window.cairo_create()
        context = Context(self.report, cr, 'dot')

        for pg in self.pages.pages:
            self.draw_blank_page(context)
            context.draw_header_style(self.report.pages.header)
            context.draw_body_style(self.report.pages.body)
            context.draw_footer_style(self.report.pages.footer) 
            for it in pg.page_items:
                context.draw_items(it)

    def draw_blank_page(self, context):
        cr = context.cr 
        cr.set_line_width(1.0)
        cr.set_dash([])
        cr.set_source_rgba(get_float_rgba(65235), 
                    get_float_rgba(65235), 
                    get_float_rgba(65235),
                    get_float_rgba(65235))
        cr.rectangle(0, 0, self.width, self.height)
        cr.fill()


