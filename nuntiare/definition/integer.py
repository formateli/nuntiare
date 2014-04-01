# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from expression import Expression

class Integer(Expression):
    def __init__(self, report, expression):
        super(Integer, self).__init__(report, expression)
