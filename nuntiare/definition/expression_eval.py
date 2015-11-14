# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from importlib import import_module
import sys
from .. import logger

class ExpressionEval(object):
    def __init__(self, report):
        self.report = report
        self._context = {}
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

