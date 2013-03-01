# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from page import Page
from nuntiare.definition.report_items.line import Line
from nuntiare.definition.report_items.rectangle import Rectangle
from nuntiare.pages.page_item import PageLine
from nuntiare.pages.page_item import PageRectangle

def get_pages(report):
    pages=[]

    page_count = 0

    body = report.get_element("Body") 
    pg = Page()

    items = body.get_element("ReportItems")
    for name, it in items.reportitems_list.items():
        page_item = None
        if isinstance(it, Line):
            page_item = PageLine(it)    
        if isinstance(it, Rectangle):
            page_item = PageRectangle(it)
        pg.add(page_item)

    page_count = page_count + 1
    pg.page_number = page_count
    pages.append (pg)
    return pages

