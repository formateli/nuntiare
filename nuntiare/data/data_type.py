# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from sys import version_info
from dateutil import parser
from datetime import date, datetime
from decimal import Decimal
from .. import logger

class DataType():
    @staticmethod
    def get_value(data_type, value):
        def _to_bool(value):
            if value == None: 
                return None
            if isinstance(value, bool):
                return value
            
            if str(value).lower() in \
                ("yes", "y", "true",  "t", "1", "-1"): 
                return True
            if str(value).lower() in \
                ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"): 
                return False
            
            logger.warn(
                "Unknown bool expression '{0}'. False assigned.".format(value))
            return False
    
        if data_type == None or value == None:
            return value
        
        types = ("Boolean",
                 "DateTime",
                 "Integer",
                 "String",
                 "Float",
                 "Decimal",
                 "Object"                 
                )
        
        if not data_type in types:
            logger.error(
                "Unknown Data Type '{0}' for expression '{1}'. Data type must be: {2}".format(
                    data_type, value, types), True)
        
        if data_type == "Object":
            return value
        
        result = None
        
        if data_type == "Boolean":
            result = _to_bool(value)            
        if data_type == "DateTime":
            if isinstance(value, datetime):
                result = value
            elif isinstance(value, date):
                result = datetime.combine(value, datetime.min.time())
            else:
                result = parser.parse(value)
        if data_type == "Integer":
            result = int(value)
        if data_type == "String":
            result = str(value) # Python3 always return unicode
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


class _Collection_BK(object):
    def __init__(self, read_only=True):
        self._read_only = read_only
        self._item_dict = {}
        
    def _add_item(self, key, item):
        if key in self._item_dict.keys():
            logger.error(
                "Item '{0}' already exists in '{1}' collection.".format(
                    key, self.__class__.__name__), True)
        self._item_dict[key] = item
        self.__setattr__(key, item)

    def __call__(self, key=None):
        return self._get_item(key)

    def __getitem__(self, key):
        return self._get_item(key)

    def __setitem__(self, key, value):
        if self._read_only:
            logger.error(
                "'{0}' collection is read only.".format(
                    self.__class__.__name__), True)        
        if key in self._item_dict.keys():
            item = self._item_dict[key]
            item.set_default_prop_value(value)
        else:
            logger.error(
                "Item '{0}' not found in '{1}' collection.".format(
                    key, self.__class__.__name__), True)

    def _get_item(self, key):
        if key in self._item_dict.keys():
            item = self._item_dict[key]
            return item.get_default_prop()
        logger.error(
            "Item '{0}' not found in '{1}' collection.".format(
                key, self.__class__.__name__), True)
                

class _CollectionObject_BK(object):
    def __init__(self, name, default_att="Value"):
        self._prop_dict = {}
        self._default_att = default_att
        self._add_prop("Name", name)
        
    def _add_prop(self, key, value):
        if key in self._prop_dict.keys():
            logger.error(
                "Property '{0}' already exists in '{1}' object.".format(
                    key, self.__class__.__name__), True)
        self._prop_dict[key] = value
        self.__setattr__(key, value)
        
    def get_default_prop(self):
        return self.__dict__[self._default_att]
        
    def set_default_prop_value(self, value):
        self._prop_dict[self._default_att] = value
        
    def __call__(self, prop=None):
        if not prop:
            return self.get_default_prop()
        if not self.__dict__ or not prop in self.__dict__.keys():
            logger.error(
                "Not a valid property '{0}' for '{1}'.".format(
                    prop, self.__class__.__name__), True)
        return self.__dict__[prop]


class Parameters_BK(_Collection_BK):
    class Parameter(_CollectionObject_BK):
        def __init__(self, name, value):
            super(Parameters.Parameter, self).__init__(name, "Value")
            self._add_prop("Value", value)

    def __init__(self):
        super(Parameters, self).__init__()

    def add_parameter(self, name, value):
        p = Parameters.Parameter(name, value)
        self._add_item(name, p)


class Globals_BK(_Collection_BK):
    class Global(_CollectionObject_BK):
        def __init__(self, name, value):
            super(Globals.Global, self).__init__(name, "Value")
            self._add_prop("Value", value)

    def __init__(self):
        super(Globals, self).__init__(read_only=False)

    def add_global(self, name, value):
        g = Globals.Global(name, value)
        self._add_item(name, g)

