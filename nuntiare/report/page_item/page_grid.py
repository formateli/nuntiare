# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from page_item import PageItem, PageItemsInfo
from ... tools import get_expression_value_or_default, raise_error_with_log

class PageGrid(PageItem):
    def __init__(self, report, report_item_def, parent):
        super(PageGrid, self).__init__("PageGrid", report, report_item_def, parent)        
        
        self.data_set = None
        data_set_name = get_expression_value_or_default(report, report_item_def, 
                                                        'DataSetName', None)
        if data_set_name:
            if not report.data_sets.has_key(data_set_name):
                raise_error_with_log("Dataset '{0}' not found for Tablix '{1}'".format(data_set_name, self.name))
            self.data_set = report.data_sets[data_set_name]

        self.columns = []
        self.rows = []
        
        columns = report_item_def.get_element("TablixBody").get_element("TablixColumns")
        sum_width = 0
        for c in columns.column_list:          
            #hidden = get_expression_value_or_default(c.get_element("Visibility"), "Hidden", False)
            hidden = False
            #width = c.width
            width = get_expression_value_or_default(report, c, 'Width', 0.0)
            if width == 0:
                hidden = True
            col = GridColumn(hidden, width)
            sum_width = sum_width + width
            self.columns.append(col)
        self.width = sum_width
        
        self.run_rows(report_item_def.get_element("TablixBody").get_element("TablixRows"))

    def run_rows(self, rows_def):
        rws = []
        if not rows_def:
            return rws
        for row in rows_def.row_list: 
            cells = row.get_element("TablixCells")
            if not cells:
                raise_error_with_log("TablixCells not found in tablix '{0}'".format(self.name))
            #hidden = get_expression_value_or_default(row.get_element("Visibility"), "Hidden", False)
            hidden = False
            r = GridRow(self.report, hidden, 
                    get_expression_value_or_default(self.report, row, 'Height', 0.0),
                    cells, 
                    self.columns)
            self.height = self.height + r.height 
            rws. append(r)
        self.rows.extend(rws)
        return rws
        
        
class GridColumn(object):
    def __init__(self, hidden, width):
        self.hidden = hidden
        self.width = width


class GridRow(object):
    def __init__(self, report, hidden, height, cells, cols):
        self.hidden = hidden
        self.height = height
        self.can_grow = False
        self.can_shrink = False
        self.cells = []
        i=0
        for cell in cells.cell_list:
            if i == len(cols): # Ignore excedent cells
                break
                
            cl = RowCell(report, cell, height)
            x=1
            sum_width=0
            while x <= cl.col_span:
                sum_width = sum_width + cols[i+(x-1)].width
                x=x+1
            cl.width = sum_width
            i=i+(x-1)
            self.cells.append(cl)
            cl.get_items()
            if cl.items_info.total_height > self.height:
                self.height = cl.items_info.total_height
            if cl.items_info.can_grow:
                self.can_grow=True
            if cl.items_info.can_shrink:
                self.can_shrink=True
                

class RowCell(object):
    def __init__(self, report, cell, height):
        self.contents = cell.get_element('CellContents')
        if not self.contents:
            raise_error_with_log("'CellContents' is required by 'TablixCell'")
    
        self.type = "RowCell" # We treat it as a ReportItem because it can be a parent of a report item
        self.report = report
        self.col_span = int(get_expression_value_or_default(report, self.contents, "ColSpan", 1))
        self.row_span = int(get_expression_value_or_default(report, self.contents, "RowSpan", 1))
        self.top=0
        self.left=0
        self.height = height
        self.width = 0 # Given according to column(s) width
        self.cell_def = cell
        self.items_info=None
        
    def get_items(self):
        self.items_info = PageItemsInfo(self.report, self.contents, self)
        if len(self.items_info.item_list) > 1:
            raise_error_with_log("'CellContents' element must have just one 'ReportItem' in 'ReportItems' collection.")

