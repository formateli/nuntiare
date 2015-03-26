# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import os
from xml.dom import minidom
from . import logger
from . template.template import Template
from . template.expression import Expression
from . outcome.outcome import Outcome
from . outcome.data import DataSourceObject, DataSetObject

class Parser(object):
    def __init__(self, definition, output_name, output_directory):
    
        self.parser = None
        
        if os.path.isfile(definition):
            if not os.access(definition, os.R_OK):
                logger.error(
                    "User has not read access for '{0}'.".format(definition), 
                    True, "IOError")
            is_file=True
        else:
            is_file=False
        root = self._get_root(definition, is_file)
        
        if root.nodeName == "Report":
            self.parser = TemplateParser(
                definition, is_file, root, output_name, output_directory)
        else:
            self.parser = OutcomeParser(
                definition, is_file, root, output_name, output_directory)

    def _get_root(self, definition, is_file):
        dom = None
        try:
            if is_file:
                dom = minidom.parse(definition)
            else:
                dom = minidom.parseString(definition)
        except Exception as e:
            logger.critical(
                "Error getting xml dom from definition '{0}'. {1}".format(
                    definition, e.message), 
                True)
        
        root = dom.getElementsByTagName("Report")
        if not root:
            root = dom.getElementsByTagName("Nuntiare")
            if not root:
                logger.critical(
                    "Root tag 'Report' or 'Nuntiare' not found.", True)

        return root[0]


class _Parser(object):
    def __init__(self, definition, is_file, root_node, 
            output_name, output_directory):
        self.object = None                # Result definition object
        self.definition = None            # A file or a xml string
        self.root_node = root_node        # A xml root node
        self.output_name = output_name
        self.output_directory = output_directory
        self.globals = {}
        self.type = None

        if is_file:
            self.globals['report_file'] = definition
            self.globals['report_file_name'] = os.path.basename(definition)
            self.globals['report_folder'] = os.path.dirname(os.path.realpath(definition))
            if not output_directory:
                output_directory = os.path.dirname(
                    os.path.realpath(definition))
            if not output_name:
                output_name = os.path.splitext(
                    self.globals['report_file_name'])[0]
        else:
            self.globals['report_file'] = "From XML string."
            self.globals['report_file_name'] = "From XML string."
            self.globals['report_folder'] = "From XML string."            
            if not output_directory:
                output_directory = os.path.dirname(
                    os.path.realpath(__file__))
        if not os.path.isdir(output_directory):
            logger.error(
                "'{0}' is not a valid directory.".format(
                    output_directory), 
                True, "IOError")
            
        self.globals['output_directory'] = output_directory
        self.globals['output_name'] = output_name
        
    def get_globals(self):
        result = {}
        for key, value in self.globals.items():
            result[key] = value
        if self.object.globals: # report_file, report_folder, report_name
            for key, value in self.object.globals.items():
                result[key] = value
        if not result['output_name']:
            result['output_name'] = result['report_name']                
        return result

    def get_parameters(self, report, parameters=None):
        report.parameters = {}
        
    def get_data_sources(self, report):
        return {}

    def get_data_sets(self, report):
        return {}, {}

    @staticmethod
    def get_value(report, element, element_name, default):
        pass


class TemplateParser(_Parser):
    def __init__(self, definition, is_file, root_node, 
            output_name, output_directory):
                
        super(TemplateParser, self).__init__(
                definition, is_file, root_node, 
                output_name, output_directory)
        
        self.type="xml_template"
        self.object = Template(root_node)

    def get_parameters(self, report, parameters):
        report.parameters = {}
        for p in self.object.parameters_def:
            key = p.parameter_name
            if key in report.parameters:
                logger.error(
                    "ReportParameter '{0}' already assigned.".format(key), True)
            if key in parameters:
                report.parameters[key] = p.get_value(report, parameters[key])
            else:
                report.parameters[key] = p.get_default_value(report)
        if parameters:
            for key, value in parameters.items():
                if not key in self.object.parameters_def:
                    logger.warn("Unknown Parameter '{0}'. Ignored.".format(key))
        
    def get_data_sources(self, report):
        result = {}
        for ds in self.object.data_sources:
            result[ds.name] = DataSourceObject(report, ds)
            result[ds.name].connect()
        return result

    def get_data_sets(self, report):
        data_sets = {}
        data_groups = {}
        for ds in self.object.data_sets:
            logger.info("  Running DataSet '{0}'".format(ds.name))
            data_sets[ds.name] = DataSetObject(report, ds)
            data_sets[ds.name].execute()
            data_groups[ds.name] = data_sets[ds.name].data
        return data_sets, data_groups

    @staticmethod
    def get_value(report, element, element_name, default):
        return Expression.get_value_or_default(
                report, element, element_name, default)
        

class OutcomeParser(_Parser):
    def __init__(self, definition, is_file, root_node, 
            output_name, output_directory):
                
        super(OutcomeParser, self).__init__(
                definition, is_file, root_node, 
                output_name, output_directory)
        
        self.type="xml_outcome"
        self.object = Outcome(root_node)

    def get_parameters(self, report, parameters):
        #TODO
        result = {}
        return result        


    @staticmethod
    def get_value(report, element, element_name, default):
        el = element.get_element(element_name)
        print(el)
        if el:
            return el.value
        return default

