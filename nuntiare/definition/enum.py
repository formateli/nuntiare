# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from . expression import Expression
from .. import logger

class _Enum(Expression):
    def __init__(self, enum_name, expression, enum_list, 
            lnk, must_be_constant):
        self.name = enum_name 
        self.enum_list = enum_list
        super(_Enum, self).__init__(expression, lnk, must_be_constant)

    def value(self, report):
        name = super(_Enum, self).value(report)
        return self.get_enum_by_name(name)

    def get_enum_by_name(self, name):
        if not name or name == '':
            return None
        name=name.strip().lower()
        if self.enum_list.has_key(name):
            return self.enum_list[name]

        logger.warn("Unknown value '{0}' for Enum '{1}'. <None> assigned.".format(name, self.name))
        return None

        
class DataElementOutput(_Enum):
    enum_list={'auto': 'Auto',
               'output': 'Output', 
               'nooutput': 'NoOutput', 
               'contentsonly': 'ContentsOnly',                
              }

    def __init__(self, expression, lnk, must_be_constant):
        super(DataElementOutput, self).__init__('DataElementOutput', expression, 
                DataElementOutput.enum_list, lnk, must_be_constant)


class DataElementStyle(_Enum):    
    enum_list={'auto': 'Auto',
               'attribute': 'Attribute', 
               'element': 'Element', 
              }

    def __init__(self, expression, lnk, must_be_constant):
        super(DataElementStyle, self).__init__('DataElementStyle', expression, 
                DataElementStyle.enum_list, lnk, must_be_constant)

                
class BorderStyle(_Enum):
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

    def __init__(self, expression, lnk, must_be_constant):
        super(BorderStyle, self).__init__('BorderStyle', expression, 
                BorderStyle.enum_list, lnk, must_be_constant)
                
class FontStyle(_Enum):
    enum_list={'normal': 'Normal',
               'italic': 'Italic', 
              }

    def __init__(self, expression, lnk, must_be_constant):
        super(FontStyle, self).__init__('FontStyle', expression, 
            FontStyle.enum_list, lnk, must_be_constant)


class FontWeight(_Enum):
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

    def __init__(self, expression, lnk, must_be_constant):
        super(FontWeight, self).__init__('FontWeight', expression, 
            FontWeight.enum_list, lnk, must_be_constant)


class TextDecoration(_Enum):
    enum_list={'none': 'None',
               'underline': 'Underline', 
               'overline': 'Overline', 
               'linethrough': 'LineThrough', 
              }

    def __init__(self, expression, lnk, must_be_constant):
        super(TextDecoration, self).__init__('TextDecoration', expression, 
            TextDecoration.enum_list, lnk, must_be_constant)


class TextAlign(_Enum):
    enum_list={'none': 'None',
               'left': 'Left', 
               'center': 'Center', 
               'right': 'Right', 
               'justify': 'Justify', 
              }

    def __init__(self, expression, lnk, must_be_constant):
        super(TextAlign, self).__init__('TextAlign', expression, 
            TextAlign.enum_list, lnk, must_be_constant)


class VerticalAlign(_Enum):
    enum_list={'top': 'Top',
               'middle': 'Middle', 
               'bottom': 'Bottom', 
              }

    def __init__(self, expression, lnk, must_be_constant):
        super(VerticalAlign, self).__init__('VerticalAlign', expression, 
            VerticalAlign.enum_list, lnk, must_be_constant)


class TextDirection(_Enum):
    enum_list={'ltr': 'LTR',
               'rtl': 'RTL', 
              }

    def __init__(self, expression, lnk, must_be_constant):
        super(TextDirection, self).__init__('TextDirection', expression, 
            TextDirection.enum_list, lnk, must_be_constant)


class WritingMode(_Enum):
    enum_list={'lr-tb': 'LR-TB',
               'tb-rl': 'TB-RL', 
              }

    def __init__(self, expression, lnk, must_be_constant):
        super(WritingMode, self).__init__('WritingMode', expression, 
            WritingMode.enum_list, lnk, must_be_constant)


class BackgroundRepeat(_Enum):
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

    def __init__(self, expression, lnk, must_be_constant):
        super(BackgroundRepeat, self).__init__('BackgroundRepeat', expression, 
                BackgroundRepeat.enum_list, lnk, must_be_constant)


class BackgroundGradientType(_Enum):
    enum_list={'none': 'None',
               'leftright': 'LeftRight', 
               'topbottom': 'TopBottom', 
               'center': 'Center', 
               'diagonalleft': 'DiagonalLeft', 
               'diagonalright': 'DiagonalRight', 
               'horizontalcenter': 'HorizontalCenter', 
               'verticalcenter': 'VerticalCenter', 
              }

    def __init__(self, expression, lnk, must_be_constant):
        super(BackgroundGradientType, self).__init__('BackgroundGradientType', expression, 
                BackgroundGradientType.enum_list, lnk, must_be_constant)            


class DataType(_Enum):
    enum_list={'boolean': 'Boolean',
               'datetime': 'DateTime', 
               'integer': 'Integer', 
               'float': 'Float', 
               'decimal': 'Decimal',
               'string': 'String', 
              }

    def __init__(self, expression, lnk, must_be_constant):
        super(DataType, self).__init__('DataType', expression, 
            DataType.enum_list, lnk, must_be_constant)
            
            
class Operator(_Enum):
    enum_list={'equal': 'Equal',
               'like': 'Like',  
               'notequal': 'NotEqual',  
               'greaterthan': 'GreaterThan',
               'greaterthanorequal': 'GreaterThanOrEqual',
               'lessthan': 'LessThan',
               'lessthanorequal': 'LessThanOrEqual',
               'topn': 'TopN',
               'bottomn': 'BottomN',
               'toppercent': 'TopPercent',
               'bottompercent': 'BottomPercent',
               'in': 'In',
               'between': 'Between',
              }
    def __init__(self, expression, lnk, must_be_constant):
        super(Operator, self).__init__('Operator', expression, 
                Operator.enum_list, lnk, must_be_constant)
                
                
class SortDirection(_Enum):
    enum_list={'ascending': 'Ascending',
               'descending': 'Descending',  
              }
    def __init__(self, expression, lnk, must_be_constant):
        super(SortDirection, self).__init__('SortDirection', expression, 
            SortDirection.enum_list, lnk, must_be_constant)
            

class Function(_Enum):
    enum_list={'sum': 'Sum',
               'avg': 'Avg',
               'max': 'Max',
               'min': 'Min',
               'count': 'Count',
               'countdistinct': 'CountDistinct',
               'countrows': 'CountRows',
               'stdev': 'stDev',
               'stdevp': 'stDevP',
               'var': 'Var',
               'varp': 'VarP',
               'first': 'First',
               'last': 'Last',
               'previous': 'Previous',
               'custom': 'Custom',
              }
    def __init__(self, expression, lnk, must_be_constant):
        super(Function, self).__init__('VariableFunction', expression, 
            Function.enum_list, lnk, must_be_constant)
        
