# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from .. report_item import ReportItem
from .... types.element import Element

class DataRegion(ReportItem):
    def __init__(self, type, node, lnk, additional_elements):
        elements={'NoRowsMessage': [Element.STRING],
                  'DataSetName': [Element.STRING, True],
                  'PageBreak': [Element.ELEMENT],
                  'Filters': [Element.ELEMENT],
                  'SortExpressions': [Element.ELEMENT],
                 }
        if additional_elements:
            for key, value in additional_elements.items():
                elements[key] = value
        super(DataRegion, self).__init__(type, node, lnk, elements)

