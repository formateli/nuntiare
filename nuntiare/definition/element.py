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
from .. import LOGGER
from .. data.data_type import DataType as dt
from .. tools import get_xml_tag_value


class ElementCard(object):
    ZERO_OR_ONE = 0
    ONE = 1
    ONE_OR_MANY = 2
    ZERO_OR_MANY = 3


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
            Card: Values can be: 0 (0 to 1), 1 (1), 2 (1 to N), 3 (0 to N).
                Default value: 0
            Must be a constant: If true,
                this element value can not be an expression.
                Ignore if type is Element.ELEMENT. Default value: False
            DefaultValue
                Ignore if type is Element.ELEMENT. Default value: False
        lnk: The linking object
        '''

        super(Element, self).__init__()

        self._original_element_list = elements

        # Here we list elements found for this element
        self.element_list = {}
        lnk.obj = self
        # This is the linking object. See link.py
        self.lnk = lnk

        self.element_name = self.__class__.__name__
        self.expression_list = {}
        self.non_expression_list = {}

        # Collect all report items, at the end,
        # order by ZIndex or appears order
        items_by_name = {}
        z_count = 0

        for n in node.childNodes:
            if n.nodeName not in elements:
                if n.nodeName == 'DataEmbedded' and \
                        n.parentNode.nodeName == 'Report':
                    self.set_data()
                    continue
                if n.nodeName not in ('#text', '#comment'):
                    LOGGER.warn(
                        "Unknown xml element '{0}' for '{1}'. Ignored.".format(
                            n.nodeName, lnk.obj.__class__.__name__))
                continue

            element_type, card, must_be_constant, default_value = \
                Element.get_element_def(elements[n.nodeName], n.nodeName)

            elements[n.nodeName] = \
                [element_type, card, must_be_constant, default_value, True]

            if element_type == Element.ELEMENT:
                el = Element.element_factory(n.nodeName, n, lnk)
                if n.nodeName in (
                        'Line', 'Rectangle', 'Textbox', 'Image',
                        'Subreport', 'CustomReportItem', 'Tablix'):
                    if n.nodeName in ('Textbox'):
                        err_msg = "Report already has a " \
                            "Texbox with name '{0}'"
                        if el.Name in lnk.report_def.report_items:
                            LOGGER.error(err_msg.format(el.Name), True)
                        lnk.report_def.report_items[el.Name] = el
                    if el.Name in items_by_name:
                        err_msg = "The container already has " \
                            "a report item with name '{0}'"
                        LOGGER.error(err_msg.format(el.Name), True)
                    i = el.ZIndex if el.ZIndex > -1 else z_count
                    items_by_name[el.Name] = [el, i]
                    z_count = z_count + 1
                self.element_list[n.nodeName] = el
                self.non_expression_list[n.nodeName] = \
                    self.element_list[n.nodeName]
            elif element_type == Element.EXPRESSION_LIST:
                self.element_list[n.nodeName] = \
                    Element.expression_list_factory(n.nodeName, n, lnk)
                self.non_expression_list[n.nodeName] = \
                    self.element_list[n.nodeName]
            elif element_type == Element.ENUM:
                self.element_list[n.nodeName] = \
                    Element.enum_factory(
                        n.nodeName, n, lnk, card, must_be_constant)
                self.expression_list[n.nodeName] = \
                    self.element_list[n.nodeName]
                self._set_attr(
                    n.nodeName, False, default_value, must_be_constant)
            else:
                self.element_list[n.nodeName] = \
                    Element.expression_factory(
                        elements[n.nodeName][0], n, lnk,
                        card, must_be_constant)
                self.expression_list[n.nodeName] = \
                    self.element_list[n.nodeName]
                self._set_attr(
                    n.nodeName, False, default_value, must_be_constant)

        # Validate elements not used
        for key, el in elements.items():
            if len(el) < 5:  # Not verified in the node loop above
                element_type, card, must_be_constant, default_value = \
                    Element.get_element_def(el, key)
                if card in [ElementCard.ONE, ElementCard.ONE_OR_MANY]:
                    LOGGER.error("'{0}' must be defined for '{1}'.".format(
                        key, lnk.obj.__class__.__name__), True)

        # Z Order
        reportitems_list = []
        if len(items_by_name) > 0:
            z_list = []
            for key, it in items_by_name.items():
                l = (it[1], it[0])  # zindex, reportitem
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

        if result[0] in (
                Element.ELEMENT, Element.EXPRESSION_LIST, Element.URL):
            el = self.get_element(name)
            if el:
                self._set_attr(name, True, el, False)
                return self.__dict__[name]
        else:
            if not result[2]:
                err_msg = "'{0}' is not a constant property " \
                    "for element '{1}'. Use get_value() instead."
                LOGGER.error(err_msg.format(name, self.element_name), True)
            else:
                self._set_attr(name, False, result[3], result[2])
                return self.__dict__[name]

    def get_value(self, report, name, default_value=None):
        self._verify_element(name)
        return Expression.get_value_or_default(
            report, self, name, default_value)

    def _verify_element(self, name):
        if name not in self._original_element_list.keys():
            err_msg = "'{0}' is not a valid member for element '{1}'. " \
                "Valid values are: {2}"
            LOGGER.error(err_msg.format(
                name, self.element_name,
                self._original_element_list.keys()), True)

    @staticmethod
    def extend_element_list(class_, additional_elements):
        el = {}
        for key, value in class_.elements.items():
            el[key] = value
        if additional_elements:
            for key, value in additional_elements.items():
                el[key] = value
        return el

    @staticmethod
    def element_factory(name, node, lnk):
        ln = Link(lnk.report_def, lnk.obj)
        if name == 'Page':
            obj = Page(node, ln)
        elif name == 'PageHeader':
            obj = PageHeader(node, ln)
        elif name == 'PageFooter':
            obj = PageFooter(node, ln)
        elif name == 'EmbeddedImages':
            obj = EmbeddedImages(node, ln)
        elif name == 'EmbeddedImage':
            obj = EmbeddedImage(node, ln)
        elif name == 'Body':
            obj = Body(node, ln)
        elif name == 'Visibility':
            obj = Visibility(node, ln)
        elif name == 'DataSources':
            obj = DataSources(node, ln)
        elif name == 'DataSource':
            obj = DataSource(node, ln)
        elif name == 'ConnectionProperties':
            obj = ConnectionProperties(node, ln)
        elif name == 'DataSets':
            obj = DataSets(node, ln)
        elif name == 'DataSet':
            obj = DataSet(node, ln)
        elif name == 'Fields':
            obj = Fields(node, ln)
        elif name == 'Field':
            obj = Field(node, ln)
        elif name == 'Query':
            obj = Query(node, ln)
        elif name == 'QueryParameters':
            obj = QueryParameters(node, ln)
        elif name == 'QueryParameter':
            obj = QueryParameter(node, ln)
        elif name == 'SortExpressions':
            obj = SortExpressions(node, ln)
        elif name == 'SortExpression':
            obj = SortExpression(node, ln)
        elif name == 'Filters':
            obj = Filters(node, ln)
        elif name == 'Filter':
            obj = Filter(node, ln)
        elif name == 'Group':
            obj = Group(node, ln)
        elif name == 'ReportParameters':
            obj = ReportParameters(node, ln)
        elif name == 'ReportParameter':
            obj = ReportParameter(node, ln)
        elif name == 'ReportItems':
            obj = ReportItems(node, ln)
        elif name == 'Tablix':
            obj = Tablix(node, ln)
        elif name == 'TablixColumnHierarchy':
            obj = TablixColumnHierarchy(node, ln)
        elif name == 'TablixRowHierarchy':
            obj = TablixRowHierarchy(node, ln)
        elif name == 'TablixMembers':
            obj = TablixMembers(node, ln)
        elif name == 'TablixMember':
            obj = TablixMember(node, ln)
        elif name == 'TablixBody':
            obj = TablixBody(node, ln)
        elif name == 'TablixHeader':
            obj = TablixHeader(node, ln)
        elif name == 'TablixColumns':
            obj = TablixColumns(node, ln)
        elif name == 'TablixColumn':
            obj = TablixColumn(node, ln)
        elif name == 'TablixRows':
            obj = TablixRows(node, ln)
        elif name == 'TablixRow':
            obj = TablixRow(node, ln)
        elif name == 'TablixCells':
            obj = TablixCells(node, ln)
        elif name == 'TablixCell':
            obj = TablixCell(node, ln)
        elif name == 'CellContents':
            obj = CellContents(node, ln)
        elif name == 'Style':
            obj = Style(node, ln)
        elif name == 'Border':
            obj = Border(node, ln)
        elif name == 'TopBorder':
            obj = TopBorder(node, ln)
        elif name == 'BottomBorder':
            obj = BottomBorder(node, ln)
        elif name == 'LeftBorder':
            obj = LeftBorder(node, ln)
        elif name == 'RightBorder':
            obj = Border(node, ln)
        elif name == 'BackgroundImage':
            obj = BackgroundImage(node, ln)
        elif name == 'Line':
            obj = Line(node, ln)
        elif name == 'Rectangle':
            obj = Rectangle(node, ln)
        elif name == 'Textbox':
            obj = Textbox(node, ln)
        elif name == 'PageBreak':
            obj = PageBreak(node, ln)
    #    elif name == 'Image':
    #        obj = Image(node, ln)
        elif name == 'Modules':
            obj = Modules(node, ln)
        elif name == 'Module':
            obj = Module(node, ln)
        else:
            LOGGER.error(
                "Element '{0}' not implemented.".format(name), True)

        return obj

    @staticmethod
    def enum_factory(name, node, lnk, card, must_be_constant):
        value = get_xml_tag_value(node)
        if card in [ElementCard.ONE, ElementCard.ONE_OR_MANY] \
                and value is None:
            LOGGER.error("'{0}' is required by '{1}'.".format(
                node.nodeName, lnk.obj.__class__.__name__), True)

        if name == 'BorderStyle':
            return BorderStyle(value, lnk, must_be_constant)
        if name == 'FontStyle':
            return FontStyle(value, lnk, must_be_constant)
        if name == 'FontWeight':
            return FontWeight(value, lnk, must_be_constant)
        if name == 'TextDecoration':
            return TextDecoration(value, lnk, must_be_constant)
        if name == 'TextAlign':
            return TextAlign(value, lnk, must_be_constant)
        if name == 'VerticalAlign':
            return VerticalAlign(value, lnk, must_be_constant)
        if name == 'TextDirection':
            return TextDirection(value, lnk, must_be_constant)
        if name == 'WritingMode':
            return WritingMode(value, lnk, must_be_constant)
        if name == 'BackgroundRepeat':
            return BackgroundRepeat(value, lnk, must_be_constant)
        if name == 'BackgroundGradientType':
            return BackgroundGradientType(value, lnk, must_be_constant)
        if name == 'DataType':
            return DataType(value, lnk, must_be_constant)
        if name == 'SortDirection':
            return SortDirection(value, lnk, must_be_constant)
        if name == 'Operator':
            return Operator(value, lnk, must_be_constant)
        if name == 'BreakLocation':
            return BreakLocation(value, lnk, must_be_constant)

        LOGGER.error("Enum '{0}' not implemented.".format(name), True)

    @staticmethod
    def expression_factory(name, node, lnk, card, must_be_constant):
        ln = Link(lnk.report_def, lnk.obj, data=node.nodeName)
        value = get_xml_tag_value(node)
        if card in [ElementCard.ONE, ElementCard.ONE_OR_MANY] and \
                value is None:
            LOGGER.error("'{0}' is required by '{1}'.".format(
                node.nodeName, lnk.obj.__class__.__name__), True)

        if name == Element.STRING:
            return String(value, ln, must_be_constant)
        if name == Element.INTEGER:
            return Integer(value, ln, must_be_constant)
        if name == Element.BOOLEAN:
            return Boolean(value, ln, must_be_constant)
        if name == Element.SIZE:
            return Size(value, ln, must_be_constant)
        if name == Element.COLOR:
            return Color(value, ln, must_be_constant)
        if name == Element.URL:
            return None
        if name == Element.VARIANT:
            return Variant(value, ln, must_be_constant)

        LOGGER.error(
            "Unknown expression element definition: '{0}'.".format(
                name), True)

    @staticmethod
    def expression_list_factory(name, node, lnk):
        ln = Link(lnk.report_def, lnk.obj)
        if name == 'FilterValues':
            obj = FilterValues(node, ln)
        elif name == 'GroupExpressions':
            obj = GroupExpressions(node, ln)
        else:
            LOGGER.error(
                "Unknown Element: '{0}' for ExpressionList".format(
                    name), True)

        return obj

    @staticmethod
    def get_element_def(element, class_name=None):
        element_type = Element.ELEMENT
        card = ElementCard.ZERO_OR_ONE
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
                LOGGER.error(
                    "Invalid number of values. Class: '{0}'".format(
                        class_name), True)

        return element_type, card, must_be_constant, default_value

    def get_element(self, name):
        if name in self.element_list:
            return self.element_list[name]

    def has_element(self, name):
        el = self.get_element(name)
        if el:
            return True


class Link(object):
    def __init__(self, report_def, parent, obj=None, data=None):
        # Main Report() object where some collections are stored
        self.report_def = report_def
        # Parent element
        self.parent = parent
        # object itself. It is used to assign parent to others
        self.obj = obj
        # optional extra data
        self.data = data
        if not parent:
            self.report_def = obj


class _ExpressionList(object):
    def __init__(self, node, elements, lnk):

        if len(elements) == 0 or len(elements) > 1:
            LOGGER.error(
                "ElementList only can have one sub element type.", True)

        lnk.obj = self
        self.lnk = lnk
        self.expression_list = []

        for n in node.childNodes:
            if n.nodeName not in elements:
                if n.nodeName not in ('#text', '#comment'):
                    LOGGER.warn(
                        "Unknown xml element '{0}' for '{1}'. Ignored.".format(
                            n.nodeName, lnk.obj.__class__.__name__))
                continue

            element_type, card, must_be_constant, default_value = \
                Element.get_element_def(
                    elements[n.nodeName], lnk.obj.__class__.__name__)

            ex = Element.expression_factory(
                elements[n.nodeName][0], n, lnk, card, must_be_constant)
            self.expression_list.append(ex)


class Nuntiare(Element):
    '''
    Root definition element.
    '''
    class Data():
        def __init__(self):
            self._loaded = False
            self.data = {}

        def load(self, report):
            if self._loaded:
                return
            LOGGER.info("Getting data from 'DataEmbedded'")
            # Loads the Data emmeded in definition file
            self._curr_data_name = None
            self._curr_index = 0
            doc = report._get_xml_document()
            root = report._get_root(doc)
            data = doc.getElementsByTagName('DataEmbedded')
            self._get_data(doc, data[0])
            self._loaded = True

        def get_data(self, data_name):
            if data_name in self.data.keys():
                return self.data[data_name]
            err_msg = "Attempted to get data '{0}' from DataEmbedded, "
            err_msg += "but it does not exist"
            LOGGER.warn(err_msg.format(data_name))

        def reset(self):
            self.data = {}

        def _get_data(self, doc, node):
            for n in node.childNodes:
                if n.nodeName in ('#comment'):
                    continue
                if n.nodeName == 'Record' and \
                        n.parentNode.nodeName == 'Records':
                    self._curr_index = self._curr_index + 1
                if n.nodeName in ('#text'):
                    if len(n.parentNode.childNodes) != 1:
                        continue
                    if n.parentNode.nodeName == 'Name' and \
                            n.parentNode.parentNode.nodeName == 'Data':
                        self._curr_data_name = n.nodeValue
                        self.data[self._curr_data_name] = [[], []]
                        self._curr_index = -1
                        continue
                    if n.parentNode.parentNode.nodeName == 'Record' and \
                            n.parentNode.parentNode.parentNode.nodeName == \
                            'Records':
                        if n.parentNode.nodeName not in \
                                self.data[self._curr_data_name][0]:
                            # append to columns
                            self.data[self._curr_data_name][0].append(
                                n.parentNode.nodeName)

                        if len(self.data[self._curr_data_name][1]) == \
                                self._curr_index:
                            self.data[self._curr_data_name][1].append([])
                        self.data[
                            self._curr_data_name][1][self._curr_index].append(
                                n.nodeValue)

                self._get_data(doc, n)

    elements = {
        'Name': [Element.STRING, 1, True],
        'Description': [Element.STRING, 0, True],
        'Author': [Element.STRING, 0, True],
        'Version': [Element.STRING, 0, True],
        'DateCreate': [Element.DATE, 0, True],
        'DateUpdate': [Element.DATE, 0, True],
        'DataSources': [],
        'DataSets': [],
        'Body': [Element.ELEMENT, 1],
        'ReportParameters': [],
        'Modules': [],
        'EmbeddedImages': [],
        'Page': [Element.ELEMENT, 1],
    }

    def __init__(self, node):
        LOGGER.info('Initializing report definition...')

        self.parameters_def = []
        self.data_sources = []
        self.data_sets = []
        self.modules = []
        self.report_items = {}  # only textboxes
        self.report_items_group = {}
        self.data = None

        lnk = Link(None, None, self)
        super(Nuntiare, self).__init__(node, self.elements, lnk)

    def get_parameter_def(self, parameter_name):
        for p in self.parameters_def:
            if p.Name == parameter_name:
                return p

    def set_data(self):
        self.data = Report.Data()


class EmbeddedImages(Element):
    elements = {'EmbeddedImage': [Element.ELEMENT, 2], }

    def __init__(self, node, lnk):
        super(EmbeddedImages, self).__init__(node, self.elements, lnk)


class EmbeddedImage(Element):
    elements = {
        'Name': [Element.STRING, 1, True],
        'MIMEType': [Element.STRING, 1, True],
        'ImageData': [Element.STRING, 1, True],
    }

    def __init__(self, node, lnk):
        super(EmbeddedImage, self).__init__(node, self.elements, lnk)


class Modules(Element):
    elements = {'Module': [Element.ELEMENT, 2], }

    def __init__(self, node, lnk):
        self.modules = []
        super(Modules, self).__init__(node, self.elements, lnk)


class Module(Element):
    elements = {
        'From': [Element.STRING, 0, True],
        'Import': [Element.STRING, 0, True],
        'As': [Element.STRING, 0, True],
    }

    def __init__(self, node, lnk):
        super(Module, self).__init__(node, self.elements, lnk)
        lnk.parent.modules.append(self)


class ReportParameters(Element):
    elements = {'ReportParameter': [Element.ELEMENT, 2], }

    def __init__(self, node, lnk):
        super(ReportParameters, self).__init__(node, self.elements, lnk)


class ReportParameter(Element):
    elements = {
        'Name': [Element.STRING, 1, True],
        'DataType': [Element.ENUM, 1, True],
        'CanBeNone': [Element.BOOLEAN, 0, True, True],
        'AllowBlank': [Element.BOOLEAN, 0, True, True],
        'DefaultValue': [Element.VARIANT, 1],
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
        if passed_value is None:
            result = self.get_default_value(report)
        else:
            result = dt.get_value(
                self.DataType, self._default_value.value(
                    report, passed_value))

        if not result and not self.CanBeNone:
            LOGGER.error(
                "Parameter '{0}' value can not be 'None'".format(
                    self.Name), True)
        if result and result == '' and \
                not self.AllowBlank and DataType == 'String':
            LOGGER.error(
                "Parameter '{0}' value can not be an empty string.".format(
                    self.Name), True)

        return result


class Visibility(Element):
    elements = {
        'Hidden': [Element.BOOLEAN, 0],
        'ToggleItem': [Element.STRING, 0, True],
    }

    def __init__(self, node, lnk):
        super(Visibility, self).__init__(node, self.elements, lnk)


class Page(Element):
    elements = {
        'PageHeader': [],
        'PageFooter': [],
        'PageHeight': [Element.SIZE, 0, True],
        'PageWidth': [Element.SIZE, 0, True],
        'LeftMargin': [Element.SIZE, 0, True],
        'RightMargin': [Element.SIZE, 0, True],
        'TopMargin': [Element.SIZE, 0, True],
        'BottomMargin': [Element.SIZE, 0, True],
        'Columns': [Element.INTEGER, 0, True],
        'ColumnSpacing': [Element.SIZE, 0, True],
        'Style': [],
    }

    def __init__(self, node, lnk):
        super(Page, self).__init__(node, self.elements, lnk)


class _ReportElement(Element):
    elements = {'Style': [], }

    def __init__(self, node, additional_elements, lnk):
        el = Element.extend_element_list(
                _ReportElement, additional_elements)
        super(_ReportElement, self).__init__(node, el, lnk)


class _PageSection(_ReportElement):
    elements = {
        'ReportItems': [],
        'Height': [Element.SIZE, 1, True],
        'PrintOnFirstPage': [Element.BOOLEAN, 0, True],
        'PrintOnLastPage': [Element.BOOLEAN, 0, True],
    }

    def __init__(self, node, lnk):
        super(_PageSection, self).__init__(node, self.elements, lnk)


class PageHeader(_PageSection):
    def __init__(self, node, lnk):
        super(PageHeader, self).__init__(node, lnk)


class PageFooter(_PageSection):
    def __init__(self, node, lnk):
        super(PageFooter, self).__init__(node, lnk)


class Body(_ReportElement):
    elements = {'ReportItems': [], }

    def __init__(self, node, lnk):
        super(Body, self).__init__(node, self.elements, lnk)


class DataSources(Element):
    elements = {'DataSource': [Element.ELEMENT, 2], }

    def __init__(self, node, lnk):
        super(DataSources, self).__init__(node, self.elements, lnk)


class DataSource(Element):
    elements = {
        'Name': [Element.STRING, 1, True],
        'Transaction': [Element.BOOLEAN, 0, True],
        'ConnectionProperties': [],
    }

    def __init__(self, node, lnk):
        super(DataSource, self).__init__(node, self.elements, lnk)
        self.conn_properties = self.get_element('ConnectionProperties')
        for ds in lnk.report_def.data_sources:
            if ds.Name == self.Name:
                LOGGER.error(
                    "Report already has a DataSource with name '{0}'".format(
                        self.name), True)
        lnk.report_def.data_sources.append(self)


class ConnectionProperties(Element):
    elements = {
        'DataProvider': [Element.STRING, 1],
        'ConnectObject': [Element.STRING, 1],
        'Prompt': [Element.STRING, 0, True],
    }

    def __init__(self, node, lnk):
        super(ConnectionProperties, self).__init__(node, self.elements, lnk)


class DataSets(Element):
    elements = {'DataSet': [Element.ELEMENT, 2], }

    def __init__(self, node, lnk):
        super(DataSets, self).__init__(node, self.elements, lnk)


class DataSet(Element):
    elements = {
        'Name': [Element.STRING, 1, True],
        'Fields': [],
        'Query': [Element.ELEMENT, 1],
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
                LOGGER.error(
                    "DataSet with name '{0}' already exists.".format(
                        self.name), True)
        lnk.report_def.data_sets.append(self)


class Fields(Element):
    elements = {'Field': [Element.ELEMENT, 2], }

    def __init__(self, node, lnk):
        super(Fields, self).__init__(node, self.elements, lnk)


class Field(Element):
    '''
    The Field element contains information about a field in
    the data model of the report.
    '''
    elements = {
        'Name': [Element.STRING, 1, True],
        'DataType': [Element.ENUM, 0, True],
        'DataField': [Element.STRING, 0, True],
        'Value': [Element.VARIANT],
    }

    def __init__(self, node, lnk):
        super(Field, self).__init__(node, self.elements, lnk)
        data_set = lnk.parent.lnk.parent  # Get Dataset
        for fd in data_set.fields:
            if fd.Name == self.Name:
                LOGGER.error(
                    "DataSet already has '{0}' Field.".format(
                        self.name), True)
        data_set.fields.append(self)


class Query(Element):
    elements = {
        'DataSourceName': [Element.STRING, 1, True],
        'CommandText': [Element.STRING],
        'QueryParameters': [],
    }

    def __init__(self, node, lnk):
        super(Query, self).__init__(node, self.elements, lnk)

    def get_command_text(self, report):
        cmd = Expression.get_value_or_default(
            None, self, "CommandText", None)
        if not cmd:
            LOGGER.error(
                "'CommandText' is required by 'Query' element.", True)
        return cmd


class QueryParameters(Element):
    elements = {'QueryParameter': [Element.ELEMENT, 2], }

    def __init__(self, node, lnk):
        super(QueryParameters, self).__init__(node, self.elements, lnk)


class QueryParameter(Element):
    elements = {
        'Name': [Element.STRING, 1, True],
        'Value': [Element.VARIANT, 1],
    }

    def __init__(self, node, lnk):
        super(QueryParameter, self).__init__(node, self.elements, lnk)


class Filters(Element):
    elements = {'Filter': [Element.ELEMENT, 1], }

    def __init__(self, node, lnk):
        self.filter_list = []
        super(Filters, self).__init__(node, self.elements, lnk)


class Filter(Element):
    elements = {
        'FilterExpression': [Element.VARIANT, 1],
        'Operator': [Element.ENUM, 1, True],
        'FilterValues': [Element.EXPRESSION_LIST, 1],
    }

    def __init__(self, node, lnk):
        super(Filter, self).__init__(node, self.elements, lnk)
        lnk.parent.filter_list.append(self)


class FilterValues(_ExpressionList):
    elements = {'FilterValue': [Element.VARIANT, 2], }

    def __init__(self, node, lnk):
        super(FilterValues, self).__init__(node, self.elements, lnk)


class Group(Element):
    elements = {
        'Name': [Element.STRING, 1, True],
        'GroupExpressions': [Element.EXPRESSION_LIST],
        'PageBreak': [],
        'Filters': [],
        'SortExpressions': [],
        'Parent': [Element.VARIANT],
    }

    def __init__(self, node, lnk):
        super(Group, self).__init__(node, self.elements, lnk)


class GroupExpressions(_ExpressionList):
    elements = {'GroupExpression': [Element.VARIANT, 2], }

    def __init__(self, node, lnk):
        super(GroupExpressions, self).__init__(node, self.elements, lnk)


class SortExpressions(Element):
    elements = {'SortExpression': [Element.ELEMENT, 2], }

    def __init__(self, node, lnk):
        self.sortby_list = []
        super(SortExpressions, self).__init__(node, self.elements, lnk)


class SortExpression(Element):
    elements = {
        'Value': [Element.VARIANT, 1],
        'SortDirection': [Element.ENUM, 0, True],
    }

    def __init__(self, node, lnk):
        super(SortExpression, self).__init__(node, self.elements, lnk)
        lnk.parent.sortby_list.append(self)


class Style(Element):
    elements = {
        'Border': [],
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
    elements = {
        'Color': [Element.COLOR],
        'BorderStyle': [Element.ENUM],
        'Width': [Element.SIZE],
    }

    def __init__(self, node, lnk):
        super(Border, self).__init__(node, self.elements, lnk)


class RightBorder(Border):
    def __init__(self, node, lnk):
        super(RightBorder, self).__init__(node, lnk)


class LeftBorder(Border):
    def __init__(self, node, lnk):
        super(LeftBorder, self).__init__(node, lnk)


class TopBorder(Border):
    def __init__(self, node, lnk):
        super(TopBorder, self).__init__(node, lnk)


class BottomBorder(Border):
    def __init__(self, node, lnk):
        super(BottomBorder, self).__init__(node, lnk)


class BackgroundImage(Element):
    elements = {
        'ImageSource': [Element.ENUM, 1, True],
        'Value': [Element.VARIANT, 1],
        'MIMEType': [Element.STRING],
        'BackgroundRepeat': [Element.ENUM],
        'TransparentColor': [Element.COLOR],
        'Position': [Element.ENUM],
    }

    def __init__(self, node, lnk):
        super(Image, self).__init__('Image', node, lnk, self.elements)


class BackgroundImage(Element):
    elements = {
        'ImageSource': [Element.ENUM, 1, True],
        'BorderStyle': [Element.ENUM],
        'Width': [Element.SIZE],
    }

    def __init__(self, node, lnk):
        super(Border, self).__init__(node, self.elements, lnk)


class ReportItems(Element):
    elements = {
        'Line': [Element.ELEMENT, 3],
        'Rectangle': [Element.ELEMENT, 3],
        'Textbox': [Element.ELEMENT, 3],
        'Image': [Element.ELEMENT, 3],
        'Subreport': [Element.ELEMENT, 3],
        'Tablix': [Element.ELEMENT, 3],
        'Chart': [Element.ELEMENT, 3],
    }

    def __init__(self, node, lnk):
        self.reportitems_list = []
        super(ReportItems, self).__init__(node, self.elements, lnk)


class _ReportItem(_ReportElement):
    elements = {
        'Name': [Element.STRING, 1, True],
        'ActionInfo': [],
        'Top': [Element.SIZE, 0, True],
        'Left': [Element.SIZE, 0, True],
        'Height': [Element.SIZE, 0, True],
        'Width': [Element.SIZE, 0, True],
        'ZIndex': [Element.INTEGER, 0, True, -1],
        'Visibility': [],
        'ToolTip': [Element.STRING],
        'Bookmark': [Element.STRING],
        'RepeatWith': [Element.STRING, 0, True],
    }

    def __init__(self, type, node, lnk, additional_elements):
        el = Element.extend_element_list(
                _ReportItem, additional_elements)
        super(_ReportItem, self).__init__(node, el, lnk)
        self.type = type
        lnk.parent.reportitems_list.append(self)


class Line(_ReportItem):
    def __init__(self, node, lnk):
        super(Line, self).__init__('Line', node, lnk, None)


class Rectangle(_ReportItem):
    elements = {
        'ReportItems': [],
        'PageBreak': [],
        'OmitBorderOnPageBreak': [Element.BOOLEAN, 0, True],
    }

    def __init__(self, node, lnk):
        super(Rectangle, self).__init__('Rectangle', node, lnk, self.elements)


class Subreport(_ReportItem):
    elements = {
        'ReportName': [Element.STRING, 1, True],
        'Parameters': [],
        'NoRowsMessage': [Element.STRING],
        'MergeTransactions': [Element.BOOLEAN, 0, True],
        'OmitBorderOnPageBreak': [Element.BOOLEAN, 0, True],
    }

    def __init__(self, node, lnk):
        super(Subreport, self).__init__('Subreport', node, lnk, self.elements)


class Parameters(Element):
    elements = {'Parameter': [Element.ELEMENT, 2], }

    def __init__(self, node, lnk):
        super(Parameters, self).__init__(node, self.elements, lnk)


class Parameter(Element):
    elements = {
        'Name': [Element.STRING, 1, True],
        'Value': [Element.VARIANT, 1],
        'Omit': [Element.BOOLEAN],
    }

    def __init__(self, node, lnk):
        super(Parameter, self).__init__(node, self.elements, lnk)


class Image(_ReportItem):
    elements = {
        'ImageSource': [Element.ENUM, 1, True],
        'Value': [Element.VARIANT, 1],
        'MIMEType': [Element.STRING],
        'ImageSizing': [Element.ENUM, 0, True],
    }

    def __init__(self, node, lnk):
        super(Image, self).__init__('Image', node, lnk, self.elements)


class Textbox(_ReportItem):
    elements = {
        'Value': [Element.VARIANT, 0],
        'CanGrow': [Element.BOOLEAN, 0, True],
        'CanShrink': [Element.BOOLEAN, 0, True],
        'HideDuplicates': [Element.STRING, 0, True],
        'ToggleImage': [],
    }

    def __init__(self, node, lnk):
        super(Textbox, self).__init__("Textbox", node, lnk, self.elements)


class ToggleImage(Element):
    elements = {'InitialState': [Element.BOOLEAN, 1], }

    def __init__(self, node, lnk):
        super(ToggleImage, self).__init__(node, self.elements, lnk)


class _DataRegion(_ReportItem):
    elements = {
        'NoRowsMessage': [Element.STRING],
        'DataSetName': [Element.STRING, 0, True],
        'PageBreak': [],
        'Filters': [],
        'SortExpressions': [],
    }

    def __init__(self, type, node, lnk, additional_elements):
        el = Element.extend_element_list(
                _DataRegion, additional_elements)
        super(_DataRegion, self).__init__(type, node, lnk, el)


class Tablix(_DataRegion):
    elements = {
        'TablixCorner': [],
        'TablixBody': [Element.ELEMENT, 1],
        'TablixColumnHierarchy': [Element.ELEMENT, 1],
        'TablixRowHierarchy': [Element.ELEMENT, 1],
        'LayoutDirection': [Element.ENUM, 0, True],
        'GroupsBeforeRowHeaders': [Element.INTEGER, 0, True],
        'RepeatColumnHeaders': [Element.BOOLEAN, 0, True],
        'RepeatRowHeaders': [Element.BOOLEAN, 0, True],
        'FixedColumnHeaders': [Element.BOOLEAN, 0, True],
        'FixedRowHeaders': [Element.BOOLEAN, 0, True],
        'OmitBorderOnPageBreak': [Element.BOOLEAN, 0, True],
    }

    def __init__(self, node, lnk):
        super(Tablix, self).__init__('Tablix', node, lnk, self.elements)


class TablixCorner(Element):
    elements = {'TablixCornerRows': [Element.ELEMENT, 1], }

    def __init__(self, node, lnk):
        super(TablixCorner, self).__init__(node, self.elements, lnk)


class TablixCornerRows(Element):
    elements = {'TablixCornerRow': [Element.ELEMENT, 2], }

    def __init__(self, node, lnk):
        super(TablixCornerRows, self).__init__(node, self.elements, lnk)


class TablixCornerRow(Element):
    elements = {'TablixCornerCell': [Element.ELEMENT, 2], }

    def __init__(self, node, lnk):
        super(TablixCornerRow, self).__init__(node, self.elements, lnk)


class TablixCornerCell(Element):
    elements = {'CellContents': [], }

    def __init__(self, node, lnk):
        super(TablixCornerCell, self).__init__(node, self.elements, lnk)


class CellContents(Element):
    elements = {
        'ReportItems': [],
        'ColSpan': [Element.INTEGER, 0, True],
        'RowSpan': [Element.INTEGER, 0, True],
    }

    def __init__(self, node, lnk):
        super(CellContents, self).__init__(node, self.elements, lnk)


class TablixHierarchy(Element):
    elements = {'TablixMembers': [Element.ELEMENT, 1], }

    def __init__(self, node, lnk):
        super(TablixHierarchy, self).__init__(node, self.elements, lnk)


class TablixRowHierarchy(TablixHierarchy):
    def __init__(self, node, lnk):
        super(TablixRowHierarchy, self).__init__(node, lnk)


class TablixColumnHierarchy(TablixHierarchy):
    def __init__(self, node, lnk):
        super(TablixColumnHierarchy, self).__init__(node, lnk)


class TablixMembers(Element):
    elements = {'TablixMember': [Element.ELEMENT, 2], }

    def __init__(self, node, lnk):
        self.member_list = []
        super(TablixMembers, self).__init__(node, self.elements, lnk)


class TablixMember(Element):
    elements = {
        'Group': [],
        'TablixHeader': [],
        'TablixMembers': [],
        'FixedData': [Element.BOOLEAN, 0, True],
        'Visibility': [],
        'HideIfNoRows': [Element.BOOLEAN, 0, True],
        'RepeatOnNewPage': [Element.BOOLEAN, 0, True],
    }

    def __init__(self, node, lnk):
        super(TablixMember, self).__init__(node, self.elements, lnk)
        lnk.parent.member_list.append(self)


class TablixHeader(Element):
    elements = {
        'Size': [Element.SIZE, 1, True],
        'CellContents': [Element.ELEMENT, 1],
    }

    def __init__(self, node, lnk):
        super(TablixHeader, self).__init__(node, self.elements, lnk)


class TablixBody(Element):
    elements = {
        'TablixColumns': [Element.ELEMENT, 1],
        'TablixRows': [Element.ELEMENT, 1],
    }

    def __init__(self, node, lnk):
        super(TablixBody, self).__init__(node, self.elements, lnk)


class TablixColumns(Element):
    elements = {'TablixColumn': [Element.ELEMENT, 2], }

    def __init__(self, node, lnk):
        self.column_list = []
        super(TablixColumns, self).__init__(node, self.elements, lnk)


class TablixColumn(Element):
    elements = {'Width': [Element.SIZE, 1, True], }

    def __init__(self, node, lnk):
        super(TablixColumn, self).__init__(node, self.elements, lnk)
        lnk.parent.column_list.append(self)


class TablixRows(Element):
    elements = {'TablixRow': [Element.ELEMENT, 2], }

    def __init__(self, node, lnk):
        self.row_list = []
        super(TablixRows, self).__init__(node, self.elements, lnk)


class TablixRow(Element):
    elements = {
        'Height': [Element.SIZE, 1, True],
        'TablixCells': [Element.ELEMENT, 1],
    }

    def __init__(self, node, lnk):
        super(TablixRow, self).__init__(node, self.elements, lnk)
        lnk.parent.row_list.append(self)


class TablixCells(Element):
    elements = {'TablixCell': [Element.ELEMENT, 2], }

    def __init__(self, node, lnk):
        self.cell_list = []
        super(TablixCells, self).__init__(node, self.elements, lnk)


class TablixCell(Element):
    elements = {'CellContents': [], }

    def __init__(self, node, lnk):
        super(TablixCell, self).__init__(node, self.elements, lnk)
        lnk.parent.cell_list.append(self)


class PageBreak(Element):
    elements = {'BreakLocation': [Element.ENUM, 1, True], }

    def __init__(self, node, lnk):
        super(PageBreak, self).__init__(node, self.elements, lnk)
