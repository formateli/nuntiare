# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from data import Data
from filter import FiltersObject
from sort import SortingObject

class DataSetObject(object):
    def __init__(self, report, data_set_def):
        self.report = report
        self.data_set_def = data_set_def
        self.data = None
        
    def execute(self): #TODO Query parameters
        data_source = self.report.data_sources[self.data_set_def.query_def.data_source_name]
        command_text = self.data_set_def.query_def.get_command_text(self.report)
        data_source.cursor.execute(command_text)
        self.data = Data(self.report, self.data_set_def, data_source.cursor)        
        
        # Filter data
        if self.data_set_def.filters_def:
            flt = FiltersObject(self.report, self.data_set_def.filters_def)
            flt.filter_data(self.data)                  

        # Sort data
        if self.data_set_def.sort_def:
            srt = SortingObject(self.report, self.data_set_def.sort_def)
            srt.sort_data(self.data)
        
