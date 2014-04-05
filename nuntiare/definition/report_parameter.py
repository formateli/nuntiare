# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from element import Element
from expression import verify_expression_constant_and_required
from ..tools import get_expression_value_or_default, raise_error_with_log
from decimal import Decimal

class ReportParameters(Element):
    def __init__(self, node, lnk):
        elements={'ReportParameter': [Element.ELEMENT],}
        super(ReportParameters, self).__init__(node, elements, lnk) 


class ReportParameter(Element):
    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING],
                  'DataType': [Element.ENUM, 'DataType'],
                  'CanBeNone': [Element.BOOLEAN],
                  'AllowBlank': [Element.BOOLEAN],
                  'DefaultValue': [Element.VARIANT],
                  'Promt': [Element.STRING],
                 }

        super(ReportParameter, self).__init__(node, elements, lnk)

        name = verify_expression_constant_and_required('Name', 'ReportParameter', self.get_element('Name'))
        datatype = verify_expression_constant_and_required('DataType', 'ReportParameter', self.get_element('DataType'))

        self.parameter_name = name.value()
        self.default_value = self.get_element('DefaultValue')
        if not self.default_value:
            raise_error_with_log("'DefaultValue' is required for Parameter '{0}'".format(self.parameter_name))
        self.lnk.report.parameters_obj.append(self)

    def set_value(self, val):
        self.default_value.set_expression(val)

    def value(self):
        can_be_none = get_expression_value_or_default(self, 'CanBeNone', True)
        allow_blank = get_expression_value_or_default(self, 'AllowBlank', True)
        data_type = get_expression_value_or_default(self, 'DataType', None)

        result = None
        if self.default_value:
            result = self.default_value.value() 

        if not result and not can_be_none:
            raise_error_with_log("Parameter '{0}' value can not be 'None'".format(self.parameter_name))
        if result and result=="" and not allow_blank and data_type=='String':
            raise_error_with_log("Parameter '{0}' value can not be an empty string".format(self.parameter_name))

        if not result or not data_type:
            return result

        if data_type == "String":
            result = str(result)
        if data_type == "Integer":
            result = int(result)
        if data_type == "Float":
            result = float(result)
        if data_type == "Boolean":
            result = bool(result)
        if data_type == "DateTime":
            pass
        if data_type == "Decimal":
            result = Decimal(result)

        return result

