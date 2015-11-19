# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from . page_item import PageItem, PageItemsInfo
from .. import logger
from .. data.data import DataGroupObject

class PageTablix(PageItem):
    def __init__(self, report, tablix_def, parent):
        super(PageTablix, self).__init__("PageTablix", report, tablix_def, parent)

        data_set = None
        tablix_group = None
        data_set_name = report.get_value(
                tablix_def, 'DataSetName', None)

        if data_set_name:
            if not data_set_name in report.data_sets:
                logger.error(
                    "Dataset '{0}' not found for Tablix '{1}'".format(
                        data_set_name, self.name), True)
            data_set = report.data_sets[data_set_name]
            tablix_group = DataGroupObject(
                report, self.name, report.data_groups[data_set_name])
            tablix_group.create_instances(tablix_def)

        self.column_hierarchy = TablixHierarchy(
            report, tablix_def.get_element(
                "TablixColumnHierarchy"), tablix_group)
        self.row_hierarchy = TablixHierarchy(
            report, tablix_def.get_element(
                "TablixRowHierarchy"), tablix_group)

        columns = tablix_def.get_element("TablixBody").get_element("TablixColumns")
        rows = tablix_def.get_element("TablixBody").get_element("TablixRows")

        if not data_set:
            # It is a simple grid.
            # We redefine both Hierarchies with empty members (static)
            # according to columns and rows count.
            self.column_hierarchy.members = []
            for col in columns.column_list:
                member = TablixMember(self.column_hierarchy, report, None, None, None)
                self.column_hierarchy.members.append(member)
            self.row_hierarchy.members = []
            for rw in rows.row_list:
                member = TablixMember(self.row_hierarchy, report, None, None, None)
                self.row_hierarchy.members.append(member)

        self.grid_body = Grid()

        # Validate total columns and rows according to hierarchies.
        self.validate_hierarchy(rows.row_list, columns.column_list)

        # Move all data and instances to its first value.
        self.all_to_first(self.row_hierarchy.members)
        self.all_to_first(self.column_hierarchy.members)

        #self.set_cells_width()
        self.get_body()        

        self.width = self.grid_body.width
        self.height = self.grid_body.height

    def validate_hierarchy(self, rows, columns):
        err = "There must be as many Columns/Rows elements as there are " \
            "leaf-node (that is, has no sub-groups) TablixMembers in " \
            "corresponding Hierarchy."

        index = self._validate_hierarchy(
            "Columns", self.column_hierarchy.members, columns, err)
        self._check_hierarchy_index(
            "Columns", index, columns, err, ending=True)
        
        index = self._validate_hierarchy(
            "Rows", self.row_hierarchy.members, rows, err)
        self._check_hierarchy_index(
            "Rows", index, rows, err, ending=True)

    def _check_hierarchy_index(self, type_, index, items, err, ending=False):
        if not ending:
            if index > len(items) - 1:
                logger.error(
                    "Number of {0} is lower than its hierarchy definition. {1}/{2}. {3}.".format(
                        type_, len(items), index + 1, err), True)
        else:
            if len(items) - 1 >= index:
                logger.error(
                    "Number of {0} is greater than its hierarchy definition. {1}/{2}. {3}.".format(
                        type_, len(items) - 1, index, err), True)

    def _validate_hierarchy(self, type_, members, items, err, index=0):
        for member in members:
            if not member.members:
                self._check_hierarchy_index(
                    type_, index, items, err)                
                member.set_definition(type_, items[index])
                index += 1
            else:
                index = self._validate_hierarchy(
                    type_, member.members, items, err, index)
        return index

    def get_body(self):
        self._get_body(self.row_hierarchy.members)

    def _get_body(self, members, row_count=0, parent_group=None):
        for member in members:
            if not member.group:
                self._do_cells(member.def_object, row_count)
                row_count += 1
            elif member.group and not member.group.is_detail_group:
                i = 0
                while not member.group.EOF:
                    row_count = self._get_body(
                        member.members, row_count, member.group)
                    member.group.move_next()
                    i += 1
                    if parent_group:
                        if i >= len(parent_group.current_instance().sub_instance):
                            break

            elif member.group.is_detail_group:
                if parent_group:
                    member.group.move(parent_group._current_instance_index)
                else:
                    member.group.move(0)
                data = member.group.current_instance().data
                data.move_first()
                while not data.EOF:
                    self._do_cells(member.def_object, row_count)
                    data.move_next()
                    row_count += 1
            else: #TODO members of no groups member?
                print("TODO")
                pass

        return row_count

    def _do_cells(self, row, row_index):
        i = 0
        cols = self.column_hierarchy.rows_columns
        self.report.current_data_scope = [row.member.scope, None]
        for cell in row.cells:
            if i == len(cols):
                logger.error(
                    "Number of cells exceeds number of columns", True)
            x = 1
            sum_width = 0
            grid_cell = None
            while x <= cell.col_span:
                curr_col = cols[i + (x - 1)]
                if not curr_col.member.is_static:
                    logger.error("ColSpan only possible on static members. Tablix '{0}'".format(
                        self.name), True)
                self.report.current_data_scope[1] = curr_col.member.scope
                if x == 1:
                    grid_cell = self.grid_body.add_cell(
                        row_index, i, cell, 
                        col_span=cell.col_span, row_span=cell.row_span)
                sum_width += curr_col.width
                x += 1
            grid_cell.width = sum_width
            grid_cell.height = cell.height
            item_info = grid_cell.object.get_items(grid_cell)
            grid_cell.object = item_info
            if item_info.total_height > self.height:
                self.height = item_info.total_height
            i += (x - 1)
        self.report.current_data_scope = [None, None]

    def all_to_first(self, members):
        for member in members:
            if member.group:
                if member.group.instance:
                    member.group.move_first()
                    for instance in member.group.instance:
                        instance.data.move_first()
            if member.members:
                self.all_to_first(member.members)


class TablixHierarchy(object):
    def __init__(self, report, definition, tablix_group):        
        self.members = []
        self.rows_columns = []
        members_def = definition.get_element("TablixMembers")
        if members_def:
            for member in members_def.member_list:
                self.members.append(
                    TablixMember(self, report, member, None, tablix_group))


class TablixMember(object):
    class Column():
        def __init__(self, member, definition):
            self.member = member
            self.width = member.report.get_value(
                definition, "Width", 0.0)

    class Row():
        class Cell():
            def __init__(self, report, definition, height):
                self.report = report
                self.height = height
                self.contents = definition.get_element('CellContents')
                self.row_span = int(report.get_value(
                    self.contents, "RowSpan", 1))
                self.col_span = int(report.get_value(
                    self.contents, "ColSpan", 1))

            def get_items(self, grid_cell):
                items_info = PageItemsInfo(self.report, self.contents, grid_cell)
                if len(items_info.item_list) > 1:
                    logger.error(
                        "'CellContents' element must have just one 'ReportItem'.", True)
                return items_info

        def __init__(self, member, definition):
            self.member = member
            self.hidden = False #TODO
            self.height = member.report.get_value(
                    definition, "Height", 0.0)
            self.cells = []
            cells_def = definition.get_element("TablixCells")
            if cells_def:
                for cell in cells_def.cell_list:
                    self.cells.append(TablixMember.Row.Cell(member.report, cell, self.height))

    def __init__(self, hierarchy, report, definition, 
            parent_member, parent_data_group):
        '''
        hierarchy: The TablixHierarchy object which owns this member.
        report: The report object.
        definition: The nuntiare TablixMember definition.
        parent_member: Parent member.
        parent_data_group: The parent data. TablixGroup for First members.
        '''
        self.hierarchy = hierarchy
        self.report = report
        self.members = []
        self.parent_member = parent_member
        self.children = []
        self.fixed_data = report.get_value(
            definition, "FixedData", False)
        self.hide_if_no_rows = report.get_value(
            definition, "HideIfNoRows", False)
        self.repeat_on_new_page = report.get_value(
            definition, "RepeatOnNewPage", False)
        self.group = None
        self.scope = None
        self.is_static = True
        self.def_object = None  # Row or Column definition.

        if definition:
            group_def = definition.get_element("Group")
            if group_def:
                self.group = DataGroupObject(
                    report, group_def.Name, parent_data_group)
                self.group.create_instances(group_def)

        if self.group:
            self.scope = self.group.name
            self.is_static = False
        else:
            self.scope = parent_data_group.name

        if parent_member:
            if parent_member.is_static:
                self.is_static = False
            parent_member.children.append(self)

        if definition:
            members_def = definition.get_element("TablixMembers")
            group_to_parent = self.group if self.group else parent_data_group
            if members_def:
                for member in members_def.member_list:
                    self.members.append(
                        TablixMember(hierarchy, report, member, self, group_to_parent))

    def set_definition(self, type_, row_column_def):
        if type_ == "Rows":
            self.def_object = TablixMember.Row(self, row_column_def)
        else:
            self.def_object = TablixMember.Column(self, row_column_def)
        self.hierarchy.rows_columns.append(self.def_object)
        

class Grid(object):
    ''' 
    Thought as a spreadsheet,
    zero to one cell per row/column coordinate.
    If one group expands then row/column of grid increases
    in number and others cells may span.
    '''

    class Column(object):
        def __init__(self, index):
            self.width = 0.0
            self.index = index
            self.cells = []

    class Row(object):
        class Cell(object):
            def __init__(self, grow_direction, row, cell_object):
                self.type = "RowCell"
                self.object = cell_object
                self.row = row
                self.row_span = 1
                self.col_span = 1
                self._grow_direction = grow_direction
                self._auto_span_count = 0
                self._parent_cell = None
                self._children_cells = []
                
                self.top = 0.0
                self.left = 0.0
                self.height = 0.0
                self.width = 0.0 # Given according to column(s) width

            def set_parent(self, parent, columns, column):
                if not parent:
                    return
                self._parent_cell = parent
                self._parent_cell._children_cells.append(self)
                parent._auto_span(columns, column)

            def _auto_span(self, columns, column):
                self._auto_span_count += 1
                if self._grow_direction == "row":
                    column = columns[column.index - 1]
                    self.row_span = self._auto_span_2(self.row_span, columns, column)
                    if self.row_span > 1:
                        column.cells[self.row.index + (self.row_span - 1)] = self
                else:
                    self.col_span = self._auto_span_2(self.col_span, columns, column)
                    if self.col_span > 1:
                        column.cells[self.row.index] = self

            def _auto_span_2(self, unit_to_span, columns, column):
                result = unit_to_span
                if self._auto_span_count > unit_to_span:
                    result = self._auto_span_count
                    if self._parent_cell:
                        self._parent_cell._auto_span(columns, column)
                return result

        def __init__(self, index):
            self.height = 0.0
            self.index = index
            self.cells = []
            
        def add_cell(self, grow_direction, cell_object):
            cell = Grid.Row.Cell(grow_direction, self, cell_object)
            self.cells.append(cell)
            return cell

    def __init__(self, grow_direction="row"):
        self._grow_direction = grow_direction
        self.columns = []
        self.rows = []
        self.height = 0.0
        self.width = 0.0

    def add_cell(self, row_index, column_index,
            cell_object=None, row_span=1, col_span=1, 
            parent_cell=None):

        row, new_row = self._get_item(
            row_index, self.rows, Grid.Row)
        column, new_column = self._get_item(
            column_index, self.columns, Grid.Column)
        
        cell = row.add_cell(self._grow_direction, cell_object)

        if new_row:
            for col in self.columns:
                col.cells.append(None)
            column.cells.pop() # Remove last None of current column
            column.cells.append(cell)
        else:
            if new_column and len(self.rows) == 0:
                column.cells.append(cell)
            elif new_column and len(self.rows) > 0:
                i = 0
                while i < len(self.rows):
                    column.cells.append(None)
                    i += 1
                column.cells.pop(row_index)
                column.cells.insert(row_index, cell)
            else:
                column.cells.pop(row_index)
                column.cells.insert(row_index, cell)

        cell.col_span = col_span
        cell.row_span = row_span
        
        cell.set_parent(parent_cell, self.columns, column)
                
        if col_span > 1:
            i = 1
            while i < col_span:
                self.add_cell(
                    row_index, column_index + i)
                self.columns[column_index + i].cells.pop(row_index)
                self.columns[column_index + i].cells.insert(row_index, cell)
                i += 1

        if row_span > 1:
            i = 1
            while i < row_span:
                self.add_cell(
                    row_index + i, column_index)
                self.columns[column_index].cells.pop(row_index + i)
                self.columns[column_index].cells.insert(row_index + i, cell)
                i += 1
                
        if col_span > 1 and row_span > 1:
            # Intersection    
            i = row_index + 1
            while i < (row_index + row_span):
                x = column_index + 1
                while x < (column_index + col_span):
                    self.columns[x].cells.pop(i)
                    self.columns[x].cells.insert(i, cell)
                    x += 1
                i += 1
        
        return cell

    def get_cell(self, row_index, column_index):
        col = self.columns[column_index]
        return col.cells[row_index]
        
    def next_column(self):
        return len(self.columns)

    def next_row(self):
        return len(self.rows)

    def set_column_width(self, index, width):
        col = self.columns[index]
        col.width = width
        self.width += width

    def set_row_height(self, index, height):
        row = self.rows[index]
        row.height = height
        self.height += height

    def extend(self, grid, direction):
        if direction == "right":
            if len(self.rows) != len(grid.rows):
                logger.error(
                    "To extend Grid to the right, both rows length must be equal.", True)
            i = 0
            for row in grid.rows:
                self.rows[i].cells.extend(row.cells)
                i += 1
            self.columns.extend(grid.columns)

        else: # Down
            if len(self.columns) != len(grid.columns):
                logger.error(
                    "To extend Grid down, both columns length must be equal.", True)
            i = 0
            for column in grid.columns:
                self.columns[i].cells.extend(column.cells)
                i += 1
            self.rows.extend(grid.rows)

    def _get_item(self, index, collection, class_):
        new = False
        if index == len(collection):
            item = class_(index)
            collection.append(item)
            new = True
        elif index > len(collection):
            logger.error(
                "Grid must increase by one Row/Column.", True)
        else:
            item = collection[index]
        return item, new

