# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ..expression import Expression
from ..data.filter import get_filtered_rows
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
        #print "Creating Data: " + name
        report.data_groups[name] = self

    def has_groups(self):
        return False if len(self.groups)==0 else True

    def EOF(self):
        self.report.current_scope = self.name
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
        self.report.current_scope = self.name
        if  len(self.rows) == 0:
            self.set_eof()
            return
        self.is_eof=False
        self.current_index=0

    def move_next(self):
        self.report.current_scope = self.name
        self.current_index = self.current_index + 1
        if self.current_index >= len(self.rows):
            self.set_eof()

    def move(self, i):
        self.report.current_scope = self.name
        self.current_index = i
        if self.current_index >= len(self.rows):
            self.set_eof()

    def set_eof(self):
        self.is_eof = True
        self.current_index = -1

    def get_current_row(self):
        return self.rows[self.current_index] 


class Data(DataInterface):
    def __init__(self, report, data_set, cursor):
        super(Data, self).__init__(report, data_set.name)

        fields = data_set.get_element('Fields')
        if not fields:
            raise_error_with_log("DataSet '{0}' does not have 'Fields' element.".format(data_set.name))
        x=0
        for f in fields.field_list:
            self.columns.append(Field(report, x, f.name, f.data_field, f.value))
            x=x+1
 
        self.filter_def = data_set.get_element("Filters")

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
                raise_error_with_log("Error trying to collect row in DataSet '{0}'.".format(data_set.name))
            self.rows.append(row)

    def do_filter(self):
        get_filtered_rows(self.filter_def, self)


class Field(object):
    def __init__(self, report, index, name, data_field=None, value=None):
        
        if (not data_field and not value) or (data_field and value):
            raise_error_with_log("'Field' must have 'DataField' or 'Value' assigned.")

        self.index=index 
        self.name = name
        self.data_field = data_field
        self.report=report
        self.is_expression=False
        if value:
            self.expression = Expression(self.report, value)
            self.is_expression=True

    def get_value(self, row):
        if self.is_expression:
            return self.expression.value()
        return row[self.index]


class SubGroup(DataInterface):
    def __init__(self, report, name, columns):
        super(SubGroup, self).__init__(report, name)
        self.columns = columns


class DataGroup(DataInterface):
    def __init__(self, data_parent, name, grouping_def, sorting_def, filter_def):
        super(DataGroup, self).__init__(data_parent.report, name)
        self.columns = data_parent.columns
        self.grouping_def = grouping_def
        self.sorting_def = sorting_def
        self.filter_def = filter_def

        data_parent.move_first()
        while not data_parent.EOF():
            r = data_parent.get_current_row()
            self.rows.append(r)
            data_parent.move_next()

    def do_filter(self):
        get_filtered_rows(self.filter_def, self)

    def sort(self):
        if not self.sorting_def:
            return

        groups=[]
        for sortby in self.sorting_def.sortby_list:
            direction = get_expression_value_or_default(sortby, "SortDirection", "Ascending")
            ex = sortby.get_element("SortExpression")
            reverse = False if direction == "Ascending" else True
            groups = self.get_groups(ex, groups)
            groups = sorted(groups, key=lambda z: z[0], reverse=reverse)

        if len (groups)==0:
            return
        self.rows=[]
        for g in groups:
            for r in g[1].rows:
                self.rows.append(r)
            del self.report.data_groups[g[1].name] # Delete from global collection

    def create_groups(self):
        if not self.grouping_def:
            return

        expressions = self.grouping_def.get_element("GroupExpressions")
        groups=[]
        for grp_ex in expressions.expression_list:
            groups = self.get_groups(grp_ex, groups)

        for g in groups:
            self.groups.append(g[1])

    def get_groups(self, expression, sub_groups=[]):
        group_list=[] # List of DataInterface objects
        groups = {}   # Uses its key as grouping expression

        if len(sub_groups) == 0: # If first grouping
            sub_groups.append([self.name, self])
 
        for data_group in sub_groups:
            data = data_group[1]
            data.move_first()
            while not data.EOF():
                r = data.get_current_row()
                key = get_expression_value_or_default(None, None, None, direct_expression=expression)
                if groups.has_key(key):
                    groups[key].rows.append(r) 
                else:
                    groups[key] = SubGroup(self.report, "{0}-{1}".format(data.name, key), data.columns)
                    groups[key].rows.append(r)
                    group_list.append([key, groups[key]])

                data.move_next()

        return group_list

