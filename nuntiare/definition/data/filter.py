# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ..element import Element
from ..expression_list import ExpressionList
from ..enum import Enum
from ...tools import raise_error_with_log, get_expression_value_or_default

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
    def __init__(self, report, expression):
        super(Operator, self).__init__(report, 'Operator', expression, Operator.enum_list)


class Filters(Element):
    def __init__(self, node, lnk):
        elements={'Filter': [Element.ELEMENT],}
        self.filter_list=[]
        super(Filters, self).__init__(node, elements, lnk)


class Filter(Element):
    def __init__(self, node, lnk):
        elements={'FilterExpression': [Element.VARIANT],
                  'Operator': [Element.ENUM],
                  'FilterValues': [Element.EXPRESSION_LIST],
                 }
        super(Filter, self).__init__(node, elements, lnk)
        lnk.parent.filter_list.append(self)


class FilterValues(ExpressionList):
    def __init__(self, node, lnk):
        elements={'FilterValue': [Element.VARIANT],}
        super(FilterValues, self).__init__(node, elements, lnk)


def get_filtered_rows(filter_def, data):
    def do_filter(filter_def, data):
        data.move_first()
        rows=[]
        while not data.EOF():
            val = get_expression_value_or_default(filter_def, 'FilterExpression', None)
            expressions_def = filter_def.get_element('FilterValues')
            operator = get_expression_value_or_default(filter_def, 'Operator', None)
            if operator==None:
                raise_error_with_log("Operator could not be defined for Data '{0}'".format(data.name))
            row = filter_row(data.name, expressions_def, data.get_current_row(), val, operator)
            if row:
                rows.append(row)
            data.move_next()
        return rows

    def filter_row(name, expressions_def, current_row, val, operator):
        filtered=False

        vals=[]
        for v in expressions_def.expression_list:        
            vals.append(get_expression_value_or_default(None, None, None, direct_expression=v))

        if len(vals) == 0:
            raise_error_with_log("No filter values defined for '{0}'".format(name))

        if operator not in ('In','Between'):
            if len(vals) > 1:
                raise_error_with_log("Operator '{0}' only accepts one filter value. Data name: '{1}'".format(operator, name))
            if operator == "Equal":
                if val == vals[0]:
                    filtered=True
            if operator == "NotEqual":
                if val != vals[0]:
                    filtered=True
            if operator == "GreaterThan":
                if val > vals[0]:
                    filtered=True
            if operator == "GreaterThanOrEqual":
                if val >= vals[0]:
                    filtered=True
            if operator == "LessThan":
                if val < vals[0]:
                    filtered=True
            if operator == "LessThanOrEqual":
                if val <= vals[0]:
                    filtered=True
            if operator in ('Like','TopN','BottomN','TopPercent','BottomPercent'):
                raise_error_with_log("Operator '{0}' is not supported at this moment.".format(operator))        

        else:
            if operator == "Between":
                if len(vals) > 2:
                    raise_error_with_log("Operator '{0}' takes exactly 2 filter values. Data name: '{1}'".format(operator, name))
                if val >= vals[0] and val <= vals[1]:
                    filtered=True
            if operator == "In":
                if val in vals:
                    filtered=True

        if filtered:
            return current_row

    result=[]
    if not filter_def or len(data.rows)==0:
        return result 

    for flt in filter_def.filter_list:
        data.rows = do_filter(flt, data)

