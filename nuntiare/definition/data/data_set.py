# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from .. types.element import Element
from .. types.expression import verify_expression_required
from ... tools import get_expression_value_or_default, raise_error_with_log

class DataSets(Element):
    def __init__(self, node, lnk):
        elements={'DataSet': [Element.ELEMENT],}
        super(DataSets, self).__init__(node, elements, lnk) 


class DataSet(Element):
    '''
    The DataSet element contains information about a set of data to display 
    as a part of the report.
    Name of the data set Cannot be the same name as any data region or group.
    '''

    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING, True],
                  'Fields': [Element.ELEMENT],
                  'Query': [Element.ELEMENT],
                  'Filters': [Element.ELEMENT],
                  'SortExpressions': [Element.ELEMENT],                  
                 }

        self.fields=[]
        super(DataSet, self).__init__(node, elements, lnk)
        
        self.name = get_expression_value_or_default (None, self, 'Name', None)         
        verify_expression_required("Name", 'DataSet', self.name)       
        
        self.fields_def = self.get_element('Fields')
        self.query_def = self.get_element('Query')
        self.filters_def = self.get_element('Filters')
        self.sort_def = self.get_element('SortExpressions')
        if not self.fields_def or not self.query_def: 
            raise_error_with_log("'Fields' and 'Query' elements are required by DataSet '{0}'.".format(self.name))
        
        for ds in lnk.report_def.data_sets:
            if ds.name == self.name:
                raise_error_with_log("DataSet with name '{0}' already exists.".format(self.name))
        lnk.report_def.data_sets.append(self)


class Fields(Element):
    '''
    The Fields element defines the fields in the data model.
    '''
    
    def __init__(self, node, lnk):
        elements={'Field': [Element.ELEMENT],}
        super(Fields, self).__init__(node, elements, lnk) 


class Field(Element):
    '''
    The Field element contains information about a field in the data model of the report.
    '''

    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING, True],
                  'DataType': [Element.ENUM],
                  'DataField': [Element.STRING, True],
                  'Value': [Element.VARIANT],
                 }
        super(Field, self).__init__(node, elements, lnk)

        self.name = get_expression_value_or_default (None, self, 'Name', None)         
        verify_expression_required("Name", 'Field', self.name)        

        self.data_type = get_expression_value_or_default(None, self, 'DataType', None)        
        self.data_field = get_expression_value_or_default(None, self, 'DataField', None)
        self.value=None
        value_element = self.get_element("Value")
        if value_element:
            self.value = value_element.expression
        
        data_set = lnk.parent.lnk.parent # Get Dataset
        for fd in data_set.fields:
            if fd.name == self.name:
                raise_error_with_log("DataSet already has '{0}' Field.".format(self.name))
        data_set.fields.append(self)
        

class Query(Element):
    def __init__(self, node, lnk):
        elements={'DataSourceName': [Element.STRING, True],
                  'CommandText': [Element.STRING],
                  'QueryParameters': [Element.ELEMENT],
                 }
        super(Query, self).__init__(node, elements, lnk)
        
        self.data_source_name = get_expression_value_or_default (None, self, 'DataSourceName', None)
        verify_expression_required("DataSourceName", 'Query', self.data_source_name)

    def get_command_text(self, report):
        cmd = get_expression_value_or_default(report, self, "CommandText", None)
        if not cmd:
            raise_error_with_log("'CommandText' is required by 'Query' element.")
        return cmd


class QueryParameters(Element):
    def __init__(self, node, lnk):
        elements={'QueryParameter': [Element.ELEMENT],}
        super(QueryParameters, self).__init__(node, elements, lnk) 


class QueryParameter(Element):
    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING, True],
                  'Value': [Element.VARIANT],
                 }
        super(QueryParameter, self).__init__(node, elements, lnk)

        self.name = get_expression_value_or_default (None, self, 'Name', None)
        verify_expression_required("Name", 'QueryParameter', self.name)

