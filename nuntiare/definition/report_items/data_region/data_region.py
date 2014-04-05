# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ..report_item import ReportItem
from ...element import Element

class DataRegion(ReportItem):
    def __init__(self, node, lnk, additional_elements):
        elements={'KeepTogether': [Element.BOOLEAN], 
                  'NoRows': [Element.STRING],
                  'DataSetName': [Element.STRING],
                  'PageBreakAtStart': [Element.BOOLEAN],
                  'PageBreakAtEnd': [Element.BOOLEAN],
                  'Filters': [Element.ELEMENT],
                 }
        if additional_elements:
            for key, value in additional_elements.items():
                elements[key] = value
        super(DataRegion, self).__init__(node, lnk, elements)
