# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from report_item import ReportItem
from ... types.element import Element

class Rectangle(ReportItem):
    def __init__(self, node, lnk):
        elements={'ReportItems': [Element.ELEMENT], 
                  'PageBreak': [Element.ELEMENT], 
                  'KeepTogether': [Element.BOOLEAN, True],
                  'OmitBorderOnPageBreak': [Element.BOOLEAN, True],
                 }
        super(Rectangle, self).__init__("Rectangle", node, lnk, elements)
        
