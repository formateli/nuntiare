# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ..element import Element
from ..expression import verify_expression_constant_and_required
from ...tools import raise_error_with_log, get_expression_value_or_default
from data import Data

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

        self.data = None
        name = verify_expression_constant_and_required("Name", 'DataSet', self.get_element('Name'))
        self.name = name.value()
        self.query = self.get_element('Query')
        if lnk.report.data_sets.has_key(self.name):
            raise_error_with_log("DataSet with name '{0}' already exists.".format(self.name))
        lnk.report.data_sets[self.name] = self

    def execute(self):
        cursor = self.query.get_data_source().cursor
        cursor.execute(self.query.get_command_text())
        result = cursor.fetchall()
        self.data = Data(self.lnk.report, self, cursor, result)


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

