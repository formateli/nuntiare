# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ..types.element import Element
from ..types.enum import Enum

class BorderStyle(Enum):
    enum_list={'none': 'None', 
               'dotted': 'Dotted', 
               'dashed': 'Dashed', 
               'solid': 'Solid', 
               'double': 'Double', 
               'groove': 'Groove', 
               'ridge': 'Ridge', 
               'inset': 'Inset', 
               'windowinset': 'WindowInset', 
               'outset': 'Outset',
              }

    def __init__(self, expression):
        super(BorderStyle, self).__init__('BorderStyle', expression, BorderStyle.enum_list)


class BorderElement(Element):
    def __init__(self, node, lnk):     
        elements={'Color': [Element.COLOR],
                  'Style': [Element.ENUM, 'BorderStyle'],
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

