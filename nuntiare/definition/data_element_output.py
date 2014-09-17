# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

class DataElementOutput(Enum):    
    enum_list={'auto': 'Auto',
               'output': 'Output', 
               'nooutput': 'NoOutput', 
               'contentsonly': 'ContentsOnly',                
              }

    def __init__(self, expression):
        super(DataElementOutput, self).__init__('DataElementOutput', expression, DataElementOutput.enum_list)

