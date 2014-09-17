# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ..types.element import Element
from ..types.expression_list import ExpressionList
from ..types.enum import Enum
from ...tools import get_expression_value_or_default

class Operator(Enum):
    enum_list={'equal': 'Equal',
               'like': 'Like',  
               'notequal': 'NotEqual',  
               'greaterthan': 'GreaterThan',
               'greaterthanorequal': 'GreaterThanOrEqual',
               'lessthan': 'LessThan',
               'lessthanorequal': 'LessThanOrEqual',
               'topn': 'TopN',
               'bottomn': 'BottomN',
               'toppercent': 'TopPercent',
               'bottompercent': 'BottomPercent',
               'in': 'In',
               'between': 'Between',
              }
    def __init__(self, expression):
        super(Operator, self).__init__('Operator', expression, Operator.enum_list)


class Filters(Element):
    '''
    The Filters element is a collection of filters to apply to a data set, data region or group.
    '''
    
    def __init__(self, node, lnk):
        elements={'Filter': [Element.ELEMENT],}
        self.filter_list=[]
        super(Filters, self).__init__(node, elements, lnk)


class Filter(Element):
    '''
    The Filter element describes a filter to apply to rows of data in a data set or data region or to
    apply to group instances.
    
    FilterExpression:
    An expression that is evaluated for each instance within the group or 
    each row of the data set or data region and compared (via the Operator) 
    to the FilterValues. Failed comparisons result in the row/instance being filtered 
    out of the data set, data region or group.

    Operator:
    Equal, Like, NotEqual, GreaterThan, GreaterThanOrEqual, LessThan, LessThanOrEqual,
    TopN, BottomN TopPercent, BottomPercent, In, Between.
    
    FilterValues:
    The values to compare to the FilterExpression.
    For Equal, Like, NotEqual, GreaterThan, GreaterThanOrEqual, LessThan, LessThanOrEqual,
    TopN, BottomN, TopPercent and BottomPercent, there must be exactly one FilterValue.
    For TopN and BottomN, the FilterValue expression must evaluate to an integer.
    For TopPercent and BottomPercent, the FilterValue expression must evaluate to an integer or float.
    For Between, there must be exactly two FilterValue elements.
    For In, the FilterValues are treated as a set (if the FilterExpression value appears anywhere 
    in the set of FilterValues, the instance is not filtered out.)        
    '''

    def __init__(self, node, lnk):
        elements={'FilterExpression': [Element.VARIANT],
                  'Operator': [Element.ENUM],
                  'FilterValues': [Element.EXPRESSION_LIST],
                 }
        super(Filter, self).__init__(node, elements, lnk)
        lnk.parent.filter_list.append(self)


class FilterValues(ExpressionList):
    def __init__(self, node, lnk):
        elements={'FilterValue': [Element.VARIANT,],}
        super(FilterValues, self).__init__(node, elements, lnk)

