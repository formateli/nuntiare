# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ...definition.element import Element
from ...definition.enum import Enum

class BorderColor(Element):
    def __init__(self, node, lnk):     
        elements={'Default': [Element.COLOR],
                  'Left': [Element.COLOR],
                  'Right': [Element.COLOR],
                  'Top': [Element.COLOR],
                  'Bottom': [Element.COLOR],
                 }
        super(BorderColor, self).__init__(node, elements, lnk)


class BorderWidth(Element):
    def __init__(self, node, lnk):
        elements={'Default': [Element.SIZE],
                  'Left': [Element.SIZE],
                  'Right': [Element.SIZE],
                  'Top': [Element.SIZE],
                  'Bottom': [Element.SIZE],
                 }
        super(BorderWidth, self).__init__(node, elements, lnk)


class BorderStyle(Element):
    def __init__(self, node, lnk):
        elements={'Default': [Element.ENUM, 'BorderStyle'],
                  'Left': [Element.ENUM, 'BorderStyle'],
                  'Right': [Element.ENUM, 'BorderStyle'],
                  'Top': [Element.ENUM, 'BorderStyle'],
                  'Bottom': [Element.ENUM, 'BorderStyle'],
                 }
        super(BorderStyle, self).__init__(node, elements, lnk)


class BorderStyleEnum(Enum):
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
        super(BorderStyleEnum, self).__init__('BorderStyle', expression, BorderStyleEnum.enum_list)


