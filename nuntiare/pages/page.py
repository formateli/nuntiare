# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from nuntiare.definition.report_items.report_item import Line, Rectangle, Textbox
from nuntiare.definition.report_items.grid import Grid
from nuntiare.pages.section import HeaderInfo, FooterInfo, BodyInfo
from nuntiare.pages.page_item import PageLine, PageRectangle, PageText, PageGrid
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

        pg = Page()
        self.run_reportitems(pg, self.body.definition, self.margin_top + self.header.height, self.margin_left)
        pg.page_number = len(self.pages) + 1
        self.pages.append(pg)

        # Run Header and footer for each page 
        for page in self.pages:
            self.run_reportitems(page, self.header.definition, self.margin_top, self.margin_left)
            self.run_reportitems(page, self.footer.definition, self.height - self.margin_bottom - self.footer.height, self.margin_left)

    def run_reportitems(self, page, element, top, left, height=None, width=None):
        result = {'can_grow' : False,
                  'can_shrink' : False,
                  'min_height' : 30000,
                  'max_height' : 0,
                  'item_list' : [],
                 }

        items = element.get_element("ReportItems")

        for name, it in items.reportitems_list.items():
            page_item = None

            if isinstance(it, Line):
                page_item = PageLine(it, top, left)
                page.add_page_item(page_item)
            if isinstance(it, Rectangle):
                page_item = PageRectangle(it, top, left)
                page.add_page_item(page_item)
            if isinstance(it, Textbox):
                page_item = PageText(it, top, left, height, width)
                result['can_grow'] = page_item.can_grow
                result['can_shrink'] = page_item.can_shrink
                if page_item.height < result['min_height']:
                    result['min_height'] = page_item.height
                if page_item.height > result['max_height']:
                    result['max_height'] = page_item.height
                result['item_list'].append(page_item)
                page.add_page_item(page_item)
            if isinstance(it, Grid):
                page_item = PageGrid(it, top, left)
                page.add_page_item(page_item)
                grid_top = get_expression_value_or_default(it, "Top", 0)
                grid_left = get_expression_value_or_default(it, "Left", 0)  
                columns = it.get_element("Columns")
                rows = it.get_element("Rows")
                sum_height = 0
                for row in rows.row_list:
                    sum_width = 0 
                    cells = row.get_element("Cells")
                    if not cells:
                        raise_error_with_log("Cells not found in grid Row. Grid name: '{0}'".format(it.name))
                    if len (columns.column_list) != len (cells.cell_list):
                        raise_error_with_log("Row cells quantity and Columns quantity must be equal. Grid name: '{0}'".format(it.name))

                    row_height = get_expression_value_or_default(row, "Height", 0)
                    can_grow = False 
                    can_shrink = False 
                    min_height = 30000
                    max_height = 0
                    item_list = []

                    i=0
                    for cell in cells.cell_list:
                        col_width = get_expression_value_or_default(columns.column_list[i], "Width", 0) 
                        data = self.run_reportitems(page, cell, 
                            top + grid_top + sum_height,
                            left + grid_left + sum_width, 
                            row_height,
                            col_width)
 
                        if data['can_grow']:
                            can_grow = True 
                        if data['can_shrink']:
                            can_shrink = True
                        if data['min_height'] < min_height:
                            min_height = data['min_height']
                        if data['max_height'] > max_height:
                            max_height = data['max_height']

                        for item in data['item_list']:
                            item_list.append(item)

                        sum_width = sum_width + col_width
                        i=i+1

                    if can_grow and max_height > row_height:
                        row_height = max_height
                        for item in item_list:
                            item.height = max_height

                    sum_height = sum_height + row_height

                page_item.width = sum_width

        return result


class Page(object):
    def __init__(self):
        self.page_number = None
        self.page_items=[]

    def add_page_item(self, page_item):
        self.page_items.append(page_item)

