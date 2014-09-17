# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from expression import Expression

class Variant(Expression):
    def __init__(self, expression, must_be_constant=False):
        super(Variant, self).__init__(expression, must_be_constant)

