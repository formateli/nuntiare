# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from expression import Expression
from ..tools import raise_error_with_log

class Size(Expression):
    size_6 = float(6)
    size_10 = float(10)
    size_25_4 = float(25.4)
    size_72 = float(72)

    def __init__(self, report, string_size):
        super(Size, self).__init__(report, string_size)

        self.size=None           # Milimeters.
        self.original_size=None  # Original size, ex: 12
        self.original_unit=None  # Original unit, ex: in

        if not self.is_constant:
            return

        self.get_value(string_size)
        self.expression = self.size

    def value(self):
        if self.is_constant:
            return self.size
        result = super(Size, self).value()
        if not result:
            return None
        return self.get_value(result) 

    def get_value(self, string_size):
        units=('in','cm','mm','pt','pc')

        string_size=string_size.strip()
        if len(string_size) < 3:
            raise_error_with_log("Bad format for size: {0}".format(string_size))

        unit=string_size[len(string_size)-2:]
        if not unit in units:
            raise_error_with_log("Invalid unit value: '{0}' for size '{1}'".format(unit, string_size))

        # Decimal convertion
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

