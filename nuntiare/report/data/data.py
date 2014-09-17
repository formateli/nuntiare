# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ... definition.data.data_type import get_data_type_value
from ... definition.types.expression import Expression
from ... tools import get_expression_value_or_default, raise_error_with_log

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

        if report.data_groups.has_key(name):
            raise_error_with_log("DataSet or Group with name '{0}' already exists.".format(self.name))            
        report.data_groups[name] = self

    def EOF(self):
        self.set_current_scope()
        return self.is_eof

    def row_number(self): 
        return self.current_index + 1

    def total_rows(self):
        return len(self.rows)

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
            raise_error_with_log("EOF=True in Data '{0}'".format(self.name))
        for c in self.columns:
            if c.name == key:
                return c.get_value (self.rows[self.current_index])
        raise_error_with_log("Field '{0}' not found in Data '{1}'".format(key, self.name))

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
                raise_error_with_log("Error trying to collect row in DataSet '{0}'. Verify column names.".format(name))
            self.rows.append(row)


class Field(object):
    def __init__(self, report, index, name, data_field=None, value=None, data_type=None):
        
        if (not data_field and not value) or (data_field and value):
            raise_error_with_log("'Field' must have 'DataField' or 'Value' assigned.")

        self.report = report
        self.index=index 
        self.name = name
        self.data_type = data_type
        self.data_field = data_field
        self.is_expression=False
        if value:
            self.expression = Expression(value, False)
            self.is_expression=True

    def get_value(self, row):
        result = None
        if self.is_expression:
            result = self.expression.value(self.report)
        else:
            result = row[self.index]
        return get_data_type_value(self.data_type, result)


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
            groups = get_groups(self, grp_ex, groups, None, page_break)
            
        for g in groups:
            self.groups.append(g[1])


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
            exp_key = get_expression_value_or_default(dt.report, None, None, None, 
                                            direct_expression=expression)
            if not groups_exp.has_key(exp_key):
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

