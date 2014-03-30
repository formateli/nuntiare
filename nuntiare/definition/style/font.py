# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ...definition.enum import Enum

class FontStyle(Enum):
    enum_list={'normal': 'Normal',
               'italic': 'Italic', 
              }

    def __init__(self, expression):
        super(FontStyle, self).__init__('FontStyle', expression, FontStyle.enum_list)


class FontWeight(Enum):
    enum_list={'lighter': 'Lighter',
               'normal': 'Normal', 
               'bold': 'Bold', 
               'bolder': 'Bolder', 
               '100': '100', 
               '200': '200', 
               '300': '300', 
               '400': '400', 
               '500': '500', 
               '600': '600', 
               '700': '700', 
               '800': '800', 
               '900': '900', 
              }

    def __init__(self, expression):
        super(FontWeight, self).__init__('FontWeight', expression, FontWeight.enum_list)


class TextDecoration(Enum):
    enum_list={'none': 'None',
               'underline': 'Underline', 
               'overline': 'Overline', 
               'linethrough': 'LineThrough', 
              }

    def __init__(self, expression):
        super(TextDecoration, self).__init__('TextDecoration', expression, TextDecoration.enum_list)


class TextAlign(Enum):
    enum_list={'none': 'None',
               'left': 'Left', 
               'center': 'Center', 
               'right': 'Right', 
               'justify': 'Justify', 
              }

    def __init__(self, expression):
        super(TextAlign, self).__init__('TextAlign', expression, TextAlign.enum_list)


class VerticalAlign(Enum):
    enum_list={'top': 'Top',
               'middle': 'Middle', 
               'bottom': 'Bottom', 
              }

    def __init__(self, expression):
        super(VerticalAlign, self).__init__('VerticalAlign', expression, VerticalAlign.enum_list)


class TextDirection(Enum):
    enum_list={'ltr': 'LTR',
               'rtl': 'RTL', 
              }

    def __init__(self, expression):
        super(TextDirection, self).__init__('TextDirection', expression, TextDirection.enum_list)


class WritingMode(Enum):
    enum_list={'lr-tb': 'LR-TB',
               'tb-rl': 'TB-RL', 
              }

    def __init__(self, expression):
        super(WritingMode, self).__init__('WritingMode', expression, WritingMode.enum_list)





