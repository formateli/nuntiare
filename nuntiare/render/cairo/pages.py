# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ...tools import get_size_in_unit, raise_error_with_log

class Pages(object):
    def __init__(self, report, unit):
        self.report = report
        self.width = get_size_in_unit(report.pages.page_width, unit)
        self.height = get_size_in_unit(report.pages.page_height, unit)
        self.margin_top = get_size_in_unit(report.pages.margin_top, unit)
        self.margin_bottom = get_size_in_unit(report.pages.margin_bottom, unit)
        self.margin_left = get_size_in_unit(report.pages.margin_left, unit)
        self.margin_right = get_size_in_unit(report.pages.margin_right, unit)
        self.available_height = get_size_in_unit(report.pages.available_height, unit)
        self.columns = report.pages.body.columns
        self.column_spacing = get_size_in_unit(report.pages.body.column_spacing, unit)
        
        self.pages = []
        self.create_pages()

        report.globals['total_pages'] = len(pages)
        report.globals['page_number'] = 0
        
        for p in self.pages:
            report.globals['page_number'] = report.globals['page_number'] + 1
            self.header_footer(p)

    def create_pages(self):
        for it in self.report.pages.body_items.item_list:
            if it.type == "PageLine":
                continue
            if it.type == "PageRectangle" or it.type == "PageText":
                el = self.get_rectangle(it)
            if it.type == "PageGrid":
                el = self.get_grid(it)

            container.add_element(el)

    def header_footer(self, page):
        pass


class Page(object):
    def __init__(self):
        pass
        
