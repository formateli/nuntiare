# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

class DataElementStyle(Enum):    
    enum_list={'auto': 'Auto',
               'attribute': 'Attribute', 
               'element': 'Element', 
              }

    def __init__(self, expression):
        super(DataElementStyle, self).__init__('DataElementStyle', expression, DataElementStyle.enum_list)

