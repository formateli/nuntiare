# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ..expression import Expression

class Data(object):
    def __init__(self, report, data_set, cursor, query_result):
        self.fields=[]
        self.report = report
        self.current_index = -1
        self.eof = True 

        fields = data_set.get_element('Fields')
        if not fields:
            raise_error_with_log("DataSet '{0}' does not have 'Fields' element.".format(data_set.name))
        field_by_name={}
        for f in fields.field_list:
            #print " Adding field: " + f.name
            field_by_name[f.name] = (Field(report, f.name, f.data_field, f.value))
            self.fields.append(field_by_name[f.name])
 
        i = 0
        for d in cursor.description:
            #print "  d[0]: " + str(d[0]) 
            for f in self.fields:
                if not f.is_expression and f.data_field == d[0]:
                    #print "  Adding values..."
                    for r in query_result:
                        #print "   " + r[i] 
                        f.add_row(r[i])
            i=i+1

        self.total_records = len(query_result)     

    def move_first(self):
        if  self.total_records == 0:
            self.set_eof()
            return
        self.eof=False
        self.set_current_fields(0)
        self.current_index=0

    def move_next(self):
        self.current_index = self.current_index + 1
        if  self.total_records == self.current_index:
            self.set_eof()
            return
        self.set_current_fields(self.current_index)

    def set_eof(self):
        self.eof = True
        self.set_current_fields(-1)
        self.current_index=-1

    def set_current_fields(self, index):
        self.report.current_fields={}
        if index > -1:
            for f in self.fields:
                self.report.current_fields[f.name]=f.value(index)


class Field(object):
    def __init__(self, report, name, data_field=None, value=None):
        
        if (not data_field and not value) or (data_field and value):
            raise_error_with_log("'Field' must have 'DataField' or 'Value' assigned.")

        self.rows=[]
        self.name = name
        self.data_field = data_field
        self.report=report
        self.is_expression=False
        if value:
            self.is_expression=True
    
    def add_row(self, val):
        if self.is_expression:
            expression = Expression(self.report, val)
        else:
            expression = val
        self.rows.append(expression)

    def value(self, index):
        if self.is_expression:
            return self.rows[index].value()
        return self.rows[index]

