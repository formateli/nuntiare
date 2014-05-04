# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from expression import Expression

class String(Expression):
    def __init__(self, report, expression):
        super(String, self).__init__(report, expression)

    def value(self):
        val = super(String, self).value()
        if val != None:
            return str(val)

