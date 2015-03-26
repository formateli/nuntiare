# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.


from .. import logger
from .. tools import get_xml_tag_value
from .. template.data_type import DataType

class Outcome(object):
    def __init__(self, root_node):

        logger.info('Initializing outcome definition...')

        self.definition=None

        self.globals={
                'author': None,
                'description': None,
                'version': None,
                'report_name':None,
            }
        
        self.parameters_def=[]
        self.data_sources=[] 
        self.data_sets=[]
        self.modules=[]
        self.report_items={} # only textboxes
        self.report_items_group={}

        self.definition = Report(root_node)

    def get_element(self, name):
        return self.definition.get_element(name)

    def has_element(self, name):
        return self.definition.has_element(name)


class _OutcomeElement(object):
    def __init__(self, node, elements, parent):
        super(_OutcomeElement, self).__init__()

        self.parent=parent
        self.element_list={}
        self.element_name = self.__class__.__name__

        for n in node.childNodes:
            if not n.nodeName in elements:
                if n.nodeName not in ('#text', '#comment'):
                    logger.warn("Unknown xml element '{0}' for '{1}'. Ignored.".format(
                            n.nodeName, self.element_name))
                continue
            
            if elements[n.nodeName] == "Element":
                if n.nodeName=="Globals":
                    self.element_list[n.nodeName]=Globals(n, self)
                elif n.nodeName=="Page":
                    self.element_list[n.nodeName]=Page(n, self)
                elif n.nodeName=="Styles":
                    self.element_list[n.nodeName]=Styles(n, self)
                elif n.nodeName=="Style":
                    self.element_list[n.nodeName]=Style(n, self)
            else:
                self.element_list[n.nodeName]=ElementValue(n, elements[n.nodeName])

    def get_element(self, name):
        if name in self.element_list:
            return self.element_list[name]

    def has_element(self, name):
        el = self.get_element(name)
        if el:
            return True
        return False


class ElementValue(object):
    def __init__(self, node, type):
        super(ElementValue, self).__init__()
        self.value=self._set_value(node, type)
        
    def _set_value(self, node, type):
        str_value=get_xml_tag_value(node)
        return DataType.get_value(type, str_value)
        

class Report(_OutcomeElement):
    def __init__(self, node):
        elements={'Name': "String",
                  'Description': "String",
                  'Author': "String",
                  'Version': "String",
                  'Body': "Element",
                  'Globals': "Element",
                  'ReportParameters': "Element",
                  'Imports': "Element",
                  'EmbeddedImages': "Element",
                  'Page': "Element",
                 }

        super(Report, self).__init__(node, elements, None)


class Page(_OutcomeElement):
    def __init__(self, node, parent):
        elements={'PageHeight': "Float",
                  'PageWidth': "Float",
                  'TopMargin': "Float",
                  'BottomMargin': "Float",
                  'RightMargin': "Float",
                  'LeftMargin': "Float",                  
                  'Columns': "Integer",
                  'ColumnSpacing': "Float",
                  'StyleId': "Element",
                 }

        super(Page, self).__init__(node, elements, parent)
        

class Globals(_OutcomeElement):
    def __init__(self, node, parent):
        elements={'report_name': "String",
                  'author': "String",
                  'description': "String",
                  'version': "String",
                 }

        super(Globals, self).__init__(node, elements, parent)


class Styles(_OutcomeElement):
    def __init__(self, node, parent):
        elements={'Style': "Element",}
        self.style_list=[]
        super(Styles, self).__init__(node, elements, parent)


class Style(_OutcomeElement):
    def __init__(self, node, parent):
        elements={'Id': "Integer",
                  'BackgroundColor': "String",
                 }
        super(Style, self).__init__(node, elements, parent)
        self.parent.style_list.append(self)
        
