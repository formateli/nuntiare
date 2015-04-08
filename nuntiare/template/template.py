# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from . element import Element, Link
from . expression import Expression
from .. import logger

class Template(object):
    def __init__(self, root_node):

        logger.info('Initializing template definition...')

        self.definition=None
        self.globals={
                'author': None,
                'description': None,
                'version': None,
                'report_name': None,
                }
        self.parameters_def = []
        self.data_sources = []
        self.data_sets = []
        self.modules = []
        self.report_items = {} # only textboxes
        self.report_items_group = {}

        self.definition = Report(root_node, self)

    def get_element(self, name):
        return self.definition.get_element(name)

    def has_element(self, name):
        return self.definition.has_element(name)
        
    def get_parameter_def(self, parameter_name):
        for p in self.parameters_def:
            if p.parameter_name ==  parameter_name:
                return p


class Report(Element):
    '''
    Get xml definition objects hierarchically
    '''

    def __init__(self, node, template):
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

        lnk = Link(template, None, self)
        super(Report, self).__init__(node, elements, lnk)
        template.globals['report_name'] = Expression.get_value_or_default(None,self,"Name", None)
        template.globals['author'] = Expression.get_value_or_default(None,self,"Author", None)
        template.globals['description'] = Expression.get_value_or_default(None,self,"Description", None)
        template.globals['version'] = Expression.get_value_or_default(None,self,"Version", None)
        
