# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import uuid
from nuntiare import logger, __reports__
from nuntiare.tools import raise_error_with_log
from definition.link import Link
from definition.element import Element
from xml.dom.minidom import parse, parseString
from pages import get_pages

class Report(object):
    def __init__(self, report_file=None, string_xml=None, parameters=None):
        if (report_file==None and string_xml==None) or (report_file!=None and string_xml!=None):
            raise ValueError('Report must be initialized by a report file or by xml string.')

        logger.info('Initializing report...')

        self.definition=None

        # Global Colections
        self.globals={}      # page_number, total_pages, execution_time, report_folder, report_name 
        self.user={}         # user_id, language
        self.parameters={}
        self.data_sources={} # Only data sources and data sets used in the body of the report will be included in 
                             # the DataSources and DataSets collections. Data sets and data sources used only 
                             # in parameter valid values and default values properties will not be included.
        self.data_sets={}    # for each data_set, there is a fields collection
        self.report_items={} # only textboxes
        self.code_modules={} # python modules

        if report_file:
            dom = parse(report_file)
        else:
            dom = parseString(string_xml)

        report_node = dom.getElementsByTagName("Report")
        self.definition = Definition(report_node[0], self)

        self.id = uuid.uuid4()                               # Sirve de algo?
        __reports__[self.id] = self # cached at module level #

        self.run(parameters) 

    def run(self, parameters):
        self.globals={}
        self.globals['page_number'] = 0
        self.globals['total_pages'] = 0
        #self.globals['execution_time']= TODO add now()

        # 1.- Build data_sources
        if self.data_sources:
            for d in self.data_sources:
                d.connect()

            # 2.- Build data_sets in parameters
            for d in self.data_sets:
                d.get_data(self.data_sources)

            # 3.- Build parameters that depends on data_sets
            #for p in self.parameters:
            #    p.get_parameter(self.data_sets)

            # 4.- Accomodate data (Grouping, sorting, filtering, etc...)

        # 5.- Build pages
        self.pages = get_pages(self) # Return a collection of page() objects

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
                  'Language': [Element.LANGUAGE],
                  'CodeModules': [Element.ELEMENT],
                 }

        lnk = Link(report, None, self)
        super(Definition, self).__init__(node, elements, lnk)

        if not self.get_element("Body"):
            raise_error_with_log("'Body' element is required by report definition.")

   

