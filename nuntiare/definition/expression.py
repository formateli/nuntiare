# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from . expression_eval import get_expression_eval
from .. tools import raise_error_with_log, get_data_type_value

class Expression(object):
    def __init__(self, expression, lnk, must_be_constant):
        self.lnk=lnk
        self.must_be_constant=must_be_constant
        self.expression, self.is_constant = self.set_expression(expression)        

    def set_expression(self, expression):
        is_constant=False
        if expression==None or not expression.startswith('='):
            is_constant=True
        if self.must_be_constant and not is_constant:
            raise_error_with_log("Invalid expression '{0}' for '{1}' in '{2}' element. " \
                    "It must be a constant expression.".format(expression, self.lnk.data, 
                    self.lnk.parent.__class__.__name__))
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
        return get_expression_eval(report, ex) # Run python code


class Color(Expression):
    def __init__(self, string_color, lnk, must_be_constant=False):
        super(Color, self).__init__(string_color, lnk, must_be_constant)

        self.color={}  # Returned by value() function

        if self.is_constant:
            self.set_color(self.expression)
        else:
            self.set_default_color()

    def value(self, report):
        if self.is_constant:
            return self.color
        result = super(Color, self).value(report)
        if not result:
            return self.color 

        self.set_color(result)
        return self.color

    def set_default_color(self):
        # Sets to black full opaque
        self.set_values("#FF000000")

    def set_values(self, str_input):
        self.color['hex'] = '#'+ str_input[3:]
        self.color['hex_alpha']=str_input
        self.color['red_int'] = int(str_input[3:5],16)
        self.color['green_int'] = int(str_input[5:7],16)
        self.color['blue_int'] = int(str_input[7:],16)
        self.color['alpha_int'] = int(str_input[1:3],16)
        self.color['red'] = int(str_input[3:5] + str_input[3:5],16)
        self.color['green'] = int(str_input[5:7] + str_input[5:7],16)
        self.color['blue'] = int(str_input[7:] + str_input[7:],16)
        self.color['alpha'] = int(str_input[1:3] + str_input[1:3],16)

    def set_color(self, str_input):
        if str_input==None or str_input.strip()=="":
            self.set_default_color()
            return
	
        str_input = str_input.strip()
        if not str_input.startswith("#"): # It is not in hex format
            str_input=Color.get_color_by_name(str_input) 

        self.convert_hexstring_to_argb(str_input)

    def convert_hexstring_to_argb(self, hex_color):
        self.set_default_color()
        if (hex_color=="#FF000000"):
            return
            
        hex_color = hex_color[1:] # Remove '#'

        if len(hex_color) < 6 or len(hex_color) > 8:
            logger.warn("Color '{0}' not in correct format. Black assigned.".format(hex_color))
            return

        if len(hex_color) == 6:
            hex_color = "FF" + hex_color # Add Full opaque

        self.set_values('#' + hex_color)

    @staticmethod
    def get_color_by_name(name):
        # See http://www.w3schools.com/html/html_colornames.asp
        if name=="AliceBlue":
            return "#FFF0F8FF"
        if name=="AntiqueWhite":
            return "#FFFAEBD7"
        if name=="Aqua":
            return "#FF00FFFF"
        if name=="Aquamarine":
            return "#FF7FFFD4"	
        if name=="Azure":
            return "#FFF0FFFF"	
        if name=="Beige":
            return "#FFF5F5DC"	
        if name=="Bisque":
            return "#FFFFE4C4"	
        if name=="Black":
            return "#FF000000"	
        if name=="BlanchedAlmond":
            return "#FFFFEBCD"
        if name=="Blue":
            return "#FF0000FF"
        if name=="BlueViolet":
            return "#FF8A2BE2"
        if name=="Brown":
            return "#FFA52A2A"
        if name=="BurlyWood":
            return "#FFDEB887"
        if name=="CadetBlue":
            return "#FF5F9EA0"
        if name=="Chartreuse":
            return "#FF7FFF00"
        if name=="Chocolate":
            return "#FFD2691E"
        if name=="Coral":
            return "#FFFF7F50"
        if name=="CornflowerBlue":
            return "#FF6495ED"
        if name=="Cornsilk":
            return "#FFFFF8DC"
        if name=="Crimson":
            return "#FFDC143C"
        if name=="Cyan":
            return "#FF00FFFF"
        if name=="DarkBlue":
            return "#FF00008B"
        if name=="DarkCyan":
            return "#FF008B8B"
        if name=="DarkGoldenrod":
            return "#FFB8860B"
        if name=="DarkGray":
            return "#FFA9A9A9"
        if name=="DarkGreen":
            return "#FF006400"
        if name=="DarkKhaki":
            return "#FFBDB76B"
        if name=="DarkMagenta":
            return "#FF8B008B"
        if name=="DarkOliveGreen":
            return "#FF556B2F"
        if name=="DarkOrange":
            return "#FFFF8C00"
        if name=="DarkOrchid":
            return "#FF9932CC"
        if name=="DarkRed":
            return "#FF8B0000"
        if name=="DarkSalmon":
            return "#FFE9967A"
        if name=="DarkSeaGreen":
            return "#FF8FBC8F"
        if name=="DarkSlateBlue":
            return "#FF483D8B"
        if name=="DarkSlateGray":
            return "#FF2F4F4F"
        if name=="DarkTurquoise":
            return "#FF00CED1"
        if name=="DarkViolet":
            return "#FF9400D3"
        if name=="DeepPink":
            return "#FFFF1493"
        if name=="DeepSkyBlue":
            return "#FF00BFFF"
        if name=="DimGray":
            return "#FF696969"
        if name=="DodgerBlue":
            return "#FF1E90FF"
        if name=="Firebrick":
            return "#FFB22222"
        if name=="FloralWhite":
            return "#FFFFFAF0"
        if name=="ForestGreen":
            return "#FF228B22"	
        if name=="Fuchsia":
            return "#FFFF00FF"
        if name=="Gainsboro":
            return "#FFDCDCDC"	
        if name=="GhostWhite":
            return "#FFF8F8FF"            
        if name=="Gold":
            return "#FFFFD700"            				
        if name=="Goldenrod":
            return "#FFDAA520"
        if name=="Gray":
            return "#FF808080"	
        if name=="Green":
            return "#FF008000"
        if name=="GreenYellow":
            return "#FFADFF2F"				
        if name=="Honeydew":
            return "#FFF0FFF0"            			
        if name=="HotPink":
            return "#FFFF69B4"
        if name=="IndianRed":
            return "#FFCD5C5C"				
        if name=="Indigo":
            return "#FF4B0082"            			
        if name=="Ivory":
            return "#FFFFFFF0"            		
        if name=="Khaki":
            return "#FFF0E68C"
        if name=="Lavender":
            return "#FFE6E6FA"				
        if name=="LavenderBlush":
            return "#FFFFF0F5"            			
        if name=="LawnGreen":
            return "#FF7CFC00"
        if name=="LemonChiffon":
            return "#FFFFFACD"				
        if name=="LightBlue":
            return "#FFADD8E6"            			
        if name=="LightCoral":
            return "#FFF08080"
        if name=="LightCyan":
            return "#FFE0FFFF"
        if name=="LightGoldenrodYellow":
            return "#FFFAFAD2"				
        if name=="LightGray":
            return "#FFD3D3D3"            			
        if name=="LightGreen":
            return "#FF90EE90"
        if name=="LightPink":
            return "#FFFFB6C1"				
        if name=="LightSalmon":
            return "#FFFFA07A"
        if name=="LightSeaGreen":
            return "#FF20B2AA"				
        if name=="LightSkyBlue":
            return "#FF87CEFA"
        if name=="LightSlateGray":
            return "#FF778899"	
        if name=="LightSteelBlue":
            return "#FFB0C4DE"            
        if name=="LightYellow":
            return "#FFFFFFE0"
        if name=="Lime":
            return "#FF00FF00"				
        if name=="LimeGreen":
            return "#FF32CD32"            			
        if name=="Linen":
            return "#FFFAF0E6"
        if name=="Magenta":
            return "#FFFF00FF"				
        if name=="Maroon":
            return "#FF800000"            
        if name=="MediumAquamarine":
            return "#FF66CDAA"
        if name=="MediumBlue":
            return "#FF0000CD"	
        if name=="MediumOrchid":
            return "#FFBA55D3"
        if name=="MediumPurple":
            return "#FF9370DB"
        if name=="MediumSeaGreen":
            return "#FF3CB371"
        if name=="MediumSlateBlue":
            return "#FF7B68EE"				
        if name=="MediumSpringGreen":
            return "#FF00FA9A"
        if name=="MediumTurquoise":
            return "#FF48D1CC"				
        if name=="MediumVioletRed":
            return "#FFC71585"            			
        if name=="MidnightBlue":
            return "#FF191970"
        if name=="MintCream":
            return "#FFF5FFFA"				
        if name=="MistyRose":
            return "#FFFFE4E1"            			
        if name=="Moccasin":
            return "#FFFFE4B5"            			
        if name=="NavajoWhite":
            return "#FFFFDEAD"				
        if name=="Navy":
            return "#FF000080"
        if name=="OldLace":
            return "#FFFDF5E6"				
        if name=="Olive":
            return "#FF808000"
        if name=="OliveDrab":
            return "#FF6B8E23"				
        if name=="Orange":
            return "#FFFFA500"
        if name=="OrangeRed":
            return "#FFFF4500"				
        if name=="Orchid":
            return "#FFDA70D6"            			
        if name=="PaleGoldenrod":
            return "#FFEEE8AA"
        if name=="PaleGreen":
            return "#FF98FB98"				
        if name=="PaleTurquoise":
            return "#FFAFEEEE"            			
        if name=="PaleVioletRed":
            return "#FFDB7093"
        if name=="PapayaWhip":
            return "#FFFFEFD5"				
        if name=="PeachPuff":
            return "#FFFFDAB9"
        if name=="Peru":
            return "#FFCD853F"				
        if name=="Pink":
            return "#FFFFC0CB"            			
        if name=="PowderBlue":
            return "#FFB0E0E6"
        if name=="Purple":
            return "#FF800080"
        if name=="Red":
            return "#FFFF0000"
        if name=="RosyBrown":
            return "#FFBC8F8F"				
        if name=="RoyalBlue":
            return "#FF4169E1"            			
        if name=="SaddleBrown":
            return "#FF8B4513"
        if name=="Salmon":
            return "#FFFA8072"				
        if name=="SandyBrown":
            return "#FFF4A460"            			
        if name=="SeaGreen":
            return "#FF2E8B57"
        if name=="SeaShell":
            return "#FFFFF5EE"
        if name=="Sienna":
            return "#FFA0522D"				
        if name=="Silver":
            return "#FFC0C0C0"
        if name=="SkyBlue":
            return "#FF87CEEB"
        if name=="SlateBlue":
            return "#FF6A5ACD"				
        if name=="SlateGray":
            return "#FF708090"            			
        if name=="Snow":
            return "#FFFFFAFA"
        if name=="SpringGreen":
            return "#FF00FF7F"
        if name=="SteelBlue":
            return "#FF4682B4"				
        if name=="Tan":
            return "#FFD2B48C"
        if name=="Teal":				
            return "#FF008080"				
        if name=="Thistle":
            return "#FFD8BFD8"
        if name=="Tomato":
            return "#FFFF6347"
        if name=="Turquoise":
            return "#FF40E0D0"
        if name=="Violet":
            return "#FFEE82EE"
        if name=="Wheat":
            return "#FFF5DEB3"
        if name=="White":
            return "#FFFFFFFF"
        if name=="WhiteSmoke":
            return "#FFF5F5F5"            
        if name=="Yellow":
            return "#FFFFFF00"            				
        if name=="YellowGreen":
            return "#FF9ACD32"

        logger.warn("Color '{0}' not implemented. Black assigned.".format(name))
        return "#FF000000"


class Size(Expression):
    size_6 = float(6)
    size_10 = float(10)
    size_25_4 = float(25.4)
    size_72 = float(72)

    def __init__(self, string_size, lnk, must_be_constant=False):
        super(Size, self).__init__(string_size, lnk, must_be_constant)

        self.size=None           # Milimeters.
        self.original_size=None  # Original size, ex: 12
        self.original_unit=None  # Original unit, ex: in

        if not self.is_constant:
            return

        self.get_value(string_size)

    def value(self, report):
        if self.is_constant:
            return self.size
        result = super(Size, self).value(report)
        if not result:
            return None
        return self.get_value(result) 

    def get_value(self, string_size):
        if not string_size:
            self.size = 0.0
            return self.size
        
        units=('in','cm','mm','pt','pc')

        string_size=string_size.strip()
        if len(string_size) < 3:
            raise_error_with_log("Bad format for size: {0}".format(string_size))

        unit=string_size[len(string_size)-2:]
        if not unit in units:
            raise_error_with_log("Invalid unit value: '{0}' for size '{1}'".format(unit, string_size))

        size=string_size[:len(string_size)-2]
        size=size.strip()
        self.size = float(size) 
        
        # Milimeter convertion
        if unit=="in":
            self.size = self.size * Size.size_25_4
        elif unit=="cm":
            self.size = self.size * Size.size_10
        elif unit=="pt":
            self.size = (self.size * Size.size_25_4) / Size.size_72;
        elif unit=="pc":
            self.size = (self.size * Size.size_25_4) / Size.size_6;
        elif unit != "mm":
            raise_error_with_log("Unknown unit '{0}'".format(unit))

        self.original_size=size
        self.original_unit=unit

        return self.size

    def get_value_in_unit(self, unit):
        unit = unit.strip().lower()
        if unit=='mm':
            return self.size

        if unit=="in":
            return self.size / Size.size_25_4
        elif unit=="cm":
            return self.size / Size.size_10
        elif unit=="pt":
            return int((self.size / Size.size_25_4) * Size.size_72)
        elif unit=="pc":
            return int((self.size / Size.size_25_4) * Size.size_6)

        raise_error_with_log("Unknown unit '{0}'".format(unit))


class Boolean(Expression):
    def __init__(self, expression, lnk, must_be_constant=False):
        super(Boolean, self).__init__(expression, lnk, must_be_constant)

    def value(self, report):
        val = super(Boolean, self).value(report)
        return get_data_type_value('Boolean', val)
        
        
class Float(Expression):
    def __init__(self, expression, lnk, must_be_constant=False):
        super(Float, self).__init__(expression, lnk, must_be_constant)

    def value(self, report):
        val = super(Float, self).value(report)
        return get_data_type_value('Float', val)
        
        
class Integer(Expression):
    def __init__(self, expression, lnk, must_be_constant=False):
        super(Integer, self).__init__(expression, lnk, must_be_constant)

    def value(self, report):
        val = super(Integer, self).value(report)
        return get_data_type_value('Integer', val)                  


class String(Expression):
    def __init__(self, expression, lnk, must_be_constant=False):
        super(String, self).__init__(expression, lnk, must_be_constant)

    def value(self, report):
        val = super(String, self).value(report)
        return get_data_type_value('String', val)
        
        
class Variant(Expression):
    def __init__(self, expression, lnk, must_be_constant=False):
        super(Variant, self).__init__(expression, lnk, must_be_constant)
        
                
#def verify_expression_required(name, element, expr):
#    if not expr or expr.strip()=='':
#        raise_error_with_log("Element '{0}' is required for element '{1}'.".format(name, element))    

    
