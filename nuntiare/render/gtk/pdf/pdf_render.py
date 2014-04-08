# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import cairo
from ..context import Context
from ...render import Render
from ....tools import get_size_in_unit

class GtkPdfRender(Render):
    def __init__(self):
        super(GtkPdfRender, self).__init__(extension='pdf')

    def render(self, report):
        super(GtkPdfRender, self).render(report)
        ps = cairo.PDFSurface(self.result_file, get_size_in_unit(report.pages.width, 'pt'), 
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

