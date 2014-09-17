# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from .. report_element import ReportElement
from ... types.element import Element
from ... types.expression import verify_expression_required
from .... tools import get_expression_value_or_default

class ReportItems(Element):
    '''
    The ReportItems element is a collection of report items (used to define the contents of a region
    of a report).
    '''

    def __init__(self, node, lnk):
        elements={'Line': [Element.ELEMENT],
                  'Rectangle': [Element.ELEMENT],
                  'Textbox': [Element.ELEMENT],
                  'Image': [Element.ELEMENT],
                  'Subreport': [Element.ELEMENT],
                  'Grid': [Element.ELEMENT],
                  'Tablix': [Element.ELEMENT], 
                  'Chart': [Element.ELEMENT],
                 }
        super(ReportItems, self).__init__(node, elements, lnk)


class ReportItem(ReportElement):
    '''
    A report item is one of the following types of objects: Line, Rectangle, Textbox, Image,
      Subreport, CustomReportItem or DataRegion. DataRegions are: Tablix and Chart.
    The ReportItem element itself is not used. Instead, specific report item element is used wherever
      ReportItem is allowed.
    '''

    def __init__(self, type, node, lnk, additional_elements):
        elements={'Name': [Element.STRING, True],
                  'ActionInfo': [Element.ELEMENT],
                  'Top': [Element.SIZE, True], 
                  'Left': [Element.SIZE, True],                   
                  'Height': [Element.SIZE, True],
                  'Width': [Element.SIZE, True],
                  'ZIndex': [Element.INTEGER, True],
                  'Visibility': [Element.ELEMENT],
                  'ToolTip': [Element.STRING],    
                  'Bookmark': [Element.STRING],                                
                  'RepeatWith': [Element.STRING, True],
                  'DataElementName': [Element.STRING, True],
                  'DataElementOutput': [Element.ENUM],
                 }
        if additional_elements:
            for key, value in additional_elements.items():
                elements[key] = value

        super(ReportItem, self).__init__(node, elements, lnk)
        self.type = type
        
        self.name = get_expression_value_or_default (None, self, 'Name', None)         
        verify_expression_required("Name", 'ReportItem ' + self.type, self.name)

        self.zindex = get_expression_value_or_default (None, self, "ZIndex", 0)


