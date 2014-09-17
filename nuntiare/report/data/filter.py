# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ... tools import get_expression_value_or_default

class FiltersObject(object):
    def __init__(self, report, filter_def):
        self.report = report
        self.filter_def = filter_def
        self.filter_list=[]
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
            val = get_expression_value_or_default(self.report, None, None, None, direct_expression=flt.filter_expression)
            operator = get_expression_value_or_default(self.report, None, None, None, direct_expression=flt.operator)
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
            vals.append(get_expression_value_or_default(self.report, None, None, None, direct_expression=v))

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
    def __init__(self, filter_def):
        self.filter_values=[]
        self.filter_expression = filter_def.get_element("FilterExpression")
        self.operator = filter_def.get_element("Operator")
        filter_values_def = filter_def.get_element("FilterValues")
        if filter_values_def:
            for v in filter_values_def.expression_list:        
                self.filter_values.append(v)            

