# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ....render.render import Render
import cairo
from ....render.gtk.context import Context
from ....tools import get_size_in_unit

class GtkSvgRender(Render):
    def __init__(self):
        super(GtkSvgRender, self).__init__()

    def render(self, report):
        ps = cairo.SVGSurface("svgfile.svg", 
                get_size_in_unit(report.pages.width, 'pt'), 
                get_size_in_unit(report.pages.height, 'pt'))
        cr = cairo.Context(ps)

        context = Context(report, cr, "pt")

        for pg in report.pages.pages:
            context.draw_header_style(report.pages.header)
            context.draw_body_style(report.pages.body)
            context.draw_footer_style(report.pages.footer) 
            for it in pg.page_items:
                context.draw_items(it)
            cr.show_page()

    def help(self):
        "GtkPngRender help"
    

