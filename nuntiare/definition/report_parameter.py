# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from element import Element
from expression import verify_expression_constant_and_required

class ReportParameters(Element):
    def __init__(self, node, lnk):
        elements={'ReportParameter': [Element.ELEMENT],}
        super(ReportParameters, self).__init__(node, elements, lnk) 


class ReportParameter(Element):
    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING],
                  'DataType': [Element.ENUM, 'DataType'],
                  'CanBeNone': [Element.BOOLEAN],
                  'DefaultValue': [Element.ELEMENT],
                  'AllowBlank': [Element.BOOLEAN],
                  'Promt': [Element.STRING],
                  'ValidValues': [Element.ELEMENT], 
                  'MultiValue': [Element.BOOLEAN],
                 }

        super(ReportParameter, self).__init__(node, elements, lnk)

        name = verify_expression_constant_and_required('Name', 'ReportParameter', self.get_element('Name'))
        datatype = verify_expression_constant_and_required('DataType', 'ReportParameter', self.get_element('DataType'))

        # Add to report dictionary
        self.lnk.report.parameters[name.value()] = self


class ValidValues(Element):
    def __init__(self, node, lnk):
        elements={'DataSetReference ': [Element.ELEMENT],
                  'ParameterValues ': [Element.ELEMENT],
                 }

        super(ValidValues, self).__init__(node, elements, lnk)


class DataSetReference(Element):
    def __init__(self, node, lnk):
        elements={'DataSetName  ': [Element.STRING],
                  'ValueField  ': [Element.STRING],
                  'LabelField   ': [Element.STRING],
                 }

        super(DataSetReference, self).__init__(node, elements, lnk)


class ParameterValues(Element):
    def __init__(self, node, lnk):
        elements={'ParameterValue  ': [Element.ELEMENT]}

        super(ParameterValues, self).__init__(node, elements, lnk)


class ParameterValue(Element):
    def __init__(self, node, lnk):
        elements={'Value ': [Element.VARIANT],
                  'Label ': [Element.STRING],
                 }

        super(ParameterValue, self).__init__(node, elements, lnk)


class DefaultValue(Element):
    def __init__(self, node, lnk):
        elements={'DataSetReference   ': [Element.ELEMENT],
                  'Values  ': [Element.ELEMENT],
                 }

        super(DefaultValue, self).__init__(node, elements, lnk)


class Values(Element):
    def __init__(self, node, lnk):
        elements={'Value  ': [Element.VARIANT]}

        super(Values, self).__init__(node, elements, lnk)

