# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ....render.render import Render
import cairo
from ....render.gtk.context import Context
from ....tools import get_size_in_unit

class GtkPngRender(Render):
    def __init__(self):
        super(GtkPngRender, self).__init__()

    def render(self, report):
        ps = cairo.ImageSurface(cairo.FORMAT_ARGB32, 
                    get_size_in_unit(report.pages.width, 'dot'), 
                    get_size_in_unit(report.pages.height, 'dot'))
        cr = cairo.Context(ps)

        context = Context(report, cr, 'dot')

        for pg in report.pages.pages:
            context.draw_header_style(report.pages.header)
            context.draw_body_style(report.pages.body)
            context.draw_footer_style(report.pages.footer) 
            for it in pg.page_items:
                context.draw_items(it)

        ps.write_to_png("image.png")

    def help(self):
        "GtkPngRender help"
    

