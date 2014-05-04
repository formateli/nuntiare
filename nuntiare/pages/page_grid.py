# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from get_report_items import get_report_items
from page_item import PageItem
from ..tools import raise_error_with_log, get_expression_value_or_default
from ..definition.data.data import DataGroup

class PageGrid(PageItem):
    def __init__(self, report_item_def, grid_type="Grid"):
        super(PageGrid, self).__init__("PageGrid", report_item_def)
        self.columns = []
        self.rows = []
        self.grid_type = grid_type

        columns = report_item_def.get_element("Columns")
        sum_width = 0
        for c in columns.column_list:          
            visible = get_expression_value_or_default(c, "Visibility", True)
            width = get_expression_value_or_default(c, "Width", 0)
            if width == 0:
                visible = False
            col = GridColumn(visible, width)
            sum_width = sum_width + width
            self.columns.append(col)
        self.width = sum_width

        if grid_type == "Grid": 
            self.run_rows(report_item_def.get_element("Rows"))
        elif grid_type == "Table":
            data_set_name = get_expression_value_or_default(report_item_def, "DataSetName", None)
            if not report_item_def.lnk.report.data_sets.has_key(data_set_name):
                raise_error_with_log("DataSetName '{0}' not found for Table '{1}'".format(data_set_name, self.name))
            grouping = TableGroupings(report_item_def.lnk.report.data_sets[data_set_name].data, 
                    report_item_def)
 
            header = report_item_def.get_element("Header")
            footer = report_item_def.get_element("Footer")

            grouping.groupings[0].data[0].EOF() # Puts this data as current
            if header:
                self.run_rows(header.get_element("Rows"))

            idx=[]
            for g in grouping.groupings:
                idx.append([0,0])

            for data in grouping.groupings[0].data:
                self.run_details(grouping, 0, idx, data)

            grouping.groupings[0].data[0].EOF() # Puts this data as current
            if footer:
                self.run_rows(footer.get_element("Rows"))

    def run_details(self, grouping, grouping_i, idx, data_grp=None):
        if grouping_i == 0:
            data = data_grp 
            data_index = idx[grouping_i][0]
        else:
            data_index = idx[grouping_i - 1][1]
            data = grouping.groupings[grouping_i].data[data_index]

        if data.has_groups():
            for group in data.groups:
                group_index = idx[grouping_i][1]
                group.move(group_index)

                if grouping.groupings[grouping_i].header:
                    self.run_rows(grouping.groupings[grouping_i].header.get_element("Rows"))

                self.run_details(grouping, grouping_i + 1, idx)

                group.EOF() # Puts this data as current

                if grouping.groupings[grouping_i].footer:
                    self.run_rows(grouping.groupings[grouping_i].footer.get_element("Rows"))
                idx[grouping_i][1] = group_index + 1

        else:
            detail = grouping.groupings[grouping_i].data[idx[grouping_i - 1][1]]
            detail.move_first()
            while not detail.EOF():
                self.run_rows(self.report_item_def.get_element("Details").get_element("Rows"))    
                detail.move_next()
        
        idx[grouping_i][0] = data_index + 1 

    def run_rows(self, rows):
        if not rows:
            return
        for row in rows.row_list: 
            cells = row.get_element("Cells")
            if not cells:
                raise_error_with_log("Cells not found in grid Row. {0} name: '{1}'".format(self.grid_type, self.name))
            visible = get_expression_value_or_default(row, "Visibility", True)
            r = GridRow(visible, get_expression_value_or_default(row, "Height", 8), cells, self.columns)
            self.rows.append(r)


class PageTable(PageGrid):
    def __init__(self, report_item_def):
        super(PageTable, self).__init__(report_item_def, grid_type="Table")


class GridColumn(object):
    def __init__(self, visible, width):
        self.visible = visible
        self.width = width


class GridRow(object):
    def __init__(self, visible, height, cells, cols):
        self.visible = visible
        self.height = height
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


class RowCell(object):
    def __init__(self, cell):
        self.type = "RowCell"
        self.col_span = int(get_expression_value_or_default(cell, "ColSpan", 1))
        self.width = 0
        self.cell_def = cell
        self.item_list=get_report_items(cell, self)


class TableGroupings(object):
    def __init__(self, data, table_def):
        self.columns = data.columns
        self.groupings=[]
        self.details=None

        element_groups = table_def.get_element("TableGroups")
        if element_groups:
            for gr in element_groups.group_list:
                self.groupings.append(TableGrouping(gr, gr.get_element("Grouping"), gr.get_element("Sorting")))
        element_details = table_def.get_element("Details")
        self.groupings.append(TableGrouping(None, element_details.get_element("Grouping"), 
                    element_details.get_element("Sorting"), name="{0}_{1}".format(data.name, "details")))

        parent_g=None
        for g in self.groupings:
            if not parent_g:
                g.add_data (DataGroup(data, g.name, g.grouping_def, g.sorting_def, g.filter_def))
                g.data[0].do_filter()
                g.data[0].sort()
                g.data[0].create_groups()
            else:
                for d in parent_g.data:
                    i=0
                    for dgp in d.groups: 
                        g.add_data(DataGroup(dgp, parent_g.name + d.name + str(i), g.grouping_def, g.sorting_def, g.filter_def))
                        i=i+1
                for g_data in g.data:
                    g_data.do_filter()
                    g_data.sort()
                    g_data.create_groups()
            parent_g = g

class TableGrouping(object):
    def __init__(self, table_def, grouping_def, sorting_def, name=None):
        self.name = None
        self.grouping_def = grouping_def
        self.sorting_def = sorting_def
        self.filter_def = None
        self.header=None
        self.footer=None
        self.data=[]

        if not grouping_def:
            self.name = name
        else:
            self.name = get_expression_value_or_default(grouping_def, "Name", None)
        if not self.name:
            raise_error_with_log("'Name' is required for DataSet or Grouping element.")

        if grouping_def:
            self.filter_def = grouping_def.get_element("Filters")

        if table_def:
            self.header = table_def.get_element("Header")
            self.footer = table_def.get_element("Footer")

    def add_data(self, data):
        self.data.append(data)        

