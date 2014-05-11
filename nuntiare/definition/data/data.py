# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from filter import get_groups
from ..expression import Expression
from ...tools import raise_error_with_log, get_expression_value_or_default

class DataInterface(object):
    def __init__(self, report, name):
        self.name=name
        self.report = report
        self.columns=[]
        self.rows=[]
        self.is_eof = True
        self.current_index = -1
        self.groups=[]

        if report.data_groups.has_key(name):
            raise_error_with_log("DataSet or Grouping with name '{0}' already exists.".format(self.name))            
        report.data_groups[name] = self

    def has_groups(self):
        return False if len(self.groups)==0 else True

    def EOF(self):
        self.set_current_scope()
        return self.is_eof

    def row_number(self):
        return self.current_index + 1

    def sum_fields(self, *args):
        total = 0
        cols=[]

        for f in args: 
            c = self.get_column(f)            
            if not c:
                raise KeyError("Field '{0}' not found in Data group '{1}'".format(f, self.name))
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
        self.move(len(self.rows) - 1)

    def move(self, i):
        self.set_current_scope()
        if len(self.rows) == 0:
            self.set_eof()
            return
        self.is_eof = False
        self.current_index = i    
        if self.current_index >= len(self.rows):
            self.set_eof()

    def set_eof(self):
        self.is_eof = True
        self.current_index = -1

    def get_current_row(self):
        return self.rows[self.current_index] 

    def set_current_scope(self):
        self.report.current_scope = self.name
            

class Data(DataInterface):
    def __init__(self, report, name, fields, cursor):
        super(Data, self).__init__(report, name)

        x=0
        for f in fields.field_list:
            self.columns.append(Field(report, x, f.name, f.data_field, f.value))
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
    def __init__(self, report, index, name, data_field=None, value=None):
        
        if (not data_field and not value) or (data_field and value):
            raise_error_with_log("'Field' must have 'DataField' or 'Value' assigned.")

        self.index=index 
        self.name = name
        self.data_field = data_field
        self.is_expression=False
        if value:
            self.expression = Expression(report, value)
            self.is_expression=True

    def get_value(self, row):
        if self.is_expression:
            return self.expression.value()
        return row[self.index]


class DataGroup(DataInterface):
    def __init__(self, data_parent, name, page_break_at_start, page_break_at_end):
        super(DataGroup, self).__init__(data_parent.report, name)
        self.data_parent = data_parent
        self.columns = data_parent.columns
        self.page_break_at_start=page_break_at_start
        self.page_break_at_end=page_break_at_end

    def add_rows_by_parent(self):
        self.data_parent.move_first()
        while not self.data_parent.EOF():
            r = self.data_parent.get_current_row()
            self.rows.append(r)
            self.data_parent.move_next()
            
    def add_row(self, row):
        self.rows.append(row)

    def create_groups(self, expressions, page_break_at_start, page_break_at_end):
        if len(expressions)==0:
            # We have to create just one group, because it can be filtered and/or sortered later.
            grp = DataGroup(self, "{0}-{1}".format(self.name, self.name),
                            page_break_at_start, page_break_at_end)
            grp.add_rows_by_parent()
            self.groups.append(grp)
            return
        
        groups=[]
                 
        for grp_ex in expressions:
            groups = get_groups(self, grp_ex, groups, page_break_at_start, page_break_at_end)
            
        for g in groups:
            self.groups.append(g[1])
        
