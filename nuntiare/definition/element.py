# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from . expression import String, Boolean, Integer, Variant, Size, Color
from . enum import BorderStyle, FontStyle, FontWeight, TextDecoration, \
        TextAlign, VerticalAlign, TextDirection, WritingMode, \
        BackgroundRepeat, BackgroundGradientType, \
        DataType, SortDirection, Operator
from .. import logger
from .. tools import raise_error_with_log, get_xml_tag_value, \
            get_data_type_value

class Element(object):
    ELEMENT=0
    STRING=1
    INTEGER=2
    BOOLEAN=3
    FLOAT=4
    SIZE=5
    DATE=6
    COLOR=7
    EXPRESSION=8
    EXPRESSION_LIST=9
    URL=10
    ENUM=11
    VARIANT=90

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
        lnk: The linking object
        '''

        self.element_list={}        # Here we list elements found for this element
        #self.reportitems_list=[]    # Peers report items list.
        lnk.obj=self
        self.lnk=lnk                # This is the linking object. See link.py

        # Collect all report items, at the end, order by ZIndex or appears order
        items_by_name={}
        z_count=0        

        for n in node.childNodes:            
            if not elements.has_key(n.nodeName):
                if n.nodeName not in ('#text', '#comment'):
                    logger.warn("Unknown xml element '{0}' for '{1}'. Ignored.".format(n.nodeName, lnk.obj.__class__.__name__))
                continue
            
            element_type, card, must_be_constant = Element.get_element_def(
                            elements[n.nodeName],
                            n.nodeName
                        )
            elements[n.nodeName]=[element_type, card, must_be_constant, True]
                
            if element_type == Element.ELEMENT:
                el = Element.element_factory(n.nodeName, n, lnk)
                if n.nodeName in ("Line", "Rectangle", "Textbox", "Image", "Subreport",
                            "CustomReportItem", "Tablix"):
                    if n.nodeName in ("Textbox"): 
                        if lnk.report_def.report_items.has_key(el.name):
                            raise_error_with_log("Report already has a Texbox with name '{0}'".format(el.name))
                        lnk.report_def.report_items[el.name] = el
                    if items_by_name.has_key(el.name):
                        raise_error_with_log("The container already has a report item with name '{0}'".format(el.name))
                    i = el.zindex if el.zindex > -1 else z_count
                    items_by_name[el.name]=[el, i]
                    z_count = z_count + 1
                self.element_list[n.nodeName] = el
            elif element_type == Element.ENUM:
                self.element_list[n.nodeName]=Element.enum_factory(
                        n.nodeName, n, lnk, card, must_be_constant)
            elif element_type == Element.EXPRESSION_LIST:
                self.element_list[n.nodeName]=Element.expression_list_factory(
                        n.nodeName, n, lnk)
            else: 
                self.element_list[n.nodeName]=Element.expression_factory(
                        elements[n.nodeName][0], n, lnk, card, must_be_constant)


        # Validate elements not used
        for key, el in elements.items():
            if len(el) < 4: # Not verified in the node loop above
                element_type, card, must_be_constant = Element.get_element_def(
                            el, key
                        )
                if card in [1,2]:
                    raise_error_with_log("'{0}' must be defined for '{1}'.".format(key, 
                            lnk.obj.__class__.__name__))

        # Z Order
        reportitems_list=[]
        if len(items_by_name) > 0:
            z_list=[]
            for key, it in items_by_name.items():
                l = (it[1], it[0]) # zindex, reportitem
                z_list.append(l)
            res = sorted(z_list, key=lambda z: z[0])
            for r in res:
                reportitems_list.append(r[1])
                
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
            obj = TopBorder(node, ln)
        elif name=='BottomBorder':
            obj = BottomBorder(node, ln)
        elif name=='LeftBorder':
            obj = LeftBorder(node, ln)
        elif name=='RightBorder':
            obj = RightBorder(node, ln)
        elif name=='BackgroundImage':
            obj = BackgroundImage(node, ln)        
        elif name=='Line':
            obj = Line(node, ln)
        elif name=='Rectangle':
            obj = Rectangle(node, ln)
        elif name=='Textbox':
            obj = Textbox(node, ln)
    #    elif name=='Image':
    #        obj = Image(node, ln)
    #    elif name=='Imports':
    #        obj = Imports(node, ln)
    #    elif name=='Import':
    #        obj = Import(node, ln)
        else:
            raise_error_with_log("Unknown Element: '{0}'".format(name)) 

        return obj
    
    
    @staticmethod
    def enum_factory(name, node, lnk, card, must_be_constant):
        value = get_xml_tag_value(node)
        if card==1 and value==None:
            raise_error_with_log("'{0}' is required for '{1}'.".format(
                    node.nodeName,
                    lnk.obj.__class__.__name__))
     
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

        raise_error_with_log("Unknown Enum: '{0}'.".format(name))
    
    @staticmethod
    def expression_factory(name, node, lnk, card, must_be_constant):
        ln = Link(lnk.report_def, lnk.obj, data=node.nodeName)
        value = get_xml_tag_value(node)
        if card==1 and value==None:
            raise_error_with_log("'{0}' is required for '{1}'.".format(
                    node.nodeName,
                    lnk.obj.__class__.__name__))

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
     
        raise_error_with_log("Unknown expression element definition: '{0}'.".format(name))

    @staticmethod
    def expression_list_factory(name, node, lnk):
        ln = Link(lnk.report_def, lnk.obj)
        if name=='FilterValues':
            obj = FilterValues(node, ln)
        elif name=='GroupExpressions':
            obj = GroupExpressions(node, ln)
        else:
            raise_error_with_log("Unknown Element: '{0}' for ExpressionList".format(name))

        return obj

    @staticmethod
    def get_element_def(element, class_name):
        element_type = Element.ELEMENT
        card = 0
        must_be_constant = False

        if len(element) > 0:
            if element[0]:
                element_type = element[0]
            if len(element) >= 2:
                if element[1]:
                    card = element[1]
            if len(element) >= 3:
                if element[2]:
                    must_be_constant = element[2]
            # len(element)==3 is ignored, it means that element was checked
            if len(element) > 4:
                raise_error_with_log("Invalid number of values for element. Class: '{0}'".format(class_name))

        return element_type, card, must_be_constant
                
    def get_property_value(self, report, property_name, default_value):
        el = self.get_element(property_name)
        if el==None:
            logger.debug("Property '{0}' not found for '{1}'. " \
                "Default value '{2}' returned.".format(property_name, 
                self.lnk.obj.__class__.__name__, default_value))
                
            return default_value
        value = el.value(report)
        if value == None:
            return default_value
        return value
        
    def get_element(self, name):
        if self.element_list.has_key(name):
            return self.element_list[name]

            
class Link(object):
    def __init__(self, report_def, parent, obj=None, data=None):
        self.report_def=report_def  # Main ReportDef() object
        self.parent=parent          # Parent element
        self.obj=obj                # object itself. It is used to assign parent to others
        self.data=data              # optional extra data


class ExpressionList(object):
    def __init__(self, node, elements, lnk):

        if len(elements) == 0 or len(elements) > 1:
            raise_error_with_log("ElementList only can have one sub element type.")

        lnk.obj=self
        self.lnk=lnk
        self.expression_list=[]

        for n in node.childNodes:
            if not elements.has_key(n.nodeName):
                if n.nodeName not in ('#text', '#comment'):
                    logger.warn("Unknown xml element '{0}' for '{1}'. Ignored.".format(n.nodeName, lnk.obj.__class__.__name__))
                continue
                
            element_type, card, must_be_constant = Element.get_element_def(elements[n.nodeName],
                        lnk.obj.__class__.__name__)
                
            ex = Element.expression_factory(elements[n.nodeName][0], n, lnk, card, must_be_constant) 
            self.expression_list.append(ex)
            

#------------------------------------------
#   ReportParameter
#------------------------------------------
class ReportParameters(Element):
    def __init__(self, node, lnk):
        elements={'ReportParameter': [Element.ELEMENT,2],}
        super(ReportParameters, self).__init__(node, elements, lnk) 


class ReportParameter(Element):
    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING,1,True],
                  'DataType': [Element.ENUM,1,True],
                  'CanBeNone': [Element.BOOLEAN,0,True],
                  'AllowBlank': [Element.BOOLEAN,0,True],
                  'DefaultValue': [Element.VARIANT,1],
                  'Promt': [Element.STRING],
                 }

        super(ReportParameter, self).__init__(node, elements, lnk)
        
        self.parameter_name = self.get_property_value(None, 'Name', None)
        self.can_be_none = self.get_property_value(None, 'CanBeNone', True)
        self.allow_blank = self.get_property_value(None, 'AllowBlank', True)
        self.data_type = self.get_property_value(None, 'DataType', None)
        
        #verify_expression_required('Name', 'ReportParameter', self.parameter_name)
        #verify_expression_required('DataType', 'ReportParameter', self.data_type)

        self.default_value = self.get_element('DefaultValue')
        if not self.default_value:
            raise_error_with_log("'DefaultValue' is required for Parameter '{0}'".format(self.parameter_name))
        self.lnk.report_def.parameters_def.append(self)

    def get_default_value(self, report):
        if self.default_value:
            return get_data_type_value(self.data_type, self.default_value.value(report))             
                        
    def get_value(self, report, passed_value):
        if passed_value == None:
            result = self.get_default_value(report)
        else:
            result = get_data_type_value(self.data_type, self.default_value.value(report, passed_value)) 

        if not result and not self.can_be_none:
            raise_error_with_log("Parameter '{0}' value can not be 'None'".format(self.parameter_name))
        if result and result=="" and not self.allow_blank and data_type=='String':
            raise_error_with_log("Parameter '{0}' value can not be an empty string.".format(self.parameter_name))

        return result


class Page(Element):
    '''
    The Page element contains page layout information for the report.
    '''

    def __init__(self, node, lnk):
        elements={'PageHeader': [],
                  'PageFooter': [],
                  'PageHeight': [Element.SIZE,0,True],
                  'PageWidth': [Element.SIZE,0,True],
                  'InteractiveHeight': [Element.SIZE,0,True],
                  'InteractiveWidth': [Element.SIZE,0,True],
                  'LeftMargin': [Element.SIZE,0,True],
                  'RightMargin': [Element.SIZE,0,True],
                  'TopMargin': [Element.SIZE,0,True],
                  'BottomMargin': [Element.SIZE,0,True],
                  'Columns': [Element.INTEGER,0,True],
                  'ColumnSpacing': [Element.SIZE,0,True],
                  'Style': [],
                 }
        super(Page, self).__init__(node, elements, lnk)
        

#------------------------------------------
#   ReportElement
#------------------------------------------
class _ReportElement(Element):
    '''
    The virtual ReportElement element defines an element of a report. The ReportElement element
    itself is not used. Only the subtypes of ReportElement are used: Body, PageSection, ReportItem
    '''

    def __init__(self, node, additional_elements, lnk):
        elements={'Style':[],}
        
        if additional_elements:
            for key, value in additional_elements.items():
                elements[key] = value
        super(_ReportElement, self).__init__(node, elements, lnk)


class _PageSection(_ReportElement):
    '''
    The virtual PageSection element defines the layout of report items to appear at the top or bottom
    of every page of the report. The PageSection element itself is not used. Only subtypes of
    PageSection are used: PageHeader, PageFooter. It inherits from ReportElement.
    '''

    def __init__(self, node, lnk):
        elements={'ReportItems': [],
                  'Height': [Element.SIZE,1,True], 
                  'PrintOnFirstPage': [Element.BOOLEAN,0,True],
                  'PrintOnLastPage': [Element.BOOLEAN,0,True],
                 }
        super(_PageSection, self).__init__(node, elements, lnk)
        
        self.height=self.get_property_value(None, "Height", 0.0)
        self.print_on_first_page=self.get_property_value(None, "PrintOnFirstPage", True)
        self.print_on_last_page=self.get_property_value(None, "PrintOnLastPage", True)


class PageHeader(_PageSection):
    '''
    The PageHeader element defines the layout of report items to appear at the top of every page of
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

    def __init__(self, node, lnk):
        elements={'ReportItems': [],
                  'Height': [Element.SIZE,1,True], 
                 }
        super(Body, self).__init__(node, elements, lnk)


#------------------------------------------
#   Data
#------------------------------------------
class DataSources(Element):
    def __init__(self, node, lnk):
        elements={'DataSource': [Element.ELEMENT,2],}
        super(DataSources, self).__init__(node, elements, lnk) 


class DataSource(Element):
    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING,1,True],
                  'Transaction': [Element.BOOLEAN,0,True],
                  'ConnectionProperties': [],
                 }
        super(DataSource, self).__init__(node, elements, lnk)
        self.name = self.get_property_value(None, "Name", None)        
        self.conn_properties = self.get_element('ConnectionProperties')        
        for ds in lnk.report_def.data_sources:
            if ds.name == self.name:
                raise_error_with_log("Report already has a DataSource with name '{0}'".format(self.name))
        lnk.report_def.data_sources.append(self)


class ConnectionProperties(Element):
    def __init__(self, node, lnk):
        elements={'DataProvider': [Element.STRING,1],
                  'ConnectString': [Element.STRING,1],
                  'Prompt': [Element.STRING,0,True],
                 }
        super(ConnectionProperties, self).__init__(node, elements, lnk)
        self.data_provider = self.get_element("DataProvider")
        if not self.data_provider:
            raise_error_with_log("DataProvider no defined for ConnectionProperties element.")
        self.connection_string = self.get_element("ConnectString")
        if not self.connection_string:
            raise_error_with_log("ConnectString no defined for ConnectionProperties element.")


class DataSets(Element):
    def __init__(self, node, lnk):
        elements={'DataSet': [Element.ELEMENT,2],}
        super(DataSets, self).__init__(node, elements, lnk) 


class DataSet(Element):
    '''
    The DataSet element contains information about a set of data to display 
    as a part of the report.
    Name of the data set Cannot be the same name as any data region or group.
    '''

    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING,1,True],
                  'Fields': [],
                  'Query': [Element.ELEMENT,1],
                  'Filters': [],
                  'SortExpressions': [],
                 }

        self.fields=[]
        super(DataSet, self).__init__(node, elements, lnk)

        self.name = self.get_property_value(None, "Name", None)        
        self.fields_def = self.get_element('Fields')
        self.query_def = self.get_element('Query')
        self.filters_def = self.get_element('Filters')
        self.sort_def = self.get_element('SortExpressions')
        if not self.fields_def or not self.query_def: 
            raise_error_with_log("'Fields' and 'Query' elements are required by DataSet '{0}'.".format(self.name))
        
        for ds in lnk.report_def.data_sets:
            if ds.name == self.name:
                raise_error_with_log("DataSet with name '{0}' already exists.".format(self.name))
        lnk.report_def.data_sets.append(self)


class Fields(Element):
    '''
    The Fields element defines the fields in the data model.
    '''
    
    def __init__(self, node, lnk):
        elements={'Field': [Element.ELEMENT,2],}
        super(Fields, self).__init__(node, elements, lnk) 


class Field(Element):
    '''
    The Field element contains information about a field in the data model of the report.
    '''

    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING,1,True],
                  'DataType': [Element.ENUM,0,True],
                  'DataField': [Element.STRING,0,True],
                  'Value': [Element.VARIANT],
                 }
        super(Field, self).__init__(node, elements, lnk)

        self.name = self.get_property_value(None, "Name", None)
        self.data_type = self.get_property_value(None, "DataType", None)
        self.data_field = self.get_property_value(None, "DataField", None)
        self.value=None
        value_element = self.get_element("Value")
        if value_element:
            self.value = value_element.expression
        
        data_set = lnk.parent.lnk.parent # Get Dataset
        for fd in data_set.fields:
            if fd.name == self.name:
                raise_error_with_log("DataSet already has '{0}' Field.".format(self.name))
        data_set.fields.append(self)
        

class Query(Element):
    def __init__(self, node, lnk):
        elements={'DataSourceName': [Element.STRING,1,True],
                  'CommandText': [Element.STRING,1],
                  'QueryParameters': [],
                 }
        super(Query, self).__init__(node, elements, lnk)
        self.data_source_name = self.get_property_value(None, "DataSourceName", None)        

    def get_command_text(self, report):
        cmd = self.get_property_value(None, "CommandText", None)
        if not cmd:
            raise_error_with_log("'CommandText' is required by 'Query' element.")
        return cmd


class QueryParameters(Element):
    def __init__(self, node, lnk):
        elements={'QueryParameter': [Element.ELEMENT,2],}
        super(QueryParameters, self).__init__(node, elements, lnk) 


class QueryParameter(Element):
    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING,1,True],
                  'Value': [Element.VARIANT,1],
                 }
        super(QueryParameter, self).__init__(node, elements, lnk)
        self.name = get_expression_value_or_default (None, self, 'Name', None)
        

class Filters(Element):
    '''
    The Filters element is a collection of filters to apply to a data set, data region or group.
    '''
    
    def __init__(self, node, lnk):
        elements={'Filter': [Element.ELEMENT,1],}
        self.filter_list=[]
        super(Filters, self).__init__(node, elements, lnk)


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

    def __init__(self, node, lnk):
        elements={'FilterExpression': [Element.VARIANT,1],
                  'Operator': [Element.ENUM,1,True],
                  'FilterValues': [Element.EXPRESSION_LIST,1],
                 }
        super(Filter, self).__init__(node, elements, lnk)
        lnk.parent.filter_list.append(self)


class FilterValues(ExpressionList):
    def __init__(self, node, lnk):
        elements={'FilterValue': [Element.VARIANT,2],}
        super(FilterValues, self).__init__(node, elements, lnk)        


class Group(Element):
    '''
    The Group element defines the expressions to group the data by.
    '''

    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING,1,True],
                  'GroupExpressions': [Element.EXPRESSION_LIST],
                  'PageBreak': [],
                  'Filters': [],
                  'Parent': [Element.VARIANT],
                  'Variables': [],
                  'DataElementName': [Element.STRING,0,True],
                  'DataElementOutput': [Element.ENUM,0,True],
                 }
        super(Group, self).__init__(node, elements, lnk)


class GroupExpressions(ExpressionList):
    '''
    The GroupExpressions element defines an ordered list of expressions to group the data by.
    '''

    def __init__(self, node, lnk):
        elements={'GroupExpression': [Element.VARIANT,2],}
        super(GroupExpressions, self).__init__(node, elements, lnk)
        

class GroupingData(object):
    def __init__(self, data):
        self.data = data
        self.group_data=None
        self.groups={} # key: grouping name, value: list of groups for this grouping
        self.last_group_name=None
    
    def grouping_by(self, grouping_object, sorting_def, optional_name=None):
        if optional_name:
            name = optional_name
        else:
            name = get_expression_value_or_default(None,None,None, direct_expression=grouping_object.name)

        break_at_start = get_expression_value_or_default(None,None,False, direct_expression=grouping_object.page_break_at_start)
        break_at_end = get_expression_value_or_default(None,None,False, direct_expression=grouping_object.page_break_at_end)
        
        self.groups[name] = []
        if not self.group_data: #First grouping
            self.group_data = DataGroup(self.data, name, break_at_start, break_at_end)
            self.group_data.add_rows_by_parent()
            self.filter(self.group_data, grouping_object.filters)
            self.sort(self.group_data, sorting_def)
            # Group
            self.group_data.create_groups(grouping_object.expression_list, break_at_start, break_at_end)            
            for g in self.group_data.groups:
                self.groups[name].append(g)
                self.data.groups.append(g)
        else:
            group_list = self.get_group(self.last_group_name)
            for g in group_list:
                g.create_groups(grouping_object.expression_list, break_at_start, break_at_end)
                for g2 in g.groups:
                    self.filter(g2, grouping_object.filters)                    
                    self.sort(g2, sorting_def)
                    self.groups[name].append(g2)
                    
        self.last_group_name = name
                
    def get_group(self, name):
        result = []
        if self.groups.has_key(name):
            result = self.groups[name]
        return result

    def filter(self, data, filters):
        if filters:
            flt = FiltersObject(filters)
            flt.filter_data(data)
            
    def sort(self, data, sorting_def):
        if sorting_def:
            srt = SortingObject(sorting_def)
            srt.sort_data(data)


class GroupingObject(object):
    def __init__(self, grouping_def, test_grouping_list=None):
        self.expression_list=[]
        self.name=None
        self.page_break_at_start=None
        self.page_break_at_end=None
        self.filters=None
        self.parent=None
        
        if test_grouping_list: # unittest
            self.name = test_grouping_list[0]
            self.page_break_at_start = test_grouping_list[1]
            self.page_break_at_end = test_grouping_list[2]
            self.filters = test_grouping_list[3]
            self.parent = test_grouping_list[4]
            for ex in test_grouping_list[5]:
                self.expression_list.append(ex)
        else:
            if grouping_def:
                self.name = grouping_def.get_element("Name")            
                self.page_break_at_start = grouping_def.get_element("PageBreakAtStart")
                self.page_break_at_end = grouping_def.get_element("PageBreakAtEnd")
                self.filters = grouping_def.get_element("Filters")
                self.parent = grouping_def.get_element("Parent")
                exps = grouping_def.get_element("GroupExpressions")
                for ex in exps.expression_list:
                    self.expression_list.append(ex)
        
        
class SortExpressions(Element):
    def __init__(self, node, lnk):
        elements={'SortExpression': [Element.ELEMENT,2],}
        self.sortby_list=[]
        super(SortExpressions, self).__init__(node, elements, lnk)


class SortExpression(Element):
    def __init__(self, node, lnk):
        elements={'Value': [Element.VARIANT,1],
                  'SortDirection': [Element.ENUM,0,True],
                 }
        super(SortExpression, self).__init__(node, elements, lnk)
        lnk.parent.sortby_list.append(self)
        
        
class Variables(Element):    
    def __init__(self, node, lnk):
        elements={'Variable': [Element.ELEMENT, 2],}
        self.variable_list=[]
        super(Variables, self).__init__(node, elements, lnk)


class Variable(Element):
    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING,1,True],
                  'Expression': [Element.VARIANT],
                  'InitialValue': [Element.VARIANT],
                  'Function': [Element.ENUM,0,True],
                  'CustomFunction': [Element.STRING,0,True],
                 }
        super(Variable, self).__init__(node, elements, lnk)
        lnk.parent.variable_list.append(self)


#------------------------------------------
#   Style
#------------------------------------------

class Style(Element):
    '''
    The Style element contains information about 
    the style of a report item. Where possible, the style
    property names and values match standard HTML/CSS properties.
    '''

    def __init__(self, node, lnk):
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
                  'Direction': [Element.ENUM],
                  'WritingMode': [Element.ENUM],
                 }

        super(Style, self).__init__(node, elements, lnk)        


class BorderElement(Element):
    def __init__(self, node, lnk):     
        elements={'Color': [Element.COLOR],
                  'BorderStyle': [Element.ENUM],
                  'Width': [Element.SIZE],
                 }
        super(BorderElement, self).__init__(node, elements, lnk)


class Border(BorderElement):
    def __init__(self, node, lnk):     
        super(Border, self).__init__(node, lnk)


class TopBorder(BorderElement):
    def __init__(self, node, lnk):     
        super(TopBorder, self).__init__(node, lnk)


class BottomBorder(BorderElement):
    def __init__(self, node, lnk):     
        super(BottomBorder, self).__init__(node, lnk)


class LeftBorder(BorderElement):
    def __init__(self, node, lnk):     
        super(LeftBorder, self).__init__(node, lnk)


class RightBorder(BorderElement):
    def __init__(self, node, lnk):     
        super(RightBorder, self).__init__(node, lnk)


#------------------------------------------
#   Report Items
#------------------------------------------
        
class ReportItems(Element):
    '''
    The ReportItems element is a collection of report items (used to define the contents of a region
    of a report).
    '''

    def __init__(self, node, lnk):
        elements={'Line': [Element.ELEMENT,3],
                  'Rectangle': [Element.ELEMENT,3],
                  'Textbox': [Element.ELEMENT,3],
                  'Image': [Element.ELEMENT,3],
                  'Subreport': [Element.ELEMENT,3],
                  'Tablix': [Element.ELEMENT,3], 
                  'Chart': [Element.ELEMENT,3],
                 }
        self.reportitems_list=[]         
        super(ReportItems, self).__init__(node, elements, lnk)


class _ReportItem(_ReportElement):
    '''
    A report item is one of the following types of objects: Line, Rectangle, Textbox, Image,
      Subreport, CustomReportItem or DataRegion. DataRegions are: Tablix and Chart.
    The ReportItem element itself is not used. Instead, specific report item element is used wherever
      ReportItem is allowed.
    '''

    def __init__(self, type, node, lnk, additional_elements):
        elements={'Name': [Element.STRING,1,True],
                  'ActionInfo': [],
                  'Top': [Element.SIZE,0,True],
                  'Left': [Element.SIZE,0,True],
                  'Height': [Element.SIZE,0,True],
                  'Width': [Element.SIZE,0,True],
                  'ZIndex': [Element.INTEGER,0,True],
                  'Visibility': [],
                  'ToolTip': [Element.STRING],
                  'Bookmark': [Element.STRING],
                  'RepeatWith': [Element.STRING,0,True],
                  'DataElementName': [Element.STRING,0,True],
                  'DataElementOutput': [Element.ENUM,0,True],
                 }
        if additional_elements:
            for key, value in additional_elements.items():
                elements[key] = value

        super(_ReportItem, self).__init__(node, elements, lnk)
        self.type = type        
        self.name = self.get_property_value(None, "Name", None)
        self.zindex = self.get_property_value(None, "ZIndex", -1)        
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
    def __init__(self, node, lnk):
        elements={'ReportItems': [],
                  'PageBreak': [],
                  'KeepTogether': [Element.BOOLEAN,0,True],
                  'OmitBorderOnPageBreak': [Element.BOOLEAN,0,True],
                 }
        super(Rectangle, self).__init__("Rectangle", node, lnk, elements)
        
        
class Subreport(_ReportItem):
    def __init__(self, node, lnk):
        elements={'ReportName': [Element.STRING,1,True],
                  'Parameters': [],
                  'NoRowsMessage': [Element.STRING],
                  'MergeTransactions': [Element.BOOLEAN,0,True],
                  'KeepTogether': [Element.BOOLEAN,0,True],
                  'OmitBorderOnPageBreak': [Element.BOOLEAN,0,True],
                 }
        super(Subreport, self).__init__("Subreport", node, lnk, elements)


class Parameters(Element):
    def __init__(self, node, lnk):
        elements={'Parameter': [Element.ELEMENT,2],}
        super(Parameters, self).__init__(node, elements, lnk) 


class Parameter(Element):
    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING,1,True],
                  'Value': [Element.VARIANT,1],
                  'Omit': [Element.BOOLEAN],
                 }
        super(Parameter, self).__init__(node, elements, lnk)


class Image(_ReportItem):
    def __init__(self, node, lnk):
        elements={'ImageSource': [Element.ENUM,1,True],
                  'Value': [Element.VARIANT,1],
                  'MIMEType': [Element.STRING],
                  'ImageSizing': [Element.ENUM,0,True],
                 }
        super(Image, self).__init__("Image", node, lnk, elements)


class Textbox(_ReportItem):
    def __init__(self, node, lnk):
        elements={'Value': [Element.VARIANT,1],
                  'CanGrow': [Element.BOOLEAN,0,True],
                  'CanShrink': [Element.BOOLEAN,0,True],
                  'HideDuplicates': [Element.STRING,0,True],
                  'ToggleImage': [],
                  'DataElementStyle': [Element.ENUM,0,True],
                 }
        super(Textbox, self).__init__("Textbox", node, lnk, elements)


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

    def __init__(self, node, lnk):
        elements={'InitialState': [Element.BOOLEAN,1],}
        super(ToggleImage, self).__init__(node, elements, lnk)


#------------------------------------------
#   Data Region
#------------------------------------------

class _DataRegion(_ReportItem):
    def __init__(self, type, node, lnk, additional_elements):
        elements={'NoRowsMessage': [Element.STRING],
                  'DataSetName': [Element.STRING,0,True],
                  'PageBreak': [],
                  'Filters': [],
                  'SortExpressions': [],
                  'Variables': [],                  
                 }
        if additional_elements:
            for key, value in additional_elements.items():
                elements[key] = value
        super(_DataRegion, self).__init__(type, node, lnk, elements)
        

class Tablix(_DataRegion):
    def __init__(self, node, lnk):
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
                  'KeepTogether': [Element.BOOLEAN,0,True],
                 }
        super(Tablix, self).__init__('Tablix', node, lnk, elements)       
               

class TablixCorner(Element):
    '''
    The TablixCorner element defines the layout and structure of the 
    upper left-hand corner region of a Tablix
    '''
    
    def __init__(self, node, lnk):
        elements={'TablixCornerRows': [Element.ELEMENT,1],}
        super(TablixCorner, self).__init__(node, elements, lnk)


class TablixCornerRows(Element):
    '''
    The TablixCornerRows element defines the list of rows in the TablixCorner.
    '''
    
    def __init__(self, node, lnk):
        elements={'TablixCornerRow': [Element.ELEMENT,2],}
        super(TablixCornerRows, self).__init__(node, elements, lnk)        


class TablixCornerRow(Element):
    '''
    The TablixCornerRow element defines the list of cells in a row 
    of the corner section of a Tablix. The height of the row is equal to 
    the height of the corresponding column TablixHeader
    '''
    
    def __init__(self, node, lnk):
        elements={'TablixCornerCell': [Element.ELEMENT,2],}
        super(TablixCornerRow, self).__init__(node, elements, lnk)  


class TablixCornerCell(Element):
    '''
    The TablixCornerCell element defines the contents of each 
    corner cell in the Tablix. The width of the each column is equal 
    to the width of the corresponding row TablixHeader.
    '''
    
    def __init__(self, node, lnk):
        elements={'CellContents': [],}
        super(TablixCornerCell, self).__init__(node, elements, lnk)  


class CellContents(Element):
    '''
    The CellContents element defines the report item contained in a body, 
    header or corner cell of a Tablix.
    '''
    
    def __init__(self, node, lnk):
        elements={'ReportItems': [],
                  'ColSpan': [Element.INTEGER,0,True],
                  'RowSpan': [Element.INTEGER,0,True],
                 }
        super(CellContents, self).__init__(node, elements, lnk) 


class TablixHierarchy(Element):
    '''
    The virtual TablixHierarchy element defines a hierarchy of members for the tablix
    '''
    
    def __init__(self, node, lnk):
        elements={'TablixMembers': [Element.ELEMENT,1],}
        super(TablixHierarchy, self).__init__(node, elements, lnk)


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
    
    def __init__(self, node, lnk):
        elements={'TablixMember': [Element.ELEMENT,2],}
        self.member_list=[]
        super(TablixMembers, self).__init__(node, elements, lnk)


class TablixMember(Element):
    '''
    The TablixMember element defines a member of a tablix hierarchy.
    '''
    
    def __init__(self, node, lnk):
        elements={'Group': [],
                  'SortExpressions': [],
                  'TablixHeader': [],
                  'TablixMembers': [],
                  'FixedData': [Element.BOOLEAN,0,True],
                  'Visibility': [],
                  'HideIfNoRows': [Element.BOOLEAN,0,True],
                  'KeepWithGroup': [Element.ENUM,0,True],
                  'RepeatOnNewPage': [Element.BOOLEAN,0,True],
                  'DataElementName': [Element.STRING,0,True],
                  'DataElementOutput': [Element.ENUM,0,True],
                  'KeepTogether': [Element.BOOLEAN,0,True],                                                         
                 }
        super(TablixMember, self).__init__(node, elements, lnk)
        lnk.parent.member_list.append(self)


class TablixHeader(Element):
    '''
    The TablixHeader element defines the ReportItem to use as the header for the group.
    '''
    
    def __init__(self, node, lnk):
        elements={'Size': [Element.SIZE,1,True],
                  'CellContents': [Element.ELEMENT,1],
                 }
        super(TablixHeader, self).__init__(node, elements, lnk)  


class TablixBody(Element):
    '''
    The TablixBody element defines the layout and structure of the 
    bottom right region that contains the data elements of the Tablix.
    '''
    
    def __init__(self, node, lnk):
        elements={'TablixColumns': [Element.ELEMENT,1],
                  'TablixRows': [Element.ELEMENT,1],
                 }
        super(TablixBody, self).__init__(node, elements, lnk)
        

class TablixColumns(Element):
    '''
    The TablixColumns element defines the set of columns 
    in the body section of a Tablix.
    '''
    
    def __init__(self, node, lnk):
        elements={'TablixColumn': [Element.ELEMENT,2],}
        self.column_list=[]
        super(TablixColumns, self).__init__(node, elements, lnk)
        
        
class TablixColumn(Element):
    '''
    The TablixColumn element defines a column in the body section of a Tablix.
    '''
    
    def __init__(self, node, lnk):
        elements={'Width': [Element.SIZE,1,True],}
        super(TablixColumn, self).__init__(node, elements, lnk)
        lnk.parent.column_list.append(self)


class TablixRows(Element):
    '''
    The TablixRows element defines the list of rows in the body section of a Tablix.
    '''
    
    def __init__(self, node, lnk):
        elements={'TablixRow': [Element.ELEMENT,2],}
        self.row_list=[]
        super(TablixRows, self).__init__(node, elements, lnk)


class TablixRow(Element):
    '''
    The TablixRow element defines a list of cells in a row of the body section of a Tablix.
    '''
    
    def __init__(self, node, lnk):
        elements={'Height': [Element.SIZE,1,True],
                  'TablixCells': [Element.ELEMENT,1],
                 }
        super(TablixRow, self).__init__(node, elements, lnk)
        lnk.parent.row_list.append(self)
    

class TablixCells(Element):
    '''
    The TablixCells element defines the list of cells in 
    a row of the body section of a Tablix.
    '''
    
    def __init__(self, node, lnk):
        elements={'TablixCell': [Element.ELEMENT,2],}
        self.cell_list=[]
        super(TablixCells, self).__init__(node, elements, lnk)


class TablixCell(Element):
    '''
    The TablixCell element defines the contents of each cell 
    in the body section of a Tablix.
    '''
    
    def __init__(self, node, lnk):
        elements={'CellContents': [],
                  'DataElementName': [Element.STRING,0,True],
                  'DataElementOutput': [Element.ENUM,0,True],
                 }
        super(TablixCell, self).__init__(node, elements, lnk)
        lnk.parent.cell_list.append(self)        
        
