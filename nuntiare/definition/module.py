# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import sys
from importlib import import_module
from element import Element
from ..tools import raise_error_with_log, get_expression_value_or_default

class Imports(Element):
    def __init__(self, node, lnk):
        elements={'Import': [Element.ELEMENT],}
        super(Imports, self).__init__(node, elements, lnk) 


class Import(Element):
    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING],
                  'Module': [Element.STRING],
                 }
        super(Import, self).__init__(node, elements, lnk)

        name = get_expression_value_or_default(self, "Name", None)
        if not name:
            raise_error_with_log("'Name' is required for 'Import' element")
        module = get_expression_value_or_default(self, "Module", None)
        if not module:
            raise_error_with_log("'Module' is required for '{0} Import' element".format(name))

        md = self.load_module(module) 
        if not md:
            raise_error_with_log("Module {0} could not be loaded.".format(module))

        if lnk.report.modules.has_key(name):
            raise_error_with_log("Module with name '{0}' already exists.".format(name))
        lnk.report.modules[name] = md

    def load_module(self, module):
        try:        
            result = import_module(module)
        except:
            raise_error_with_log("Error loading module: '{0}'. {1}.".format(module, sys.exc_info()[0]))
        return result

