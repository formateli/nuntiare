# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ..expression_eval import get_expression_eval
from ...tools import raise_error_with_log

class Expression(object):
    def __init__(self, expression, must_be_constant=False):
        self.must_be_constant=must_be_constant
        self.expression, self.is_constant = self.set_expression(expression)

    def set_expression(self, expression):
        is_constant=False
        if expression==None or not expression.startswith('='):
            is_constant=True
        if self.must_be_constant and not is_constant:
            raise_error_with_log("Invalid expression '{0}'. It must be a constant expression.".format(expression))
        return [expression, is_constant]

    def value(self, report, new_expression=None):
        if new_expression:
            expression, is_constant = self.set_expression(new_expression)        
        else:
            expression = self.expression
            is_constant = self.is_constant    
    
        if is_constant:
            return expression
        ex = expression[1:]
        return get_expression_eval(report, ex) # Run python code


def verify_expression_required(name, element, expr):
    if not expr or expr.strip()=='':
        raise_error_with_log("Element '{0}' is required for element '{1}'.".format(name, element))    

    
