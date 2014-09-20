# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from report_element import ReportElement
from ..types.element import Element
from ...tools import get_expression_value_or_default

class Body(ReportElement):
    '''
    The Body element defines the visual elements of the body of the report, how the data is
    structured/grouped and binds the visual elements to the data for the report.
    It inherits from ReportElement.
    '''

    def __init__(self, node, lnk):
        elements={'ReportItems': [Element.ELEMENT],
                  'Height': [Element.SIZE, True], 
                 }
        super(Body, self).__init__(node, elements, lnk)
        self.height = get_expression_value_or_default(None, self, "Height", 0.0)

