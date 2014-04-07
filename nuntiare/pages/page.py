# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ..definition.report_items.report_item import Line, Rectangle, Textbox
from ..definition.report_items.grid import Grid
from ..definition.report_items.data_region.table import Table
from ..pages.section import HeaderInfo, FooterInfo, BodyInfo
from ..pages.page_item import PageLine, PageRectangle, PageText, PageGrid, PageTable
from ..tools import raise_error_with_log, get_expression_value_or_default, inch_2_mm

class Pages(object):
    def __init__(self, report):
        self.pages = []
        self.report = report
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
        while True:
            self.report.globals['page_number'] = len(self.pages) + 1
            self.run_reportitems(pg, self.body.definition, self.margin_top + self.header.height, self.margin_left)
            pg.page_number = len(self.pages) + 1
            self.pages.append(pg)
            break

        self.report.globals['total_pages'] = len(self.pages)

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
                result['item_list'].append(page_item)
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

            if isinstance(it, Table):
                page_item = PageTable(it, top, left, width)
                result['can_grow'] = True
                result['item_list'].append(page_item)
                page.add_page_item(page_item)

                grid_top = get_expression_value_or_default(it, "Top", 0)
                grid_left = get_expression_value_or_default(it, "Left", 0)
  
                columns = it.get_element("TableColumns")
                total_columns = len (columns.column_list)
                column_list=[]
                for c in columns.column_list:
                     column_data = {} 
                     column_data['Width'] = get_expression_value_or_default(c, "Width", 0)
                     column_data['Visibility'] = get_expression_value_or_default(c, "Visibility", True)
                     column_list.append(column_data)

                rows = it.get_element("TableDetails").get_element("TableRows")
                sum_height = 0

                data_set_name = get_expression_value_or_default(it, "DataSetName", None)
                reg = it.lnk.report.data_sets[data_set_name].data

                reg.move_first()
                while not reg.eof:
 
                    for row in rows.row_list:
                        sum_width = 0
                        cells = row.get_element("TableCells")
                        if not cells:
                            raise_error_with_log("TableCells not found in table Row. Table name: '{0}'".format(it.name))
                        total_cells = len(cells.cell_list)
                        row_height = get_expression_value_or_default(row, "Height", 8) #Default 8 mm
                        can_grow = False 
                        can_shrink = False 
                        min_height = 30000
                        max_height = 0
                        item_list = []

                        i=0
                        jump=0
                        for col in columns.column_list:
                            if jump > 0: # ColSpan
                                jump = jump - 1
                                sum_width = sum_width + column_list[i]['Width']
                                i = i + 1
                                continue

                            if i > total_cells - 1:
                                raise_error_with_log("Incongruent number of columns and cells. Table name: '{0}'".format(it.name))
                            cell = cells.cell_list[i]

                            col_span = int(get_expression_value_or_default(cell, "ColSpan", 1))
                            cell_Width = column_list[i]['Width']
                            if col_span <= 0:
                                raise_error_with_log("Cell ColSpan must be greater than '0'. Table name: '{0}'".format(it.name))
                            if col_span > 1:
                                remain = (total_columns - i) - col_span
                                if remain < 0:
                                    raise_error_with_log("Incongruent number of columns and cells. Table name: '{0}'".format(it.name))

                                x = 1
                                while x < col_span:
                                  cell_Width = cell_Width + column_list[i + x]['Width']
                                  x = x + 1  

                            data = self.run_reportitems(page, cell, 
                                top + grid_top + sum_height,
                                left + grid_left + sum_width, 
                                row_height,
                                cell_Width)
 
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

                            sum_width = sum_width + column_list[i]['Width']
                            i = i + 1
                            jump = col_span - 1

                        height_changed = False 
                        if can_grow and max_height > row_height:
                            row_height = max_height
                            height_changed = True
                        if can_shrink and min_height < row_height:
                            row_height = min_height
                            height_changed = True
                        if height_changed:
                            for item in item_list:
                                item.height = row_height

                        sum_height = sum_height + row_height

                    reg.move_next()

                page_item.width = sum_width
                page_item.height = sum_height

                if page_item.height < result['min_height']:
                    result['min_height'] = page_item.height
                if page_item.height > result['max_height']:
                    result['max_height'] = page_item.height


            if isinstance(it, Grid):
                page_item = PageGrid(it, top, left, width)
                result['can_grow'] = True
                result['item_list'].append(page_item)
                page.add_page_item(page_item)

                grid_top = get_expression_value_or_default(it, "Top", 0)
                grid_left = get_expression_value_or_default(it, "Left", 0)
  
                columns = it.get_element("Columns")
                total_columns = len (columns.column_list)
                column_list=[]
                for c in columns.column_list:
                     column_data = {} 
                     column_data['Width'] = get_expression_value_or_default(c, "Width", 0)
                     column_data['Visibility'] = get_expression_value_or_default(c, "Visibility", True)
                     column_list.append(column_data)

                rows = it.get_element("Rows")
                sum_height = 0
                for row in rows.row_list:
                    sum_width = 0 
                    cells = row.get_element("Cells")
                    if not cells:
                        raise_error_with_log("Cells not found in grid Row. Grid name: '{0}'".format(it.name))
                    total_cells = len(cells.cell_list)
                    row_height = get_expression_value_or_default(row, "Height", 8) #Default 8 mm
                    can_grow = False 
                    can_shrink = False 
                    min_height = 30000
                    max_height = 0
                    item_list = []

                    i=0
                    jump=0
                    for col in columns.column_list:
                        if jump > 0: # ColSpan
                            jump = jump - 1
                            sum_width = sum_width + column_list[i]['Width']
                            i = i + 1
                            continue

                        if i > total_cells - 1:
                            raise_error_with_log("Incongruent number of columns and cells. Grid name: '{0}'".format(it.name))
                        cell = cells.cell_list[i]

                        col_span = int(get_expression_value_or_default(cell, "ColSpan", 1))
                        cell_Width = column_list[i]['Width']
                        if col_span <= 0:
                            raise_error_with_log("Cell ColSpan must be greater than '0'. Grid name: '{0}'".format(it.name))
                        if col_span > 1:
                            remain = (total_columns - i) - col_span
                            if remain < 0:
                                raise_error_with_log("Incongruent number of columns and cells. Grid name: '{0}'".format(it.name))

                            x = 1
                            while x < col_span:
                              cell_Width = cell_Width + column_list[i + x]['Width']
                              x = x + 1  

                        data = self.run_reportitems(page, cell, 
                            top + grid_top + sum_height,
                            left + grid_left + sum_width, 
                            row_height,
                            cell_Width)
 
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

                        sum_width = sum_width + column_list[i]['Width']
                        i = i + 1
                        jump = col_span - 1

                    height_changed = False 
                    if can_grow and max_height > row_height:
                        row_height = max_height
                        height_changed = True
                    if can_shrink and min_height < row_height:
                        row_height = min_height
                        height_changed = True
                    if height_changed:
                        for item in item_list:
                            item.height = row_height

                    sum_height = sum_height + row_height

                page_item.width = sum_width
                page_item.height = sum_height

                if page_item.height < result['min_height']:
                    result['min_height'] = page_item.height
                if page_item.height > result['max_height']:
                    result['max_height'] = page_item.height
        
        return result


class Page(object):
    def __init__(self):
        self.page_number = None
        self.page_items=[]

    def add_page_item(self, page_item):
        self.page_items.append(page_item)

