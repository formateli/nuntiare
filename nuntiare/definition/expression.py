# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from expression_eval import get_expression_eval
from ..tools import raise_error_with_log

class Expression(object):
    def __init__(self, report, expression):
        self.report = report
        self.expression=None
        self.is_constant=False
        self.set_expression(expression)

    def set_expression(self, expression):
        self.expression=expression
        if self.expression==None or not self.expression.startswith('='):
            self.is_constant=True

    def value(self):
        if self.is_constant:
            return self.expression
        ex = self.expression[1:]
        return get_expression_eval(self.report, ex) # Run python code


def verify_expression_required(name, element, expr):
    if not expr or expr.value()==None or expr.value().strip()=='':
        raise_error_with_log("Attribute '{0}' is required for element '{1}'.".format(name, element))
    return expr


def verify_expression_constant(name, element, expr):
    if not expr or not expr.is_constant:
        raise_error_with_log("Attribute '{0}' of element '{1}' must be a constant value.".format(name, element))
    return expr


def verify_expression_constant_and_required(name, element, expr):
    verify_expression_required(name, element, expr)
    verify_expression_constant(name, element, expr)
    return expr







