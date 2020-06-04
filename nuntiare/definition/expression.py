# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
from .. import LOGGER
from .. data.data_type import DataType


class Expression:
    def __init__(self, expression, lnk, must_be_constant):
        self.lnk = lnk
        self.must_be_constant = must_be_constant
        self.expression, self.is_constant = self.set_expression(expression)

    def set_expression(self, expression):
        is_constant = False
        if expression is None:
            is_constant = True
        try:
            if not expression.startswith('='):
                is_constant = True
        except Exception:
            # It is probably an object
            is_constant = True

        if self.must_be_constant and not is_constant:
            err_msg = "Invalid expression '{0}' for '{1}' in '{2}' element." \
                " It must be a constant expression."
            LOGGER.error(err_msg.format(
                expression, self.lnk.data,
                self.lnk.parent.__class__.__name__), True)
        return [expression, is_constant]

    def value(self, report, new_expression=None):
        if new_expression is not None:
            expression, is_constant = self.set_expression(new_expression)
        else:
            expression = self.expression
            is_constant = self.is_constant

        if is_constant:
            return expression

        # Remove '=' from begining
        ex = expression[1:]
        # Run python code
        return report.modules.resolve_expression(ex)

    @staticmethod
    def get_value_or_default(
                report, element,
                expression_name, default_value,
                direct_expression=None):
        '''
        Gets the value of a report element of type expression,
        or its default value
        '''
        if direct_expression is not None:
            value = direct_expression.value(report)
            if value is None:
                return default_value
            return value

        el = None
        if element:
            el = element.get_element(expression_name)

        if not el:
            return default_value

        value = el.value(report)
        if value is None:
            return default_value

        return value


class Color(Expression):

    _default_color = '#000000'

    def __init__(self, string_color, lnk, must_be_constant=False):
        super(Color, self).__init__(string_color, lnk, must_be_constant)
        self._color = None
        if not self.is_constant:
            return
        self._set_color(self.expression)

    def value(self, report):
        if self.is_constant:
            return self._color
        result = super(Color, self).value(report)
        if not result:
            return Color._default_color
        self._set_color(result)
        return self._color

    def _set_color(self, str_input):
        if str_input is None or str_input.strip() == '':
            self._color = self._default_color
            return

        str_input = str_input.strip()
        if str_input.startswith('#'):
            Color._validate_hex_color(str_input)
            self._color = str_input
        elif str_input.startswith('rgb'):
            pass  # TODO
        elif str_input.startswith('argb'):
            pass  # TODO
        else:
            self._color = self._get_color_by_name(str_input)

    @staticmethod
    def _validate_hex_color(hex_color):
        if not hex_color:
            LOGGER.error(
                "Invalid color '{0}'".format(hex_color), True)
        if len(hex_color) != 7 or not hex_color.startswith('#'):
            LOGGER.error(
                "Color '{0}' not in correct format.".format(hex_color), True)

    @staticmethod
    def to_rgb(hex_color):
        result = []
        Color._validate_hex_color(hex_color)
        hex_color = hex_color[1:]  # Remove '#'
        result.append(int(hex_color[0:2], 16))
        result.append(int(hex_color[2:4], 16))
        result.append(int(hex_color[4:], 16))
        return result

    @staticmethod
    def _get_color_by_name(name):
        name = name.lower()
        # See https://www.w3schools.com/colors/colors_names.asp
        if name == "aliceblue":
            return "#F0F8FF"
        if name == "antiquewhite":
            return "#FAEBD7"
        if name == "aqua":
            return "#00FFFF"
        if name == "aquamarine":
            return "#7FFFD4"
        if name == "azure":
            return "#F0FFFF"
        if name == "beige":
            return "#F5F5DC"
        if name == "bisque":
            return "#FFE4C4"
        if name == "black":
            return "#000000"
        if name == "blanchedalmond":
            return "#FFEBCD"
        if name == "blue":
            return "#0000FF"
        if name == "blueviolet":
            return "#8A2BE2"
        if name == "brown":
            return "#A52A2A"
        if name == "burlywood":
            return "#DEB887"
        if name == "cadetblue":
            return "#5F9EA0"
        if name == "chartreuse":
            return "#7FFF00"
        if name == "chocolate":
            return "#D2691E"
        if name == "coral":
            return "#FF7F50"
        if name == "cornflowerblue":
            return "#6495ED"
        if name == "cornsilk":
            return "#FFF8DC"
        if name == "crimson":
            return "#DC143C"
        if name == "cyan":
            return "#00FFFF"
        if name == "darkblue":
            return "#00008B"
        if name == "darkcyan":
            return "#008B8B"
        if name == "darkgoldenrod":
            return "#B8860B"
        if name == "darkgray":
            return "#A9A9A9"
        if name == "darkgreen":
            return "#006400"
        if name == "darkkhaki":
            return "#BDB76B"
        if name == "darkmagenta":
            return "#8B008B"
        if name == "darkolivegreen":
            return "#556B2F"
        if name == "darkorange":
            return "#FF8C00"
        if name == "darkorchid":
            return "#9932CC"
        if name == "darkred":
            return "#8B0000"
        if name == "darksalmon":
            return "#E9967A"
        if name == "darkseagreen":
            return "#8FBC8F"
        if name == "darkslateblue":
            return "#483D8B"
        if name == "darkslategray":
            return "#2F4F4F"
        if name == "darkturquoise":
            return "#00CED1"
        if name == "darkviolet":
            return "#9400D3"
        if name == "deeppink":
            return "#FF1493"
        if name == "deepskyblue":
            return "#00BFFF"
        if name == "dimgray":
            return "#696969"
        if name == "dodgerblue":
            return "#1E90FF"
        if name == "firebrick":
            return "#B22222"
        if name == "floralwhite":
            return "#FFFAF0"
        if name == "forestgreen":
            return "#228B22"
        if name == "fuchsia":
            return "#FF00FF"
        if name == "gainsboro":
            return "#DCDCDC"
        if name == "ghostwhite":
            return "#F8F8FF"
        if name == "gold":
            return "#FFD700"
        if name == "goldenrod":
            return "#DAA520"
        if name == "gray":
            return "#808080"
        if name == "green":
            return "#008000"
        if name == "greenyellow":
            return "#ADFF2F"
        if name == "honeydew":
            return "#F0FFF0"
        if name == "hotpink":
            return "#FF69B4"
        if name == "indianred":
            return "#CD5C5C"
        if name == "indigo":
            return "#4B0082"
        if name == "ivory":
            return "#FFFFF0"
        if name == "khaki":
            return "#F0E68C"
        if name == "lavender":
            return "#E6E6FA"
        if name == "lavenderblush":
            return "#FFF0F5"
        if name == "lawngreen":
            return "#7CFC00"
        if name == "lemonchiffon":
            return "#FFFACD"
        if name == "lightblue":
            return "#ADD8E6"
        if name == "lightcoral":
            return "#F08080"
        if name == "lightcyan":
            return "#E0FFFF"
        if name == "lightgoldenrodyellow":
            return "#FAFAD2"
        if name == "lightgrey":
            return "#D3D3D3"
        if name == "lightgreen":
            return "#90EE90"
        if name == "lightpink":
            return "#FFB6C1"
        if name == "lightsalmon":
            return "#FFA07A"
        if name == "lightseagreen":
            return "#20B2AA"
        if name == "lightskyblue":
            return "#87CEFA"
        if name == "lightslategray":
            return "#778899"
        if name == "lightsteelblue":
            return "#B0C4DE"
        if name == "lightyellow":
            return "#FFFFE0"
        if name == "lime":
            return "#00FF00"
        if name == "limegreen":
            return "#32CD32"
        if name == "linen":
            return "#FAF0E6"
        if name == "magenta":
            return "#FF00FF"
        if name == "maroon":
            return "#800000"
        if name == "mediumaquamarine":
            return "#66CDAA"
        if name == "mediumblue":
            return "#0000CD"
        if name == "mediumorchid":
            return "#BA55D3"
        if name == "mediumpurple":
            return "#9370DB"
        if name == "mediumseagreen":
            return "#3CB371"
        if name == "mediumslateblue":
            return "#7B68EE"
        if name == "mediumspringgreen":
            return "#00FA9A"
        if name == "mediumturquoise":
            return "#48D1CC"
        if name == "mediumvioletred":
            return "#C71585"
        if name == "midnightblue":
            return "#191970"
        if name == "mintcream":
            return "#F5FFFA"
        if name == "mistyrose":
            return "#FFE4E1"
        if name == "moccasin":
            return "#FFE4B5"
        if name == "navajowhite":
            return "#FFDEAD"
        if name == "navy":
            return "#000080"
        if name == "oldlace":
            return "#FDF5E6"
        if name == "olive":
            return "#808000"
        if name == "olivedrab":
            return "#6B8E23"
        if name == "orange":
            return "#FFA500"
        if name == "orangered":
            return "#FF4500"
        if name == "orchid":
            return "#DA70D6"
        if name == "palegoldenrod":
            return "#EEE8AA"
        if name == "palegreen":
            return "#98FB98"
        if name == "paleturquoise":
            return "#AFEEEE"
        if name == "palevioletred":
            return "#DB7093"
        if name == "papayawhip":
            return "#FFEFD5"
        if name == "peachpuff":
            return "#FFDAB9"
        if name == "peru":
            return "#CD853F"
        if name == "pink":
            return "#FFC0CB"
        if name == "powderblue":
            return "#B0E0E6"
        if name == "purple":
            return "#800080"
        if name == "red":
            return "#FF0000"
        if name == "rosybrown":
            return "#BC8F8F"
        if name == "royalblue":
            return "#4169E1"
        if name == "saddlebrown":
            return "#8B4513"
        if name == "salmon":
            return "#FA8072"
        if name == "sandybrown":
            return "#F4A460"
        if name == "seagreen":
            return "#2E8B57"
        if name == "seashell":
            return "#FFF5EE"
        if name == "sienna":
            return "#A0522D"
        if name == "silver":
            return "#C0C0C0"
        if name == "skyblue":
            return "#87CEEB"
        if name == "slateblue":
            return "#6A5ACD"
        if name == "slategray":
            return "#708090"
        if name == "snow":
            return "#FFFAFA"
        if name == "springgreen":
            return "#00FF7F"
        if name == "steelblue":
            return "#4682B4"
        if name == "tan":
            return "#D2B48C"
        if name == "teal":
            return "#008080"
        if name == "thistle":
            return "#D8BFD8"
        if name == "tomato":
            return "#FF6347"
        if name == "turquoise":
            return "#40E0D0"
        if name == "violet":
            return "#EE82EE"
        if name == "wheat":
            return "#F5DEB3"
        if name == "white":
            return "#FFFFFF"
        if name == "whitesmoke":
            return "#F5F5F5"
        if name == "yellow":
            return "#FFFF00"
        if name == "yellowgreen":
            return "#9ACD32"
        LOGGER.warn(
            "Color '{0}' not implemented. Default '{1}' assigned.".format(
                name, Color._default_color))
        return Color._default_color


class Size(Expression):
    size_6 = float(6)
    size_10 = float(10)
    size_25_4 = float(25.4)
    size_72 = float(72)

    def __init__(self, string_size, lnk, must_be_constant=False):
        super(Size, self).__init__(string_size, lnk, must_be_constant)
        self._size = None
        if not self.is_constant:
            return
        self._get_value(string_size)

    def value(self, report):
        if self.is_constant:
            return self._size
        result = super(Size, self).value(report)
        if not result:
            return 0.0
        return self._get_value(result)

    def _get_value(self, string_size):
        if not string_size:
            self._size = 0.0
            return self._size

        # convert to unicode
        string_size = DataType.get_value('String', string_size)

        units = ('in', 'cm', 'mm', 'pt', 'pc')

        string_size = string_size.strip()
        if len(string_size) < 3:
            LOGGER.error(
                "Invalid format for size: {0}".format(string_size), True)

        unit = string_size[len(string_size) - 2:]
        if unit not in units:
            LOGGER.error(
                "Invalid unit '{0}' for size '{1}'. Valid are: {2}".format(
                    unit, string_size, units), True)

        size = string_size[:len(string_size) - 2]
        size = size.strip()
        self._size = Size.convert(float(size), unit, 'pt')  # Default point
        return self._size

    @staticmethod
    def convert_to_pixel(value, unit, ppi=96):
        unit = unit.strip().lower()
        if unit == 'px':
            return value
        points = Size.convert(value, unit, 'pt')
        return (points * ppi) / Size.size_72

    @staticmethod
    def convert_from_pixel(value, unit, ppi=96):
        unit = unit.strip().lower()
        if unit == 'px':
            return value
        points = (value * Size.size_72) / ppi
        return Size.convert(points, 'pt', unit)

    @staticmethod
    def convert_to_mm(value, unit):
        unit = unit.strip().lower()
        if unit == 'mm':
            return value
        result = None
        if unit == 'in':
            result = value * Size.size_25_4
        elif unit == 'cm':
            result = value * Size.size_10
        elif unit == 'pt':
            result = (value * Size.size_25_4) / Size.size_72
        elif unit == 'pc':
            result = (value * Size.size_25_4) / Size.size_6
        else:
            LOGGER.error("Unknown unit '{0}'".format(unit), True)

        return result

    @staticmethod
    def convert(value, from_unit, to_unit='mm'):
        from_unit = from_unit.strip().lower()
        to_unit = to_unit.strip().lower()

        if from_unit == to_unit:
            return value

        result = None
        value = Size.convert_to_mm(value, from_unit)

        if to_unit == 'mm':
            result = value
        elif to_unit == 'in':
            result = value / Size.size_25_4
        elif to_unit == 'cm':
            result = value / Size.size_10
        elif to_unit == 'pt':
            result = (value / Size.size_25_4) * Size.size_72
        elif to_unit == 'pc':
            result = int((value / Size.size_25_4) * Size.size_6)
        else:
            LOGGER.error(
                "Unknown unit '{0}'".format(to_unit), True)

        return result


class Boolean(Expression):
    def __init__(self, expression, lnk, must_be_constant=False):
        super(Boolean, self).__init__(expression, lnk, must_be_constant)

    def value(self, report):
        val = super(Boolean, self).value(report)
        return DataType.get_value('Boolean', val)


class Float(Expression):
    def __init__(self, expression, lnk, must_be_constant=False):
        super(Float, self).__init__(expression, lnk, must_be_constant)

    def value(self, report):
        val = super(Float, self).value(report)
        return DataType.get_value('Float', val)


class Integer(Expression):
    def __init__(self, expression, lnk, must_be_constant=False):
        super(Integer, self).__init__(expression, lnk, must_be_constant)

    def value(self, report):
        val = super(Integer, self).value(report)
        return DataType.get_value('Integer', val)


class String(Expression):
    def __init__(self, expression, lnk, must_be_constant=False):
        super(String, self).__init__(expression, lnk, must_be_constant)

    def value(self, report):
        val = super(String, self).value(report)
        return DataType.get_value('String', val)


class Variant(Expression):
    def __init__(self, expression, lnk, must_be_constant=False):
        super(Variant, self).__init__(expression, lnk, must_be_constant)
