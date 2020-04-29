# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
from . data_type import DataType
from . dataprovider import get_data_provider
from .. import LOGGER
from .. collection import Collection, CollectionItem
from .. definition.expression import Expression


class Field(CollectionItem):
    def __init__(
            self, index, parent, name,
            data_field, field_value, data_type):
        super(Field, self).__init__(name)

        if (not data_field and not field_value) or \
                (data_field and field_value):
            LOGGER.error(
                "'Field' must be type of 'DataField' or 'Value'.", True)

        self.data_field = data_field
        self.field_value = field_value
        self._parent = parent
        self._index = index
        self._data_type = data_type
        self.is_missing = True
        self.is_expression = False
        if field_value:
            self.expression = Expression(field_value, None, False)
            self.is_expression = True

    def get_value(self):
        if self.data_field and self.is_missing:
            return
        result = None

        data = self._parent.current_data
        row = data.get_current_row()
        if self.is_expression:
            result = self.expression.value(self._parent.report)
        else:
            result = row[self._index]
        return DataType.get_value(self._data_type, result)


class Fields(Collection):
    '''
    Fields collection. One instance per DataSet.
    Instance must be shared with descendants data interfaces.
    '''
    def __init__(self, report):
        super(Fields, self).__init__()
        self.report = report
        self._field_index = 0
        self.current_data = None

    def set_current_data(self, data):
        self.current_data = data

    def add_field(self, name, data_field, field_value, data_type):
        field = Field(self._field_index, self,
                name, data_field, field_value, data_type)
        super(Fields, self).add_item(field)
        self._field_index += 1

    def __call__(self, name, function):
        res = super(Fields, self).__call__(name, function)
        if res:
            return res

        item = self._items_dict[name]

        if function == 'DataField':
            return item.data_field
        if function == 'IsMissing':
            return item.is_missing
        if function == 'DataType':
            return item._data_type
        LOGGER.error(
            "Invalid property '{0}' for {1} collection item.".format(
                name, item.__class__.__name__), True)

    def __setitem__(self, key, value):
        LOGGER.error(
            "Item '{0}' in Collection '{1}' is read only.".format(
                name, self.__class__.__name__), True)


class FieldsDataInterface:
    def __init__(self, parent):
        self.parent = parent
        self.fields = None
        self.count = 0

    def add_field(self, name, data_field=None,
                field_value=None, data_type=None):
        'Must be call only for DataSet'
        if not self.fields:
            self.fields = Fields(self.parent.report)
        self.fields.add_field(
            name, data_field, field_value, data_type)

    def __getattr__(self, name):
        self.fields.set_current_data(self.parent)
        return getattr(self.fields, name)

    def __call__(self, name, function):
        self.fields.set_current_data(self.parent)
        return self.fields.__call__(name, function)

    def __getitem__(self, key):
        self.fields.set_current_data(self.parent)
        return self.fields[key]

    def __setitem__(self, key, value):
        self.fields.set_current_data(self.parent)
        self.fields[key] = value


class DataInterface:
    def __init__(self, report, name):
        self.report = report
        self.name = name
        self.original_rows = []  # Not Filtered nor sorted
        self.rows = []           # Filtered and sorted
        self.EOF = True
        self._current_index = -1
        self.fields = FieldsDataInterface(self)
        self._row_id_manager = {}

        if report:
            if name in report.data_interfaces:
                LOGGER.error(
                    "'{0}' '{1}' already exists.".format(
                        self.__class__.__name__, name))
            report.data_interfaces[name] = self

    def add_field(self, name, data_field=None,
                    field_value=None, data_type=None):
        self.fields.add_field(
            name, data_field, field_value, data_type)

    def get_field_list(self):
        return self.fields.fields._items

    def add_row(self, row):
        self.original_rows.append(row)
        self.rows.append(row)
        self._manage_row_id(row)
        if self.row_count() == 1:
            self.move_first()

    def row_number(self):
        return self._current_index + 1

    def row_count(self):
        return len(self.rows)

    def move_first(self):
        self.move(0)

    def move_next(self):
        self.move(self._current_index + 1)

    def move_last(self):
        self.move(self.row_count() - 1)

    def move(self, i):
        if i < 0 or i >= self.row_count():
            self.set_eof()
            return
        if self.report:
            self.report.current_data_interface = self.name
        self.EOF = False
        self._current_index = i

    def set_eof(self):
        self.EOF = True
        self._current_index = -1
        if self.report:
            self.report.current_data_interface = None

    def get_current_row(self):
        return self.rows[self._current_index]

    def copy(self):
        result = DataInterface(self.report, 'data_copy_' + self.name)
        result.fields.fields = self.fields.fields
        for r in self.rows:
            result.add_row(r)
        return result

    def has_row_id(self, row_id):
        centena = self._get_id_centena(row_id)
        if centena not in self._row_id_manager:
            return
        if row_id in self._row_id_manager[centena]:
            return True

    def _manage_row_id(self, row):
        row_id = row[len(row) - 1]
        centena = self._get_id_centena(row_id)
        if centena not in self._row_id_manager:
            self._row_id_manager[centena] = []
        self._row_id_manager[centena].append(row_id)

    def _get_id_centena(self, row_id):
        i = 0
        limit = 500
        while True:
            if row_id >= i and row_id < (i + limit):
                return i
            i += limit


class DataSource:
    def __init__(self, name, data_provider):
        self.name = name
        self.data_provider = data_provider
        self.cursor = None

    def connect(self, connection_object):
        self.cursor = None
        if not self.data_provider:
            LOGGER.error(
                    "Invalid DataProvider '{0}' for DataSource '{1}'".format(
                    self.data_provider, self.name))
            return False

        if connection_object is None:
            LOGGER.error(
                    "Invalid connection object for DataSource '{0}'.".format(
                    self.name))
            return False

        try:
            LOGGER.debug(
                    "Connecting Data Source '{0}'".format(self.name))
            conn = self.data_provider.connect(connection_object)
            self.cursor = conn.cursor()
        except Exception as e:
            LOGGER.error(
                    "Error while connecting to database. '{0}'".format(e.args[0]))
            return False

        return True


class DataSet(DataInterface):
    def __init__(self, report, name, data_source, field_map):
        super(DataSet, self).__init__(report, name)
        self.data_source = data_source
        for f in field_map:
            self.add_field(
                f['name'],
                f['data_field'],
                f['field_value'],
                f['data_type'])

    def execute(self, command=None, data_grid=None):
        is_api_2 = False
        if not data_grid:
            if not self.data_source or \
                    not self.data_source.cursor:
                return
            try:
                self.data_source.cursor.execute(command)
            except Exception as e:
                LOGGER.error(
                    "Error executing data set '{0}': {1}".format(
                        self.name, e.args), True)
            query_result = self.data_source.cursor.fetchall()
            if self.data_source.cursor.description:
                is_api_2 = True
                for f in self.get_field_list():
                    found = False
                    if f.is_expression:
                        continue
                    for d in self.data_source.cursor.description:
                        if d[0] == f.data_field:
                            found = True
                            break
                    if not found:
                        LOGGER.error(
                            "Field '{0}' not found in dataset '{1}'.".format(
                                f.data_field, self.name), True)
        else:
            query_result = data_grid

        row_id = 0

        for r in query_result:
            row = []
            x = 0
            for f in self.get_field_list():
                try:
                    if f.is_expression:
                        row.append(None)
                    else:
                        if is_api_2:
                            i = 0
                            for d in self.data_source.cursor.description:
                                if f.data_field == d[0]:
                                    row.append(r[i])
                                    f.is_missing = False
                                    break
                                i += 1
                        elif hasattr(r, f.name):  # An Object
                            row.append(getattr(r, f.name))
                            f.is_missing = False
                        else:  # Treat just as a list of values.
                            if x > len(r) - 1:
                                break
                            f.is_missing = False
                            row.append(r[x])
                except:
                    # TODO add more error info
                    raise Exception(
                        "Error with field '{0}'".format(
                            f.name))
                x += 1

            if len(row) == 0:
                LOGGER.error(
                    "No rows collected for DataSet '{0}'.".format(
                        self.name), True)
            row.append(row_id)
            self.add_row(row)
            row_id += 1


class DataGroupInstance(DataInterface):
    def __init__(self, data_parent, name, page_break):
        super(DataGroupInstance, self).__init__(data_parent.report, name)
        self.data_parent = data_parent
        self.page_break = page_break
        # Share Fields definition
        self.fields.fields = data_parent.fields.fields

    def _add_parent_rows(self):
        self.data_parent.move_first()
        while not self.data_parent.EOF:
            r = self.data_parent.get_current_row()
            self.add_row(r)
            self.data_parent.move_next()

    @staticmethod
    def get_groups(data, expression, sub_groups=[],
                sort_descending=None, page_break=None):

        group_list = []  # List of DataInterface objects

        if len(sub_groups) == 0:  # If first grouping
            sub_groups.append([data.name, data])

        for data_group in sub_groups:
            groups_exp = {}
            group_exp_list = []
            dt = data_group[1]
            dt.move_first()
            while not dt.EOF:
                r = dt.get_current_row()

                exp_key = Expression.get_value_or_default(
                            dt.report, None, None, None,
                            direct_expression=expression
                        )

                if exp_key not in groups_exp:
                    groups_exp[exp_key] = DataGroupInstance(
                        dt, "{0}-{1}".format(dt.name, exp_key), page_break)
                    group_exp_list.append([exp_key, groups_exp[exp_key]])
                groups_exp[exp_key].add_row(r)
                dt.move_next()
            if sort_descending is not None:
                group_exp_list = sorted(
                    group_exp_list,
                    key=lambda z: (z[0] is None, z[0]),
                    reverse=sort_descending)
            group_list.extend(group_exp_list)

        return group_list


class DataSourceObject(DataSource):
    def __init__(self, report, data_source_def):
        self.report = report
        dp_name = Expression.get_value_or_default(
                self.report, data_source_def.conn_properties,
                'DataProvider', None)
        LOGGER.debug(
            "Looking for Data Provider '{0}'".format(dp_name))
        data_provider = get_data_provider(dp_name)
        super(DataSourceObject, self).__init__(
            data_source_def.Name, data_provider)
        self.conn_object = Expression.get_value_or_default(
                self.report, data_source_def.conn_properties,
                'ConnectObject', None)

    def connect(self):
        return super(DataSourceObject, self).connect(self.conn_object)


class DataSetObject(DataSet):
    def __init__(self, report, data_set_def):
        self.report = report
        self.data_set_def = data_set_def

        data_source_name = self.data_set_def.query_def.DataSourceName
        if data_source_name not in self.report.data_sources:
            LOGGER.error(
                "Data source '{0}' not defined in report.".format(
                    data_source_name), True)
        data_source = self.report.data_sources[data_source_name]

        field_map = []
        for field in data_set_def.fields:
            val = field.get_element('Value')
            if val:
                val = val.expression
            field_map.append({
                    'name': field.Name,
                    'data_field': Expression.get_value_or_default(
                        report, field, 'DataField', None),
                    'field_value': val,
                    'data_type': Expression.get_value_or_default(
                        report, field, 'DataType', None)
                })

        super(DataSetObject, self).__init__(
            report, data_set_def.Name, data_source, field_map)

    def execute(self):  # TODO Query parameters
        if self.data_source and self.data_source.cursor:
            command_text = self.data_set_def.query_def.get_command_text(
                self.report)
            super(DataSetObject, self).execute(
                command_text)
        else:
            # Connection failed, try to load data appended to report
            LOGGER.info("Trying to load embedded data for data set '{0}'".format(self.name))
            if not self.report.definition.data:
                err_msg = "DataSource connection failed and " \
                    "no data embedded in defintion file for DataSet: '{0}'."
                LOGGER.critical(err_msg.format(self.name), True)
            self.report.definition.data.load(self.report)
            data = self.report.definition.data.get_data(
                self.data_set_def.Name)
            super(DataSetObject, self).execute(data_grid=data)

        # Filter data
        if self.data_set_def.filters_def:
            flt = FiltersObject(self.report, self.data_set_def.filters_def)
            flt.filter_data(self)

        # Sort data
        if self.data_set_def.sort_def:
            srt = SortingObject(self.report, self.data_set_def.sort_def)
            srt.sort_data(self)

        dg = DataGroupObject(self.report, self.name, None)
        dg.add_data_instance(self)


class FiltersObject:
    class _FilterObject:
        def __init__(self, filter_def):
            self.filter_values = []
            self.filter_expression = filter_def.get_element(
                'FilterExpression')
            self.operator = filter_def.get_element(
                'Operator')
            filter_values_def = filter_def.get_element(
                'FilterValues')
            if filter_values_def:
                for v in filter_values_def.expression_list:
                    self.filter_values.append(v)

    def __init__(self, report, filter_def):
        self.report = report
        self.filter_def = filter_def
        self.filter_list = []
        if filter_def:
            for flt in filter_def.filter_list:
                self.filter_list.append(
                    FiltersObject._FilterObject(flt))

    def filter_data(self, data):
        if len(self.filter_list) == 0 or \
                len(data.rows) == 0:  # Nothing to filter
            return
        for flt in self.filter_list:
            data.rows = self._do_filter(flt, data)

    def _do_filter(self, flt, data):
        rows = []
        data.move_first()
        while not data.EOF:
            val = Expression.get_value_or_default(
                self.report, None, None, None,
                direct_expression=flt.filter_expression)
            operator = Expression.get_value_or_default(
                self.report, None, None, None,
                direct_expression=flt.operator)
            if operator is None:
                raise_error_with_log(
                    "No Operator for Filter in Data '{0}'".format(data.name))
            row = self._filter_row(
                data.name, flt.filter_values,
                data.get_current_row(), val, operator)
            if row:
                rows.append(row)
            data.move_next()
        return rows

    def _filter_row(self, name, filter_values, current_row, val, operator):
        filtered = False
        vals = []

        for v in filter_values:
            vals.append(Expression.get_value_or_default(
                self.report, None, None, None, direct_expression=v))

        if len(vals) == 0:
            raise_error_with_log(
                "No filter values defined for '{0}'".format(name))

        if operator not in ('In', 'Between'):
            if len(vals) > 1:
                err_msg = "Operator '{0}' only accepts one filter value. "
                err_msg += "Data name: '{1}'"
                raise_error_with_log(err_msg.format(operator, name))
            if operator == 'Equal':
                if val == vals[0]:
                    filtered = True
            if operator == 'NotEqual':
                if val != vals[0]:
                    filtered = True
            if operator == 'GreaterThan':
                if val > vals[0]:
                    filtered = True
            if operator == 'GreaterThanOrEqual':
                if val >= vals[0]:
                    filtered = True
            if operator == 'LessThan':
                if val < vals[0]:
                    filtered = True
            if operator == 'LessThanOrEqual':
                if val <= vals[0]:
                    filtered = True
            if operator in (
                    'Like', 'TopN', 'BottomN', 'TopPercent', 'BottomPercent'):
                raise_error_with_log(
                    "Operator '{0}' is not supported at this moment.".format(
                        operator))
        else:
            if operator == 'Between':
                if len(vals) > 2:
                    err_msg = "Operator '{0}' takes exactly 2 " \
                        "filter values. Data name: '{1}'"
                    raise_error_with_log(err_msg.format(operator, name))
                if val >= vals[0] and val <= vals[1]:
                    filtered = True
            if operator == 'In':
                if val in vals:
                    filtered = True

        if filtered:
            return current_row


class SortingObject:
    class _SortByObject:
        def __init__(self, sortby_def, report):
            self.sort_expression = None
            self.direction = 'Ascending'
            if sortby_def:
                self.sort_value = sortby_def.get_element('Value')
                self.direction = report.get_value(
                    sortby_def, 'SortDirection', 'Ascending')

    def __init__(self, report, sorting_def):
        self.report = report
        self.sortby_list = []
        for srt in sorting_def.sortby_list:
            self.sortby_list.append(
                SortingObject._SortByObject(srt, report))

    def sort_data(self, data):
        if len(self.sortby_list) == 0:
            return

        groups = []
        i = 0
        for sortby in self.sortby_list:
            reverse = False if sortby.direction == 'Ascending' else True
            if i == 0:
                groups = DataGroupInstance.get_groups(
                    data, sortby.sort_value, sub_groups=[])
                groups = sorted(
                    groups, key=lambda z: z[0], reverse=reverse)
            else:
                # Sort is made in get_groups function.
                groups = DataGroupInstance.get_groups(
                        data, sortby.sort_value,
                        sub_groups=groups,
                        sort_descending=reverse)
            i += 1

        if len(groups) == 0:
            return

        data.rows = []
        for g in groups:
            for r in g[1].rows:
                data.rows.append(r)
            # Delete from global collection
            del data.report.data_interfaces[g[1].name]


class DataGroupObject:
    class GroupInstance:
        def __init__(self, group, data):
            self.group = group
            self.data = data
            self.sub_instance = []

        def add_sub_instance(self, instance):
            self.sub_instance.append(instance)

    def __init__(self, report, name, parent, location=None):
        self.name = name
        self.report = report
        self.instances = []     # List of GroupInstance objects.
        self.top_group = None   # Top group. Normally the data set.
        self.parent = parent    # Parent group. 'None' for Dataset.
        self.sub_group = []     # List of DataGroupObject defining sub groups.
        self.is_detail_group = False
        self._current_instance_index = -1
        self.EOF = True
        self.location = location
        self.data_element_name = name
        self.data_element_output = 'Auto'

        if name in report.data_groups:
            err_msg = "DataSet, DataRegion or Group with " \
                "name '{0}' already exists."
            LOGGER.error(err_msg.format(name), True)
        report.data_groups[name] = self
        if not parent:
            self.top_group = self
        else:
            self.top_group = parent.top_group
            if parent.location:
                self.location = parent.location

    def create_instances(self, group_def):
        if not group_def:
            return

        self.data_element_name = self.report.get_value(
                group_def, 'DataElementName', self.name)
        self.data_element_output = self.report.get_value(
                group_def, 'DataElementOutput', 'Auto')

        if self.parent and self.parent.is_detail_group:
            err_msg = "Group '{0}' could not be created. " \
                "Parent group '{1}' is a detail group."
            LOGGER.error(err_msg.format(
                    group_def.Name, self.parent.name), True)

        exp_def = group_def.get_element('GroupExpressions')
        filter_def = group_def.get_element('Filters')
        sort_def = group_def.get_element('SortExpressions')
        flt = None
        srt = None
        if filter_def:
            flt = FiltersObject(self.report, filter_def)
        if sort_def:
            srt = SortingObject(self.report, sort_def)
        class_name = group_def.__class__.__name__
        for parent_instance in self.parent.instances:
            groups = []
            data = self._get_filtered_and_sorted(parent_instance.data, flt, srt)
            if class_name == 'Group' and not exp_def:
                groups.append([None, self._create_one_group(data)])
                self.is_detail_group = True
            elif exp_def:
                if len(exp_def.expression_list) == 0:
                    groups.append([None, self._create_one_group(data)])
                    self.is_detail_group = True
                else:
                    for exp in exp_def.expression_list:
                        groups = DataGroupInstance.get_groups(data, exp, groups)
            else:
                groups.append([None, self._create_one_group(data)])

            if data != parent_instance.data:
                del self.report.data_interfaces[data.name]

            for g in groups:
                self._modify_name(g[1])
                instance = self.add_data_instance(g[1])
                parent_instance.add_sub_instance(instance)

        self.parent.sub_group.append(self)

    def add_data_instance(self, data):
        instance = DataGroupObject.GroupInstance(self, data)
        self.instances.append(instance)
        return instance

    def current_instance(self):
        return self.instances[self._current_instance_index]

    def move_first(self):
        self.move(0)

    def move_next(self):
        self.move(self._current_instance_index + 1)

    def move(self, index):
        self.EOF = True
        self._current_instance_index = -1
        if not self.instances or index > len(self.instances) - 1:
            return
        self.EOF = False
        self._current_instance_index = index

    def _get_filtered_and_sorted(self, data, flt, srt):
        if not flt and not srt:
            return data
        result = data.copy()
        if flt:
            flt.filter_data(result)
        if srt:
            srt.sort_data(result)
        return result

    def _modify_name(self, data):
        name = data.name
        check = ''
        while name.startswith('data_copy_'):
            check += 'data_copy_'
            name = name[10:]
        if check:
            del self.report.data_interfaces[check + name]
            self.report.data_interfaces[name] = data
        data.name = name

    def _create_one_group(self, data):
        name = "{0}_{1}".format(data.name, self.name)
        one_grp = DataGroupInstance(data, name, None)
        one_grp._add_parent_rows()
        return one_grp
