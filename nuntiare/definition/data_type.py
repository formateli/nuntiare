# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from nuntiare.definition.enum import Enum

class DataType(Enum):
    enum_list={'boolean': 'Boolean',
               'datetime': 'DateTime', 
               'integer': 'Integer', 
               'float': 'Float', 
               'decimal': 'Decimal', 
               'string': 'String', 
              }

    def __init__(self, expression):
        super(DataType, self).__init__('DataType', expression, DataType.enum_list)
