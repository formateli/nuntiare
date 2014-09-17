# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from expression import Expression
from .. data.data_type import get_data_type_value

class Float(Expression):
    def __init__(self, expression, must_be_constant=False):
        super(Float, self).__init__(expression, must_be_constant)

    def value(self, report):
        val = super(Float, self).value(report)
        return get_data_type_value('Float', val)
            
