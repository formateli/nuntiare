# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import datetime
from page import Pages
from data.data_source import DataSourceObject
from data.data_set import DataSetObject
from .. import logger

class Report(object):
    def __init__(self, report_def):
        self.report_def=report_def
        self.parameters={}
        self.data_sources={}
        self.data_sets={}
        self.data_groups={}
        self.globals={}
        self.report_items_group={}
        self.current_scope=None

    def run(self, parameters={}):
        self.globals={}
        if self.report_def.globals: # report_file, report_folder, report_name
            for key, value in self.report_def.globals.items():
                self.globals[key] = value       
        self.globals['page_number'] = -1
        self.globals['total_pages'] = -1
        self.globals['execution_time'] = datetime.datetime.now()
        logger.info('Execution time: {0}'.format(self.globals['execution_time']))

        # 1.- Resolve parameters values in declared order.
        self.parameters = {}
        for p in self.report_def.parameters_def:
            key=p.parameter_name
            if self.parameters.has_key(key):
                raise_error_with_log("ReportParameter '{0}' already assigned.".format(key))            
            if parameters.has_key(key):
                self.parameters[key] = p.get_value(self, parameters[key])
            else:
                self.parameters[key] = p.get_default_value(self)

        # 2.- Build data_sources
        self.data_sources={}
        for ds in self.report_def.data_sources:
            self.data_sources[ds.name] = DataSourceObject(self, ds)
            self.data_sources[ds.name].connect()

        # 3.- Build data_sets
        self.data_sets={}
        self.data_groups={}
        for ds in self.report_def.data_sets:
            self.data_sets[ds.name] = DataSetObject(self, ds)
            self.data_sets[ds.name].execute()
            self.data_groups[ds.name] = self.data_sets[ds.name].data

        # 5.- Build pages
        self.pages = Pages(self)

