# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import os
from xml.dom.minidom import parse, parseString
from link import Link
from types.element import Element
from .. import logger
from ..tools import raise_error_with_log

class ReportDef(object):
    def __init__(self, report_file=None, string_xml=None, 
            output_name=None, output_directory=None, 
            over_write=True, compress=False):

        if (report_file==None and string_xml==None) or (report_file!=None and string_xml!=None):
            raise ValueError('Report must be initialized by a report file or by xml string.')

        logger.info('Initializing report definition...')

        self.definition=None
                  
        self.report_file=None
        self.report_filename=None
        self.report_folder=None
        self.string_xml=None
        self.output_name=output_name
        self.output_directory=None
        self.over_write=over_write
        self.compress=compress

        self.globals={}      # report_file, report_folder, report_name 
        self.parameters_def=[]
        self.data_sources=[] 
        self.data_sets=[]
        self.modules=[]
        self.report_items={} # only textboxes
        self.report_items_group={}

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
            self.globals['report_file'] = "From XML string."
            self.globals['report_folder'] = "From XML string."

        if not os.path.isdir(output_directory):
            raise_error_with_log("'{0}' is not a valid directory.".format(output_directory))
        self.output_directory=output_directory

        self.globals['report_name'] = ''

        report_node = dom.getElementsByTagName("Report")
        self.definition = Definition(report_node[0], self)

    def get_element(self, name):
        return self.definition.get_element(name)


class Definition(Element):
    '''
    Get xml definition objects hierarchically
    '''

    def __init__(self, node, report_def):
        elements={'Name': [Element.STRING, True],
                  'Description': [Element.STRING, True],
                  'Author': [Element.STRING, True],
                  'AutoRefresh': [Element.INTEGER, True],
                  'DataSources': [Element.ELEMENT],
                  'DataSets': [Element.ELEMENT],
                  'Body': [Element.ELEMENT],
                  'ReportParameters': [Element.ELEMENT],
                  'Width': [Element.SIZE, True],
                  'Imports': [Element.ELEMENT],                  
                  'EmbeddedImages': [Element.ELEMENT],
                  'Page': [Element.ELEMENT],
                  'DataElementStyle': [Element.ENUM],                  
                 }

        lnk = Link(report_def, None, self)
        super(Definition, self).__init__(node, elements, lnk)

        if not self.get_element("Body"):
            raise_error_with_log("'Body' element is required by report definition.")

        self.name = self.get_element('Name').value(None)
        report_def.globals['report_name'] = self.name
        if not report_def.output_name:
            report_def.output_name = self.name

