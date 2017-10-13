# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from importlib import import_module
from . expression import Expression
from . functions import *
from .. import LOGGER


class _Aggregate(object):
    class _AggregateInfo(object):
        def __init__(self, report, expression, scope):
            self.expression = None
            self.current_group = {'Column': None, 'Row': None}
            self.current_scope = {'Column': None, 'Row': None}

            if expression is not None:
                self.expression = Expression(
                    '=' + expression, None, False)

            self.current_scope['Row'] = \
                report.current_data_scope[0]
            self.current_scope['Column'] = \
                report.current_data_scope[1]

            if scope:
                self.current_group['Row'] = report.data_groups[scope]
            else:
                # Current running row group
                self.current_group['Row'] = report.data_groups[
                        self.current_scope['Row']
                    ]

            self.current_group['Column'] = report.data_groups[
                    self.current_scope['Column']
                ]

    class _AggregateCache(object):
        def __init__(self):
            # Cache result of Aggregates with scope.
            self._values = {}

        def get_value(self, function, row_scope, col_scope, expression):
            if function not in self._values:
                return
            scope_str = self._get_scope_str(row_scope)
            scope_str += '||' + self._get_scope_str(col_scope)
            if scope_str not in self._values[function]:
                return
            if expression not in self._values[function][scope_str]:
                return
            return self._values[function][scope_str][expression]

        def set_value(
                self, function, row_scope, col_scope,
                expression, value):
            if function not in self._values:
                self._values[function] = {}
            scope_str = self._get_scope_str(row_scope)
            scope_str += '||' + self._get_scope_str(col_scope)
            if scope_str not in self._values[function]:
                self._values[function][scope_str] = {}
            if expression not in self._values[function][scope_str]:
                self._values[function][scope_str][expression] = None
            self._values[function][scope_str][expression] = value

        def _get_scope_str(self, scope):
            if scope is None:
                return 'None'
            return scope

    def __init__(self, report):
        self.report = report
        self._cache = _Aggregate._AggregateCache()

    def Aggregate(self, expression, scope=None):
        '''
        Returns a list of grouped values according to expression and scope.
        '''
        return self._get_value(
            'Aggregate', expression, scope, [[], None])

    def Max(self, expression, scope=None):
        return self._get_value(
            'Max', expression, scope, [0.0, None])

    def Min(self, expression, scope=None):
        return self._get_value(
            'Min', expression, scope, [0.0, None])

    def Count(self, expression, scope=None):
        return self._get_value(
            'Count', expression, scope, [0, None])

    def CountDistinct(self, expression, scope=None):
        return self._get_value(
            'CountDistinct', expression, scope, [{}, None])

    def CountRows(self, scope=None):
        return self._get_value(
            'CountRows', None, scope, [0, None])

    def First(self, expression, scope=None):
        return self._get_value(
            'First', expression, scope, [None, None])

    def Last(self, expression, scope=None):
        return self._get_value(
            'Last', expression, scope, [None, None])

    def Previous(self, expression, scope=None):
        return self._get_value(
            'Previous', expression, scope, [None, None])

    def Avg(self, expression, scope=None):
        return self._get_value(
            'Avg', expression, scope, [0.0, 0])

    def Sum(self, expression, scope=None):
        return self._get_value(
            'Sum', expression, scope, [None, None])

    def StDev(self, expression, scope=None):
        return self._get_value(
            'StDev', expression, scope, [0.0, None])

    def StDevP(self, expression, scope=None):
        return self._get_value(
            'StDevP', expression, scope, [0.0, None])

    def Var(self, expression, scope=None):
        return self._get_value(
            'Var', expression, scope, [0.0, None])

    def VarP(self, expression, scope=None):
        return self._get_value(
            'VarP', expression, scope, [0.0, None])

    def RunningValue(self, expression, function, scope=None):
        return self._running_value(
            expression, function, scope)

    def RowNumber(self, scope=None):
        return self._running_value(
            None, 'RowNumber', scope)

    def _running_value(self, expression, function, scope):
        if function != 'RowNumber':
            valid_fun = ['Sum', 'Avg', 'CountDistinct']
            if function not in valid_fun:
                err_msg = "Invalid function '{0}' for aggregate " \
                    "RunningValue. Valid are: {1}"
                LOGGER.error(err_msg.format(function, valid_fun), True)

        name = 'RunningValue.' + function

        result = None
        # Group name for Running calculation.
        scope_name = None
        # Current instance of scope_name group.
        instance_group = None
        # Group from where Running function is called.
        location_group = {'Row': None, 'Column': None}
        location_instance = {'Row': None, 'Column': None}
        # Current data name and row index if location_group is a detail group.
        current_row = {'DataName': None, 'Index': None}
        # Last data name and row index if location_group is a detail group.
        last_row = {'DataName': None, 'Index': None}

        aggr = _Aggregate._AggregateInfo(self.report, expression, scope)

        if scope is None:
            # Top group (DataSet)
            scope_name = aggr.current_group['Row'].top_group.name
            aggr = _Aggregate._AggregateInfo(
                self.report, expression, scope_name)
        else:
            scope_name = scope

        instance_group = \
            self.report.data_groups[scope_name].current_instance()
        location_group['Row'] = \
            self.report.data_groups[aggr.current_scope['Row']]
        location_group['Column'] = \
            self.report.data_groups[aggr.current_scope['Column']]

        location_instance['Row'] = \
            location_group['Row'].current_instance()
        location_instance['Column'] = \
            location_group['Column'].current_instance()

        location_type = self.report.data_groups[scope_name].location
        if location_type:
            location_type = location_type[:len(location_type) - 1]
        else:
            location_type = 'Row'

        current_row['DataName'] = \
            location_instance[location_type].data.name

        if location_group[location_type].is_detail_group:
            current_row['Index'] = \
                location_instance[location_type].data._current_index

        value_cache = self._cache.get_value(
            name,
            scope_name + "." + location_group['Row'].name,
            scope_name + "." + location_group['Column'].name,
            expression
        )

        if value_cache:
            if value_cache[0] == instance_group.data.name:
                last_row = value_cache[1]
                result = [value_cache[2], value_cache[3]]
                if last_row['DataName'] is not None:
                    if last_row['DataName'] != current_row['DataName']:
                        # Reset if detail group instance changed.
                        last_row['Index'] = None

        if function == 'RowNumber':
            if result is None:
                result = [0, 0]
            if location_group[location_type].is_detail_group:
                if last_row['Index'] != current_row['Index']:
                    result[0] += 1
            else:
                if last_row['DataName'] != current_row['DataName']:
                    lg = location_group[location_type]
                    result[0] += \
                        lg.current_instance().data.row_count()
        else:
            if location_group[location_type].is_detail_group:
                if last_row['Index'] != current_row['Index']:
                    val = aggr.expression.value(self.report)
                    if val is not None:
                        if function == 'Count':
                            if result is None:
                                result = [0, None]
                            result[0] += 1
                        elif function == 'CountDistinct':
                            if result is None:
                                result = [{}, None]
                            if val not in result[0]:
                                result[0][val] = None
                        else:
                            if result is None:
                                result = [0, 0]
                            result[0] += val
                            if function == 'Avg':
                                result[1] += 1
            else:
                if result is None:
                    if function == 'CountDistinct':
                        result = [{}, None]
                    else:
                        result = [0, 0]
                if last_row['DataName'] != current_row['DataName']:
                    result = self._instance_value(
                        function, aggr.expression,
                        location_group['Row'].current_instance().data,
                        None,  # TODO col_data
                        result[0], result[1])

        self._cache.set_value(
            name,
            scope_name + '.' + location_group['Row'].name,
            scope_name + '.' + location_group['Column'].name,
            expression,
            [
                instance_group.data.name,
                current_row,
                result[0],
                result[1]
            ]
        )

        return self._get_function_result(function, result)

    def _get_value(self, function, expression, scope, value):
        aggr = _Aggregate._AggregateInfo(self.report, expression, scope)
        result = [value[0], value[1]]

        row_instance_data = \
            aggr.current_group['Row'].current_instance().data
        col_instance_data = \
            aggr.current_group['Column'].current_instance().data

        value_cache = self._cache.get_value(
            function,
            row_instance_data.name,
            col_instance_data.name,
            expression)
        if value_cache:
            return self._get_function_result(
                function, value_cache)

        result = self._instance_value(
            function, aggr.expression,
            row_instance_data,
            col_instance_data,
            result[0], result[1])

        self._cache.set_value(
            function,
            row_instance_data.name,
            col_instance_data.name,
            expression,
            result)

        return self._get_function_result(function, result)

    def _get_function_result(self, function, result):
        if function == 'Avg':
            if result[1] > 0:
                return result[0] / result[1]
            else:
                return 0
        elif function == 'CountDistinct':
            if result[0] is None:
                return 0
            return len(result[0])
        return result[0]

    def _instance_value(
            self, function, expression,
            row_data, col_data,
            result1_start, result2_start):

        result1 = result1_start
        result2 = result2_start
        remember = row_data._current_index

        if function == 'CountRows':
            result1 += row_data.row_count
            return [result1, None]

        row_data.move_first()
        while not row_data.EOF:
            val = expression.value(self.report)
            if val is not None:
                if not self._in_column_scope(
                        row_data.get_current_row(), col_data):
                    row_data.move_next()
                    continue
                if function == 'First':
                    result1 = val
                    break
                if result1 is None:
                    result1 = 0
                if function == 'Last':
                    result1 = val
                elif function == 'Sum':
                    result1 += val
                elif function == 'Avg':
                    result1 += val
                    result2 += 1
                elif function == 'Count':
                    result1 += 1
                elif function == 'CountDistinct':
                    if val not in result1:
                        result1[val] = None
                elif function == 'Max':
                    if val > result1:
                        result1 = val
                elif function == 'Min':
                    if val < result1:
                        result1 = val
            if function == 'Aggregate':
                result1.append(val)
            row_data.move_next()
        row_data.move(remember)
        return [result1, result2]

    def _in_column_scope(self, row, column_data):
        if not column_data:
            return True
        row_id = row[len(row) - 1]
        return column_data.has_row_id(row_id)


class ExpressionEval(object):
    def __init__(self, report):
        self.report = report
        self._context = {}
        self._loaded = False
        self._aggregate = _Aggregate(report)

    def load_modules(self, modules_def):
        if not modules_def:
            return
        for module in modules_def.modules:
            self._add_context(
                self.report.get_value(module, 'From', None),
                self.report.get_value(module, 'Import', None),
                self.report.get_value(module, 'As', None)
            )

    def _add_context(self, from_name, import_name, alias):
        if alias is None:
            alias = import_name
        if alias in self._context:
            err_msg = "'{0}' already exists in the " \
                "expression evaluation context."
            LOGGER.error(err_msg.format(alias), True)
        mod_object = None
        if from_name:
            module = import_module(from_name)
            mod_object = getattr(module, import_name)
        else:
            mod_object = import_module(import_name)
        self._context[alias] = mod_object

    def resolve_expression(self, expression):
        if not self._loaded:
            for key, value in self._context.items():
                setattr(self, key, value)
            self._loaded = True

        Modules = M = self

        Aggregate = self._aggregate.Aggregate
        Avg = self._aggregate.Avg
        Count = self._aggregate.Count
        CountDistinct = self._aggregate.CountDistinct
        CountRows = self._aggregate.CountRows
        First = self._aggregate.First
        Last = self._aggregate.Last
        Max = self._aggregate.Max
        Min = self._aggregate.Min
        Previous = self._aggregate.Previous
        RowNumber = self._aggregate.RowNumber
        RunningValue = self._aggregate.RunningValue
        Sum = self._aggregate.Sum
        StDev = self._aggregate.StDev
        StDevP = self._aggregate.StDevP
        Var = self._aggregate.Var
        VarP = self._aggregate.VarP

        exp_error = "Error evaluating expression: '{0}'".format(expression)

        try:
            if self.report:
                # Collections and aliases
                Parameters = P = self.report.parameters
                Globals = G = self.report.globals
                # TODO ReportItems

                if self.report.current_data_scope[0]:  # Always in Row
                    Fields = F = self.report.data_groups[
                            self.report.current_data_scope[0]
                        ].current_instance().data.fields
                elif self.report.current_data_interface:
                    Fields = F = self.report.data_interfaces[
                        self.report.current_data_interface].fields

            result = eval(expression)

        except KeyError as e:
            LOGGER.error(
                "{0}. Key <{1}> does not exist in dictionary.".format(
                    exp_error, self._get_error_str(e)),
                True, "ValueError")
        except Exception as e:
            LOGGER.error(
                "{0}. Unexpected error: '{1}'".format(
                    exp_error, self._get_error_str(e)), True)
        return result

    def _get_error_str(self, e):
        res = None
        if not e:
            return ''
        for message in e.args:
            if not message:
                continue
            if not res:
                res = message
            else:
                res = "{0} - {1}".format(res, message)
        return res
