# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from . expression import Expression
from .. import logger

class _Enum(Expression):
    def __init__(self, expression, enum_list, 
            lnk, must_be_constant):
        self._enum_list = enum_list
        super(_Enum, self).__init__(expression, lnk, must_be_constant)

    def value(self, report):
        name = super(_Enum, self).value(report)
        return self._get_enum_by_name(name)

    def _get_enum_by_name(self, name):
        if not name or name == '':
            return None
        l_name = name.strip().lower()
        if l_name in self._enum_list:
            return self._enum_list[l_name]

        logger.error(
            "Invalid value '{0}' for Enum '{1}'. Valid values are: {2}".format(
                name, self.__class__.__name__, self.get_values_list()), True)

    def get_values_list(self):
        result = []
        for key, value in self._enum_list.items():
            result.append(value)
        return result


class DataElementOutput(_Enum):
    enum_list={'auto': 'Auto',
               'output': 'Output', 
               'nooutput': 'NoOutput', 
               'contentsonly': 'ContentsOnly',                
              }

    def __init__(self, expression, lnk, must_be_constant):
        super(DataElementOutput, self).__init__(
            expression, DataElementOutput.enum_list, lnk, must_be_constant)

                
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
        super(BorderStyle, self).__init__(
            expression, BorderStyle.enum_list, lnk, must_be_constant)


class FontStyle(_Enum):
    enum_list={'normal': 'Normal',
               'italic': 'Italic', 
              }

    def __init__(self, expression, lnk, must_be_constant):
        super(FontStyle, self).__init__(
            expression, FontStyle.enum_list, lnk, must_be_constant)


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
        super(FontWeight, self).__init__(
            expression, FontWeight.enum_list, lnk, must_be_constant)


class TextDecoration(_Enum):
    enum_list={'none': 'None',
               'underline': 'Underline', 
               'overline': 'Overline', 
               'linethrough': 'LineThrough', 
              }

    def __init__(self, expression, lnk, must_be_constant):
        super(TextDecoration, self).__init__(
            expression, TextDecoration.enum_list, lnk, must_be_constant)


class TextAlign(_Enum):
    enum_list={'none': 'None',
               'left': 'Left', 
               'center': 'Center', 
               'right': 'Right', 
               'justify': 'Justify', 
              }

    def __init__(self, expression, lnk, must_be_constant):
        super(TextAlign, self).__init__(
            expression, TextAlign.enum_list, lnk, must_be_constant)


class VerticalAlign(_Enum):
    enum_list={'top': 'Top',
               'middle': 'Middle', 
               'bottom': 'Bottom', 
              }

    def __init__(self, expression, lnk, must_be_constant):
        super(VerticalAlign, self).__init__(
            expression, VerticalAlign.enum_list, lnk, must_be_constant)


class TextDirection(_Enum):
    enum_list={'ltr': 'LTR',
               'rtl': 'RTL', 
              }

    def __init__(self, expression, lnk, must_be_constant):
        super(TextDirection, self).__init__(
            expression, TextDirection.enum_list, lnk, must_be_constant)


class WritingMode(_Enum):
    enum_list={'lr-tb': 'LR-TB',
               'tb-rl': 'TB-RL', 
              }

    def __init__(self, expression, lnk, must_be_constant):
        super(WritingMode, self).__init__(
            expression, WritingMode.enum_list, lnk, must_be_constant)


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
        super(BackgroundRepeat, self).__init__(
            expression, BackgroundRepeat.enum_list, lnk, must_be_constant)


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
        super(BackgroundGradientType, self).__init__(
            expression, BackgroundGradientType.enum_list, lnk, must_be_constant)            


class DataType(_Enum):
    enum_list={'boolean': 'Boolean',
               'datetime': 'DateTime', 
               'integer': 'Integer', 
               'float': 'Float', 
               'decimal': 'Decimal',
               'string': 'String', 
               'object': 'Object',
              }

    def __init__(self, expression, lnk, must_be_constant):
        super(DataType, self).__init__(
            expression, DataType.enum_list, lnk, must_be_constant)


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
        super(Operator, self).__init__(
            expression, Operator.enum_list, lnk, must_be_constant)


class SortDirection(_Enum):
    enum_list={'ascending': 'Ascending',
               'descending': 'Descending',  
              }
    def __init__(self, expression, lnk, must_be_constant):
        super(SortDirection, self).__init__(
            expression, SortDirection.enum_list, lnk, must_be_constant)


class BreakLocation(_Enum):
    '''
    BreakLocation enum.
    Start: There should be a page break
        before the report item or each
        instance of the group.
    End: There should be a page break
        after the report item or each
        instance of the group.
    StartAndEnd: There should be a page break
        both before and after the report item 
        or each instance of the group.
    Between: There should be a page break
        between each instance of the group 
        (does not apply to reportitems).
    '''

    enum_list={'start': 'Start',
               'end': 'End',
               'startandend': 'StartAndEnd',
               'between': 'Between',
              }
    def __init__(self, expression, lnk, must_be_constant):
        super(BreakLocation, self).__init__(
            expression, BreakLocation.enum_list, lnk, must_be_constant)


class ImageSource(_Enum):
    '''
    The source of the image
    '''
    enum_list={'external': 'External',
               'embedded': 'Embedded',
               'database': 'Database',
              }
    def __init__(self, expression, lnk, must_be_constant):
        super(ImageSource, self).__init__(
            expression, ImageSource.enum_list, lnk, must_be_constant)


class ImageSizing(_Enum):
    '''
    Defines the behavior if the image does not fit in the
    specified size.
    '''
    enum_list={'autosize': 'AutoSize',
               'fit': 'Fit',
               'fitproportional': 'FitProportional',
               'clip': 'Clip',
              }
    def __init__(self, expression, lnk, must_be_constant):
        super(ImageSizing, self).__init__(
            expression, ImageSizing.enum_list, lnk, must_be_constant)


class LayoutDirection(_Enum):
    '''
    Indicates the overall direction of the layout.
    '''
    enum_list={'ltr': 'LTR',
               'rtl': 'RTL',
              }
    def __init__(self, expression, lnk, must_be_constant):
        super(LayoutDirection, self).__init__(
            expression, LayoutDirection.enum_list, lnk, must_be_constant)

