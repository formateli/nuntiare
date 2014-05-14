# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from get_report_items import ReportItemsInfo
from page_item import PageItem
from ..tools import raise_error_with_log, get_expression_value_or_default
from ..definition.data.data import DataGroup
from ..definition.data.grouping import GroupingData, GroupingObject

class PageGrid(PageItem):
    def __init__(self, report_item_def, parent, grid_type="Grid"):
        super(PageGrid, self).__init__("PageGrid", report_item_def, parent)
        self.columns = []
        self.rows = []
        self.page_break_at_start = get_expression_value_or_default(report_item_def, "PageBreakAtStart", False)
        self.page_break_at_end = get_expression_value_or_default(report_item_def, "PageBreakAtEnd", False)        
        self.grid_type = grid_type

        columns = report_item_def.get_element("Columns")
        sum_width = 0
        for c in columns.column_list:          
            hidden = get_expression_value_or_default(c.get_element("Visibility"), "Hidden", False)
            width = get_expression_value_or_default(c, "Width", 0)
            if width == 0:
                hidden = True
            col = GridColumn(hidden, width)
            sum_width = sum_width + width
            self.columns.append(col)
        self.width = sum_width

        if grid_type == "Grid": 
            self.run_rows(report_item_def.get_element("Rows"))
        elif grid_type == "Table":
            data_set_name = get_expression_value_or_default(report_item_def, "DataSetName", None)
            if not report_item_def.lnk.report.data_sets.has_key(data_set_name):
                raise_error_with_log("DataSetName '{0}' not found for Table '{1}'".format(data_set_name, self.name))
            grouping = TableGroupings(report_item_def.lnk.report.data_sets[data_set_name].data_set_object.data, 
                    report_item_def)
 
            header = report_item_def.get_element("Header")
            footer = report_item_def.get_element("Footer")

            grouping.data.set_current_scope() # Puts this data as current
            if header:
                self.run_rows(header.get_element("Rows"))
                    
            self.run_details(grouping, 0, grouping.groupings[0].groups)

            grouping.data.set_current_scope() # Puts this data as current
            if footer:
                self.run_rows(footer.get_element("Rows"))

    def run_details(self, grouping, grouping_i, groups):
        for g in groups:
            g.move_first()
            if grouping_i < len(grouping.groupings) - 1:
                if grouping.groupings[grouping_i].header:
                    self.run_rows(grouping.groupings[grouping_i].header.get_element("Rows"))            
                self.run_details(grouping, grouping_i + 1, g.groups)
                g.set_current_scope()
                if grouping.groupings[grouping_i].footer:
                    self.run_rows(grouping.groupings[grouping_i].footer.get_element("Rows"))                            
            else:
                while not g.EOF():
                    self.run_rows(self.report_item_def.get_element("Details").get_element("Rows"))    
                    g.move_next()

    def run_rows(self, rows):
        if not rows:
            return
        for row in rows.row_list: 
            cells = row.get_element("Cells")
            if not cells:
                raise_error_with_log("Cells not found in grid Row. {0} name: '{1}'".format(self.grid_type, self.name))
            hidden = get_expression_value_or_default(row.get_element("Visibility"), "Hidden", False)
            r = GridRow(hidden, get_expression_value_or_default(row, "Height", 8), cells, self.columns)
            self.height = self.height + r.height 
            self.rows.append(r)


class PageTable(PageGrid):
    def __init__(self, report_item_def, parent):
        super(PageTable, self).__init__(report_item_def, parent, grid_type="Table")


class GridColumn(object):
    def __init__(self, hidden, width):
        self.hidden = hidden
        self.width = width


class GridRow(object):
    def __init__(self, hidden, height, cells, cols):
        self.type = "GridRow"
        self.hidden = hidden
        self.height = height
        self.can_grow = False
        self.can_shrink = False
        self.cells = []
        i=0
        for cell in cells.cell_list:
            if i == len(cols): # Ignore excedent cells 
                break
            cl = RowCell(cell)
            x=1
            sum_width=0
            while x <= cl.col_span:
                sum_width = sum_width + cols[i+(x-1)].width
                x=x+1                
            cl.width = sum_width
            i=i+(x-1)
            self.cells.append(cl)
            if cl.items_info.total_height > self.height:
                self.height = cl.items_info.total_height
            if cl.items_info.can_grow:
                self.can_grow=True
            if cl.items_info.can_shrink:
                self.can_shrink=True
                

class RowCell(object):
    def __init__(self, cell):
        self.type = "RowCell"
        self.col_span = int(get_expression_value_or_default(cell, "ColSpan", 1))
        self.height = 0
        self.width = 0
        self.cell_def = cell
        self.items_info = ReportItemsInfo(cell, self)


class TableGroupings(object):
    def __init__(self, data, table_def):
        self.columns = data.columns
        self.groupings=[]
        self.details=None
        self.data = data
        
        grouping_data=GroupingData(data)

        element_groups = table_def.get_element("TableGroups")
        if element_groups:
            for gr in element_groups.group_list:
                grouping_object = GroupingObject(gr.get_element("Grouping"))
                grouping_data.grouping_by(grouping_object, gr.get_element("Sorting"))
                self.groupings.append(TableGrouping(gr, grouping_data.get_group(grouping_data.last_group_name)))
                
        element_details = table_def.get_element("Details")        
        grouping_object = GroupingObject(element_details.get_element("Grouping"))
        grouping_data.grouping_by(grouping_object, element_details.get_element("Sorting"), 
                                        optional_name="{0}_{1}".format(data.name, "details"))
        self.groupings.append(TableGrouping(None, grouping_data.get_group(grouping_data.last_group_name)))


class TableGrouping(object):
    def __init__(self, table_def, groups):
        self.header = None
        self.footer = None
        self.groups = groups

        if table_def:
            self.header = table_def.get_element("Header")
            self.footer = table_def.get_element("Footer")
  
