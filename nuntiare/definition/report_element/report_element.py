# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ..types.element import Element

class ReportElement(Element):
    '''
    The virtual ReportElement element defines an element of a report. The ReportElement element
    itself is not used. Only the subtypes of ReportElement are used: Body, PageSection, ReportItem
    '''

    def __init__(self, node, additional_elements, lnk):
        elements={'Style': [Element.ELEMENT],}
        
        if additional_elements:
            for key, value in additional_elements.items():
                elements[key] = value
        super(ReportElement, self).__init__(node, elements, lnk)        

