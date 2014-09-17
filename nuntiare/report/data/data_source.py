# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ... tools import get_expression_value_or_default
from ... data_providers import get_data_provider

class DataSourceObject(object):
    def __init__(self, report, data_source_def):
        self.report = report
        self.data_source_def = data_source_def
        self.cursor=None
    
    def connect(self):   
        data_provider_name = get_expression_value_or_default(self.report, 
                                            self.data_source_def.conn_properties, 
                                            "DataProvider", None)
        conn_string = get_expression_value_or_default(self.report, 
                                            self.data_source_def.conn_properties, 
                                            "ConnectString", None)

        dp = get_data_provider(data_provider_name) 
        if not dp:
            raise_error_with_log("Invalid DataProvider '{0}' for DataSource '{1}'".format(data_provider_name, self.data_source_def.name))

        if not conn_string:
            raise_error_with_log("Invalid ConnectString for DataSource '{1}'.".format(self.data_source_def.name))
        
        conn = dp.connect(conn_string)
        self.cursor = conn.cursor()
        
