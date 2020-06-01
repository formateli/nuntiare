# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import sys
from . expression import (Expression, String, Boolean,  # noqa: F401
        Integer, Variant, Size, Color)                  # noqa: F401
from . enum import (BorderStyle, FontStyle,             # noqa: F401
        FontWeight, TextDecoration, TextAlign,          # noqa: F401
        VerticalAlign, TextDirection, WritingMode,      # noqa: F401
        BackgroundRepeat, BackgroundGradientType,       # noqa: F401
        DataType, SortDirection, Operator,              # noqa: F401
        BreakLocation, DataElementStyle,                # noqa: F401
        DataElementOutput)                              # noqa: F401
from .. import LOGGER
from .. data.data_type import DataType as dt
from .. tools import get_xml_tag_value

_ELEMENT_CLASSES = [
    'Page', 'PageHeader', 'PageFooter',
    'EmbeddedImages', 'EmbeddedImage',
    'Body', 'Visibility',
    'DataSources', 'DataSource', 'ConnectionProperties',
    'DataSets', 'DataSet', 'Fields', 'Field',
    'Query', 'QueryParameters', 'QueryParameter',
    'SortExpressions', 'SortExpression',
    'Filters', 'Filter', 'Group',
    'ReportParameters', 'ReportParameter',
    'ReportItems', 'Tablix',
    'TablixColumnHierarchy', 'TablixRowHierarchy',
    'TablixMembers', 'TablixMember', 'TablixCorner',
    'TablixCornerRows', 'TablixCornerRow',
    'TablixCornerCell', 'TablixBody', 'TablixHeader',
    'TablixColumns', 'TablixColumn',
    'TablixRows', 'TablixRow', 'TablixCells', 'TablixCell',
    'CellContents', 'Style', 'Border',
    'TopBorder', 'BottomBorder', 'LeftBorder', 'RightBorder',
    'BackgroundImage', 'Line', 'Rectangle', 'Textbox',
    'PageBreak', 'Image', 'Modules', 'Module'
]

_ENUM_CLASSES = [
    'BorderStyle', 'FontStyle', 'FontWeight',
    'TextDecoration', 'TextAlign', 'VerticalAlign',
    'TextDirection', 'WritingMode', 'BackgroundRepeat',
    'BackgroundGradientType', 'DataType',
    'SortDirection', 'Operator', 'BreakLocation',
    'DataElementStyle', 'DataElementOutput'
]

_EXPRESSION_CLASSES = [
    'String', 'Integer', 'Boolean',
    'Size', 'Color', 'Variant'
]

_EXPRESSION_LIST_CLASSES = [
    'FilterValues',
    'GroupExpressions'
]


class Card:
    ZERO_ONE = 0
    ONE = 1
    ONE_MANY = 2
    ZERO_MANY = 3


class Element:
    ELEMENT = 0
    STRING = 1
    INTEGER = 2
    BOOLEAN = 3
    FLOAT = 4
    SIZE = 5
    DATE = 6
    COLOR = 7
    EXPRESSION_LIST = 8
    ENUM = 9
    VARIANT = 90

    def __init__(self, node, elements, lnk):
        '''
        node: Xml node with the element definition.
        elements: A dictionary with the elements belonging to this element.
         key: Element name
         value: A list [] with the following values:
            Element type. Default: Element.ELEMENT
            Card: ElementCard value.
                Default: Card.ZERO_ONE
            Must be a constant: If true,
                this element value can not be an expression.
                Ignore if type is Element.ELEMENT. Default: False
            DefaultValue
                Ignore if type is Element.ELEMENT. Default: None
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
                        n.parentNode.nodeName == 'Nuntiare':
                    self.set_data()
                    continue
                if n.nodeName not in ('#text', '#comment'):
                    LOGGER.warn(
                        "Unknown element '{0}' for '{1}'. Ignored.".format(
                            n.nodeName, self.element_name))
                continue

            element_type, card, must_be_constant, default_value = \
                Element.get_element_def(elements[n.nodeName])

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
                    z_count += 1
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
                    Element.get_element_def(el)
                if card in [Card.ONE, Card.ONE_MANY]:
                    LOGGER.error(
                        "'{0}' must be defined for '{1}'.".format(
                            key, self.element_name), True)
                if default_value and element_type not in \
                        [Element.ELEMENT, Element.EXPRESSION_LIST]:
                    self._set_attr(
                        key, False, default_value, True)

        # Z Order
        reportitems_list = []
        if len(items_by_name) > 0:
            z_list = []
            for key, it in items_by_name.items():
                ls = (it[1], it[0])  # zindex, reportitem
                z_list.append(ls)
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
                    self._original_element_list[name])
        if result[0] in (
                Element.ELEMENT, Element.EXPRESSION_LIST):
            el = self.get_element(name)
            if el:
                self._set_attr(name, True, el, False)
                return self.__dict__[name]
        else:
            if result[2] is None:
                err_msg = "'{0}' is not a constant property " \
                    "for element '{1}'. Use get_value() instead."
                LOGGER.error(err_msg.format(name, self.element_name), True)
            else:
                self._set_attr(name, False, result[3], result[2])
                return self.__dict__[name]

    def _verify_element(self, name):
        if name not in self._original_element_list.keys():
            err_msg = "'{0}' is not a valid member for element '{1}'. " \
                "Valid are: {2}"
            LOGGER.error(err_msg.format(
                name, self.element_name,
                self._original_element_list.keys()), True)

    def get_value(self, report, name, default_value=None):
        if name in self.__dict__:
            return self.__dict__[name]
        self._verify_element(name)
        return Expression.get_value_or_default(
                report, self, name, default_value)

    @staticmethod
    def extend_element_list(orig, additional_elements):
        el = {}
        for key, value in orig.items():
            el[key] = value
        if additional_elements:
            for key, value in additional_elements.items():
                el[key] = value
        return el

    @staticmethod
    def _factory_get(name, class_name, class_list):
        if class_name not in class_list:
            err = "Invalid or not implementd {0} '{1}'. " \
                "Valid are: {2}"
            LOGGER.error(
                err.format(name, class_name, class_list), True)
        current_module = sys.modules[__name__]
        obj = getattr(current_module, class_name)
        return obj

    @staticmethod
    def element_factory(name, node, lnk):
        obj = Element._factory_get(
            'Element', name, _ELEMENT_CLASSES)
        ln = Link(lnk.report_def, lnk.obj)
        return obj(node, ln)

    @staticmethod
    def enum_factory(name, node, lnk, card, must_be_constant):
        obj = Element._factory_get(
            'Enum', name, _ENUM_CLASSES)
        value = get_xml_tag_value(node)
        if card in [Card.ONE, Card.ONE_MANY] \
                and value is None:
            LOGGER.error("'{0}' is required by '{1}'.".format(
                node.nodeName, lnk.obj.__class__.__name__), True)
        return obj(value, lnk, must_be_constant)

    @staticmethod
    def expression_list_factory(name, node, lnk):
        obj = Element._factory_get(
            'ExpressionList', name, _EXPRESSION_LIST_CLASSES)
        ln = Link(lnk.report_def, lnk.obj)
        return obj(node, ln)

    @staticmethod
    def expression_factory(name, node, lnk, card, must_be_constant):
        def get_class_name(name_i):
            result = 'Unknown_' + str(name_i)
            if name_i == Element.STRING:
                result = 'String'
            if name_i == Element.INTEGER:
                result = 'Integer'
            if name_i == Element.BOOLEAN:
                result = 'Boolean'
            if name_i == Element.SIZE:
                result = 'Size'
            if name_i == Element.COLOR:
                result = 'Color'
            if name_i == Element.VARIANT:
                result = 'Variant'
            return result

        class_name = get_class_name(name)
        obj = Element._factory_get(
            'Expression', class_name, _EXPRESSION_CLASSES)
        ln = Link(lnk.report_def, lnk.obj, data=node.nodeName)
        value = get_xml_tag_value(node)
        if card in [Card.ONE, Card.ONE_MANY] and \
                value is None:
            LOGGER.error("'{0}' is required by '{1}'.".format(
                node.nodeName, lnk.obj.__class__.__name__), True)
        return obj(value, ln, must_be_constant)

    @staticmethod
    def get_element_def(element):
        element_type = Element.ELEMENT
        card = Card.ZERO_ONE
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
                if element[3] is not None:
                    default_value = element[3]

            # len(element)==4 is ignored, it means that element was checked

        return element_type, card, must_be_constant, default_value

    def get_element(self, name):
        if name in self.element_list:
            return self.element_list[name]

    def has_element(self, name):
        el = self.get_element(name)
        if el:
            return True


class Link:
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


class _ExpressionList:
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
                Element.get_element_def(elements[n.nodeName])

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
            # Loads the Data embedded in definition file
            self._curr_data_name = None
            self._curr_index = 0
            root = report.definition.node
            data = root.getElementsByTagName('DataEmbedded')
            self._get_data(data[0])
            self._loaded = True

        def get_data(self, data_name):
            if data_name in self.data:
                return self.data[data_name]
            err_msg = "Attempted to get data '{0}' from DataEmbedded, " \
                "but it does not exist"
            LOGGER.warn(err_msg.format(data_name))

        def reset(self):
            self.data = {}

        def _get_data(self, node):
            def add_record(name, node):
                row = []
                for field in node.childNodes:
                    if field.nodeName in ('#text', '#comment'):
                        continue
                    row.append(field.firstChild.nodeValue)
                self.data[name].append(row)

            def create_data(node):
                name_el = node.getElementsByTagName('Name')
                name = name_el[0].firstChild.nodeValue
                self.data[name] = []
                records = node.getElementsByTagName('Records')
                for n in records[0].childNodes:
                    if n.nodeName == 'Record':
                        add_record(name, n)

            for n in node.childNodes:
                if n.nodeName == 'Data':
                    create_data(n)

    def __init__(self, node):
        LOGGER.info('Initializing report definition...')

        self.elements = {
            'Name': [Element.STRING, Card.ONE, True],
            'Description': [Element.STRING, Card.ZERO_ONE, True],
            'Author': [Element.STRING, Card.ZERO_ONE, True],
            'Version': [Element.STRING, Card.ZERO_ONE, True],
            'DateCreate': [Element.DATE, Card.ZERO_ONE, True],
            'DateUpdate': [Element.DATE, Card.ZERO_ONE, True],
            'DataSources': [],
            'DataSets': [],
            'Body': [Element.ELEMENT, Card.ONE],
            'ReportParameters': [],
            'Modules': [],
            'EmbeddedImages': [],
            'Page': [Element.ELEMENT, Card.ONE],
            'Language': [Element.STRING, Card.ZERO_ONE, True],
            'DataElementName': [
                Element.STRING, Card.ZERO_ONE, True, 'Nuntiare'],
            'DataElementStyle': [
                Element.ENUM, Card.ZERO_ONE, True, 'Attribute'],
        }

        self.parameters_def = []
        self.data_sources = []
        self.data_sets = []
        self.modules = []
        self.report_items = {}  # only textboxes
        self.report_items_group = {}
        self.data = None
        self.node = node

        lnk = Link(None, None, self)
        super(Nuntiare, self).__init__(node, self.elements, lnk)

    def get_parameter_def(self, parameter_name):
        for p in self.parameters_def:
            if p.Name == parameter_name:
                return p

    def set_data(self):
        self.data = Nuntiare.Data()


class EmbeddedImages(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'EmbeddedImage': [Element.ELEMENT, Card.ONE_MANY], }
        super(EmbeddedImages, self).__init__(node, self.elements, lnk)

    @staticmethod
    def embed_image_file(xml_file, image_file, name, mimetype):
        name, mimetype, image_string = EmbeddedImage.get_base64_image(
                image_file, name, mimetype)
        EmbeddedImages.embed_image_base64(
                xml_file, image_string, name, mimetype)

    @staticmethod
    def embed_image_base64(xml_file, image_string, name, mimetype):
        from xml.dom import minidom

        def create_text_node(dom, parent_el, child, txt):
            child_el = dom.createElement(child)
            child_el.appendChild(dom.createTextNode(txt))
            parent_el.appendChild(child_el)

        def replace_text_node(dom, parent_el, child, txt):
            found = False
            for node in parent_el.childNodes:
                if node.nodeName == child:
                    node.firstChild.replaceWholeText(txt)
                    found = True
            if not found:
                create_text_node(dom, parent_el, child, txt)

        # This routine is necesary to avoid
        # lines spaces when file is saved using toprettyxml
        with open(xml_file, 'rb') as file_read:
            data = file_read.read()
        data = data.decode('utf-8')
        reparsed = minidom.parseString(data)
        data = ''
        for line in reparsed.toprettyxml(indent=' ').split('\n'):
            st = line.strip()
            if st:
                data += st

        dom = minidom.parseString(data)

        root = dom.getElementsByTagName('Nuntiare')[0]
        ei = dom.getElementsByTagName('EmbeddedImages')
        if not ei:
            ei_element = dom.createElement('EmbeddedImages')
            root.appendChild(ei_element)
        else:
            ei_element = ei[0]

        image_element = None
        for el in ei_element.childNodes:
            if el.nodeName == 'EmbeddedImage':
                for node in el.childNodes:
                    if node.nodeName == 'Name':
                        if node.firstChild.nodeValue == name:
                            image_element = el

        if image_element is None:
            image_element = dom.createElement('EmbeddedImage')
            create_text_node(dom, image_element, 'Name', name)
            create_text_node(dom, image_element, 'MIMEType', mimetype)
            create_text_node(dom, image_element, 'ImageData', image_string)
            ei_element.appendChild(image_element)
        else:
            replace_text_node(dom, image_element, 'MIMEType', mimetype)
            replace_text_node(dom, image_element, 'ImageData', image_string)

        with open(xml_file, 'wb') as file_write:
            file_write.write(dom.toprettyxml(indent='  ', encoding='utf-8'))


class EmbeddedImage(Element):

    _mimetype_valid = {
        'image/bmp': 'BMP',
        'image/jpeg': 'JPG',
        'image/gif': 'GIF',
        'image/png': 'PNG',
        'image/xpng': 'PNG'
        }

    def __init__(self, node, lnk):
        self.elements = {
            'Name': [Element.STRING, Card.ONE, True],
            'MIMEType': [Element.STRING, Card.ONE, True],
            'ImageData': [Element.STRING, Card.ONE, True],
        }
        super(EmbeddedImage, self).__init__(node, self.elements, lnk)

    @classmethod
    def get_base64_image(cls, image_file, name=None, mimetype=None):
        """ Return a Base64 string reporesentation
            along with its name and mimetype of Image file.
            name and mimetype can be inferred from image_file if
            they are not provided. 
        """
        import base64
        from PIL import Image
        import base64
        import io
        import os

        filename, ext = os.path.splitext(os.path.basename(image_file))

        if name is None:
            name = filename

        if mimetype is None:
            ext = ext.lower()[1:]
            if ext == 'bmp':
                mimetype = 'image/bmp'
            elif ext in ['jpg', 'jpeg']:
                mimetype = 'image/jpeg'
            elif ext == 'gif':
                mimetype = 'image/gif'
            elif ext == 'png':
                mimetype = 'image/png'
            else:
                LOGGER.error(
                    "MIMEType can not be inferred from {0} extension".format(
                        ext), raise_error=True)

        mimetype = mimetype.lower()
        if mimetype not in cls._mimetype_valid:
            LOGGER.error(
                "Invalid MIMEType '{0}' for '{1}' image.".format(
                    mimetype, name), raise_error=True)

        buffered = io.BytesIO()
        img = Image.open(image_file)
        img.show()
        img.save(buffered, format=cls._mimetype_valid[mimetype])
        img_str = base64.b64encode(buffered.getvalue())
        res = img_str.decode('utf-8')

        #test = Image.open(io.BytesIO(base64.b64decode(res)))

        return name, mimetype, res


class Modules(Element):
    def __init__(self, node, lnk):
        self.elements = {'Module': [Element.ELEMENT, Card.ONE_MANY], }
        self.modules = []
        super(Modules, self).__init__(node, self.elements, lnk)


class Module(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'From': [Element.STRING, Card.ZERO_ONE, True],
            'Import': [Element.STRING, Card.ZERO_ONE, True],
            'As': [Element.STRING, Card.ZERO_ONE, True],
        }
        super(Module, self).__init__(node, self.elements, lnk)
        lnk.parent.modules.append(self)


class ReportParameters(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'ReportParameter': [Element.ELEMENT, Card.ONE_MANY], }
        super(ReportParameters, self).__init__(node, self.elements, lnk)


class ReportParameter(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'Name': [Element.STRING, Card.ONE, True],
            'DataType': [Element.ENUM, Card.ZERO_ONE, True, 'String'],
            'CanBeNone': [Element.BOOLEAN, Card.ZERO_ONE, True, True],
            'AllowBlank': [Element.BOOLEAN, Card.ZERO_ONE, True, True],
            'DefaultValue': [Element.VARIANT, Card.ONE],
            'Promt': [Element.STRING],
        }
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
                not self.AllowBlank and self.DataType == 'String':
            LOGGER.error(
                "Parameter '{0}' value can not be an empty string.".format(
                    self.Name), True)

        return result


class Visibility(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'Hidden': [Element.BOOLEAN, Card.ZERO_ONE],
            'ToggleItem': [Element.STRING, Card.ZERO_ONE, True],
        }
        super(Visibility, self).__init__(node, self.elements, lnk)


class Page(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'PageHeader': [],
            'PageFooter': [],
            'PageHeight': [Element.SIZE, Card.ZERO_ONE, True, 11 * 72],
            'PageWidth': [Element.SIZE, Card.ZERO_ONE, True, 8.5 * 72],
            'LeftMargin': [Element.SIZE, Card.ZERO_ONE, True, 0.0],
            'RightMargin': [Element.SIZE, Card.ZERO_ONE, True, 0.0],
            'TopMargin': [Element.SIZE, Card.ZERO_ONE, True, 0.0],
            'BottomMargin': [Element.SIZE, Card.ZERO_ONE, True, 0.0],
            'Columns': [Element.INTEGER, Card.ZERO_ONE, True, 1],
            'ColumnSpacing': [Element.SIZE, Card.ZERO_ONE, True, 0.5 * 72],
            'Style': [],
        }
        super(Page, self).__init__(node, self.elements, lnk)


class _PageSection(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'ReportItems': [],
            'Height': [Element.SIZE, Card.ONE, True, 0.0],
            'PrintOnFirstPage': [
                Element.BOOLEAN, Card.ZERO_ONE, True],
            'PrintOnLastPage': [
                Element.BOOLEAN, Card.ZERO_ONE, True],
            'Style': [],
        }
        super(_PageSection, self).__init__(node, self.elements, lnk)


class PageHeader(_PageSection):
    def __init__(self, node, lnk):
        super(PageHeader, self).__init__(node, lnk)


class PageFooter(_PageSection):
    def __init__(self, node, lnk):
        super(PageFooter, self).__init__(node, lnk)


class Body(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'ReportItems': [],
            'Style': [],
        }
        super(Body, self).__init__(node, self.elements, lnk)


class DataSources(Element):
    def __init__(self, node, lnk):
        self.elements = {'DataSource': [Element.ELEMENT, Card.ONE_MANY], }
        super(DataSources, self).__init__(node, self.elements, lnk)


class DataSource(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'Name': [Element.STRING, Card.ONE, True],
            'Transaction': [Element.BOOLEAN, Card.ZERO_ONE, True],
            'ConnectionProperties': [],
        }
        super(DataSource, self).__init__(node, self.elements, lnk)
        self.conn_properties = self.get_element('ConnectionProperties')
        for ds in lnk.report_def.data_sources:
            if ds.Name == self.Name:
                LOGGER.error(
                    "Report already has a DataSource with name '{0}'".format(
                        self.name), True)
        lnk.report_def.data_sources.append(self)


class ConnectionProperties(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'DataProvider': [Element.STRING, Card.ONE],
            'ConnectObject': [Element.VARIANT, Card.ONE],
            'Prompt': [Element.STRING, Card.ZERO_ONE, True],
        }
        super(ConnectionProperties, self).__init__(node, self.elements, lnk)


class DataSets(Element):
    def __init__(self, node, lnk):
        self.elements = {'DataSet': [Element.ELEMENT, Card.ONE_MANY], }
        super(DataSets, self).__init__(node, self.elements, lnk)


class DataSet(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'Name': [Element.STRING, Card.ONE, True],
            'Fields': [],
            'Query': [Element.ELEMENT, Card.ONE],
            'Filters': [],
            'SortExpressions': [],
        }
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
    def __init__(self, node, lnk):
        self.elements = {'Field': [Element.ELEMENT, Card.ONE_MANY], }
        super(Fields, self).__init__(node, self.elements, lnk)


class Field(Element):
    '''
    The Field element contains information about a field in
    the data model of the report.
    '''
    def __init__(self, node, lnk):
        self.elements = {
            'Name': [Element.STRING, Card.ONE, True],
            'DataType': [Element.ENUM, Card.ZERO_ONE, True, 'String'],
            'DataField': [Element.STRING, Card.ZERO_ONE, True],
            'Value': [Element.VARIANT],
        }
        super(Field, self).__init__(node, self.elements, lnk)
        data_set = lnk.parent.lnk.parent  # Get Dataset
        for fd in data_set.fields:
            if fd.Name == self.Name:
                LOGGER.error(
                    "DataSet already has '{0}' Field.".format(
                        self.name), True)
        data_set.fields.append(self)


class Query(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'DataSourceName': [Element.STRING, Card.ONE, True],
            'CommandText': [Element.STRING],
            'QueryParameters': [],
        }
        super(Query, self).__init__(node, self.elements, lnk)

    def get_command_text(self, report):
        cmd = Expression.get_value_or_default(
            report, self, 'CommandText', None)
        if not cmd:
            LOGGER.error(
                "'CommandText' is required by 'Query' element.", True)
        return cmd


class QueryParameters(Element):
    def __init__(self, node, lnk):
        self.elements = {'QueryParameter': [Element.ELEMENT, Card.ONE_MANY], }
        super(QueryParameters, self).__init__(node, self.elements, lnk)


class QueryParameter(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'Name': [Element.STRING, Card.ONE, True],
            'Value': [Element.VARIANT, Card.ONE],
        }
        super(QueryParameter, self).__init__(node, self.elements, lnk)


class Filters(Element):
    def __init__(self, node, lnk):
        self.elements = {'Filter': [Element.ELEMENT, Card.ONE_MANY], }
        self.filter_list = []
        super(Filters, self).__init__(node, self.elements, lnk)


class Filter(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'FilterExpression': [Element.VARIANT, Card.ONE],
            'Operator': [Element.ENUM, Card.ONE, True],
            'FilterValues': [Element.EXPRESSION_LIST, Card.ONE],
        }
        super(Filter, self).__init__(node, self.elements, lnk)
        lnk.parent.filter_list.append(self)


class FilterValues(_ExpressionList):
    def __init__(self, node, lnk):
        self.elements = {'FilterValue': [Element.VARIANT, Card.ONE_MANY], }
        super(FilterValues, self).__init__(node, self.elements, lnk)


class Group(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'Name': [Element.STRING, Card.ONE, True],
            'GroupExpressions': [Element.EXPRESSION_LIST],
            'PageBreak': [],
            'Filters': [],
            'SortExpressions': [],
            'Parent': [Element.VARIANT],
            'DataElementName': [Element.STRING, Card.ZERO_ONE, True],
            'DataElementOutput': [
                    Element.ENUM, Card.ZERO_ONE, True, 'Output'],
        }
        super(Group, self).__init__(node, self.elements, lnk)


class GroupExpressions(_ExpressionList):
    def __init__(self, node, lnk):
        self.elements = {
                'GroupExpression': [Element.VARIANT, Card.ONE_MANY], }
        super(GroupExpressions, self).__init__(node, self.elements, lnk)


class SortExpressions(Element):
    def __init__(self, node, lnk):
        self.elements = {'SortExpression': [Element.ELEMENT, Card.ONE_MANY], }
        self.sortby_list = []
        super(SortExpressions, self).__init__(node, self.elements, lnk)


class SortExpression(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'Value': [Element.VARIANT, Card.ONE],
            'SortDirection': [Element.ENUM, Card.ZERO_ONE, True, 'Ascending'],
        }
        super(SortExpression, self).__init__(node, self.elements, lnk)
        lnk.parent.sortby_list.append(self)


class Style(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'Border': [],
            'TopBorder': [],
            'BottomBorder': [],
            'LeftBorder': [],
            'RightBorder': [],
            'BackgroundColor': [Element.COLOR],
            'BackgroundGradientType': [Element.ENUM],
            'BackgroundGradientEndColor': [Element.COLOR],
            'BackgroundImage': [],
            'FontStyle': [Element.ENUM, Card.ZERO_ONE, False, 'Normal'],
            'FontFamily': [Element.STRING, Card.ZERO_ONE, False, 'Arial'],
            'FontSize': [Element.SIZE, Card.ZERO_ONE, False, 10],
            'FontWeight': [Element.ENUM, Card.ZERO_ONE, False, 'Normal'],
            'Format': [Element.STRING],
            'TextDecoration': [Element.ENUM, Card.ZERO_ONE, False, 'None'],
            'TextAlign': [Element.ENUM, Card.ZERO_ONE, False, 'General'],
            'VerticalAlign': [Element.ENUM, Card.ZERO_ONE, False, 'Top'],
            'Color': [Element.COLOR, Card.ZERO_ONE, False, '#000000'],
            'PaddingLeft': [Element.SIZE, Card.ZERO_ONE, False, 0.0],
            'PaddingRight': [Element.SIZE, Card.ZERO_ONE, False, 0.0],
            'PaddingTop': [Element.SIZE, Card.ZERO_ONE, False, 0.0],
            'PaddingBottom': [Element.SIZE, Card.ZERO_ONE, False, 0.0],
            'LineHeight': [Element.SIZE, Card.ZERO_ONE, False, 1.0],
            'TextDirection': [Element.ENUM, Card.ZERO_ONE, False, 'LTR'],
            'WritingMode': [Element.ENUM, Card.ZERO_ONE, False, 'Horizontal'],
        }
        super(Style, self).__init__(node, self.elements, lnk)


class Border(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'Color': [Element.COLOR, Card.ZERO_ONE, False, '#000000'],
            'BorderStyle': [Element.ENUM, Card.ZERO_ONE, False],
            'Width': [Element.SIZE, Card.ZERO_ONE, False, 1],
        }
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
    def __init__(self, node, lnk):
        self.elements = {
            'ImageSource': [Element.ENUM, Card.ONE, True],
            'Value': [Element.VARIANT, Card.ONE],
            'MIMEType': [Element.STRING],
            'BackgroundRepeat': [Element.ENUM],
            'TransparentColor': [Element.COLOR],

            'Position': [Element.ENUM],
        }
        super(BackgroundImage, self).__init__(
                'Image', node, lnk, self.elements)


class ReportItems(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'Line': [Element.ELEMENT, Card.ZERO_MANY],
            'Rectangle': [Element.ELEMENT, Card.ZERO_MANY],
            'Textbox': [Element.ELEMENT, Card.ZERO_MANY],
            'Image': [Element.ELEMENT, Card.ZERO_MANY],
            'Subreport': [Element.ELEMENT, Card.ZERO_MANY],
            'Tablix': [Element.ELEMENT, Card.ZERO_MANY],
            'Chart': [Element.ELEMENT, Card.ZERO_MANY],
        }
        self.reportitems_list = []
        super(ReportItems, self).__init__(node, self.elements, lnk)


class _ReportItem(Element):
    def __init__(self, type, node, lnk, additional_elements):
        self.elements = {
            'Name': [Element.STRING, Card.ONE, True],
            'ActionInfo': [],
            'Top': [Element.SIZE, Card.ZERO_ONE, True],
            'Left': [Element.SIZE, Card.ZERO_ONE, True],
            'Height': [Element.SIZE, Card.ZERO_ONE, True],
            'Width': [Element.SIZE, Card.ZERO_ONE, True],
            'ZIndex': [Element.INTEGER, Card.ZERO_ONE, True, -1],
            'Visibility': [],
            'ToolTip': [Element.STRING],
            'Bookmark': [Element.STRING],
            'RepeatWith': [Element.STRING, Card.ZERO_ONE, True],
            'Style': [],
            'DataElementName': [Element.STRING, Card.ZERO_ONE, True],
            'DataElementOutput': [Element.ENUM, Card.ZERO_ONE, True, 'Auto'],
        }
        self.elements = Element.extend_element_list(
                self.elements, additional_elements)
        super(_ReportItem, self).__init__(node, self.elements, lnk)
        self.type = type
        lnk.parent.reportitems_list.append(self)


class Line(_ReportItem):
    def __init__(self, node, lnk):
        super(Line, self).__init__('Line', node, lnk, None)


class Rectangle(_ReportItem):
    def __init__(self, node, lnk):
        self.elements = {
            'ReportItems': [],
            'PageBreak': [],
            'KeepTogether': [Element.BOOLEAN, 0, True, False],
            'OmitBorderOnPageBreak': [Element.BOOLEAN, 0, True, True],
        }
        super(Rectangle, self).__init__('Rectangle', node, lnk, self.elements)


class Subreport(_ReportItem):
    def __init__(self, node, lnk):
        self.elements = {
            'ReportName': [Element.STRING, Card.ONE, True],
            'Parameters': [],
            'NoRowsMessage': [Element.STRING],
            'KeepTogether': [Element.BOOLEAN, Card.ZERO_ONE, True, False],
            'MergeTransactions': [Element.BOOLEAN, Card.ZERO_ONE, True],
            'OmitBorderOnPageBreak': [Element.BOOLEAN, Card.ZERO_ONE, True],
        }
        super(Subreport, self).__init__('Subreport', node, lnk, self.elements)


class Parameters(Element):
    def __init__(self, node, lnk):
        self.elements = {'Parameter': [Element.ELEMENT, Card.ONE_MANY], }
        super(Parameters, self).__init__(node, self.elements, lnk)


class Parameter(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'Name': [Element.STRING, Card.ONE, True],
            'Value': [Element.VARIANT, Card.ONE],
            'Omit': [Element.BOOLEAN],
        }
        super(Parameter, self).__init__(node, self.elements, lnk)


class Image(_ReportItem):
    def __init__(self, node, lnk):
        self.elements = {
            'ImageSource': [Element.ENUM, Card.ONE, True],
            'Value': [Element.VARIANT, Card.ONE],
            'MIMEType': [Element.STRING],
            'ImageSizing': [Element.ENUM, Card.ZERO_ONE, True, 'AutoSize'],
        }
        super(Image, self).__init__('Image', node, lnk, self.elements)


class Textbox(_ReportItem):
    def __init__(self, node, lnk):
        self.elements = {
            'Value': [Element.VARIANT, Card.ZERO_ONE],
            'CanGrow': [Element.BOOLEAN, Card.ZERO_ONE, True],
            'CanShrink': [Element.BOOLEAN, Card.ZERO_ONE, True],
            'KeepTogether': [Element.BOOLEAN, Card.ZERO_ONE, True, False],
            'HideDuplicates': [Element.STRING, Card.ZERO_ONE, True],
            'ToggleImage': [],
            'DataElementStyle': [
                Element.ENUM, Card.ZERO_ONE, True, 'Auto'],
        }
        super(Textbox, self).__init__('Textbox', node, lnk, self.elements)


class ToggleImage(Element):
    def __init__(self, node, lnk):
        self.elements = {'InitialState': [Element.BOOLEAN, Card.ONE], }
        super(ToggleImage, self).__init__(node, self.elements, lnk)


class _DataRegion(_ReportItem):
    def __init__(self, type, node, lnk, additional_elements):
        self.elements = {
            'NoRowsMessage': [Element.STRING],
            'DataSetName': [Element.STRING, Card.ZERO_ONE, True],
            'PageBreak': [],
            'Filters': [],
            'SortExpressions': [],
        }
        self.elements = Element.extend_element_list(
                self.elements, additional_elements)
        super(_DataRegion, self).__init__(type, node, lnk, self.elements)


class Tablix(_DataRegion):
    def __init__(self, node, lnk):
        self.elements = {
            'TablixCorner': [],
            'TablixBody': [Element.ELEMENT, Card.ONE],
            'TablixColumnHierarchy': [Element.ELEMENT, Card.ONE],
            'TablixRowHierarchy': [Element.ELEMENT, Card.ONE],
            'LayoutDirection': [Element.ENUM, Card.ZERO_ONE, True, 'LTR'],
            'GroupsBeforeRowHeaders': [Element.INTEGER, Card.ZERO_ONE, True],
            'RepeatColumnHeaders': [Element.BOOLEAN, Card.ZERO_ONE, True],
            'RepeatRowHeaders': [Element.BOOLEAN, Card.ZERO_ONE, True],
            'FixedColumnHeaders': [Element.BOOLEAN, Card.ZERO_ONE, True],
            'FixedRowHeaders': [Element.BOOLEAN, Card.ZERO_ONE, True],
            'KeepTogether': [Element.BOOLEAN, Card.ZERO_ONE, True, False],
            'OmitBorderOnPageBreak': [Element.BOOLEAN, Card.ZERO_ONE, True],
        }
        super(Tablix, self).__init__('Tablix', node, lnk, self.elements)


class TablixCorner(Element):
    def __init__(self, node, lnk):
        self.elements = {'TablixCornerRows': [Element.ELEMENT, Card.ONE], }
        super(TablixCorner, self).__init__(node, self.elements, lnk)


class TablixCornerRows(Element):
    def __init__(self, node, lnk):
        self.elements = {
                'TablixCornerRow': [Element.ELEMENT, Card.ONE_MANY], }
        self.row_list = []
        super(TablixCornerRows, self).__init__(node, self.elements, lnk)


class TablixCornerRow(Element):
    def __init__(self, node, lnk):
        self.elements = {'TablixCornerCell': [Element.ELEMENT, 2], }
        self.cell_list = []
        super(TablixCornerRow, self).__init__(node, self.elements, lnk)
        lnk.parent.row_list.append(self)


class TablixCornerCell(Element):
    def __init__(self, node, lnk):
        self.elements = {'CellContents': [], }
        super(TablixCornerCell, self).__init__(node, self.elements, lnk)
        lnk.parent.cell_list.append(self)


class CellContents(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'ReportItems': [],
            'ColSpan': [Element.INTEGER, Card.ZERO_ONE, True],
            'RowSpan': [Element.INTEGER, Card.ZERO_ONE, True],
        }
        super(CellContents, self).__init__(node, self.elements, lnk)


class _TablixHierarchy(Element):
    def __init__(self, node, lnk):
        self.elements = {'TablixMembers': [Element.ELEMENT, Card.ONE], }
        super(_TablixHierarchy, self).__init__(node, self.elements, lnk)


class TablixRowHierarchy(_TablixHierarchy):
    def __init__(self, node, lnk):
        super(TablixRowHierarchy, self).__init__(node, lnk)


class TablixColumnHierarchy(_TablixHierarchy):
    def __init__(self, node, lnk):
        super(TablixColumnHierarchy, self).__init__(node, lnk)


class TablixMembers(Element):
    def __init__(self, node, lnk):
        self.elements = {'TablixMember': [Element.ELEMENT, Card.ONE_MANY], }
        self.member_list = []
        super(TablixMembers, self).__init__(node, self.elements, lnk)


class TablixMember(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'Group': [],
            'TablixHeader': [],
            'TablixMembers': [],
            'FixedData': [Element.BOOLEAN, Card.ZERO_ONE, True],
            'Visibility': [],
            'KeepTogether': [Element.BOOLEAN, Card.ZERO_ONE, True, False],
            'HideIfNoRows': [Element.BOOLEAN, Card.ZERO_ONE, True],
            'RepeatOnNewPage': [Element.BOOLEAN, Card.ZERO_ONE, True],
            'DataElementName': [Element.STRING, Card.ZERO_ONE, True],
            'DataElementOutput': [Element.ENUM, Card.ZERO_ONE, True, 'Auto'],
        }
        super(TablixMember, self).__init__(node, self.elements, lnk)
        lnk.parent.member_list.append(self)


class TablixHeader(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'Size': [Element.SIZE, Card.ONE, True],
            'CellContents': [Element.ELEMENT, Card.ONE],
        }
        super(TablixHeader, self).__init__(node, self.elements, lnk)


class TablixBody(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'TablixColumns': [Element.ELEMENT, Card.ONE],
            'TablixRows': [Element.ELEMENT, Card.ONE],
        }
        super(TablixBody, self).__init__(node, self.elements, lnk)


class TablixColumns(Element):
    def __init__(self, node, lnk):
        self.elements = {'TablixColumn': [Element.ELEMENT, Card.ONE_MANY], }
        self.column_list = []
        super(TablixColumns, self).__init__(node, self.elements, lnk)


class TablixColumn(Element):
    def __init__(self, node, lnk):
        self.elements = {'Width': [Element.SIZE, Card.ONE, True], }
        super(TablixColumn, self).__init__(node, self.elements, lnk)
        lnk.parent.column_list.append(self)


class TablixRows(Element):
    def __init__(self, node, lnk):
        self.elements = {'TablixRow': [Element.ELEMENT, Card.ONE_MANY], }
        self.row_list = []
        super(TablixRows, self).__init__(node, self.elements, lnk)


class TablixRow(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'Height': [Element.SIZE, Card.ONE, True],
            'TablixCells': [Element.ELEMENT, Card.ONE],
        }
        super(TablixRow, self).__init__(node, self.elements, lnk)
        lnk.parent.row_list.append(self)


class TablixCells(Element):
    def __init__(self, node, lnk):
        self.elements = {'TablixCell': [Element.ELEMENT, Card.ONE_MANY], }
        self.cell_list = []
        super(TablixCells, self).__init__(node, self.elements, lnk)


class TablixCell(Element):
    def __init__(self, node, lnk):
        self.elements = {
            'CellContents': [],
            'DataElementName': [Element.STRING, Card.ZERO_ONE, True, 'Cell'],
            'DataElementOutput': [
                Element.ENUM, Card.ZERO_ONE, True, 'ContentsOnly'],
        }
        super(TablixCell, self).__init__(node, self.elements, lnk)
        lnk.parent.cell_list.append(self)


class PageBreak(Element):
    def __init__(self, node, lnk):
        self.elements = {'BreakLocation': [Element.ENUM, Card.ONE, True], }
        super(PageBreak, self).__init__(node, self.elements, lnk)
