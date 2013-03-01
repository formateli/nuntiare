# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from expression import Expression

class Boolean(Expression):
    def __init__(self, expression):
        super(Boolean, self).__init__(expression)

