# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import cairo
from ..pages import Pages
from ..context import Context
from ...render import Render
from ....tools import get_size_in_unit

class GtkPdfRender(Render):
    def __init__(self):
        super(GtkPdfRender, self).__init__(extension='pdf')

    def render(self, report):
        super(GtkPdfRender, self).render(report)
        
        pages = Pages(report, 'pt')        
        ps = cairo.PDFSurface(self.result_file, pages.width, pages.height)
        
        
        
        cr = cairo.Context(ps)
        context = Context(report, cr, 'pt')
        
        report.globals['total_pages'] = 1
        report.globals['page_number'] = 1
        
        if report.pages.body_items.total_height <= report.pages.available_height:
            print "One page"
            context.draw_header_style(report.pages.header)
            context.draw_body_style(report.pages.body)
            context.draw_footer_style(report.pages.footer) 
            
            self.render_items(report.pages.body_items.item_list, context)         
            
            cr.show_page()
        else:
            print "More than one page"
        

#        for pg in report.pages.pages:
#            print "  pdf page: " + str(pg.page_number)
#            context.draw_header_style(report.pages.header)
#            context.draw_body_style(report.pages.body)
#            context.draw_footer_style(report.pages.footer) 
#            for it in pg.page_items:
#                context.draw_items(it)
#            cr.show_page()


    def render_items(self, items, context):
        print "render_items..."
        for it in items:
            print "  " + it.type
            context.draw_items(it)
        

    def help(self):
        "GtkPdfRender help"

