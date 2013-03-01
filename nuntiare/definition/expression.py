# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from nuntiare.tools import raise_error_with_log

class Expression(object):
    def __init__(self, expression):    
        self.is_constant=False
        self.expression=expression
        self.original_expression=expression # Expression may change for constant value. Ex. Enum
        if self.expression==None or not self.expression.startswith('pass '):
            self.is_constant=True

    def value(self):
        if self.is_constant:
            return self.expression
        ex = self.expression[5:]
        return self.get_eval_value(ex) # Run python code

    def get_eval_value(self, code):
        #TODO Try exception
        print "Pass code: " + code
        result = eval(code)
        print "Pass code result: " + str(result)
        return result  

def verify_expression_required(name, element, expr):
    if not expr or expr.value()==None or expr.value().strip()=='':
        raise_error_with_log("Attribute '{0}' is required for element '{1}'.".format(name, element))
    return expr

def verify_expression_constant(name, element, expr):
    if not expr.is_constant:
        raise_error_with_log("Attribute '{0}' of element '{1}' can not be an expression.".format(name, element))
    return expr

def verify_expression_constant_and_required(name, element, expr):
    verify_expression_required(name, element, expr)
    verify_expression_constant(name, element, expr)
    return expr


