# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import sys
import base64
from PIL import Image as PilImage
import base64
import io
import os
from . expression import (Expression, String, Boolean,  # noqa: F401
        Integer, Variant, Size, Color)                  # noqa: F401
from . enum import (BorderStyle, FontStyle,             # noqa: F401
        FontWeight, TextDecoration, TextAlign,          # noqa: F401
        VerticalAlign, TextDirection, WritingMode,      # noqa: F401
        BackgroundRepeat, BackgroundGradientType,       # noqa: F401
        DataType, SortDirection, Operator,              # noqa: F401
        BreakLocation, DataElementStyle,                # noqa: F401
        DataElementOutput, ImageSource, ImageSizing)    # noqa: F401
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
    'DataElementStyle', 'DataElementOutput',
    'ImageSource', 'ImageSizing'
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

    def __init__(self, node, lnk):
        """
        node: Xml node with the element definition.
        lnk: The linking object

        Each Element sub class must declare a class member '_element_list'
        wich is a dictionary with the elements that belongs to that element.
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
        """

        elements = Element._get_element_list(self.__class__)
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
        for key, value in additional_elements.items():
            el[key] = value
        return el

    @staticmethod
    def _get_element_list(class_):
        elements = {}
        while True:
            if not hasattr(class_, '_element_list'):
                break
            elements = Element.extend_element_list(
                elements,
                getattr(class_, '_element_list'),
                )
            class_ = class_.__base__
        return elements

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
    def __init__(self, node, lnk):

        elements = Element._get_element_list(self.__class__)

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

    _element_list = {
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
        self.parameters_def = []
        self.data_sources = []
        self.data_sets = []
        self.modules = []
        self.report_items = {}  # only textboxes
        self.report_items_group = {}
        self.data = None
        self.node = node

        lnk = Link(None, None, self)
        super(Nuntiare, self).__init__(node, lnk)

    def get_parameter_def(self, parameter_name):
        for p in self.parameters_def:
            if p.Name == parameter_name:
                return p

    def set_data(self):
        self.data = Nuntiare.Data()


class EmbeddedImages(Element):

    _element_list = {
        'EmbeddedImage': [Element.ELEMENT, Card.ONE_MANY]
        }

    def __init__(self, node, lnk):
        self.embedded_images = {}
        super(EmbeddedImages, self).__init__(node, lnk)

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

    _element_list = {
            'Name': [Element.STRING, Card.ONE, True],
            'MIMEType': [Element.STRING, Card.ONE, True],
            'ImageData': [Element.STRING, Card.ONE, True],
        }

    _mimetype_valid = {
        'image/bmp': 'BMP',
        'image/jpeg': 'JPG',
        'image/gif': 'GIF',
        'image/png': 'PNG',
        'image/xpng': 'PNG'
        }

    def __init__(self, node, lnk):
        super(EmbeddedImage, self).__init__(node, lnk)
        # Original size in pixel
        self.image_width, self.image_height = \
                self.get_pil_image_size_from_base64(self.ImageData)
        lnk.parent.embedded_images[self.Name] = self

    @classmethod
    def get_base64_image(cls, image_file, name=None, mimetype=None):
        """ Return a Base64 string reporesentation and PIL Image
            along with its name and mimetype.
            name and mimetype can be inferred from image_file if
            they are not provided. 
        """
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
        img = PilImage.open(image_file)
        img.save(buffered, format=cls._mimetype_valid[mimetype])
        img_str = base64.b64encode(buffered.getvalue())
        res = img_str.decode('utf-8')

        return [name, mimetype, res, img]

    @staticmethod
    def get_pil_image_io_from_base64(image_str, mimetype):
        buffered = io.BytesIO()
        img = PilImage.open(io.BytesIO(base64.b64decode(image_str)))
        img.save(buffered, format=EmbeddedImage._mimetype_valid[mimetype])
        return buffered

    @staticmethod
    def get_pil_image_from_base64(image_str):
        img = PilImage.open(io.BytesIO(base64.b64decode(image_str)))
        return img

    @staticmethod
    def get_pil_image_size_from_base64(image_str):
        img = EmbeddedImage.get_pil_image_from_base64(image_str)
        return img.size

    @staticmethod
    def get_proportional_size(container_width, container_height,
                              image_width, image_height):
        width = container_width
        height = container_height

        factor_base = [
            width / height,
            height / width
            ]

        factor_image = [
            image_width / image_height,
            image_height / image_width
            ]

        if container_width == container_height:
            if image_width > image_height:
                height = width * factor_image[1]
            elif image_width < image_height:
                width = height * factor_image[0]
        elif container_width > container_height:
            if image_width >= image_height:
                if factor_image[0] >= factor_base[0]:
                    width = container_width
                    height = width * factor_image[1]
                else:
                    height = container_height
                    width = height * factor_image[0]
            else:
                height = container_height
                width = height * factor_image[0]
        elif container_width < container_height:
            if image_height >= image_width:
                if factor_image[1] >= factor_base[1]:
                    height = container_height
                    width = height * factor_image[0]
                else:
                    width = container_width
                    height = width * factor_image[1]
            else:
                width = container_width
                height = width * factor_image[1]

        return [width, height]


class Modules(Element):

    _element_list = {
        'Module': [Element.ELEMENT, Card.ONE_MANY]
        }

    def __init__(self, node, lnk):
        self.modules = []
        super(Modules, self).__init__(node, lnk)


class Module(Element):

    _element_list = {
        'From': [Element.STRING, Card.ZERO_ONE, True],
        'Import': [Element.STRING, Card.ZERO_ONE, True],
        'As': [Element.STRING, Card.ZERO_ONE, True],
        }

    def __init__(self, node, lnk):
        super(Module, self).__init__(node, lnk)
        lnk.parent.modules.append(self)


class ReportParameters(Element):

    _element_list = {
        'ReportParameter': [Element.ELEMENT, Card.ONE_MANY]
        }

    def __init__(self, node, lnk):
        super(ReportParameters, self).__init__(node, lnk)


class ReportParameter(Element):

    _element_list = {
        'Name': [Element.STRING, Card.ONE, True],
        'DataType': [Element.ENUM, Card.ZERO_ONE, True, 'String'],
        'CanBeNone': [Element.BOOLEAN, Card.ZERO_ONE, True, True],
        'AllowBlank': [Element.BOOLEAN, Card.ZERO_ONE, True, True],
        'DefaultValue': [Element.VARIANT, Card.ONE],
        'Promt': [Element.STRING],
        }

    def __init__(self, node, lnk):
        super(ReportParameter, self).__init__(node, lnk)
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

    _element_list = {
        'Hidden': [Element.BOOLEAN, Card.ZERO_ONE],
        'ToggleItem': [Element.STRING, Card.ZERO_ONE, True],
        }

    def __init__(self, node, lnk):
        super(Visibility, self).__init__(node, lnk)


class Page(Element):

    _element_list = {
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

    def __init__(self, node, lnk):
        super(Page, self).__init__(node, lnk)


class _PageSection(Element):

    _element_list = {
        'ReportItems': [],
        'Height': [Element.SIZE, Card.ONE, True, 0.0],
        'PrintOnFirstPage': [
            Element.BOOLEAN, Card.ZERO_ONE, True],
        'PrintOnLastPage': [
            Element.BOOLEAN, Card.ZERO_ONE, True],
        'Style': [],
        }

    def __init__(self, node, lnk):
        super(_PageSection, self).__init__(node, lnk)


class PageHeader(_PageSection):
    _element_list = {}
    def __init__(self, node, lnk):
        super(PageHeader, self).__init__(node, lnk)


class PageFooter(_PageSection):
    _element_list = {}
    def __init__(self, node, lnk):
        super(PageFooter, self).__init__(node, lnk)


class Body(Element):

    _element_list = {
        'ReportItems': [],
        'Style': [],
        }

    def __init__(self, node, lnk):
        super(Body, self).__init__(node, lnk)


class DataSources(Element):

    _element_list = {
        'DataSource': [Element.ELEMENT, Card.ONE_MANY]
        }

    def __init__(self, node, lnk):
        super(DataSources, self).__init__(node, lnk)


class DataSource(Element):

    _element_list = {
        'Name': [Element.STRING, Card.ONE, True],
        'Transaction': [Element.BOOLEAN, Card.ZERO_ONE, True],
        'ConnectionProperties': [],
        }

    def __init__(self, node, lnk):
        super(DataSource, self).__init__(node, lnk)
        self.conn_properties = self.get_element('ConnectionProperties')
        for ds in lnk.report_def.data_sources:
            if ds.Name == self.Name:
                LOGGER.error(
                    "Report already has a DataSource with name '{0}'".format(
                        self.name), True)
        lnk.report_def.data_sources.append(self)


class ConnectionProperties(Element):

    _element_list = {
        'DataProvider': [Element.STRING, Card.ONE],
        'ConnectObject': [Element.VARIANT, Card.ONE],
        'Prompt': [Element.STRING, Card.ZERO_ONE, True],
        }

    def __init__(self, node, lnk):
        super(ConnectionProperties, self).__init__(node, lnk)


class DataSets(Element):

    _element_list = {
        'DataSet': [Element.ELEMENT, Card.ONE_MANY]
        }

    def __init__(self, node, lnk):
        super(DataSets, self).__init__(node, lnk)


class DataSet(Element):

    _element_list = {
        'Name': [Element.STRING, Card.ONE, True],
        'Fields': [],
        'Query': [Element.ELEMENT, Card.ONE],
        'Filters': [],
        'SortExpressions': [],
        }

    def __init__(self, node, lnk):
        self.fields = []
        super(DataSet, self).__init__(node, lnk)
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

    _element_list = {
        'Field': [Element.ELEMENT, Card.ONE_MANY]
        }

    def __init__(self, node, lnk):
        super(Fields, self).__init__(node, lnk)


class Field(Element):
    '''
    The Field element contains information about a field in
    the data model of the report.
    '''

    _element_list = {
        'Name': [Element.STRING, Card.ONE, True],
        'DataType': [Element.ENUM, Card.ZERO_ONE, True, 'String'],
        'DataField': [Element.STRING, Card.ZERO_ONE, True],
        'Value': [Element.VARIANT],
        }

    def __init__(self, node, lnk):
        super(Field, self).__init__(node, lnk)
        data_set = lnk.parent.lnk.parent  # Get Dataset
        for fd in data_set.fields:
            if fd.Name == self.Name:
                LOGGER.error(
                    "DataSet already has '{0}' Field.".format(
                        self.name), True)
        data_set.fields.append(self)


class Query(Element):

    _element_list = {
        'DataSourceName': [Element.STRING, Card.ONE, True],
        'CommandText': [Element.STRING],
        'QueryParameters': [],
        }

    def __init__(self, node, lnk):
        super(Query, self).__init__(node, lnk)

    def get_command_text(self, report):
        cmd = Expression.get_value_or_default(
            report, self, 'CommandText', None)
        if not cmd:
            LOGGER.error(
                "'CommandText' is required by 'Query' element.", True)
        return cmd


class QueryParameters(Element):

    _element_list = {
        'QueryParameter': [Element.ELEMENT, Card.ONE_MANY]
        }

    def __init__(self, node, lnk):
        super(QueryParameters, self).__init__(node, lnk)


class QueryParameter(Element):

    _element_list = {
            'Name': [Element.STRING, Card.ONE, True],
            'Value': [Element.VARIANT, Card.ONE],
        }

    def __init__(self, node, lnk):
        super(QueryParameter, self).__init__(node, lnk)


class Filters(Element):

    _element_list = {
        'Filter': [Element.ELEMENT, Card.ONE_MANY]
        }

    def __init__(self, node, lnk):
        self.filter_list = []
        super(Filters, self).__init__(node, lnk)


class Filter(Element):

    _element_list = {
        'FilterExpression': [Element.VARIANT, Card.ONE],
        'Operator': [Element.ENUM, Card.ONE, True],
        'FilterValues': [Element.EXPRESSION_LIST, Card.ONE],
        }

    def __init__(self, node, lnk):
        super(Filter, self).__init__(node, lnk)
        lnk.parent.filter_list.append(self)


class FilterValues(_ExpressionList):

    _element_list = {
        'FilterValue': [Element.VARIANT, Card.ONE_MANY]
        }

    def __init__(self, node, lnk):
        super(FilterValues, self).__init__(node, lnk)


class Group(Element):

    _element_list = {
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

    def __init__(self, node, lnk):
        super(Group, self).__init__(node, lnk)


class GroupExpressions(_ExpressionList):

    _element_list = {
        'GroupExpression': [Element.VARIANT, Card.ONE_MANY]
        }

    def __init__(self, node, lnk):
        super(GroupExpressions, self).__init__(node, lnk)


class SortExpressions(Element):

    _element_list = {
        'SortExpression': [Element.ELEMENT, Card.ONE_MANY]
        }

    def __init__(self, node, lnk):
        self.sortby_list = []
        super(SortExpressions, self).__init__(node, lnk)


class SortExpression(Element):

    _element_list = {
        'Value': [Element.VARIANT, Card.ONE],
        'SortDirection': [Element.ENUM, Card.ZERO_ONE, True, 'Ascending'],
        }

    def __init__(self, node, lnk):
        super(SortExpression, self).__init__(node, lnk)
        lnk.parent.sortby_list.append(self)


class Style(Element):

    _element_list = {
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

    def __init__(self, node, lnk):
        super(Style, self).__init__(node, lnk)


class Border(Element):

    _element_list = {
        'Color': [Element.COLOR, Card.ZERO_ONE, False, '#000000'],
        'BorderStyle': [Element.ENUM, Card.ZERO_ONE, False],
        'Width': [Element.SIZE, Card.ZERO_ONE, False, 1],
        }

    def __init__(self, node, lnk):
        super(Border, self).__init__(node, lnk)


class RightBorder(Border):
    _element_list = {}
    def __init__(self, node, lnk):
        super(RightBorder, self).__init__(node, lnk)


class LeftBorder(Border):
    _element_list = {}
    def __init__(self, node, lnk):
        super(LeftBorder, self).__init__(node, lnk)


class TopBorder(Border):
    _element_list = {}
    def __init__(self, node, lnk):
        super(TopBorder, self).__init__(node, lnk)


class BottomBorder(Border):
    _element_list = {}
    def __init__(self, node, lnk):
        super(BottomBorder, self).__init__(node, lnk)


class BackgroundImage(Element):

    _element_list = {
        'ImageSource': [Element.ENUM, Card.ONE, True],
        'Value': [Element.VARIANT, Card.ONE],
        'MIMEType': [Element.STRING],
        'BackgroundRepeat': [Element.ENUM],
        'TransparentColor': [Element.COLOR],
        'Position': [Element.ENUM],
        }

    def __init__(self, node, lnk):
        super(BackgroundImage, self).__init__(
                'Image', node, lnk)


class ReportItems(Element):

    _element_list = {
            'Line': [Element.ELEMENT, Card.ZERO_MANY],
            'Rectangle': [Element.ELEMENT, Card.ZERO_MANY],
            'Textbox': [Element.ELEMENT, Card.ZERO_MANY],
            'Image': [Element.ELEMENT, Card.ZERO_MANY],
            'Subreport': [Element.ELEMENT, Card.ZERO_MANY],
            'Tablix': [Element.ELEMENT, Card.ZERO_MANY],
            'Chart': [Element.ELEMENT, Card.ZERO_MANY],
        }

    def __init__(self, node, lnk):
        self.reportitems_list = []
        super(ReportItems, self).__init__(node, lnk)


class _ReportItem(Element):

    _element_list = {
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

    def __init__(self, type, node, lnk):
        super(_ReportItem, self).__init__(node, lnk)
        self.type = type
        lnk.parent.reportitems_list.append(self)


class Line(_ReportItem):
    _element_list = {}
    def __init__(self, node, lnk):
        super(Line, self).__init__('Line', node, lnk)


class Rectangle(_ReportItem):

    _element_list = {
        'ReportItems': [],
        'PageBreak': [],
        'KeepTogether': [Element.BOOLEAN, 0, True, False],
        'OmitBorderOnPageBreak': [Element.BOOLEAN, 0, True, True],
        }

    def __init__(self, node, lnk):
        super(Rectangle, self).__init__('Rectangle', node, lnk)


class Subreport(_ReportItem):

    _element_list = {
        'ReportName': [Element.STRING, Card.ONE, True],
        'Parameters': [],
        'NoRowsMessage': [Element.STRING],
        'KeepTogether': [Element.BOOLEAN, Card.ZERO_ONE, True, False],
        'MergeTransactions': [Element.BOOLEAN, Card.ZERO_ONE, True],
        'OmitBorderOnPageBreak': [Element.BOOLEAN, Card.ZERO_ONE, True],
        }

    def __init__(self, node, lnk):
        super(Subreport, self).__init__('Subreport', node, lnk)


class Parameters(Element):

    _element_list = {
        'Parameter': [Element.ELEMENT, Card.ONE_MANY]
        }

    def __init__(self, node, lnk):
        super(Parameters, self).__init__(node, lnk)


class Parameter(Element):

    _element_list = {
        'Name': [Element.STRING, Card.ONE, True],
        'Value': [Element.VARIANT, Card.ONE],
        'Omit': [Element.BOOLEAN],
        }

    def __init__(self, node, lnk):
        super(Parameter, self).__init__(node, lnk)


class Image(_ReportItem):

    _element_list = {
        'ImageSource': [Element.ENUM, Card.ONE, True],
        'Value': [Element.VARIANT, Card.ONE],
        'MIMEType': [Element.STRING],
        'ImageSizing': [Element.ENUM, Card.ZERO_ONE, True, 'AutoSize'],
        }

    def __init__(self, node, lnk):
        super(Image, self).__init__('Image', node, lnk)


class Textbox(_ReportItem):

    _element_list = {
        'Value': [Element.VARIANT, Card.ZERO_ONE],
        'CanGrow': [Element.BOOLEAN, Card.ZERO_ONE, True],
        'CanShrink': [Element.BOOLEAN, Card.ZERO_ONE, True],
        'KeepTogether': [Element.BOOLEAN, Card.ZERO_ONE, True, False],
        'HideDuplicates': [Element.STRING, Card.ZERO_ONE, True],
        'ToggleImage': [],
        'DataElementStyle': [
            Element.ENUM, Card.ZERO_ONE, True, 'Auto'],
        }

    def __init__(self, node, lnk):
        super(Textbox, self).__init__('Textbox', node, lnk)


class ToggleImage(Element):

    _element_list = {
        'InitialState': [Element.BOOLEAN, Card.ONE]
        }

    def __init__(self, node, lnk):
        super(ToggleImage, self).__init__(node, lnk)


class _DataRegion(_ReportItem):

    _element_list = {
        'NoRowsMessage': [Element.STRING],
        'DataSetName': [Element.STRING, Card.ZERO_ONE, True],
        'PageBreak': [],
        'Filters': [],
        'SortExpressions': [],
        }

    def __init__(self, type, node, lnk):
        super(_DataRegion, self).__init__(type, node, lnk)


class Tablix(_DataRegion):

    _element_list = {
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

    def __init__(self, node, lnk):
        super(Tablix, self).__init__('Tablix', node, lnk)


class TablixCorner(Element):

    _element_list = {
        'TablixCornerRows': [Element.ELEMENT, Card.ONE]
        }

    def __init__(self, node, lnk):
        super(TablixCorner, self).__init__(node, lnk)


class TablixCornerRows(Element):

    _element_list = {
        'TablixCornerRow': [Element.ELEMENT, Card.ONE_MANY]
        }

    def __init__(self, node, lnk):
        self.row_list = []
        super(TablixCornerRows, self).__init__(node, lnk)


class TablixCornerRow(Element):

    _element_list = {
        'TablixCornerCell': [Element.ELEMENT, Card.ZERO_ONE]
        }

    def __init__(self, node, lnk):
        self.cell_list = []
        super(TablixCornerRow, self).__init__(node, lnk)
        lnk.parent.row_list.append(self)


class TablixCornerCell(Element):

    _element_list = {
        'CellContents': []
        }

    def __init__(self, node, lnk):
        super(TablixCornerCell, self).__init__(node, lnk)
        lnk.parent.cell_list.append(self)


class CellContents(Element):

    _element_list = {
        'ReportItems': [],
        'ColSpan': [Element.INTEGER, Card.ZERO_ONE, True],
        'RowSpan': [Element.INTEGER, Card.ZERO_ONE, True],
        }

    def __init__(self, node, lnk):
        super(CellContents, self).__init__(node, lnk)


class _TablixHierarchy(Element):

    _element_list = {
        'TablixMembers': [Element.ELEMENT, Card.ONE]
        }

    def __init__(self, node, lnk):
        super(_TablixHierarchy, self).__init__(node, lnk)


class TablixRowHierarchy(_TablixHierarchy):
    _element_list = {}
    def __init__(self, node, lnk):
        super(TablixRowHierarchy, self).__init__(node, lnk)


class TablixColumnHierarchy(_TablixHierarchy):
    _element_list = {}
    def __init__(self, node, lnk):
        super(TablixColumnHierarchy, self).__init__(node, lnk)


class TablixMembers(Element):

    _element_list = {
        'TablixMember': [Element.ELEMENT, Card.ONE_MANY]
        }

    def __init__(self, node, lnk):
        self.member_list = []
        super(TablixMembers, self).__init__(node, lnk)


class TablixMember(Element):

    _element_list = {
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

    def __init__(self, node, lnk):
        super(TablixMember, self).__init__(node, lnk)
        lnk.parent.member_list.append(self)


class TablixHeader(Element):

    _element_list = {
        'Size': [Element.SIZE, Card.ONE, True],
        'CellContents': [Element.ELEMENT, Card.ONE],
        }

    def __init__(self, node, lnk):
        super(TablixHeader, self).__init__(node, lnk)


class TablixBody(Element):

    _element_list = {
        'TablixColumns': [Element.ELEMENT, Card.ONE],
        'TablixRows': [Element.ELEMENT, Card.ONE],
        }

    def __init__(self, node, lnk):
        super(TablixBody, self).__init__(node, lnk)


class TablixColumns(Element):

    _element_list = {
        'TablixColumn': [Element.ELEMENT, Card.ONE_MANY]
        }

    def __init__(self, node, lnk):
        self.column_list = []
        super(TablixColumns, self).__init__(node, lnk)


class TablixColumn(Element):

    _element_list = {
        'Width': [Element.SIZE, Card.ONE, True]
        }

    def __init__(self, node, lnk):
        super(TablixColumn, self).__init__(node, lnk)
        lnk.parent.column_list.append(self)


class TablixRows(Element):

    _element_list = {
        'TablixRow': [Element.ELEMENT, Card.ONE_MANY]
        }

    def __init__(self, node, lnk):
        self.row_list = []
        super(TablixRows, self).__init__(node, lnk)


class TablixRow(Element):

    _element_list = {
            'Height': [Element.SIZE, Card.ONE, True],
            'TablixCells': [Element.ELEMENT, Card.ONE],
        }

    def __init__(self, node, lnk):
        super(TablixRow, self).__init__(node, lnk)
        lnk.parent.row_list.append(self)


class TablixCells(Element):

    _element_list = {
        'TablixCell': [Element.ELEMENT, Card.ONE_MANY]
        }

    def __init__(self, node, lnk):
        self.cell_list = []
        super(TablixCells, self).__init__(node, lnk)


class TablixCell(Element):

    _element_list = {
        'CellContents': [],
        'DataElementName': [Element.STRING, Card.ZERO_ONE, True, 'Cell'],
        'DataElementOutput': [
            Element.ENUM, Card.ZERO_ONE, True, 'ContentsOnly'],
        }

    def __init__(self, node, lnk):
        super(TablixCell, self).__init__(node, lnk)
        lnk.parent.cell_list.append(self)


class PageBreak(Element):

    _element_list = {
        'BreakLocation': [Element.ENUM, Card.ONE, True]
        }

    def __init__(self, node, lnk):
        super(PageBreak, self).__init__(node, lnk)
