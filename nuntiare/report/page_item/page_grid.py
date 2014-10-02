# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from page_item import PageItem
from ... tools import get_expression_value_or_default

class PageGrid(PageItem):
    def __init__(self, report, report_item_def, parent):
        super(PageGrid, self).__init__("PageGrid", report, report_item_def, parent)
        self.columns = []
        self.rows = []
        #self.page_break_at_start = get_expression_value_or_default(report_item_def, "PageBreakAtStart", False)
        #self.page_break_at_end = get_expression_value_or_default(report_item_def, "PageBreakAtEnd", False)        

        self.get_columns()
        
#        sum_width = 0
#        for c in columns.column_list:          
#            hidden = get_expression_value_or_default(c.get_element("Visibility"), "Hidden", False)
#            width = c.width
#            if width == 0:
#                hidden = True
#            col = GridColumn(hidden, width)
#            sum_width = sum_width + width
#            self.columns.append(col)
#        self.width = sum_width

    def get_columns(self):
        ch = []
        members = self.report_item_def.get_element("TablixColumnHierarchy").get_element("TablixMembers")
        for m in members.member_list:
            ch.append(GridColumnHierarchy(m))
        cols = self.report_item_def.get_element("TablixBody").get_element('TablixColumns')
        if len(cols.column_list) != len(ch):
            raise_error_with_log("")

    def run_rows(self, rows):
        rws = []
        if not rows:
            return rws
        for row in rows.row_list: 
            cells = row.get_element("Cells")
            if not cells:
                raise_error_with_log("Cells not found in grid Row. {0} name: '{1}'".format(self.grid_type, self.name))
            hidden = get_expression_value_or_default(row.get_element("Visibility"), "Hidden", False)
            r = GridRow(hidden, row.height, cells, self.columns)
            self.height = self.height + r.height 
            rws. append(r)
        self.rows.extend(rws)
        return rws
        
        
class GridColumnHierarchy(object):
    def __init__(self, member_def):
        self.member_def = member_def
        self.is_static = True
    
        #self.hidden = hidden
        #elf.width = width


class GridRow(object):
    def __init__(self, hidden, height, cells, cols):
        self.hidden = hidden
        self.height = height
        self.can_grow = False
        self.can_shrink = False
        self.cells = []
        i=0
        for cell in cells.cell_list:
            if i == len(cols): # Ignore excedent cells 
                break
            cl = RowCell(cell, height)
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
    def __init__(self, cell, height):
        self.type = "RowCell" # We treat it as a ReportItem because it can be a parent of a report item
        self.col_span = int(get_expression_value_or_default(cell, "ColSpan", 1))
        self.top=0            
        self.left=0
        self.height = height
        self.width = 0 # Given according to column(s) width
        self.cell_def = cell
        self.items_info=None
        
    def get_items(self):
        self.items_info = ReportItemsInfo(self.cell_def, self)
        if len(self.items_info.item_list) > 1:
            raise_error_with_log("Cell element may have just one ReportItem.")

