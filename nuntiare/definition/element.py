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
    'Nuntiare',
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

_REPORT_ITEMS = [
    'Line', 'Rectangle',
    'Textbox', 'Image',
    'Subreport', 'CustomReportItem',
    'Tablix', 'Chart'
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

    meta = {}

    def __init__(self, node, lnk):
        """
        node: Xml node with the element definition.
        lnk: The linking object

        Each Element sub class must declare a class member '_element_list'
        wich is a dictionary with the Meta objects for each member.
         key: Element name
         value: Meta object
        """

        if self.__class__.__name__ not in Element.meta:
            Element.meta[self.__class__.__name__] = \
                Element._get_element_list(self.__class__)

        self._meta = Element.meta[self.__class__.__name__]
        verified = []

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
            if n.nodeName not in self._meta:
                if n.nodeName == 'DataEmbedded' and \
                        n.parentNode.nodeName == 'Nuntiare':
                    self.set_data()
                    continue
                if n.nodeName not in ('#text', '#comment'):
                    LOGGER.warn(
                        "Unknown element '{0}' for '{1}'. Ignored.".format(
                            n.nodeName, self.element_name))
                continue

            verified.append(n.nodeName)
            meta = self._meta[n.nodeName]

            if meta.type == Element.ELEMENT:
                el = Element.element_factory(n.nodeName, n, lnk)
                if n.nodeName in _REPORT_ITEMS:
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
            elif meta.type == Element.EXPRESSION_LIST:
                self.element_list[n.nodeName] = \
                    Element.expression_list_factory(n.nodeName, n, lnk)
                self.non_expression_list[n.nodeName] = \
                    self.element_list[n.nodeName]
            elif meta.type == Element.ENUM:
                self.element_list[n.nodeName] = \
                    Element.enum_factory(
                        n.nodeName, n, lnk, meta.card, meta.constant)
                self.expression_list[n.nodeName] = \
                    self.element_list[n.nodeName]
                self._set_attr(
                    n.nodeName, False, meta.default,
                    meta.constant)
            else:
                self.element_list[n.nodeName] = \
                    Element.expression_factory(
                        meta.type, n, lnk,
                        meta.card, meta.constant)
                self.expression_list[n.nodeName] = \
                    self.element_list[n.nodeName]
                self._set_attr(
                    n.nodeName, False, meta.default,
                    meta.constant)

        # Validate elements not used
        for key, meta in self._meta.items():
            if key in verified:
                continue
            if meta.card in [Card.ONE, Card.ONE_MANY]:
                LOGGER.error(
                    "'{0}' must be defined for '{1}'.".format(
                        key, self.element_name), True)
            if meta.default is not None and meta.type not in \
                    (Element.ELEMENT, Element.EXPRESSION_LIST):
                self._set_attr(
                    key, False, meta.default, True)

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
        if name in self.__dict__:
            return self.__dict__[name]

        self._verify_element(name)
        result = self._meta[name]
        if result.type in (
                Element.ELEMENT, Element.EXPRESSION_LIST):
            el = self.get_element(name)
            if el:
                self._set_attr(name, True, el, False)
                return self.__dict__[name]
        else:
            if not result.constant:
                err_msg = "'{0}' is not a constant property " \
                    "for element '{1}'. Use 'get_value()' instead."
                LOGGER.error(err_msg.format(name, self.element_name), True)
            else:
                self._set_attr(
                        name, False,
                        result.default,
                        result.constant)
                return self.__dict__[name]

    def _verify_element(self, name):
        if name not in self._meta:
            err_msg = "'{0}' is not a valid member for element '{1}'. " \
                "Valid are: {2}"
            LOGGER.error(err_msg.format(
                name, self.element_name,
                self._meta.keys()), True)

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

    def get_element(self, name):
        if name in self.element_list:
            return self.element_list[name]

    def has_element(self, name):
        el = self.get_element(name)
        if el:
            return True


class Meta:
    def __init__(self,
                 type_=Element.ELEMENT,
                 card=Card.ZERO_ONE,
                 constant=False,
                 default=None):
        self.type = type_
        self.card = card
        self.constant = constant
        self.default = default

        if type_ == Element.SIZE and self.default is None:
            self.default = 0


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

            meta = elements[n.nodeName]
            ex = Element.expression_factory(
                meta.type, n, lnk, meta.card, meta.constant)
            self.expression_list.append(ex)


class Nuntiare(Element):
    '''
    Root definition element.
    '''

    _element_list = {
        'Name': Meta(Element.STRING, Card.ONE, True),
        'Description': Meta(Element.STRING, constant=True),
        'Author': Meta(Element.STRING, constant=True),
        'Version': Meta(Element.STRING, constant=True),
        'DateCreate': Meta(Element.DATE, constant=True),
        'DateUpdate': Meta(Element.DATE, constant=True),
        'DataSources': Meta(),
        'DataSets': Meta(),
        'Body': Meta(card=Card.ONE),
        'ReportParameters': Meta(),
        'Modules': Meta(),
        'EmbeddedImages': Meta(),
        'Page': Meta(card=Card.ONE),
        'Language': Meta(Element.STRING, constant=True),
        'DataElementName': Meta(
            Element.STRING, constant=True, default='Nuntiare'),
        'DataElementStyle': Meta(
            Element.ENUM, constant=True, default='Attribute'),
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
        'EmbeddedImage': Meta(card=Card.ONE_MANY)
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
            'Name': Meta(Element.STRING, Card.ONE, True),
            'MIMEType': Meta(Element.STRING, Card.ONE, True),
            'ImageData': Meta(Element.STRING, Card.ONE, True),
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
        'Module': Meta(Element.ELEMENT, Card.ONE_MANY)
        }

    def __init__(self, node, lnk):
        self.modules = []
        super(Modules, self).__init__(node, lnk)


class Module(Element):

    _element_list = {
        'From': Meta(Element.STRING, constant=True),
        'Import': Meta(Element.STRING, constant=True),
        'As': Meta(Element.STRING, constant=True),
        }

    def __init__(self, node, lnk):
        super(Module, self).__init__(node, lnk)
        lnk.parent.modules.append(self)


class ReportParameters(Element):

    _element_list = {
        'ReportParameter': Meta(Element.ELEMENT, Card.ONE_MANY)
        }

    def __init__(self, node, lnk):
        super(ReportParameters, self).__init__(node, lnk)


class ReportParameter(Element):

    _element_list = {
        'Name': Meta(Element.STRING, Card.ONE, True),
        'DataType': Meta(Element.ENUM, constant=True, default='String'),
        'CanBeNone': Meta(Element.BOOLEAN, constant=True, default=True),
        'AllowBlank': Meta(Element.BOOLEAN, constant=True, default=True),
        'DefaultValue': Meta(Element.VARIANT, Card.ONE),
        'Promt': Meta(Element.STRING),
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
        'Hidden': Meta(Element.BOOLEAN),
        'ToggleItem': Meta(Element.STRING, constant=True),
        }

    def __init__(self, node, lnk):
        super(Visibility, self).__init__(node, lnk)


class Page(Element):

    _element_list = {
        'PageHeader': Meta(),
        'PageFooter': Meta(),
        'PageHeight': Meta(Element.SIZE, constant=True, default=11 * 72),
        'PageWidth': Meta(Element.SIZE, constant=True, default=8.5 * 72),
        'LeftMargin': Meta(Element.SIZE, constant=True),
        'RightMargin': Meta(Element.SIZE, constant=True),
        'TopMargin': Meta(Element.SIZE, constant=True),
        'BottomMargin': Meta(Element.SIZE, constant=True),
        'Columns': Meta(Element.INTEGER, constant=True, default=1),
        'ColumnSpacing': Meta(Element.SIZE, constant=True, default=0.5 * 72),
        'Style': Meta(),
        }

    def __init__(self, node, lnk):
        super(Page, self).__init__(node, lnk)


class _PageSection(Element):

    _element_list = {
        'ReportItems': Meta(),
        'Height': Meta(Element.SIZE, Card.ONE, True),
        'PrintOnFirstPage': Meta(Element.BOOLEAN, constant=True),
        'PrintOnLastPage': Meta(Element.BOOLEAN, constant=True),
        'Style': Meta(),
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
        'ReportItems': Meta(),
        'Style': Meta(),
        }

    def __init__(self, node, lnk):
        super(Body, self).__init__(node, lnk)


class DataSources(Element):

    _element_list = {
        'DataSource': Meta(card=Card.ONE_MANY)
        }

    def __init__(self, node, lnk):
        super(DataSources, self).__init__(node, lnk)


class DataSource(Element):

    _element_list = {
        'Name': Meta(Element.STRING, Card.ONE, True),
        'Transaction': Meta(Element.BOOLEAN, constant=True),
        'ConnectionProperties': Meta(),
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
        'DataProvider': Meta(Element.STRING, Card.ONE),
        'ConnectObject': Meta(Element.VARIANT, Card.ONE),
        'Prompt': Meta(Element.STRING, constant=True),
        }

    def __init__(self, node, lnk):
        super(ConnectionProperties, self).__init__(node, lnk)


class DataSets(Element):

    _element_list = {
        'DataSet': Meta(Element.ELEMENT, Card.ONE_MANY)
        }

    def __init__(self, node, lnk):
        super(DataSets, self).__init__(node, lnk)


class DataSet(Element):

    _element_list = {
        'Name': Meta(Element.STRING, Card.ONE, True),
        'Fields': Meta(),
        'Query': Meta(Element.ELEMENT, Card.ONE),
        'Filters': Meta(),
        'SortExpressions': Meta(),
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
        'Field': Meta(Element.ELEMENT, Card.ONE_MANY)
        }

    def __init__(self, node, lnk):
        super(Fields, self).__init__(node, lnk)


class Field(Element):
    '''
    The Field element contains information about a field in
    the data model of the report.
    '''

    _element_list = {
        'Name': Meta(Element.STRING, Card.ONE, True),
        'DataType': Meta(Element.ENUM, constant=True, default='String'),
        'DataField': Meta(Element.STRING, constant=True),
        'Value': Meta(Element.VARIANT),
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
        'DataSourceName': Meta(Element.STRING, Card.ONE, True),
        'CommandText': Meta(Element.STRING),
        'QueryParameters': Meta(),
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
        'QueryParameter': Meta(Element.ELEMENT, Card.ONE_MANY)
        }

    def __init__(self, node, lnk):
        super(QueryParameters, self).__init__(node, lnk)


class QueryParameter(Element):

    _element_list = {
            'Name': Meta(Element.STRING, Card.ONE, True),
            'Value': Meta(Element.VARIANT, Card.ONE),
        }

    def __init__(self, node, lnk):
        super(QueryParameter, self).__init__(node, lnk)


class Filters(Element):

    _element_list = {
        'Filter': Meta(Element.ELEMENT, Card.ONE_MANY)
        }

    def __init__(self, node, lnk):
        self.filter_list = []
        super(Filters, self).__init__(node, lnk)


class Filter(Element):

    _element_list = {
        'FilterExpression': Meta(Element.VARIANT, Card.ONE),
        'Operator': Meta(Element.ENUM, Card.ONE, True),
        'FilterValues': Meta(Element.EXPRESSION_LIST, Card.ONE),
        }

    def __init__(self, node, lnk):
        super(Filter, self).__init__(node, lnk)
        lnk.parent.filter_list.append(self)


class FilterValues(_ExpressionList):

    _element_list = {
        'FilterValue': Meta(Element.VARIANT, Card.ONE_MANY)
        }

    def __init__(self, node, lnk):
        super(FilterValues, self).__init__(node, lnk)


class Group(Element):

    _element_list = {
        'Name': Meta(Element.STRING, Card.ONE, True),
        'GroupExpressions': Meta(Element.EXPRESSION_LIST),
        'PageBreak': Meta(),
        'Filters': Meta(),
        'SortExpressions': Meta(),
        'Parent': Meta(Element.VARIANT),
        'DataElementName': Meta(Element.STRING, constant=True),
        'DataElementOutput': Meta(
                Element.ENUM, constant=True, default='Output'),
        }

    def __init__(self, node, lnk):
        super(Group, self).__init__(node, lnk)


class GroupExpressions(_ExpressionList):

    _element_list = {
        'GroupExpression': Meta(Element.VARIANT, Card.ONE_MANY)
        }

    def __init__(self, node, lnk):
        super(GroupExpressions, self).__init__(node, lnk)


class SortExpressions(Element):

    _element_list = {
        'SortExpression': Meta(Element.ELEMENT, Card.ONE_MANY)
        }

    def __init__(self, node, lnk):
        self.sortby_list = []
        super(SortExpressions, self).__init__(node, lnk)


class SortExpression(Element):

    _element_list = {
        'Value': Meta(Element.VARIANT, Card.ONE),
        'SortDirection': Meta(
            Element.ENUM, constant=True, default='Ascending'),
        }

    def __init__(self, node, lnk):
        super(SortExpression, self).__init__(node, lnk)
        lnk.parent.sortby_list.append(self)


class Style(Element):

    _element_list = {
        'Border': Meta(),
        'TopBorder': Meta(),
        'BottomBorder': Meta(),
        'LeftBorder': Meta(),
        'RightBorder': Meta(),
        'BackgroundColor': Meta(Element.COLOR),
        'BackgroundGradientType': Meta(Element.ENUM),
        'BackgroundGradientEndColor': Meta(Element.COLOR),
        'BackgroundImage': Meta(),
        'FontStyle': Meta(Element.ENUM, default='Normal'),
        'FontFamily': Meta(Element.STRING, default='Helvetica'),
        'FontSize': Meta(Element.SIZE, default=10),
        'FontWeight': Meta(Element.ENUM, default='Normal'),
        'Format': Meta(Element.STRING),
        'TextDecoration': Meta(Element.ENUM, default='None'),
        'TextAlign': Meta(Element.ENUM, default='None'),
        'VerticalAlign': Meta(Element.ENUM, default='Top'),
        'Color': Meta(Element.COLOR, default='#000000'),
        'PaddingLeft': Meta(Element.SIZE),
        'PaddingRight': Meta(Element.SIZE),
        'PaddingTop': Meta(Element.SIZE),
        'PaddingBottom': Meta(Element.SIZE),
        'LineHeight': Meta(Element.SIZE, default=1.0),
        'TextDirection': Meta(Element.ENUM, default='LTR'),
        'WritingMode': Meta(Element.ENUM, default='Horizontal'),
        }

    def __init__(self, node, lnk):
        super(Style, self).__init__(node, lnk)


class Border(Element):

    _element_list = {
        'Color': Meta(Element.COLOR, default='#000000'),
        'BorderStyle': Meta(Element.ENUM, default='None'),
        'Width': Meta(Element.SIZE, default=1),
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
        'ImageSource': Meta(Element.ENUM, Card.ONE, True),
        'Value': Meta(Element.VARIANT, Card.ONE),
        'MIMEType': Meta(Element.STRING),
        'BackgroundRepeat': Meta(Element.ENUM),
        'TransparentColor': Meta(Element.COLOR),
        'Position': Meta(Element.ENUM),
        }

    def __init__(self, node, lnk):
        super(BackgroundImage, self).__init__(
                'Image', node, lnk)


class ReportItems(Element):

    _element_list = {
            'Line': Meta(Element.ELEMENT, Card.ZERO_MANY),
            'Rectangle': Meta(Element.ELEMENT, Card.ZERO_MANY),
            'Textbox': Meta(Element.ELEMENT, Card.ZERO_MANY),
            'Image': Meta(Element.ELEMENT, Card.ZERO_MANY),
            'Subreport': Meta(Element.ELEMENT, Card.ZERO_MANY),
            'Tablix': Meta(Element.ELEMENT, Card.ZERO_MANY),
            'Chart': Meta(Element.ELEMENT, Card.ZERO_MANY),
        }

    def __init__(self, node, lnk):
        self.reportitems_list = []
        super(ReportItems, self).__init__(node, lnk)


class _ReportItem(Element):

    _element_list = {
        'Name': Meta(Element.STRING, Card.ONE, True),
        'ActionInfo': Meta(),
        'Top': Meta(Element.SIZE, constant=True),
        'Left': Meta(Element.SIZE, constant=True),
        'Height': Meta(Element.SIZE, constant=True),
        'Width': Meta(Element.SIZE, constant=True),
        'ZIndex': Meta(Element.INTEGER, constant=True, default=-1),
        'Visibility': Meta(),
        'ToolTip': Meta(Element.STRING),
        'Bookmark': Meta(Element.STRING),
        'RepeatWith': Meta(Element.STRING, constant=True),
        'Style': Meta(),
        'DataElementName': Meta(Element.STRING, constant=True),
        'DataElementOutput': Meta(
            Element.ENUM, constant=True, default='Auto'),
        }

    def __init__(self, type, node, lnk):
        super(_ReportItem, self).__init__(node, lnk)
        self.type = type
        lnk.parent.reportitems_list.append(self)


class Line(_ReportItem):
    """ Line ReportItem. Negative values for Height/Width allow
    lines to be drawed Top/Left from its origin.
    """
    _element_list = {}
    def __init__(self, node, lnk):
        super(Line, self).__init__('Line', node, lnk)


class Rectangle(_ReportItem):

    _element_list = {
        'ReportItems': Meta(),
        'PageBreak': Meta(),
        'KeepTogether': Meta(Element.BOOLEAN, 0, True, False),
        'OmitBorderOnPageBreak': Meta(Element.BOOLEAN, 0, True, True),
        }

    def __init__(self, node, lnk):
        super(Rectangle, self).__init__('Rectangle', node, lnk)


class Subreport(_ReportItem):

    _element_list = {
        'ReportName': Meta(Element.STRING, Card.ONE, True),
        'Parameters': Meta(),
        'NoRowsMessage': Meta(Element.STRING),
        'KeepTogether': Meta(Element.BOOLEAN, constant=True, default=False),
        'MergeTransactions': Meta(Element.BOOLEAN, constant=True),
        'OmitBorderOnPageBreak': Meta(Element.BOOLEAN, constant=True),
        }

    def __init__(self, node, lnk):
        super(Subreport, self).__init__('Subreport', node, lnk)


class Parameters(Element):

    _element_list = {
        'Parameter': Meta(Element.ELEMENT, Card.ONE_MANY)
        }

    def __init__(self, node, lnk):
        super(Parameters, self).__init__(node, lnk)


class Parameter(Element):

    _element_list = {
        'Name': Meta(Element.STRING, Card.ONE, True),
        'Value': Meta(Element.VARIANT, Card.ONE),
        'Omit': Meta(Element.BOOLEAN),
        }

    def __init__(self, node, lnk):
        super(Parameter, self).__init__(node, lnk)


class Image(_ReportItem):

    _element_list = {
        'ImageSource': Meta(Element.ENUM, Card.ONE, True),
        'Value': Meta(Element.VARIANT, Card.ONE),
        'MIMEType': Meta(Element.STRING),
        'ImageSizing': Meta(Element.ENUM, constant=True, default='AutoSize'),
        }

    def __init__(self, node, lnk):
        super(Image, self).__init__('Image', node, lnk)


class Textbox(_ReportItem):

    _element_list = {
        'Value': Meta(Element.VARIANT),
        'CanGrow': Meta(Element.BOOLEAN, constant=True),
        'CanShrink': Meta(Element.BOOLEAN, constant=True),
        'KeepTogether': Meta(Element.BOOLEAN, constant=True, default=False),
        'HideDuplicates': Meta(Element.STRING, constant=True),
        'ToggleImage': Meta(),
        'DataElementStyle': Meta(
            Element.ENUM, constant=True, default='Auto'),
        }

    def __init__(self, node, lnk):
        super(Textbox, self).__init__('Textbox', node, lnk)


class ToggleImage(Element):

    _element_list = {
        'InitialState': Meta(Element.BOOLEAN, Card.ONE)
        }

    def __init__(self, node, lnk):
        super(ToggleImage, self).__init__(node, lnk)


class _DataRegion(_ReportItem):

    _element_list = {
        'NoRowsMessage': Meta(Element.STRING),
        'DataSetName': Meta(Element.STRING, constant=True),
        'PageBreak': Meta(),
        'Filters': Meta(),
        'SortExpressions': Meta(),
        }

    def __init__(self, type, node, lnk):
        super(_DataRegion, self).__init__(type, node, lnk)


class Tablix(_DataRegion):

    _element_list = {
        'TablixCorner': Meta(),
        'TablixBody': Meta(Element.ELEMENT, Card.ONE),
        'TablixColumnHierarchy': Meta(Element.ELEMENT, Card.ONE),
        'TablixRowHierarchy': Meta(Element.ELEMENT, Card.ONE),
        'LayoutDirection': Meta(Element.ENUM, constant=True, default='LTR'),
        'GroupsBeforeRowHeaders': Meta(Element.INTEGER, constant=True),
        'RepeatColumnHeaders': Meta(Element.BOOLEAN, constant=True),
        'RepeatRowHeaders': Meta(Element.BOOLEAN, constant=True),
        'FixedColumnHeaders': Meta(Element.BOOLEAN, constant=True),
        'FixedRowHeaders': Meta(Element.BOOLEAN, constant=True),
        'KeepTogether': Meta(Element.BOOLEAN, constant=True, default=False),
        'OmitBorderOnPageBreak': Meta(Element.BOOLEAN, constant=True),
        }

    def __init__(self, node, lnk):
        super(Tablix, self).__init__('Tablix', node, lnk)


class TablixCorner(Element):

    _element_list = {
        'TablixCornerRows': Meta(Element.ELEMENT, Card.ONE)
        }

    def __init__(self, node, lnk):
        super(TablixCorner, self).__init__(node, lnk)


class TablixCornerRows(Element):

    _element_list = {
        'TablixCornerRow': Meta(Element.ELEMENT, Card.ONE_MANY)
        }

    def __init__(self, node, lnk):
        self.row_list = []
        super(TablixCornerRows, self).__init__(node, lnk)


class TablixCornerRow(Element):

    _element_list = {
        'TablixCornerCell': Meta()
        }

    def __init__(self, node, lnk):
        self.cell_list = []
        super(TablixCornerRow, self).__init__(node, lnk)
        lnk.parent.row_list.append(self)


class TablixCornerCell(Element):

    _element_list = {
        'CellContents': Meta()
        }

    def __init__(self, node, lnk):
        super(TablixCornerCell, self).__init__(node, lnk)
        lnk.parent.cell_list.append(self)


class CellContents(Element):

    _element_list = {
        'ReportItems': Meta(),
        'ColSpan': Meta(Element.INTEGER, constant=True),
        'RowSpan': Meta(Element.INTEGER, constant=True),
        }

    def __init__(self, node, lnk):
        super(CellContents, self).__init__(node, lnk)


class _TablixHierarchy(Element):

    _element_list = {
        'TablixMembers': Meta(Element.ELEMENT, Card.ONE)
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
        'TablixMember': Meta(Element.ELEMENT, Card.ONE_MANY)
        }

    def __init__(self, node, lnk):
        self.member_list = []
        super(TablixMembers, self).__init__(node, lnk)


class TablixMember(Element):

    _element_list = {
        'Group': Meta(),
        'TablixHeader': Meta(),
        'TablixMembers': Meta(),
        'FixedData': Meta(Element.BOOLEAN, constant=True),
        'Visibility': Meta(),
        'KeepTogether': Meta(
            Element.BOOLEAN, constant=True, default=False),
        'HideIfNoRows': Meta(Element.BOOLEAN, constant=True),
        'RepeatOnNewPage': Meta(Element.BOOLEAN, constant=True),
        'DataElementName': Meta(Element.STRING, constant=True),
        'DataElementOutput': Meta(
            Element.ENUM, constant=True, default='Auto'),
        }

    def __init__(self, node, lnk):
        super(TablixMember, self).__init__(node, lnk)
        lnk.parent.member_list.append(self)


class TablixHeader(Element):

    _element_list = {
        'Size': Meta(Element.SIZE, Card.ONE, True),
        'CellContents': Meta(Element.ELEMENT, Card.ONE),
        }

    def __init__(self, node, lnk):
        super(TablixHeader, self).__init__(node, lnk)


class TablixBody(Element):

    _element_list = {
        'TablixColumns': Meta(Element.ELEMENT, Card.ONE),
        'TablixRows': Meta(Element.ELEMENT, Card.ONE),
        }

    def __init__(self, node, lnk):
        super(TablixBody, self).__init__(node, lnk)


class TablixColumns(Element):

    _element_list = {
        'TablixColumn': Meta(Element.ELEMENT, Card.ONE_MANY)
        }

    def __init__(self, node, lnk):
        self.column_list = []
        super(TablixColumns, self).__init__(node, lnk)


class TablixColumn(Element):

    _element_list = {
        'Width': Meta(Element.SIZE, Card.ONE, True)
        }

    def __init__(self, node, lnk):
        super(TablixColumn, self).__init__(node, lnk)
        lnk.parent.column_list.append(self)


class TablixRows(Element):

    _element_list = {
        'TablixRow': Meta(Element.ELEMENT, Card.ONE_MANY)
        }

    def __init__(self, node, lnk):
        self.row_list = []
        super(TablixRows, self).__init__(node, lnk)


class TablixRow(Element):

    _element_list = {
            'Height': Meta(Element.SIZE, Card.ONE, True),
            'TablixCells': Meta(Element.ELEMENT, Card.ONE),
        }

    def __init__(self, node, lnk):
        super(TablixRow, self).__init__(node, lnk)
        lnk.parent.row_list.append(self)


class TablixCells(Element):

    _element_list = {
        'TablixCell': Meta(Element.ELEMENT, Card.ONE_MANY)
        }

    def __init__(self, node, lnk):
        self.cell_list = []
        super(TablixCells, self).__init__(node, lnk)


class TablixCell(Element):

    _element_list = {
        'CellContents': Meta(),
        'DataElementName': Meta(
            Element.STRING, constant=True, default='Cell'),
        'DataElementOutput': Meta(
            Element.ENUM, constant=True, default='ContentsOnly'),
        }

    def __init__(self, node, lnk):
        super(TablixCell, self).__init__(node, lnk)
        lnk.parent.cell_list.append(self)


class PageBreak(Element):

    _element_list = {
        'BreakLocation': Meta(Element.ENUM, Card.ONE, True)
        }

    def __init__(self, node, lnk):
        super(PageBreak, self).__init__(node, lnk)
