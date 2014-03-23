# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from nuntiare.definition.report_items.report_item import Line, Rectangle, Textbox
from nuntiare.pages.section import HeaderInfo, FooterInfo, BodyInfo
from nuntiare.pages.page_item import PageLine, PageRectangle, PageText
from nuntiare.tools import raise_error_with_log, get_expression_value_or_default, inch_2_mm

class Pages(object):
    def __init__(self, report):
        self.pages = []

        self.height = get_expression_value_or_default(report, "PageHeight", inch_2_mm(11)) 
        self.width = get_expression_value_or_default(report, "PageWidth", inch_2_mm(8.5)) 

        self.margin_top = get_expression_value_or_default(report, "TopMargin", 0)
        self.margin_left = get_expression_value_or_default(report, "LeftMargin", 0)
        self.margin_right = get_expression_value_or_default(report, "RightMargin", 0)
        self.margin_bottom = get_expression_value_or_default(report, "BottomMargin", 0)

        self.header = HeaderInfo(report.get_element("PageHeader"))
        self.footer = FooterInfo(report.get_element("PageFooter"))
        self.body = BodyInfo(report.get_element("Body"))

    def build_pages(self):
        last_page = False
        while not last_page:
            pg = Page()
            last_page = self.run_section(self.body, pg)
            pg.page_number = len(self.pages) + 1
            self.pages.append(pg)

        # Run Header and footer for each page 
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
            if isinstance(it, Textbox):
                page_item = PageText(it, top, self.margin_left)
            page.add_page_item(page_item)

        return last_page


class Page(object):
    def __init__(self):
        self.page_number = None
        self.page_items=[]

    def add_page_item(self, page_item):
        self.page_items.append(page_item)


