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
        
        
class FiltersObject(object):
    def __init__(self, filter_def, test_filter_list=None):
        self.filter_list=[]
        if test_filter_list: # We are unittest
            for flt in test_filter_list:
                self.filter_list.append(FilterObject(None, test_filter=flt))
        else:
            if filter_def:
                for flt in filter_def.filter_list:
                    self.filter_list.append(FilterObject(flt))

    def filter_data(self, data):    
        if len(self.filter_list)==0 or len(data.rows)==0: # Nothing to filter
            return
        for flt in self.filter_list:
            data.rows = self.do_filter(flt, data)
            
    def do_filter(self, flt, data):
        data.move_first()
        rows=[]
        while not data.EOF():
            val = get_expression_value_or_default(None, None, None, direct_expression=flt.filter_expression)
            operator = get_expression_value_or_default(None, None, None, direct_expression=flt.operator)
            if operator==None:
                raise_error_with_log("Operator could not be defined for Data '{0}'".format(data.name))
            row = self.filter_row(data.name, flt.filter_values, data.get_current_row(), val, operator)
            if row:
                rows.append(row)
            data.move_next()
        return rows

    def filter_row(self, name, filter_values, current_row, val, operator):
        filtered=False

        vals=[]
        for v in filter_values:        
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
            

class FilterObject(object):
    def __init__(self, filter_def, test_filter=None):
        self.filter_expression = None
        self.operator = None
        self.filter_values = []    
    
        if test_filter: # We are unittest
            self.filter_expression = test_filter[0]
            self.operator = test_filter[1]
            for v in test_filter[2]:
                self.filter_values.append(v)
        else:
            self.filter_expression = filter_def.get_element("FilterExpression")
            self.operator = filter_def.get_element("Operator")
            filter_values_def = filter_def.get_element("FilterValues")
            if filter_values_def:
                for v in filter_values_def.expression_list:        
                    self.filter_values.append(v)


def get_groups(data, expression, sub_groups=[], page_break_at_start=False, page_break_at_end=False):
    group_list=[] # List of DataInterface objects
    groups = {}   # Uses its exp_key as grouping expression

    if len(sub_groups) == 0: # If first grouping
        sub_groups.append([data.name, data])
 
    for data_group in sub_groups:
        groups_exp={}
        group_exp_list=[]
        dt = data_group[1]        
        dt.move_first()
        while not dt.EOF():
            r = dt.get_current_row()
            exp_key = get_expression_value_or_default(None, None, None, direct_expression=expression)
            if not groups_exp.has_key(exp_key):
                from .data import DataGroup
                groups_exp[exp_key] = DataGroup(dt, 
                                    "{0}-{1}".format(dt.name, exp_key),
                                    page_break_at_start, 
                                    page_break_at_end)                   
                group_exp_list.append([exp_key, groups_exp[exp_key]])
            groups_exp[exp_key].add_row(r)
            dt.move_next()
        group_list.extend(group_exp_list)

    return group_list

