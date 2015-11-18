# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from importlib import import_module
from . expression import Expression
from .. import logger

class Aggregate(object):
    def __init__(self, report):
        self.report = report

    def Aggregate(self, expression, scope=None):
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

    def CountRows(self, expression, scope=None):
        result = self._get_value(
            "count_rows", expression, scope, [0, None])
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

    def _get_value(self, function, expression, scope, value):
        aggr = self._get_aggr_info(expression, scope)
        result = [value[0], value[1]]
        if scope and aggr[1].instance:
            if function == "first":
                result = self._instance_value(function, aggr[0],
                    aggr[1].instance[0].data, result[0], result[1])
            elif function == "last":
                result = self._instance_value(function, aggr[0],
                    aggr[1].instance[len(aggr[1].instance - 1)].data, result[0], result[1])
            else:
                for instance in aggr[1].instance:
                    result = self._instance_value(function, aggr[0],
                        instance.data, result[0], result[1])
        else:
            result = self._instance_value(function, aggr[0],
                aggr[1].current_instance().data, result[0], result[1])
        return result

    def _get_aggr_info(self, expression, scope):
        result = []
        result.append(Expression("=" + expression, None, False))
        if scope:
            group = self.report.data_groups[scope]
        else:
            group = self.report.data_groups[self.report.current_data_scope[0]]
        result.append(group)
        return result    
        
    def _instance_value(self, function, expression, data, 
            result1_start, result2_start):
        result1 = result1_start
        result2 = result2_start
        
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
                    if val > result:
                        result1 = val
                elif function == 'min':
                    if val < result1:
                        result1 = val
            elif function == "aggregate":
                result1.append(val)
            data.move_next()
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
        res = ""
        if not e:
            return ""
        for message in e.args:
            res = "{0} - {1}".format(res, message)
        return res

