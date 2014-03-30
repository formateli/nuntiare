# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from nuntiare.render.render import Render
import cairo
from nuntiare.render.gtk.context import Context
from nuntiare.tools import get_size_in_unit

class GtkPdfRender(Render):
    def __init__(self):
        super(GtkPdfRender, self).__init__()

    def render(self, report):
        ps = cairo.PDFSurface("pdffile.pdf", get_size_in_unit(report.pages.width, 'pt'), 
                                get_size_in_unit(report.pages.height, 'pt'))
        cr = cairo.Context(ps)

        context = Context(report, cr, 'pt')

        for pg in report.pages.pages:
            context.draw_header_style(report.pages.header)
            context.draw_body_style(report.pages.body)
            context.draw_footer_style(report.pages.footer) 
            for it in pg.page_items:
                context.draw_items(it)
            cr.show_page()

    def help(self):
        "GtkPdfRender help"
    

