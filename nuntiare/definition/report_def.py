# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import os
from xml.dom.minidom import parse, parseString
from . element import Element, Link
from . expression import Expression
from .. import logger

class ReportDef(object):
    def __init__(self, report_file=None, string_xml=None, 
            output_name=None, output_directory=None):

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

        self.globals={}      # report_file, report_folder, report_name 
        self.parameters_def=[]
        self.data_sources=[] 
        self.data_sets=[]
        self.modules=[]
        self.report_items={} # only textboxes
        self.report_items_group={}

        if report_file:
            if not os.path.isfile(report_file):
                logger.error("'{0}' is not a valid file.".format(report_file), True)
            if not os.access(report_file, os.R_OK):
                logger.error("User has not read access for '{0}'.".format(report_file), True)
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

        logger.info(" File: {0}".format(self.globals['report_file']))
        logger.info(" Folder: {0}".format(self.globals['report_folder']))

        if not os.path.isdir(output_directory):
            logger.error("'{0}' is not a valid directory.".format(output_directory), True)
        self.output_directory=output_directory

        self.globals['report_name'] = ''

        report_node = dom.getElementsByTagName("Nuntiare")
        if not report_node:
            logger.error("Not a valid Nuntiare report definition file. " \
                "Verify 'Report' root element.", True)
        self.definition = Report(report_node[0], self)

    def get_element(self, name):
        return self.definition.get_element(name)


class Report(Element):
    '''
    Get xml definition objects hierarchically
    '''

    def __init__(self, node, report_def):
        elements={'Name': [Element.STRING,1,True],
                  'Description': [Element.STRING,0,True],
                  'Author': [Element.STRING,0,True],
                  'Version': [Element.STRING,0,True],
                  'DataSources': [],
                  'DataSets': [],
                  'Body': [Element.ELEMENT,1],
                  'ReportParameters': [],
                  'Variables': [], #TODO Should be only at group level, ex. Tablix? 
                  'Imports': [],
                  'EmbeddedImages': [],
                  'Page': [Element.ELEMENT,1],
                 }

        lnk = Link(report_def, None, self)
        super(Report, self).__init__(node, elements, lnk)
        report_def.globals['report_name'] = Expression.get_value_or_default(None,self,"Name", None)
        logger.info("Report name: {0}".format(report_def.globals['report_name']))
        if not report_def.output_name:
            report_def.output_name = report_def.globals['report_name']

