# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
from . expression import Expression
from .. import LOGGER


class _Enum(Expression):
    def __init__(self, expression, lnk, must_be_constant):
        super(_Enum, self).__init__(expression, lnk, must_be_constant)

    def value(self, report):
        name = super(_Enum, self).value(report)
        return self._get_enum_by_name(name)

    @classmethod
    def _get_enum_by_name(cls, name):
        if name is None or name == '':
            return
        if name in cls.enum_list:
            return name
        LOGGER.error(
            "Invalid value '{0}' for Enum '{1}'. Valid values are: {2}".format(
                name, cls.__name__, cls.enum_list), True)


class DataElementStyle(_Enum):
    enum_list = [
        'Auto',
        'Attribute',
        'Element'
    ]
    def __init__(self, expression, lnk, must_be_constant):
        super(DataElementStyle, self).__init__(
            expression, lnk, must_be_constant)


class DataElementOutput(_Enum):
    enum_list = [
        'Auto',
        'Output',
        'NoOutput',
        'ContentsOnly'
    ]
    def __init__(self, expression, lnk, must_be_constant):
        super(DataElementOutput, self).__init__(
            expression, lnk, must_be_constant)


class BorderStyle(_Enum):
    enum_list = [
        'None',
        'Dotted',
        'Dashed',
        'Solid',
        'Double',
        'Groove',
        'Ridge',
        'Inset',
        'WindowInset',
        'Outset',
    ]
    def __init__(self, expression, lnk, must_be_constant):
        super(BorderStyle, self).__init__(
            expression, lnk, must_be_constant)


class FontStyle(_Enum):
    enum_list = [
        'Normal',
        'Italic',
    ]
    def __init__(self, expression, lnk, must_be_constant):
        super(FontStyle, self).__init__(
            expression, lnk, must_be_constant)


class FontWeight(_Enum):
    enum_list = [
        'Lighter',
        'Normal',
        'Bold',
        'Bolder',
        '100',
        '200',
        '300',
        '400',
        '500',
        '600',
        '700',
        '800',
        '900',
    ]
    def __init__(self, expression, lnk, must_be_constant):
        super(FontWeight, self).__init__(
            expression, lnk, must_be_constant)


class TextDecoration(_Enum):
    enum_list = [
        'None',
        'Underline',
        'Overline',
        'LineThrough',
    ]
    def __init__(self, expression, lnk, must_be_constant):
        super(TextDecoration, self).__init__(
            expression, lnk, must_be_constant)


class TextAlign(_Enum):
    enum_list = [
        'None',
        'Left',
        'Center',
        'Right',
        'Justify',
    ]
    def __init__(self, expression, lnk, must_be_constant):
        super(TextAlign, self).__init__(
            expression, lnk, must_be_constant)


class VerticalAlign(_Enum):
    enum_list = [
        'Top',
        'Middle',
        'Bottom',
    ]
    def __init__(self, expression, lnk, must_be_constant):
        super(VerticalAlign, self).__init__(
            expression, lnk, must_be_constant)


class TextDirection(_Enum):
    enum_list = [
        'LTR',
        'RTL',
    ]
    def __init__(self, expression, lnk, must_be_constant):
        super(TextDirection, self).__init__(
            expression, lnk, must_be_constant)


class WritingMode(_Enum):
    enum_list = [
        'LR-TB',
        'TB-RL',
    ]
    def __init__(self, expression, lnk, must_be_constant):
        super(WritingMode, self).__init__(
            expression, lnk, must_be_constant)


class BackgroundRepeat(_Enum):
    enum_list = [
        'Repeat',
        'NoRepeat',
        'RepeatX',
        'RepeatY',
    ]
    def __init__(self, expression, lnk, must_be_constant):
        super(BackgroundRepeat, self).__init__(
            expression, lnk, must_be_constant)


class BackgroundGradientType(_Enum):
    enum_list = [
        'None',
        'LeftRight',
        'TopBottom',
        'Center',
        'DiagonalLeft',
        'DiagonalRight',
        'HorizontalCenter',
        'VerticalCenter',
    ]
    def __init__(self, expression, lnk, must_be_constant):
        super(BackgroundGradientType, self).__init__(
            expression, lnk, must_be_constant)


class DataType(_Enum):
    enum_list = [
        'Boolean',
        'DateTime',
        'Integer',
        'Float',
        'Decimal',
        'String',
        'Object',
    ]
    def __init__(self, expression, lnk, must_be_constant):
        super(DataType, self).__init__(
            expression, lnk, must_be_constant)


class Operator(_Enum):
    enum_list = [
        'Equal',
        'Like',
        'NotEqual',
        'GreaterThan',
        'GreaterThanOrEqual',
        'LessThan',
        'LessThanOrEqual',
        'TopN',
        'BottomN',
        'TopPercent',
        'BottomPercent',
        'In',
        'Between',
    ]
    def __init__(self, expression, lnk, must_be_constant):
        super(Operator, self).__init__(
            expression, lnk, must_be_constant)


class SortDirection(_Enum):
    enum_list = [
        'Ascending',
        'Descending',
    ]
    def __init__(self, expression, lnk, must_be_constant):
        super(SortDirection, self).__init__(
            expression, lnk, must_be_constant)


class BreakLocation(_Enum):
    enum_list = [
        'Start',
        'End',
        'StartAndEnd',
        'Between',
    ]
    def __init__(self, expression, lnk, must_be_constant):
        super(BreakLocation, self).__init__(
            expression, lnk, must_be_constant)


class ImageSource(_Enum):
    enum_list = [
        'External',
        'Embedded',
        'Database',
    ]
    def __init__(self, expression, lnk, must_be_constant):
        super(ImageSource, self).__init__(
            expression, lnk, must_be_constant)


class ImageSizing(_Enum):
    enum_list = [
        'AutoSize',
        'Fit',
        'FitProportional',
        'Clip',
    ]
    def __init__(self, expression, lnk, must_be_constant):
        super(ImageSizing, self).__init__(
            expression, lnk, must_be_constant)


class LayoutDirection(_Enum):
    enum_list = [
        'LTR',
        'RTL',
    ]
    def __init__(self, expression, lnk, must_be_constant):
        super(LayoutDirection, self).__init__(
            expression, lnk, must_be_constant)


class Position(_Enum):
    enum_list = [
        'Top',
        'TopLeft',
        'TopRight',
        'Left',
        'Center',
        'Right',
        'BottomRight',
        'Bottom',
        'BottomLeft'
    ]
    def __init__(self, expression, lnk, must_be_constant):
        super(LayoutDirection, self).__init__(
            expression, lnk, must_be_constant)
