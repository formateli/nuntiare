# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from importlib import import_module
from . expression import Expression
from . functions import *
from .. import LOGGER


class _Aggregate(object):
    class _AggregateCache(object):
        def __init__(self):
            self._values = {}  # Cache result of Aggregates with scope.

        def get_value(self, function, scope, expression):
            if function not in self._values:
                return
            if scope not in self._values[function]:
                return
            if expression not in self._values[function][scope]:
                return
            return self._values[function][scope][expression]

        def set_value(self, function, scope, expression, value):
            if function not in self._values:
                self._values[function] = {}
            if scope not in self._values[function]:
                self._values[function][scope] = {}
            if expression not in self._values[function][scope]:
                self._values[function][scope][expression] = None
            self._values[function][scope][expression] = value

    def __init__(self, report):
        self.report = report
        self._cache = _Aggregate._AggregateCache()

    def Aggregate(self, expression, scope=None):
        '''
        Returns a list of grouped values according to expression and scope.
        '''
        return self._get_value(
            "Aggregate", expression, scope, [[], None])

    def Max(self, expression, scope=None):
        return self._get_value(
            "Max", expression, scope, [0.0, None])

    def Min(self, expression, scope=None):
        return self._get_value(
            "Min", expression, scope, [0.0, None])

    def Count(self, expression, scope=None):
        return self._get_value(
            "Count", expression, scope, [0, None])

    def CountDistinct(self, expression, scope=None):
        return self._get_value(
            "CountDistinct", expression, scope, [{}, None])

    def CountRows(self, scope=None):
        return self._get_value(
            "CountRows", None, scope, [0, None])

    def First(self, expression, scope=None):
        return self._get_value(
            "First", expression, scope, [None, None])

    def Last(self, expression, scope=None):
        return self._get_value(
            "Last", expression, scope, [None, None])

    def Previous(self, expression, scope=None):
        return self._get_value(
            "Previous", expression, scope, [None, None])

    def Avg(self, expression, scope=None):
        return self._get_value(
            "Avg", expression, scope, [0.0, 0])

    def Sum(self, expression, scope=None):
        return self._get_value(
            "Sum", expression, scope, [0.0, None])

    def StDev(self, expression, scope=None):
        return self._get_value(
            "StDev", expression, scope, [0.0, None])

    def StDevP(self, expression, scope=None):
        return self._get_value(
            "StDevP", expression, scope, [0.0, None])

    def Var(self, expression, scope=None):
        return self._get_value(
            "Var", expression, scope, [0.0, None])

    def VarP(self, expression, scope=None):
        return self._get_value(
            "VarP", expression, scope, [0.0, None])

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
        scope_name = None           # Name of group for Running calculation.
        instance_group = None       # Current instance of scope_name group.
        location_group = None       # Group where Running function is called.
        # Current data name and row index if location_group is a detail group.
        current_row = [None, None]
        # Last data name and row index if location_group is a detail group.
        last_row = [None, None]

        aggr = self._get_aggr_info(expression, scope)

        if scope is None:
            scope_name = aggr[1].top_group.name  # Top group (DataSet)
            aggr = self._get_aggr_info(expression, scope_name)
        else:
            scope_name = scope
        instance_group = \
            self.report.data_groups[scope_name].current_instance()
        location_group = self.report.data_groups[aggr[2][0]]
        current_row[0] = location_group.current_instance().data.name
        if location_group.is_detail_group:
            current_row[1] = \
                location_group.current_instance().data._current_index

        value_cache = self._cache.get_value(
            name,
            scope_name + "." + location_group.name,
            expression
        )

        if value_cache:
            if value_cache[0] == instance_group.data.name:
                last_row = value_cache[1]
                result = [value_cache[2], value_cache[3]]
                if last_row[0] is not None:
                    if last_row[0] != current_row[0]:
                        # Reset if detail group instance changed.
                        last_row[1] = None

        if function == 'RowNumber':
            if result is None:
                result = [0, 0]
            if location_group.is_detail_group:
                if last_row[1] != current_row[1]:
                    result[0] += 1
            else:
                if last_row[0] != current_row[0]:
                    result[0] += \
                        location_group.current_instance().data.row_count()
        else:
            if location_group.is_detail_group:
                if last_row[1] != current_row[1]:
                    val = aggr[0].value(self.report)
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
                if last_row[0] != current_row[0]:
                    result = self._instance_value(
                        function, aggr[0],
                        location_group.current_instance().data,
                        result[0], result[1])

        self._cache.set_value(
            name,
            scope_name + "." + location_group.name,
            expression,
            [instance_group.data.name, current_row, result[0], result[1]]
        )

        return self._get_function_result(function, result)

    def _get_value(self, function, expression, scope, value):
        aggr = self._get_aggr_info(expression, scope)
        result = [value[0], value[1]]

        scope_name = aggr[1].current_instance().data.name

        value_cache = self._cache.get_value(function, scope_name, expression)
        if value_cache:
            return self._get_function_result(function, value_cache)

        result = self._instance_value(
            function, aggr[0],
            aggr[1].current_instance().data,
            result[0], result[1])
        self._cache.set_value(function, scope_name, expression, result)

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

    def _get_aggr_info(self, expression, scope):
        # [expression, group, [current_scope]]
        result = [None, None, None]
        if expression is not None:
            result[0] = Expression("=" + expression, None, False)
        result[2] = self.report.current_data_scope
        if scope:
            group = self.report.data_groups[scope]
        else:
            # Current running group
            group = self.report.data_groups[result[2][0]]
        result[1] = group
        return result

    def _instance_value(
            self, function, expression, data,
            result1_start, result2_start):

        result1 = result1_start
        result2 = result2_start
        remember = data._current_index

        if function == "CountRows":
            result1 += data.row_count
            return [result1, None]
        elif function == "First" or function == "Last":
            if function == "First":
                data.move_first()
            else:
                data.move_last()
            if not data.EOF:
                result1 = expression.value(self.report)
            data.move(remember)
            return [result1, None]

        data.move_first()
        while not data.EOF:
            val = expression.value(self.report)
            if val is not None:
                if function == 'Sum':
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
            elif function == 'Aggregate':
                result1.append(val)
            data.move_next()
        data.move(remember)
        return [result1, result2]


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
            return ""
        for message in e.args:
            if not message:
                continue
            if not res:
                res = message
            else:
                res = "{0} - {1}".format(res, message)
        return res
