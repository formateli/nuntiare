# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from types.element import Element
from types.expression import verify_expression_required
from data.data_type import get_data_type_value
from .. tools import get_expression_value_or_default

class ReportParameters(Element):
    def __init__(self, node, lnk):
        elements={'ReportParameter': [Element.ELEMENT],}
        super(ReportParameters, self).__init__(node, elements, lnk) 


class ReportParameter(Element):
    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING, True],
                  'DataType': [Element.ENUM],
                  'CanBeNone': [Element.BOOLEAN, True],
                  'AllowBlank': [Element.BOOLEAN, True],
                  'DefaultValue': [Element.VARIANT],
                  'Promt': [Element.STRING],
                 }

        super(ReportParameter, self).__init__(node, elements, lnk)
        
        self.parameter_name = get_expression_value_or_default(None, self, 'Name', None)
        self.can_be_none = get_expression_value_or_default(None, self, 'CanBeNone', True)
        self.allow_blank = get_expression_value_or_default(None, self, 'AllowBlank', True)
        self.data_type = get_expression_value_or_default(None, self, 'DataType', None)
        
        verify_expression_required('Name', 'ReportParameter', self.parameter_name)
        verify_expression_required('DataType', 'ReportParameter', self.data_type)

        self.default_value = self.get_element('DefaultValue')
        if not self.default_value:
            raise_error_with_log("'DefaultValue' is required for Parameter '{0}'".format(self.parameter_name))
        self.lnk.report_def.parameters_def.append(self)

    def get_default_value(self, report):
        if self.default_value:
            return get_data_type_value(self.data_type, self.default_value.value(report))             
                        
    def get_value(self, report, passed_value):
        if passed_value == None:
            result = self.get_default_value(report)
        else:
            result = get_data_type_value(self.data_type, self.default_value.value(report, passed_value)) 

        if not result and not self.can_be_none:
            raise_error_with_log("Parameter '{0}' value can not be 'None'".format(self.parameter_name))
        if result and result=="" and not self.allow_blank and data_type=='String':
            raise_error_with_log("Parameter '{0}' value can not be an empty string.".format(self.parameter_name))

        return result

