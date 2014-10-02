# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ..types.element import Element
from ..types.expression_list import ExpressionList
from ..types.enum import Enum
from ...tools import get_expression_value_or_default

class VariableFunction(Enum):
    enum_list={'sum': 'Sum',
               'avg': 'Avg',  
               'max': 'Max',  
               'min': 'Min',
               'count': 'Count',
               'countdistinct': 'CountDistinct',
               'countrows': 'CountRows',
               'stdev': 'stDev',
               'stdevp': 'stDevP',
               'var': 'Var',
               'varp': 'VarP',
               'first': 'First',
               'last': 'Last',
               'previous': 'Previous',
               'custom': 'Custom',
              }
    def __init__(self, expression):
        super(VariableFunction, self).__init__('VariableFunction', expression, VariableFunction.enum_list)


class Variables(Element):    
    def __init__(self, node, lnk):
        elements={'Variable': [Element.ELEMENT],}
        self.variable_list=[]
        super(Variables, self).__init__(node, elements, lnk)


class Variable(Element):
    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING, True],
                  'Expression': [Element.VARIANT],
                  'InitialValue': [Element.VARIANT],
                  'Function': [Element.ENUM, 'VariableFunction'],
                  'CustomFunction': [Element.STRING, True],
                 }
        super(Variable, self).__init__(node, elements, lnk)
        lnk.parent.variable_list.append(self)

