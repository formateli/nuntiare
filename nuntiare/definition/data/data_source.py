# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ..element import Element
from ..expression import verify_expression_constant_and_required
from ...data_providers import get_data_provider
from ...tools import raise_error_with_log

class DataSources(Element):
    def __init__(self, node, lnk):
        elements={'DataSource': [Element.ELEMENT],}
        super(DataSources, self).__init__(node, elements, lnk) 


class DataSource(Element):
    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING],
                  'Transaction': [Element.BOOLEAN],
                  'ConnectionProperties': [Element.ELEMENT],
                 }
        super(DataSource, self).__init__(node, elements, lnk)
        name = verify_expression_constant_and_required("Name", 'DataSource', self.get_element('Name'))
        self.name = name.value()
        
        self.data_source_object=None

        self.conn_properties = self.get_element('ConnectionProperties')
        if not self.conn_properties:
            raise_error_with_log("No 'ConnectionProperties' element defined for DataSource '{0}'".format(self.name))
         
        if lnk.report.data_sources.has_key(self.name):
            raise_error_with_log("Report already has a DataSource with name '{0}'".format(self.name))
        lnk.report.data_sources[self.name] = self

    def connect(self):
        self.data_source_object = DataSourceObject()
        self.data_source_object.connect(self.conn_properties.data_provider.value(), 
                            self.conn_properties.connection_string.value())


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


# We use a separate class for unittest
class DataSourceObject(object):
    def __init__(self):
        self.cursor=None
    
    def connect(self, data_provider_name, conn_string):
        dp = get_data_provider(data_provider_name)
        conn = dp.connect(conn_string)
        self.cursor = conn.cursor()



