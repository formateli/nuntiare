# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from report_element import ReportElement
from .. types.element import Element
from ... tools import get_expression_value_or_default, inch_2_mm

class PageSection(ReportElement):
    '''
    The virtual PageSection element defines the layout of report items to appear at the top or bottom
    of every page of the report. The PageSection element itself is not used. Only subtypes of
    PageSection are used: PageHeader, PageFooter. It inherits from ReportElement
    '''

    def __init__(self, node, lnk):
        elements={'ReportItems': [Element.ELEMENT],
                  'Height': [Element.SIZE, True], 
                  'PrintOnFirstPage': [Element.BOOLEAN, True],
                  'PrintOnLastPage': [Element.BOOLEAN, True],
                 }
        super(PageSection, self).__init__(node, elements, lnk)


class PageHeader(PageSection):
    '''
    The PageHeader element defines the layout of report items to appear at the top of every page of
    the report. It has no properties beyond those it inherits from PageSection.
    '''
    
    def __init__(self, node, lnk):
        super(PageHeader, self).__init__(node, lnk)


class PageFooter(PageSection):
    '''
    The PageFooter element defines the layout of report items to appear at the bottom of every page of
    the report. It has no properties beyond those it inherits from PageSection.
    '''
    
    def __init__(self, node, lnk):
        super(PageFooter, self).__init__(node, lnk)

