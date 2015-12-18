# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from importlib import import_module
from . expression import Expression
from .. import logger

class Aggregate(object):
    class _AggregateCache(object):
        def __init__(self):
            self._values = {}   # Cache result of Aggregates with scope.
            self._running = {}  # Cache for Running values

        def get_value(self, function, scope, expression):
            if not function in self._values:
                return
            if not scope in self._values[function]:
                return
            if not expression in self._values[function][scope]:
                return
            return self._values[function][scope][expression]

        def set_value(self, function, scope, expression, value):
            if not function in self._values:
                self._values[function] = {}
            if not scope in self._values[function]:
                self._values[function][scope] = {}
            if not expression in self._values[function][scope]:
                self._values[function][scope][expression] = None
            self._values[function][scope][expression] = value

        def _get_key(self, function, scope, expression):
            return "{0}-{1}-{2}".format(
                function, scope, expression)

    def __init__(self, report):
        self.report = report
        self._cache = Aggregate._AggregateCache()

    def Aggregate(self, expression, scope=None):
        '''
        Returns a list of values according to expression and scope.
        '''
        result = self._get_value(
            "aggregate", expression, scope, [[], None])
        return result[0]

    def Max(self, expression, scope=None):
        result = self._get_value(
            "max", expression, scope, [0.0, None])
        return result[0]

    def Min(self, expression, scope=None):
        result = self._get_value(
            "min", expression, scope, [0.0, None])
        return result[0]

    def Count(self, expression, scope=None):
        result = self._get_value(
            "count", expression, scope, [0, None])
        return result[0]

    def CountRows(self, scope=None):
        result = self._get_value(
            "count_rows", None, scope, [0, None])
        return result[0]

    def First(self, expression, scope=None):
        result = self._get_value(
            "first", expression, scope, [None, None])
        return result[0]

    def Last(self, expression, scope=None):
        result = self._get_value(
            "last", expression, scope, [None, None])
        return result[0]

    def Avg(self, expression, scope=None):
        result = self._get_value(
            "avg", expression, scope, [0.0, 1])
        return result[0] / result[1]

    def Sum(self, expression, scope=None):
        result = self._get_value(
            "sum", expression, scope, [0.0, None])
        return result[0]

    def RunningValue(self, expression, function, scope=None):
        return self._running_value(
            'RunningValue', expression, function, scope)

    def RowNumber(self, scope=None):
        return self._running_value(
            'RowNumber', None, 'RowNumber', scope)

    def _running_value(self, running_name, expression, function, scope):
        if running_name == 'RunningValue':
            valid_fun = ['Sum', 'Avg', 'CountDistinct']
            if function not in valid_fun:
                logger.error(
                    "Invalid function '{0}' for aggregate RunningValue. Valid are: {1}".format(
                        function, valid_fun), True)
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

        if scope == None:
            scope_name = aggr[1].top_group.name # Top group (DataSet)
            aggr = self._get_aggr_info(expression, scope_name)
        else:
            scope_name = scope
        instance_group = self.report.data_groups[scope_name].current_instance()
        location_group = self.report.data_groups[aggr[2][0]]
        current_row[0] = location_group.current_instance().data.name
        if location_group.is_detail_group:
            current_row[1] = location_group.current_instance().data._current_index

        value_cache = self._cache.get_value(
                name, 
                scope_name + "." + location_group.name,
                expression
            )

        if value_cache:
            if value_cache[0] == instance_group.data.name:
                last_row = value_cache[1]
                result = [value_cache[2], value_cache[3]]
                if last_row[0] != None:
                    if last_row[0] != current_row[0]:
                        last_row[1] = None # Reset if detail group instance change.

        if function == 'RowNumber':
            if result == None:
                result = [0, None]
            if location_group.is_detail_group:
                if last_row[1] != current_row[1]:
                    result[0] += 1
            else:
                if current_row[0] != last_row[0]:
                    result[0] += location_group.current_instance().data.row_count()
        else:
            if result == None:
                result = [0.0, None]
            val = aggr[0].value(self.report)
            if val != None:
                pass #TODO
            #    if function == "Sum":
            #        result[0] += val
            #    if function == "Avg":
            #        if len(result) == 1:
            #            result.append(val)
            #            result.append(1)
            #        else:
            #            result[1] += val
            #            result[2] += result[2]
            #        result[0] = result[1] / result[2]

        self._cache.set_value(
                name,
                scope_name + "." + location_group.name,
                expression,
                [instance_group.data.name, current_row, result[0], result[1]]
            )

        return result[0]

    def _get_value(self, function, expression, scope, value):
        aggr = self._get_aggr_info(expression, scope)
        result = [value[0], value[1]]

        scope_name = aggr[1].current_instance().data.name

        value_cache = self._cache.get_value(function, scope_name, expression)
        if value_cache:
            return value_cache

        result = self._instance_value(function, aggr[0],
            aggr[1].current_instance().data, result[0], result[1])
        self._cache.set_value(function, scope_name, expression, result)
        return result

    def _get_aggr_info(self, expression, scope):
        result = [None, None, None] # [expression, group, [current_scope]]
        if expression != None:
            result[0] = Expression("=" + expression, None, False)
        result[2] = self.report.current_data_scope
        if scope:
            group = self.report.data_groups[scope]
        else:
            group = self.report.data_groups[result[2][0]] # Current running group
        result[1] = group
        return result

    def _instance_value(self, function, expression, data, 
            result1_start, result2_start):

        result1 = result1_start
        result2 = result2_start
        remember = data._current_index

        if function == "count_rows":
            result1 += data.row_count
            return [result1, None]
        elif function == "first" or function == "last":
            if function == "first":
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
            if val != None:
                if function == "sum":
                    result1 += val
                elif function == "avg":
                    result1 += val
                    result2 += 1
                elif function == "count":
                    result1 += 1
                elif function == 'max':
                    if val > result1:
                        result1 = val
                elif function == 'min':
                    if val < result1:
                        result1 = val
            elif function == "aggregate":
                result1.append(val)
            data.move_next()
        data.move(remember)
        return [result1, result2]


class ExpressionEval(object):
    def __init__(self, report):
        self.report = report
        self._context = {}
        self.aggregate = Aggregate(report)
        self._loaded = False

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
        if alias == None:
            alias = import_name
        if alias in self._context:
            logger.error(
                "'{0}' already exists in the expression evaluation context.".format(
                    alias), True)
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
        Aggr = A = self.aggregate
        exp_error = "Error evaluating expression: '{0}'".format(expression)

        try:
            if self.report:
                # Collections and aliases
                Parameters = P = self.report.parameters
                Globals = G = self.report.globals
                #TODO ReportItems

                if self.report.current_data_scope[0]: # Always in Row
                    Fields = F = self.report.data_groups[
                        self.report.current_data_scope[0]].current_instance().data.fields
                elif self.report.current_data_interface:
                    Fields = F = self.report.data_interfaces[
                        self.report.current_data_interface].fields

            result = eval(expression)
            
        except KeyError as e:
            logger.error(
                "{0}. Key <{1}> does not exist in dictionary.".format(
                    exp_error, self._get_error_str(e)),
                True, "ValueError")
        except Exception as e:
            logger.error(
                    "{0}. Unexpected error: '{1}'".format(exp_error, self._get_error_str(e)),
                        True)
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

