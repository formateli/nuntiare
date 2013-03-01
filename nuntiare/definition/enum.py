# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from nuntiare import logger
from expression import Expression

class Enum(Expression):
    def __init__(self, enum_name, expression, enum_list):
        self.name = enum_name 
        self.enum_list = enum_list
        super(Enum, self).__init__(expression)
        if self.is_constant:
            self.expression = self.get_enum_by_name(self.expression)

    def get_enum_by_name(self, name):
        if not name or name == '':
            return None
        name=name.strip().lower()
        if self.enum_list.has_key(name):
            return self.enum_list[name]

        logger.warn("Unknown value '{0}' for Enum '{1}'. <None> assigned.".format(name, self.name))
        return None

