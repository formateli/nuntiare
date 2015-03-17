# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from sys import version_info
from dateutil import parser #TODO raise error if python3-dateutil is not installed
from decimal import Decimal
from .. import logger

class DataType():

    @staticmethod
    def get_value(data_type, value):
        if data_type==None or value==None:
            return value
        
        result = None
        if data_type == "Boolean":
            result = DataType._to_bool(value)
        if data_type == "DateTime":
            result = parser.parse(value)
        if data_type == "Integer":
            result = int(value)
        if data_type == "String":
            result = str(value)
            if version_info[0] == 2: # if python2, Convert to unicode
                if isinstance(result, unicode):
                    pass
                elif isinstance(result, str):
                    result = unicode(result, 'utf-8')
                else:
                    result = unicode(str(result), 'utf-8')            
        if data_type == "Float":
            result = float(value)
        if data_type == "Decimal":
            result = Decimal(value)

        return result

    @staticmethod
    def _to_bool(value):
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

