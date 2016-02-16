# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import copy
from . expression import Expression, String, Boolean, \
        Integer, Variant, Size, Color
from . enum import BorderStyle, FontStyle, FontWeight, TextDecoration, \
        TextAlign, VerticalAlign, TextDirection, WritingMode, \
        BackgroundRepeat, BackgroundGradientType, \
        DataType, SortDirection, Operator, BreakLocation
from .. import logger
from .. data.data_type import DataType as dt
from .. tools import get_xml_tag_value

class Element(object):
    ELEMENT = 0
    STRING = 1
    INTEGER = 2
    BOOLEAN = 3
    FLOAT = 4
    SIZE = 5
    DATE = 6
    COLOR = 7
    EXPRESSION = 8
    EXPRESSION_LIST = 9
    URL = 10
    ENUM = 11
    VARIANT = 90

    def __init__(self, node, elements, lnk):
        '''
        node: Xml node with the element definition.
        elements: A dictionary with the elements belonging to this element.
         key: Element name
         value: A list [] with the following values:
            Element type. Default value: Element.ELEMENT
            Card: Values can be: 0 (0 to 1), 1 (1), 2 (1 to N), 3 (0 to N). Default value: 0
            Must be a constant: If true, this element value can not be an expression.
                Ignore if type is Element.ELEMENT. Default value: False
            DefaultValue
                Ignore if type is Element.ELEMENT. Default value: False
        lnk: The linking object
        '''
        
        super(Element, self).__init__()
        
        self._original_element_list = elements

        self.element_list={}    # Here we list elements found for this element
        lnk.obj = self
        self.lnk = lnk          # This is the linking object. See link.py
        
        self.element_name = self.__class__.__name__
        self.expression_list={}
        self.non_expression_list={}

        # Collect all report items, at the end, order by ZIndex or appears order
        items_by_name={}
        z_count = 0

        for n in node.childNodes:
            if not n.nodeName in elements:
                if n.nodeName == "DataEmbedded" and \
                        n.parentNode.nodeName == "Report":
                    self.set_data()
                    continue
                if n.nodeName not in ('#text', '#comment'):
                    logger.warn("Unknown xml element '{0}' for '{1}'. Ignored.".format(
                            n.nodeName, lnk.obj.__class__.__name__))
                continue
            
            element_type, card, must_be_constant, default_value = Element.get_element_def(
                            elements[n.nodeName], n.nodeName)

            elements[n.nodeName] = [element_type, card, must_be_constant, default_value, True]
                
            if element_type == Element.ELEMENT:
                el = Element.element_factory(n.nodeName, n, lnk)
                if n.nodeName in ("Line", "Rectangle", "Textbox", "Image", "Subreport",
                            "CustomReportItem", "Tablix"):
                    if n.nodeName in ("Textbox"): 
                        if el.Name in lnk.report_def.report_items:
                            logger.error(
                                "Report already has a Texbox with name '{0}'".format(
                                    el.Name), True)
                        lnk.report_def.report_items[el.Name] = el
                    if el.Name in items_by_name:
                        logger.error(
                            "The container already has a report item with name '{0}'".format(
                                el.Name), True)
                    i = el.ZIndex if el.ZIndex > -1 else z_count
                    items_by_name[el.Name]=[el, i]
                    z_count = z_count + 1
                self.element_list[n.nodeName] = el
                self.non_expression_list[n.nodeName] = self.element_list[n.nodeName]
            elif element_type == Element.EXPRESSION_LIST:
                self.element_list[n.nodeName]=Element.expression_list_factory(
                        n.nodeName, n, lnk)
                self.non_expression_list[n.nodeName] = self.element_list[n.nodeName]                
            elif element_type == Element.ENUM:
                self.element_list[n.nodeName]=Element.enum_factory(
                        n.nodeName, n, lnk, card, must_be_constant)
                self.expression_list[n.nodeName] = self.element_list[n.nodeName]
                self._set_attr(n.nodeName, False, default_value, must_be_constant)
            else: 
                self.element_list[n.nodeName]=Element.expression_factory(
                        elements[n.nodeName][0], n, lnk, card, must_be_constant)
                self.expression_list[n.nodeName] = self.element_list[n.nodeName]
                self._set_attr(n.nodeName, False, default_value, must_be_constant)


        # Validate elements not used
        for key, el in elements.items():
            if len(el) < 5: # Not verified in the node loop above
                element_type, card, must_be_constant, default_value = Element.get_element_def(
                            el, key)
                if card in [1, 2]:
                    logger.error("'{0}' must be defined for '{1}'.".format(key, 
                            lnk.obj.__class__.__name__), True)

        # Z Order
        reportitems_list = []
        if len(items_by_name) > 0:
            z_list=[]
            for key, it in items_by_name.items():
                l = (it[1], it[0]) # zindex, reportitem
                z_list.append(l)
            res = sorted(z_list, key=lambda z: z[0])
            for r in res:
                reportitems_list.append(r[1])
    
    def _set_attr(self, name, is_element, value, must_be_constant):
        if is_element:
            self.__setattr__(name, value)
        else:
            if must_be_constant:
                self.__setattr__(
                    name, Expression.get_value_or_default(
                        None, self, name, value))

    def __getattr__(self, name):
        self._verify_element(name)
        result = Element.get_element_def(
                    self._original_element_list[name], name)
            
        if result[0] in (Element.ELEMENT, Element.EXPRESSION_LIST, Element.URL):
            el = self.get_element(name)
            if el:
                self._set_attr(name, True, el, False)
                return self.__dict__[name]
        else:
            if not result[2]:
                logger.error(
                    "'{0}' is not a constant property for element '{1}'. Use get_value() instead.".format(
                        name, self.element_name), True)
            else:
                self._set_attr(name, False, result[3], result[2])
                return self.__dict__[name]

    def get_value(self, report, name, default_value=None):
        self._verify_element(name)
        return Expression.get_value_or_default(
            report, self, name, default_value)

    def _verify_element(self, name):
        if not name in self._original_element_list.keys():
            logger.error(
                "'{0}' is not a valid member for element '{1}'. Valid values are: {2}".format(
                    name, self.element_name, self._original_element_list.keys()), True)

    @staticmethod
    def extend_element_list(_class, additional_elements):
        el = {}
        for key, value in _class.elements.items():
            el[key] = value
        if additional_elements:
            for key, value in additional_elements.items():
                el[key] = value
        return el

    @staticmethod
    def element_factory(name, node, lnk):
        ln = Link(lnk.report_def, lnk.obj)
        if name=='Page':
            obj = Page(node, ln)
        elif name=='PageHeader':
            obj = PageHeader(node, ln)
        elif name=='PageFooter':
           obj = PageFooter(node, ln)
        elif name=='Body':
            obj = Body(node, ln)
        elif name=='Visibility':
            obj = Visibility(node, ln)
        elif name=='DataSources':
            obj = DataSources(node, ln)
        elif name=='DataSource':
            obj = DataSource(node, ln)
        elif name=='ConnectionProperties':
            obj = ConnectionProperties(node, ln)
        elif name=='DataSets':
            obj = DataSets(node, ln)
        elif name=='DataSet':
            obj = DataSet(node, ln)
        elif name=='Fields':
            obj = Fields(node, ln)
        elif name=='Field':
            obj = Field(node, ln)
        elif name=='Query':
            obj = Query(node, ln)
        elif name=='QueryParameters':
            obj = QueryParameters(node, ln)
        elif name=='QueryParameter':
            obj = QueryParameter(node, ln)
        elif name=='SortExpressions':
            obj = SortExpressions(node, ln)
        elif name=='SortExpression':
            obj = SortExpression(node, ln)
        elif name=='Filters':
            obj = Filters(node, ln)
        elif name=='Filter':
            obj = Filter(node, ln)
        elif name=='Group':
            obj = Group(node, ln)
        elif name=='ReportParameters':
            obj = ReportParameters(node, ln)
        elif name=='ReportParameter':
            obj = ReportParameter(node, ln)
        elif name=='ReportItems':
            obj = ReportItems(node, ln)
        elif name=='Tablix':
            obj = Tablix(node, ln)
        elif name=='TablixColumnHierarchy':
            obj = TablixColumnHierarchy(node, ln)
        elif name=='TablixRowHierarchy':
            obj = TablixRowHierarchy(node, ln)
        elif name=='TablixMembers':
            obj = TablixMembers(node, ln)
        elif name=='TablixMember':
            obj = TablixMember(node, ln)
        elif name=='TablixBody':
            obj = TablixBody(node, ln)
        elif name=='TablixHeader':
            obj = TablixHeader(node, ln)            
        elif name=='TablixColumns':
            obj = TablixColumns(node, ln)
        elif name=='TablixColumn':
            obj = TablixColumn(node, ln)
        elif name=='TablixRows':
            obj = TablixRows(node, ln)
        elif name=='TablixRow':
            obj = TablixRow(node, ln)
        elif name=='TablixCells':
            obj = TablixCells(node, ln)
        elif name=='TablixCell':
            obj = TablixCell(node, ln)
        elif name=='CellContents':
            obj = CellContents(node, ln)        
        elif name=='Style':
            obj = Style(node, ln)
        elif name=='Border':
            obj = Border(node, ln)
        elif name=='TopBorder':
            obj = Border(node, ln)
        elif name=='BottomBorder':
            obj = Border(node, ln)
        elif name=='LeftBorder':
            obj = Border(node, ln)
        elif name=='RightBorder':
            obj = Border(node, ln)
        elif name=='BackgroundImage':
            obj = BackgroundImage(node, ln)        
        elif name=='Line':
            obj = Line(node, ln)
        elif name=='Rectangle':
            obj = Rectangle(node, ln)
        elif name=='Textbox':
            obj = Textbox(node, ln)
        elif name=='PageBreak':
            obj = PageBreak(node, ln)            
    #    elif name=='Image':
    #        obj = Image(node, ln)
        elif name=='Modules':
            obj = Modules(node, ln)
        elif name=='Module':
            obj = Module(node, ln)
        else:
            logger.error("Element '{0}' not implemented.".format(name), True)

        return obj
    
    
    @staticmethod
    def enum_factory(name, node, lnk, card, must_be_constant):
        value = get_xml_tag_value(node)
        if card==1 and value==None:
            logger.error("'{0}' is required for '{1}'.".format(
                    node.nodeName,
                    lnk.obj.__class__.__name__), True)
     
        if name=='BorderStyle':
            return BorderStyle(value, lnk, must_be_constant)
        if name=='FontStyle':
            return FontStyle(value, lnk, must_be_constant)
        if name=='FontWeight':
            return FontWeight(value, lnk, must_be_constant)
        if name=='TextDecoration':
            return TextDecoration(value, lnk, must_be_constant)
        if name=='TextAlign':
            return TextAlign(value, lnk, must_be_constant)
        if name=='VerticalAlign':
            return VerticalAlign(value, lnk, must_be_constant)
        if name=='TextDirection':
            return TextDirection(value, lnk, must_be_constant)
        if name=='WritingMode':
            return WritingMode(value, lnk, must_be_constant)
        if name=='BackgroundRepeat':
            return BackgroundRepeat(value, lnk, must_be_constant)
        if name=='BackgroundGradientType':
            return BackgroundGradientType(value, lnk, must_be_constant)
        if name=='DataType':
            return DataType(value, lnk, must_be_constant)
        if name=='SortDirection':
            return SortDirection(value, lnk, must_be_constant)
        if name=='Operator':
            return Operator(value, lnk, must_be_constant)
        if name=='BreakLocation':
            return BreakLocation(value, lnk, must_be_constant)

        logger.error("Enum '{0}' not implemented.".format(name), True)
    
    @staticmethod
    def expression_factory(name, node, lnk, card, must_be_constant):
        ln = Link(lnk.report_def, lnk.obj, data=node.nodeName)
        value = get_xml_tag_value(node)
        if card == 1 and value == None:
            logger.error("'{0}' is required for '{1}'.".format(
                    node.nodeName, lnk.obj.__class__.__name__), True)

        if name==Element.STRING:
            return String(value, ln, must_be_constant)
        if name==Element.INTEGER:
            return Integer(value, ln, must_be_constant)
        if name==Element.BOOLEAN:
            return Boolean(value, ln, must_be_constant)
        if name==Element.SIZE:
            return Size(value, ln, must_be_constant)        
        if name==Element.COLOR:
            return Color(value, ln, must_be_constant)
        if name==Element.URL:
            return None
        if name==Element.VARIANT:
            return Variant(value, ln, must_be_constant)
     
        logger.error("Unknown expression element definition: '{0}'.".format(name), True)

    @staticmethod
    def expression_list_factory(name, node, lnk):
        ln = Link(lnk.report_def, lnk.obj)
        if name=='FilterValues':
            obj = FilterValues(node, ln)
        elif name=='GroupExpressions':
            obj = GroupExpressions(node, ln)
        else:
            logger.error("Unknown Element: '{0}' for ExpressionList".format(name), True)

        return obj

    @staticmethod
    def get_element_def(element, class_name):
        element_type = Element.ELEMENT
        card = 0
        must_be_constant = False
        default_value = None

        if len(element) > 0:
            if element[0]:
                element_type = element[0]
            if len(element) >= 2:
                if element[1]:
                    card = element[1]
            if len(element) >= 3:
                if element[2]:
                    must_be_constant = element[2]
            if len(element) >= 4:
                if element[3]:
                    default_value = element[3]

            # len(element)==4 is ignored, it means that element was checked
            if len(element) > 5:
                logger.error(
                    "Invalid number of values for element. Class: '{0}'".format(class_name), True)

        return element_type, card, must_be_constant, default_value
        
    def get_element(self, name):
        if name in self.element_list:
            return self.element_list[name]

    def has_element(self, name):
        el = self.get_element(name)
        if el:
            return True
        return False


class Link(object):
    def __init__(self, report_def, parent, obj=None, data=None):
        self.report_def = report_def  # Main Report() object where some collections are stored
        self.parent = parent          # Parent element
        self.obj = obj                # object itself. It is used to assign parent to others
        self.data = data              # optional extra data
        if not parent:
            self.report_def = obj


class _ExpressionList(object):
    def __init__(self, node, elements, lnk):

        if len(elements) == 0 or len(elements) > 1:
            logger.error("ElementList only can have one sub element type.", True)

        lnk.obj=self
        self.lnk=lnk
        self.expression_list=[]

        for n in node.childNodes:
            if not n.nodeName in elements:
                if n.nodeName not in ('#text', '#comment'):
                    logger.warn("Unknown xml element '{0}' for '{1}'. Ignored.".format(n.nodeName, lnk.obj.__class__.__name__))
                continue
                
            element_type, card, must_be_constant, default_value = Element.get_element_def(elements[n.nodeName],
                        lnk.obj.__class__.__name__)
                
            ex = Element.expression_factory(
                elements[n.nodeName][0], n, lnk, card, must_be_constant) 
            self.expression_list.append(ex)


###########################
###########################


class Report(Element):
    '''
    Root definition element
    '''
    class Data():
        def __init__(self):
            self._loaded = False
            self.data = {}
            
        def load(self, report):
            if self._loaded:
                return
            logger.info("Getting data from 'DataEmbedded'")
            # Loads the Data emmeded in definition file
            self._curr_data_name = None
            self._curr_index = 0
            doc = report._get_xml_document()
            root = report._get_root(doc)
            data = doc.getElementsByTagName("DataEmbedded")
            self._get_data(doc, data[0])            
            self._loaded = True

        def get_data(self, data_name):
            if data_name in self.data.keys():
                return self.data[data_name]
            logger.warn(
                "Attempted to get data '{0}' form DataEmbedded, but it does not exist".format(data_name))

        def reset(self):
            self.data = {}
            
        def _get_data(self, doc, node):
            for n in node.childNodes:
                if n.nodeName in ('#comment'):
                    continue
                if n.nodeName == "Record" and n.parentNode.nodeName == "Records":
                    self._curr_index = self._curr_index + 1
                if n.nodeName in ('#text'):
                    if len(n.parentNode.childNodes) == 1:
                        if n.parentNode.nodeName == "Name" and \
                                n.parentNode.parentNode.nodeName == "Data":
                            self._curr_data_name = n.nodeValue
                            self.data[self._curr_data_name] = [[], []]
                            self._curr_index = -1
                            continue
                        if n.parentNode.parentNode.nodeName == "Record" and \
                                n.parentNode.parentNode.parentNode.nodeName == "Records":
                            if not n.parentNode.nodeName in \
                                    self.data[self._curr_data_name][0]:
                                # append to columns
                                self.data[self._curr_data_name][0].append(n.parentNode.nodeName)
                            
                            if len(self.data[self._curr_data_name][1]) == self._curr_index:
                                self.data[self._curr_data_name][1].append([])
                            self.data[self._curr_data_name][1][self._curr_index].append(n.nodeValue)

                self._get_data(doc, n)

    elements={'Name': [Element.STRING,1,True],
              'Description': [Element.STRING,0,True],
              'Author': [Element.STRING,0,True],
              'Version': [Element.STRING,0,True],
              'DataSources': [],
              'DataSets': [],
              'Body': [Element.ELEMENT,1],
              'ReportParameters': [],
              'Modules': [],
              'EmbeddedImages': [],
              'Page': [Element.ELEMENT,1],
             }

    def __init__(self, node):
        logger.info('Initializing report definition...')

        self.parameters_def = []
        self.data_sources = []
        self.data_sets = []
        self.modules = []
        self.report_items = {} # only textboxes
        self.report_items_group = {}
        self.data = None

        lnk = Link(None, None, self)
        super(Report, self).__init__(node, self.elements, lnk)

    def get_parameter_def(self, parameter_name):
        for p in self.parameters_def:
            if p.Name ==  parameter_name:
                return p

    def set_data (self):
        self.data = Report.Data()


class Modules(Element):
    elements={'Module': [Element.ELEMENT,2],}
    def __init__(self, node, lnk):
        self.modules=[]
        super(Modules, self).__init__(node, self.elements, lnk)


class Module(Element):
    elements={'From': [Element.STRING,0,True],
              'Import': [Element.STRING,0,True],
              'As': [Element.STRING,0,True],
             }
    def __init__(self, node, lnk):
        super(Module, self).__init__(node, self.elements, lnk)
        lnk.parent.modules.append(self)

#------------------------------------------
#   ReportParameter
#------------------------------------------
class ReportParameters(Element):
    elements={'ReportParameter': [Element.ELEMENT,2],}
    def __init__(self, node, lnk):
        super(ReportParameters, self).__init__(node, self.elements, lnk)


class ReportParameter(Element):
    elements={'Name': [Element.STRING,1,True],
              'DataType': [Element.ENUM,1,True],
              'CanBeNone': [Element.BOOLEAN,0,True,True],
              'AllowBlank': [Element.BOOLEAN,0,True,True],
              'DefaultValue': [Element.VARIANT,1],
              'Promt': [Element.STRING],
             }
    def __init__(self, node, lnk):
        super(ReportParameter, self).__init__(node, self.elements, lnk)
        self._default_value = self.get_element('DefaultValue')
        self.lnk.report_def.parameters_def.append(self)

    def get_default_value(self, report):
        if self._default_value:
            return dt.get_value(
                self.DataType, self._default_value.value(report))

    def get_value(self, report, passed_value):
        if passed_value == None:
            result = self.get_default_value(report)
        else:
            result = dt.get_value(self.DataType, 
                    self._default_value.value(report, passed_value)) 

        if not result and not self.CanBeNone:
            logger.error("Parameter '{0}' value can not be 'None'".format(
                    self.Name), True)
        if result and result=="" and not self.AllowBlank and DataType=='String':
            logger.error("Parameter '{0}' value can not be an empty string.".format(
                    self.Name), True)

        return result


class Visibility(Element):
    '''
    The Visibility element indicates if the ReportItem should be shown in the rendered report. If no
    Visibility element is present, the item is unconditionally shown.
    
    Hidden:
    Indicates if the item should be hidden at first.    
        
    ToggleItem:
    The name of the text box used to hide/unhide this report
    item. Clicking on an instance of the ToggleItem will
    toggle the hidden state of every corresponding instance
    of this item. If the ToggleItem becomes hidden
    (because either the item or an ancestor is toggled or
    conditionally hidden), this item should become hidden.
    Must be a text box in the same group scope as this item
    or in any containing (ancestor) group scope.
    If omitted, no item will toggle the hidden state of this
    item.
    Not allowed on and cannot refer to report items
    contained in a page header or footer.
    Cannot refer to a report item contained in the current
    report item unless current group scope has a Parent.
    '''
    elements={'Hidden': [Element.BOOLEAN,0],
              'ToggleItem': [Element.STRING,0,True],
             }
    def __init__(self, node, lnk):
        super(Visibility, self).__init__(node, self.elements, lnk)


class Page(Element):
    '''
    The Page element contains page layout information for the report.
    '''
    elements={'PageHeader': [],
              'PageFooter': [],
              'PageHeight': [Element.SIZE,0,True],
              'PageWidth': [Element.SIZE,0,True],
              'LeftMargin': [Element.SIZE,0,True],
              'RightMargin': [Element.SIZE,0,True],
              'TopMargin': [Element.SIZE,0,True],
              'BottomMargin': [Element.SIZE,0,True],
              'Columns': [Element.INTEGER,0,True],
              'ColumnSpacing': [Element.SIZE,0,True],
              'Style': [],
             }
    def __init__(self, node, lnk):
        super(Page, self).__init__(node, self.elements, lnk)


#------------------------------------------
#   ReportElement
#------------------------------------------
class _ReportElement(Element):
    '''
    The virtual ReportElement element defines an element of a report. 
    The ReportElement element itself is not used. 
    Only the subtypes of ReportElement are used: Body, PageSection, ReportItem
    '''
    elements={'Style':[],}
    def __init__(self, node, additional_elements, lnk):    
        el = Element.extend_element_list(
                _ReportElement, additional_elements)
        super(_ReportElement, self).__init__(node, el, lnk)


class _PageSection(_ReportElement):
    '''
    The virtual PageSection element defines the layout of report items to appear at the top or bottom
    of every page of the report. The PageSection element itself is not used. Only subtypes of
    PageSection are used: PageHeader, PageFooter. It inherits from ReportElement.
    '''
    elements={'ReportItems': [],
              'Height': [Element.SIZE,1,True], 
              'PrintOnFirstPage': [Element.BOOLEAN,0,True],
              'PrintOnLastPage': [Element.BOOLEAN,0,True],
             }
    def __init__(self, node, lnk):
        super(_PageSection, self).__init__(node, self.elements, lnk)


class PageHeader(_PageSection):
    '''
    The PageFooter element defines the layout of report items to appear at the bottom of every page of
    the report. It has no properties beyond those it inherits from PageSection.
    '''
    def __init__(self, node, lnk):
        super(PageHeader, self).__init__(node, lnk)


class PageFooter(_PageSection):
    '''
    The PageFooter element defines the layout of report items to appear at the bottom of every page of
    the report. It has no properties beyond those it inherits from PageSection.
    '''
    def __init__(self, node, lnk):
        super(PageFooter, self).__init__(node, lnk)
        
        
class Body(_ReportElement):
    '''
    The Body element defines the visual elements of the body of the report, how the data is
    structured/grouped and binds the visual elements to the data for the report.
    It inherits from ReportElement.
    '''
    elements={'ReportItems': [],}
    def __init__(self, node, lnk):
        super(Body, self).__init__(node, self.elements, lnk)


#------------------------------------------
#   Data
#------------------------------------------
class DataSources(Element):
    elements={'DataSource': [Element.ELEMENT,2],}
    def __init__(self, node, lnk):
        super(DataSources, self).__init__(node, self.elements, lnk)


class DataSource(Element):
    elements={'Name': [Element.STRING,1,True],
              'Transaction': [Element.BOOLEAN,0,True],
              'ConnectionProperties': [],
             }
    def __init__(self, node, lnk):
        super(DataSource, self).__init__(node, self.elements, lnk)
        self.conn_properties = self.get_element('ConnectionProperties')
        for ds in lnk.report_def.data_sources:
            if ds.Name == self.Name:
                logger.error(
                    "Report already has a DataSource with name '{0}'".format(
                        self.name), True)
        lnk.report_def.data_sources.append(self)


class ConnectionProperties(Element):
    elements={'DataProvider': [Element.STRING,1],
              'ConnectObject': [Element.STRING,1],
              'Prompt': [Element.STRING,0,True],
             }
    def __init__(self, node, lnk):
        super(ConnectionProperties, self).__init__(node, self.elements, lnk)


class DataSets(Element):
    elements={'DataSet': [Element.ELEMENT,2],}
    def __init__(self, node, lnk):
        super(DataSets, self).__init__(node, self.elements, lnk)


class DataSet(Element):
    '''
    The DataSet element contains information about a set of data to display 
    as a part of the report.
    Name of the data set Cannot be the same name as any data region or group.
    '''
    elements={'Name': [Element.STRING,1,True],
              'Fields': [],
              'Query': [Element.ELEMENT,1],
              'Filters': [],
              'SortExpressions': [],
             }
    def __init__(self, node, lnk):
        self.fields = []
        super(DataSet, self).__init__(node, self.elements, lnk)
        self.fields_def = self.get_element('Fields')
        self.query_def = self.get_element('Query')
        self.filters_def = self.get_element('Filters')
        self.sort_def = self.get_element('SortExpressions')
        
        for ds in lnk.report_def.data_sets:
            if ds.Name == self.Name:
                logger.error(
                    "DataSet with name '{0}' already exists.".format(
                        self.name), True)
        lnk.report_def.data_sets.append(self)


class Fields(Element):
    '''
    The Fields element defines the fields in the data model.
    '''
    elements={'Field': [Element.ELEMENT,2],}
    def __init__(self, node, lnk):
        super(Fields, self).__init__(node, self.elements, lnk) 


class Field(Element):
    '''
    The Field element contains information about a field in the data model of the report.
    '''
    elements={'Name': [Element.STRING,1,True],
              'DataType': [Element.ENUM,0,True],
              'DataField': [Element.STRING,0,True],
              'Value': [Element.VARIANT],
             }
    def __init__(self, node, lnk):
        super(Field, self).__init__(node, self.elements, lnk)
        data_set = lnk.parent.lnk.parent # Get Dataset
        for fd in data_set.fields:
            if fd.Name == self.Name:
                logger.error(
                    "DataSet already has '{0}' Field.".format(
                        self.name), True)
        data_set.fields.append(self)


class Query(Element):
    elements={'DataSourceName': [Element.STRING,1,True],
              'CommandText': [Element.STRING],
              'QueryParameters': [],
             }
    def __init__(self, node, lnk):
        super(Query, self).__init__(node, self.elements, lnk)

    def get_command_text(self, report):
        cmd = Expression.get_value_or_default(
            None, self, "CommandText", None)
        if not cmd:
            logger.error(
                "'CommandText' is required by 'Query' element.", True)
        return cmd


class QueryParameters(Element):
    elements={'QueryParameter': [Element.ELEMENT,2],}
    def __init__(self, node, lnk):
        super(QueryParameters, self).__init__(node, self.elements, lnk)


class QueryParameter(Element):
    elements={'Name': [Element.STRING,1,True],
              'Value': [Element.VARIANT,1],
             }
    def __init__(self, node, lnk):
        super(QueryParameter, self).__init__(node, self.elements, lnk)


class Filters(Element):
    '''
    The Filters element is a collection of filters to apply to a data set, data region or group.
    '''
    elements={'Filter': [Element.ELEMENT,1],}
    def __init__(self, node, lnk):
        self.filter_list=[]
        super(Filters, self).__init__(node, self.elements, lnk)


class Filter(Element):
    '''
    The Filter element describes a filter to apply to rows of data in a data set or data region or to
    apply to group instances.
    
    FilterExpression:
    An expression that is evaluated for each instance within the group or 
    each row of the data set or data region and compared (via the Operator) 
    to the FilterValues. Failed comparisons result in the row/instance being filtered 
    out of the data set, data region or group.

    Operator:
    Equal, Like, NotEqual, GreaterThan, GreaterThanOrEqual, LessThan, LessThanOrEqual,
    TopN, BottomN TopPercent, BottomPercent, In, Between.
    
    FilterValues:
    The values to compare to the FilterExpression.
    For Equal, Like, NotEqual, GreaterThan, GreaterThanOrEqual, LessThan, LessThanOrEqual,
    TopN, BottomN, TopPercent and BottomPercent, there must be exactly one FilterValue.
    For TopN and BottomN, the FilterValue expression must evaluate to an integer.
    For TopPercent and BottomPercent, the FilterValue expression must evaluate to an integer or float.
    For Between, there must be exactly two FilterValue elements.
    For In, the FilterValues are treated as a set (if the FilterExpression value appears anywhere 
    in the set of FilterValues, the instance is not filtered out.)        
    '''
    elements={'FilterExpression': [Element.VARIANT,1],
              'Operator': [Element.ENUM,1,True],
              'FilterValues': [Element.EXPRESSION_LIST,1],
             }
    def __init__(self, node, lnk):
        super(Filter, self).__init__(node, self.elements, lnk)
        lnk.parent.filter_list.append(self)


class FilterValues(_ExpressionList):
    elements={'FilterValue': [Element.VARIANT,2],}
    def __init__(self, node, lnk):
        super(FilterValues, self).__init__(node, self.elements, lnk)


class Group(Element):
    '''
    The Group element defines the expressions 
    to group the data by.
    '''
    elements={'Name': [Element.STRING,1,True],
              'GroupExpressions': [Element.EXPRESSION_LIST],
              'PageBreak': [],
              'Filters': [],
              'SortExpressions': [],
              'Parent': [Element.VARIANT],
             }
    def __init__(self, node, lnk):
        super(Group, self).__init__(node, self.elements, lnk)


class GroupExpressions(_ExpressionList):
    '''
    The GroupExpressions element defines an ordered list 
    of expressions to group the data by.
    '''
    elements={'GroupExpression': [Element.VARIANT,2],}
    def __init__(self, node, lnk):
        super(GroupExpressions, self).__init__(node, self.elements, lnk)


class SortExpressions(Element):
    elements={'SortExpression': [Element.ELEMENT,2],}
    def __init__(self, node, lnk):
        self.sortby_list=[]
        super(SortExpressions, self).__init__(node, self.elements, lnk)


class SortExpression(Element):
    elements={'Value': [Element.VARIANT,1],
              'SortDirection': [Element.ENUM,0,True],
             }
    def __init__(self, node, lnk):
        super(SortExpression, self).__init__(node, self.elements, lnk)
        lnk.parent.sortby_list.append(self)

#------------------------------------------
#   Style
#------------------------------------------

class Style(Element):
    '''
    The Style element contains information about 
    the style of a report item. Where possible, the style
    property names and values match standard HTML/CSS properties.
    '''
    elements={'Border': [],
              'TopBorder': [],
              'BottomBorder': [],
              'LeftBorder': [],
              'RightBorder': [],
              'BackgroundColor': [Element.COLOR],
              'BackgroundGradientType': [Element.ENUM],
              'BackgroundGradientEndColor': [Element.COLOR],
              'BackgroundImage': [],
              'FontStyle': [Element.ENUM],
              'FontFamily': [Element.STRING],
              'FontSize': [Element.SIZE],
              'FontWeight': [Element.ENUM],
              'Format': [Element.STRING],
              'TextDecoration': [Element.ENUM],
              'TextAlign': [Element.ENUM],
              'VerticalAlign': [Element.ENUM],
              'Color': [Element.COLOR],
              'PaddingLeft': [Element.SIZE],
              'PaddingRight': [Element.SIZE],
              'PaddingTop': [Element.SIZE],
              'PaddingBottom': [Element.SIZE],
              'LineHeight': [Element.SIZE],
              'TextDirection': [Element.ENUM],
              'WritingMode': [Element.ENUM],
             }
    def __init__(self, node, lnk):
        super(Style, self).__init__(node, self.elements, lnk)


class Border(Element):
    elements={'Color': [Element.COLOR],
              'BorderStyle': [Element.ENUM],
              'Width': [Element.SIZE],
             }
    def __init__(self, node, lnk):     
        super(Border, self).__init__(node, self.elements, lnk)


#------------------------------------------
#   Report Items
#------------------------------------------
class ReportItems(Element):
    '''
    The ReportItems element is a collection of report items 
    (used to define the contents of a region of a report).
    '''
    elements={'Line': [Element.ELEMENT,3],
              'Rectangle': [Element.ELEMENT,3],
              'Textbox': [Element.ELEMENT,3],
              'Image': [Element.ELEMENT,3],
              'Subreport': [Element.ELEMENT,3],
              'Tablix': [Element.ELEMENT,3], 
              'Chart': [Element.ELEMENT,3],
             }
    def __init__(self, node, lnk):
        self.reportitems_list=[]
        super(ReportItems, self).__init__(node, self.elements, lnk)


class _ReportItem(_ReportElement):
    '''
    A report item is one of the following types of objects: Line, Rectangle, Textbox, Image,
    Subreport, CustomReportItem or DataRegion. DataRegions are: Tablix and Chart.
    The ReportItem element itself is not used. Instead, specific report item element is used wherever
    ReportItem is allowed.
    '''
    elements={'Name': [Element.STRING,1,True],
              'ActionInfo': [],
              'Top': [Element.SIZE,0,True],
              'Left': [Element.SIZE,0,True],
              'Height': [Element.SIZE,0,True],
              'Width': [Element.SIZE,0,True],
              'ZIndex': [Element.INTEGER,0,True, -1],
              'Visibility': [],
              'ToolTip': [Element.STRING],
              'Bookmark': [Element.STRING],
              'RepeatWith': [Element.STRING,0,True],
             }
    def __init__(self, type, node, lnk, additional_elements):
        el = Element.extend_element_list(
                _ReportItem, additional_elements)
        super(_ReportItem, self).__init__(node, el, lnk)
        self.type = type
        lnk.parent.reportitems_list.append(self)


class Line(_ReportItem):
    '''
    The Line element has no additional attributes/elements beyond what it inherits from ReportItem
    Negative heights/widths allow for lines that are drawn up and/or left from their origin.
    Although negative Height and Width are allowed, both Top+Height and Left+Width must be
    nonnegative valid sizes.
    '''
    def __init__(self, node, lnk):
        super(Line, self).__init__("Line", node, lnk, None)


class Rectangle(_ReportItem):
    elements={'ReportItems': [],
              'PageBreak': [],
              'OmitBorderOnPageBreak': [Element.BOOLEAN,0,True],
             }
    def __init__(self, node, lnk):
        super(Rectangle, self).__init__("Rectangle", node, lnk, self.elements)


class Subreport(_ReportItem):
    elements={'ReportName': [Element.STRING,1,True],
              'Parameters': [],
              'NoRowsMessage': [Element.STRING],
              'MergeTransactions': [Element.BOOLEAN,0,True],
              'OmitBorderOnPageBreak': [Element.BOOLEAN,0,True],
             }
    def __init__(self, node, lnk):
        super(Subreport, self).__init__("Subreport", node, lnk, self.elements)


class Parameters(Element):
    elements={'Parameter': [Element.ELEMENT,2],}
    def __init__(self, node, lnk):
        super(Parameters, self).__init__(node, self.elements, lnk)


class Parameter(Element):
    elements={'Name': [Element.STRING,1,True],
              'Value': [Element.VARIANT,1],
              'Omit': [Element.BOOLEAN],
             }
    def __init__(self, node, lnk):
        super(Parameter, self).__init__(node, self.elements, lnk)


class Image(_ReportItem):
    elements={'ImageSource': [Element.ENUM,1,True],
              'Value': [Element.VARIANT,1],
              'MIMEType': [Element.STRING],
              'ImageSizing': [Element.ENUM,0,True],
             }
    def __init__(self, node, lnk):
        super(Image, self).__init__("Image", node, lnk, self.elements)


class Textbox(_ReportItem):
    elements={'Value': [Element.VARIANT,0],
              'CanGrow': [Element.BOOLEAN,0,True],
              'CanShrink': [Element.BOOLEAN,0,True],
              'HideDuplicates': [Element.STRING,0,True],
              'ToggleImage': [],
             }
    def __init__(self, node, lnk):
        super(Textbox, self).__init__("Textbox", node, lnk, self.elements)


class ToggleImage(Element):
    '''
    Indicates the initial state of a toggle image should such an image be displayed as a part of the
    text box. The image is always displayed if the text box is a toggle item for another report item.
    Whenever the text box/image is clicked on, the toggle image state flips and the image associated
    with the new state is displayed instead
    InitialState:
        A Boolean expression, the value of which determines the
        initial state of the toggle image. True = 'expanded' (that
        is, a minus sign). False = 'collapsed' (that is, a plus sign).    
    '''
    elements={'InitialState': [Element.BOOLEAN,1],}
    def __init__(self, node, lnk):
        super(ToggleImage, self).__init__(node, self.elements, lnk)


#------------------------------------------
#   Data Region
#------------------------------------------
class _DataRegion(_ReportItem):
    elements={'NoRowsMessage': [Element.STRING],
              'DataSetName': [Element.STRING,0,True],
              'PageBreak': [],
              'Filters': [],
              'SortExpressions': [],
             }
    def __init__(self, type, node, lnk, additional_elements):
        el = Element.extend_element_list(
                _DataRegion, additional_elements)
        super(_DataRegion, self).__init__(type, node, lnk, el)


class Tablix(_DataRegion):
    elements={'TablixCorner': [],
              'TablixBody': [Element.ELEMENT,1],
              'TablixColumnHierarchy': [Element.ELEMENT,1],
              'TablixRowHierarchy': [Element.ELEMENT,1],
              'LayoutDirection': [Element.ENUM,0,True],
              'GroupsBeforeRowHeaders': [Element.INTEGER,0,True],
              'RepeatColumnHeaders': [Element.BOOLEAN,0,True],
              'RepeatRowHeaders': [Element.BOOLEAN,0,True],
              'FixedColumnHeaders': [Element.BOOLEAN,0,True],
              'FixedRowHeaders': [Element.BOOLEAN,0,True],
              'OmitBorderOnPageBreak': [Element.BOOLEAN,0,True],
             }
    def __init__(self, node, lnk):
        super(Tablix, self).__init__('Tablix', node, lnk, self.elements)


class TablixCorner(Element):
    '''
    The TablixCorner element defines the layout and structure of the 
    upper left-hand corner region of a Tablix
    '''
    elements={'TablixCornerRows': [Element.ELEMENT,1],}
    def __init__(self, node, lnk):
        super(TablixCorner, self).__init__(node, self.elements, lnk)


class TablixCornerRows(Element):
    '''
    The TablixCornerRows element defines the list of rows in the TablixCorner.
    '''
    elements={'TablixCornerRow': [Element.ELEMENT,2],}
    def __init__(self, node, lnk):
        super(TablixCornerRows, self).__init__(node, self.elements, lnk)


class TablixCornerRow(Element):
    '''
    The TablixCornerRow element defines the list of cells in a row 
    of the corner section of a Tablix. The height of the row is equal to 
    the height of the corresponding column TablixHeader
    '''
    elements={'TablixCornerCell': [Element.ELEMENT,2],}
    def __init__(self, node, lnk):
        super(TablixCornerRow, self).__init__(node, self.elements, lnk)


class TablixCornerCell(Element):
    '''
    The TablixCornerCell element defines the contents of each 
    corner cell in the Tablix. The width of the each column is equal 
    to the width of the corresponding row TablixHeader.
    '''
    elements={'CellContents': [],}
    def __init__(self, node, lnk):
        super(TablixCornerCell, self).__init__(node, self.elements, lnk)


class CellContents(Element):
    '''
    The CellContents element defines the report item contained in a body, 
    header or corner cell of a Tablix.
    '''
    elements={'ReportItems': [],
              'ColSpan': [Element.INTEGER,0,True],
              'RowSpan': [Element.INTEGER,0,True],
             }
    def __init__(self, node, lnk):
        super(CellContents, self).__init__(node, self.elements, lnk)


class TablixHierarchy(Element):
    '''
    The virtual TablixHierarchy element defines a hierarchy of members for the tablix
    '''
    elements={'TablixMembers': [Element.ELEMENT,1],}
    def __init__(self, node, lnk):
        super(TablixHierarchy, self).__init__(node, self.elements, lnk)


class TablixRowHierarchy(TablixHierarchy):
    def __init__(self, node, lnk):
        super(TablixRowHierarchy, self).__init__(node, lnk)


class TablixColumnHierarchy(TablixHierarchy):
    def __init__(self, node, lnk):
        super(TablixColumnHierarchy, self).__init__(node, lnk)        


class TablixMembers(Element):
    '''
    The TablixMembers element defines a list of members in a Tablix hierarchy.
    '''
    elements={'TablixMember': [Element.ELEMENT,2],}
    def __init__(self, node, lnk):
        elements={'TablixMember': [Element.ELEMENT,2],}
        self.member_list=[]
        super(TablixMembers, self).__init__(node, self.elements, lnk)


class TablixMember(Element):
    '''
    The TablixMember element defines a member of a tablix hierarchy.
    '''
    elements={'Group': [],
              'TablixHeader': [],
              'TablixMembers': [],
              'FixedData': [Element.BOOLEAN,0,True],
              'Visibility': [],
              'HideIfNoRows': [Element.BOOLEAN,0,True],
              'RepeatOnNewPage': [Element.BOOLEAN,0,True],
             }
    def __init__(self, node, lnk):
        super(TablixMember, self).__init__(node, self.elements, lnk)
        lnk.parent.member_list.append(self)


class TablixHeader(Element):
    '''
    The TablixHeader element defines the ReportItem to use as the header for the group.
    '''
    elements={'Size': [Element.SIZE,1,True],
              'CellContents': [Element.ELEMENT,1],
             }
    def __init__(self, node, lnk):
        super(TablixHeader, self).__init__(node, self.elements, lnk)


class TablixBody(Element):
    '''
    The TablixBody element defines the layout and structure of the 
    bottom right region that contains the data elements of the Tablix.
    '''
    elements={'TablixColumns': [Element.ELEMENT,1],
              'TablixRows': [Element.ELEMENT,1],
             }
    def __init__(self, node, lnk):
        super(TablixBody, self).__init__(node, self.elements, lnk)


class TablixColumns(Element):
    '''
    The TablixColumns element defines the set of columns 
    in the body section of a Tablix.
    '''
    elements={'TablixColumn': [Element.ELEMENT,2],}
    def __init__(self, node, lnk):
        self.column_list=[]
        super(TablixColumns, self).__init__(node, self.elements, lnk)


class TablixColumn(Element):
    '''
    The TablixColumn element defines a column in the body section of a Tablix.
    '''
    elements={'Width': [Element.SIZE,1,True],}
    def __init__(self, node, lnk):
        super(TablixColumn, self).__init__(node, self.elements, lnk)
        lnk.parent.column_list.append(self)


class TablixRows(Element):
    '''
    The TablixRows element defines the list of rows in the body section of a Tablix.
    '''
    elements={'TablixRow': [Element.ELEMENT,2],}
    def __init__(self, node, lnk):
        self.row_list=[]
        super(TablixRows, self).__init__(node, self.elements, lnk)


class TablixRow(Element):
    '''
    The TablixRow element defines a list of cells in a row of the body section of a Tablix.
    '''
    elements={'Height': [Element.SIZE,1,True],
              'TablixCells': [Element.ELEMENT,1],
             }
    def __init__(self, node, lnk):
        super(TablixRow, self).__init__(node, self.elements, lnk)
        lnk.parent.row_list.append(self)


class TablixCells(Element):
    '''
    The TablixCells element defines the list of cells in 
    a row of the body section of a Tablix.
    '''
    elements={'TablixCell': [Element.ELEMENT,2],}
    def __init__(self, node, lnk):
        self.cell_list=[]
        super(TablixCells, self).__init__(node, self.elements, lnk)


class TablixCell(Element):
    '''
    The TablixCell element defines the contents of each cell 
    in the body section of a Tablix.
    '''
    elements={'CellContents': [],}
    def __init__(self, node, lnk):
        super(TablixCell, self).__init__(node, self.elements, lnk)
        lnk.parent.cell_list.append(self)


class PageBreak(Element):
    '''
    The PageBreak element defines page break behavior for a group or report item.
    '''
    elements={'BreakLocation': [Element.ENUM,1,True],}
    def __init__(self, node, lnk):    
        super(PageBreak, self).__init__(node, self.elements, lnk)

