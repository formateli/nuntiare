# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from .. types.element import Element
from .. types.expression import verify_expression_required
from ... data_providers import get_data_provider
from ... tools import get_expression_value_or_default

class DataSources(Element):
    def __init__(self, node, lnk):
        elements={'DataSource': [Element.ELEMENT],}
        super(DataSources, self).__init__(node, elements, lnk) 


class DataSource(Element):
    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING, True],
                  'Transaction': [Element.BOOLEAN, True],
                  'ConnectionProperties': [Element.ELEMENT],
                 }
        super(DataSource, self).__init__(node, elements, lnk)
        self.name = get_expression_value_or_default (None, self, 'Name', None) 
        self.transaction = get_expression_value_or_default (None, self, 'Transaction', None)
        
        verify_expression_required("Name", 'DataSource', self.name)
        
        self.conn_properties = self.get_element('ConnectionProperties')
        if not self.conn_properties:
            raise_error_with_log("No 'ConnectionProperties' element defined for DataSource '{0}'".format(self.name))
        
        for ds in lnk.report_def.data_sources:
            if ds.name == self.name:
                raise_error_with_log("Report already has a DataSource with name '{0}'".format(self.name))
        lnk.report_def.data_sources.append(self)


class ConnectionProperties(Element):
    def __init__(self, node, lnk):
        elements={'DataProvider': [Element.STRING],
                  'ConnectString': [Element.STRING],
                  'Prompt': [Element.STRING],
                 }
        super(ConnectionProperties, self).__init__(node, elements, lnk)
        self.data_provider = self.get_element("DataProvider")
        if not self.data_provider:
            raise_error_with_log("DataProvider no defined for ConnectionProperties element.")
        self.connection_string = self.get_element("ConnectString")
        if not self.connection_string:
            raise_error_with_log("ConnectString no defined for ConnectionProperties element.")
