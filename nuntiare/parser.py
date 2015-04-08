# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import os
from xml.dom import minidom
from . import logger
from . template.expression import Expression
from . template.template import Template
from . outcome.outcome import Outcome
from . outcome.data import DataSourceObject, DataSetObject
from . outcome.style import OutcomeStyle

class Parser(object):
    def __init__(self, report, definition, 
                 output_name, output_directory):
                 
        super(Parser, self).__init__()
        
        self.parser = None
        
        is_file = False
        if os.path.isfile(definition):
            if not os.access(definition, os.R_OK):
                logger.error(
                    "User has not read access for '{0}'.".format(definition),
                    True, "IOError")
            is_file=True
        root = self._get_root(definition, is_file)
        
        if root.nodeName == "Report":
            self.parser = TemplateParser(
                report, definition, is_file, root, output_name, output_directory)
        else:
            self.parser = OutcomeParser(
                report, definition, is_file, root, output_name, output_directory)

    def _get_root(self, definition, is_file):
        dom = None
        try:
            if is_file:
                dom = minidom.parse(definition)
            else:
                dom = minidom.parseString(definition)
        except Exception as e:
            err_msg = '''Error getting xml dom from definition '{0}'.
Is it supposed to be a file?. Verify that it exists.
If it is a xml string, verify that it is well formed.
System error: {1}'''

            logger.critical(
                err_msg.format(definition, e.message), True)
        
        root = dom.getElementsByTagName("Report")
        if not root:
            root = dom.getElementsByTagName("Nuntiare")
            if not root:
                logger.critical(
                    "Root tag 'Report' or 'Nuntiare' not found.", True)

        return root[0]


class _Parser(object):
    def __init__(self, report, definition, is_file, root_node, 
            output_name, output_directory):
        super(_Parser, self).__init__()    
            
        self.report = report    
        self.object = None                # Result definition object
        self.definition = None            # A file or a xml string
        self.root_node = root_node        # A xml root node
        self.output_name = output_name
        self.output_directory = output_directory
        self.globals = {}
        self.type = None
        self.style = OutcomeStyle(report)        

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
        return result

    def get_parameters(self, parameters):
        report.parameters = {}
        
    def get_data_sources(self):
        return {}

    def get_data_sets(self):
        return {}, {}

    def get_style(self, element):
        el = element.get_element("Style")
        return self.style.get_style(el)

    def get_item_list(self, element):
        return

    def get_value(self, element, element_name, default):
        return Expression.get_value_or_default(
                self.report, element, element_name, default)

    def get_item_list(self, element):
        el = element.get_element("ReportItems")
        if el:
            return el.reportitems_list


class TemplateParser(_Parser):
    def __init__(self, report, definition, is_file, root_node, 
            output_name, output_directory):
                
        super(TemplateParser, self).__init__(
                report, definition, is_file, root_node, 
                output_name, output_directory)
        
        self.type="xml_template"
        self.object = Template(root_node)

    def get_parameters(self, parameters):
        self.report.parameters = {}
        for p in self.object.parameters_def:
            key = p.parameter_name
            if key in self.report.parameters:
                logger.error(
                    "ReportParameter '{0}' already assigned.".format(key), True)
            if key in parameters:
                self.report.parameters[key] = p.get_value(self.report, parameters[key])
            else:
                self.report.parameters[key] = p.get_default_value(self.report)
        if parameters:
            for key, value in parameters.items():
                if not key in self.object.parameters_def:
                    logger.warn("Unknown Parameter '{0}'. Ignored.".format(key))
        
    def get_data_sources(self):
        result = {}
        for ds in self.object.data_sources:
            result[ds.name] = DataSourceObject(self.report, ds)
            result[ds.name].connect()
        return result

    def get_data_sets(self):
        data_sets = {}
        data_groups = {}
        for ds in self.object.data_sets:
            logger.info("  Running DataSet '{0}'".format(ds.name))
            data_sets[ds.name] = DataSetObject(self.report, ds)
            data_sets[ds.name].execute()
            data_groups[ds.name] = data_sets[ds.name].data
        return data_sets, data_groups


class OutcomeParser(_Parser):
    def __init__(self, report, definition, is_file, root_node, 
            output_name, output_directory):
                
        super(OutcomeParser, self).__init__(
                report, definition, is_file, root_node, 
                output_name, output_directory)
        
        self.type = "xml_outcome"
        self.object = Outcome(root_node)

    def get_globals(self):
        result = super(OutcomeParser, self).get_globals()
        gb = self.object.get_element("Globals")
        if gb:
            self._add_global(result, gb, "report_name")
            self._add_global(result, gb, "author")
            self._add_global(result, gb, "description")
            self._add_global(result, gb, "version")
        return result
        
    def _add_global(self, globals_, el, name):
        gb = el.get_element(name)
        if gb:
            globals_[name] = gb.value

    def get_parameters(self, parameters):
        self.report.parameters = {}
        prms = self.object.get_element("ReportParameters")
        if prms:
            for p in prms.parameter_list:
                name = p.get_element("Name").value
                self.report.parameters[name] = p.value()

    def get_style(self, element):
        style_id = self.get_value(element, "StyleId", None)
        if style_id == None:
            return super(OutcomeParser, self).get_style(element)
        st = self.object.get_element("Styles").style_list[style_id]
        return self.style.get_style(st)

    def get_item_list(self, element):
        el = element.get_element("PageItems")
        if el:
            return el.pageitem_list
        return super(OutcomeParser, self).get_item_list(element)

    def get_value(self, element, element_name, default):
        if not element:
            return default
        el = element.get_element(element_name)
        if el:
            if isinstance(el, Expression): 
                return super(OutcomeParser, self).get_value(
                        element, element_name, default)
            return el.value
        return default

