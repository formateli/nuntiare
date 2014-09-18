# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from decimal import Decimal
from dateutil import parser
from .. types.enum import Enum
from ... import logger

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


def get_data_type_value(data_type, value):
    if data_type==None or value==None:
        return value
    
    result = None
    if data_type == "Boolean":
        result = to_bool(value)
    if data_type == "DateTime":
        result = parser.parse(value)
    if data_type == "Integer":
        result = int(value)
    if data_type == "String":
        result = str(value) # TODO Return unicode ???
    if data_type == "Float":
        result = float(value)
    if data_type == "Decimal":
        result = Decimal(value)

    return result
    
    
def to_bool(value):
    if value == None: 
        return None
    if value is bool:
        return value
    
    if str(value).lower() in ("yes", "y", "true",  "t", "1", "-1"): 
        return True
    if str(value).lower() in ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"): 
        return False
    
    logger.warn("Unknown bool expression '{0}'. False assigned.".format(value))
    return False    

