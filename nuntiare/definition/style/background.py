# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from nuntiare.definition.element import Element
from nuntiare.definition.enum import Enum

class BackgroudImage(Element):
    def __init__(self, node, lnk):
        elements={'Source': [Element.ENUM, 'ImageSource'],
                  'Value': [Element.STRING],
                  'MIMEType': [Element.STRING],
                  'Top': [Element.COLOR],
                  'BackgroundRepeat': [Element.ENUM, 'BackgroundRepeat'],
                 }
        super(BackgroudImage, self).__init__(node, elements, lnk)


class BackgroundRepeat(Enum):
    '''
    Indicates how the background image should
    repeat to fill the available space: vertically
    (y), horizontally (x), both or neither
    '''

    enum_list={'repeat': 'Repeat',
               'norepeat': 'NoRepeat', 
               'repeatx': 'RepeatX', 
               'repeaty': 'RepeatY', 
              }

    def __init__(self, expression):
        super(BackgroundRepeat, self).__init__('BackgroundRepeat', expression, BackgroundRepeat.enum_list)


class BackgroundGradientType(Enum):
    enum_list={'none': 'None',
               'leftright': 'LeftRight', 
               'topbottom': 'TopBottom', 
               'center': 'Center', 
               'diagonalleft': 'DiagonalLeft', 
               'diagonalright': 'DiagonalRight', 
               'horizontalcenter': 'HorizontalCenter', 
               'verticalcenter': 'VerticalCenter', 
              }

    def __init__(self, expression):
        super(BackgroundGradientType, self).__init__('BackgroundGradientType', expression, BackgroundGradientType.enum_list)

    
