# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from .. import logger
from .. data_providers import get_data_provider
from .. definition.expression import Expression
from .. definition.data_type import DataType

class DataInterface(object):
    def __init__(self, report, name, parent):
        self.name=name
        self.report = report
        self.columns=[]
        self.rows=[]
        self.is_eof = True
        self.current_index = -1
        self.groups=[]
        self.parent = parent

        if name in report.data_groups:
            logger.error("DataSet or Group with name '{0}' already exists.".format(self.name), True)
        report.data_groups[name] = self

    def EOF(self):
        self.set_current_scope()
        return self.is_eof

    def row_number(self): 
        return self.current_index + 1

    def total_rows(self):
        return len(self.rows)

    #TODO Remove, use Variable
    def sum(self, *args):
        total = 0
        cols=[]

        for f in args:
            c = self.get_column(f)
            if not c:
                raise KeyError("'sum_fields' Error. Field '{0}' not found in Data group '{1}'".format(f, self.name))
            cols.append(c)

        for r in self.rows:
            for col in cols:
                total = total + col.get_value(r)        

        return total

    def get_column(self, name):
        for c in self.columns:
            if c.name == name:
                return c 

    def __getitem__(self, key):
        if self.is_eof:
            logger.error("EOF=True in Data '{0}'".format(self.name), True)
        for c in self.columns:
            if c.name == key:
                return c.get_value (self.rows[self.current_index])
        logger.error("Field '{0}' not found in Data '{1}'".format(key, self.name), True)

    def move_first(self):
        self.move(0)

    def move_next(self):
        self.move(self.current_index + 1)

    def move_last(self):
        self.move(self.total_rows() - 1)

    def move(self, i):
        self.set_current_scope()
        if self.total_rows() == 0:
            self.set_eof()
            return
        self.is_eof = False
        self.current_index = i    
        if self.current_index >= self.total_rows():
            self.set_eof()

    def set_eof(self):
        self.is_eof = True
        self.current_index = -1

    def get_current_row(self):
        return self.rows[self.current_index] 

    def set_current_scope(self):
        self.report.current_scope = self.name
    

class Data(DataInterface): 
    def __init__(self, report, data_set, cursor):
        super(Data, self).__init__(report, data_set.name, None)

        x=0
        for fd in data_set.fields:
            self.columns.append(Field(report, x, fd.name, fd.data_field, fd.value, fd.data_type))
            x=x+1

        query_result = cursor.fetchall()
        for r in query_result:
            row=[]
            for c in self.columns:
                if c.is_expression:
                    row.append(None)
                else:
                    i=0
                    for d in cursor.description:
                        if c.data_field == d[0]:
                            row.append(r[i])
                            break 
                        i=i+1
            if len(row) == 0:
                logger.error("Error trying to collect row in DataSet '{0}'. Verify column names.".format(name), True)
            self.rows.append(row)


class Field(object):
    def __init__(self, report, index, name, data_field=None, value=None, data_type=None):
        
        if (not data_field and not value) or (data_field and value):
            logger.error("'Field' must have 'DataField' or 'Value' assigned.", True)

        self.report = report
        self.index=index 
        self.name = name
        self.data_type = data_type
        self.data_field = data_field
        self.is_expression=False
        if value:
            self.expression = Expression(value, None, False)
            self.is_expression=True

    def get_value(self, row):
        result = None
        if self.is_expression:
            result = self.expression.value(self.report)
        else:
            result = row[self.index]
        return DataType.get_value(self.data_type, result)


class DataGroup(DataInterface):
    def __init__(self, data_parent, name, page_break):
        super(DataGroup, self).__init__(data_parent.report, name, data_parent)
        self.columns = data_parent.columns
        self.page_break = page_break

    def add_parent_rows(self):
        self.parent.move_first()
        while not self.parent.EOF():
            r = self.parent.get_current_row()
            self.rows.append(r)
            self.parent.move_next()
            
    def add_row(self, row):
        self.rows.append(row)

    def create_groups(self, expressions, page_break):
        if len(expressions)==0:
            # We have to create just one group, because it can be filtered and/or sortered later.
            grp = DataGroup(self, "{0}-{1}".format(self.name, self.name), page_break)
            grp.add_parent_rows()
            self.groups.append(grp)
            return
        
        groups=[]
                 
        for grp_ex in expressions:
            groups = DataGroup.get_groups(self, grp_ex, groups, None, page_break)
            
        for g in groups:
            self.groups.append(g[1])

    @staticmethod
    def get_groups(data, expression, sub_groups=[], sort_descending=None, page_break=None):
                    
        group_list=[] # List of DataInterface objects

        if len(sub_groups) == 0: # If first grouping
            sub_groups.append([data.name, data])

        for data_group in sub_groups:
            groups_exp={}
            group_exp_list=[]
            dt = data_group[1]
            dt.move_first()
            while not dt.EOF():
                r = dt.get_current_row()
                exp_key = Expression.get_value_or_default(dt.report, None, None, None, 
                        direct_expression=expression)
                if not exp_key in groups_exp:
                    groups_exp[exp_key] = DataGroup(dt,
                                        "{0}-{1}".format(dt.name, exp_key),
                                        page_break)
                    group_exp_list.append([exp_key, groups_exp[exp_key]])
                groups_exp[exp_key].add_row(r)
                dt.move_next()
            if sort_descending != None: 
                group_exp_list = sorted(group_exp_list, key=lambda z: z[0], reverse=sort_descending)
            group_list.extend(group_exp_list)

        return group_list


class DataSourceObject(object):
    def __init__(self, report, data_source_def):
        self.report = report
        self.data_source_def = data_source_def
        self.cursor=None
    
    def connect(self):
        data_provider_name=Expression.get_value_or_default(self.report, 
                self.data_source_def.conn_properties, 
                "DataProvider", None)
        conn_string=Expression.get_value_or_default(self.report, 
                self.data_source_def.conn_properties, 
                "ConnectString", None)    

        dp = get_data_provider(data_provider_name) 
        if not dp:
            logger.error("Invalid DataProvider '{0}' for DataSource '{1}'".format(
                    data_provider_name, self.data_source_def.name), True)

        if not conn_string:
            logger.error("Invalid ConnectString for DataSource '{1}'.".format(
                    self.data_source_def.name), True)
        
        conn = dp.connect(conn_string)
        self.cursor = conn.cursor()


class DataSetObject(object):
    def __init__(self, report, data_set_def):
        self.report = report
        self.data_set_def = data_set_def
        self.data = None
        
    def execute(self): #TODO Query parameters
        data_source = self.report.data_sources[self.data_set_def.query_def.data_source_name]
        command_text = self.data_set_def.query_def.get_command_text(self.report)
        data_source.cursor.execute(command_text)
        self.data = Data(self.report, self.data_set_def, data_source.cursor)
        
        # Filter data
        if self.data_set_def.filters_def:
            flt = FiltersObject(self.report, self.data_set_def.filters_def)
            flt.filter_data(self.data)                  

        # Sort data
        if self.data_set_def.sort_def:
            srt = SortingObject(self.report, self.data_set_def.sort_def)
            srt.sort_data(self.data)
            
            
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
            val = Expression.get_value_or_default(self.report, 
                    None, None, None, direct_expression=flt.filter_expression)
            operator = Expression.get_value_or_default(self.report, 
                    None, None, None, direct_expression=flt.operator)
            if operator==None:
                raise_error_with_log("Operator could not be defined for Data '{0}'".format(data.name))
            row = self.filter_row(data.name, flt.filter_values, 
                    data.get_current_row(), val, operator)
            if row:
                rows.append(row)
            data.move_next()
        return rows
        
    def filter_row(self, name, filter_values, current_row, val, operator):
        filtered=False

        vals=[]
        for v in filter_values:        
            vals.append(Expression.get_value_or_default(self.report, 
                    None, None, None, direct_expression=v))

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


class GroupingObject(object):
    def __init__(self, group_def):
        self.expression_list=[]
        self.name=None
        self.page_break=None
        self.filters=None
        self.parent=None
        
        if group_def:
            self.name = group_def.get_element("Name")            
            self.page_break_at_start = group_def.get_element("PageBreakAtStart")
            self.page_break_at_end = group_def.get_element("PageBreakAtEnd")
            self.filters = group_def.get_element("Filters")
            self.parent = group_def.get_element("Parent")
            exps = group_def.get_element("GroupExpressions")
            for ex in exps.expression_list:
                self.expression_list.append(ex)


class SortingObject(object):
    def __init__(self, report, sorting_def):
        self.report = report
        self.sortby_list=[]
        for srt in sorting_def.sortby_list:
            self.sortby_list.append(SortByObject(srt, report))

    def sort_data(self, data):
        if len(self.sortby_list)==0:
            return

        groups=[]
        i=0
        for sortby in self.sortby_list:            
            reverse = False if sortby.direction == "Ascending" else True
            if i==0:    
                groups = DataGroup.get_groups(data, sortby.sort_value, sub_groups=[])
                groups = sorted(groups, key=lambda z: z[0], reverse=reverse)
            else:
                #Sort is made in get_groups function.
                groups = DataGroup.get_groups(data, sortby.sort_value, sub_groups=groups, sort_descending=reverse)
            i=i+1 
        
        if len (groups)==0:
            return
        data.rows=[]
        for g in groups:
            for r in g[1].rows:
                data.rows.append(r)
            del data.report.data_groups[g[1].name] # Delete from global collection


class SortByObject(object):
    def __init__(self, sortby_def, report):
        self.sort_expression=None
        self.direction="Ascending"

        if sortby_def:
            self.sort_value = sortby_def.get_element("Value")
            self.direction = Expression.get_value_or_default(report, 
                    sortby_def, "SortDirection", "Ascending")                


