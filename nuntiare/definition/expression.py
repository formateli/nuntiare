# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from .. import LOGGER
from .. data.data_type import DataType


class Expression(object):
    def __init__(self, expression, lnk, must_be_constant):
        self.lnk = lnk
        self.must_be_constant = must_be_constant
        self.expression, self.is_constant = self.set_expression(expression)

    def set_expression(self, expression):
        is_constant = False
        if expression is None or not expression.startswith('='):
            is_constant = True
        if self.must_be_constant and not is_constant:
            err_msg = "Invalid expression '{0}' for '{1}' in '{2}' element. "
            err_msg += "It must be a constant expression."
            LOGGER.error(err_msg.format(
                expression, self.lnk.data,
                self.lnk.parent.__class__.__name__), True)
        return [expression, is_constant]

    def value(self, report, new_expression=None):
        if new_expression:
            expression, is_constant = self.set_expression(new_expression)
        else:
            expression = self.expression
            is_constant = self.is_constant

        if is_constant:
            return expression
        ex = expression[1:]
        return report.modules.resolve_expression(ex)  # Run python code

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
        if str_input is None or str_input.strip() == "":
            self._color = Color._default_color
            return

        str_input = str_input.strip()
        if str_input.startswith("#"):
            Color._validate_hex_color(str_input)
            self._color = str_input
        elif str_input.startswith("rgb"):
            pass  # TODO
        elif str_input.startswith("argb"):
            pass  # TODO
        else:
            self._color = Color._get_color_by_name(str_input)

    @staticmethod
    def _validate_hex_color(hex_color):
        if not hex_color:
            LOGGER.error(
                "Invalid color '{0}'".format(hex_color), True)
        if len(hex_color) != 7 or not hex_color.startswith("#"):
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
        # See http://www.w3schools.com/html/html_colornames.asp
        if name == "AliceBlue":
            return "#F0F8FF"
        if name == "AntiqueWhite":
            return "#FAEBD7"
        if name == "Aqua":
            return "#00FFFF"
        if name == "Aquamarine":
            return "#7FFFD4"
        if name == "Azure":
            return "#F0FFFF"
        if name == "Beige":
            return "#F5F5DC"
        if name == "Bisque":
            return "#FFE4C4"
        if name == "Black":
            return "#000000"
        if name == "BlanchedAlmond":
            return "#FFEBCD"
        if name == "Blue":
            return "#0000FF"
        if name == "BlueViolet":
            return "#8A2BE2"
        if name == "Brown":
            return "#A52A2A"
        if name == "BurlyWood":
            return "#DEB887"
        if name == "CadetBlue":
            return "#5F9EA0"
        if name == "Chartreuse":
            return "#7FFF00"
        if name == "Chocolate":
            return "#D2691E"
        if name == "Coral":
            return "#FF7F50"
        if name == "CornflowerBlue":
            return "#6495ED"
        if name == "Cornsilk":
            return "#FFF8DC"
        if name == "Crimson":
            return "#DC143C"
        if name == "Cyan":
            return "#00FFFF"
        if name == "DarkBlue":
            return "#00008B"
        if name == "DarkCyan":
            return "#008B8B"
        if name == "DarkGoldenrod":
            return "#B8860B"
        if name == "DarkGray":
            return "#A9A9A9"
        if name == "DarkGreen":
            return "#006400"
        if name == "DarkKhaki":
            return "#BDB76B"
        if name == "DarkMagenta":
            return "#8B008B"
        if name == "DarkOliveGreen":
            return "#556B2F"
        if name == "DarkOrange":
            return "#FF8C00"
        if name == "DarkOrchid":
            return "#9932CC"
        if name == "DarkRed":
            return "#8B0000"
        if name == "DarkSalmon":
            return "#E9967A"
        if name == "DarkSeaGreen":
            return "#8FBC8F"
        if name == "DarkSlateBlue":
            return "#483D8B"
        if name == "DarkSlateGray":
            return "#2F4F4F"
        if name == "DarkTurquoise":
            return "#00CED1"
        if name == "DarkViolet":
            return "#9400D3"
        if name == "DeepPink":
            return "#FF1493"
        if name == "DeepSkyBlue":
            return "#00BFFF"
        if name == "DimGray":
            return "#696969"
        if name == "DodgerBlue":
            return "#1E90FF"
        if name == "Firebrick":
            return "#B22222"
        if name == "FloralWhite":
            return "#FFFAF0"
        if name == "ForestGreen":
            return "#228B22"
        if name == "Fuchsia":
            return "#FF00FF"
        if name == "Gainsboro":
            return "#DCDCDC"
        if name == "GhostWhite":
            return "#F8F8FF"
        if name == "Gold":
            return "#FFD700"
        if name == "Goldenrod":
            return "#DAA520"
        if name == "Gray":
            return "#808080"
        if name == "Green":
            return "#008000"
        if name == "GreenYellow":
            return "#ADFF2F"
        if name == "Honeydew":
            return "#F0FFF0"
        if name == "HotPink":
            return "#FF69B4"
        if name == "IndianRed":
            return "#CD5C5C"
        if name == "Indigo":
            return "#4B0082"
        if name == "Ivory":
            return "#FFFFF0"
        if name == "Khaki":
            return "#F0E68C"
        if name == "Lavender":
            return "#E6E6FA"
        if name == "LavenderBlush":
            return "#FFF0F5"
        if name == "LawnGreen":
            return "#7CFC00"
        if name == "LemonChiffon":
            return "#FFFACD"
        if name == "LightBlue":
            return "#ADD8E6"
        if name == "LightCoral":
            return "#F08080"
        if name == "LightCyan":
            return "#E0FFFF"
        if name == "LightGoldenrodYellow":
            return "#FAFAD2"
        if name == "LightGrey":
            return "#D3D3D3"
        if name == "LightGreen":
            return "#90EE90"
        if name == "LightPink":
            return "#FFB6C1"
        if name == "LightSalmon":
            return "#FFA07A"
        if name == "LightSeaGreen":
            return "#20B2AA"
        if name == "LightSkyBlue":
            return "#87CEFA"
        if name == "LightSlateGray":
            return "#778899"
        if name == "LightSteelBlue":
            return "#B0C4DE"
        if name == "LightYellow":
            return "#FFFFE0"
        if name == "Lime":
            return "#00FF00"
        if name == "LimeGreen":
            return "#32CD32"
        if name == "Linen":
            return "#FAF0E6"
        if name == "Magenta":
            return "#FF00FF"
        if name == "Maroon":
            return "#800000"
        if name == "MediumAquamarine":
            return "#66CDAA"
        if name == "MediumBlue":
            return "#0000CD"
        if name == "MediumOrchid":
            return "#BA55D3"
        if name == "MediumPurple":
            return "#9370DB"
        if name == "MediumSeaGreen":
            return "#3CB371"
        if name == "MediumSlateBlue":
            return "#7B68EE"
        if name == "MediumSpringGreen":
            return "#00FA9A"
        if name == "MediumTurquoise":
            return "#48D1CC"
        if name == "MediumVioletRed":
            return "#C71585"
        if name == "MidnightBlue":
            return "#191970"
        if name == "MintCream":
            return "#F5FFFA"
        if name == "MistyRose":
            return "#FFE4E1"
        if name == "Moccasin":
            return "#FFE4B5"
        if name == "NavajoWhite":
            return "#FFDEAD"
        if name == "Navy":
            return "#000080"
        if name == "OldLace":
            return "#FDF5E6"
        if name == "Olive":
            return "#808000"
        if name == "OliveDrab":
            return "#6B8E23"
        if name == "Orange":
            return "#FFA500"
        if name == "OrangeRed":
            return "#FF4500"
        if name == "Orchid":
            return "#DA70D6"
        if name == "PaleGoldenrod":
            return "#EEE8AA"
        if name == "PaleGreen":
            return "#98FB98"
        if name == "PaleTurquoise":
            return "#AFEEEE"
        if name == "PaleVioletRed":
            return "#DB7093"
        if name == "PapayaWhip":
            return "#FFEFD5"
        if name == "PeachPuff":
            return "#FFDAB9"
        if name == "Peru":
            return "#CD853F"
        if name == "Pink":
            return "#FFC0CB"
        if name == "PowderBlue":
            return "#B0E0E6"
        if name == "Purple":
            return "#800080"
        if name == "Red":
            return "#FF0000"
        if name == "RosyBrown":
            return "#BC8F8F"
        if name == "RoyalBlue":
            return "#4169E1"
        if name == "SaddleBrown":
            return "#8B4513"
        if name == "Salmon":
            return "#FA8072"
        if name == "SandyBrown":
            return "#F4A460"
        if name == "SeaGreen":
            return "#2E8B57"
        if name == "SeaShell":
            return "#FFF5EE"
        if name == "Sienna":
            return "#A0522D"
        if name == "Silver":
            return "#C0C0C0"
        if name == "SkyBlue":
            return "#87CEEB"
        if name == "SlateBlue":
            return "#6A5ACD"
        if name == "SlateGray":
            return "#708090"
        if name == "Snow":
            return "#FFFAFA"
        if name == "SpringGreen":
            return "#00FF7F"
        if name == "SteelBlue":
            return "#4682B4"
        if name == "Tan":
            return "#D2B48C"
        if name == "Teal":
            return "#008080"
        if name == "Thistle":
            return "#D8BFD8"
        if name == "Tomato":
            return "#FF6347"
        if name == "Turquoise":
            return "#40E0D0"
        if name == "Violet":
            return "#EE82EE"
        if name == "Wheat":
            return "#F5DEB3"
        if name == "White":
            return "#FFFFFF"
        if name == "WhiteSmoke":
            return "#F5F5F5"
        if name == "Yellow":
            return "#FFFF00"
        if name == "YellowGreen":
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

        units = ('in', 'cm', 'mm', 'pt', 'pc')

        string_size = string_size.strip()
        if len(string_size) < 3:
            LOGGER.error(
                "Invalid format for size: {0}".format(string_size), True)

        unit = string_size[len(string_size)-2:]
        if unit not in units:
            LOGGER.error(
                "Invalid unit value: '{0}' for size '{1}'".format(
                    unit, string_size), True)

        size = string_size[:len(string_size) - 2]
        size = size.strip()
        self._size = Size.convert_to_mm(float(size), unit)
        return self._size

    @staticmethod
    def convert_to_mm(value, unit):
        unit = unit.strip().lower()
        if unit == 'mm':
            return value
        result = None
        if unit == "in":
            result = value * Size.size_25_4
        elif unit == "cm":
            result = value * Size.size_10
        elif unit == "pt":
            result = (value * Size.size_25_4) / Size.size_72
        elif unit == "pc":
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

        if to_unit == "mm":
            result = value
        elif to_unit == "in":
            result = value / Size.size_25_4
        elif to_unit == "cm":
            result = value / Size.size_10
        elif to_unit == "pt":
            result = int((value / Size.size_25_4) * Size.size_72)
        elif to_unit == "pc":
            result = int((value / Size.size_25_4) * Size.size_6)
        else:
            LOGGER.error(
                "Can not convert from 'mm'. Unknown unit '{0}'".format(
                    to_unit), True)

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
