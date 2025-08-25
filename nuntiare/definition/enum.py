# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
from . expression import Expression
from .. import LOGGER


class _Enum(Expression):
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


class DataElementOutput(_Enum):
    enum_list = [
        'Auto',
        'Output',
        'NoOutput',
        'ContentsOnly'
    ]


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


class FontStyle(_Enum):
    enum_list = [
        'Normal',
        'Italic',
    ]


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


class TextDecoration(_Enum):
    enum_list = [
        'None',
        'Underline',
        'Overline',
        'LineThrough',
    ]


class TextAlign(_Enum):
    enum_list = [
        'None',
        'Left',
        'Center',
        'Right',
        'Justify',
    ]


class VerticalAlign(_Enum):
    enum_list = [
        'Top',
        'Middle',
        'Bottom',
    ]


class TextDirection(_Enum):
    enum_list = [
        'LTR',
        'RTL',
    ]


class WritingMode(_Enum):
    enum_list = [
        'LR-TB',
        'TB-RL',
    ]


class BackgroundRepeat(_Enum):
    enum_list = [
        'Repeat',
        'NoRepeat',
        'RepeatX',
        'RepeatY',
    ]


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


class SortDirection(_Enum):
    enum_list = [
        'Ascending',
        'Descending',
    ]


class BreakLocation(_Enum):
    enum_list = [
        'Start',
        'End',
        'StartAndEnd',
        'Between',
    ]


class ImageSource(_Enum):
    enum_list = [
        'External',
        'Embedded',
        'Database',
    ]


class ImageSizing(_Enum):
    enum_list = [
        'AutoSize',
        'Fit',
        'FitProportional',
        'Clip',
    ]


class LayoutDirection(_Enum):
    enum_list = [
        'LTR',
        'RTL',
    ]


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
