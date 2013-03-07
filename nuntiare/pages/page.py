# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from nuntiare.definition.report_items.line import Line
from nuntiare.definition.report_items.rectangle import Rectangle
from nuntiare.pages.page_item import PageLine, PageRectangle
from nuntiare.tools import raise_error_with_log

class Pages(object):
    def __init__(self, report):
        self.pages = []

        self.height = get_value(report.get_element("PageHeight"), inch_2_mm(11)) 
        self.width = get_value(report.get_element("PageWidth"), inch_2_mm(8.5)) 

        self.margin_top = get_value(report.get_element("TopMargin"), 0)
        self.margin_left = get_value(report.get_element("LeftMargin"), 0)
        self.margin_right = get_value(report.get_element("RightMargin"), 0)
        self.margin_bottom = get_value(report.get_element("BottomMargin"), 0)

        self.header = HeaderInfo(report.get_element("PageHeader"))
        self.footer = FooterInfo(report.get_element("PageFooter"))
        self.body = BodyInfo(report.get_element("Body"))

    def build_pages(self):
        last_page = False
        while not last_page:
            pg = Page()
            last_page = self.run_section(self.body, pg)
            pg.page_number = len(self.pages) + 1
            self.add_page(pg)

        # Run Header and footer 
        for page in self.pages:
            self.run_section(self.header, page)
            self.run_section(self.footer, page)

    def run_section(self, section, page):
        last_page = True
        if not section.definition:
            return last_page

        if isinstance(section, HeaderInfo):
            top = self.margin_top
        elif isinstance(section, BodyInfo):
            top = self.margin_top + self.header.height
        elif isinstance(section, FooterInfo):
            top = self.height - self.margin_bottom - self.footer.height
        else: 
            raise_error_with_log('Unknown section type {0}'.format(str(section)))

        items = section.definition.get_element("ReportItems")
        for name, it in items.reportitems_list.items():
            page_item = None
            if isinstance(it, Line):
                page_item = PageLine(it, top, self.margin_left)
            if isinstance(it, Rectangle):
                page_item = PageRectangle(it, top, self.margin_left)
            page.add_page_item(page_item)

        return last_page

    def add_page(self, page):
        self.pages.append(page)


class Page(object):
    def __init__(self):
        self.page_number = None
        self.page_items=[]

    def add_page_item(self, page_item):
        self.page_items.append(page_item)


class HeaderFooterInfo(object):
    def __init__(self, element):
        self.definition = element 
        self.height = 0
        self.print_on_first_page = False
        self.print_on_last_page = False
        if element:
            self.height = get_value(element.get_element("Height"), 0)
            self.print_on_first_page = get_value(element.get_element("PrintOnFirstPage"), False)
            self.print_on_last_page = get_value(element.get_element("PrintOnLastPage"), False)

class HeaderInfo(HeaderFooterInfo):
    def __init__(self, element):
        super(HeaderInfo, self).__init__(element)

class FooterInfo(HeaderFooterInfo):
    def __init__(self, element):
        super(FooterInfo, self).__init__(element)

class BodyInfo(object):
    def __init__(self, element):
        if not element:
            raise_error_with_log("Body section is requiered!")
        self.definition = element
        self.height = get_value(element.get_element("Height"), 0)
        self.columns = get_value(element.get_element("Columns"), 1)
        self.column_spacing = get_value(element.get_element("ColumnSpacing"), inch_2_mm(0.5))
        # TODO
        # self.style 

# Module functions

def get_value(element, default):
    if not element:
        return default
    value = element.value()
    if not value:
        return default
    return value

def inch_2_mm(inch):
    return inch * 25.4

