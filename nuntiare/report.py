# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import os
import datetime
from xml.dom import minidom
from . result import Result
from . import logger
from . definition.element import Report as ReportDef
from . definition.expression import Expression
from . definition.expression_eval import ExpressionEval
from . data.data_type import DataType
from . data.data import DataSourceObject, DataSetObject
from . outcome.style import OutcomeStyle
from . collection import Collection, CollectionItem

class Globals(Collection):
    def __init__(self):
        super(Globals, self).__init__()


class Parameters(Collection):
    def __init__(self):
        super(Parameters, self).__init__()


class Report(object):
    def __init__(self, definition, 
            output_name=None, output_directory=None):

        self.result = None
        self.globals = None
        self.parameters = None
        self.data_sources = {}
        self.data_sets = {}
        self.data_groups = {}
        self.data_interfaces = {}
        self.report_items_group = None
        self.current_data_scope = [None, None]
        self.current_data_interface = None
        self._style = OutcomeStyle(self)
        self._globals = {
                'Author': None,
                'Description': None,
                'Version': None,
                'PageNumber': -1,
                'TotalPages': -1,
                'ExecutionTime': None,
                'ReportServerUrl': None,
                'ReportName': None,
                'ReportFolder': None,
                'ReportFile': None,
                'ReportFileName': None,
                'OutputDirectory': None,
                'OutputName': None,
                }

        # The ReportDef object
        self.definition = self._parse(
            definition, output_name, output_directory)

        self.modules = ExpressionEval(self)
        self.modules.load_modules(self.definition.get_element("Modules"))

    def run(self, parameters={}):
        if not self.definition:
            logger.critical("No definition found in report.", True)
    
        logger.info("Running Report '{0}'".format(self.definition.Name))
    
        logger.info('Running Globals...')
        self._get_globals()

        logger.info('Running Parameters...')
        self._get_parameters(parameters)

        logger.info('Running DataSources...')
        self.data_sources = {}
        self.data_sources = self._get_data_sources()

        logger.info('Running DataSets...')
        self.data_sets = {}
        self.data_groups = {}
        self.data_sets = self._get_data_sets()

        logger.info('Building result...')
        self.result = Result(self)

    def save(self, overwrite, apply_filters=False):
        # TODO if apply_filters=True report is saved with filters applied.
        '''
        Append dataset records (without filtering) to definition
        and saves it in a new file with .nuntiare extension.
        ''' 
        def _add_element(doc, parent, element_name, text=None):
            el = doc.createElement(element_name)
            if text != None:
                text_el = doc.createTextNode(text)
                el.appendChild(text_el)
            parent.appendChild(el)
            return el

        def _get_element(doc, node, base_element):
            for n in node.childNodes:
                if n.nodeName in ('#comment') or n.nodeName.startswith("rd:"):
                    continue
                if n.nodeName in ('#text'):
                    if len(n.parentNode.childNodes) == 1:
                        text = doc.createTextNode(n.nodeValue)
                        base_element.appendChild(text)
                    continue

                el = _add_element(doc, base_element, n.nodeName)
                _get_element(doc, n, el)

        def _data_to_string(data_type, value):
            v = DataType.get_value(data_type, value)
            if v != None:
                if data_type == "DateTime":
                    return "{:%Y-%m-%d %H:%M:%S}".format(v)
                else:
                    return str(v)

        def _add_data(doc, root_element):
            data_root  = _add_element(doc, root_element, "DataEmbedded")
            for key, ds in self.data_sets.items():
                data = _add_element(doc, data_root, "Data")
                _add_element(doc, data, "Name", key)
                records = _add_element(doc, data, "Records")
                for rw in ds.data.original_rows:
                    record = _add_element(doc, records, "Record")
                    i = 0
                    for c in ds.data.field_list:
                        if c.data_field:
                            _add_element(
                                doc, record, c.data_field, 
                                _data_to_string(c.DataType, rw[i]))
                        i = i + 1

        result_file = os.path.join(self.globals['OutputDirectory'], 
                self.globals['OutputName'] + ".nuntiare")

        if not overwrite:
            if os.path.isfile(result_file):
                logger.error("File '{0}' already exists.".format(result_file),
                        True, "IOError")

        doc = minidom.Document()
        root_element = doc.createElement("Report")
        orig_root = self._get_root(doc = self._get_xml_document())

        _get_element(doc, orig_root, root_element)
        _add_data(doc, root_element)

        doc.appendChild(root_element)

        f = open(result_file, "wb")
        try:
            f.write(doc.toprettyxml(indent="  ", encoding="utf-8"))
        finally:
            f.close()        
        logger.info("Report '{0}' saved.".format(result_file))

    def get_value(self, element, element_name, default):
        return Expression.get_value_or_default(
                self, element, element_name, default)

    def get_style(self, element):
       el = element.get_element("Style")
       return self._style.get_style(el)

    def _parse(self, definition, output_name, output_directory):
        is_file = False
        if os.path.isfile(definition):
            if not os.access(definition, os.R_OK):
                logger.error(
                    "User has not read access for '{0}'.".format(definition),
                    True, "IOError")
            is_file = True

        root = self._get_root(self._get_xml_document(definition, is_file))
        report_def = ReportDef(root)

        self._globals['Author'] = report_def.Author
        self._globals['Description'] = report_def.Description
        self._globals['Version'] = report_def.Version
        self._globals['ReportName'] = report_def.Name

        if is_file:
            self._globals['ReportFile'] = definition
            self._globals['ReportFileName'] = os.path.basename(definition)
            self._globals['ReportFolder'] = os.path.dirname(os.path.realpath(definition))
            if not output_directory:
                output_directory = os.path.dirname(
                    os.path.realpath(definition))
            if not output_name:
                output_name = os.path.splitext(
                    self._globals['ReportFileName'])[0]
        else:
            self._globals['ReportFile'] = "From XML string."
            self._globals['ReportFileName'] = "From XML string."
            self._globals['ReportFolder'] = "From XML string."
            if not output_directory:
                output_directory = os.path.dirname(
                    os.path.realpath(__file__))
        if not os.path.isdir(output_directory):
            logger.error(
                "'{0}' is not a valid directory.".format(
                    output_directory), 
                True, "IOError")

        self._globals['OutputDirectory'] = output_directory
        self._globals['OutputName'] = output_name

        if not self._globals['OutputName']:
            self._globals['OutputName'] = self._globals['ReportName']

        return report_def

    def _get_xml_document(self, definition, is_file):
        doc = None
        try:
            if is_file:
                doc = minidom.parse(definition)
            else:
                doc = minidom.parseString(definition)
        except Exception as e:
            err_msg = '''Error getting xml dom from definition '{0}'.
Is it supposed to be a file?. Verify that it exists.
If it is a xml string, verify that it is well formed.
System error: {1}'''
            logger.critical(
                err_msg.format(definition, e.args), True)
        return doc

    def _get_root(self, doc):
        root = doc.getElementsByTagName('Nuntiare')
        if not root:
            logger.critical(
                "Xml root element 'Nuntiare' not found.", True)
        return root[0]

    def _get_globals(self):
        self.globals = Globals()
        self._globals['PageNumber'] = -1
        self._globals['TotalPages'] = -1
        self._globals['ExecutionTime'] = datetime.datetime.now()
        for key, value in self._globals.items():
            self.globals.add_item(CollectionItem(key))
            self.globals[key] = value
        
    def _get_parameters(self, parameters):
        self.parameters = Parameters()
        for p in self.definition.parameters_def:
            key = p.Name
            value = None
            if parameters:
                if key in parameters:
                    value = p.get_value(self, parameters[key])
                else:
                    value = p.get_default_value(self)
            else:
                value = p.get_default_value(self)
            self.parameters.add_item(CollectionItem(key))
            self.parameters[key] = value

        if parameters:
            # Just for logging ...
            for key, value in parameters.items():
                if not self.definition.get_parameter_def(key):
                    logger.warn("Unknown Parameter '{0}'. Ignored.".format(key))

    def _get_data_sources(self):
        result = {}
        for ds in self.definition.data_sources:
            result[ds.Name] = DataSourceObject(self, ds)
            result[ds.Name].connect()
        return result

    def _get_data_sets(self):
        data_sets = {}
        for ds in self.definition.data_sets:
            logger.info("  Running DataSet '{0}'".format(ds.Name))
            data_sets[ds.Name] = DataSetObject(self, ds)
            data_sets[ds.Name].execute()
        return data_sets

