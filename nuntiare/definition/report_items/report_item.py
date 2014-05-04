# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ...definition.element import Element
from ...definition.expression import verify_expression_constant_and_required
from ...tools import raise_error_with_log, get_expression_value_or_default

class ReportItems(Element):
    def __init__(self, node, lnk):
        elements={'Line': [Element.ELEMENT],
                  'Rectangle': [Element.ELEMENT],
                  'Textbox': [Element.ELEMENT],
                  'Image': [Element.ELEMENT],
                  'Subreport': [Element.ELEMENT],
                  'CustomReportItem': [Element.ELEMENT],
                  'Grid': [Element.ELEMENT],
                  'Table': [Element.ELEMENT],
                 }
        
        super(ReportItems, self).__init__(node, elements, lnk)


class ReportItem(Element):
    '''
    A report item is one of the following types of objects: Line, Rectangle, Textbox, Image,
    Subreport, CustomReportItem or DataRegion. DataRegions are: List, Table, Matrix, and Chart.
    The ReportItem element itself is not used. Instead, specific report item element is used wherever
    ReportItem is allowed.
    '''

    def __init__(self, type, node, lnk, additional_elements):
        elements={'Name': [Element.STRING], 
                  'Style': [Element.ELEMENT],
                  'Action': [Element.ELEMENT],
                  'Top': [Element.SIZE],
                  'Left': [Element.SIZE],
                  'Height': [Element.SIZE],
                  'Width': [Element.SIZE],
                  'ZIndex': [Element.INTEGER],
                  'Visibility': [Element.ELEMENT],
                  'ToolTip': [Element.STRING],
                  'LinkToChild': [Element.STRING],
                  'Bookmark': [Element.STRING],
                  'RepeatWith': [Element.STRING],
                  'Custom': [Element.ELEMENT],
                 }

        if additional_elements:
            for key, value in additional_elements.items():
                elements[key] = value

        super(ReportItem, self).__init__(node, elements, lnk)
        self.type = type

        name = verify_expression_constant_and_required("Name", "ReportItem", self.get_element("Name"))
        self.name = name.value()
        self.zindex = get_expression_value_or_default(self, "ZIndex", 0)
        self.top = get_expression_value_or_default(self, "Top", 0)
        self.left = get_expression_value_or_default(self, "Left", 0)
        self.height = get_expression_value_or_default(self, "Height", 1)
        self.width = get_expression_value_or_default(self, "Width", 1)


class Line(ReportItem):
    def __init__(self, node, lnk):
        super(Line, self).__init__("Line", node, lnk, None)


class Rectangle(ReportItem):
    def __init__(self, node, lnk):
        elements={'ReportItems': [Element.ELEMENT], 
                  'PageBreakAtStart': [Element.BOOLEAN],
                  'PageBreakAtEnd': [Element.BOOLEAN],
                 }
        super(Rectangle, self).__init__("Rectangle", node, lnk, elements)


class Image(ReportItem):
    def __init__(self, node, lnk):
        elements={'Source': [Element.ENUM, 'ImageSource'],
                  'Value': [Element.VARIANT],
                  'MIMEType': [Element.STRING],
                  'Sizing': [Element.ENUM, 'ImageSizing'],
                 }
        super(Image, self).__init__("Image", node, lnk, elements)


class Textbox(ReportItem):
    def __init__(self, node, lnk):
        elements={'Value': [Element.VARIANT],
                  'CanGrow': [Element.BOOLEAN],
                  'CanShrink': [Element.BOOLEAN],
                  'HideDuplicates': [Element.STRING],
                  'ToggleImage': [Element.ELEMENT],
                  'UserSort': [Element.ELEMENT],
                 }
        super(Textbox, self).__init__("Textbox", node, lnk, elements)

