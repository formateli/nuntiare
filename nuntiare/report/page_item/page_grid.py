# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from . page_item import PageItem, PageItemsInfo
from ... import logger
from ... definition.expression import Expression

class PageGrid(PageItem):
    def __init__(self, report, grid_def, parent):
        super(PageGrid, self).__init__("PageGrid", report, grid_def, parent)
        
        self.data_set = None
        self.column_h = TablixHierarchy(report, grid_def.get_element("TablixColumnHierarchy"))
        self.row_h = TablixHierarchy(report, grid_def.get_element("TablixRowHierarchy"))
        
        data_set_name = Expression.get_value_or_default(report, grid_def, 
                                                        'DataSetName', None)
        if data_set_name:
            if not data_set_name in report.data_sets:
                logger.error(
                    "Dataset '{0}' not found for Tablix '{1}'".format(data_set_name, self.name), True
                    )
            self.data_set = report.data_sets[data_set_name]

        self.columns = []
        self.rows = []
        
        columns = grid_def.get_element("TablixBody").get_element("TablixColumns")
        if len(columns.column_list) != len(self.column_h.members):
            logger.error(
                "The quantity of TablixColumn must be equal to " + \
                "the quantity of Members of TablixColumnHierarchy", True
                )
        
        sum_width = 0
        for c in columns.column_list:
            hidden = False
            width = Expression.get_value_or_default(report, c, 'Width', 0.0)
            if width == 0:
                hidden = True
            col = GridColumn(hidden, width)
            sum_width = sum_width + width
            self.columns.append(col)
        self.width = sum_width        
        self.run_rows(grid_def.get_element("TablixBody").get_element("TablixRows"))

    def run_rows(self, rows_def):
        rws = []
        if not rows_def:
            return rws
        for row in rows_def.row_list: 
            cells = row.get_element("TablixCells")
            if not cells:
                logger.error("TablixCells not found in Tablix '{0}'".format(self.name), True)
            hidden = False
            r = GridRow(self.report, hidden, 
                    Expression.get_value_or_default(self.report, row, 'Height', 0.0),
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
            logger.error("'CellContents' is required by 'TablixCell'", True)
    
        self.type = "RowCell" # We treat it as a ReportItem because it can be a parent of a report item
        self.report = report
        self.col_span = int(Expression.get_value_or_default(report, self.contents, "ColSpan", 1))
        self.row_span = int(Expression.get_value_or_default(report, self.contents, "RowSpan", 1))
        self.top=0
        self.left=0
        self.height = height
        self.width = 0 # Given according to column(s) width
        self.cell_def = cell
        self.items_info=None
        
    def get_items(self):
        self.items_info = PageItemsInfo(self.report, self.contents, self)
        if len(self.items_info.item_list) > 1:
            logger.error("'CellContents' element must have just one 'ReportItem'.", True)


class TablixHierarchy(object):
    def __init__(self, report, definition):
        self.members=[]
        members_def = definition.get_element("TablixMembers")
        for m in members_def.member_list:
            self.members.append(TablixMember(report, m, None))
            

class TablixMember(object):
    def __init__(self, report, definition, parent):
        self.members=[]
        self.parent=parent
        self.children=[]
        self.is_static=True
        self.fixed_data=Expression.get_value_or_default(report,definition,"FixedData",False)
        self.hide_if_no_rows=Expression.get_value_or_default(report,definition,"HideIfNoRows",False)
        self.repeat_on_new_page=Expression.get_value_or_default(report,definition,"RepeatOnNewPage",False)        
        #TODO Hidden
        self.show=True
        
        if parent:
            parent.children.append(self)
        
        members_def = definition.get_element("TablixMembers")
        if members_def:
            for m in members_def.member_list:
                self.members.append(TablixMember(report, m, self))   

