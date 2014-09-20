# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from report_item import ReportItem
from ... types.element import Element
from .... tools import get_expression_value_or_default

class Rectangle(ReportItem):
    def __init__(self, node, lnk):
        elements={'ReportItems': [Element.ELEMENT], 
                  'PageBreak': [Element.ELEMENT], 
                  'KeepTogether': [Element.BOOLEAN, True],
                  'OmitBorderOnPageBreak': [Element.BOOLEAN, True],
                 }
        super(Rectangle, self).__init__("Rectangle", node, lnk, elements)
        self.keep_together = get_expression_value_or_default (None, self, "KeepTogether", True)
        self.omit_border_on_page_break = get_expression_value_or_default (None, self, "OmitBorderOnPageBreak", True)
        self.page_break = get_expression_value_or_default (None, self.get_element("PageBreak"), 
                    "BreakLocation", None)
        
