# This file is part of Nuntiare project.

# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from . page_item import PageItem, PageItemsInfo
from .. import LOGGER
from .. data.data import DataGroupObject


class HeaderItem(object):
    def __init__(self, type_, member, parent):
        self.type = type_
        self.member = member
        self.cell = None
        self.parent = parent
        self.sub_items = []
        self.has_items = False
        self.level = None
        self.span = 0
        self.last_items_count = 0
        if parent:
            parent.sub_items.append(self)

    def run(self):
        grid = Grid()
        self.cell = grid.add_cell(
            0, 0, self.member.header.cell)
        self._validate_init_span()
        self._run_grid_cell(
            self.cell, self.member.header.size)
        span = self._get_span()
        is_last = False
        if self.member.def_object:
            is_last = True
        if self.type == 'Column':
            self.cell.row_span = span
            if self.member.def_object:
                self._update_info(self.member.def_object.width, is_last)
        else:
            self.cell.col_span = span
            if self.member.def_object:
                self._update_info(self.member.def_object.height, is_last)
        self._has_items()

    def _update_info(self, size, is_last):
        self.span += 1
        if is_last:
            self.last_items_count += 1
        if self.type == 'Column':
            self.cell.col_span = self.span
            self.cell.width += size
        else:
            self.cell.row_span = self.span
            self.cell.height += size
        if self.parent:
            self.parent._update_info(size, is_last)

    def _run_grid_cell(self, grid_cell, size):
        grid_cell.width = 0.0
        grid_cell.height = 0.0
        if self.type == 'Column':
            grid_cell.height = size
        else:
            grid_cell.width = size
        if grid_cell.object:
            item_info = grid_cell.object.get_items(grid_cell)
            grid_cell.object = item_info

    def _has_items(self):
        self.has_items = True
        if self.parent:
            self.parent._has_items()

    def _validate_init_span(self):
        if not self.cell:
            return
        if self.cell.col_span > 1 or self.cell.row_span > 1:
            LOGGER.error(
                'ColSpan and RowSpan are not allowed in members headers.')

    def _get_span(self):
        def get_index(sizes, cumulative_size):
            i = 0
            while i < len(sizes):
                if abs(sizes[i] - cumulative_size) < 0.001:
                    return i
                i += 1
            return -1

        if self.member.header.size == 0.0:
            return 0
        if self.member.header.span > 0:
            self.level = self.member.header.level
            return self.member.header.span

        sizes = self.member.hierarchy.cumulative_sizes
        index = get_index(
            sizes, self.member.header.cumulative_size)
        top_index = get_index(
            sizes,
            self.member.header.cumulative_size - self.member.header.size)

        self.member.header.level = top_index + 1
        self.level = self.member.header.level
        self.member.header.span = index - top_index

        return self.member.header.span


class PageTablix(PageItem):
    def __init__(self, report, tablix_def, parent):
        super(PageTablix, self).__init__(
            'PageTablix', report, tablix_def, parent)

        data_set = None
        tablix_group = None
        data_set_name = report.get_value(
            tablix_def, 'DataSetName', None)

        if data_set_name:
            if data_set_name not in report.data_sets:
                LOGGER.error(
                    "Dataset '{0}' not found for Tablix '{1}'".format(
                        data_set_name, self.name), True)
            data_set = report.data_sets[data_set_name]
            tablix_group = DataGroupObject(
                report, self.name, report.data_groups[data_set_name])
            tablix_group.create_instances(tablix_def)

        self.column_hierarchy = TablixHierarchy(
            'Columns', report, tablix_def.get_element(
                'TablixColumnHierarchy'), tablix_group)
        self.row_hierarchy = TablixHierarchy(
            'Rows', report, tablix_def.get_element(
                'TablixRowHierarchy'), tablix_group)
        self.page_break = report.get_value(
            tablix_def.get_element('PageBreak'), 'BreakLocation', None)

        columns = tablix_def.get_element(
            'TablixBody').get_element('TablixColumns')
        rows = tablix_def.get_element(
            'TablixBody').get_element('TablixRows')

        if not data_set:
            # It is a simple grid.
            # We redefine both Hierarchies with empty members (static)
            # according to columns and rows count.
            self.column_hierarchy.members = []
            for col in columns.column_list:
                member = TablixMember(
                    self.column_hierarchy, report,
                    None, None, None, None)
                self.column_hierarchy.members.append(member)
            self.row_hierarchy.members = []
            for rw in rows.row_list:
                member = TablixMember(
                    self.row_hierarchy, report,
                    None, None, None, None)
                self.row_hierarchy.members.append(member)
            # TODO No headers are allowed, raise an error if so.

        self.column_hierarchy.validate(columns.column_list)
        self.row_hierarchy.validate(rows.row_list)

        for row in self.row_hierarchy.rows_columns:
            if len(row.cells) != len(self.column_hierarchy.rows_columns):
                err = "Number of cells and columns must be equal. {0}/{1}"
                LOGGER.error(err.format(
                    len(row.cells), len(self.column_hierarchy.rows_columns)),
                    True)

        self.column_header_groups = []
        self.all_to_first(self.column_hierarchy.members)
        self._get_header('Column', self.column_hierarchy.members)

        self.row_header_groups = []
        self.all_to_first(self.row_hierarchy.members)
        self._get_header('Row', self.row_hierarchy.members)

        self.tablix_corner = self._get_tablix_corner(
            tablix_def.get_element('TablixCorner'))

        self.grid_body = Grid()
        self.all_to_first(self.row_hierarchy.members)
        self.all_to_first(self.column_hierarchy.members)
        self.get_body()

        self.width = self.grid_body.width
        self.height = self.grid_body.height

    def _get_tablix_corner(self, corner_def):
        if not corner_def:
            return

        if not self.row_hierarchy.has_header() or \
                not self.column_hierarchy.has_header():
            LOGERR.error(
                'ColumnHierarchy and RowHierarchy headers '
                'must be defined for TablixCorner.', True)
            return

        if len(corner_def.TablixCornerRows.row_list) != \
                len(self.column_hierarchy.cumulative_sizes):
            LOGGER.error(
                'Number of corner rows must be equal to '
                'number of rows in tablix column header', True)

        return TablixCorner(
            self.report, corner_def,
            self.column_hierarchy, self.row_hierarchy)

    def _get_header(
            self, type_, members,
            parent_item=None, parent_group=None):

        def append_to_group(type_, item):
            if not item or not item.has_items:
                return
            if type_ == 'Column':
                groups = self.column_header_groups
            else:
                groups = self.row_header_groups
            groups.append(item)

        for member in members:
            if not member.group:
                header_item = HeaderItem(
                    type_, member, parent_item)
                header_item.run()
                if member.members:
                    self._get_header(
                        type_, member.members,
                        header_item, None)
                if not parent_item:
                    append_to_group(type_, header_item)

            elif not member.group.is_detail_group:
                i = 0
                while not member.group.EOF:
                    self.report.current_data_scope = [
                        member.scope, None]
                    header_item = HeaderItem(
                        type_, member, parent_item)
                    header_item.run()
                    if member.members:
                        self._get_header(
                            type_, member.members,
                            header_item, member.group)
                    if not parent_item:
                        append_to_group(type_, header_item)
                    member.group.move_next()
                    i += 1
                    if parent_group:
                        if i >= len(
                                parent_group.current_instance().sub_instance):
                            break

            elif member.group.is_detail_group:
                if type_ == 'Column':
                    LOGGER.error(
                        'Detail group in column hierarchy is not supported',
                        True)
                header_item = None
                if parent_group:
                    member.group.move(parent_group._current_instance_index)
                else:
                    member.group.move(0)
                data = member.group.current_instance().data
                while not data.EOF:
                    data.move_next()
                    if not parent_item:
                        append_to_group(type_, header_item)

    def get_body(self):
        self._run_rows(self.row_hierarchy.members)

    def _run_rows(self, members, row_count=0, parent_group=None):
        for member in members:
            row_instance = None
            if not member.group:
                if member.group_belongs:
                    row_instance = \
                        member.group_belongs.current_instance().data.name
                if member.def_object:
                    self._run_cols(
                        self.column_hierarchy.members,
                        member.def_object, row_count,
                        row_instance=row_instance)
                    row_count += 1
                elif member.children:
                    row_count = self._run_rows(
                        member.members, row_count, None)

            elif not member.group.is_detail_group:
                i = 0
                while not member.group.EOF:
                    row_instance = \
                        member.group.current_instance().data.name
                    if member.def_object:
                        self._run_cols(
                            self.column_hierarchy.members,
                            member.def_object, row_count,
                            row_instance=row_instance)
                        row_count += 1
                    else:
                        row_count = self._run_rows(
                            member.members, row_count, member.group)
                    member.group.move_next()
                    i += 1
                    if parent_group:
                        if i >= len(
                                parent_group.current_instance().sub_instance):
                            break

            elif member.group.is_detail_group:
                if parent_group:
                    member.group.move(parent_group._current_instance_index)
                else:
                    member.group.move(0)
                data = member.group.current_instance().data
                while not data.EOF:
                    self._run_cols(
                        self.column_hierarchy.members,
                        member.def_object, row_count,
                        row_instance=data.name)
                    data.move_next()
                    row_count += 1

        return row_count

    def _run_cols(
            self, members, row, row_index,
            col_count=0, parent_group=None,
            is_new_row=True, row_instance=None):

        if is_new_row:
            self.all_to_first(
                self.column_hierarchy.members)

        for member in members:
            col_instance = None
            if not member.group:
                if member.group_belongs:
                    col_instance = \
                        member.group_belongs.current_instance().data.name
                if member.def_object:
                    self._do_cell(
                        row, row_index,
                        member.def_object,
                        col_count,
                        row_instance,
                        col_instance=col_instance)
                    col_count += 1
                elif member.children:
                    col_count = self._run_cols(
                        member.members, row, row_index,
                        col_count, None, False,
                        row_instance=row_instance)

            elif not member.group.is_detail_group:
                i = 0
                while not member.group.EOF:
                    data = member.group.current_instance().data
                    if member.def_object:
                        self._do_cell(
                            row, row_index,
                            member.def_object, col_count,
                            row_instance,
                            col_instance=data.name)
                        col_count += 1
                    else:
                        col_count = self._run_cols(
                            member.members, row, row_index,
                            col_count, member.group, False,
                            row_instance=row_instance)
                    member.group.move_next()
                    i += 1
                    if parent_group:
                        if i >= len(
                                parent_group.current_instance().sub_instance):
                            break

            elif member.group.is_detail_group:
                LOGGER.error(
                    'Detail group in column hierarchy is not supported',
                    True)

        return col_count

    def _do_cell(
            self, row, row_index, col, col_index,
            row_instance, col_instance):
        self.report.current_data_scope = [
                row.member.scope,
                col.member.scope
            ]
        cell = row.cells[col.index]
        grid_cell = self.grid_body.add_cell(
            row_index, col_index, cell,
            col_span=cell.col_span,
            row_span=cell.row_span,
            row_member=row.member,
            col_member=col.member,
            row_instance=row_instance,
            col_instance=col_instance)

        grid_cell.width = col.width
        grid_cell.height = cell.height
        item_info = grid_cell.object.get_items(grid_cell)
        grid_cell.object = item_info
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
    def __init__(self, type_, report, definition, tablix_group):
        self.type = type_
        self.members = []
        self.rows_columns = []
        self.cumulative_sizes = []
        members_def = definition.get_element('TablixMembers')
        if members_def:
            header_size = 0.0
            for member in members_def.member_list:
                mb = TablixMember(
                    self, report, member,
                    parent_member=None,
                    parent_data_group=tablix_group,
                    group_belongs=None)
                if header_size == 0.0:
                    header_size = mb.header.get_total_size()
                else:
                    if mb.header.get_total_size() != header_size:
                        err = 'Peers members header size ' \
                            'must be equal.'
                        LOGGER.error(err, True)
                self.members.append(mb)

        if self.cumulative_sizes:
            z_list = []
            for size in self.cumulative_sizes:
                l = (size, None)
                z_list.append(l)
            res = sorted(z_list, key=lambda z: z[0])
            self.cumulative_sizes = []
            for r in res:
                self.cumulative_sizes.append(r[0])

    def validate(self, rows_cols):
        err = "There must be as many Columns/Rows elements as there are " \
            "leaf-node (that is, has no sub-groups) TablixMembers in " \
            "corresponding Hierarchy."

        index = self._validate_hierarchy(
            self.members, rows_cols, err)
        self._check_hierarchy_index(
            index, rows_cols, err, ending=True)

    def check_cumulative_size(self, size):
        if not size:
            return
        if size not in self.cumulative_sizes:
            self.cumulative_sizes.append(size)

    def has_header(self):
        if self.cumulative_sizes:
            return True

    def _validate_hierarchy(self, members, items, err, index=0):
        for member in members:
            if not member.members:
                self._check_hierarchy_index(index, items, err)
                member.set_definition(self.type, items[index], index)
                index += 1
            else:
                index = self._validate_hierarchy(
                    member.members, items, err, index)
        return index

    def _check_hierarchy_index(
            self, index, items, err, ending=False):
        if not ending:
            if index > len(items) - 1:
                err_msg = "Number of {0} is lower than its " \
                    "hierarchy definition. {1}/{2}. {3}."
                LOGGER.error(err_msg.format(
                    self.type, len(items), index + 1, err), True)
        else:
            if len(items) - 1 >= index:
                err_msg = "Number of {0} is greater than its " \
                    "hierarchy definition. {1}/{2}. {3}."
                LOGGER.error(err_msg.format(
                    self.type, len(items) - 1, index, err), True)


class TablixCell(object):
    def __init__(self, report, definition, height):
        self.report = report
        self.height = height
        self.contents = definition.get_element('CellContents')
        self.row_span = int(report.get_value(
            self.contents, 'RowSpan', 1))
        self.col_span = int(report.get_value(
            self.contents, 'ColSpan', 1))
        self.items_info = None

    def get_items(self, grid_cell):
        self.items_info = PageItemsInfo(
            self.report, self.contents, grid_cell)
        if len(self.items_info.item_list) > 1:
            err_msg = "'CellContents' element must have " \
                "just one 'ReportItem'."
            LOGGER.error(err_msg, True)
        return self.items_info


class TablixMember(object):
    class Header():
        def __init__(self, member):
            self.member = member
            self.size = 0.0
            self.cumulative_size = 0.0
            self.span = 0
            self.level = None
            self.cell = None
            self.defined = False
            self.textbox_name = None

        def set_header(self, header_definition):
            if not header_definition:
                return
            self.size = self.member.report.get_value(
                header_definition, 'Size', 0.0)
            self.cell = TablixCell(
                self.member.report, header_definition, 0.0)
            self._check_cumulative_size()

            if self.cell.contents:
                reportitems = \
                    self.cell.contents.get_element('ReportItems')
                if reportitems:
                    textbox = reportitems.get_element('Textbox')
                    if textbox:
                        self.textbox_name = textbox.Name
            self.defined = True

        def get_total_size(self):
            size = self.size
            size += self._get_size(self.member.children)
            return size

        def _get_size(self, children):
            if not children:
                return 0.0
            size = 0.0
            for child in children:
                size += child.header.size
                size += self._get_size(child.children)
                return size  # Just one

        def _check_cumulative_size(self):
            parent = self.member.parent_member
            cumulative = self.size
            while parent:
                cumulative += parent.header.size
                parent = parent.parent_member
            self.cumulative_size = cumulative
            self.member.hierarchy.check_cumulative_size(cumulative)

    class Column():
        def __init__(self, member, definition, index):
            self.member = member
            self.width = member.report.get_value(
                definition, 'Width', 0.0)
            self.index = index

    class Row():
        def __init__(self, member, definition, index):
            self.member = member
            self.hidden = False  # TODO
            self.height = member.report.get_value(
                definition, 'Height', 0.0)
            self.cells = []
            self.index = index
            cells_def = definition.get_element('TablixCells')
            if cells_def:
                for cell in cells_def.cell_list:
                    self.cells.append(
                        TablixCell(
                            member.report, cell, self.height))

    def __init__(
            self, hierarchy, report, definition,
            parent_member, parent_data_group, group_belongs):
        '''
        hierarchy: The TablixHierarchy object which owns this member.
        report: The report object.
        definition: The nuntiare TablixMember definition.
        parent_member: Parent member.
        parent_data_group: The parent data. TablixGroup for First members.
        group_belongs: Group for wich this member belongs. Usefull in case
            member is static but is part of a group.
            It can not be the TablixGroup.
        '''
        self.hierarchy = hierarchy
        self.report = report
        self.definition = definition
        self.members = []
        self.parent_member = parent_member
        self.children = []
        self.fixed_data = report.get_value(
            definition, 'FixedData', False)
        self.hide_if_no_rows = report.get_value(
            definition, 'HideIfNoRows', False)
        self.repeat_on_new_page = report.get_value(
            definition, 'RepeatOnNewPage', False)
        self.group = None
        self.scope = None
        self.is_static = True
        self.group_belongs = None
        self.header = TablixMember.Header(self)
        self.data_element_name = report.get_value(
            definition, 'DataElementName', None)
        self.data_element_output = report.get_value(
            definition, 'DataElementOutput', 'Auto')
        self.def_object = None  # Row or Column definition.        

        if definition:
            header_def = definition.get_element('TablixHeader')
            if header_def:
                self.header.set_header(header_def)                
            group_def = definition.get_element('Group')
            if group_def:
                self.group = DataGroupObject(
                    report, group_def.Name, parent_data_group,
                    location=hierarchy.type)
                self.group.create_instances(group_def)

        if self.group:
            self.group_belongs = self.group
            self.scope = self.group.name
            self.is_static = False
        else:
            if parent_data_group:
                self.scope = parent_data_group.name
            self.group_belongs = group_belongs

        if parent_member:
            parent_member.children.append(self)

        if self.data_element_name is None:
            if self.is_static:
                if self.header.textbox_name:
                    self.data_element_name = self.header.textbox_name
                else:
                    self.data_element_name = 'StaticMember'
            else:
                self.data_element_name = \
                    self.group.name + '_Collection' 

        if definition:
            members_def = definition.get_element('TablixMembers')
            data_group_to_parent = \
                self.group if self.group else parent_data_group
            if members_def:
                header_size = 0.0
                for member in members_def.member_list:
                    new_member = TablixMember(
                        hierarchy, report, member,
                        self, data_group_to_parent,
                        self.group_belongs)
                    self.members.append(new_member)
                    if header_size == 0.0:
                        header_size = new_member.header.get_total_size()
                    else:
                        if new_member.header.get_total_size() != header_size:
                            err = 'Peers members header size ' \
                                'must be equal.'
                            LOGGER.error(err, True)

    def get_parent_group(self, tablix):
        if not self.group_belongs:
            return
        names = [tablix.name, self.group_belongs.top_group.name]
        if self.group_belongs.parent.name not in names:
            return self.group_belongs.parent

    def set_definition(self, type_, row_column_def, index):
        if type_ == 'Rows':
            self.def_object = TablixMember.Row(
                self, row_column_def, index)
        else:
            self.def_object = TablixMember.Column(
                self, row_column_def, index)
        self.hierarchy.rows_columns.append(self.def_object)


class Grid(object):
    '''
    Thought as a spreadsheet,
    zero to one cell per row/column coordinate.
    If one group expands then row/column of grid increases
    in number and others cells may span.
    '''

    class Column(object):
        def __init__(self, index, member, instance):
            self.width = 0.0
            self.index = index
            self.cells = []
            self.member = member
            self.instance = instance

    class Row(object):
        class Cell(object):
            def __init__(
                    self, grow_direction, row, column, cell_object,
                    row_instance, col_instance):
                self.type = 'RowCell'
                self.object = cell_object
                self.row = row
                self.column = column
                self.row_instance = row_instance
                self.col_instance = col_instance
                self.row_span = 0
                self.col_span = 0
                self._grow_direction = grow_direction
                self._auto_span_count = 0
                self._parent_cell = None
                self._children_cells = []

                self.top = 0.0
                self.left = 0.0
                self.height = 0.0
                # Given according to column(s) width
                self.width = 0.0

            def set_parent(self, parent, columns, column):
                if not parent:
                    return
                self._parent_cell = parent
                self._parent_cell._children_cells.append(self)
                parent._auto_span(columns, column)

            def set_new_height(self, height):
                pass

            def _auto_span(self, columns, column):
                self._auto_span_count += 1
                if self._grow_direction == "row":
                    column = columns[column.index - 1]
                    self.row_span = self._auto_span_2(
                        self.row_span, columns, column)
                    if self.row_span > 1:
                        column.cells[self.row.index + (
                            self.row_span - 1)] = self
                else:
                    self.col_span = self._auto_span_2(
                        self.col_span, columns, column)
                    if self.col_span > 1:
                        column.cells[self.row.index] = self

            def _auto_span_2(self, unit_to_span, columns, column):
                result = unit_to_span
                if self._auto_span_count > unit_to_span:
                    result = self._auto_span_count
                    if self._parent_cell:
                        self._parent_cell._auto_span(columns, column)
                return result

        def __init__(
                self, index, member, instance):
            self.height = 0.0
            self.index = index
            self.cells = []
            self.member = member
            self.instance = instance

        def add_cell(
                self, grow_direction,
                cell_object, column,
                row_instance, col_instance):
            cell = Grid.Row.Cell(
                grow_direction, self, column, cell_object,
                row_instance, col_instance)
            self.cells.append(cell)
            return cell

    def __init__(self, grow_direction='row'):
        self._grow_direction = grow_direction
        self.columns = []
        self.rows = []
        self.height = 0.0
        self.width = 0.0

    def add_cell(
            self, row_index, column_index,
            cell_object=None, row_span=1, col_span=1,
            parent_cell=None, row_member=None, col_member=None,
            row_instance=None, col_instance=None):

        row, new_row = self._get_item(
            row_index, self.rows, Grid.Row,
            row_member, row_instance)
        column, new_column = self._get_item(
            column_index, self.columns, Grid.Column,
            col_member, col_instance)

        cell = row.add_cell(
            self._grow_direction, cell_object,
            column, row_instance, col_instance)

        if new_row:
            for col in self.columns:
                col.cells.append(None)
            # Remove last None of current column
            column.cells.pop()
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
        if direction == 'right':
            if len(self.rows) != len(grid.rows):
                err_msg = 'To extend Grid to the right, ' \
                    'both rows length must be equal.'
                LOGGER.error(err_msg, True)
            i = 0
            for row in grid.rows:
                self.rows[i].cells.extend(row.cells)
                i += 1
            self.columns.extend(grid.columns)

        else:  # Down
            if len(self.columns) != len(grid.columns):
                LOGGER.error(
                    'To extend Grid down, both columns length must be equal.',
                    True)
            i = 0
            for column in grid.columns:
                self.columns[i].cells.extend(column.cells)
                i += 1
            self.rows.extend(grid.rows)

    def _get_item(
            self, index, collection, class_,
            member, instance):
        new = False
        if index == len(collection):
            item = class_(
                index, member, instance)
            collection.append(item)
            new = True
        elif index > len(collection):
            LOGGER.error(
                'Grid must increase by one Row/Column.', True)
        else:
            item = collection[index]
        return item, new


class TablixCorner(Grid):
    def __init__(
            self, report, corner_def,
            column_hierarchy, row_hierarchy):
        super(TablixCorner, self).__init__()
        self.report = report
        row_index = 0
        for row in corner_def.TablixCornerRows.row_list:
            if not row.cell_list:
                continue
            for cell_def in row.cell_list:
                col_index = 0
                cell = self._do_cell(
                    cell_def, row_index, col_index,
                    column_hierarchy.cumulative_sizes[row_index],
                    row_hierarchy.cumulative_sizes[col_index])
                if cell.col_span > 1:
                    col_index += cell.col_span
                else:
                    col_index += 1
            row_index += 1

    def _do_cell(
            self, cell_def, row_index, col_index,
            height, width):
        cell = TablixCell(self.report, cell_def, 0.0)
        grid_cell = self.add_cell(
            row_index, col_index, cell,
            col_span=cell.col_span,
            row_span=cell.row_span)
        grid_cell.width = width
        grid_cell.height = height
        item_info = grid_cell.object.get_items(grid_cell)
        grid_cell.object = item_info
        return cell
