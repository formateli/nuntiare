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
        self.globals = {
                'author': None,
                'description': None,
                'version': None,
                'report_name':None,
                }
        self.parameters_def=[]
        self.data_sources=[] 
        self.data_sets=[]
        self.modules=[]
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
                elif n.nodeName=="PageHeader":
                    self.element_list[n.nodeName]=PageHeader(n, self)
                elif n.nodeName=="PageFooter":
                    self.element_list[n.nodeName]=PageFooter(n, self)
                elif n.nodeName=="ReportParameters":
                    self.element_list[n.nodeName]=ReportParameters(n, self)
                elif n.nodeName=="ReportParameter":
                    self.element_list[n.nodeName]=ReportParameter(n, self)
                elif n.nodeName=="Styles":
                    self.element_list[n.nodeName]=Styles(n, self)
                elif n.nodeName=="Style":
                    self.element_list[n.nodeName]=Style(n, self)
                elif n.nodeName=="TopBorder":
                    self.element_list[n.nodeName]=Border(n, self)
                elif n.nodeName=="BottomBorder":
                    self.element_list[n.nodeName]=Border(n, self)
                elif n.nodeName=="LeftBorder":
                    self.element_list[n.nodeName]=Border(n, self)
                elif n.nodeName=="RightBorder":
                    self.element_list[n.nodeName]=Border(n, self)                                                            
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
                  'Styles': "Element",
                 }

        super(Report, self).__init__(node, elements, None)
        

class Globals(_OutcomeElement):
    def __init__(self, node, parent):
        elements={'report_name': "String",
                  'author': "String",
                  'description': "String",
                  'version': "String",
                 }

        super(Globals, self).__init__(node, elements, parent)


class ReportParameters(_OutcomeElement):
    def __init__(self, node, parent):
        elements={'ReportParameter': "Element",}
        self.parameter_list=[]
        super(ReportParameters, self).__init__(node, elements, parent)


class ReportParameter(_OutcomeElement):
    def __init__(self, node, parent):
        elements = {'Name': 'String',
                    'DataType': 'String',
                    'Value': None
                   }
        super(ReportParameter, self).__init__(node, elements, parent)
        self.parent.parameter_list.append(self)

    def value(self):
        v = self.get_element("Value")
        t = self.get_element("DataType")
        datatype = None
        if t:
            datatype = t.value
        return DataType.get_value(datatype, v.value)


class Page(_OutcomeElement):
    def __init__(self, node, parent):
        elements={'PageHeader': "Element",
                  'PageFooter': "Element",
                  'PageHeight': "Float",
                  'PageWidth': "Float",
                  'TopMargin': "Float",
                  'BottomMargin': "Float",
                  'RightMargin': "Float",
                  'LeftMargin': "Float",                  
                  'Columns': "Integer",
                  'ColumnSpacing': "Float",
                  'StyleId': "Integer",
                 }

        super(Page, self).__init__(node, elements, parent)


class _PageSection(_OutcomeElement):
    def __init__(self, node, parent):
        elements={'ReportItems': "Element",
                  'Height': "Float", 
                  'PrintOnFirstPage': "Boolean",
                  'PrintOnLastPage': "Boolean",
                  'StyleId': "Integer",
                  'ReportItems': "Element",
                 }
        super(_PageSection, self).__init__(node, elements, parent)
        

class PageHeader(_PageSection):
    def __init__(self, node, parent):
        super(PageHeader, self).__init__(node, parent)


class PageFooter(_PageSection):
    def __init__(self, node, parent):
        super(PageFooter, self).__init__(node, parent)


class Styles(_OutcomeElement):
    def __init__(self, node, parent):
        elements={'Style': "Element",}
        self.style_list={}
        super(Styles, self).__init__(node, elements, parent)
        

class Style(_OutcomeElement):
    def __init__(self, node, parent):
        elements={'Id': "Integer",
                  'TopBorder': "Element",
                  'BottomBorder': "Element",
                  'LeftBorder': "Element",
                  'RightBorder': "Element",
                  'BackgroundColor': "String",
                  'BackgroundGradientType': "String",
                  'BackgroundGradientEndColor': "String",
                  'BackgroundImage': "Element",
                  'FontStyle': "String",
                  'FontFamily': "String",
                  'FontSize': "Float",
                  'FontWeight': "String",
                  'Format': "String",
                  'TextDecoration': "String",
                  'TextAlign': "String",
                  'VerticalAlign': "String",
                  'Color': "String",
                  'PaddingLeft': "Float",
                  'PaddingRight': "Float",
                  'PaddingTop': "Float",
                  'PaddingBottom': "Float",
                  'LineHeight': "Float",
                  'Direction': "String",
                  'WritingMode': "String",
                 }
        super(Style, self).__init__(node, elements, parent)
        style_id = self.get_element("Id").value
        self.parent.style_list[style_id] = self


class Border(_OutcomeElement):
    def __init__(self, node, parent):
        elements={'Color': "String",
                  'BorderStyle': "String",
                  'Width': "Float",
                 }
        super(Border, self).__init__(node, elements, parent)

