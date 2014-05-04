# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import os
import datetime
from . import logger, __reports__
from .tools import raise_error_with_log, get_expression_value_or_default
from definition.expression import verify_expression_constant
from definition.link import Link
from definition.element import Element
from xml.dom.minidom import parse, parseString
from pages import get_pages, Pages

class Report(object):
    def __init__(self, report_file=None, string_xml=None, parameters=None, 
            output_name=None, output_directory=None, 
            over_write=True, compress=False):

        if (report_file==None and string_xml==None) or (report_file!=None and string_xml!=None):
            raise ValueError('Report must be initialized by a report file or by xml string.')

        logger.info('Initializing report...')

        self.definition=None

        self.report_file=None
        self.report_filename=None
        self.report_folder=None
        self.string_xml=None
        self.output_name=output_name
        self.output_directory=None
        self.over_write=over_write
        self.compress=compress

        self.globals={}      # page_number, total_pages, execution_time, report_folder, report_name 
        self.parameters_passed={}
        if parameters:
            self.parameters_passed=parameters
        self.parameters_obj=[]
        self.parameters={}
        self.data_sources={} 
        self.data_sets={}
        self.data_groups={}
        self.fields={}
        self.current_scope=None
        self.report_items={} # only textboxes

        if report_file:
            if not os.path.isfile(report_file):
                raise_error_with_log("'{0}' is not a valid file.".format(report_file))
            if not os.access(report_file, os.R_OK):
                raise_error_with_log("User has not read access for '{0}'.".format(report_file))
            self.report_file=report_file

            if not output_directory:
                output_directory = os.path.dirname(os.path.realpath(report_file))

            dom = parse(report_file)

            self.globals['report_file'] = os.path.basename(report_file)
            self.globals['report_folder'] = os.path.dirname(os.path.realpath(report_file))
        else:
            if not output_directory:
                output_directory = os.path.dirname(os.path.realpath(__file__))
            dom = parseString(string_xml)
            self.globals['From xml string']
            self.globals['From xml string']

        if not os.path.isdir(output_directory):
            raise_error_with_log("'{0}' is not a valid directory.".format(output_directory))
        self.output_directory=output_directory

        self.globals['report_name'] = ''

        report_node = dom.getElementsByTagName("Report")
        self.definition = Definition(report_node[0], self)
        self.run()

    def run(self):
        self.globals['page_number'] = -1
        self.globals['total_pages'] = -1
        self.globals['execution_time'] = datetime.datetime.now()
        logger.info('Execution time: {0}'.format(self.globals['execution_time']))

        # 1.- Set parameters values in declared order.
        for p in self.parameters_obj:
            key=p.parameter_name  
            if self.parameters_passed.has_key(key):
                p.set_value(self.parameters_passed[key])
            if self.parameters.has_key(key):
                raise_error_with_log("ReportParameter '{0}' already exists.".format(key))
            self.parameters[key] = p.value()
            print "Parameter [" + key + "]=" + str(self.parameters[key])
        self.parameters_obj = None

        # 2.- Build data_sources
        for key, obj in self.data_sources.items():
            obj.connect()

        # 3.- Build data_sets
        for key, obj in self.data_sets.items():
            obj.execute()

        # 5.- Build pages
        self.pages = Pages(self)      

    def get_element(self, name):
        return self.definition.get_element(name)


class Definition(Element):
    '''
    Get xml definition objects hierarchically
    '''

    def __init__(self, node, report):
        elements={'Name': [Element.STRING],
                  'Description': [Element.STRING],
                  'Author': [Element.STRING],
                  'AutoRefresh': [Element.INTEGER],
                  'DataSources': [Element.ELEMENT],
                  'DataSets': [Element.ELEMENT],
                  'Body': [Element.ELEMENT],
                  'ReportParameters': [Element.ELEMENT],
                  'Custom': [Element.ELEMENT],
                  'Width': [Element.SIZE],
                  'PageHeader': [Element.ELEMENT],
                  'PageFooter': [Element.ELEMENT],
                  'PageHeight': [Element.SIZE],
                  'PageWidth': [Element.SIZE],
                  'LeftMargin': [Element.SIZE],
                  'RightMargin': [Element.SIZE],
                  'TopMargin': [Element.SIZE],
                  'BottomMargin': [Element.SIZE],
                  'EmbeddedImages': [Element.ELEMENT],
                  'CodeModules': [Element.ELEMENT],
                 }

        lnk = Link(report, None, self)
        super(Definition, self).__init__(node, elements, lnk)

        if not self.get_element("Body"):
            raise_error_with_log("'Body' element is required by report definition.")

        name = verify_expression_constant("Name", "Report", self.get_element('Name'))
        self.name = name.value()
        report.globals['report_name'] = self.name
        if not report.output_name:
            report.output_name = self.name

