# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from data import Data
from filter import FiltersObject
from ..element import Element
from ..expression import verify_expression_constant_and_required
from ...tools import raise_error_with_log, get_expression_value_or_default

class DataSets(Element):
    def __init__(self, node, lnk):
        elements={'DataSet': [Element.ELEMENT],}
        super(DataSets, self).__init__(node, elements, lnk) 


class DataSet(Element):
    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING],
                  'Fields': [Element.ELEMENT],
                  'Query': [Element.ELEMENT],
                  'Filters': [Element.ELEMENT],
                 }
        super(DataSet, self).__init__(node, elements, lnk)

        self.data_set_object = None
        name = verify_expression_constant_and_required("Name", 'DataSet', self.get_element('Name'))
        self.name = name.value()
        self.query = self.get_element('Query')
        if lnk.report.data_sets.has_key(self.name):
            raise_error_with_log("DataSet with name '{0}' already exists.".format(self.name))
        lnk.report.data_sets[self.name] = self

    def execute(self):
        field_def = self.get_element('Fields')    
        if not field_def:
            raise_error_with_log("DataSet '{0}' does not have 'Fields' element.".format(self.name))
        fields = FieldsObject(field_def)        
        self.data_set_object = DataSetObject(self.name,
                                self.lnk.report, 
                                self.query.get_data_source().data_source_object.cursor, 
                                self.query.get_command_text(), 
                                fields)
        flt = FiltersObject(self.get_element("Filters"))
        flt.filter_data(self.data_set_object.data)


class Fields(Element):
    def __init__(self, node, lnk):
        elements={'Field': [Element.ELEMENT],}
        self.field_list=[]
        super(Fields, self).__init__(node, elements, lnk) 


class Field(Element):
    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING],
                  'DataField': [Element.STRING],
                  'Value': [Element.VARIANT],
                 }
        super(Field, self).__init__(node, elements, lnk)
        self.name = get_expression_value_or_default(self, 'Name', None)
        if not self.name:
            raise_error_with_log("Name is required for 'Field'element.")
        self.data_field = get_expression_value_or_default(self, 'DataField', None)
        self.value = get_expression_value_or_default(self, 'Value', None)
        if lnk.report.fields.has_key(self.name):
            raise_error_with_log("Field '{0}' already exists.".format(self.name))
        lnk.report.fields[self.name] = self
        lnk.parent.field_list.append(self)


class Query(Element):
    def __init__(self, node, lnk):
        elements={'DataSourceName': [Element.STRING],
                  'CommandText': [Element.STRING],
                  'QueryParameters': [Element.ELEMENT],
                 }
        super(Query, self).__init__(node, elements, lnk)

    def get_data_source(self):
        ds_name = get_expression_value_or_default(self, "DataSourceName", None)
        if not ds_name:
            raise_error_with_log("'DataSourceName' is required for 'Query' element.")
        if not self.lnk.report.data_sources.has_key(ds_name):
            raise_error_with_log("Unknown DataSourceName '{0}' in 'Query' element.", format(ds_name))
        return self.lnk.report.data_sources[ds_name]

    def get_command_text(self):
        cmd = get_expression_value_or_default(self, "CommandText", None)
        if not cmd:
            raise_error_with_log("'CommandText' is required for 'Query' element.")
        return cmd

    def get_query_parameters(self):
        return self.get_element("QueryParameters")


class QueryParameters(Element):
    def __init__(self, node, lnk):
        elements={'QueryParameter': [Element.ELEMENT],}
        super(QueryParameters, self).__init__(node, elements, lnk) 


class QueryParameter(Element):
    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING],
                  'Value': [Element.VARIANT],
                 }
        super(QueryParameter, self).__init__(node, elements, lnk)


class DataSetObject(object):
    def __init__(self, name, report, cursor, command_text, fields):
        cursor.execute(command_text)
        self.data = Data(report, name, fields, cursor)
        #self.data.do_filter()


class FieldsObject(object):
    def __init__(self, field_def, test_field_list=None):        
        self.field_list=[]
        if test_field_list: # We are unittest
            for fd in test_field_list:
                self.add_field(fd[0], fd[1], fd[2])
        else:
            for f in field_def.field_list:
                self.add_field(f.name, f.data_field, f.value)
        
    def add_field(self, name, data_field, value):
        self.field_list.append(FieldObject(name, data_field, value))


class FieldObject(object):
    def __init__(self, name, data_field, value):
        self.name = name
        self.data_field = data_field
        self.value = value

